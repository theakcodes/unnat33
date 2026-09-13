"""
app/api/v1/recommendations.py

FastAPI router exposing endpoints for:
1. POST /api/v1/recommendations/recommend: Ranked, explainable government programme recommendations
2. GET /api/v1/recommendations/district-market-context: Empirical district MSME indicators from Udyam records
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.schemas.district_msme import DistrictMarketContext
from app.schemas.financial_structuring import (
    FinancialStructuringRequest,
    FinancialStructuringResponse,
)
from app.services.recommendation_service import recommendation_service
from app.services.district_msme_service import district_msme_service
from app.services.financial_structuring_service import financial_structuring_service

router = APIRouter(prefix="/recommendations", tags=["Programme Recommendations & Market Context"])



@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate ranked, explainable programme recommendations",
)
def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    """Generate deterministic, explainable government programme recommendations.
    
    Evaluates statutory eligibility as a hard gate, enriches with empirical district MSME
    market indicators, and scores qualified candidates across 6 independent dimensions.
    """
    return recommendation_service.generate_recommendations(db=db, request=request)


@router.get(
    "/district-market-context",
    response_model=DistrictMarketContext,
    status_code=status.HTTP_200_OK,
    summary="Retrieve empirical district MSME market indicators",
)
def get_district_market_context(
    district_name: Optional[str] = Query(None, description="District name (e.g. 'Pune', 'Jaipur')"),
    state_name: Optional[str] = Query(None, description="State name or code (e.g. 'Maharashtra', 'MH')"),
    lg_dt_code: Optional[str] = Query(None, description="Local Government Directory (LGD) district code (e.g. '490')"),
    db: Session = Depends(get_db),
) -> DistrictMarketContext:
    """Retrieve empirical MSME market-context indicators derived from official Udyam records.
    
    Resolves by LGD code first, then district and state name, with state-level fallback.
    """
    context = district_msme_service.get_market_context(
        db=db,
        district_name=district_name,
        state_name=state_name,
        lg_dt_code=lg_dt_code,
    )
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No MSME market records found for the specified district or state parameters.",
        )
    return context


@router.post(
    "/financial-structuring",
    response_model=FinancialStructuringResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate deterministic financial structuring and amortization scenarios",
)
def calculate_financial_structuring(
    request: FinancialStructuringRequest,
    db: Session = Depends(get_db),
) -> FinancialStructuringResponse:
    """Generate deterministic financial structuring for a government programme.
    
    Computes equity margin, statutory subsidies, bank debt, credit guarantee coverage,
    and 3-tier repayment amortization scenarios without LLM/ML intervention.
    """
    return financial_structuring_service.calculate_structure(db=db, request=request)

