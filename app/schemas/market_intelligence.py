"""
app/schemas/market_intelligence.py

Pydantic schemas for the unified Market Intelligence pipeline:
- Quantitative district MSME metrics from PostgreSQL
- Quantitative ML cluster assignments and characteristics from scikit-learn (KMeans)
- Qualitative market interpretations, opportunities, and risks from Anthropic Claude / deterministic fallback
- Integrated research observations and climate alerts
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.geography import DistrictCoordinates
from app.schemas.district_msme import DistrictMarketContext
from app.schemas.weather import DistrictWeatherContext
from app.schemas.market_similarity import ComparableMarketContext


class BusinessProfileContext(BaseModel):
    """Optional user business profile attributes provided for context-aware analysis."""
    model_config = ConfigDict(from_attributes=True)

    business_type: Optional[str] = Field(None, description="Primary sector / domain (e.g. 'Handloom', 'Food Processing')")
    sub_type: Optional[str] = Field(None, description="Specific trade sub-type or niche")
    experience_level: Optional[str] = Field(None, description="Years / level of operational experience")
    target_market: Optional[str] = Field(None, description="Target customer base (e.g. 'Local Rural', 'B2B Regional', 'Export')")
    current_income: Optional[float] = Field(None, description="Current annual revenue or income in INR")
    estimated_capital: Optional[float] = Field(None, description="Planned capital outlay or project cost in INR")
    existing_debt: Optional[float] = Field(None, description="Current outstanding debt burden in INR")
    additional_context: Optional[str] = Field(None, description="User's operational notes or strategic goals")


class MarketIntelligenceRequest(BaseModel):
    """Request payload for unified district market intelligence."""
    model_config = ConfigDict(from_attributes=True)

    district_name: Optional[str] = Field(None, description="District name (e.g. 'Varanasi', 'Pune')")
    state_name: Optional[str] = Field(None, description="State / UT name (e.g. 'Uttar Pradesh', 'Maharashtra')")
    lg_dt_code: Optional[str] = Field(None, description="Local Government Directory (LGD) district code")
    business_profile: Optional[BusinessProfileContext] = Field(
        None, description="Optional entrepreneur and business profile for contextual enrichment"
    )


class ClusterQuantitativeIndicators(BaseModel):
    """Empirical quantitative indicators and cluster baseline comparisons."""
    model_config = ConfigDict(from_attributes=True)

    total_msmes: int = Field(..., description="Total registered MSMEs in district")
    micro_enterprises: int = Field(..., description="Total Micro enterprises")
    small_enterprises: int = Field(..., description="Total Small enterprises")
    medium_enterprises: int = Field(..., description="Total Medium enterprises")
    micro_share: float = Field(..., description="Percentage of micro enterprises in district (0-100)")
    small_share: float = Field(..., description="Percentage of small enterprises in district (0-100)")
    medium_share: float = Field(..., description="Percentage of medium enterprises in district (0-100)")
    small_medium_share: float = Field(..., description="Combined percentage of small and medium enterprises (0-100)")
    
    # Normalized Percentiles & Indices
    national_density_percentile: float = Field(
        ..., description="District enterprise density percentile nationally (0-100, where 100 is highest)"
    )
    state_density_percentile: float = Field(
        ..., description="District enterprise density percentile within state (0-100, where 100 is highest)"
    )
    sme_depth_score: float = Field(
        ..., description="Normalized formalized SME supply chain depth score (0-100)"
    )
    market_research_indicator: float = Field(
        ..., description="Transparent composite market research indicator (0-100, documented weighted formula)"
    )
    
    # Cluster Baselines
    cluster_mean_total_msmes: float = Field(..., description="Mean total MSMEs across all districts in this cluster")
    cluster_mean_micro_share: float = Field(..., description="Mean micro enterprise share percentage in this cluster")
    cluster_mean_sme_share: float = Field(..., description="Mean small & medium enterprise share percentage in this cluster")


class MarketResearchMLAnalysis(BaseModel):
    """Outputs from the scikit-learn KMeans market clustering pipeline."""
    model_config = ConfigDict(from_attributes=True)

    is_available: bool = Field(True, description="True if ML clustering completed successfully")
    cluster_id: int = Field(..., description="Assigned cluster index (0 to K-1)")
    cluster_label: str = Field(..., description="Empirically validated descriptive label for the cluster")
    cluster_description: str = Field(..., description="Analytical characterization of the cluster archetype")
    features_used: List[str] = Field(..., description="List of numerical features utilized in KMeans training")
    quantitative_indicators: ClusterQuantitativeIndicators = Field(..., description="District indicators and baselines")
    cluster_distribution_summary: Dict[str, int] = Field(
        default_factory=dict, description="Distribution of all 785 Indian districts across clusters"
    )
    methodology_notes: List[str] = Field(
        default_factory=list, description="Methodological notes explaining preprocessing and model setup"
    )


class QualitativeLLMAnalysis(BaseModel):
    """Outputs from the server-side Anthropic Claude / deterministic qualitative analysis pipeline."""
    model_config = ConfigDict(from_attributes=True)

    is_available: bool = Field(True, description="True if qualitative analysis is available")
    source: str = Field(
        ..., description="Source of analysis: 'anthropic-claude-3-5-sonnet' or 'deterministic-empirical-fallback'"
    )
    market_interpretation: str = Field(..., description="Comprehensive qualitative summary of the local district market")
    opportunities: List[str] = Field(default_factory=list, description="Data-grounded commercial opportunities")
    operational_considerations: List[str] = Field(
        default_factory=list, description="Operational, infrastructural, and climate considerations"
    )
    competitive_considerations: List[str] = Field(
        default_factory=list, description="Competitive environment and supplier dynamics"
    )
    risks: List[str] = Field(default_factory=list, description="Prudent operational and financial risks")
    practical_recommendations: List[str] = Field(
        default_factory=list, description="Actionable, pragmatic recommendations for enterprise setup"
    )
    qualitative_notes: List[str] = Field(
        default_factory=list, description="Advisory notes on the qualitative reasoning process"
    )


class WeatherRiskSignals(BaseModel):
    """Discrete operational risk levels derived from transparent weather heuristics."""
    model_config = ConfigDict(from_attributes=True)

    heat_stress: str = Field(..., description="Heat stress level: 'Low', 'Moderate', 'High', or 'Severe'")
    rain_disruption: str = Field(..., description="Precipitation disruption: 'None', 'Low', 'Moderate', 'High', or 'Severe'")
    outdoor_activity: str = Field(..., description="Outdoor activity favourability: 'Favourable', 'Normal', 'Moderate Disruption', or 'Lower'")
    logistics_disruption: str = Field(..., description="Logistics / transport disruption: 'Low', 'Moderate', or 'High'")


class DailyWeatherOutlookItem(BaseModel):
    """Daily forecast weather activity impact projection."""
    model_config = ConfigDict(from_attributes=True)

    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    day_name: str = Field(..., description="Label such as 'Today', 'Tomorrow', or day of week")
    temp_range: str = Field(..., description="Formatted temperature range, e.g. '32° / 24°C'")
    precipitation_sum_mm: float = Field(..., description="Expected daily precipitation in mm")
    precipitation_probability_pct: Optional[int] = Field(None, description="Precipitation probability (0-100)")
    weather_description: str = Field(..., description="Human-readable weather description")
    impact_score: float = Field(..., description="Indicative Weather Activity Impact score (0-100)")
    impact_label: str = Field(..., description="Categorical label: 'Very Favourable', 'Favourable', 'Neutral', 'Potentially Disruptive', 'Highly Disruptive'")
    outdoor_activity_signal: str = Field(..., description="Qualitative activity signal")


class WeatherActivityImpactAnalysis(BaseModel):
    """
    Modelled Indicative Weather Activity Impact Analysis.
    
    IMPORTANT ARCHITECTURAL INVARIANT & ZERO-FABRICATION CONTRACT:
    - This is an INDICATIVE PRODUCT HEURISTIC, NOT a scientifically validated footfall model or economic forecast.
    - Weather thresholds are transparent product heuristics chosen to demonstrate how environmental
      conditions may influence general business activity.
    - Zero customer counts, zero revenue projections, zero percentage claims.
    """
    model_config = ConfigDict(from_attributes=True)

    is_available: bool = Field(True, description="True if weather activity impact could be evaluated")
    activity_impact_score: Optional[float] = Field(None, description="Indicative Weather Activity Impact score (0-100, weighted heuristic)")
    activity_impact_label: Optional[str] = Field(None, description="Categorical impact: 'Very Favourable', 'Favourable', 'Neutral', 'Potentially Disruptive', 'Highly Disruptive'")
    potential_footfall_effect: Optional[str] = Field(None, description="Qualitative walk-in and customer activity implication")
    risk_signals: Optional[WeatherRiskSignals] = Field(None, description="Categorical weather risk signals")
    business_type_implication: Optional[str] = Field(None, description="Domain-tailored qualitative operational guidance")
    weather_outlook_3days: List[DailyWeatherOutlookItem] = Field(default_factory=list, description="3-day indicative activity impact outlook")
    methodology_disclaimer: str = Field(
        default="Indicative weather impact on business activity — not observed footfall or a sales forecast.",
        description="Mandatory statutory zero-fabrication disclaimer",
    )
    heuristic_notes: List[str] = Field(default_factory=list, description="Explanations of formula weights and inputs")


class MarketIntelligenceResponse(BaseModel):
    """Unified Market Intelligence response combining PostgreSQL, ML, LLM, and Climate data."""
    model_config = ConfigDict(from_attributes=True)

    district_id: Optional[int] = Field(None, description="PostgreSQL district ID")
    district_name: str = Field(..., description="Canonical district name")
    state_name: str = Field(..., description="Canonical state name")
    lg_dt_code: Optional[str] = Field(None, description="Official LGD district code")
    
    geographic_coordinates: Optional[DistrictCoordinates] = Field(
        None, description="Centroid coordinates and elevation"
    )
    market_context: Optional[DistrictMarketContext] = Field(
        None, description="Official Udyam district MSME records and ranks"
    )
    weather_context: Optional[DistrictWeatherContext] = Field(
        None, description="Observational weather conditions and 3-day forecast"
    )
    ml_analysis: MarketResearchMLAnalysis = Field(
        ..., description="Quantitative scikit-learn KMeans market clustering and indicators"
    )
    llm_analysis: QualitativeLLMAnalysis = Field(
        ..., description="Qualitative market interpretation from server-side Claude or deterministic fallback"
    )
    weather_activity_impact: Optional[WeatherActivityImpactAnalysis] = Field(
        None, description="Indicative Weather Activity Impact heuristic analysis"
    )
    comparable_markets: Optional[ComparableMarketContext] = Field(
        None, description="Empirical market similarity across 785 districts from scikit-learn NearestNeighbors"
    )
    research_observations: List[str] = Field(
        default_factory=list, description="Empirical observations regarding market density and local conditions"
    )
    operational_cautions: List[str] = Field(
        default_factory=list, description="Operational considerations based on climate alerts and SME depth"
    )
    disclaimer: str = Field(
        default=(
            "RESEARCH CONTEXT ONLY: Geographic, weather, ML clustering, and market indicators are provided "
            "solely for business planning, operational risk assessment, and empirical research. "
            "They do NOT constitute statutory proof of scheme eligibility, financial viability, "
            "or guarantee of government program sanctions or business success."
        ),
        description="Statutory advisory disclaimer",
    )
