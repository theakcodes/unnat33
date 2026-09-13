from typing import List
from fastapi import status
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Business logic for User operations."""

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        existing = user_repository.get_by_email(db, email=user_in.email)
        if existing:
            raise AppException(
                message=f"User with email '{user_in.email}' is already registered",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        hashed_password = None
        if user_in.password:
            hashed_password = get_password_hash(user_in.password)

        return user_repository.create(db, user_in=user_in, hashed_password=hashed_password)

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = user_repository.get_by_id(db, user_id=user_id)
        if not user:
            raise AppException(
                message=f"User with ID {user_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return user

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 50) -> List[User]:
        return user_repository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
        db_user = UserService.get_user_by_id(db, user_id=user_id)

        if user_in.email and user_in.email.strip().lower() != db_user.email.lower():
            existing = user_repository.get_by_email(db, email=user_in.email)
            if existing and existing.id != user_id:
                raise AppException(
                    message=f"Email '{user_in.email}' is already in use by another user",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        hashed_password = None
        if user_in.password:
            hashed_password = get_password_hash(user_in.password)

        return user_repository.update(db, db_user=db_user, user_in=user_in, hashed_password=hashed_password)


user_service = UserService()
