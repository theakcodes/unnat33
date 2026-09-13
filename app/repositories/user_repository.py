from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """Repository handling all database queries for Users."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.strip().lower()).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 50) -> List[User]:
        return db.query(User).order_by(User.id.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user_in: UserCreate, hashed_password: Optional[str] = None) -> User:
        db_user = User(
            email=user_in.email.strip().lower(),
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            phone_number=user_in.phone_number,
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(db: Session, db_user: User, user_in: UserUpdate, hashed_password: Optional[str] = None) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            del update_data["password"]
        if hashed_password:
            db_user.hashed_password = hashed_password

        for field, value in update_data.items():
            if field == "email" and value:
                value = value.strip().lower()
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user


user_repository = UserRepository()
