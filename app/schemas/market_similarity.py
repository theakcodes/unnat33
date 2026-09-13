"""
app/schemas/market_similarity.py

Pydantic schemas for the scikit-learn NearestNeighbors Market Similarity Engine:
- Comparable districts ranked by Euclidean distance in standardized 6-feature space
- Real MSME metrics from the 785-district PostgreSQL census
- Qualitative structural observations (zero percentage similarity claims)
- Strict provenance labeling (MODELLED INDICATOR)
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ComparableDistrictItem(BaseModel):
    """A comparable Indian district identified via scikit-learn NearestNeighbors."""
    model_config = ConfigDict(from_attributes=True)

    district_id: Optional[int] = Field(None, description="PostgreSQL district ID")
    district_name: str = Field(..., description="Canonical district name")
    state_name: str = Field(..., description="Canonical state / UT name")
    similarity_rank: int = Field(..., description="Proximity rank (1 = closest non-identical district)")
    similarity_distance: float = Field(
        ..., description="Euclidean distance in standardized 6-feature space (lower = closer structural profile)"
    )
    total_msmes: int = Field(..., description="Total registered MSMEs in district")
    micro_share: float = Field(..., description="Percentage of micro enterprises (0-100)")
    small_medium_share: float = Field(..., description="Percentage of small & medium enterprises (0-100)")
    cluster_label: Optional[str] = Field(None, description="KMeans cluster archetype label if available")
    qualitative_observation: str = Field(
        ..., description="Analytical structural comparison note (e.g. comparable density, SME depth)"
    )
    provenance: str = Field(
        default="MODELLED INDICATOR",
        description="Data provenance tag: MODELLED INDICATOR",
    )


class ComparableMarketContext(BaseModel):
    """NearestNeighbors Market Similarity Analysis across 785 Indian districts."""
    model_config = ConfigDict(from_attributes=True)

    is_available: bool = Field(True, description="True if NearestNeighbors calculation completed successfully")
    target_district: str = Field(..., description="Name of the evaluated target district")
    target_state: str = Field(..., description="State of the evaluated target district")
    comparable_districts: List[ComparableDistrictItem] = Field(
        default_factory=list, description="Top 3-5 comparable districts sorted by increasing Euclidean distance"
    )
    features_used: List[str] = Field(
        default_factory=lambda: [
            "total_msmes",
            "micro_enterprises",
            "small_enterprises",
            "medium_enterprises",
            "micro_share",
            "small_medium_share",
        ],
        description="List of standardized numerical features utilized in NearestNeighbors query",
    )
    methodology_notes: List[str] = Field(
        default_factory=list, description="Methodological notes explaining the NearestNeighbors model"
    )
    disclaimer: str = Field(
        default=(
            "Empirical market similarity computed using scikit-learn NearestNeighbors on standardized Udyam MSME features "
            "across 785 Indian districts. Similarity distances represent mathematical proximity in multi-dimensional feature space "
            "and do NOT imply commercial equivalence, percentage parity, or revenue guarantees."
        ),
        description="Zero-fabrication similarity disclaimer",
    )
