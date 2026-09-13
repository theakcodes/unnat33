from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.business_profile import (
    BusinessProfileCreate,
    BusinessProfileResponse,
)
from app.services.user_service import user_service
from app.services.business_profile_service import business_profile_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Register a new platform user with Argon2 password hashing."""
    user = user_service.create_user(db, user_in=user_in)
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List users",
)
def list_users(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db),
) -> List[UserResponse]:
    """Retrieve users with pagination."""
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Retrieve user details by ID."""
    user = user_service.get_user_by_id(db, user_id=user_id)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user details",
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update profile details for an existing user."""
    user = user_service.update_user(db, user_id=user_id, user_in=user_in)
    return UserResponse.model_validate(user)


@router.post(
    "/{user_id}/business-profiles",
    response_model=BusinessProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create business profile for user",
)
def create_business_profile_for_user(
    user_id: int,
    profile_in: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfileResponse:
    """Create and associate a new business profile with an existing user."""
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create a business profile for another user",
        )
    profile = business_profile_service.create_profile(db, user_id=user_id, profile_in=profile_in)
    return BusinessProfileResponse.model_validate(profile)


@router.get(
    "/{user_id}/business-profiles",
    response_model=List[BusinessProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="List business profiles for user",
)
def list_business_profiles_for_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[BusinessProfileResponse]:
    """List all business profiles owned by a specific user."""
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access another user's business profiles",
        )
    profiles = business_profile_service.get_profiles_for_user(db, user_id=user_id)
    return [BusinessProfileResponse.model_validate(p) for p in profiles]
