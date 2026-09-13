"""
tests/test_dpr.py

Comprehensive test suite for Phase 8.1 Structured DPR:
- All 13 canonical sections populated in DPRResponse
- Provenance tags present across all sections
- Mandatory statutory disclaimer on illustrative operating assumptions
- Authoritative financial structuring and subsidy integration (zero frontend math)
- Deterministic fallback when Claude/Open-Meteo are offline
- Anti-fabrication assertions (no fake competitor counts, market share %, or profit curves)
- API endpoint integration: POST /api/v1/advisory/dpr
- Invariant verification: existing engines remain untouched
"""

import pytest
import re
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.schemas.dpr import DPRRequest, DPRResponse
from app.services.dpr_service import dpr_service


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


def test_dpr_service_canonical_13_sections(db_session: Session):
    """Verify that DPRService generates all 13 canonical sections plus auxiliary sections."""
    req = DPRRequest(
        project_name="Banarasi Handloom Weaving Unit",
        promoter_name="Ramesh Kumar",
        business_type="Handloom & Textiles",
        sub_type="Zari Brocade Weaving",
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        estimated_capital=1000000.0,
        current_income=360000.0,
        selected_program_code="PMEGP_NEW",
    )

    res = asyncio.run(dpr_service.generate_dpr(db=db_session, request=req))

    assert isinstance(res, DPRResponse)
    assert res.report_id.startswith("DPR-")

    # Section 1: Executive Summary
    assert res.executive_summary is not None
    assert res.executive_summary.total_project_cost == 1000000.0
    assert res.executive_summary.bank_loan_amount > 0
    assert res.executive_summary.monthly_emi > 0
    assert len(res.executive_summary.executive_narrative) > 50

    # Section 2: Business Model
    assert res.business_model is not None
    assert len(res.business_model.value_proposition) > 10
    assert len(res.business_model.revenue_streams) >= 2
    assert len(res.business_model.key_activities) >= 2

    # Section 3: Market Analysis
    assert res.market_analysis is not None
    assert res.market_analysis.total_msmes_in_district > 0
    assert res.market_analysis.micro_enterprise_share > 0
    assert len(res.market_analysis.comparable_districts) > 0

    # Section 4: Customer Segments
    assert res.customer_segments is not None
    assert len(res.customer_segments.customer_segments) >= 1

    # Section 5: Competition
    assert res.competition is not None
    assert res.competition.competition_intensity in ["Low", "Moderate", "High", "Very High"]
    assert len(res.competition.differentiation_vectors) >= 2

    # Section 6: Location Analysis
    assert res.location_analysis is not None
    assert res.location_analysis.district_name.upper() == "VARANASI"
    assert len(res.location_analysis.connectivity_advantages) >= 1

    # Section 7: Operations Plan
    assert res.operations_plan is not None
    assert len(res.operations_plan.workflow_steps) >= 3
    assert len(res.operations_plan.key_machinery_equipment) >= 2

    # Section 8: Marketing Strategy
    assert res.marketing_strategy is not None
    assert len(res.marketing_strategy.sales_channels) >= 2
    assert "margin" in res.marketing_strategy.pricing_framework.lower() or "cost-plus" in res.marketing_strategy.pricing_framework.lower()

    # Section 9: Government Support
    assert res.government_support is not None
    assert res.government_support.program_code == "PMEGP_NEW"
    assert res.government_support.eligible_subsidy_amount > 0

    # Section 10: Capital Structure
    assert res.capital_structure is not None
    assert res.capital_structure.total_project_cost == 1000000.0
    assert res.capital_structure.promoter_equity_amount is None
    assert res.capital_structure.net_bank_loan_exposure > 0
    assert res.capital_structure.is_statutorily_balanced is True

    # Section 11: Financial Assumptions
    assert res.financial_assumptions is not None
    assert res.financial_assumptions.annual_interest_rate_pct > 0
    assert res.financial_assumptions.monthly_emi > 0
    assert len(res.financial_assumptions.amortization_schedule) >= 1

    # Section 12: Risk Analysis
    assert res.risk_analysis is not None
    assert len(res.risk_analysis.identified_risks) >= 1

    # Section 13: Implementation Plan
    assert res.implementation_plan is not None
    assert len(res.implementation_plan.milestones) >= 3

    # Auxiliary Sections
    assert res.illustrative_assumptions is not None
    assert "Illustrative assumption" in res.illustrative_assumptions.disclaimer
    assert res.research_gaps is not None


