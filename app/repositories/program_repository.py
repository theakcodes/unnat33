from typing import List, Optional, Union
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.program_models import (
    GovernmentProgram,
    UnifiedProgramSector,
)
from app.models.scheme import Scheme
from app.schemas.program import ProgramQueryParams

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


class ProgramRepository:
    """Repository managing queries for GovernmentProgram and its normalized components."""

    @staticmethod
    def _base_query(db: Session):
        """Query with selectinload for all related entities, preventing N+1 queries."""
        return db.query(GovernmentProgram).options(
            selectinload(GovernmentProgram.sectors),
            selectinload(GovernmentProgram.legacy_scheme).selectinload(Scheme.sectors_mapped),
            selectinload(GovernmentProgram.legacy_scheme).selectinload(Scheme.eligibility_criteria),
            selectinload(GovernmentProgram.eligibility),
            selectinload(GovernmentProgram.credit_details),
            selectinload(GovernmentProgram.guarantee_details),
            selectinload(GovernmentProgram.subsidy_details),
        )

    @classmethod
    def get_by_id(cls, db: Session, program_id: int) -> Optional[GovernmentProgram]:
        """Fetch a single programme by integer primary key ID."""
        return cls._base_query(db).filter(GovernmentProgram.id == program_id).first()

    @classmethod
    def get_by_code(cls, db: Session, program_code: str) -> Optional[GovernmentProgram]:
        """Fetch a single programme by unique program_code."""
        return (
            cls._base_query(db)
            .filter(func.lower(GovernmentProgram.program_code) == program_code.strip().lower())
            .first()
        )

    @classmethod
    def get_by_identifier(cls, db: Session, identifier: Union[int, str]) -> Optional[GovernmentProgram]:
        """Fetch by primary key ID or program_code flexibly."""
        if isinstance(identifier, int):
            return cls.get_by_id(db, program_id=identifier)

        identifier_clean = str(identifier).strip()
        if identifier_clean.isdigit():
            # Try integer ID first, fallback to code match
            prog = cls.get_by_id(db, program_id=int(identifier_clean))
            if prog:
                return prog

        return cls.get_by_code(db, program_code=identifier_clean)

    @staticmethod
    def count(db: Session) -> int:
        """Count total government programmes."""
        return db.query(GovernmentProgram).count()

    @classmethod
    def get_all(
        cls,
        db: Session,
        filters: Optional[ProgramQueryParams] = None,
    ) -> List[GovernmentProgram]:
        """Query government programmes applying optional filters and pagination."""
        query = cls._base_query(db)

        if filters:
            # 1. Status filter
            if filters.status:
                query = query.filter(
                    func.lower(GovernmentProgram.status) == filters.status.strip().lower()
                )

            # 2. Primary Type filter
            if filters.primary_type:
                type_clean = filters.primary_type.strip().lower()
                query = query.filter(
                    func.lower(GovernmentProgram.primary_type).like(f"%{type_clean}%")
                )

            # 3. Actionability Type filter
            if filters.actionability_type:
                act_clean = filters.actionability_type.strip().lower()
                query = query.filter(
                    func.lower(GovernmentProgram.actionability_type).like(f"%{act_clean}%")
                )

            # 4. Ministry filter
            if filters.ministry:
                ministry_clean = filters.ministry.strip().lower()
                query = query.filter(
                    func.lower(GovernmentProgram.owning_ministry).like(f"%{ministry_clean}%")
                )

            # 5. Sector filter (leverages UnifiedProgramSector view for both legacy and new programmes)
            if filters.sector:
                sector_clean = filters.sector.strip().lower()
                canonical_code = CANONICAL_SECTOR_CODES.get(sector_clean)

                sector_clauses = [
                    func.lower(UnifiedProgramSector.sector_name).like(f"%{sector_clean}%"),
                    func.lower(UnifiedProgramSector.sector_code) == sector_clean,
                ]
                if canonical_code:
                    sector_clauses.append(
                        func.lower(UnifiedProgramSector.sector_code) == canonical_code.lower()
                    )

                matching_ids_select = (
                    select(UnifiedProgramSector.program_id)
                    .filter(or_(*sector_clauses))
                    .distinct()
                )
                query = query.filter(GovernmentProgram.id.in_(matching_ids_select))

            # Pagination & Deterministic Sorting
            skip = max(0, filters.skip)
            limit = max(1, min(100, filters.limit))
            query = query.order_by(GovernmentProgram.id).offset(skip).limit(limit)
        else:
            query = query.order_by(GovernmentProgram.id).limit(100)

        return query.all()


program_repository = ProgramRepository()
