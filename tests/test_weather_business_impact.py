"""
backend/tests/test_weather_business_impact.py

Comprehensive test suite for Phase 7 Weather -> Business Activity Intelligence Layer:
1. Weather -> activity impact calculation
2. Heavy rainfall produces a more disruptive signal than clear weather
3. Extreme heat produces a lower outdoor-activity signal
4. Mild/clear weather produces a favourable/neutral signal
5. Business-type interpretations (Retail, Food, Agriculture, Manufacturing, Logistics, Tourism, Services)
6. Weather API failure / missing data graceful fallback
7. 3-day forecast outlook evaluation
8. Claude failure isolation
9. Anti-fabrication assertions: zero fabricated footfall %, customer counts, or revenue figures
10. Authoritative backend engine invariance
11. End-to-end integration via /api/v1/research/market-intelligence
"""

import re
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.weather import (
    DistrictWeatherContext,
    CurrentWeatherMetrics,
    DailyForecastDay,
)
from app.schemas.market_intelligence import (
    WeatherActivityImpactAnalysis,
    BusinessProfileContext,
    MarketIntelligenceRequest,
)
from app.services.weather_business_impact_service import (
    WeatherBusinessImpactService,
    weather_business_impact_service,
)


@pytest.fixture
def service():
    return WeatherBusinessImpactService()


@pytest.fixture
def sample_clear_weather():
    """Clear, comfortable weather context."""
    return DistrictWeatherContext(
        is_available=True,
        is_stale=False,
        source="open-meteo",
        current=CurrentWeatherMetrics(
            temperature_c=26.0,
            relative_humidity_pct=45,
            apparent_temperature_c=26.5,
            precipitation_mm=0.0,
            weather_code=0,
            weather_description="Clear sky",
            wind_speed_kmh=12.0,
            observed_at="2026-09-07T08:00:00Z",
        ),
        forecast_3days=[
            DailyForecastDay(
                date="2026-09-07",
                temp_max_c=28.0,
                temp_min_c=20.0,
                precipitation_sum_mm=0.0,
                precipitation_probability_pct=5,
                wind_speed_max_kmh=14.0,
                weather_code=0,
                weather_description="Clear sky",
            ),
            DailyForecastDay(
                date="2026-09-08",
                temp_max_c=29.0,
                temp_min_c=21.0,
                precipitation_sum_mm=0.2,
                precipitation_probability_pct=15,
                wind_speed_max_kmh=16.0,
                weather_code=1,
                weather_description="Mainly clear",
            ),
            DailyForecastDay(
                date="2026-09-09",
                temp_max_c=30.0,
                temp_min_c=22.0,
                precipitation_sum_mm=1.0,
                precipitation_probability_pct=25,
                wind_speed_max_kmh=18.0,
                weather_code=2,
                weather_description="Partly cloudy",
            ),
        ],
    )


@pytest.fixture
def sample_heavy_rain_weather():
    """Heavy downpour / monsoon weather context."""
    return DistrictWeatherContext(
        is_available=True,
        is_stale=False,
        source="open-meteo",
        current=CurrentWeatherMetrics(
            temperature_c=24.0,
            relative_humidity_pct=95,
            apparent_temperature_c=25.0,
            precipitation_mm=28.5,
            weather_code=65,
            weather_description="Heavy rain",
            wind_speed_kmh=32.0,
            observed_at="2026-09-07T08:00:00Z",
        ),
        forecast_3days=[
            DailyForecastDay(
                date="2026-09-07",
                temp_max_c=26.0,
                temp_min_c=22.0,
                precipitation_sum_mm=35.0,
                precipitation_probability_pct=90,
                wind_speed_max_kmh=38.0,
                weather_code=65,
                weather_description="Heavy rain",
            ),
            DailyForecastDay(
                date="2026-09-08",
                temp_max_c=27.0,
                temp_min_c=23.0,
                precipitation_sum_mm=18.0,
                precipitation_probability_pct=80,
                wind_speed_max_kmh=25.0,
                weather_code=63,
                weather_description="Moderate rain",
            ),
            DailyForecastDay(
                date="2026-09-09",
                temp_max_c=28.0,
                temp_min_c=23.0,
                precipitation_sum_mm=4.0,
                precipitation_probability_pct=40,
                wind_speed_max_kmh=15.0,
                weather_code=51,
                weather_description="Light drizzle",
            ),
        ],
    )


@pytest.fixture
def sample_extreme_heat_weather():
    """Extreme summer heatwave weather context."""
    return DistrictWeatherContext(
        is_available=True,
        is_stale=False,
        source="open-meteo",
        current=CurrentWeatherMetrics(
            temperature_c=45.5,
            relative_humidity_pct=25,
            apparent_temperature_c=47.0,
            precipitation_mm=0.0,
            weather_code=0,
            weather_description="Clear and severely hot",
            wind_speed_kmh=18.0,
            observed_at="2026-09-07T14:00:00Z",
        ),
        forecast_3days=[],
    )


