from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_all_schemes(client: TestClient):
    """Test 4: GET /api/v1/schemes returns all 12 schemes as Pydantic models."""
    response = client.get("/api/v1/schemes")
    assert response.status_code == status.HTTP_200_OK
    schemes = response.json()
    assert isinstance(schemes, list)
    assert len(schemes) == 12

    # Verify schema structure of first scheme
    first_scheme = schemes[0]
    assert "id" in first_scheme
    assert "name" in first_scheme
    assert "ministry" in first_scheme
    assert "scheme_type" in first_scheme
    assert "state" in first_scheme


def test_get_scheme_by_id(client: TestClient):
    """Test 5: GET /api/v1/schemes/{id} returns specific scheme details."""
    response = client.get("/api/v1/schemes/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert "PM MUDRA - Shishu" in data["name"]
    assert data["ministry"] == "Ministry of Finance"
    assert data["scheme_type"] == "loan"
    assert data["max_loan_amount"] == 50000.0


def test_get_scheme_by_id_not_found(client: TestClient):
    """Test 6: GET /api/v1/schemes/{id} returns 404 for nonexistent scheme."""
    response = client.get("/api/v1/schemes/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"] == "Not Found"
    assert "Scheme with ID 999999 not found" in data["detail"]


def test_state_filtering(client: TestClient):
    """Test 7: State filtering query parameter."""
    # Nationwide schemes apply across all India
    res_all_india = client.get("/api/v1/schemes?state=All India")
    assert res_all_india.status_code == status.HTTP_200_OK
    assert len(res_all_india.json()) == 12

    # Filtering by Rajasthan with include_all_india=True (default) returns all nationwide applicable schemes
    res_rajasthan = client.get("/api/v1/schemes?state=Rajasthan")
    assert res_rajasthan.status_code == status.HTTP_200_OK
    assert len(res_rajasthan.json()) == 12

    # Strict filtering for state without nationwide schemes returns empty list (since all current 12 are Central)
    res_strict = client.get("/api/v1/schemes?state=NonExistentState&include_all_india=false")
    assert res_strict.status_code == status.HTTP_200_OK
    assert len(res_strict.json()) == 0


def test_sector_filtering(client: TestClient):
    """Test 8: Sector filtering query parameter."""
    # Test filtering by Micro Enterprise
    res_micro = client.get("/api/v1/schemes?sector=Micro Enterprise")
    assert res_micro.status_code == status.HTTP_200_OK
    micro_schemes = res_micro.json()
    assert len(micro_schemes) >= 6
    for s in micro_schemes:
        assert (
            "micro" in s["sector"].lower()
            or (s["business_type"] and "micro" in s["business_type"].lower())
        )

    # Test filtering by Artisan
    res_artisan = client.get("/api/v1/schemes?sector=Artisan Enterprise")
    assert res_artisan.status_code == status.HTTP_200_OK
    artisan_schemes = res_artisan.json()
    assert len(artisan_schemes) >= 1
    assert any("Vishwakarma" in s["name"] for s in artisan_schemes)

    # Test filtering by Manufacturing (matched via business activity)
    res_mfg = client.get("/api/v1/schemes?sector=Manufacturing")
    assert res_mfg.status_code == status.HTTP_200_OK
    mfg_schemes = res_mfg.json()
    assert len(mfg_schemes) > 0


def test_multiple_filters(client: TestClient):
    """Test 9: Combining multiple query parameter filters."""
    # Sector = Micro Enterprise AND scheme_type = loan
    response = client.get("/api/v1/schemes?sector=Micro Enterprise&scheme_type=loan")
    assert response.status_code == status.HTTP_200_OK
    schemes = response.json()
    assert len(schemes) >= 4  # MUDRA Shishu, Kishore, Tarun, Tarun Plus
    for s in schemes:
        assert "loan" in s["scheme_type"].lower()

    # Category = NSFDC Financing AND target_group = Scheduled Caste
    res_nsfdc = client.get("/api/v1/schemes?category=NSFDC Financing&target_group=Scheduled Caste")
    assert res_nsfdc.status_code == status.HTTP_200_OK
    assert len(res_nsfdc.json()) == 4  # All 4 NSFDC schemes


def test_legacy_route_compatibility(client: TestClient):
    """Test backwards compatibility of /api/schemes route."""
    response = client.get("/api/schemes")
    assert response.status_code == status.HTTP_200_OK
    schemes = response.json()
    assert isinstance(schemes, list)
    assert len(schemes) == 12


def test_deterministic_eligibility_engine(client: TestClient):
    """Test deterministic rule-based eligibility evaluation endpoint."""
    # Profile for a young entrepreneur with micro project (₹40,000)
    profile = {
        "age": 28,
        "gender": "Female",
        "state": "Rajasthan",
        "is_rural": False,
        "annual_income": 200000,
        "project_cost": 40000,
        "requested_loan_amount": 40000,
        "is_new_business": True,
        "social_category": "General",
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_evaluated"] == 12
    assert data["total_eligible"] > 0
    # MUDRA Shishu (up to 50k) should be eligible
    eligible_ids = [s["scheme_id"] for s in data["eligible_schemes"]]
    assert 1 in eligible_ids  # PM MUDRA Shishu


def test_normalized_eligibility_criteria_relationship(db_session: Session):
    """Verify that scheme_eligibility records are properly linked via ORM."""
    from app.models.scheme import Scheme

    # Scheme 9: NSFDC MFS (SC only, 5L ceiling)
    scheme_9 = db_session.query(Scheme).filter(Scheme.id == 9).first()
    assert scheme_9 is not None
    assert scheme_9.eligibility_criteria is not None
    assert scheme_9.eligibility_criteria.sc_eligible is True
    assert scheme_9.eligibility_criteria.general_eligible is False
    assert scheme_9.eligibility_criteria.max_annual_income == 500000.00

    # Scheme 1: MUDRA Shishu (Universal, social category is NULL)
    scheme_1 = db_session.query(Scheme).filter(Scheme.id == 1).first()
    assert scheme_1 is not None
    assert scheme_1.eligibility_criteria is not None
    assert scheme_1.eligibility_criteria.general_eligible is None
    assert scheme_1.eligibility_criteria.sc_eligible is None

    # Scheme 8: PM SVANidhi (Urban street vendors, rural_eligible is False)
    scheme_8 = db_session.query(Scheme).filter(Scheme.id == 8).first()
    assert scheme_8 is not None
    assert scheme_8.eligibility_criteria is not None
    assert scheme_8.eligibility_criteria.rural_eligible is False
    assert scheme_8.eligibility_criteria.urban_eligible is True

    # Scheme 5: PMEGP (min_age 18, broad category support)
    scheme_5 = db_session.query(Scheme).filter(Scheme.id == 5).first()
    assert scheme_5 is not None
    assert scheme_5.eligibility_criteria is not None
    assert scheme_5.eligibility_criteria.min_age == 18
    assert scheme_5.eligibility_criteria.general_eligible is True
    assert scheme_5.eligibility_criteria.sc_eligible is True


def test_normalized_sector_mappings_relationship(db_session: Session):
    """Verify that scheme_sectors relationships accurately reflect source data."""
    from app.models.scheme import Scheme

    # Scheme 1 (MUDRA Shishu): MFG, SRV, TRD
    scheme_1 = db_session.query(Scheme).filter(Scheme.id == 1).first()
    sector_codes_1 = {s.sector_code for s in scheme_1.sectors_mapped}
    assert sector_codes_1 == {"MFG", "SRV", "TRD"}

    # Scheme 7 (PM Vishwakarma): ART
    scheme_7 = db_session.query(Scheme).filter(Scheme.id == 7).first()
    sector_codes_7 = {s.sector_code for s in scheme_7.sectors_mapped}
    assert sector_codes_7 == {"ART"}

    # Scheme 8 (PM SVANidhi): No direct sector mapped (informal street vending)
    scheme_8 = db_session.query(Scheme).filter(Scheme.id == 8).first()
    assert len(scheme_8.sectors_mapped) == 0

    # Scheme 9 (NSFDC MFS): AGR, MFG, SRV, TRD
    scheme_9 = db_session.query(Scheme).filter(Scheme.id == 9).first()
    sector_codes_9 = {s.sector_code for s in scheme_9.sectors_mapped}
    assert sector_codes_9 == {"AGR", "MFG", "SRV", "TRD"}


def test_canonical_sector_filtering_api(client: TestClient):
    """Test 14: Sector filtering via repository/API supports canonical names and codes."""
    # Canonical names
    res_trd_name = client.get("/api/v1/schemes?sector=Trading / Retail")
    assert res_trd_name.status_code == status.HTTP_200_OK
    trd_ids = {s["id"] for s in res_trd_name.json()}
    assert {1, 2, 3, 4, 9, 11}.issubset(trd_ids)

    res_agr_name = client.get("/api/v1/schemes?sector=Agriculture and Allied Activities")
    assert res_agr_name.status_code == status.HTTP_200_OK
    agr_ids = {s["id"] for s in res_agr_name.json()}
    assert {9, 11}.issubset(agr_ids)

    res_art_name = client.get("/api/v1/schemes?sector=Artisans and Traditional Crafts")
    assert res_art_name.status_code == status.HTTP_200_OK
    art_ids = {s["id"] for s in res_art_name.json()}
    assert 7 in art_ids

    # Canonical codes
    res_trd_code = client.get("/api/v1/schemes?sector=TRD")
    assert res_trd_code.status_code == status.HTTP_200_OK
    assert {s["id"] for s in res_trd_code.json()} == trd_ids

    res_agr_code = client.get("/api/v1/schemes?sector=AGR")
    assert res_agr_code.status_code == status.HTTP_200_OK
    assert {s["id"] for s in res_agr_code.json()} == agr_ids

    res_art_code = client.get("/api/v1/schemes?sector=ART")
    assert res_art_code.status_code == status.HTTP_200_OK
    assert {s["id"] for s in res_art_code.json()} == art_ids

    res_mfg_code = client.get("/api/v1/schemes?sector=MFG")
    assert res_mfg_code.status_code == status.HTTP_200_OK
    mfg_ids = {s["id"] for s in res_mfg_code.json()}
    assert {1, 2, 3, 4, 5, 9, 11}.issubset(mfg_ids)

    res_srv_code = client.get("/api/v1/schemes?sector=SRV")
    assert res_srv_code.status_code == status.HTTP_200_OK
    srv_ids = {s["id"] for s in res_srv_code.json()}
    assert {1, 2, 3, 4, 6, 9, 11}.issubset(srv_ids)


def test_manufacturing_sector_eligibility_matching(client: TestClient):
    """Test 1: A Manufacturing business can match schemes mapped to Manufacturing."""
    profile = {
        "age": 30,
        "is_rural": False,
        "sector": "Manufacturing",
        "project_cost": 500000,
        "requested_loan_amount": 400000,
        "annual_income": 200000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    eligible_ids = {s["scheme_id"] for s in data["eligible_schemes"]}
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}

    # MUDRA Kishore (2) and PMEGP (5) are mapped to MFG and accept new businesses -> Eligible
    assert 2 in eligible_ids
    assert 5 in eligible_ids
    # PMEGP 2nd Loan (6) requires existing business -> Ineligible
    assert 6 in ineligible_ids
    # PM Vishwakarma (7) is ART only -> Ineligible
    assert 7 in ineligible_ids


def test_services_sector_eligibility_matching(client: TestClient):
    """Test 2: A Services business can match schemes mapped to Services."""
    profile = {
        "age": 30,
        "is_rural": False,
        "sector": "Services",
        "project_cost": 500000,
        "requested_loan_amount": 400000,
        "annual_income": 200000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    eligible_ids = {s["scheme_id"] for s in data["eligible_schemes"]}
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}

    # MUDRA Kishore (2) and PMEGP (5) are mapped to SRV -> Eligible
    assert 2 in eligible_ids
    assert 5 in eligible_ids
    # PMEGP 2nd Loan (6) is for existing business upgradation -> Ineligible
    assert 6 in ineligible_ids
    # PM Vishwakarma (7) is ART only -> Ineligible
    assert 7 in ineligible_ids


def test_trading_sector_eligibility_matching(client: TestClient):
    """Test 3: A Trading business can match schemes mapped to Trading / Retail."""
    profile = {
        "age": 30,
        "is_rural": False,
        "sector": "Trading / Retail",
        "project_cost": 500000,
        "requested_loan_amount": 400000,
        "annual_income": 200000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    eligible_ids = {s["scheme_id"] for s in data["eligible_schemes"]}
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}

    # MUDRA Kishore (2) includes TRD -> Eligible
    assert 2 in eligible_ids
    # PMEGP Mfg (5) and PMEGP Srv (6) exclude trading -> Ineligible
    assert 5 in ineligible_ids
    assert 6 in ineligible_ids


def test_agriculture_sector_eligibility_matching(client: TestClient):
    """Test 4: An Agriculture business can match schemes mapped to Agriculture and Allied Activities."""
    profile = {
        "age": 30,
        "is_rural": False,
        "sector": "Agriculture and Allied Activities",
        "social_category": "SC",
        "annual_income": 200000,
        "project_cost": 100000,
        "requested_loan_amount": 90000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    eligible_ids = {s["scheme_id"] for s in data["eligible_schemes"]}
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}

    # NSFDC MFS (9) includes AGR -> Eligible
    assert 9 in eligible_ids
    # MUDRA (1-4) only covers MFG, SRV, TRD -> Ineligible
    assert {1, 2, 3, 4}.issubset(ineligible_ids)
    # PMEGP (5, 6) non-farm only -> Ineligible
    assert 5 in ineligible_ids
    assert 6 in ineligible_ids


def test_artisan_sector_and_vishwakarma_matching(client: TestClient):
    """Test 5: An artisan/traditional-craft business can match PM Vishwakarma through ART."""
    profile_artisan = {
        "age": 35,
        "is_rural": False,
        "sector": "Artisans and Traditional Crafts",
        "is_traditional_artisan": True,
        "project_cost": 100000,
        "requested_loan_amount": 100000,
        "annual_income": 200000,
    }
    resp_artisan = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_artisan)
    assert resp_artisan.status_code == status.HTTP_200_OK
    data_artisan = resp_artisan.json()
    eligible_ids = {s["scheme_id"] for s in data_artisan["eligible_schemes"]}
    assert 7 in eligible_ids  # PM Vishwakarma

    # Manufacturing sector without artisan trade is rejected
    profile_mfg = {
        "age": 35,
        "is_rural": False,
        "sector": "Manufacturing",
        "is_traditional_artisan": False,
        "project_cost": 100000,
        "requested_loan_amount": 100000,
        "annual_income": 200000,
    }
    resp_mfg = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_mfg)
    assert resp_mfg.status_code == status.HTTP_200_OK
    data_mfg = resp_mfg.json()
    ineligible_ids = {s["scheme_id"] for s in data_mfg["ineligible_schemes"]}
    assert 7 in ineligible_ids  # PM Vishwakarma rejected


