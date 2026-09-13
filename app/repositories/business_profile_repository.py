from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.business_profile import BusinessProfile
from app.schemas.business_profile import BusinessProfileCreate, BusinessProfileUpdate


class BusinessProfileRepository:
    """Repository handling all database queries for Business Profiles."""

    @staticmethod
    def get_by_id(db: Session, profile_id: int) -> Optional[BusinessProfile]:
        return db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()

    @staticmethod
    def get_by_udyam(db: Session, udyam_number: str) -> Optional[BusinessProfile]:
        return db.query(BusinessProfile).filter(
            BusinessProfile.udyam_registration_number == udyam_number.strip().upper()
        ).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> List[BusinessProfile]:
        return (
            db.query(BusinessProfile)
            .filter(BusinessProfile.user_id == user_id)
            .order_by(BusinessProfile.id.asc())
            .all()
        )

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 50) -> List[BusinessProfile]:
        return db.query(BusinessProfile).order_by(BusinessProfile.id.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user_id: int, profile_in: BusinessProfileCreate) -> BusinessProfile:
        data = profile_in.model_dump()
        if data.get("udyam_registration_number"):
            data["udyam_registration_number"] = data["udyam_registration_number"].strip().upper()

        db_profile = BusinessProfile(user_id=user_id, **data)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def update(
        db: Session,
        db_profile: BusinessProfile,
        profile_in: BusinessProfileUpdate,
    ) -> BusinessProfile:
        update_data = profile_in.model_dump(exclude_unset=True)
        if "udyam_registration_number" in update_data and update_data["udyam_registration_number"]:
            update_data["udyam_registration_number"] = update_data["udyam_registration_number"].strip().upper()

        for field, value in update_data.items():
            setattr(db_profile, field, value)

        db.commit()
        db.refresh(db_profile)
        return db_profile


business_profile_repository = BusinessProfileRepository()