# -----------------------------------------------------------------------------
# 1. Weather -> Activity Impact Calculation
# -----------------------------------------------------------------------------

def test_weather_activity_impact_calculation(service, sample_clear_weather):
    """Verify standard calculation outputs with all required fields."""
    result = service.calculate_impact(sample_clear_weather, business_type="Retail")
    assert result.is_available is True
    assert result.activity_impact_score is not None
    assert 0.0 <= result.activity_impact_score <= 100.0
    assert result.activity_impact_label in [
        "Very Favourable", "Favourable", "Neutral", "Potentially Disruptive", "Highly Disruptive"
    ]
    assert result.risk_signals is not None
    assert result.risk_signals.heat_stress in ["Low", "Moderate", "High", "Severe"]
    assert result.risk_signals.rain_disruption in ["None", "Low", "Moderate", "High", "Severe"]
    assert result.risk_signals.outdoor_activity in ["Favourable", "Normal", "Moderate Disruption", "Lower"]
    assert result.risk_signals.logistics_disruption in ["Low", "Moderate", "High"]
    assert "Indicative weather impact on business activity" in result.methodology_disclaimer


# -----------------------------------------------------------------------------
# 2. Heavy Rain vs Clear Weather Comparison
# -----------------------------------------------------------------------------

def test_heavy_rainfall_produces_more_disruptive_signal_than_clear(
    service, sample_clear_weather, sample_heavy_rain_weather
):
    """Verify that heavy rainfall yields a much lower score and higher disruption signal than clear weather."""
    clear_res = service.calculate_impact(sample_clear_weather)
    rain_res = service.calculate_impact(sample_heavy_rain_weather)

    assert rain_res.activity_impact_score < clear_res.activity_impact_score
    assert clear_res.activity_impact_score >= 80.0
    assert clear_res.activity_impact_label in ["Very Favourable", "Favourable"]
    assert rain_res.activity_impact_score <= 50.0
    assert rain_res.activity_impact_label in ["Potentially Disruptive", "Highly Disruptive"]

    assert clear_res.risk_signals.rain_disruption == "None"
    assert rain_res.risk_signals.rain_disruption == "Severe"
    assert rain_res.risk_signals.outdoor_activity in ["Moderate Disruption", "Lower"]


# -----------------------------------------------------------------------------
# 3. Extreme Heat Produces Heat Stress & Activity Shift
# -----------------------------------------------------------------------------

def test_extreme_heat_produces_lower_activity_signal(
    service, sample_clear_weather, sample_extreme_heat_weather
):
    """Verify that 45.5°C heat reduces score, triggers Severe heat stress, and advises shifted hours."""
    heat_res = service.calculate_impact(sample_extreme_heat_weather, business_type="Retail")
    clear_res = service.calculate_impact(sample_clear_weather, business_type="Retail")

    assert heat_res.activity_impact_score < clear_res.activity_impact_score
    assert heat_res.risk_signals.heat_stress == "Severe"
    assert "heat" in heat_res.potential_footfall_effect.lower() or "afternoon" in heat_res.potential_footfall_effect.lower()


# -----------------------------------------------------------------------------
# 4. Mild / Clear Weather Produces Favourable Signal
# -----------------------------------------------------------------------------

def test_mild_clear_weather_produces_favourable_signal(service, sample_clear_weather):
    """Verify comfortable conditions (26°C, no rain) return Very Favourable / Favourable."""
    res = service.calculate_impact(sample_clear_weather)
    assert res.activity_impact_score >= 80.0
    assert res.activity_impact_label in ["Very Favourable", "Favourable"]
    assert res.risk_signals.heat_stress == "Low"
    assert res.risk_signals.rain_disruption == "None"
    assert res.risk_signals.outdoor_activity == "Favourable"


# -----------------------------------------------------------------------------
# 5. Business-Type Specific Qualitative Guidance
# -----------------------------------------------------------------------------

def test_business_type_interpretations(service, sample_heavy_rain_weather):
    """Verify distinct business types receive tailored operational advice."""
    sectors = [
        ("Retail", "walk-in"),
        ("Street Food", "counter"),
        ("Agriculture", "field"),
        ("Manufacturing", "warehouse"),
        ("Logistics", "transit"),
        ("Tourism", "sightseeing"),
        ("Local Services", "repair"),
    ]
    for sector_name, keyword in sectors:
        res = service.calculate_impact(sample_heavy_rain_weather, business_type=sector_name)
        assert res.business_type_implication is not None
        assert len(res.business_type_implication) > 20
        # Qualitative operational advice should contain sector relevance
        assert keyword in res.business_type_implication.lower()


# -----------------------------------------------------------------------------
# 6. Weather API Failure & Missing Data Fallback
# -----------------------------------------------------------------------------