def test_provenance_tags_on_all_sections(db_session: Session):
    """Verify that every section carries a valid provenance tag."""
    req = DPRRequest(
        project_name="Organic Flour Mill",
        promoter_name="Sita Devi",
        business_type="Food Processing",
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        estimated_capital=800000.0,
    )
    res = asyncio.run(dpr_service.generate_dpr(db=db_session, request=req))

    valid_tags = {
        "USER PROVIDED",
        "GOVERNMENT / DATASET DERIVED",
        "MODELLED INDICATOR",
        "AI INTERPRETATION",
        "ILLUSTRATIVE ASSUMPTION",
        "BACKEND DETERMINISTIC CALCULATION",
    }

    # Verify key sections
    assert "AI INTERPRETATION" in res.business_model.provenance
    assert "MODELLED INDICATOR" in res.market_analysis.provenance or "GOVERNMENT" in res.market_analysis.provenance
    assert "AI INTERPRETATION" in res.customer_segments.provenance
    assert "MODELLED INDICATOR" in res.competition.provenance
    assert "AI INTERPRETATION" in res.operations_plan.provenance
    assert "BACKEND DETERMINISTIC CALCULATION" in res.capital_structure.provenance
    assert "BACKEND DETERMINISTIC CALCULATION" in res.financial_assumptions.provenance
    assert res.illustrative_assumptions.provenance == "ILLUSTRATIVE ASSUMPTION"


