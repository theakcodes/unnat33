"""
tests/test_district_msme.py

Automated tests for District MSME data integration, repository queries,
service aggregation, and the district-market-context API endpoint.

Verifies:
1. Exact database counts: 36 states/UTs, 785 districts, 785 MSME records.
2. Verified total MSME aggregation: 27,917,022 registered units.
3. Fast window-function ranking: Pune (LGD 490) is #1 nationally with 705,534 MSMEs.
4. Flexible lookup by LGD code, district + state name, and case insensitivity.
5. Graceful state-level fallback for unrecognized or omitted districts.
6. API endpoint /api/v1/recommendations/district-market-context responses (200 OK & 404).
"""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.repositories.district_msme_repository import district_msme_repository
from app.services.district_msme_service import district_msme_service


def test_states_and_districts_database_counts(db_session: Session):
    """Verify PostgreSQL tables have exactly 36 states, 785 districts, and 785 MSME data records."""
    state_count = db_session.execute(text("SELECT COUNT(*) FROM states")).scalar()
    district_count = db_session.execute(text("SELECT COUNT(*) FROM districts")).scalar()
    msme_data_count = db_session.execute(text("SELECT COUNT(*) FROM msme_district_data")).scalar()

    assert state_count == 36, f"Expected 36 states/UTs, got {state_count}"
    assert district_count == 785, f"Expected 785 districts, got {district_count}"
    assert msme_data_count == 785, f"Expected 785 MSME district data records, got {msme_data_count}"


def test_msme_aggregate_totals_match_official_figures(db_session: Session):
    """Verify aggregated MSME sums match official Udyam dataset totals."""
    row = db_session.execute(
        text(
            """
            SELECT 
                SUM(micro_enterprises) AS micro,
                SUM(small_enterprises) AS small,
                SUM(medium_enterprises) AS medium
            FROM msme_district_data
            """
        )
    ).mappings().first()

    micro = int(row["micro"])
    small = int(row["small"])
    medium = int(row["medium"])
    total = micro + small + medium

    assert micro == 27136305, f"Micro enterprises sum mismatch: {micro}"
    assert small == 712961, f"Small enterprises sum mismatch: {small}"
    assert medium == 67756, f"Medium enterprises sum mismatch: {medium}"
    assert total == 27917022, f"Total MSMEs sum mismatch: {total}"


def test_pune_district_repository_lookup(db_session: Session):
    """Verify Pune lookup via LGD code 490 returns #1 national rank and expected enterprise metrics."""
    record = district_msme_repository.get_by_lgd_code(db_session, lg_dt_code="490")
    assert record is not None
    assert record["district_name"] == "PUNE"
    assert record["state_name"] == "MAHARASHTRA"
    assert record["national_rank"] == 1
    assert record["state_rank"] == 1
    assert record["total_msmes"] == 705534
    assert record["micro_enterprises"] == 687194
    assert record["small_enterprises"] == 16581
    assert record["medium_enterprises"] == 1759


def test_district_and_state_case_insensitive_lookup(db_session: Session):
    """Verify case-insensitive and whitespace-tolerant lookup for district and state."""
    record = district_msme_repository.get_by_district_and_state(
        db_session,
        district_name="  pune  ",
        state_name="  maharashtra  ",
    )
    assert record is not None
    assert record["district_name"] == "PUNE"
    assert record["lg_dt_code"] == "490"
    assert record["national_rank"] == 1


def test_state_aggregate_repository(db_session: Session):
    """Verify state aggregate metrics query returns correct district count and sums."""
    record = district_msme_repository.get_state_aggregate(db_session, state_name_or_code="Maharashtra")
    assert record is not None
    assert record["state_name"] == "MAHARASHTRA"
    assert record["total_districts_in_state"] == 36
    assert int(record["total_msmes"]) > 3000000


def test_district_msme_service_lgd_resolution(db_session: Session):
    """Verify DistrictMsmeService returns DistrictMarketContext model with calculated shares."""
    context = district_msme_service.get_market_context(db_session, lg_dt_code="490")
    assert context is not None
    assert context.geographic_level == "DISTRICT"
    assert context.district_name == "PUNE"
    assert context.state_name == "MAHARASHTRA"
    assert context.national_rank == 1
    assert context.total_districts_nationally == 785
    assert context.is_fallback is False
    assert 97.0 < context.micro_share < 98.0
    assert len(context.market_context_notes) > 0


def test_district_msme_service_state_level_fallback(db_session: Session):
    """Verify unknown district in known state gracefully triggers state-level fallback."""
    context = district_msme_service.get_market_context(
        db_session,
        district_name="NonExistentDistrictXYZ",
        state_name="Rajasthan",
    )
    assert context is not None
    assert context.geographic_level == "STATE"
    assert context.state_name == "RAJASTHAN"
    assert context.district_name is None
    assert context.lg_dt_code is None
    assert context.is_fallback is True
    assert context.national_rank is None
    assert context.total_msmes > 1000000
    assert any("fallback" in note.lower() for note in context.market_context_notes)


def test_district_msme_service_unresolved_returns_none(db_session: Session):
    """Verify unknown district and state returns None."""
    context = district_msme_service.get_market_context(
        db_session,
        district_name="CompletelyUnknown12345",
        state_name="NonExistentState99999",
    )
    assert context is None


