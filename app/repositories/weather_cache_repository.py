"""
app/repositories/weather_cache_repository.py

Repository for PostgreSQL persistent cache of district-level weather observations and forecasts.
"""

from typing import Optional, Tuple, Dict, Any
from datetime import date, datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.research_models import DistrictWeatherCache


class WeatherCacheRepository:
    """Repository for querying and updating persistent weather forecast cache."""

    @classmethod
    def get_cache(
        cls,
        db: Session,
        district_id: int,
        observation_date: date,
        cache_type: str = "FORECAST",
        max_age_hours: int = 24,
    ) -> Tuple[Optional[DistrictWeatherCache], bool]:
        """
        Fetch cache entry by district_id, observation_date, and cache_type.
        Returns: (cache_record, is_fresh)
        """
        record = (
            db.query(DistrictWeatherCache)
            .filter(
                DistrictWeatherCache.district_id == district_id,
                DistrictWeatherCache.observation_date == observation_date,
                DistrictWeatherCache.cache_type == cache_type,
            )
            .first()
        )
        if not record:
            return None, False

        # Freshness calculation based on fetched_at
        is_fresh = False
        if record.fetched_at:
            age = datetime.utcnow() - record.fetched_at
            is_fresh = age < timedelta(hours=max_age_hours)

        return record, is_fresh

    @classmethod
    def get_latest_cache(
        cls,
        db: Session,
        district_id: int,
        cache_type: str = "FORECAST",
    ) -> Optional[DistrictWeatherCache]:
        """Fetch the most recent cache entry for district_id, regardless of freshness (used for fallback)."""
        return (
            db.query(DistrictWeatherCache)
            .filter(
                DistrictWeatherCache.district_id == district_id,
                DistrictWeatherCache.cache_type == cache_type,
            )
            .order_by(DistrictWeatherCache.fetched_at.desc())
            .first()
        )

    @classmethod
    def save_cache(
        cls,
        db: Session,
        district_id: int,
        observation_date: date,
        cache_type: str,
        current_metrics: Optional[Dict[str, Any]],
        daily_forecast: Optional[Dict[str, Any]],
        source: str = "open-meteo",
        is_stale: bool = False,
    ) -> DistrictWeatherCache:
        """
        Upsert weather cache record using ORM.
        """
        record = (
            db.query(DistrictWeatherCache)
            .filter(
                DistrictWeatherCache.district_id == district_id,
                DistrictWeatherCache.observation_date == observation_date,
                DistrictWeatherCache.cache_type == cache_type,
            )
            .first()
        )
        now_dt = datetime.utcnow()
        if not record:
            record = DistrictWeatherCache(
                district_id=district_id,
                cache_type=cache_type,
                observation_date=observation_date,
                current_metrics=current_metrics,
                daily_forecast=daily_forecast,
                source=source,
                fetched_at=now_dt,
                is_stale=is_stale,
            )
            db.add(record)
        else:
            record.current_metrics = current_metrics
            record.daily_forecast = daily_forecast
            record.source = source
            record.fetched_at = now_dt
            record.is_stale = is_stale

        db.commit()
        db.refresh(record)
        return record
