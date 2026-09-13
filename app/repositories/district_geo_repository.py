"""
app/repositories/district_geo_repository.py

Repository for querying and managing authoritative district geographic centroids
(latitude, longitude, elevation) from PostgreSQL table `district_geo_centroids`.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.research_models import DistrictGeoCentroid
from app.repositories.district_msme_repository import normalize_district_key, normalize_state_key


class DistrictGeoRepository:
    """Repository for querying authoritative district geographic centroids."""

    @classmethod
    def get_by_district_id(cls, db: Session, district_id: int) -> Optional[DistrictGeoCentroid]:
        """Fetch centroid record directly by district ID."""
        return db.query(DistrictGeoCentroid).filter(DistrictGeoCentroid.district_id == district_id).first()

    @classmethod
    def get_by_district_code(cls, db: Session, lg_dt_code: str) -> Optional[DistrictGeoCentroid]:
        """Fetch centroid record by official LGD district code."""
        code_str = str(lg_dt_code).strip()
        sql = text("""
            SELECT c.*
            FROM district_geo_centroids c
            JOIN districts d ON c.district_id = d.id
            WHERE d.district_code = :code_str
        """)
        row = db.execute(sql, {"code_str": code_str}).fetchone()
        if not row:
            return None
        return cls.get_by_district_id(db, row._mapping["district_id"])

    @classmethod
    def get_by_district_and_state(
        cls,
        db: Session,
        district_name: str,
        state_name: Optional[str] = None,
    ) -> Optional[DistrictGeoCentroid]:
        """
        Fetch centroid record by district name and optional state name.
        Uses normalized keys consistent with DistrictMsmeRepository.
        """
        norm_dist = normalize_district_key(district_name)
        
        sql = """
            SELECT c.district_id, d.district_name, s.state_name
            FROM district_geo_centroids c
            JOIN districts d ON c.district_id = d.id
            JOIN states s ON d.state_id = s.id
        """
        rows = db.execute(text(sql)).fetchall()
        
        norm_state = normalize_state_key(state_name) if state_name else None
        
        # 1. Exact match on normalized district & state
        for r in rows:
            m = r._mapping
            d_norm = normalize_district_key(m["district_name"])
            s_norm = normalize_state_key(m["state_name"])
            if d_norm == norm_dist:
                if norm_state is None or s_norm == norm_state or norm_state in s_norm or s_norm in norm_state:
                    return cls.get_by_district_id(db, m["district_id"])

        # 2. Substring match if exact match not found
        for r in rows:
            m = r._mapping
            d_norm = normalize_district_key(m["district_name"])
            s_norm = normalize_state_key(m["state_name"])
            if norm_dist in d_norm or d_norm in norm_dist:
                if norm_state is None or s_norm == norm_state or norm_state in s_norm or s_norm in norm_state:
                    return cls.get_by_district_id(db, m["district_id"])

        return None

    @classmethod
    def upsert(
        cls,
        db: Session,
        district_id: int,
        lat: float,
        lon: float,
        elevation: Optional[float] = None,
        source: str = "open-meteo",
    ) -> DistrictGeoCentroid:
        """Upsert centroid record for a given district_id using ORM."""
        record = cls.get_by_district_id(db, district_id)
        now_dt = datetime.utcnow()
        if not record:
            record = DistrictGeoCentroid(
                district_id=district_id,
                latitude=Decimal(str(round(lat, 6))),
                longitude=Decimal(str(round(lon, 6))),
                elevation_meters=Decimal(str(round(elevation, 2))) if elevation is not None else None,
                source=source,
                created_at=now_dt,
                updated_at=now_dt,
            )
            db.add(record)
        else:
            record.latitude = Decimal(str(round(lat, 6)))
            record.longitude = Decimal(str(round(lon, 6)))
            record.elevation_meters = Decimal(str(round(elevation, 2))) if elevation is not None else None
            record.source = source
            record.updated_at = now_dt

        db.commit()
        db.refresh(record)
        return record