def test_sc_applicant_qualifies_for_nsfdc_within_income_limit(client: TestClient):
    """Test 6: An SC applicant can match NSFDC schemes when income is within the stated limit."""
    profile = {
        "age": 28,
        "social_category": "SC",
        "annual_income": 300000,  # Below 5 Lakh limit
        "sector": "Services",
        "project_cost": 100000,
        "requested_loan_amount": 80000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    eligible_ids = {s["scheme_id"] for s in data["eligible_schemes"]}
    assert 9 in eligible_ids  # NSFDC MFS eligible

    # Exceeding income ceiling of 5 Lakh
    profile_high_income = dict(profile, annual_income=600000)
    resp_high = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_high_income)
    assert resp_high.status_code == status.HTTP_200_OK
    data_high = resp_high.json()
    ineligible_high = {s["scheme_id"] for s in data_high["ineligible_schemes"]}
    assert 9 in ineligible_high


def test_general_category_applicant_rejected_from_nsfdc(client: TestClient):
    """Test 7: A General-category applicant does NOT incorrectly qualify for NSFDC schemes."""
    profile = {
        "age": 28,
        "social_category": "General",
        "annual_income": 200000,
        "sector": "Services",
        "project_cost": 100000,
        "requested_loan_amount": 80000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}
    # All 4 NSFDC schemes (9, 10, 11, 12) reject General applicants
    assert {9, 10, 11, 12}.issubset(ineligible_ids)


