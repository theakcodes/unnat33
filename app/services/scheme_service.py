from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import SchemeNotFoundException
from app.repositories.scheme_repository import scheme_repository
from app.schemas.scheme import SchemeQueryParams, SchemeResponse


class SchemeService:
    """Service class encapsulating business logic for government schemes."""

    @staticmethod
    def get_schemes(
        db: Session,
        filters: SchemeQueryParams,
    ) -> List[SchemeResponse]:
        """Retrieve schemes applying business filter rules and pagination."""
        schemes = scheme_repository.get_all(db, filters=filters)
        return [SchemeResponse.model_validate(s) for s in schemes]

    @staticmethod
    def get_scheme_by_id(db: Session, scheme_id: int) -> SchemeResponse:
        """Retrieve a specific scheme by ID or raise SchemeNotFoundException."""
        scheme = scheme_repository.get_by_id(db, scheme_id=scheme_id)
        if not scheme:
            raise SchemeNotFoundException(scheme_id=scheme_id)
        return SchemeResponse.model_validate(scheme)


scheme_service = SchemeService()
