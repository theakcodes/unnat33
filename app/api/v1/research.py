"""
app/api/v1/research.py

Research Intelligence API endpoints:
- GET /api/v1/research/district-market-context: Unified district geographic, MSME market, and weather context.

IMPORTANT ARCHITECTURAL INVARIANT:
External geography and weather data are research context only.
They do NOT alter recommendation scores or determine statutory scheme eligibility.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.research_context import DistrictResearchContextResponse
from app.schemas.market_intelligence import MarketIntelligenceRequest, MarketIntelligenceResponse
from app.services.research_context_service import research_context_service
from app.services.market_intelligence_service import market_intelligence_service
from app.services.weather_business_impact_service import weather_business_impact_service
from app.services.market_similarity_service import market_similarity_service

router = APIRouter(prefix="/research", tags=["Research Intelligence"])


@router.get(
    "/district-market-context",
    response_model=DistrictResearchContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unified district research intelligence context",
)
async def get_district_market_context(
    district_name: Optional[str] = Query(
        None, description="Official or colloquial district name (e.g. 'Varanasi', 'Pune')"
    ),
    state_name: Optional[str] = Query(
        None, description="Canonical State / UT name (e.g. 'Uttar Pradesh', 'Maharashtra')"
    ),
    lg_dt_code: Optional[str] = Query(
        None, description="Official Local Government Directory (LGD) district code (e.g. '194')"
    ),
    db: Session = Depends(get_db),
) -> DistrictResearchContextResponse:
    """
    Retrieve unified research intelligence for an Indian district.
    Aggregates:
    - Official geographic centroid coordinates and elevation from PostgreSQL.
    - Empirical Udyam MSME market density, composition shares, and rankings.
    - Observational weather conditions and 3-day forecast snapshots from Open-Meteo / DB cache.
    - Defensible, data-backed operational observations and cautions.

    At least one parameter (`district_name`, `state_name`, or `lg_dt_code`) must be provided.
    """
    if not district_name and not state_name and not lg_dt_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one parameter (district_name, state_name, or lg_dt_code) must be provided.",
        )

    context = await research_context_service.get_district_research_context(
        db=db,
        district_name=district_name,
        state_name=state_name,
        lg_dt_code=lg_dt_code,
    )

    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"District research context not found for district='{district_name}', state='{state_name}', lg_dt_code='{lg_dt_code}'.",
        )

    return context


@router.post(
    "/market-intelligence",
    response_model=MarketIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unified district market intelligence synthesizing ML clustering and qualitative LLM pipelines",
)
async def get_market_intelligence(
    payload: MarketIntelligenceRequest,
    db: Session = Depends(get_db),
) -> MarketIntelligenceResponse:
    """
    Unified District Market Intelligence:
    - Synthesizes PostgreSQL Udyam MSME census metrics and geographic centroid coordinates.
    - Observational weather conditions and 3-day forecast snapshots from Open-Meteo.
    - Quantitative scikit-learn KMeans market clustering (K=4) & documented Market Research Indicator.
    - Qualitative market interpretations, opportunities, operational considerations, and risks via
      server-side Anthropic Claude / resilient deterministic fallback.
    """
    if not payload.district_name and not payload.state_name and not payload.lg_dt_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one parameter (district_name, state_name, or lg_dt_code) must be provided in request body.",
        )

    intel = await market_intelligence_service.get_market_intelligence(db=db, req=payload)
    if not intel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market intelligence not found for district='{payload.district_name}', state='{payload.state_name}'.",
        )

    # Enrich with Indicative Weather Activity Impact heuristic layer (Failure-isolated)
    try:
        b_type = (
            payload.business_profile.business_type
            if payload.business_profile
            else None
        )
        intel.weather_activity_impact = weather_business_impact_service.calculate_impact(
            weather_context=intel.weather_context,
            business_type=b_type,
        )
    except Exception as e:
        # Weather calculation failure must not break core MSME or ML market intelligence
        pass

    # Enrich with scikit-learn NearestNeighbors Comparable Markets (Failure-isolated)
    try:
        intel.comparable_markets = market_similarity_service.get_comparable_markets(
            db=db,
            district_name=payload.district_name,
            state_name=payload.state_name,
            lg_dt_code=payload.lg_dt_code,
            market_context=intel.market_context,
        )
    except Exception as e:
        # Similarity calculation failure must not break core MSME or ML market intelligence
        pass

    return intel

