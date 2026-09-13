"""
app/clients/open_meteo_client.py

Client for Open-Meteo Weather Forecast and Geocoding APIs.
Adheres strictly to research context rules:
- Non-blocking, isolated network calls.
- Graceful degradation returning None on failure.
"""

import logging
from typing import Optional, Dict, Any, List
from app.clients.base_client import BaseAsyncHttpClient

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes (WW)
WMO_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    62: "Moderate rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_description(code: Optional[int]) -> str:
    """Map WMO numeric weather code to descriptive text."""
    if code is None:
        return "Unknown"
    return WMO_CODE_DESCRIPTIONS.get(code, f"Weather condition (code {code})")


class OpenMeteoClient(BaseAsyncHttpClient):
    """Client for Open-Meteo Weather Forecast API."""

    def __init__(
        self,
        base_url: str = "https://api.open-meteo.com/v1",
        timeout_seconds: float = 3.0,
        max_retries: int = 1,
    ):
        super().__init__(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 3,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather metrics and multi-day forecast for given latitude and longitude.
        Returns parsed raw dictionary from Open-Meteo or None on failure.
        """
        params = {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,et0_fao_evapotranspiration,weather_code",
            "timezone": "Asia/Kolkata",
            "forecast_days": min(max(forecast_days, 1), 7),
        }
        return await self.get_json("forecast", params=params)


class OpenMeteoGeocodingClient(BaseAsyncHttpClient):
    """Client for Open-Meteo Geocoding API."""

    def __init__(
        self,
        base_url: str = "https://geocoding-api.open-meteo.com/v1",
        timeout_seconds: float = 3.0,
        max_retries: int = 1,
    ):
        super().__init__(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    async def geocode(
        self,
        name: str,
        country_code: str = "IN",
        count: int = 5,
    ) -> Optional[List[Dict[str, Any]]]:
        """Geocode place name using Open-Meteo Geocoding API."""
        params = {
            "name": name,
            "countryCode": country_code,
            "count": count,
            "language": "en",
            "format": "json",
        }
        res = await self.get_json("search", params=params)
        if res and "results" in res:
            return res["results"]
        return None
