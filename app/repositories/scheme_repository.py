from typing import List, Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload
from app.models.scheme import Scheme
from app.models.master import Sector
from app.schemas.scheme import SchemeQueryParams

CANONICAL_SECTOR_CODES = {
    "mfg": "MFG",
    "manufacturing": "MFG",
    "srv": "SRV",
    "service": "SRV",
    "services": "SRV",
    "trd": "TRD",
    "trading": "TRD",
    "retail": "TRD",
    "trading / retail": "TRD",
    "trading/retail": "TRD",
    "agr": "AGR",
    "agriculture": "AGR",
    "allied": "AGR",
    "agriculture and allied activities": "AGR",
    "agriculture & allied activities": "AGR",
    "agriculture & allied": "AGR",
    "agriculture and allied": "AGR",
    "art": "ART",
    "artisan": "ART",
    "artisans": "ART",
    "craft": "ART",
    "crafts": "ART",
    "traditional crafts": "ART",
    "artisans and traditional crafts": "ART",
    "artisans & traditional crafts": "ART",
}


class SchemeRepository:
    """Repository handling all database queries for schemes.
    
    Contains pure SQL/ORM operations with no HTTP or business logic.
    """

    @staticmethod
    def get_by_id(db: Session, scheme_id: int) -> Optional[Scheme]:
        """Fetch a single scheme by primary key ID with eager-loaded relationships."""
        return (
            db.query(Scheme)
            .options(
                selectinload(Scheme.eligibility_criteria),
                selectinload(Scheme.sectors_mapped),
            )
            .filter(Scheme.id == scheme_id)
            .first()
        )

    @staticmethod
    def count(db: Session) -> int:
        """Count total schemes currently in the database."""
        return db.query(Scheme).count()

    @staticmethod
    def get_all(
        db: Session,
        filters: Optional[SchemeQueryParams] = None,
    ) -> List[Scheme]:
        """Query schemes applying optional filters and pagination."""
        query = db.query(Scheme).options(
            selectinload(Scheme.eligibility_criteria),
            selectinload(Scheme.sectors_mapped),
        )

        if filters:
            # 1. State filter
            if filters.state:
                state_clean = filters.state.strip().lower()
                if state_clean == "all india" or not filters.include_all_india:
                    query = query.filter(func.lower(Scheme.state).like(f"%{state_clean}%"))
                else:
                    query = query.filter(
                        or_(
                            func.lower(Scheme.state).like(f"%{state_clean}%"),
                            func.lower(Scheme.state) == "all india",
                        )
                    )

            # 2. Sector filter (checks canonical normalized sectors, sector codes, and legacy string fields)
            if filters.sector:
                sector_clean = filters.sector.strip().lower()
                sector_code = CANONICAL_SECTOR_CODES.get(sector_clean)

                sector_clauses = [
                    # Normalized relational matches by canonical sector name
                    Scheme.sectors_mapped.any(func.lower(Sector.sector_name).like(f"%{sector_clean}%")),
                    # Normalized relational matches by sector code
                    Scheme.sectors_mapped.any(func.lower(Sector.sector_code) == sector_clean),
                    # Legacy compatibility: raw column match on schemes.sector
                    func.lower(Scheme.sector).like(f"%{sector_clean}%"),
                    # Legacy compatibility: raw string match on schemes.business_type
                    func.lower(Scheme.business_type).like(f"%{sector_clean}%"),
                ]
                if sector_code:
                    sector_clauses.append(
                        Scheme.sectors_mapped.any(Sector.sector_code == sector_code)
                    )

                query = query.filter(or_(*sector_clauses))

            # 3. Scheme Type filter (handles 'Credit' <-> 'loan' synonymy)
            if filters.scheme_type:
                stype_clean = filters.scheme_type.strip().lower()
                if stype_clean in ["credit", "loan"]:
                    query = query.filter(
                        or_(
                            func.lower(Scheme.scheme_type).like("%loan%"),
                            func.lower(Scheme.scheme_type).like("%credit%"),
                        )
                    )
                else:
                    query = query.filter(func.lower(Scheme.scheme_type).like(f"%{stype_clean}%"))

            # 4. Category filter
            if filters.category:
                cat_clean = filters.category.strip().lower()
                query = query.filter(func.lower(Scheme.category).like(f"%{cat_clean}%"))

            # 5. Target group filter
            if filters.target_group:
                tg_clean = filters.target_group.strip().lower()
                query = query.filter(func.lower(Scheme.target_group).like(f"%{tg_clean}%"))

            # 6. Business type filter
            if filters.business_type:
                bt_clean = filters.business_type.strip().lower()
                query = query.filter(func.lower(Scheme.business_type).like(f"%{bt_clean}%"))

            # 7. Target gender filter
            if filters.target_gender:
                gender_clean = filters.target_gender.strip().lower()
                query = query.filter(
                    or_(
                        func.lower(Scheme.target_gender).like(f"%{gender_clean}%"),
                        func.lower(Scheme.target_gender) == "all",
                    )
                )

            # 8. Rural only boolean filter
            if filters.rural_only is not None:
                query = query.filter(Scheme.rural_only == filters.rural_only)

        query = query.order_by(Scheme.id.asc())

        if filters:
            # Pagination
            query = query.offset(filters.skip).limit(filters.limit)

        return query.all()


scheme_repository = SchemeRepository()
