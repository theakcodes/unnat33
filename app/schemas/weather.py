"""
app/schemas/weather.py

Pydantic schemas for district weather metrics and forecast snapshots.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CurrentWeatherMetrics(BaseModel):
    """Real-time / snapshot weather observations for a district."""
    model_config = ConfigDict(from_attributes=True)

    temperature_c: float = Field(..., description="Air temperature at 2m in Celsius")
    relative_humidity_pct: int = Field(..., description="Relative humidity at 2m percentage (0-100)")
    apparent_temperature_c: float = Field(..., description="Apparent ('feels like') temperature in Celsius")
    precipitation_mm: float = Field(..., description="Current precipitation in mm")
    weather_code: int = Field(..., description="WMO weather interpretation code")
    weather_description: str = Field(..., description="Human-readable condition description")
    wind_speed_kmh: float = Field(..., description="Wind speed at 10m in km/h")
    observed_at: Optional[str] = Field(None, description="ISO observation timestamp")


class DailyForecastDay(BaseModel):
    """Daily forecast summary metrics."""
    model_config = ConfigDict(from_attributes=True)

    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    temp_max_c: float = Field(..., description="Maximum temperature in Celsius")
    temp_min_c: float = Field(..., description="Minimum temperature in Celsius")
    precipitation_sum_mm: float = Field(..., description="Total precipitation sum in mm")
    precipitation_probability_pct: Optional[int] = Field(None, description="Maximum precipitation probability (0-100)")
    wind_speed_max_kmh: float = Field(..., description="Maximum wind speed in km/h")
    evapotranspiration_mm: Optional[float] = Field(None, description="Reference FAO-56 evapotranspiration (ET0) in mm")
    weather_code: int = Field(..., description="WMO weather interpretation code")
    weather_description: str = Field(..., description="Human-readable condition description")


class DistrictWeatherContext(BaseModel):
    """District-level weather context payload."""
    model_config = ConfigDict(from_attributes=True)

    is_available: bool = Field(..., description="True if weather snapshot is available")
    is_stale: bool = Field(False, description="True if snapshot was served from stale cache fallback")
    source: str = Field("open-meteo", description="Weather data provider")
    fetched_at: Optional[datetime] = Field(None, description="Timestamp when weather was cached/retrieved")
    current: Optional[CurrentWeatherMetrics] = Field(None, description="Current observations")
    forecast_3days: List[DailyForecastDay] = Field(default_factory=list, description="3-day daily forecast")
    weather_notes: List[str] = Field(
        default_factory=lambda: [
            "Weather data is observational research context and does not determine statutory scheme eligibility."
        ],
        description="Advisory notes",
    )