def test_unspecified_social_category_rejected_from_nsfdc(client: TestClient):
    """Unspecified social category (None) must be rejected from SC-exclusive schemes."""
    profile = {
        "age": 28,
        "social_category": None,
        "annual_income": 200000,
        "sector": "Services",
        "project_cost": 100000,
        "requested_loan_amount": 80000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}
    assert {9, 10, 11, 12}.issubset(ineligible_ids)


def test_null_social_category_preserves_universal_schemes(client: TestClient):
    """Option A: NULL in social category fields indicates universal eligibility (MUDRA)."""
    for cat in ["General", "OBC", "SC", "ST", None]:
        profile = {
            "age": 28,
            "social_category": cat,
            "annual_income": 200000,
            "project_cost": 40000,
            "requested_loan_amount": 40000,
            "is_new_business": True,
        }
        response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        eligible_ids = {s["scheme_id"] for s in data["eligible_schemes"]}
        assert 1 in eligible_ids  # PM MUDRA Shishu remains universally open


def test_age_requirement_enforcement(client: TestClient):
    """Test 8: A user who does not meet an age requirement is correctly rejected."""
    profile_underage = {
        "age": 16,
        "sector": "Manufacturing",
        "project_cost": 500000,
        "requested_loan_amount": 400000,
        "annual_income": 200000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_underage)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}
    # PMEGP Mfg (5) has min_age 18 -> Ineligible
    assert 5 in ineligible_ids


