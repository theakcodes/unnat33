"""
app/services/weather_service.py

Service for orchestrating district-level weather intelligence:
- Checks PostgreSQL persistent cache (24h TTL)
- Fetches from Open-Meteo on cache miss
- Persists snapshots to PostgreSQL
- Fallback to stale cache on network downtime
- Graceful unavailable state without throwing uncaught exceptions
"""

import json
import logging
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.schemas.weather import (
    CurrentWeatherMetrics,
    DailyForecastDay,
    DistrictWeatherContext,
)
from app.repositories.weather_cache_repository import WeatherCacheRepository
from app.clients.open_meteo_client import OpenMeteoClient, get_weather_description

logger = logging.getLogger(__name__)


class WeatherService:
    """Service providing resilient, cached district weather intelligence."""

    def __init__(self, client: Optional[OpenMeteoClient] = None):
        self.client = client or OpenMeteoClient()

    async def get_district_weather(
        self,
        db: Session,
        district_id: int,
        latitude: float,
        longitude: float,
        max_age_hours: int = 24,
    ) -> DistrictWeatherContext:
        """
        Retrieve weather context for a district by coordinates:
        1. Query PostgreSQL cache for today's forecast snapshot.
        2. If fresh (<24h), return cached context immediately (0 network calls).
        3. If missing or expired, fetch from Open-Meteo and persist snapshot.
        4. If Open-Meteo fails, fall back to most recent stale cached entry with is_stale=True.
        5. If no cache exists and API fails, return structured unavailable context.
        """
        today = date.today()

        # 1. Check PostgreSQL cache
        cached_entry, is_fresh = WeatherCacheRepository.get_cache(
            db,
            district_id=district_id,
            observation_date=today,
            cache_type="FORECAST",
            max_age_hours=max_age_hours,
        )

        if cached_entry and is_fresh:
            return self._build_weather_context(
                cached_entry=cached_entry,
                is_available=True,
                is_stale=False,
            )

        # 2. Cache miss or expired -> Fetch from Open-Meteo
        forecast_data = await self.client.get_forecast(latitude, longitude, forecast_days=3)

        if forecast_data:
            current_dict = forecast_data.get("current", {})
            daily_dict = forecast_data.get("daily", {})

            # Persist to database cache
            saved_entry = WeatherCacheRepository.save_cache(
                db=db,
                district_id=district_id,
                observation_date=today,
                cache_type="FORECAST",
                current_metrics=current_dict,
                daily_forecast=daily_dict,
                source="open-meteo",
                is_stale=False,
            )

            return self._build_weather_context(
                cached_entry=saved_entry,
                is_available=True,
                is_stale=False,
            )

        # 3. API Failure -> Fallback to stale cache
        logger.warning(
            "Open-Meteo fetch failed for district_id=%s. Attempting stale cache fallback.",
            district_id,
        )
        stale_entry = WeatherCacheRepository.get_latest_cache(
            db, district_id=district_id, cache_type="FORECAST"
        )

        if stale_entry:
            return self._build_weather_context(
                cached_entry=stale_entry,
                is_available=True,
                is_stale=True,
            )

        # 4. API Failure + No Cache -> Return structured unavailable state
        return DistrictWeatherContext(
            is_available=False,
            is_stale=False,
            source="open-meteo",
            fetched_at=None,
            current=None,
            forecast_3days=[],
            weather_notes=[
                "Live weather data is temporarily unavailable from Open-Meteo and no cached snapshot was found.",
                "External weather data is research context only and does not impact scheme eligibility or recommendations.",
            ],
        )

    def _build_weather_context(
        self,
        cached_entry: Any,
        is_available: bool,
        is_stale: bool,
    ) -> DistrictWeatherContext:
        """Construct DistrictWeatherContext schema from database cache record."""
        current_raw = cached_entry.current_metrics
        if isinstance(current_raw, str):
            try:
                current_raw = json.loads(current_raw)
            except Exception:
                current_raw = {}
        current_raw = current_raw or {}

        daily_raw = cached_entry.daily_forecast
        if isinstance(daily_raw, str):
            try:
                daily_raw = json.loads(daily_raw)
            except Exception:
                daily_raw = {}
        daily_raw = daily_raw or {}

        current_metrics = None
        if current_raw:
            code = current_raw.get("weather_code")
            current_metrics = CurrentWeatherMetrics(
                temperature_c=float(current_raw.get("temperature_2m", 0.0)),
                relative_humidity_pct=int(current_raw.get("relative_humidity_2m", 0)),
                apparent_temperature_c=float(current_raw.get("apparent_temperature", 0.0)),
                precipitation_mm=float(current_raw.get("precipitation", 0.0)),
                weather_code=int(code) if code is not None else 0,
                weather_description=get_weather_description(code),
                wind_speed_kmh=float(current_raw.get("wind_speed_10m", 0.0)),
                observed_at=str(current_raw.get("time", "")),
            )

        forecast_list: List[DailyForecastDay] = []
        dates = daily_raw.get("time", [])
        if isinstance(dates, list):
            max_temps = daily_raw.get("temperature_2m_max", [])
            min_temps = daily_raw.get("temperature_2m_min", [])
            precip_sums = daily_raw.get("precipitation_sum", [])
            precip_probs = daily_raw.get("precipitation_probability_max", [])
            wind_maxs = daily_raw.get("wind_speed_10m_max", [])
            et0s = daily_raw.get("et0_fao_evapotranspiration", [])
            codes = daily_raw.get("weather_code", [])

            for i, dt in enumerate(dates):
                c = codes[i] if i < len(codes) else None
                forecast_list.append(
                    DailyForecastDay(
                        date=str(dt),
                        temp_max_c=float(max_temps[i]) if i < len(max_temps) and max_temps[i] is not None else 0.0,
                        temp_min_c=float(min_temps[i]) if i < len(min_temps) and min_temps[i] is not None else 0.0,
                        precipitation_sum_mm=float(precip_sums[i]) if i < len(precip_sums) and precip_sums[i] is not None else 0.0,
                        precipitation_probability_pct=int(precip_probs[i]) if i < len(precip_probs) and precip_probs[i] is not None else None,
                        wind_speed_max_kmh=float(wind_maxs[i]) if i < len(wind_maxs) and wind_maxs[i] is not None else 0.0,
                        evapotranspiration_mm=float(et0s[i]) if i < len(et0s) and et0s[i] is not None else None,
                        weather_code=int(c) if c is not None else 0,
                        weather_description=get_weather_description(c),
                    )
                )

        notes = [
            "Weather data is observational research context and does not determine statutory scheme eligibility."
        ]
        if is_stale:
            notes.append(
                "NOTE: Live API call was unreachable; serving previously cached forecast snapshot."
            )

        return DistrictWeatherContext(
            is_available=is_available,
            is_stale=is_stale,
            source=cached_entry.source or "open-meteo",
            fetched_at=cached_entry.fetched_at,
            current=current_metrics,
            forecast_3days=forecast_list,
            weather_notes=notes,
        )


weather_service = WeatherService()