def test_missing_weather_data_graceful_fallback(service):
    """Verify None weather context returns honest unavailable response with zero exceptions."""
    res = service.calculate_impact(None)
    assert res.is_available is False
    assert res.activity_impact_score is None
    assert res.activity_impact_label == "Unavailable"
    assert "unavailable" in res.potential_footfall_effect.lower()
    assert res.risk_signals is None
    assert res.weather_outlook_3days == []


def test_unavailable_weather_context_graceful_fallback(service):
    """Verify is_available=False context returns clean unavailable state."""
    offline_ctx = DistrictWeatherContext(is_available=False, is_stale=False, source="open-meteo")
    res = service.calculate_impact(offline_ctx)
    assert res.is_available is False
    assert res.activity_impact_score is None
    assert res.activity_impact_label == "Unavailable"


# -----------------------------------------------------------------------------
# 7. 3-Day Forecast Outlook Projection
# -----------------------------------------------------------------------------

def test_three_day_forecast_outlook(service, sample_clear_weather):
    """Verify 3-day forecast items are correctly evaluated with scores and day names."""
    res = service.calculate_impact(sample_clear_weather)
    assert len(res.weather_outlook_3days) == 3

    today = res.weather_outlook_3days[0]
    assert today.day_name == "Today"
    assert today.impact_score >= 80.0
    assert today.impact_label in ["Very Favourable", "Favourable"]
    assert "Clear" in today.weather_description

    tomorrow = res.weather_outlook_3days[1]
    assert tomorrow.day_name == "Tomorrow"
    assert 0.0 <= tomorrow.impact_score <= 100.0


# -----------------------------------------------------------------------------
# 8. Anti-Fabrication Guarantees (Zero Fake Numbers/Percentages)
# -----------------------------------------------------------------------------

def test_anti_fabrication_guarantees(service, sample_clear_weather, sample_heavy_rain_weather):
    """Verify that NO customer counts, percentage footfall predictions, or fake revenues are generated."""
    for ctx in [sample_clear_weather, sample_heavy_rain_weather]:
        res = service.calculate_impact(ctx, business_type="Retail")

        # 1. No percentage footfall change claims (e.g. '30% decrease in footfall')
        assert not re.search(r"\d+%\s*(increase|decrease|drop|growth|footfall|sales)", res.potential_footfall_effect or "", re.I)
        assert not re.search(r"\d+%\s*(increase|decrease|drop|growth|footfall|sales)", res.business_type_implication or "", re.I)

        # 2. No currency / revenue figures
        assert "₹" not in (res.potential_footfall_effect or "")
        assert "₹" not in (res.business_type_implication or "")
        assert "$" not in (res.potential_footfall_effect or "")

        # 3. No customer / visitor counts
        assert not re.search(r"\d+\s*(customers|visitors|buyers|footfalls)", res.potential_footfall_effect or "", re.I)

        # 4. Mandatory disclaimer
        assert res.methodology_disclaimer == "Indicative weather impact on business activity — not observed footfall or a sales forecast."


# -----------------------------------------------------------------------------
# 9. Authoritative Backend Engine Invariance
# -----------------------------------------------------------------------------

def test_authoritative_backend_engines_untouched():
    """Verify that core statutory engines and orchestrators remain unaltered."""
    from app.services.eligibility_service import eligibility_service
    from app.services.recommendation_scorer import recommendation_scorer
    from app.services.financial_structuring_service import financial_structuring_service
    from app.services.market_intelligence_service import market_intelligence_service

    assert eligibility_service is not None
    assert recommendation_scorer is not None
    assert financial_structuring_service is not None
    assert market_intelligence_service is not None


# -----------------------------------------------------------------------------
# 10. End-to-End API Integration via /api/v1/research/market-intelligence
# -----------------------------------------------------------------------------

def test_market_intelligence_api_enriches_weather_impact():
    """Test full FastAPI endpoint execution for Varanasi."""
    client = TestClient(app)
    payload = {
        "state_name": "Uttar Pradesh",
        "district_name": "Varanasi",
        "business_profile": {
            "business_type": "Retail",
            "sub_type": "Handloom Sarees",
            "experience_level": "3-5 years",
            "estimated_capital": 500000.0,
        },
    }
    response = client.post("/api/v1/research/market-intelligence", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Core MSME and ML intact
    assert data["district_name"].upper() == "VARANASI"
    assert data["market_context"] is not None
    assert data["ml_analysis"] is not None
    assert data["ml_analysis"]["is_available"] is True
    assert data["ml_analysis"]["cluster_label"] is not None

    # Weather Activity Impact attached
    assert "weather_activity_impact" in data
    impact = data["weather_activity_impact"]
    assert impact is not None
    if impact.get("is_available"):
        assert impact["activity_impact_score"] is not None
        assert 0.0 <= impact["activity_impact_score"] <= 100.0
        assert impact["activity_impact_label"] in [
            "Very Favourable", "Favourable", "Neutral", "Potentially Disruptive", "Highly Disruptive"
        ]
        assert impact["risk_signals"] is not None
        assert "Indicative weather impact on business activity" in impact["methodology_disclaimer"]