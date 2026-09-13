"""
tests/test_program_eligibility.py

Comprehensive test suite for Phase 2: Deterministic Statutory Eligibility Engine
for 60 Government Programmes.

Tests:
A. Full Coverage & Integrity (60 programs evaluated, no duplicates, legacy representation)
B. Demographic statutory criteria (Age, Gender, Social Category, Income)
C. Geographic criteria (Rural vs Urban exclusivity)
D. Sector matching (Canonical sectors: MFG, SRV, TRD, AGR, ART)
E. Financial constraints (Min/max loan, max project cost, max guarantee)
F. Actionability semantics (Direct, Component, Platform, Framework)
G. Partial verification (Statutory pass + operational/institutional unverified)
H. Structured financial constraints payload
I. Adapter unit tests
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.program_models import GovernmentProgram
from app.services.program_eligibility_adapter import (
    ProgramEligibilityAdapter,
    EvaluatableProgram,
)
from app.schemas.eligibility import UserProfile
from app.services.eligibility_service import eligibility_service


# ==============================================================================
# A. FULL COVERAGE & INTEGRITY TESTS
# ==============================================================================

def test_program_eligibility_evaluates_exactly_60_programs(client: TestClient, db_session: Session):
    """Verify that evaluate-eligibility evaluates all 60 government programmes dynamically from DB."""
    total_in_db = db_session.query(GovernmentProgram).count()
    assert total_in_db == 60, f"Expected 60 government programmes in DB, found {total_in_db}"

    profile = {
        "age": 30,
        "gender": "Male",
        "social_category": "General",
        "is_rural": False,
        "sector": "Manufacturing",
        "project_cost": 500000,
        "requested_loan_amount": 400000,
        "annual_income": 200000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_evaluated"] == 60
    assert data["total_evaluated"] == total_in_db


def test_no_duplicate_program_ids_in_response(client: TestClient):
    """Verify that every evaluated programme appears exactly once across the response lists."""
    profile = {
        "age": 28,
        "gender": "Female",
        "social_category": "OBC",
        "is_rural": True,
        "sector": "Services",
        "requested_loan_amount": 200000,
        "annual_income": 150000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    all_ids = []
    for category in ["eligible_programs", "ineligible_programs", "partially_verified_programs"]:
        for p in data[category]:
            all_ids.append(p["program_id"])

    assert len(all_ids) == 60
    assert len(set(all_ids)) == 60, "Duplicate program IDs found in eligibility evaluation response"


def test_every_program_appears_exactly_once(client: TestClient):
    """Verify that sum of partitioned lists strictly equals total_evaluated."""
    profile = {"age": 35, "gender": "Male", "sector": "Manufacturing"}
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_evaluated"] == (
        data["total_eligible"]
        + data["total_ineligible"]
        + data["total_partially_verified"]
    )
    assert len(data["eligible_programs"]) == data["total_eligible"]
    assert len(data["ineligible_programs"]) == data["total_ineligible"]
    assert len(data["partially_verified_programs"]) == data["total_partially_verified"]


def test_legacy_12_schemes_represented_in_programs_evaluation(client: TestClient):
    """Verify that all 12 legacy schemes are represented in the 60 programmes evaluation."""
    profile = {"age": 30, "gender": "Male", "sector": "Manufacturing"}
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    all_programs = (
        data["eligible_programs"]
        + data["ineligible_programs"]
        + data["partially_verified_programs"]
    )
    evaluated_ids = {p["program_id"] for p in all_programs}
    # Programmes 1 to 12 correspond to legacy schemes
    for legacy_id in range(1, 13):
        assert legacy_id in evaluated_ids, f"Legacy programme {legacy_id} missing from evaluation"


# ==============================================================================
# B. DEMOGRAPHICS TESTS
# ==============================================================================

def test_age_below_minimum_fails(client: TestClient):
    """Applicant under 18 must fail programmes requiring minimum age 18."""
    profile = {
        "age": 16,
        "gender": "Male",
        "social_category": "General",
        "sector": "Manufacturing",
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    # PMEGP (ID 5) has min_age 18
    assert "PMEGP_NEW" in ineligible_by_code
    pmegp = ineligible_by_code["PMEGP_NEW"]
    assert any("below statutory minimum requirement of 18" in r for r in pmegp["disqualifying_reasons"])

    # Stand-Up India (ID 13) has min_age 18
    assert "STANDUP_INDIA" in ineligible_by_code
    standup = ineligible_by_code["STANDUP_INDIA"]
    assert any("below statutory minimum requirement of 18" in r for r in standup["disqualifying_reasons"])


def test_age_above_maximum_fails(client: TestClient):
    """Applicant exceeding maximum ceiling (e.g. 55 for NBCFDC New Swarnima) must fail."""
    profile = {
        "age": 60,
        "gender": "Female",
        "social_category": "OBC",
        "annual_income": 200000,
        "sector": "Manufacturing",
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    # NBCFDC New Swarnima (ID 15) has max_age 55
    assert "NBCFDC_NEW_SWARNIMA" in ineligible_by_code
    swarnima = ineligible_by_code["NBCFDC_NEW_SWARNIMA"]
    assert any("exceeds statutory maximum ceiling of 55" in r for r in swarnima["disqualifying_reasons"])


def test_female_only_program_rejects_male_applicant(client: TestClient):
    """Programmes exclusively designated for women must reject male applicants."""
    profile = {
        "age": 28,
        "gender": "Male",
        "social_category": "OBC",
        "annual_income": 200000,
        "sector": "Manufacturing",
        "requested_loan_amount": 100000,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    # NBCFDC New Swarnima (ID 15) is female-only
    assert "NBCFDC_NEW_SWARNIMA" in ineligible_by_code
    reasons_15 = ineligible_by_code["NBCFDC_NEW_SWARNIMA"]["disqualifying_reasons"]
    assert any("exclusively designated for female beneficiaries" in r for r in reasons_15)

    # NSTFDC AMSY (ID 16) is female-only
    assert "NSTFDC_AMSY" in ineligible_by_code
    reasons_16 = ineligible_by_code["NSTFDC_AMSY"]["disqualifying_reasons"]
    assert any("exclusively designated for female beneficiaries" in r for r in reasons_16)

    # Mahila Coir Yojana (ID 43) is female-only
    assert "MAHILA_COIR_YOJANA" in ineligible_by_code
    reasons_43 = ineligible_by_code["MAHILA_COIR_YOJANA"]["disqualifying_reasons"]
    assert any("exclusively designated for female beneficiaries" in r for r in reasons_43)


def test_female_applicant_passes_female_only_program(client: TestClient):
    """Female applicant with matching category/income should not be rejected for gender."""
    profile = {
        "age": 28,
        "gender": "Female",
        "social_category": "OBC",
        "annual_income": 200000,
        "sector": "Manufacturing",
        "requested_loan_amount": 100000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    all_programs = (
        data["eligible_programs"]
        + data["ineligible_programs"]
        + data["partially_verified_programs"]
    )
    swarnima = next(p for p in all_programs if p["program_code"] == "NBCFDC_NEW_SWARNIMA")
    assert swarnima["is_eligible"] is True
    assert not any("female beneficiaries" in r for r in swarnima["disqualifying_reasons"])
    assert any("Exclusively for women entrepreneurs" in r for r in swarnima["reasons"])


def test_sc_st_exclusive_programs_reject_general_applicant(client: TestClient):
    """Programmes reserved for SC/ST beneficiaries must reject General applicants."""
    profile = {
        "age": 30,
        "gender": "Male",
        "social_category": "General",
        "sector": "Manufacturing",
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    # NSFDC programmes (9, 10, 11, 12) are SC-only
    for code in ["NSFDC_MFS", "NSFDC_AMY", "NSFDC_TERM_LOAN", "NSFDC_UNY"]:
        assert code in ineligible_by_code
        reasons = ineligible_by_code[code]["disqualifying_reasons"]
        assert any("exclusively designated for SC" in r for r in reasons)

    # SCLCSS (ID 23) and NSSH programmes (30, 35, 57, 58) are SC/ST
    for code in ["SCLCSS_SC_ST", "NSSH_SMAS", "NSSH_TESTING_REIMB", "NSSH_SPRS_SUBSIDY", "NSSH_BANK_FEE_REIMB"]:
        assert code in ineligible_by_code
        reasons = ineligible_by_code[code]["disqualifying_reasons"]
        assert any("exclusively designated for SC/ST" in r for r in reasons)


def test_reserved_category_passes_structured_rules(client: TestClient):
    """SC applicant passes SC-reserved schemes, ST passes ST-reserved schemes."""
    # SC applicant
    profile_sc = {
        "age": 30,
        "gender": "Male",
        "social_category": "SC",
        "annual_income": 300000,
        "sector": "Manufacturing",
        "requested_loan_amount": 100000,
        "is_new_business": True,
    }
    res_sc = client.post("/api/v1/programs/evaluate-eligibility", json=profile_sc)
    data_sc = res_sc.json()
    all_sc = data_sc["eligible_programs"] + data_sc["partially_verified_programs"]
    sc_codes = {p["program_code"] for p in all_sc}
    assert "NSFDC_MFS" in sc_codes

    # ST applicant
    profile_st = {
        "age": 30,
        "gender": "Female",
        "social_category": "ST",
        "annual_income": 200000,
        "sector": "Manufacturing",
        "requested_loan_amount": 100000,
        "is_new_business": True,
    }
    res_st = client.post("/api/v1/programs/evaluate-eligibility", json=profile_st)
    data_st = res_st.json()
    all_st = data_st["eligible_programs"] + data_st["partially_verified_programs"]
    st_codes = {p["program_code"] for p in all_st}
    assert "NSTFDC_AMSY" in st_codes


def test_income_above_ceiling_fails(client: TestClient):
    """Annual income exceeding statutory ceiling must fail."""
    # NSFDC has 500,000 ceiling, NBCFDC has 300,000 ceiling
    profile = {
        "age": 30,
        "gender": "Female",
        "social_category": "OBC",
        "annual_income": 400000,  # Exceeds NBCFDC 300,000
        "sector": "Manufacturing",
        "requested_loan_amount": 100000,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    assert "NBCFDC_NEW_SWARNIMA" in ineligible_by_code
    reasons = ineligible_by_code["NBCFDC_NEW_SWARNIMA"]["disqualifying_reasons"]
    assert any("exceeds programme ceiling" in r and "300,000" in r for r in reasons)



# ==============================================================================
# C. GEOGRAPHY TESTS
# ==============================================================================

def test_rural_only_program_rejects_urban_profile(client: TestClient):
    """Urban profile must be rejected by programmes reserved exclusively for rural locations."""
    # AMI_STORAGE (ID 24) is rural-only
    profile = {
        "age": 30,
        "gender": "Male",
        "is_rural": False,  # Urban applicant
        "sector": "Agriculture and Allied Activities",
        "project_cost": 1000000,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    assert "AMI_STORAGE" in ineligible_by_code
    reasons = ineligible_by_code["AMI_STORAGE"]["disqualifying_reasons"]
    assert any("exclusively reserved for rural enterprise locations" in r for r in reasons)


def test_urban_only_program_rejects_rural_profile(client: TestClient):
    """Rural profile must be rejected by programmes designated exclusively for urban locations."""
    # PM_SVANIDHI (ID 8) is urban-only
    profile = {
        "age": 30,
        "gender": "Male",
        "is_rural": True,  # Rural applicant
        "sector": "Services",
        "is_street_vendor": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    assert "PM_SVANIDHI" in ineligible_by_code
    reasons = ineligible_by_code["PM_SVANIDHI"]["disqualifying_reasons"]
    assert any("designated exclusively for urban locations" in r for r in reasons)


# ==============================================================================
# D. SECTOR TESTS
# ==============================================================================

def test_manufacturing_sector_matches_mfg_programs(client: TestClient):
    """Manufacturing profile matches MFG programmes and rejects AGR-only programmes."""
    profile = {
        "age": 30,
        "gender": "Male",
        "sector": "Manufacturing",
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    all_programs = (
        data["eligible_programs"]
        + data["ineligible_programs"]
        + data["partially_verified_programs"]
    )
    by_code = {p["program_code"]: p for p in all_programs}

    # PMFME (ID 20) is MFG
    pmfme = by_code["PMFME"]
    assert any("matches eligible canonical sector 'Manufacturing' (MFG)" in r for r in pmfme["reasons"])

    # AIF (ID 22) is AGR only -> must be ineligible for MFG applicant
    aif = by_code["AIF"]
    assert aif["is_eligible"] is False
    assert any("is not eligible for this programme (eligible sectors: Agriculture and Allied Activities)" in r for r in aif["disqualifying_reasons"])


def test_agriculture_sector_matches_agr_programs(client: TestClient):
    """Agriculture profile matches AGR programmes (AIF, AMI Storage)."""
    profile = {
        "age": 30,
        "gender": "Male",
        "is_rural": True,
        "sector": "Agriculture and Allied Activities",
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    all_programs = (
        data["eligible_programs"]
        + data["ineligible_programs"]
        + data["partially_verified_programs"]
    )
    by_code = {p["program_code"]: p for p in all_programs}

    aif = by_code["AIF"]
    assert any("matches eligible canonical sector 'Agriculture and Allied Activities' (AGR)" in r for r in aif["reasons"])


def test_artisan_sector_matches_art_programs(client: TestClient):
    """Artisan profile matches ART programmes (PM Vishwakarma)."""
    profile = {
        "age": 30,
        "gender": "Male",
        "sector": "Artisans and Traditional Crafts",
        "is_traditional_artisan": True,
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    all_programs = (
        data["eligible_programs"]
        + data["ineligible_programs"]
        + data["partially_verified_programs"]
    )
    by_code = {p["program_code"]: p for p in all_programs}

    vishwakarma = by_code["PM_VISHWAKARMA"]
    assert any("matches eligible canonical sector 'Artisans and Traditional Crafts' (ART)" in r for r in vishwakarma["reasons"])


def test_unknown_sector_handled_deterministically(client: TestClient):
    """Unrecognized sector rejects deterministically without guessing."""
    profile = {
        "age": 30,
        "sector": "Unrecognized Novel Industry",
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    # Every programme with sector checking should disqualify the applicant
    ineligible = data["ineligible_programs"]
    assert len(ineligible) > 50
    for p in ineligible:
        assert any("not a recognized eligible sector" in r for r in p["disqualifying_reasons"])


# ==============================================================================
# E. FINANCIAL CONSTRAINTS TESTS
# ==============================================================================

def test_requested_loan_above_max_fails(client: TestClient):
    """Requested loan exceeding max_loan_amount fails credit programmes."""
    # Stand-Up India (ID 13) max loan is 10,000,000 (1 Crore)
    profile = {
        "age": 30,
        "gender": "Male",
        "sector": "Manufacturing",
        "requested_loan_amount": 25000000,  # 2.5 Crore
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    assert "STANDUP_INDIA" in ineligible_by_code
    reasons = ineligible_by_code["STANDUP_INDIA"]["disqualifying_reasons"]
    assert any("exceeds maximum loan amount" in r and "10,000,000" in r for r in reasons)


def test_requested_loan_below_min_fails(client: TestClient):
    """Requested loan below min_loan_amount fails credit programmes."""
    # Stand-Up India (ID 13) min loan is 1,000,000 (10 Lakh)
    profile = {
        "age": 30,
        "gender": "Male",
        "sector": "Manufacturing",
        "requested_loan_amount": 500000,  # 5 Lakh
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    assert "STANDUP_INDIA" in ineligible_by_code
    reasons = ineligible_by_code["STANDUP_INDIA"]["disqualifying_reasons"]
    assert any("is below minimum loan amount" in r and "1,000,000" in r for r in reasons)


def test_project_cost_above_max_fails(client: TestClient):
    """Project cost exceeding subsidy ceiling fails."""
    # AIF (ID 22) max project cost is 20,000,000 (2 Crore)
    profile = {
        "age": 30,
        "gender": "Male",
        "sector": "Agriculture and Allied Activities",
        "project_cost": 30000000,  # 3 Crore
        "is_rural": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    assert "AIF" in ineligible_by_code
    reasons = ineligible_by_code["AIF"]["disqualifying_reasons"]
    assert any("exceeds programme ceiling" in r and "20,000,000" in r for r in reasons)


def test_guarantee_amount_above_max_fails(client: TestClient):
    """Requested loan exceeding guarantee ceiling fails guarantee programmes."""
    # CGSSD (ID 18) max credit limit is 7,500,000 (75 Lakh)
    profile = {
        "age": 30,
        "gender": "Male",
        "sector": "Manufacturing",
        "requested_loan_amount": 10000000,  # 1 Crore
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()
    ineligible_by_code = {p["program_code"]: p for p in data["ineligible_programs"]}

    assert "CGSSD" in ineligible_by_code
    reasons = ineligible_by_code["CGSSD"]["disqualifying_reasons"]
    assert any("exceeds guarantee ceiling" in r and "7,500,000" in r for r in reasons)



# ==============================================================================
# F. ACTIONABILITY TESTS
# ==============================================================================

def test_actionability_counts_exact_aggregation(client: TestClient):
    """Verify that actionability counts aggregate across all evaluated programmes and sum to 60."""
    profile = {"age": 30, "gender": "Male", "sector": "Manufacturing"}
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["directly_recommendable_count"] == 28
    assert data["component_recommendable_count"] == 27
    assert data["platform_count"] == 2
    assert data["framework_count"] == 3

    total_actionability = (
        data["directly_recommendable_count"]
        + data["component_recommendable_count"]
        + data["platform_count"]
        + data["framework_count"]
    )
    assert total_actionability == 60


def test_platform_and_framework_actionability_types(client: TestClient):
    """Verify platforms and frameworks preserve their specific actionability_type."""
    profile = {"age": 30, "gender": "Male", "sector": "Manufacturing"}
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    all_programs = (
        data["eligible_programs"]
        + data["ineligible_programs"]
        + data["partially_verified_programs"]
    )
    by_code = {p["program_code"]: p for p in all_programs}

    # Platforms
    assert by_code["GEM_MSME"]["actionability_type"] == "PLATFORM"
    assert by_code["MSME_SAMBANDH"]["actionability_type"] == "PLATFORM"

    # Frameworks
    assert by_code["CGTMSE"]["actionability_type"] == "FRAMEWORK"
    assert by_code["MSME_SAMADHAAN"]["actionability_type"] == "FRAMEWORK"
    assert by_code["TREDS_FACTORING"]["actionability_type"] == "FRAMEWORK"


# ==============================================================================
# G. PARTIAL VERIFICATION TESTS
# ==============================================================================

def test_partial_verification_when_operational_criteria_unverified(client: TestClient):
    """When statutory criteria pass but institutional requirements (e.g. Udyam) exist, status is Partially Verified."""
    profile = {
        "age": 30,
        "gender": "Male",
        "social_category": "General",
        "sector": "Manufacturing",
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    partially_verified = {p["program_code"]: p for p in data["partially_verified_programs"]}

    # MSME ZED (ID 31) has statutory pass + requires Udyam
    assert "MSME_ZED" in partially_verified
    zed = partially_verified["MSME_ZED"]
    assert zed["is_eligible"] is True
    assert zed["status"] == "Partially Verified"
    assert any("Valid Udyam Registration required" in u for u in zed["unverified_criteria"])


def test_partial_verification_when_startup_recognition_unverified(client: TestClient):
    """CGSS requires DPIIT startup recognition which cannot be determined from basic profile."""
    profile = {
        "age": 30,
        "gender": "Male",
        "sector": "Manufacturing",
        "requested_loan_amount": 5000000,
        "is_new_business": True,
    }
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    partially_verified = {p["program_code"]: p for p in data["partially_verified_programs"]}

    assert "CGSS" in partially_verified
    cgss = partially_verified["CGSS"]
    assert cgss["is_eligible"] is True
    assert cgss["status"] == "Partially Verified"
    assert any("DPIIT startup recognition required" in u for u in cgss["unverified_criteria"])


# ==============================================================================
# H. FINANCIAL CONSTRAINTS PAYLOAD TESTS
# ==============================================================================

def test_financial_constraints_populated_in_program_result(client: TestClient):
    """Verify that structured financial limits are returned in program results."""
    profile = {"age": 30, "gender": "Male", "sector": "Manufacturing"}
    response = client.post("/api/v1/programs/evaluate-eligibility", json=profile)
    data = response.json()

    all_programs = (
        data["eligible_programs"]
        + data["ineligible_programs"]
        + data["partially_verified_programs"]
    )
    by_code = {p["program_code"]: p for p in all_programs}

    # Stand-Up India
    standup = by_code["STANDUP_INDIA"]
    fc_standup = standup["financial_constraints"]
    assert fc_standup is not None
    assert fc_standup["min_loan_amount"] == 1000000.0
    assert fc_standup["max_loan_amount"] == 10000000.0

    # CGTMSE
    cgtmse = by_code["CGTMSE"]
    fc_cgtmse = cgtmse["financial_constraints"]
    assert fc_cgtmse is not None
    assert fc_cgtmse["max_guarantee_limit"] == 100000000.0

    # AIF
    aif = by_code["AIF"]
    fc_aif = aif["financial_constraints"]
    assert fc_aif is not None
    assert fc_aif["max_project_cost"] == 20000000.0


# ==============================================================================
# I. ADAPTER UNIT TESTS
# ==============================================================================

def test_adapter_handles_both_legacy_and_new_programs(db_session: Session):
    """Test ProgramEligibilityAdapter directly on legacy and new programme records."""
    from app.repositories.program_repository import program_repository

    # Legacy-linked programme: ID 1 (PM MUDRA Shishu)
    p1 = program_repository.get_by_id(db_session, 1)
    assert p1 is not None
    assert p1.legacy_scheme_id is not None
    ep1 = ProgramEligibilityAdapter.adapt(p1)
    assert ep1.program_code == "PM_MUDRA_SHISHU"
    assert "MFG" in ep1.sector_codes
    assert "TRD" in ep1.sector_codes
    assert "SRV" in ep1.sector_codes

    # New programme: ID 13 (Stand-Up India)
    p13 = program_repository.get_by_id(db_session, 13)
    assert p13 is not None
    assert p13.legacy_scheme_id is None
    ep13 = ProgramEligibilityAdapter.adapt(p13)
    assert ep13.program_code == "STANDUP_INDIA"
    assert ep13.min_loan_amount == 1000000.0
    assert ep13.max_loan_amount == 10000000.0
    assert ep13.min_age == 18