def test_api_district_market_context_success(client: TestClient):
    """Verify GET /api/v1/recommendations/district-market-context returns 200 OK for valid district."""
    response = client.get("/api/v1/recommendations/district-market-context?district_name=Pune&state_name=Maharashtra")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["geographic_level"] == "DISTRICT"
    assert data["district_name"] == "PUNE"
    assert data["state_name"] == "MAHARASHTRA"
    assert data["national_rank"] == 1
    assert data["total_msmes"] == 705534
    assert data["is_fallback"] is False


def test_api_district_market_context_by_lgd(client: TestClient):
    """Verify GET /api/v1/recommendations/district-market-context resolves via LGD code."""
    response = client.get("/api/v1/recommendations/district-market-context?lg_dt_code=490")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["lg_dt_code"] == "490"
    assert data["district_name"] == "PUNE"


def test_api_district_market_context_fallback(client: TestClient):
    """Verify GET /api/v1/recommendations/district-market-context returns 200 OK with state fallback."""
    response = client.get("/api/v1/recommendations/district-market-context?district_name=UnknownDist&state_name=Rajasthan")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["geographic_level"] == "STATE"
    assert data["is_fallback"] is True
    assert data["state_name"] == "RAJASTHAN"


def test_api_district_market_context_404(client: TestClient):
    """Verify GET /api/v1/recommendations/district-market-context returns 404 when location cannot be resolved."""
    response = client.get("/api/v1/recommendations/district-market-context?district_name=FakeDistrict&state_name=FakeState")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_district_normalization_punctuation_parenthesis_variants(db_session: Session):
    """Verify punctuation and parenthesis variants (e.g. Bengaluru Urban) resolve to BENGALURU (URBAN)."""
    # 1. Plain string without parentheses
    res1 = district_msme_repository.get_by_district_and_state(
        db_session, district_name="Bengaluru Urban", state_name="Karnataka"
    )
    assert res1 is not None
    assert res1["district_name"] == "BENGALURU (URBAN)"
    assert res1["lg_dt_code"] == "525"

    # 2. String with parentheses
    res2 = district_msme_repository.get_by_district_and_state(
        db_session, district_name="bengaluru (urban)", state_name="Karnataka"
    )
    assert res2 is not None
    assert res2["district_name"] == "BENGALURU (URBAN)"

    # 3. Uppercase string without parentheses
    res3 = district_msme_repository.get_by_district_and_state(
        db_session, district_name="BENGALURU URBAN", state_name="Karnataka"
    )
    assert res3 is not None
    assert res3["district_name"] == "BENGALURU (URBAN)"


def test_district_normalization_aliases(db_session: Session):
    """Verify known spelling and numeral aliases (e.g. North 24 Parganas, Kolkata) resolve correctly."""
    # 1. North 24 Parganas -> NORTH 24 PRAGANAS
    res1 = district_msme_repository.get_by_district_and_state(
        db_session, district_name="North 24 Parganas", state_name="West Bengal"
    )
    assert res1 is not None
    assert res1["district_name"] == "NORTH 24 PRAGANAS"
    assert res1["lg_dt_code"] == "303"

    # 2. North Twenty Four Parganas -> NORTH 24 PRAGANAS
    res2 = district_msme_repository.get_by_district_and_state(
        db_session, district_name="North Twenty Four Parganas", state_name="West Bengal"
    )
    assert res2 is not None
    assert res2["district_name"] == "NORTH 24 PRAGANAS"

    # 3. Kolkata -> KOLKOTA
    res3 = district_msme_repository.get_by_district_and_state(
        db_session, district_name="Kolkata", state_name="West Bengal"
    )
    assert res3 is not None
    assert res3["district_name"] == "KOLKOTA"
    assert res3["lg_dt_code"] == "315"


def test_district_normalization_state_scoping(db_session: Session):
    """Verify same district name across different states resolves strictly to the scoped state."""
    # Bilaspur in Himachal Pradesh
    hp_res = district_msme_repository.get_by_district_and_state(
        db_session, district_name="Bilaspur", state_name="Himachal Pradesh"
    )
    assert hp_res is not None
    assert hp_res["state_name"] == "HIMACHAL PRADESH"
    assert hp_res["district_name"] == "BILASPUR"
    assert hp_res["lg_dt_code"] == "15"

    # Bilaspur in Chhattisgarh
    cg_res = district_msme_repository.get_by_district_and_state(
        db_session, district_name="Bilaspur", state_name="Chhattisgarh"
    )
    assert cg_res is not None
    assert cg_res["state_name"] == "CHHATTISGARH"
    assert cg_res["district_name"] == "BILASPUR"
    assert cg_res["lg_dt_code"] == "375"


def test_district_normalization_whitespace_and_case(db_session: Session):
    """Verify irregular whitespace and lowercase characters are normalized."""
    res = district_msme_repository.get_by_district_and_state(
        db_session,
        district_name="   bengaluru     urban   ",
        state_name="   karnataka   ",
    )
    assert res is not None
    assert res["district_name"] == "BENGALURU (URBAN)"


def test_district_fallback_transparency_unmatchable(db_session: Session):
    """Verify unmatchable district name falls back to state aggregate with full transparency notes."""
    context = district_msme_service.get_market_context(
        db_session,
        district_name="GenuinelyNonExistentDistrictName12345",
        state_name="Karnataka",
    )
    assert context is not None
    assert context.geographic_level == "STATE"
    assert context.is_fallback is True
    assert context.district_name is None
    assert context.state_name == "KARNATAKA"
    assert any("fallback" in note.lower() for note in context.market_context_notes)
