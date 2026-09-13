"""
app/schemas/market_research.py

Structured Pydantic schemas for the AI Market Research Intelligence Layer:
- MarketResearchEvidence: Complete evidence package assembled from real district data, ML clustering,
  NearestNeighbors comparable districts, and weather activity impact.
- Structured qualitative models for Customer Segments, Competition Assessment, and Business Strategy.
- Anti-fabrication guarantees: Zero fabricated customer counts, market shares, or unit prices.
- Strict provenance tracking across all analytical dimensions.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class MarketResearchEvidence(BaseModel):
    """
    Complete, authoritative evidence package provided to the AI synthesis engine.
    Contains strictly real or verified upstream model outputs.
    """
    model_config = ConfigDict(from_attributes=True)

    # District & Geography
    district_name: str
    state_name: str
    lg_dt_code: Optional[str] = None

    # Business Profile Context
    business_type: str = "General Enterprise"
    sub_type: Optional[str] = None
    target_market: Optional[str] = None
    experience_level: Optional[str] = None
    estimated_capital: Optional[float] = None
    current_income: Optional[float] = None

    # Real District MSME Census (PostgreSQL)
    total_msmes: int = 0
    micro_enterprises: int = 0
    small_enterprises: int = 0
    medium_enterprises: int = 0
    micro_share: float = 0.0
    small_medium_share: float = 0.0
    national_rank: Optional[int] = None
    state_rank: Optional[int] = None

    # ML Clustering Archetype
    cluster_id: Optional[int] = None
    cluster_label: Optional[str] = None
    cluster_description: Optional[str] = None
    market_research_indicator: Optional[float] = None

    # NearestNeighbors Comparable Markets
    comparable_districts_summary: List[str] = Field(
        default_factory=list,
        description="Top comparable districts with Euclidean distances and structural profiles",
    )

    # Weather / Activity Impact
    weather_condition: Optional[str] = None
    activity_impact_score: Optional[float] = None
    activity_impact_label: Optional[str] = None
    weather_risk_signals: Optional[Dict[str, str]] = None


class QualitativeAssessmentField(BaseModel):
    """Structured qualitative analytical observation with reasoning and provenance."""
    model_config = ConfigDict(from_attributes=True)

    assessment: str = Field(..., description="Qualitative summary statement")
    reasoning: str = Field(..., description="Data-grounded justification referencing evidence package")
    provenance: str = Field(default="AI INTERPRETATION", description="Data provenance classification")


class CustomerSegmentItem(BaseModel):
    """Structured customer segment profile."""
    model_config = ConfigDict(from_attributes=True)

    segment: str = Field(..., description="Segment name (e.g. 'Local Retail Consumers', 'Regional Wholesalers')")
    need: str = Field(..., description="Primary functional or commercial requirement")
    buying_consideration: str = Field(..., description="Key factor influencing purchase decision")
    recommended_channel: str = Field(..., description="Direct or indirect distribution channel")
    provenance: str = Field(default="AI INTERPRETATION", description="Data provenance classification")


class CompetitionAssessmentField(BaseModel):
    """Structured competition and market structure evaluation."""
    model_config = ConfigDict(from_attributes=True)

    competition_level: str = Field(
        ..., description="Qualitative competition intensity: 'Low', 'Moderate', 'High', or 'Very High'"
    )
    competition_reasoning: str = Field(..., description="Data-grounded reasoning based on MSME volume and density")
    market_fragmentation: str = Field(
        ..., description="Market concentration profile (e.g. 'Highly fragmented unorganized sector')"
    )
    differentiation_opportunities: List[str] = Field(
        default_factory=list, description="Defensible product, service, or packaging differentiation vectors"
    )
    research_gaps: List[str] = Field(
        default_factory=list,
        description="Explicit gaps in unorganized local market data requiring field survey verification",
    )
    provenance: str = Field(default="AI INTERPRETATION", description="Data provenance classification")


class BusinessStrategyAnalysis(BaseModel):
    """Actionable go-to-market and operational strategy."""
    model_config = ConfigDict(from_attributes=True)

    positioning_strategy: str = Field(..., description="Strategic market positioning statement")
    pricing_approach: str = Field(
        ...,
        description="Pricing framework (e.g. Cost-plus margin, Tiered wholesale/retail; zero fabricated prices)",
    )
    sales_channels: List[str] = Field(
        default_factory=list, description="Targeted physical and digital go-to-market channels"
    )
    customer_acquisition_methods: List[str] = Field(
        default_factory=list, description="Pragmatic customer outreach and relationship acquisition techniques"
    )
    operational_priorities: List[str] = Field(
        default_factory=list, description="Critical operational milestones for first 90 days"
    )
    risk_mitigations: List[str] = Field(
        default_factory=list, description="Operational and climatic contingency procedures"
    )
    provenance: str = Field(default="AI INTERPRETATION", description="Data provenance classification")


class MarketResearchAnalysis(BaseModel):
    """Unified structured market research synthesis generated from evidence package."""
    model_config = ConfigDict(from_attributes=True)

    demand_drivers: List[str] = Field(default_factory=list, description="Key local and regional demand drivers")
    market_barriers: List[str] = Field(default_factory=list, description="Regulatory, capital, or supply chain barriers")
    target_customer_segments: List[CustomerSegmentItem] = Field(
        default_factory=list, description="Identified customer personas/segments"
    )
    competition_assessment: CompetitionAssessmentField = Field(
        ..., description="Market structure and competitive analysis"
    )
    business_strategy: BusinessStrategyAnalysis = Field(
        ..., description="Actionable strategy, positioning, and operations"
    )
    research_gaps: List[str] = Field(
        default_factory=list,
        description="Data limitations or required local checks before commercial launch",
    )
    provenance: str = Field(default="AI INTERPRETATION", description="Data provenance classification")
