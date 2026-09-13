from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.eligibility import UserProfile
from app.schemas.district_msme import DistrictMarketContext


class ScoringBreakdown(BaseModel):
    """Component-level score breakdown for explainability."""
    model_config = ConfigDict(from_attributes=True)

    eligibility_confidence_score: float = Field(..., description="Score for statutory eligibility status (0 to 20 pts)")
    financial_fit_score: float = Field(..., description="Score for loan/project cost alignment and subsidies (0 to 25 pts)")
    sector_fit_score: float = Field(..., description="Score for canonical sector compatibility (0 to 20 pts)")
    actionability_score: float = Field(..., description="Score for scheme actionability classification (0 to 15 pts)")
    beneficiary_stage_score: float = Field(..., description="Score for target demographic & business stage fit (0 to 10 pts)")
    market_context_score: float = Field(..., description="Score for empirical district scale & enterprise density (0 to 10 pts)")
    total_score: float = Field(..., description="Aggregate recommendation score (0 to 100 pts)")


class ProgramRecommendationItem(BaseModel):
    """Individual ranked programme recommendation with traceable drivers."""
    model_config = ConfigDict(from_attributes=True)

    rank: int = Field(..., description="Recommendation priority rank (1 = highest priority)")
    program_id: int = Field(..., description="Government programme database ID")
    program_code: str = Field(..., description="Standard unique programme code")
    program_name: str = Field(..., description="Official government programme title")
    primary_type: str = Field(..., description="Primary assistance classification")
    actionability_type: str = Field(..., description="Actionability classification")
    eligibility_status: str = Field(..., description="'Eligible' or 'Partially Verified'")
    recommendation_score: float = Field(..., description="Transparent recommendation score (0.0 to 100.0)")
    fit_category: str = Field(..., description="'EXCELLENT_FIT', 'STRONG_FIT', 'MODERATE_FIT', or 'LOW_FIT'")
    scoring_breakdown: ScoringBreakdown = Field(..., description="Independent component score breakdown")
    recommendation_drivers: List[str] = Field(default_factory=list, description="Traceable positive factors driving this recommendation")
    cautionary_notes: List[str] = Field(default_factory=list, description="Statutory or operational caveats (e.g. unverified criteria)")
    official_portal_url: Optional[str] = Field(None, description="Official government portal URL")
    benefit_summary: Optional[str] = Field(None, description="Headline benefit summary")


class RecommendationRequest(BaseModel):
    """Request schema for generating recommendations."""
    model_config = ConfigDict(extra="ignore")

    business_profile_id: Optional[int] = Field(None, description="Optional existing business profile ID from database")
    profile: Optional[UserProfile] = Field(None, description="Optional inline UserProfile attributes")
    target_financing_need: Optional[float] = Field(None, ge=0, description="Desired financing or project funding amount in INR")
    preferred_assistance_type: Optional[str] = Field(None, description="Optional filter: 'CREDIT / LOAN', 'SUBSIDY', 'CREDIT GUARANTEE', etc.")
    top_k: int = Field(10, ge=1, le=60, description="Maximum number of recommendations to return (1 to 60)")


class RecommendationResponse(BaseModel):
    """Authoritative recommendation assessment response."""
    model_config = ConfigDict(from_attributes=True)

    total_programs_evaluated: int = Field(..., description="Total statutory programmes evaluated (e.g. 60)")
    eligible_candidates_count: int = Field(..., description="Candidates with status 'Eligible'")
    partially_verified_candidates_count: int = Field(..., description="Candidates with status 'Partially Verified'")
    total_recommended: int = Field(..., description="Number of ranked programmes returned in this response")
    district_market_context: Optional[DistrictMarketContext] = Field(None, description="Empirical district MSME market indicators")
    recommendations: List[ProgramRecommendationItem] = Field(default_factory=list, description="Ranked, scored recommendations sorted descending by score")
