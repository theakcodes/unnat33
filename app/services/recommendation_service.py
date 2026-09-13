"""
app/services/recommendation_service.py

Authoritative Recommendation Service for MSME government programmes.

Architectural Guarantees:
1. Statutory Eligibility is a strict hard-gate via EligibilityService.evaluate_all_programs().
   Ineligible programmes are completely filtered out and NEVER recommended.
2. Zero ML, zero LLM, zero external API dependencies.
3. Transparent 100-point multi-component scoring via RecommendationScorer.
4. Seamless integration with empirical district MSME records from DistrictMsmeService.
5. Deterministic sorting and explainable drivers/notes for every recommendation.
"""

from typing import Optional, List, Dict, Any
from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.schemas.eligibility import UserProfile
from app.schemas.district_msme import DistrictMarketContext
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    ProgramRecommendationItem,
)
from app.repositories.business_profile_repository import business_profile_repository
from app.repositories.program_repository import program_repository
from app.services.eligibility_service import eligibility_service
from app.services.program_eligibility_adapter import ProgramEligibilityAdapter
from app.services.district_msme_service import district_msme_service
from app.services.recommendation_scorer import recommendation_scorer


class RecommendationService:
    """Service orchestrating statutory filtering, market context enrichment, and programme recommendation."""

    @classmethod
    def generate_recommendations(
        cls,
        db: Session,
        request: RecommendationRequest,
    ) -> RecommendationResponse:
        """Generate ranked, scored programme recommendations for an enterprise profile."""
        # 1. Resolve Profile
        profile = cls._resolve_profile(db, request)

        # 2. Resolve Target Financing Need
        target_financing = request.target_financing_need
        if target_financing is not None and target_financing > 0:
            if profile.requested_loan_amount is None:
                profile.requested_loan_amount = target_financing
        else:
            target_financing = profile.requested_loan_amount or profile.project_cost

        # 3. Retrieve Empirical District Market Context
        market_context: Optional[DistrictMarketContext] = district_msme_service.get_market_context(
            db=db,
            district_name=profile.district,
            state_name=profile.state,
        )

        # 4. HARD GATE: Evaluate Statutory Eligibility deterministically
        elig_assessment = eligibility_service.evaluate_all_programs(db, profile)

        # Filter candidate pool: Admit Eligible and Partially Verified; DISCARD Ineligible
        candidates = list(elig_assessment.eligible_programs) + list(elig_assessment.partially_verified_programs)

        # 5. Optional Filter by Preferred Assistance Type
        if request.preferred_assistance_type:
            pref = request.preferred_assistance_type.strip().lower()
            matching = [c for c in candidates if pref in (c.primary_type or "").lower()]
            if matching:
                candidates = matching

        # 6. Score Qualified Candidates
        all_programs = program_repository.get_all(db)
        programs_by_id = {p.id: p for p in all_programs}

        scored_items: List[ProgramRecommendationItem] = []
        for candidate in candidates:
            prog_entity = programs_by_id.get(candidate.program_id)
            if not prog_entity:
                continue

            eval_prog = ProgramEligibilityAdapter.adapt(prog_entity)
            item = recommendation_scorer.calculate_score(
                eval_prog=eval_prog,
                profile=profile,
                market_context=market_context,
                target_amount=target_financing,
                eligibility_status=candidate.status,
                unverified_criteria=candidate.unverified_criteria,
            )
            scored_items.append(item)

        # 7. Deterministic Sorting: Primary by total score DESC, secondary by confidence DESC, tie-break by program_id ASC
        scored_items.sort(
            key=lambda x: (
                -x.recommendation_score,
                -x.scoring_breakdown.eligibility_confidence_score,
                x.program_id,
            )
        )

        # 8. Truncate to top_k and assign ranks
        top_k_items = scored_items[: request.top_k]
        for idx, item in enumerate(top_k_items, start=1):
            item.rank = idx

        return RecommendationResponse(
            total_programs_evaluated=elig_assessment.total_evaluated,
            eligible_candidates_count=elig_assessment.total_eligible,
            partially_verified_candidates_count=elig_assessment.total_partially_verified,
            total_recommended=len(top_k_items),
            district_market_context=market_context,
            recommendations=top_k_items,
        )

    @classmethod
    def _resolve_profile(cls, db: Session, request: RecommendationRequest) -> UserProfile:
        """Resolve UserProfile from business_profile_id or inline profile payload."""
        if request.business_profile_id:
            bp = business_profile_repository.get_by_id(db, profile_id=request.business_profile_id)
            if not bp:
                raise AppException(
                    message=f"Business profile with ID {request.business_profile_id} not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # Map database BusinessProfile to UserProfile
            profile_data: Dict[str, Any] = {
                "state": bp.state,
                "district": bp.district,
                "is_rural": bp.is_rural,
                "sector": bp.sector,
                "annual_income": float(bp.annual_turnover) if bp.annual_turnover is not None else None,
                "project_cost": float(bp.investment_in_plant) if bp.investment_in_plant is not None else None,
            }

            # Overlay explicit inline fields if provided
            if request.profile:
                user_dict = request.profile.model_dump(exclude_unset=True)
                profile_data.update(user_dict)

            return UserProfile(**profile_data)

        if request.profile:
            return request.profile

        raise AppException(
            message="Either 'business_profile_id' or 'profile' must be provided to generate recommendations.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


recommendation_service = RecommendationService()
