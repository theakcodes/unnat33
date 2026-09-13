"""
tests/test_programs_api.py

Automated integration tests for Government Programme API endpoints:
- GET /api/v1/programs (listing, pagination, multi-criteria filtering)
- GET /api/v1/programs/{program_id} (detail by ID and by program_code)

Verifies:
1. Exactly 60 programmes retrieved.
2. All 12 legacy programmes represented.
3. Programme detail returns metadata, benefit summary, portal URL, sectors, eligibility, credit/guarantee/subsidy details.
4. Filtering by status, primary_type, actionability_type, ministry, sector.
5. Pagination.
6. Zero duplicate programme codes or IDs.
7. Zero orphan relationships.
"""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text


def test_get_all_programs_count_60(client: TestClient):
    """Verify GET /api/v1/programs returns exactly 60 programmes."""
    response = client.get("/api/v1/programs?limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 60


def test_no_duplicate_program_codes_or_ids(client: TestClient):
    """Verify all 60 programmes have unique IDs and unique programme codes."""
    response = client.get("/api/v1/programs?limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    ids = [p["id"] for p in data]
    codes = [p["program_code"] for p in data]

    assert len(ids) == 60
    assert len(set(ids)) == 60
    assert len(codes) == 60
    assert len(set(codes)) == 60


def test_all_12_legacy_programs_represented(client: TestClient):
    """Verify all 12 legacy programmes are represented with valid legacy_scheme_id links."""
    response = client.get("/api/v1/programs?limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    legacy_progs = [p for p in data if p.get("legacy_scheme_id") is not None]
    assert len(legacy_progs) == 12

    legacy_ids = {p["legacy_scheme_id"] for p in legacy_progs}
    assert legacy_ids == set(range(1, 13))

    # Also verify non-legacy programmes count
    non_legacy_progs = [p for p in data if p.get("legacy_scheme_id") is None]
    assert len(non_legacy_progs) == 48


def test_program_detail_by_integer_id(client: TestClient):
    """Verify GET /api/v1/programs/{id} with integer ID returns full metadata and sectors."""
    response = client.get("/api/v1/programs/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == 1
    assert "program_code" in data
    assert "program_name" in data
    assert "owning_ministry" in data
    assert "official_portal_url" in data
    assert "benefit_summary" in data
    assert "actionability_type" in data
    assert "hierarchy_level" in data
    assert "status" in data
    assert isinstance(data.get("sectors"), list)
    assert len(data["sectors"]) > 0


def test_program_detail_by_code(client: TestClient):
    """Verify GET /api/v1/programs/{code} with program code returns credit details."""
    response = client.get("/api/v1/programs/STANDUP_INDIA")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["program_code"] == "STANDUP_INDIA"
    assert "Stand-Up India" in data["program_name"]
    assert data["primary_type"] == "CREDIT / LOAN"
    assert data["credit_details"] is not None
    assert data["credit_details"]["min_loan_amount"] == 1000000.0
    assert data["credit_details"]["max_loan_amount"] == 10000000.0
    assert data["credit_details"]["collateral_required"] is False


def test_program_detail_guarantee_details(client: TestClient):
    """Verify guarantee details are present for guarantee programmes (e.g. CGTMSE)."""
    response = client.get("/api/v1/programs/CGTMSE")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["program_code"] == "CGTMSE"
    assert data["primary_type"] == "CREDIT GUARANTEE"
    assert data["guarantee_details"] is not None
    assert data["guarantee_details"]["max_credit_limit"] == 100000000.0
    assert data["guarantee_details"]["guarantee_coverage_pct"] == 85.0


def test_program_detail_subsidy_details(client: TestClient):
    """Verify subsidy details are present for subsidy programmes (e.g. PMFME)."""
    response = client.get("/api/v1/programs/PMFME")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["program_code"] == "PMFME"
    assert data["subsidy_details"] is not None
    assert data["subsidy_details"]["subsidy_pct"] == 35.0
    assert data["subsidy_details"]["max_subsidy_amount"] == 1000000.0


def test_program_detail_eligibility(client: TestClient):
    """Verify eligibility criteria is resolved for programmes (e.g. MSME_ZED)."""
    response = client.get("/api/v1/programs/MSME_ZED")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["program_code"] == "MSME_ZED"
    assert data["eligibility"] is not None
    assert data["eligibility"]["general_eligible"] is True
    assert data["eligibility"]["sc_eligible"] is True
    assert data["eligibility"]["st_eligible"] is True
    assert data["eligibility"]["female_eligible"] is True


def test_program_detail_not_found(client: TestClient):
    """Verify 404 response when querying nonexistent programme."""
    response = client.get("/api/v1/programs/NONEXISTENT_CODE_99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"] == "Not Found"
    assert "NONEXISTENT_CODE_99999" in data["detail"]


def test_filter_by_status(client: TestClient):
    """Verify status query filter."""
    response = client.get("/api/v1/programs?status=active&limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    for p in data:
        assert p["status"].lower() == "active"


def test_filter_by_primary_type(client: TestClient):
    """Verify primary_type query filter."""
    response = client.get("/api/v1/programs?primary_type=CREDIT%20GUARANTEE&limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    for p in data:
        assert "GUARANTEE" in p["primary_type"].upper()


def test_filter_by_actionability_type(client: TestClient):
    """Verify actionability_type query filter."""
    response = client.get("/api/v1/programs?actionability_type=DIRECTLY_RECOMMENDABLE&limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    for p in data:
        assert "RECOMMENDABLE" in p["actionability_type"].upper()


def test_filter_by_ministry(client: TestClient):
    """Verify ministry query filter."""
    response = client.get("/api/v1/programs?ministry=Ministry%20of%20Finance&limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    for p in data:
        assert "Finance" in p["owning_ministry"]


def test_filter_by_sector(client: TestClient):
    """Verify sector query filter matches programmes across unified sector views."""
    response = client.get("/api/v1/programs?sector=Manufacturing&limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0

    # Every returned program should have Manufacturing in its sectors list
    for p in data:
        sector_names = [s["sector_name"] for s in p["sectors"]]
        sector_codes = [s.get("sector_code") for s in p["sectors"]]
        assert "Manufacturing" in sector_names or "MFG" in sector_codes


def test_pagination(client: TestClient):
    """Verify skip and limit parameters enforce proper pagination."""
    res_first_10 = client.get("/api/v1/programs?skip=0&limit=10")
    assert res_first_10.status_code == status.HTTP_200_OK
    page1 = res_first_10.json()
    assert len(page1) == 10

    res_next_10 = client.get("/api/v1/programs?skip=10&limit=10")
    assert res_next_10.status_code == status.HTTP_200_OK
    page2 = res_next_10.json()
    assert len(page2) == 10

    # Ensure no overlap
    page1_ids = {p["id"] for p in page1}
    page2_ids = {p["id"] for p in page2}
    assert page1_ids.isdisjoint(page2_ids)


def test_no_orphan_relationships_in_db(db_session: Session):
    """Verify no orphan foreign key references exist across program tables."""
    # Orphan program_sectors
    orphan_ps = db_session.execute(text("""
        SELECT COUNT(*) FROM program_sectors ps
        LEFT JOIN government_programs gp ON ps.program_id = gp.id
        LEFT JOIN sectors s ON ps.sector_id = s.id
        WHERE gp.id IS NULL OR s.id IS NULL;
    """)).scalar()
    assert orphan_ps == 0

    # Orphan program_eligibility
    orphan_pe = db_session.execute(text("""
        SELECT COUNT(*) FROM program_eligibility pe
        LEFT JOIN government_programs gp ON pe.program_id = gp.id
        WHERE gp.id IS NULL;
    """)).scalar()
    assert orphan_pe == 0

    # Orphan credit details
    orphan_credit = db_session.execute(text("""
        SELECT COUNT(*) FROM program_credit_details cd
        LEFT JOIN government_programs gp ON cd.program_id = gp.id
        WHERE gp.id IS NULL;
    """)).scalar()
    assert orphan_credit == 0

    # Orphan guarantee details
    orphan_guarantee = db_session.execute(text("""
        SELECT COUNT(*) FROM program_guarantee_details gd
        LEFT JOIN government_programs gp ON gd.program_id = gp.id
        WHERE gp.id IS NULL;
    """)).scalar()
    assert orphan_guarantee == 0

    # Orphan subsidy details
    orphan_subsidy = db_session.execute(text("""
        SELECT COUNT(*) FROM program_subsidy_details sd
        LEFT JOIN government_programs gp ON sd.program_id = gp.id
        WHERE gp.id IS NULL;
    """)).scalar()
    assert orphan_subsidy == 0
