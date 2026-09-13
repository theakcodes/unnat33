from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class DistrictMarketContext(BaseModel):
    """Market-context indicator model derived from official Udyam district MSME records.
    
    IMPORTANT: These metrics are empirical market-context indicators only.
    They do NOT constitute proof of individual business success or viability.
    """
    model_config = ConfigDict(from_attributes=True)

    geographic_level: str = Field("DISTRICT", description="'DISTRICT', 'STATE', or 'NATIONAL'")
    state_name: str = Field(..., description="Canonical State / UT name")
    state_code: Optional[str] = Field(None, description="2-letter standard State code")
    district_name: Optional[str] = Field(None, description="District name if district-level match")
    lg_dt_code: Optional[str] = Field(None, description="Local Government Directory (LGD) district code")
    
    # Absolute counts
    total_msmes: int = Field(..., description="Total registered MSMEs in this jurisdiction")
    micro_enterprises: int = Field(..., description="Registered Micro enterprises")
    small_enterprises: int = Field(..., description="Registered Small enterprises")
    medium_enterprises: int = Field(..., description="Registered Medium enterprises")
    
    # Enterprise composition shares (percentage, 0.0 to 100.0)
    micro_share: float = Field(..., description="Percentage share of Micro enterprises")
    small_share: float = Field(..., description="Percentage share of Small enterprises")
    medium_share: float = Field(..., description="Percentage share of Medium enterprises")
    small_medium_share: float = Field(..., description="Combined percentage share of Small and Medium enterprises")
    
    # Ranks
    national_rank: Optional[int] = Field(None, description="District rank nationally by total MSMEs (1 to 785)")
    total_districts_nationally: int = Field(785, description="Total districts in national reference baseline")
    state_rank: Optional[int] = Field(None, description="District rank within its State by total MSMEs")
    total_districts_in_state: Optional[int] = Field(None, description="Total districts within this State")
    
    # Transparency flags
    is_fallback: bool = Field(False, description="True if district was unrecognized and fell back to state-level aggregate")
    market_context_notes: List[str] = Field(
        default_factory=lambda: [
            "Empirical market-context indicator derived from Udyam registration records.",
            "Indicates local enterprise density and scale composition; does not guarantee individual loan or scheme approval."
        ],
        description="Statutory disclaimer and context notes"
    )
