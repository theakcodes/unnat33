"""
app/models/research_models.py

SQLAlchemy declarative models for the Research Intelligence layer:
- DistrictGeoCentroid: Geographic coordinates and elevation for official LGD districts.
- DistrictWeatherCache: Persistent cache for weather forecast and historical climate snapshots.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class DistrictGeoCentroid(Base):
    """Authoritative geographic centroids (latitude, longitude, elevation) for official LGD districts."""

    __tablename__ = "district_geo_centroids"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(
        Integer,
        ForeignKey("districts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    elevation_meters = Column(Numeric(7, 2), nullable=True)
    source = Column(String(50), default="open-meteo", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)

    district = relationship("District", backref="geo_centroid")

    def __repr__(self) -> str:
        return f"<DistrictGeoCentroid district_id={self.district_id} lat={self.latitude} lon={self.longitude}>"


class DistrictWeatherCache(Base):
    """PostgreSQL persistent cache for district-level weather observations and forecasts."""

    __tablename__ = "district_weather_cache"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(
        Integer,
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cache_type = Column(String(20), default="FORECAST", nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    current_metrics = Column(JSON, nullable=True)
    daily_forecast = Column(JSON, nullable=True)
    source = Column(String(50), default="open-meteo", nullable=False)
    fetched_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_stale = Column(Boolean, default=False, nullable=False)

    district = relationship("District", backref="weather_cache_entries")

    __table_args__ = (
        UniqueConstraint(
            "district_id",
            "observation_date",
            "cache_type",
            name="uq_district_weather_cache",
        ),
    )

    def __repr__(self) -> str:
        return f"<DistrictWeatherCache district_id={self.district_id} date={self.observation_date} type={self.cache_type}>"
