"""
app/schemas/research_context.py

Unified research intelligence response schema combining MSME market context,
geography (coordinates + elevation), and weather signals.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.geography import DistrictCoordinates
from app.schemas.district_msme import DistrictMarketContext
from app.schemas.weather import DistrictWeatherContext


class DistrictResearchContextResponse(BaseModel):
    """
    Unified Research Context response for a target district.
    Aggregates:
    - Official geographic centroid coordinates and elevation
    - Empirical Udyam MSME market-sizing and composition metrics
    - Real-time and 3-day observational weather forecast
    - Factual, defensible research observations and operational cautions

    IMPORTANT ARCHITECTURAL RULE:
    All content in this schema represents contextual research intelligence.
    It does NOT determine statutory eligibility or alter scheme recommendation scores.
    """
    model_config = ConfigDict(from_attributes=True)

    district_id: Optional[int] = Field(None, description="Internal PostgreSQL district ID")
    district_name: str = Field(..., description="Official district name")
    state_name: str = Field(..., description="Canonical state name")
    lg_dt_code: Optional[str] = Field(None, description="Official LGD district code")
    
    geographic_coordinates: Optional[DistrictCoordinates] = Field(
        None, description="Spatial coordinates and elevation"
    )
    msme_market_context: Optional[DistrictMarketContext] = Field(
        None, description="Udyam enterprise density, rankings, and composition"
    )
    weather_context: Optional[DistrictWeatherContext] = Field(
        None, description="Observational weather conditions and short-term forecast"
    )

    research_observations: List[str] = Field(
        default_factory=list,
        description="Factual, empirical data-backed observations regarding market density and local conditions",
    )
    operational_cautions: List[str] = Field(
        default_factory=list,
        description="Prudent operational considerations based strictly on observed climate and market factors",
    )

    disclaimer: str = Field(
        default=(
            "RESEARCH CONTEXT ONLY: Geographic, weather, and MSME density indicators are provided "
            "solely for business planning, operational risk assessment, and market research. "
            "They do NOT constitute statutory proof of scheme eligibility, financial viability, "
            "or guarantee of government program sanctions."
        ),
        description="Statutory advisory disclaimer",
    )
