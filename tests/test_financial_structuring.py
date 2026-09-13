"""
tests/test_financial_structuring.py

Comprehensive test suite for the Deterministic Financial Structuring Service:
1. Credit-only programme (Stand-Up India)
2. Subsidy programme with statutory cap (PMFME)
3. Credit guarantee programme (CGTMSE) - lender risk coverage invariant
4. Composite programme (PMEGP) - initial vs net debt distinction
5. Non-financial / capability programme (MSME ZED) - clean empty scenarios
6. Market-linked interest rate handling & explicit benchmark metadata
7. Fixed-rate statutory interest concession (NBCFDC New Swarnima)
8. Subsidy cap strict enforcement
9. Debt-to-Income (DTI) risk tier classifications (HEALTHY, MODERATE, STRETCHED, HIGH_RISK)
10. Dual-gate affordability evaluation
11. Missing promoter contribution handling (returns null + warning, NO 10% fallback)
12. Zero-interest amortization handling (P / n)
13. Boundary validation: Project cost exceeding statutory cap
14. Boundary validation: Debt exceeding statutory maximum loan limit
15. Full FastAPI TestClient integration (200 OK & 404 Not Found)
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.schemas.financial_structuring import (
    FinancialStructuringRequest,
    FinancialStructuringResponse,
)
from app.services.financial_structuring_service import (
    financial_structuring_service,
    PROTOTYPE_INDICATIVE_MARKET_INTEREST_RATE,
)


def test_credit_only_program(db_session: Session):
    """Verify financial structuring for a credit-only programme (Stand-Up India)."""
    req = FinancialStructuringRequest(
        program_code="STANDUP_INDIA",
        project_cost=5000000.0,
        monthly_income=150000.0,
        monthly_expenses=50000.0,
        existing_monthly_emi=10000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    assert resp.is_financing_applicable is True
    assert resp.capital_structure is not None
    assert resp.capital_structure.project_cost == 5000000.0
    # Stand-Up India has 15% promoter contribution in DB
    assert resp.capital_structure.promoter_contribution_pct == 15.0
    assert resp.capital_structure.promoter_contribution_amount == 750000.0
    assert resp.capital_structure.subsidy_amount == 0.0
    assert resp.capital_structure.net_effective_debt == 4250000.0
    assert len(resp.loan_scenarios) == 3
    # Interest rate in DB is None -> market-linked benchmark applied
    assert resp.loan_scenarios[0].is_market_linked is True
    assert resp.loan_scenarios[0].is_benchmark_assumption is True
    assert resp.loan_scenarios[0].rate_note is not None


def test_subsidy_program_with_cap(db_session: Session):
    """Verify capital subsidy calculation with statutory cap (PMFME: 35% capped at 10L)."""
    req = FinancialStructuringRequest(
        program_code="PMFME",
        project_cost=5000000.0,  # 35% of 50L = 17.5L -> capped at 10L
        monthly_income=120000.0,
        monthly_expenses=40000.0,
        existing_monthly_emi=15000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    assert resp.is_financing_applicable is True
    assert resp.capital_structure is not None
    # PMFME margin is 10% in DB
    assert resp.capital_structure.promoter_contribution_pct == 10.0
    assert resp.capital_structure.promoter_contribution_amount == 500000.0
    # Subsidy capped at 10 Lakhs
    assert resp.capital_structure.subsidy_amount == 1000000.0
    # Net debt = 50L - 5L - 10L = 35L
    assert resp.capital_structure.net_effective_debt == 3500000.0
    # Cap warning should be present
    assert any("subsidy cap enforced" in w.lower() for w in resp.warnings)


def test_credit_guarantee_coverage_not_subtracted_from_debt(db_session: Session):
    """Verify that credit guarantee is strictly lender risk coverage and NEVER subtracted from debt."""
    req = FinancialStructuringRequest(
        program_code="CGTMSE",
        project_cost=2000000.0,
        monthly_income=80000.0,
        monthly_expenses=30000.0,
        existing_monthly_emi=5000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    assert resp.is_financing_applicable is True
    assert resp.capital_structure is not None
    assert resp.capital_structure.credit_guarantee_eligible is True
    assert resp.capital_structure.guarantee_coverage_pct == 85.0
    assert resp.capital_structure.annual_guarantee_fee_pct == 0.37
    # Crucial Invariant: Debt is NOT reduced by guarantee coverage
    assert resp.capital_structure.net_effective_debt == 2000000.0
    assert "lender risk mitigation" in resp.capital_structure.guarantee_nature.lower()


def test_composite_program_initial_vs_net_debt(db_session: Session):
    """Verify composite programme (PMEGP_NEW) correctly reports initial vs net debt."""
    req = FinancialStructuringRequest(
        program_code="PMEGP_NEW",
        project_cost=1000000.0,
        monthly_income=60000.0,
        monthly_expenses=20000.0,
        existing_monthly_emi=5000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    assert resp.is_financing_applicable is True
    assert resp.capital_structure is not None
    # 15% baseline subsidy in DB = 1.5L
    assert resp.capital_structure.subsidy_amount == 150000.0
    # Initial bank loan disbursed (Project Cost - Promoter Contribution)
    assert resp.capital_structure.initial_bank_loan == 1000000.0
    # Net debt post-subsidy adjustment = 10L - 1.5L = 8.5L
    assert resp.capital_structure.net_effective_debt == 850000.0


def test_non_financial_program_clean_response(db_session: Session):
    """Verify that non-financial / capability programmes (MSME ZED) return clean empty scenarios."""
    req = FinancialStructuringRequest(
        program_code="MSME_ZED",
        project_cost=200000.0,
        monthly_income=50000.0,
        monthly_expenses=20000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    assert resp.is_financing_applicable is False
    assert resp.capital_structure is None
    assert resp.loan_scenarios == []
    assert any("non-repayable capability" in w.lower() for w in resp.warnings)


def test_fixed_rate_interest_concession(db_session: Session):
    """Verify that programmes with fixed interest rates (NBCFDC New Swarnima 5%) use the statutory rate."""
    req = FinancialStructuringRequest(
        program_code="NBCFDC_NEW_SWARNIMA",
        project_cost=200000.0,
        monthly_income=30000.0,
        monthly_expenses=12000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    assert resp.is_financing_applicable is True
    assert len(resp.loan_scenarios) == 3
    for s in resp.loan_scenarios:
        assert s.annual_interest_rate_pct == 5.0
        assert s.is_market_linked is False
        assert s.is_benchmark_assumption is False
        assert s.rate_note is None


def test_market_linked_interest_benchmark_metadata(db_session: Session):
    """Verify that market-linked programmes set explicit benchmark metadata."""
    req = FinancialStructuringRequest(
        program_code="STANDUP_INDIA",
        project_cost=2000000.0,
        monthly_income=100000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    for s in resp.loan_scenarios:
        assert s.is_market_linked is True
        assert s.is_benchmark_assumption is True
        assert "Indicative modeling rate only" in s.rate_note


def test_missing_promoter_contribution_returns_null(db_session: Session):
    """Verify that when promoter margin is missing in DB, it returns null with warning (no 10% default)."""
    # MUDRA Shishu has no promoter contribution in DB
    req = FinancialStructuringRequest(
        program_code="PM_MUDRA_SHISHU",
        project_cost=50000.0,
        monthly_income=25000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    assert resp.capital_structure is not None
    assert resp.capital_structure.promoter_contribution_pct is None
    assert resp.capital_structure.promoter_contribution_amount is None
    assert resp.capital_structure.is_statutory_margin is False
    assert any("promoter contribution requirement is not specified" in w.lower() for w in resp.warnings)


def test_dti_risk_tier_classifications(db_session: Session):
    """Verify DTI classifications: HEALTHY (<=35%), MODERATE (35-50%), STRETCHED (50-60%), HIGH_RISK (>60%)."""
    # 1. Healthy DTI (10%)
    dh_healthy = financial_structuring_service._calculate_debt_health(
        monthly_income=100000.0, monthly_expenses=30000.0, existing_monthly_emi=10000.0
    )
    assert dh_healthy.existing_dti_pct == 10.0
    assert dh_healthy.dti_health_category == "HEALTHY"

    # 2. Moderate DTI (40%)
    dh_moderate = financial_structuring_service._calculate_debt_health(
        monthly_income=100000.0, monthly_expenses=30000.0, existing_monthly_emi=40000.0
    )
    assert dh_moderate.existing_dti_pct == 40.0
    assert dh_moderate.dti_health_category == "MODERATE"

    # 3. Stretched DTI (55%)
    dh_stretched = financial_structuring_service._calculate_debt_health(
        monthly_income=100000.0, monthly_expenses=20000.0, existing_monthly_emi=55000.0
    )
    assert dh_stretched.existing_dti_pct == 55.0
    assert dh_stretched.dti_health_category == "STRETCHED"

    # 4. High Risk DTI (70%)
    dh_high = financial_structuring_service._calculate_debt_health(
        monthly_income=100000.0, monthly_expenses=10000.0, existing_monthly_emi=70000.0
    )
    assert dh_high.existing_dti_pct == 70.0
    assert dh_high.dti_health_category == "HIGH_RISK"


def test_affordability_dual_gate_evaluation(db_session: Session):
    """Verify affordability evaluates both EMI cap and projected DTI <= 50%."""
    req = FinancialStructuringRequest(
        program_code="STANDUP_INDIA",
        project_cost=8000000.0,  # High debt -> high EMI
        monthly_income=60000.0,
        monthly_expenses=25000.0,
        existing_monthly_emi=25000.0,  # Already 41.7% DTI
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)

    # All scenarios must be marked NOT affordable because DTI exceeds 50%
    for s in resp.loan_scenarios:
        assert s.is_affordable is False
        assert any("exceeds" in note.lower() for note in s.affordability_notes)


def test_zero_interest_amortization(db_session: Session):
    """Verify zero-interest amortization correctly executes linear principal division."""
    emi, interest, total = financial_structuring_service._calculate_amortization(
        principal=120000.0,
        annual_rate=0.0,
        tenure_months=12,
    )
    assert emi == 10000.0
    assert interest == 0.0
    assert total == 120000.0


def test_project_cost_exceeding_statutory_cap_warning(db_session: Session):
    """Verify that project cost exceeding programme statutory ceiling emits warning."""
    # PMEGP_NEW has max_project_cost = 5,000,000 in DB
    req = FinancialStructuringRequest(
        program_code="PMEGP_NEW",
        project_cost=7500000.0,
        monthly_income=100000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)
    assert any("exceeds programme maximum eligible project ceiling" in w.lower() for w in resp.warnings)


def test_debt_exceeding_statutory_max_loan_warning(db_session: Session):
    """Verify that loan amount exceeding programme statutory ceiling emits warning."""
    # PM_MUDRA_SHISHU has max_loan_amount = 50,000 in DB
    req = FinancialStructuringRequest(
        program_code="PM_MUDRA_SHISHU",
        project_cost=100000.0,
        requested_loan_amount=80000.0,
        monthly_income=30000.0,
    )
    resp = financial_structuring_service.calculate_structure(db=db_session, request=req)
    assert any("exceeds statutory loan ceiling" in w.lower() for w in resp.warnings)


def test_api_endpoint_success(client: TestClient):
    """Verify POST /api/v1/recommendations/financial-structuring returns 200 OK."""
    payload = {
        "program_code": "PMEGP_NEW",
        "project_cost": 1000000.0,
        "monthly_income": 60000.0,
        "monthly_expenses": 20000.0,
        "existing_monthly_emi": 5000.0,
        "applicant_social_category": "OBC",
        "applicant_gender": "Female",
        "is_rural": True,
    }
    response = client.post("/api/v1/recommendations/financial-structuring", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["program_code"] == "PMEGP_NEW"
    assert data["is_financing_applicable"] is True
    assert data["capital_structure"]["project_cost"] == 1000000.0
    assert data["capital_structure"]["subsidy_amount"] == 150000.0
    assert len(data["loan_scenarios"]) == 3
    assert "statutory_checklist" in data


def test_api_endpoint_not_found(client: TestClient):
    """Verify POST /api/v1/recommendations/financial-structuring returns 404 for unknown programme."""
    payload = {
        "program_code": "NON_EXISTENT_SCHEME_XYZ",
        "project_cost": 500000.0,
        "monthly_income": 40000.0,
    }
    response = client.post("/api/v1/recommendations/financial-structuring", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
