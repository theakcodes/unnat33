from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    """User and Enterprise Profile used for deterministic eligibility evaluation."""
    model_config = ConfigDict(extra="ignore")

    # Demographic attributes
    age: Optional[int] = Field(None, ge=14, le=120, description="Applicant age in years")
    gender: Optional[str] = Field(None, description="Applicant gender: Male, Female, Other, Transgender")
    social_category: Optional[str] = Field(None, description="Social category: General, SC, ST, OBC, Minority")
    is_differently_abled: Optional[bool] = Field(None, description="Persons with Disabilities (PwD) status")
    is_ex_serviceman: Optional[bool] = Field(None, description="Ex-servicemen status")

    # Geographic attributes
    state: Optional[str] = Field(None, description="State of operation / residence (e.g., 'Rajasthan', 'Maharashtra')")
    district: Optional[str] = Field(None, description="District name")
    is_rural: Optional[bool] = Field(None, description="True if rural area, False if urban")

    # Economic & financial attributes
    annual_income: Optional[float] = Field(None, ge=0, description="Annual household or individual income in INR")
    project_cost: Optional[float] = Field(None, ge=0, description="Estimated total project or venture cost in INR")
    requested_loan_amount: Optional[float] = Field(None, ge=0, description="Desired loan/financing amount in INR")

    # Business attributes
    is_new_business: Optional[bool] = Field(None, description="True if new enterprise, False if existing")
    sector: Optional[str] = Field(None, description="Primary sector (e.g., Manufacturing, Services, Trading)")
    business_type: Optional[str] = Field(None, description="Specific trade or business description")
    
    # Scheme-specific flags
    previous_tarun_repaid: Optional[bool] = Field(None, description="Has previously repaid a MUDRA Tarun loan")
    is_traditional_artisan: Optional[bool] = Field(None, description="Engaged in recognized traditional handicraft/artisan trade")
    is_street_vendor: Optional[bool] = Field(None, description="Engaged in street vending or informal vending")


class EligibilityResult(BaseModel):
    """Evaluation result for an individual scheme against user profile."""
    model_config = ConfigDict(from_attributes=True)

    scheme_id: int
    scheme_name: str
    scheme_type: Optional[str] = None
    is_eligible: bool
    status: str = Field("Eligible", description="'Eligible', 'Ineligible', or 'Partially Verified'")
    reasons: List[str] = Field(default_factory=list, description="Rules satisfied by the user profile")
    disqualifying_reasons: List[str] = Field(default_factory=list, description="Rules violated by the user profile")
    application_url: Optional[str] = None
    benefit: Optional[str] = None


class EligibilityAssessmentResponse(BaseModel):
    """Complete rule-based eligibility assessment response."""
    total_evaluated: int
    total_eligible: int
    total_ineligible: int
    eligible_schemes: List[EligibilityResult]
    ineligible_schemes: List[EligibilityResult]


class FinancialConstraints(BaseModel):
    """Authoritative financial constraints and limits for a government programme."""
    model_config = ConfigDict(from_attributes=True)

    min_loan_amount: Optional[float] = None
    max_loan_amount: Optional[float] = None
    min_project_cost: Optional[float] = None
    max_project_cost: Optional[float] = None
    max_subsidy_amount: Optional[float] = None
    subsidy_percentage: Optional[float] = None
    max_guarantee_limit: Optional[float] = None
    guarantee_coverage_pct: Optional[float] = None
    interest_rate_min: Optional[float] = None
    interest_rate_max: Optional[float] = None


class ProgramEligibilityResult(BaseModel):
    """Deterministic statutory evaluation result for an individual government programme."""
    model_config = ConfigDict(from_attributes=True)

    program_id: int
    program_code: str
    program_name: str
    primary_type: str
    actionability_type: str
    is_eligible: bool
    status: str = Field(..., description="'Eligible', 'Ineligible', or 'Partially Verified'")
    reasons: List[str] = Field(default_factory=list, description="Rules satisfied by the user profile")
    disqualifying_reasons: List[str] = Field(default_factory=list, description="Rules violated by the user profile")
    unverified_criteria: List[str] = Field(default_factory=list, description="Statutory or operational criteria requiring external verification")
    financial_constraints: Optional[FinancialConstraints] = None
    official_portal_url: Optional[str] = None
    benefit_summary: Optional[str] = None


class ProgramEligibilityAssessmentResponse(BaseModel):
    """Complete deterministic statutory eligibility evaluation across all government programmes."""
    total_evaluated: int
    total_eligible: int
    total_ineligible: int
    total_partially_verified: int
    eligible_programs: List[ProgramEligibilityResult]
    ineligible_programs: List[ProgramEligibilityResult]
    partially_verified_programs: List[ProgramEligibilityResult]
    directly_recommendable_count: int
    component_recommendable_count: int
    platform_count: int
    framework_count: int

