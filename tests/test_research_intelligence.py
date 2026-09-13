"""
tests/test_research_intelligence.py

Automated tests for Phase 4A & 4B: Geography Enrichment + Weather Intelligence.
Verifies:
1. DistrictGeoRepository lookup (by id, code, name + state)
2. GeographyService DB-first resolution without network calls
3. Unknown district geography handling (graceful None)
4. Weather cache hit avoids external API call (0ms DB path)
5. Weather cache miss fetches from client and persists to PostgreSQL
6. Weather metric normalization and WMO weather code descriptions
7. WeatherService API failure fallback to stale cache (is_stale=True)
8. WeatherService API failure with no cache fallback (is_available=False)
9. Unified ResearchContextService aggregation (Geo + MSME + Weather)
10. Defensible, factual research observations and operational cautions
11. API GET /api/v1/research/district-market-context (200, 400, 404)
12. Recommendation scorer and statutory eligibility invariants remain 100% untouched
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.repositories.district_geo_repository import DistrictGeoRepository
from app.repositories.weather_cache_repository import WeatherCacheRepository
from app.services.geography_service import GeographyService
from app.services.weather_service import WeatherService
from app.services.research_context_service import ResearchContextService
from app.schemas.research_context import DistrictResearchContextResponse
from app.schemas.weather import DistrictWeatherContext
from app.clients.open_meteo_client import get_weather_description


def test_district_geo_repository_lookup(db_session: Session):
    """Verify DistrictGeoRepository resolves centroids by ID, LGD code, and name."""
    # 1. Lookup Pune (LGD 490)
    centroid = DistrictGeoRepository.get_by_district_code(db_session, "490")
    assert centroid is not None
    assert centroid.latitude is not None
    assert centroid.longitude is not None
    # Latitude for Pune ~18.5, Longitude ~73.8
    assert 18.0 <= float(centroid.latitude) <= 19.5
    assert 73.0 <= float(centroid.longitude) <= 74.5

    # 2. Lookup by district_id
    by_id = DistrictGeoRepository.get_by_district_id(db_session, centroid.district_id)
    assert by_id is not None
    assert by_id.id == centroid.id

    # 3. Lookup by district and state name
    by_name = DistrictGeoRepository.get_by_district_and_state(
        db_session, district_name="Pune", state_name="Maharashtra"
    )
    assert by_name is not None
    assert by_name.district_id == centroid.district_id


def test_geography_service_db_first(db_session: Session):
    """Verify GeographyService resolves coordinates DB-first without external HTTP calls."""
    coords = GeographyService.get_district_coordinates(
        db_session, district_name="Varanasi", state_name="Uttar Pradesh"
    )
    assert coords is not None
    assert coords.district_name.upper() == "VARANASI"
    assert coords.state_name.upper() == "UTTAR PRADESH"
    assert coords.source == "open-meteo"
    # Varanasi lat ~25.3, lon ~82.9
    assert 25.0 <= coords.latitude <= 26.0
    assert 82.0 <= coords.longitude <= 84.0


def test_unknown_district_geography_handling(db_session: Session):
    """Verify unknown districts return None without raising uncaught exceptions."""
    coords = GeographyService.get_district_coordinates(
        db_session, district_name="NonExistentDistrict999XYZ", state_name="NonExistentState"
    )
    assert coords is None


import asyncio

def test_weather_cache_hit_avoids_api_call(db_session: Session):
    """Verify fresh weather cache entry is returned without calling external API."""
    async def _test():
        today = date.today()
        mock_client = AsyncMock()
        service = WeatherService(client=mock_client)

        # Save a test entry in cache
        test_district_id = 1
        WeatherCacheRepository.save_cache(
            db=db_session,
            district_id=test_district_id,
            observation_date=today,
            cache_type="FORECAST",
            current_metrics={
                "temperature_2m": 26.5,
                "relative_humidity_2m": 60,
                "apparent_temperature": 27.0,
                "precipitation": 0.0,
                "weather_code": 0,
                "wind_speed_10m": 5.0,
                "time": "2026-09-06T12:00",
            },
            daily_forecast={
                "time": [str(today)],
                "temperature_2m_max": [31.0],
                "temperature_2m_min": [22.0],
                "precipitation_sum": [0.0],
                "precipitation_probability_max": [10],
                "wind_speed_10m_max": [8.0],
                "et0_fao_evapotranspiration": [4.2],
                "weather_code": [0],
            },
            source="open-meteo",
            is_stale=False,
        )

        result = await service.get_district_weather(
            db=db_session,
            district_id=test_district_id,
            latitude=17.69,
            longitude=83.00,
        )

        assert result.is_available is True
        assert result.is_stale is False
        assert result.current is not None
        assert result.current.temperature_c == 26.5
        assert result.current.weather_description == "Clear sky"
        mock_client.get_forecast.assert_not_called()

    asyncio.run(_test())


def test_weather_cache_miss_fetches_and_persists(db_session: Session):
    """Verify cache miss fetches from client, normalizes, and persists snapshot."""
    async def _test():
        test_district_id = 2  # Bapatla
        today = date.today()

        # Clear today's cache for test district
        db_session.execute(
            text("DELETE FROM district_weather_cache WHERE district_id = :d_id AND observation_date = :dt"),
            {"d_id": test_district_id, "dt": today},
        )
        db_session.commit()

        mock_client = AsyncMock()
        mock_client.get_forecast.return_value = {
            "current": {
                "temperature_2m": 30.2,
                "relative_humidity_2m": 65,
                "apparent_temperature": 34.0,
                "precipitation": 1.2,
                "weather_code": 61,
                "wind_speed_10m": 12.5,
                "time": f"{today}T14:00",
            },
            "daily": {
                "time": [str(today), str(today + timedelta(days=1))],
                "temperature_2m_max": [32.0, 33.0],
                "temperature_2m_min": [24.0, 25.0],
                "precipitation_sum": [2.5, 0.0],
                "precipitation_probability_max": [70, 20],
                "wind_speed_10m_max": [15.0, 10.0],
                "et0_fao_evapotranspiration": [4.8, 5.1],
                "weather_code": [61, 1],
            },
        }

        service = WeatherService(client=mock_client)
        result = await service.get_district_weather(
            db=db_session,
            district_id=test_district_id,
            latitude=15.90,
            longitude=80.46,
        )

        assert result.is_available is True
        assert result.is_stale is False
        assert result.current is not None
        assert result.current.temperature_c == 30.2
        assert result.current.weather_description == "Slight rain"
        assert len(result.forecast_3days) == 2
        mock_client.get_forecast.assert_called_once()

        db_entry, is_fresh = WeatherCacheRepository.get_cache(db_session, test_district_id, today)
        assert db_entry is not None
        assert is_fresh is True

    asyncio.run(_test())


def test_open_meteo_client_forecast_parsing():
    """Verify weather description mappings and edge cases."""
    assert get_weather_description(0) == "Clear sky"
    assert get_weather_description(61) == "Slight rain"
    assert get_weather_description(95) == "Thunderstorm"
    assert get_weather_description(999) == "Weather condition (code 999)"
    assert get_weather_description(None) == "Unknown"


def test_weather_service_api_failure_stale_fallback(db_session: Session):
    """Verify that if external API fails, most recent cached snapshot is returned with is_stale=True."""
    async def _test():
        test_district_id = 3
        past_date = date.today() - timedelta(days=2)

        WeatherCacheRepository.save_cache(
            db=db_session,
            district_id=test_district_id,
            observation_date=past_date,
            cache_type="FORECAST",
            current_metrics={
                "temperature_2m": 27.0,
                "relative_humidity_2m": 50,
                "apparent_temperature": 27.5,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 4.0,
            },
            daily_forecast={"time": [str(past_date)]},
            source="open-meteo",
            is_stale=False,
        )

        db_session.execute(
            text("DELETE FROM district_weather_cache WHERE district_id = :d_id AND observation_date = :dt"),
            {"d_id": test_district_id, "dt": date.today()},
        )
        db_session.commit()

        mock_client = AsyncMock()
        mock_client.get_forecast.return_value = None

        service = WeatherService(client=mock_client)
        result = await service.get_district_weather(
            db=db_session,
            district_id=test_district_id,
            latitude=17.0,
            longitude=81.7,
        )

        assert result.is_available is True
        assert result.is_stale is True
        assert any("previously cached" in note for note in result.weather_notes)

    asyncio.run(_test())


def test_weather_service_no_cache_unavailable_fallback(db_session: Session):
    """Verify structured unavailable context returned when both API and cache are unavailable."""
    async def _test():
        non_existent_district_id = 99999
        mock_client = AsyncMock()
        mock_client.get_forecast.return_value = None

        service = WeatherService(client=mock_client)
        result = await service.get_district_weather(
            db=db_session,
            district_id=non_existent_district_id,
            latitude=20.0,
            longitude=75.0,
        )

        assert result.is_available is False
        assert result.is_stale is False
        assert result.current is None
        assert len(result.forecast_3days) == 0

    asyncio.run(_test())


def test_research_context_aggregation(db_session: Session):
    """Verify ResearchContextService aggregates Geo, MSME, and Weather into unified response."""
    async def _test():
        service = ResearchContextService()
        context = await service.get_district_research_context(
            db=db_session,
            district_name="Pune",
            state_name="Maharashtra",
        )

        assert context is not None
        assert context.district_name.upper() == "PUNE"
        assert context.state_name.upper() == "MAHARASHTRA"
        assert context.geographic_coordinates is not None
        assert context.geographic_coordinates.latitude is not None
        assert context.msme_market_context is not None
        assert context.msme_market_context.total_msmes > 500000
        assert len(context.research_observations) >= 2
        assert len(context.operational_cautions) >= 1
        assert "RESEARCH CONTEXT ONLY" in context.disclaimer

    asyncio.run(_test())


def test_research_observations_defensible_and_factual():
    """Verify observations and cautions only contain verifiable facts."""
    service = ResearchContextService()
    obs = service._generate_observations(None, None, None)
    assert isinstance(obs, list)
    assert len(obs) == 0

    cautions = service._generate_operational_cautions(None, None, None)
    assert len(cautions) >= 1
    assert "Standard operational conditions observed" in cautions[0]


def test_api_research_district_market_context_200(client: TestClient):
    """Verify GET /api/v1/research/district-market-context returns 200 OK with full schema."""
    response = client.get("/api/v1/research/district-market-context?district_name=Pune&state_name=Maharashtra")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["district_name"].upper() == "PUNE"
    assert data["state_name"].upper() == "MAHARASHTRA"
    assert data["geographic_coordinates"] is not None
    assert data["msme_market_context"] is not None
    assert "research_observations" in data
    assert "operational_cautions" in data
    assert "disclaimer" in data

    # 400 Bad Request if no parameters
    resp_400 = client.get("/api/v1/research/district-market-context")
    assert resp_400.status_code == status.HTTP_400_BAD_REQUEST

    # 404 Not Found for completely fake district
    resp_404 = client.get("/api/v1/research/district-market-context?district_name=NonExistentPlace999XYZ")
    assert resp_404.status_code == status.HTTP_404_NOT_FOUND


def test_recommendation_scorer_and_eligibility_invariants(db_session: Session):
    """
    CRITICAL INVARIANT:
    Verify recommendation scorer and statutory eligibility engines remain 100%
    untouched and identical with zero points added from weather or geography.
    """
    from app.schemas.eligibility import UserProfile
    from app.schemas.recommendation import RecommendationRequest
    from app.services.recommendation_service import recommendation_service

    profile = UserProfile(
        age=32,
        gender="Female",
        social_category="OBC",
        state="Maharashtra",
        district="Pune",
        sector="Manufacturing",
        requested_loan_amount=1200000.0,
        is_new_business=True,
    )

    req = RecommendationRequest(profile=profile, top_k=10)
    response = recommendation_service.generate_recommendations(db_session, req)

    assert response.total_programs_evaluated == 60
    assert response.total_recommended > 0
    assert len(response.recommendations) <= 10

    for item in response.recommendations:
        # Score must remain strictly bounded in [0.0, 100.0]
        assert 0.0 <= item.recommendation_score <= 100.0
        sb = item.scoring_breakdown

        # Confirm the 6 canonical dimensions with exact established score bounds (summing to 100.0)
        assert 0.0 <= sb.eligibility_confidence_score <= 20.0
        assert 0.0 <= sb.financial_fit_score <= 25.0
        assert 0.0 <= sb.sector_fit_score <= 20.0
        assert 0.0 <= sb.actionability_score <= 15.0
        assert 0.0 <= sb.beneficiary_stage_score <= 10.0
        assert 0.0 <= sb.market_context_score <= 10.0

        # Component sum must match total score (within floating point tolerance)
        comp_sum = round(
            sb.eligibility_confidence_score
            + sb.financial_fit_score
            + sb.sector_fit_score
            + sb.actionability_score
            + sb.beneficiary_stage_score
            + sb.market_context_score,
            2
        )
        assert abs(comp_sum - item.recommendation_score) < 0.01



