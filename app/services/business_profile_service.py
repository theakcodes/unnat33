from typing import List
from fastapi import status
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.business_profile import BusinessProfile
from app.repositories.business_profile_repository import business_profile_repository
from app.repositories.user_repository import user_repository
from app.schemas.business_profile import BusinessProfileCreate, BusinessProfileUpdate


class BusinessProfileService:
    """Business logic for Business Profile operations."""

    @staticmethod
    def create_profile(
        db: Session,
        user_id: int,
        profile_in: BusinessProfileCreate,
    ) -> BusinessProfile:
        user = user_repository.get_by_id(db, user_id=user_id)
        if not user:
            raise AppException(
                message=f"User with ID {user_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if profile_in.udyam_registration_number:
            existing = business_profile_repository.get_by_udyam(
                db, udyam_number=profile_in.udyam_registration_number
            )
            if existing:
                raise AppException(
                    message=f"A business profile with UDYAM number '{profile_in.udyam_registration_number}' already exists",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        return business_profile_repository.create(db, user_id=user_id, profile_in=profile_in)

    @staticmethod
    def get_profile_by_id(db: Session, profile_id: int) -> BusinessProfile:
        profile = business_profile_repository.get_by_id(db, profile_id=profile_id)
        if not profile:
            raise AppException(
                message=f"Business profile with ID {profile_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return profile

    @staticmethod
    def get_profiles_for_user(db: Session, user_id: int) -> List[BusinessProfile]:
        user = user_repository.get_by_id(db, user_id=user_id)
        if not user:
            raise AppException(
                message=f"User with ID {user_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return business_profile_repository.get_by_user_id(db, user_id=user_id)

    @staticmethod
    def update_profile(
        db: Session,
        profile_id: int,
        profile_in: BusinessProfileUpdate,
    ) -> BusinessProfile:
        db_profile = BusinessProfileService.get_profile_by_id(db, profile_id=profile_id)

        if profile_in.udyam_registration_number:
            udyam_clean = profile_in.udyam_registration_number.strip().upper()
            if udyam_clean != (db_profile.udyam_registration_number or ""):
                existing = business_profile_repository.get_by_udyam(db, udyam_number=udyam_clean)
                if existing and existing.id != profile_id:
                    raise AppException(
                        message=f"UDYAM number '{profile_in.udyam_registration_number}' is already registered to another profile",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

        return business_profile_repository.update(db, db_profile=db_profile, profile_in=profile_in)


business_profile_service = BusinessProfileService()