def test_project_cost_ceiling_enforcement(client: TestClient):
    """Test 9: Project-cost ceilings are enforced accurately."""
    # ₹100,000 exceeds MUDRA Shishu limit (₹50,000) but qualifies for Kishore (up to ₹5,00,000)
    profile = {
        "age": 30,
        "sector": "Services",
        "project_cost": 100000,
        "requested_loan_amount": 100000,
        "annual_income": 200000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    eligible_ids = {s["scheme_id"] for s in data["eligible_schemes"]}
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}
    assert 1 in ineligible_ids  # Shishu ceiling exceeded
    assert 2 in eligible_ids    # Kishore eligible


def test_street_vendor_matches_pm_svanidhi(client: TestClient):
    """Test 10 & 11: Street vendor profile matches PM SVANidhi; non-vendor does NOT."""
    # Street vendor profile -> Eligible
    profile_vendor = {
        "age": 32,
        "is_rural": False,  # Urban
        "is_street_vendor": True,
        "project_cost": 20000,
        "requested_loan_amount": 15000,
        "annual_income": 120000,
    }
    resp_vendor = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_vendor)
    assert resp_vendor.status_code == status.HTTP_200_OK
    data_vendor = resp_vendor.json()
    eligible_ids = {s["scheme_id"] for s in data_vendor["eligible_schemes"]}
    assert 8 in eligible_ids  # PM SVANidhi

    # Non-street vendor profile -> Ineligible
    profile_non_vendor = dict(profile_vendor, is_street_vendor=False)
    resp_non = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_non_vendor)
    assert resp_non.status_code == status.HTTP_200_OK
    data_non = resp_non.json()
    ineligible_ids = {s["scheme_id"] for s in data_non["ineligible_schemes"]}
    assert 8 in ineligible_ids  # Rejected from PM SVANidhi


