from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.program import (
    ProgramQueryParams,
    ProgramResponse,
    ProgramDetailResponse,
)
from app.schemas.eligibility import (
    UserProfile,
    ProgramEligibilityAssessmentResponse,
)
from app.services.program_service import program_service
from app.services.eligibility_service import eligibility_service

router = APIRouter(prefix="/programs", tags=["Government Programmes"])



@router.get(
    "",
    response_model=List[ProgramResponse],
    status_code=status.HTTP_200_OK,
    summary="List government programmes with filtering and pagination",
)
def get_programs(
    status_param: Optional[str] = Query(None, alias="status", description="Filter by operational status (e.g. 'active')"),
    primary_type: Optional[str] = Query(None, description="Filter by primary type (e.g. 'CREDIT / LOAN', 'CREDIT GUARANTEE', 'SUBSIDY / CAPITAL ASSISTANCE')"),
    actionability_type: Optional[str] = Query(None, description="Filter by actionability type (e.g. 'DIRECT_BENEFICIARY', 'INSTITUTIONAL')"),
    ministry: Optional[str] = Query(None, description="Filter by owning ministry"),
    sector: Optional[str] = Query(None, description="Filter by sector code or name (e.g. 'MFG', 'Agriculture')"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (up to 100)"),
    db: Session = Depends(get_db),
) -> List[ProgramResponse]:
    """Retrieve government programmes applying optional multi-attribute filters and pagination."""
    filters = ProgramQueryParams(
        status=status_param,
        primary_type=primary_type,
        actionability_type=actionability_type,
        ministry=ministry,
        sector=sector,
        skip=skip,
        limit=limit,
    )
    return program_service.get_programs(db=db, filters=filters)


@router.get(
    "/{program_id}",
    response_model=ProgramDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single government programme by ID or program code",
)
def get_program_by_id(
    program_id: str,
    db: Session = Depends(get_db),
) -> ProgramDetailResponse:
    """Retrieve detailed government programme information by primary key ID or unique programme code."""
    return program_service.get_program_by_identifier(db=db, identifier=program_id)


@router.post(
    "/evaluate-eligibility",
    response_model=ProgramEligibilityAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate user/business profile against all 60 government programmes using deterministic rules",
)
def evaluate_program_eligibility(
    profile: UserProfile,
    db: Session = Depends(get_db),
) -> ProgramEligibilityAssessmentResponse:
    """Evaluate profile eligibility deterministically against all 60 active government programmes.
    
    This is the rule-based statutory eligibility engine that precedes ML ranking.
    """
    return eligibility_service.evaluate_all_programs(db=db, profile=profile)

