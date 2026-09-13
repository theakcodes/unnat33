"""
app/schemas/geography.py

Pydantic schemas for district geographic centroids and coordinates.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DistrictCoordinates(BaseModel):
    """Geographic centroid coordinates and elevation for an official LGD district."""
    model_config = ConfigDict(from_attributes=True)

    district_id: int = Field(..., description="Internal district ID in PostgreSQL")
    district_name: str = Field(..., description="Official district name")
    state_name: str = Field(..., description="Canonical state name")
    lg_dt_code: Optional[str] = Field(None, description="Official LGD district code")
    latitude: float = Field(..., description="Centroid latitude in WGS84 decimal degrees")
    longitude: float = Field(..., description="Centroid longitude in WGS84 decimal degrees")
    elevation_meters: Optional[float] = Field(None, description="Elevation above sea level in meters")
    source: str = Field("open-meteo", description="Authoritative geocoding/elevation source")
