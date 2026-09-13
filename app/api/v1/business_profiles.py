from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.business_profile import (
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse,
)
from app.repositories.business_profile_repository import business_profile_repository
from app.services.business_profile_service import business_profile_service

router = APIRouter(prefix="/business-profiles", tags=["Business Profiles"])


@router.post(
    "",
    response_model=BusinessProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new business profile for authenticated user",
)
def create_my_business_profile(
    profile_in: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfileResponse:
    """Create a new business profile directly associated with the authenticated user."""
    profile = business_profile_service.create_profile(
        db, user_id=current_user.id, profile_in=profile_in
    )
    return BusinessProfileResponse.model_validate(profile)


@router.get(
    "",
    response_model=List[BusinessProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="List business profiles for authenticated user",
)
def list_my_business_profiles(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[BusinessProfileResponse]:
    """Retrieve only the business profiles owned by the currently authenticated user."""
    if current_user.is_superuser:
        profiles = business_profile_repository.get_all(db, skip=skip, limit=limit)
    else:
        profiles = business_profile_repository.get_by_user_id(db, user_id=current_user.id)
    return [BusinessProfileResponse.model_validate(p) for p in profiles]


@router.get(
    "/{profile_id}",
    response_model=BusinessProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get business profile by ID",
)
def get_business_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfileResponse:
    """Retrieve single business profile, ensuring ownership by the authenticated user."""
    profile = business_profile_service.get_profile_by_id(db, profile_id=profile_id)
    if profile.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this business profile",
        )
    return BusinessProfileResponse.model_validate(profile)


@router.put(
    "/{profile_id}",
    response_model=BusinessProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update business profile",
)
def update_business_profile(
    profile_id: int,
    profile_in: BusinessProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfileResponse:
    """Update fields on a business profile, ensuring ownership by the authenticated user."""
    profile = business_profile_service.get_profile_by_id(db, profile_id=profile_id)
    if profile.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this business profile",
        )
    updated = business_profile_service.update_profile(db, profile_id=profile_id, profile_in=profile_in)
    return BusinessProfileResponse.model_validate(updated)
