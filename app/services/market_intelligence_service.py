"""
app/services/market_intelligence_service.py

Unified Market Intelligence Orchestration Service:
- Orchestrates the full quantitative and qualitative market intelligence pipeline:
  1. Real Udyam MSME market metrics & ranks from PostgreSQL (via ResearchContextService)
  2. Official centroid coordinates & elevation from PostgreSQL
  3. Real-time atmospheric observations and 3-day forecast from Open-Meteo
  4. Quantitative market clustering (KMeans, K=4) & indicator scoring from scikit-learn
  5. Qualitative market interpretations, opportunities, and risks via server-side Anthropic Claude / deterministic fallback
- Failure Isolation: Ensures ML, LLM, and Open-Meteo failures isolate gracefully without breaking the combined response.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.market_intelligence import (
    MarketIntelligenceRequest,
    MarketIntelligenceResponse,
    BusinessProfileContext,
)
from app.services.research_context_service import research_context_service, ResearchContextService
from app.services.market_research_ml_service import market_research_ml_service, MarketResearchMLService
from app.services.market_research_llm_service import market_research_llm_service, MarketResearchLLMService

logger = logging.getLogger(__name__)


class MarketIntelligenceService:
    """Service providing unified district market intelligence synthesizing PostgreSQL, ML, LLM, and Climate data."""

    def __init__(
        self,
        research_svc: Optional[ResearchContextService] = None,
        ml_svc: Optional[MarketResearchMLService] = None,
        llm_svc: Optional[MarketResearchLLMService] = None,
    ):
        self.research_service = research_svc or research_context_service
        self.ml_service = ml_svc or market_research_ml_service
        self.llm_service = llm_svc or market_research_llm_service

    async def get_market_intelligence(
        self,
        db: Session,
        req: MarketIntelligenceRequest,
    ) -> Optional[MarketIntelligenceResponse]:
        """
        Execute unified market intelligence pipeline for a target district.
        Returns None only if district cannot be resolved in either geography or MSME records.
        """
        # 1. Fetch unified research context (Geography + Udyam MSME + Weather + Baseline Observations)
        base_context = await self.research_service.get_district_research_context(
            db=db,
            district_name=req.district_name,
            state_name=req.state_name,
            lg_dt_code=req.lg_dt_code,
        )

        if not base_context:
            logger.warning(
                "District research context unresolvable for district=%s, state=%s, code=%s",
                req.district_name,
                req.state_name,
                req.lg_dt_code,
            )
            return None

        # 2. Run scikit-learn ML Clustering Pipeline (with Failure Isolation)
        try:
            ml_analysis = self.ml_service.get_analysis_for_district(
                db=db,
                district_id=base_context.district_id,
                market_context=base_context.msme_market_context,
            )
        except Exception as e:
            logger.error("ML service execution failed: %s", e, exc_info=True)
            ml_analysis = self.ml_service._build_fallback_analysis(base_context.msme_market_context)

        # 3. Run Server-Side LLM Qualitative Pipeline (with Failure Isolation)
        try:
            llm_analysis = await self.llm_service.generate_qualitative_analysis(
                district_name=base_context.district_name,
                state_name=base_context.state_name,
                market_context=base_context.msme_market_context,
                ml_analysis=ml_analysis,
                weather_context=base_context.weather_context,
                business_profile=req.business_profile,
                operational_cautions=base_context.operational_cautions,
            )
        except Exception as e:
            logger.error("LLM service execution failed: %s", e, exc_info=True)
            llm_analysis = self.llm_service._generate_deterministic_fallback(
                district_name=base_context.district_name,
                state_name=base_context.state_name,
                market_context=base_context.msme_market_context,
                ml_analysis=ml_analysis,
                weather_context=base_context.weather_context,
                business_profile=req.business_profile,
                operational_cautions=base_context.operational_cautions,
            )

        # 4. Synthesize Combined Response
        return MarketIntelligenceResponse(
            district_id=base_context.district_id,
            district_name=base_context.district_name,
            state_name=base_context.state_name,
            lg_dt_code=base_context.lg_dt_code,
            geographic_coordinates=base_context.geographic_coordinates,
            market_context=base_context.msme_market_context,
            weather_context=base_context.weather_context,
            ml_analysis=ml_analysis,
            llm_analysis=llm_analysis,
            research_observations=base_context.research_observations,
            operational_cautions=base_context.operational_cautions,
            disclaimer=base_context.disclaimer,
        )


# Singleton Instance
market_intelligence_service = MarketIntelligenceService()