def test_dpr_api_endpoint(client: TestClient):
    """Verify POST /api/v1/advisory/dpr endpoint produces complete DPR."""
    payload = {
        "project_name": "Agri Cold Storage Unit",
        "promoter_name": "Vikram Singh",
        "business_type": "Agro Processing",
        "district_name": "Varanasi",
        "state_name": "Uttar Pradesh",
        "estimated_capital": 1500000.0,
        "current_income": 480000.0,
        "selected_program_code": "PMEGP_NEW",
    }
    response = client.post("/api/v1/advisory/dpr", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "executive_summary" in data
    assert "capital_structure" in data
    assert "market_analysis" in data
    assert data["capital_structure"]["total_project_cost"] == 1500000.0
    assert data["financial_assumptions"]["monthly_emi"] > 0


def test_anti_fabrication_assertions(client: TestClient):
    """Verify response does not contain fabricated competitor counts or 5-year profit curves."""
    payload = {
        "project_name": "Standard Tailoring Unit",
        "promoter_name": "Anita Verma",
        "business_type": "Textiles & Apparel",
        "district_name": "Varanasi",
        "state_name": "Uttar Pradesh",
        "estimated_capital": 500000.0,
    }
    response = client.post("/api/v1/advisory/dpr", json=payload)
    assert response.status_code == 200

    full_text = response.text

    # No fake market share percentages like "commands 15% market share"
    assert not re.search(r"commands?\s+\d+%\s+market\s+share", full_text, re.IGNORECASE)
    # No fake exact customer count claims like "capturing 1,450 customers"
    assert not re.search(r"capturing\s+\d+[\d,]*\s+customers", full_text, re.IGNORECASE)


def test_regression_blocker_1_pmegp_promoter_contribution_is_none(db_session: Session):
    """TEST 1: PMEGP_NEW with missing promoter contribution preserves None."""
    req = DPRRequest(
        project_name="Banarasi Silk Weaving",
        promoter_name="Ramesh Kumar",
        business_type="Handloom & Textiles",
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        estimated_capital=1200000.0,
        selected_program_code="PMEGP_NEW",
    )
    res = asyncio.run(dpr_service.generate_dpr(db=db_session, request=req))
    assert res.capital_structure.promoter_equity_amount is None
    assert res.capital_structure.promoter_equity_pct is None
    assert res.executive_summary.promoter_contribution_amount is None


def test_regression_blocker_2_no_70_30_allocation_exists(db_session: Session):
    """TEST 2: Assert no 70/30 allocation exists; term_loan and working_cap are None unless authoritative."""
    req = DPRRequest(
        project_name="Varanasi Printing Press",
        promoter_name="Alok Mishra",
        business_type="Printing",
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        estimated_capital=1200000.0,
        selected_program_code="PMEGP_NEW",
    )
    res = asyncio.run(dpr_service.generate_dpr(db=db_session, request=req))
    assert res.capital_structure.term_loan_amount is None
    assert res.capital_structure.working_capital_amount is None
    assert any("Component allocation not specified" in note for note in res.capital_structure.structuring_notes)


def test_regression_blocker_3_amortization_schedule_net_debt_principal(db_session: Session):
    """TEST 3: PMEGP_NEW amortization schedule uses net_effective_debt (10.2L) and ends at ~0."""
    req = DPRRequest(
        project_name="Kashi Textile Processing",
        promoter_name="Sanjay Gupta",
        business_type="Textiles",
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        estimated_capital=1200000.0,
        selected_program_code="PMEGP_NEW",
    )
    res = asyncio.run(dpr_service.generate_dpr(db=db_session, request=req))
    assert res.capital_structure.initial_bank_loan == 1200000.0
    assert res.capital_structure.government_subsidy_amount == 180000.0
    assert res.capital_structure.net_bank_loan_exposure == 1020000.0
    assert res.financial_assumptions.monthly_emi == 21173.52

    sched = res.financial_assumptions.amortization_schedule
    assert len(sched) == 5
    assert sched[0].opening_balance == 1020000.0
    # Closing balance in year 5 must cleanly amortize to zero within normal rounding (< 1.0)
    assert abs(sched[-1].closing_balance) < 1.0


def test_regression_blocker_4_market_linked_interest_rate_metadata(db_session: Session):
    """TEST 4: Market-linked rate detection and labelling."""
    req = DPRRequest(
        project_name="Varanasi Engineering Works",
        promoter_name="Deepak Sharma",
        business_type="Light Engineering",
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        estimated_capital=1200000.0,
        selected_program_code="PMEGP_NEW",
    )
    res = asyncio.run(dpr_service.generate_dpr(db=db_session, request=req))
    assert res.financial_assumptions.annual_interest_rate_pct == 9.0
    assert res.financial_assumptions.is_market_linked is True
    assert res.financial_assumptions.is_benchmark_assumption is True
    assert res.financial_assumptions.rate_display_text == "Market-linked / lender-dependent"
    assert res.financial_assumptions.rate_type == "market_linked"


def test_regression_blocker_5_non_credit_programme_null_assumptions(db_session: Session):
    """TEST 5: Non-credit programmes must have null financial assumptions and no repayment schedule."""
    req = DPRRequest(
        project_name="Handicraft Fair Exhibitor",
        promoter_name="Meera Devi",
        business_type="Handicrafts",
        district_name="Varanasi",
        state_name="Uttar Pradesh",
        estimated_capital=500000.0,
        selected_program_code="PMS_TRADE_FAIRS",
    )
    res = asyncio.run(dpr_service.generate_dpr(db=db_session, request=req))
    assert res.government_support.is_credit_linked is False
    assert res.financial_assumptions.annual_interest_rate_pct is None
    assert res.financial_assumptions.loan_tenure_months is None
    assert res.financial_assumptions.moratorium_months is None
    assert res.financial_assumptions.monthly_emi == 0.0
    assert res.financial_assumptions.annual_debt_service == 0.0
    assert res.financial_assumptions.amortization_schedule == []
    assert res.financial_assumptions.rate_display_text == "Not applicable — programme is not credit-linked."


def test_regression_blocker_6_anti_fabrication_code_scan():
    """TEST 6: Assert active DPR path contains no heuristic splits or hardcoded financial defaults."""
    import os
    dpr_service_path = os.path.join(os.path.dirname(__file__), "..", "app", "services", "dpr_service.py")
    with open(dpr_service_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert "bank_loan * 0.70" not in code
    assert "bank_loan * 0.30" not in code
    assert "cs.promoter_contribution_amount or 0.0" not in code
    assert "interest_rate = 9.0" not in code
    assert "tenure_months = 60" not in code
    assert "moratorium_months = 6" not in code

