from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ProgramSectorResponse(BaseModel):
    """Sector mapping representation for government programmes."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Sector primary key")
    sector_code: Optional[str] = Field(None, description="Standard sector code (e.g. MFG, SRV, AGR)")
    sector_name: str = Field(..., description="Canonical sector name")


class ProgramEligibilityResponse(BaseModel):
    """Eligibility criteria representation for government programmes."""
    model_config = ConfigDict(from_attributes=True)

    rural_eligible: Optional[bool] = Field(None, description="Eligible for rural enterprises")
    urban_eligible: Optional[bool] = Field(None, description="Eligible for urban enterprises")
    male_eligible: Optional[bool] = Field(None, description="Eligible for male applicants")
    female_eligible: Optional[bool] = Field(None, description="Eligible for female applicants")
    other_gender_eligible: Optional[bool] = Field(None, description="Eligible for other genders")
    general_eligible: Optional[bool] = Field(None, description="Eligible for general category")
    sc_eligible: Optional[bool] = Field(None, description="Eligible for SC category")
    st_eligible: Optional[bool] = Field(None, description="Eligible for ST category")
    obc_eligible: Optional[bool] = Field(None, description="Eligible for OBC category")
    minority_eligible: Optional[bool] = Field(None, description="Eligible for minority communities")
    pwd_eligible: Optional[bool] = Field(None, description="Eligible for persons with disabilities")
    ex_servicemen_eligible: Optional[bool] = Field(None, description="Eligible for ex-servicemen")
    min_age: Optional[int] = Field(None, description="Minimum age requirement")
    max_age: Optional[int] = Field(None, description="Maximum age limit")
    max_annual_income: Optional[float] = Field(None, description="Maximum annual family income ceiling")
    notes: Optional[str] = Field(None, description="Specific statutory eligibility notes")


class ProgramCreditDetailResponse(BaseModel):
    """Credit and financing terms for loan-type programmes."""
    model_config = ConfigDict(from_attributes=True)

    min_loan_amount: Optional[float] = Field(None, description="Minimum loan sanction amount")
    max_loan_amount: Optional[float] = Field(None, description="Maximum loan sanction amount")
    interest_rate_min: Optional[float] = Field(None, description="Minimum indicative annual interest rate %")
    interest_rate_max: Optional[float] = Field(None, description="Maximum indicative annual interest rate %")
    tenure_years: Optional[float] = Field(None, description="Repayment period in years")
    moratorium_months: Optional[int] = Field(None, description="Repayment moratorium period in months")
    collateral_required: Optional[bool] = Field(False, description="Whether collateral security is required")
    promoter_contribution_pct: Optional[float] = Field(None, description="Promoter margin money contribution %")


class ProgramGuaranteeDetailResponse(BaseModel):
    """Credit guarantee terms for guarantee-type programmes."""
    model_config = ConfigDict(from_attributes=True)

    max_credit_limit: float = Field(..., description="Maximum credit limit eligible for guarantee cover")
    guarantee_coverage_pct: float = Field(..., description="Default guarantee coverage percentage")
    annual_guarantee_fee_pct: Optional[float] = Field(None, description="Annual guarantee fee %")
    hybrid_security_allowed: Optional[bool] = Field(False, description="Whether hybrid collateral is accepted")
    eligible_lending_institutions: Optional[str] = Field(None, description="Participating MLIs / banks")


class ProgramSubsidyDetailResponse(BaseModel):
    """Capital subsidy and grant terms for assistance programmes."""
    model_config = ConfigDict(from_attributes=True)

    subsidy_pct: Optional[float] = Field(None, description="Capital subsidy percentage")
    max_subsidy_amount: Optional[float] = Field(None, description="Maximum financial subsidy cap in INR")
    min_project_cost: Optional[float] = Field(None, description="Minimum project cost eligible")
    max_project_cost: Optional[float] = Field(None, description="Maximum project cost eligible")
    beneficiary_contribution_pct: Optional[float] = Field(None, description="Beneficiary equity contribution %")
    disbursement_type: Optional[str] = Field(None, description="Disbursement method (Back-ended / Direct)")


class ProgramResponse(BaseModel):
    """Metadata summary representation for government programme listings."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique programme ID")
    program_code: str = Field(..., description="Standard unique programme code")
    program_name: str = Field(..., description="Official government programme title")
    owning_ministry: str = Field(..., description="Nodal Ministry or Department")
    nodal_agency: Optional[str] = Field(None, description="Implementing agency")
    official_portal_url: str = Field(..., description="Official government portal link")
    primary_type: str = Field(..., description="Primary categorization (CREDIT, SUBSIDY, GUARANTEE, etc.)")
    secondary_types: Optional[List[str]] = Field(default_factory=list, description="Ancillary assistance types")
    actionability_type: str = Field(..., description="Actionability classification")
    hierarchy_level: str = Field(..., description="Programme hierarchy level")
    parent_program_id: Optional[int] = Field(None, description="Parent programme ID if sub-programme")
    description: Optional[str] = Field(None, description="Detailed programme description")
    benefit_summary: str = Field(..., description="Key assistance benefit summary")
    benefit_type: str = Field(..., description="Primary benefit modality")
    benefit_headline_numeric: Optional[float] = Field(None, description="Headline monetary benefit in INR")
    benefit_headline_percentage: Optional[float] = Field(None, description="Headline subsidy/coverage %")
    target_beneficiary_summary: Optional[str] = Field(None, description="Target beneficiary segment description")
    status: str = Field("active", description="Operational status: active, archived, paused")
    legacy_scheme_id: Optional[int] = Field(None, description="Associated legacy scheme ID if mapped")
    created_at: Optional[datetime] = Field(None, description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Record update timestamp")
    sectors: List[ProgramSectorResponse] = Field(default_factory=list, description="Target industry sectors")


class ProgramDetailResponse(ProgramResponse):
    """Detailed representation for a single government programme including sub-components."""
    eligibility: Optional[ProgramEligibilityResponse] = Field(None, description="Normalized eligibility criteria")
    credit_details: Optional[ProgramCreditDetailResponse] = Field(None, description="Credit / loan parameters")
    guarantee_details: Optional[ProgramGuaranteeDetailResponse] = Field(None, description="Credit guarantee terms")
    subsidy_details: Optional[ProgramSubsidyDetailResponse] = Field(None, description="Capital subsidy / grant terms")


class ProgramQueryParams(BaseModel):
    """Validated query filter parameters for programme discovery."""
    status: Optional[str] = Field(None, description="Filter by operational status (e.g. 'active')")
    primary_type: Optional[str] = Field(None, description="Filter by primary type (e.g. 'CREDIT / LOAN', 'CREDIT GUARANTEE')")
    actionability_type: Optional[str] = Field(None, description="Filter by actionability (e.g. 'DIRECT_BENEFICIARY')")
    ministry: Optional[str] = Field(None, description="Filter by owning ministry")
    sector: Optional[str] = Field(None, description="Filter by industry sector code or name")
    skip: int = Field(default=0, ge=0, description="Offset for pagination")
    limit: int = Field(default=100, ge=1, le=100, description="Maximum records to return (up to 100)")
