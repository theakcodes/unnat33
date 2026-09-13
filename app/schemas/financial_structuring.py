"""
app/schemas/financial_structuring.py

Pydantic v2 schemas for deterministic financial structuring:
- FinancialStructuringRequest: Input financial and profile parameters
- CapitalStructureBreakdown: Equity, subsidy, and debt components
- DebtHealthIndicators: Income, surplus, affordable EMI cap, DTI
- RepaymentScenarioItem: 3-tier amortization repayment scenarios
- StatutoryFinancialBounds: Official constraints from PostgreSQL
- FinancialStructuringResponse: Complete frontend-ready financial structuring model
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class FinancialStructuringRequest(BaseModel):
    """Input payload for deterministic financial structuring."""
    model_config = ConfigDict(extra="ignore")

    program_id: Optional[int] = Field(None, description="Government programme database ID")
    program_code: Optional[str] = Field(None, description="Canonical programme code (e.g. 'PMEGP_NEW', 'STANDUP_INDIA')")

    project_cost: float = Field(..., gt=0, description="Total estimated project cost in INR")
    requested_loan_amount: Optional[float] = Field(None, gt=0, description="Desired debt financing amount in INR")

    # Repayment capacity inputs
    monthly_income: float = Field(..., gt=0, description="Verified personal or net business monthly surplus in INR")
    monthly_expenses: float = Field(0.0, ge=0, description="Monthly household or operational overhead in INR")
    existing_monthly_emi: float = Field(0.0, ge=0, description="Current monthly debt repayments across all loans in INR")

    # Demographic & operational parameters for conditional terms
    applicant_social_category: Optional[str] = Field(None, description="'General', 'SC', 'ST', 'OBC', 'Minority'")
    applicant_gender: Optional[str] = Field(None, description="'Male', 'Female', 'Other'")
    is_rural: Optional[bool] = Field(None, description="True if operating in a rural area")
    is_new_business: Optional[bool] = Field(True, description="True for greenfield, False for expansion")
    preferred_tenure_months: Optional[int] = Field(None, ge=6, le=240, description="Applicant preferred tenure in months")


class CapitalStructureBreakdown(BaseModel):
    """Component-level capital stack breakdown."""
    model_config = ConfigDict(from_attributes=True)

    project_cost: float = Field(..., description="Total project capital in INR")
    
    # Promoter Equity
    promoter_contribution_pct: Optional[float] = Field(None, description="Statutory or guideline promoter margin %")
    promoter_contribution_amount: Optional[float] = Field(None, description="Calculated promoter equity in INR")
    is_statutory_margin: bool = Field(False, description="True if margin percentage comes from authoritative programme rules")

    # Government Subsidy / Grant
    subsidy_pct: Optional[float] = Field(None, description="Statutory subsidy percentage")
    subsidy_amount: float = Field(0.0, description="Calculated subsidy amount in INR (subject to statutory caps)")
    is_conditional_subsidy: bool = Field(False, description="True if subsidy rate depends on unverified demographic/rural verification")
    subsidy_disbursement_type: Optional[str] = Field(None, description="Disbursement method (e.g., Back-Ended Reserve, Direct Grant)")

    # Debt Financing
    initial_bank_loan: Optional[float] = Field(None, description="Gross initial loan disbursed prior to subsidy lock-in adjustment in INR")
    net_effective_debt: Optional[float] = Field(None, description="Net remaining debt liability after subsidy adjustment in INR")

    # Credit Guarantee (Lender Risk Coverage ONLY)
    credit_guarantee_eligible: bool = Field(False, description="Whether loan is eligible for credit guarantee cover")
    guarantee_coverage_pct: Optional[float] = Field(None, description="Statutory default coverage ratio % to the lending bank")
    guaranteed_amount: Optional[float] = Field(None, description="Risk coverage extended to lender in INR")
    annual_guarantee_fee_pct: Optional[float] = Field(None, description="Annual guarantee fee % payable to trust")
    guarantee_nature: str = Field(
        "Lender risk mitigation; does NOT reduce entrepreneur repayment liability",
        description="Statutory clarity on guarantee semantics"
    )


class DebtHealthIndicators(BaseModel):
    """Applicant debt servicing capacity and DTI health."""
    model_config = ConfigDict(from_attributes=True)

    monthly_income: float = Field(..., description="Verified monthly disposable income in INR")
    existing_monthly_emi: float = Field(..., description="Prior monthly debt commitments in INR")
    uncommitted_surplus: float = Field(..., description="Remaining monthly cashflow before new loan in INR")
    affordable_emi_cap: float = Field(..., description="Maximum recommended safe monthly EMI in INR")
    existing_dti_pct: float = Field(..., description="Current Debt-to-Income ratio %")
    dti_health_category: str = Field(..., description="'HEALTHY', 'MODERATE', 'STRETCHED', or 'HIGH_RISK'")


class RepaymentScenarioItem(BaseModel):
    """Specific amortization repayment track."""
    model_config = ConfigDict(from_attributes=True)

    scenario_type: str = Field(..., description="'CONSERVATIVE', 'BALANCED', or 'EXTENDED'")
    tenure_months: int = Field(..., description="Amortization horizon in months")
    moratorium_months: int = Field(0, description="Grace / moratorium period in months")
    annual_interest_rate_pct: Optional[float] = Field(None, description="Annual interest rate % applied")
    is_market_linked: bool = Field(False, description="True if interest is determined by lending bank")
    is_benchmark_assumption: bool = Field(False, description="True if rate is an indicative modeling benchmark")
    rate_note: Optional[str] = Field(None, description="Explanatory context on interest rate determination")
    monthly_emi: Optional[float] = Field(None, description="Equated Monthly Installment in INR")
    total_interest_payable: Optional[float] = Field(None, description="Cumulative interest paid over full tenure in INR")
    total_repayment_amount: Optional[float] = Field(None, description="Total principal + interest paid in INR")
    projected_dti_pct: Optional[float] = Field(None, description="Total projected DTI % including this loan")
    is_affordable: bool = Field(..., description="True if EMI is within affordable cap and DTI <= 50%")
    is_recommended: bool = Field(False, description="True if this is the balanced baseline recommendation")
    affordability_notes: List[str] = Field(default_factory=list, description="Specific underwriting and cashflow observations")


class StatutoryFinancialBounds(BaseModel):
    """Official statutory boundaries extracted from PostgreSQL."""
    model_config = ConfigDict(from_attributes=True)

    min_loan_amount: Optional[float] = None
    max_loan_amount: Optional[float] = None
    min_project_cost: Optional[float] = None
    max_project_cost: Optional[float] = None
    max_subsidy_amount: Optional[float] = None
    interest_rate_min: Optional[float] = None
    interest_rate_max: Optional[float] = None
    tenure_years_max: Optional[float] = None
    moratorium_months: Optional[int] = None
    collateral_required: bool = False


class FinancialStructuringResponse(BaseModel):
    """Authoritative financial structuring assessment response."""
    model_config = ConfigDict(from_attributes=True)

    program_id: int = Field(..., description="Government programme database ID")
    program_code: str = Field(..., description="Canonical programme code")
    program_name: str = Field(..., description="Official government programme title")
    primary_type: str = Field(..., description="Primary assistance classification")
    actionability_type: str = Field(..., description="Actionability classification")
    is_financing_applicable: bool = Field(..., description="True if programme provides credit, debt, or capital subsidy")
    assistance_summary: str = Field(..., description="High-level financial or capability assistance description")
    
    capital_structure: Optional[CapitalStructureBreakdown] = Field(None, description="Component equity, grant, and debt stack")
    debt_health: DebtHealthIndicators = Field(..., description="Applicant repayment capacity and DTI indicators")
    loan_scenarios: List[RepaymentScenarioItem] = Field(default_factory=list, description="Amortization scenarios within statutory bounds")
    financial_constraints: StatutoryFinancialBounds = Field(..., description="Statutory programme parameters from PostgreSQL")
    
    warnings: List[str] = Field(default_factory=list, description="Statutory caveats, conditional qualifiers, and missing parameter notices")
    statutory_checklist: List[str] = Field(default_factory=list, description="Mandatory documentary requirements for financing")
    disclaimer: str = Field(
        default=(
            "ADVISORY STRUCTURING ONLY: Financial calculations are deterministic modeling estimates based on "
            "authoritative government programme guidelines and applicant inputs. They do NOT constitute a bank sanction "
            "letter, credit commitment, or statutory guarantee of government subsidy disbursement."
        ),
        description="Statutory advisory disclaimer"
    )
