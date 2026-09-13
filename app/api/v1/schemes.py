from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.scheme import SchemeQueryParams, SchemeResponse
from app.schemas.eligibility import (
    UserProfile,
    EligibilityAssessmentResponse,
)
from app.services.scheme_service import scheme_service
from app.services.eligibility_service import eligibility_service

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get(
    "",
    response_model=List[SchemeResponse],
    status_code=status.HTTP_200_OK,
    summary="List government schemes with optional filtering",
)
def get_schemes(
    state: Optional[str] = Query(None, description="Filter by state (e.g. 'Rajasthan', 'All India')"),
    sector: Optional[str] = Query(None, description="Filter by sector (e.g. 'Manufacturing', 'Micro Enterprise')"),
    scheme_type: Optional[str] = Query(None, description="Filter by scheme type (e.g. 'loan', 'Credit')"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. 'Direct Financing')"),
    target_group: Optional[str] = Query(None, description="Filter by target group"),
    business_type: Optional[str] = Query(None, description="Filter by business activity"),
    target_gender: Optional[str] = Query(None, description="Filter by target gender"),
    rural_only: Optional[bool] = Query(None, description="Filter by rural exclusivity"),
    include_all_india: bool = Query(True, description="When filtering by specific state, also include nationwide schemes"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    db: Session = Depends(get_db),
) -> List[SchemeResponse]:
    """Retrieve government schemes with optional multi-attribute filtering and pagination."""
    filters = SchemeQueryParams(
        state=state,
        sector=sector,
        scheme_type=scheme_type,
        category=category,
        target_group=target_group,
        business_type=business_type,
        target_gender=target_gender,
        rural_only=rural_only,
        include_all_india=include_all_india,
        skip=skip,
        limit=limit,
    )
    return scheme_service.get_schemes(db=db, filters=filters)


@router.get(
    "/{scheme_id}",
    response_model=SchemeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single scheme by ID",
)
def get_scheme_by_id(
    scheme_id: int,
    db: Session = Depends(get_db),
) -> SchemeResponse:
    """Retrieve detailed information for a specific scheme by primary key ID."""
    return scheme_service.get_scheme_by_id(db=db, scheme_id=scheme_id)


@router.post(
    "/evaluate-eligibility",
    response_model=EligibilityAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate user/business profile against schemes using deterministic rules",
)
def evaluate_eligibility(
    profile: UserProfile,
    db: Session = Depends(get_db),
) -> EligibilityAssessmentResponse:
    """Evaluate profile eligibility deterministically against all active government schemes.
    
    This is the rule-based eligibility engine that precedes ML ranking.
    """
    return eligibility_service.evaluate_all(db=db, profile=profile)
