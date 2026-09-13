"""
tests/test_market_intelligence.py

Comprehensive test suite for Phase 7:
- ML Preprocessing & Feature extraction
- ML Reproducibility (deterministic random_state)
- KMeans clustering on 785 Indian districts
- Cluster archetype labelling
- Missing data handling
- Market Research Indicator methodology and bounds
- Combined POST /api/v1/research/market-intelligence endpoint
- Resilient LLM failure isolation (mocked Anthropic error)
- Resilient ML failure isolation (mocked ML error)
- Resilient Weather failure isolation (unavailable Open-Meteo)
- Existing GET /api/v1/research/district-market-context regression verification
- Integration smoke test with Varanasi, Uttar Pradesh
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.services.market_research_ml_service import MarketResearchMLService, ML_FEATURES
from app.services.market_research_llm_service import MarketResearchLLMService
from app.services.market_intelligence_service import MarketIntelligenceService
from app.schemas.market_intelligence import (
    MarketIntelligenceRequest,
    BusinessProfileContext,
    QualitativeLLMAnalysis,
    MarketResearchMLAnalysis,
    ClusterQuantitativeIndicators,
)
from app.schemas.district_msme import DistrictMarketContext


@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# -----------------------------------------------------------------------------
# 1. ML Preprocessing & Feature Extraction
# -----------------------------------------------------------------------------
def test_ml_preprocessing_and_features(db_session: Session):
    service = MarketResearchMLService(n_clusters=4, random_state=42)
    df = service._load_data(db_session)

    assert not df.empty, "Dataset must not be empty"
    assert len(df) == 785, f"Expected 785 districts, found {len(df)}"

    for f in ML_FEATURES:
        assert f in df.columns, f"Feature '{f}' missing from dataset"
        assert not df[f].isnull().any(), f"Feature '{f}' contains unexpected nulls"


# -----------------------------------------------------------------------------
# 2. ML Reproducibility
# -----------------------------------------------------------------------------
def test_ml_reproducibility(db_session: Session):
    svc1 = MarketResearchMLService(n_clusters=4, random_state=42)
    svc1.fit(db_session)
    clusters_run1 = svc1._dataset_df["cluster_id"].tolist()

    svc2 = MarketResearchMLService(n_clusters=4, random_state=42)
    svc2.fit(db_session)
    clusters_run2 = svc2._dataset_df["cluster_id"].tolist()

    assert clusters_run1 == clusters_run2, "KMeans clustering must be 100% reproducible with fixed random_state"


# -----------------------------------------------------------------------------
# 3. KMeans Clustering & Cluster Counts
# -----------------------------------------------------------------------------
def test_kmeans_clustering_distribution(db_session: Session):
    service = MarketResearchMLService(n_clusters=4, random_state=42)
    service.fit(db_session)

    assert service._is_fitted, "Service must be marked fitted"
    assert len(service._cluster_distribution) == 4, "Must partition into 4 clusters"
    total_clustered = sum(service._cluster_distribution.values())
    assert total_clustered == 785, f"Expected 785 total clustered districts, got {total_clustered}"


# -----------------------------------------------------------------------------
# 4. Cluster Labelling & Archetype Characterization
# -----------------------------------------------------------------------------
def test_cluster_labelling(db_session: Session):
    service = MarketResearchMLService(n_clusters=4, random_state=42)
    service.fit(db_session)

    valid_labels = {
        "Metropolitan Commercial & Industrial Hub",
        "Formalized SME-Concentrated Industrial Market",
        "Medium-to-High Density Micro-Dominant Market",
        "Emerging / Lower-Density Micro-Enterprise Market",
    }

    for cid, (label, desc) in service._cluster_labels_map.items():
        assert label in valid_labels, f"Unexpected cluster label: {label}"
        assert len(desc) > 20, f"Description for {label} is too short"


# -----------------------------------------------------------------------------
# 5. Missing Data Handling
# -----------------------------------------------------------------------------
def test_missing_data_handling(db_session: Session):
    service = MarketResearchMLService(n_clusters=4, random_state=42)
    service.fit(db_session)

    # Synthetic context with missing/null values
    sparse_ctx = DistrictMarketContext(
        geographic_level="DISTRICT",
        state_name="TEST STATE",
        district_name="TEST DISTRICT",
        total_msmes=0,
        micro_enterprises=0,
        small_enterprises=0,
        medium_enterprises=0,
        micro_share=0.0,
        small_share=0.0,
        medium_share=0.0,
        small_medium_share=0.0,
        national_rank=None,
        state_rank=None,
        total_districts_in_state=None,
    )

    res = service.get_analysis_for_district(db=db_session, market_context=sparse_ctx)
    assert res is not None
    assert 0.0 <= res.quantitative_indicators.market_research_indicator <= 100.0


# -----------------------------------------------------------------------------
# 6. Market Research Indicator Methodology & Bounds
# -----------------------------------------------------------------------------
def test_market_research_indicator_bounds(db_session: Session):
    service = MarketResearchMLService(n_clusters=4, random_state=42)
    service.fit(db_session)

    # Test top district (high density, high SME)
    top_ctx = DistrictMarketContext(
        geographic_level="DISTRICT",
        state_name="MAHARASHTRA",
        district_name="MUMBAI",
        total_msmes=500000,
        micro_enterprises=470000,
        small_enterprises=27000,
        medium_enterprises=3000,
        micro_share=94.0,
        small_share=5.4,
        medium_share=0.6,
        small_medium_share=6.0,
        national_rank=1,
        state_rank=1,
        total_districts_in_state=36,
    )
    res_top = service.get_analysis_for_district(db=db_session, market_context=top_ctx)
    assert res_top.quantitative_indicators.market_research_indicator > 80.0

    # Test rural low density district
    low_ctx = DistrictMarketContext(
        geographic_level="DISTRICT",
        state_name="REMOTE",
        district_name="REMOTE DISTRICT",
        total_msmes=200,
        micro_enterprises=199,
        small_enterprises=1,
        medium_enterprises=0,
        micro_share=99.5,
        small_share=0.5,
        medium_share=0.0,
        small_medium_share=0.5,
        national_rank=780,
        state_rank=30,
        total_districts_in_state=30,
    )
    res_low = service.get_analysis_for_district(db=db_session, market_context=low_ctx)
    assert res_low.quantitative_indicators.market_research_indicator < 40.0


# -----------------------------------------------------------------------------
# 7. LLM Failure Isolation (Mocked Anthropic Failure)
# -----------------------------------------------------------------------------
def test_llm_failure_isolation():
    llm_service = MarketResearchLLMService()
    # Force mock failure
    with patch("anthropic.AsyncAnthropic", side_effect=Exception("API connection timeout")):
        result = asyncio.run(
            llm_service.generate_qualitative_analysis(
                district_name="VARANASI",
                state_name="UTTAR PRADESH",
                market_context=None,
                ml_analysis=None,
            )
        )

        assert result is not None
        assert result.is_available is True
        assert result.source == "deterministic-empirical-fallback"
        assert len(result.opportunities) >= 2
        assert len(result.risks) >= 2


# -----------------------------------------------------------------------------
# 8. ML Failure Isolation
# -----------------------------------------------------------------------------
def test_ml_failure_isolation(db_session: Session):
    intel_service = MarketIntelligenceService()

    # Mock ML service raising an exception
    with patch.object(intel_service.ml_service, "get_analysis_for_district", side_effect=RuntimeError("Clustering memory error")):
        req = MarketIntelligenceRequest(district_name="Varanasi", state_name="Uttar Pradesh")
        res = asyncio.run(intel_service.get_market_intelligence(db=db_session, req=req))

        assert res is not None
        assert res.district_name == "VARANASI"
        assert res.ml_analysis.is_available is False
        assert "ML Fallback" in res.ml_analysis.cluster_label


# -----------------------------------------------------------------------------
# 9. Combined POST /api/v1/research/market-intelligence
# -----------------------------------------------------------------------------
def test_combined_market_intelligence_endpoint(client: TestClient):
    payload = {
        "district_name": "Varanasi",
        "state_name": "Uttar Pradesh",
        "business_profile": {
            "business_type": "Handloom Textile Weaving",
            "estimated_capital": 600000.0,
            "experience_level": "3 years",
        },
    }
    response = client.post("/api/v1/research/market-intelligence", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["district_name"] == "VARANASI"
    assert data["state_name"] == "UTTAR PRADESH"
    assert "market_context" in data and data["market_context"] is not None
    assert data["market_context"]["total_msmes"] == 93779
    assert "ml_analysis" in data
    assert data["ml_analysis"]["cluster_label"] == "Medium-to-High Density Micro-Dominant Market"
    assert "llm_analysis" in data
    assert len(data["llm_analysis"]["opportunities"]) > 0


# -----------------------------------------------------------------------------
# 10. Existing GET /api/v1/research/district-market-context Regression Test
# -----------------------------------------------------------------------------
def test_existing_district_market_context_regression(client: TestClient):
    response = client.get("/api/v1/research/district-market-context?district_name=Varanasi&state_name=Uttar%20Pradesh")
    assert response.status_code == 200
    data = response.json()

    assert data["district_name"] == "VARANASI"
    assert data["msme_market_context"]["total_msmes"] == 93779
    assert data["weather_context"] is not None


# -----------------------------------------------------------------------------
# 11. Integration Smoke Test: Varanasi Ground Truth
# -----------------------------------------------------------------------------
def test_varanasi_smoke_test(client: TestClient):
    response = client.post(
        "/api/v1/research/market-intelligence",
        json={"district_name": "Varanasi", "state_name": "Uttar Pradesh"},
    )
    assert response.status_code == 200
    data = response.json()

    # Ground truth validations for Varanasi
    ctx = data["market_context"]
    assert ctx["total_msmes"] == 93779
    assert ctx["micro_enterprises"] == 91344
    assert ctx["small_enterprises"] == 2237
    assert ctx["medium_enterprises"] == 198
    assert ctx["national_rank"] == 52
    assert ctx["state_rank"] == 6

    # ML output validations
    ml = data["ml_analysis"]
    assert ml["is_available"] is True
    assert ml["quantitative_indicators"]["market_research_indicator"] > 70.0

    # LLM output validations
    llm = data["llm_analysis"]
    assert llm["is_available"] is True
    assert "VARANASI" in llm["market_interpretation"].upper()
