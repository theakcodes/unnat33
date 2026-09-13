"""
tests/test_market_similarity.py

Test suite for scikit-learn NearestNeighbors Market Similarity:
- Dataset loading and consistency with KMeans (785 districts)
- Euclidean distance calculation in standardized feature space
- Deterministic proximity ranking (rank 1 is closest non-identical district)
- Exclusion of self / identical duplicates
- Zero percentage similarity claims
- Integration with POST /api/v1/research/market-intelligence
- Failure isolation and graceful fallback
"""

import pytest
import re
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.services.market_similarity_service import MarketSimilarityService, market_similarity_service
from app.services.market_research_ml_service import ML_FEATURES


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


def test_market_similarity_fit(db_session: Session):
    """Verify MarketSimilarityService fits on the 785-district dataset with standardized features."""
    service = MarketSimilarityService(n_neighbors=5)
    service.fit(db_session)

    assert service._is_fitted is True
    assert service._dataset_df is not None
    assert len(service._dataset_df) >= 700  # Census districts
    assert service._scaled_matrix is not None
    assert service._scaled_matrix.shape[1] == len(ML_FEATURES)


def test_comparable_markets_for_varanasi(db_session: Session):
    """Verify comparable districts returned for Varanasi are structurally sound and deterministic."""
    res = market_similarity_service.get_comparable_markets(
        db=db_session,
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        top_k=4,
    )

    assert res.is_available is True
    assert res.target_district.upper() == "VARANASI"
    assert len(res.comparable_districts) == 4

    # Verify self-exclusion
    district_names = [d.district_name.upper() for d in res.comparable_districts]
    assert "VARANASI" not in district_names

    # Verify rankings and distance monotonicity
    prev_dist = -1.0
    for idx, item in enumerate(res.comparable_districts, start=1):
        assert item.similarity_rank == idx
        assert item.similarity_distance >= 0.0
        assert item.similarity_distance >= prev_dist
        prev_dist = item.similarity_distance
        assert item.total_msmes > 0
        assert item.micro_share >= 0.0
        assert item.provenance == "MODELLED INDICATOR"
        assert len(item.qualitative_observation) > 10


def test_zero_percentage_similarity_claims(db_session: Session):
    """CRITICAL: Verify zero percentage similarity claims appear in output."""
    res = market_similarity_service.get_comparable_markets(
        db=db_session,
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        top_k=4,
    )

    full_text = str(res.model_dump())
    assert not re.search(r"\b\d+%\s*similar\b", full_text, re.IGNORECASE)
    assert not re.search(r"similarity\s*percentage", full_text, re.IGNORECASE)
    assert not re.search(r"\b\d+%\s*match\b", full_text, re.IGNORECASE)


def test_market_intelligence_api_enrichment(client: TestClient):
    """Verify POST /api/v1/research/market-intelligence returns comparable_markets alongside weather."""
    payload = {
        "district_name": "Varanasi",
        "state_name": "Uttar Pradesh",
        "business_profile": {
            "business_type": "Handloom & Textiles",
            "estimated_capital": 500000.0,
        },
    }
    response = client.post("/api/v1/research/market-intelligence", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "comparable_markets" in data
    comp = data["comparable_markets"]
    assert comp is not None
    assert comp["is_available"] is True
    assert len(comp["comparable_districts"]) == 4
    assert comp["comparable_districts"][0]["similarity_rank"] == 1
    assert comp["comparable_districts"][0]["provenance"] == "MODELLED INDICATOR"


def test_failure_isolation_missing_district(db_session: Session):
    """Verify graceful handling for non-existent district without raising exceptions."""
    res = market_similarity_service.get_comparable_markets(
        db=db_session,
        district_name="NonExistentDistrictXYZ999",
        state_name="Atlantis",
    )
    # Should return fallback or best effort without exception
    assert res is not None
    assert isinstance(res.comparable_districts, list)