def test_mudra_tarun_plus_prior_repayment_requirement(client: TestClient):
    """Test 12: An applicant with prior MUDRA loan repayment satisfies Tarun Plus condition."""
    # Repaid prior Tarun loan -> Eligible
    profile_repaid = {
        "age": 35,
        "sector": "Manufacturing",
        "previous_tarun_repaid": True,
        "project_cost": 1500000,
        "requested_loan_amount": 1500000,
        "annual_income": 400000,
        "is_new_business": False,
    }
    resp_repaid = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_repaid)
    assert resp_repaid.status_code == status.HTTP_200_OK
    data_repaid = resp_repaid.json()
    eligible_ids = {s["scheme_id"] for s in data_repaid["eligible_schemes"]}
    assert 4 in eligible_ids  # PM MUDRA Tarun Plus

    # Not repaid prior Tarun loan -> Ineligible
    profile_not_repaid = dict(profile_repaid, previous_tarun_repaid=False)
    resp_not = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_not_repaid)
    assert resp_not.status_code == status.HTTP_200_OK
    data_not = resp_not.json()
    ineligible_ids = {s["scheme_id"] for s in data_not["ineligible_schemes"]}
    assert 4 in ineligible_ids


def test_rural_urban_location_eligibility_enforcement(client: TestClient):
    """Test 13: Rural applicant rejected from urban-only scheme (PM SVANidhi)."""
    # Rural street vendor -> Ineligible for PM SVANidhi (urban_only)
    profile_rural = {
        "age": 32,
        "is_rural": True,
        "is_street_vendor": True,
        "project_cost": 20000,
        "requested_loan_amount": 10000,
        "annual_income": 120000,
    }
    resp_rural = client.post("/api/v1/schemes/evaluate-eligibility", json=profile_rural)
    assert resp_rural.status_code == status.HTTP_200_OK
    data_rural = resp_rural.json()
    ineligible_ids = {s["scheme_id"] for s in data_rural["ineligible_schemes"]}
    assert 8 in ineligible_ids

    # Find the disqualifying reason
    svanidhi_result = next(s for s in data_rural["ineligible_schemes"] if s["scheme_id"] == 8)
    assert any("urban" in r.lower() for r in svanidhi_result["disqualifying_reasons"])


def test_unmapped_schemes_10_and_12_strict_handling(client: TestClient):
    """Verify Schemes 10 & 12 do not claim invented universal sector matches."""
    # Commercial manufacturing enterprise applying to Scheme 12 (Education Loan)
    profile = {
        "age": 30,
        "social_category": "SC",
        "sector": "Manufacturing",
        "annual_income": 200000,
        "project_cost": 500000,
        "requested_loan_amount": 400000,
    }
    response = client.post("/api/v1/schemes/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    ineligible_ids = {s["scheme_id"] for s in data["ineligible_schemes"]}
    # Scheme 12 is education loan -> commercial manufacturing is ineligible
    assert 12 in ineligible_ids


