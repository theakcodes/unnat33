import re
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text


DISTRICT_ALIASES = {
    "NORTH24PARGANAS": "NORTH24PRAGANAS",
    "NORTHTWENTYFOURPARGANAS": "NORTH24PRAGANAS",
    "SOUTH24PARGANAS": "SOUTH24PRAGANAS",
    "SOUTHTWENTYFOURPARGANAS": "SOUTH24PRAGANAS",
    "KOLKATA": "KOLKOTA",
}


def normalize_district_key(name: str) -> str:
    """Normalize district name by stripping whitespace, punctuation, parentheses and applying known aliases."""
    cleaned = re.sub(r"[^A-Z0-9]", "", name.strip().upper())
    return DISTRICT_ALIASES.get(cleaned, cleaned)


def normalize_state_key(name: str) -> str:
    """Normalize state name by stripping whitespace, punctuation, and converting to uppercase."""
    return re.sub(r"[^A-Z0-9]", "", name.strip().upper())


class DistrictMsmeRepository:
    """Repository for querying official Udyam district MSME records and computing rankings."""

    BASE_RANKED_CTE = """
        WITH ranked_districts AS (
            SELECT 
                d.id AS district_id,
                d.district_code AS lg_dt_code,
                d.district_name,
                s.id AS state_id,
                s.state_name,
                s.state_code,
                m.micro_enterprises,
                m.small_enterprises,
                m.medium_enterprises,
                (m.micro_enterprises + m.small_enterprises + m.medium_enterprises) AS total_msmes,
                RANK() OVER (ORDER BY (m.micro_enterprises + m.small_enterprises + m.medium_enterprises) DESC) AS national_rank,
                RANK() OVER (PARTITION BY s.id ORDER BY (m.micro_enterprises + m.small_enterprises + m.medium_enterprises) DESC) AS state_rank,
                COUNT(*) OVER (PARTITION BY s.id) AS total_districts_in_state
            FROM districts d
            JOIN states s ON d.state_id = s.id
            JOIN msme_district_data m ON m.district_id = d.id
        )
    """

    @classmethod
    def get_by_lgd_code(cls, db: Session, lg_dt_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve district MSME metrics by unique LGD district code."""
        code_str = str(lg_dt_code).strip()
        sql = f"""
            {cls.BASE_RANKED_CTE}
            SELECT * FROM ranked_districts
            WHERE lg_dt_code = :code_str;
        """
        row = db.execute(text(sql), {"code_str": code_str}).fetchone()
        return dict(row._mapping) if row else None

    @classmethod
    def get_by_district_and_state(
        cls,
        db: Session,
        district_name: str,
        state_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve district MSME metrics by district name and optional state name.
        
        Uses deterministic alphanumeric normalization to resolve punctuation, parentheses,
        and casing variants (e.g. 'Bengaluru Urban' <-> 'BENGALURU (URBAN)') safely scoped to the state.
        """
        if not district_name or not district_name.strip():
            return None

        d_norm = normalize_district_key(district_name)
        
        if state_name and state_name.strip():
            s_norm = normalize_state_key(state_name)
            s_clean = state_name.strip().upper()
            sql = f"""
                {cls.BASE_RANKED_CTE}
                SELECT * FROM ranked_districts
                WHERE REGEXP_REPLACE(UPPER(district_name), '[^A-Z0-9]', '', 'g') = :d_norm
                  AND (
                      REGEXP_REPLACE(UPPER(state_name), '[^A-Z0-9]', '', 'g') = :s_norm
                      OR state_code = :s_clean
                  )
                ORDER BY total_msmes DESC
                LIMIT 1;
            """
            row = db.execute(text(sql), {"d_norm": d_norm, "s_norm": s_norm, "s_clean": s_clean}).fetchone()
            if row:
                return dict(row._mapping)
        else:
            # Look up by district name alone (pick highest MSME volume if homonymous)
            sql = f"""
                {cls.BASE_RANKED_CTE}
                SELECT * FROM ranked_districts
                WHERE REGEXP_REPLACE(UPPER(district_name), '[^A-Z0-9]', '', 'g') = :d_norm
                ORDER BY total_msmes DESC
                LIMIT 1;
            """
            row = db.execute(text(sql), {"d_norm": d_norm}).fetchone()
            if row:
                return dict(row._mapping)

        return None

    @classmethod
    def get_state_aggregate(
        cls,
        db: Session,
        state_name_or_code: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve aggregated MSME metrics for an entire State / UT with normalization."""
        if not state_name_or_code or not state_name_or_code.strip():
            return None

        s_norm = normalize_state_key(state_name_or_code)
        s_clean = state_name_or_code.strip().upper()
        sql = """
            SELECT 
                s.id AS state_id,
                s.state_name,
                s.state_code,
                COALESCE(SUM(m.micro_enterprises), 0) AS micro_enterprises,
                COALESCE(SUM(m.small_enterprises), 0) AS small_enterprises,
                COALESCE(SUM(m.medium_enterprises), 0) AS medium_enterprises,
                COALESCE(SUM(m.micro_enterprises + m.small_enterprises + m.medium_enterprises), 0) AS total_msmes,
                COUNT(d.id) AS total_districts_in_state
            FROM states s
            LEFT JOIN districts d ON d.state_id = s.id
            LEFT JOIN msme_district_data m ON m.district_id = d.id
            WHERE REGEXP_REPLACE(UPPER(s.state_name), '[^A-Z0-9]', '', 'g') = :s_norm
               OR s.state_code = :s_clean
            GROUP BY s.id, s.state_name, s.state_code
            LIMIT 1;
        """
        row = db.execute(text(sql), {"s_norm": s_norm, "s_clean": s_clean}).fetchone()
        return dict(row._mapping) if row and row.total_msmes > 0 else None

    @classmethod
    def get_top_districts(
        cls,
        db: Session,
        state_id: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Retrieve top districts by total MSME volume nationally or within a state."""
        if state_id:
            sql = f"""
                {cls.BASE_RANKED_CTE}
                SELECT * FROM ranked_districts
                WHERE state_id = :state_id
                ORDER BY state_rank ASC
                LIMIT :limit;
            """
            rows = db.execute(text(sql), {"state_id": state_id, "limit": limit}).fetchall()
        else:
            sql = f"""
                {cls.BASE_RANKED_CTE}
                SELECT * FROM ranked_districts
                ORDER BY national_rank ASC
                LIMIT :limit;
            """
            rows = db.execute(text(sql), {"limit": limit}).fetchall()
        return [dict(r._mapping) for r in rows]


district_msme_repository = DistrictMsmeRepository()
