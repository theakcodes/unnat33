from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class SchemeBase(BaseModel):
    """Base schema for Scheme representation."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Official scheme name")
    description: Optional[str] = Field(None, description="Detailed description of scheme")
    ministry: Optional[str] = Field(None, description="Nodal Ministry or Department")
    scheme_type: Optional[str] = Field(None, description="Type of support: loan, subsidy, grant, etc.")
    category: Optional[str] = Field(None, description="Scheme category")
    business_type: Optional[str] = Field(None, description="Eligible enterprise types")
    sector: Optional[str] = Field(None, description="Sector applicability")
    target_group: Optional[str] = Field(None, description="Target beneficiary segment")
    state: Optional[str] = Field(None, description="State applicability, or 'All India'")
    target_gender: Optional[str] = Field(None, description="Target gender or 'All'")
    min_age: Optional[int] = Field(None, ge=0, description="Minimum beneficiary age")
    max_age: Optional[int] = Field(None, ge=0, description="Maximum beneficiary age")
    rural_only: Optional[bool] = Field(False, description="Whether scheme is restricted to rural areas")
    income_limit: Optional[float] = Field(None, description="Maximum family/annual income ceiling")


class SchemeResponse(SchemeBase):
    """Full scheme details returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique scheme ID")

    # Financial / Project cost details
    min_project_cost: Optional[float] = Field(None, description="Minimum project cost eligible")
    max_project_cost: Optional[float] = Field(None, description="Maximum project cost eligible")
    loan_percentage: Optional[float] = Field(None, description="Percentage of project financed as loan")
    min_loan_amount: Optional[float] = Field(None, description="Minimum loan amount")
    max_loan_amount: Optional[float] = Field(None, description="Maximum loan amount")
    beneficiary_contribution_percentage: Optional[float] = Field(None, description="Beneficiary contribution %")

    # Subsidy parameters
    subsidy_percentage: Optional[float] = Field(None, description="Subsidy / margin money percentage")
    max_subsidy: Optional[float] = Field(None, description="Maximum financial subsidy amount")

    # Repayment
    interest_rate: Optional[float] = Field(None, description="Indicative interest rate %")
    tenure_years: Optional[float] = Field(None, description="Loan tenure in years")
    moratorium_months: Optional[int] = Field(None, description="Moratorium period in months")
    repayment_frequency: Optional[str] = Field(None, description="Frequency of repayment")

    # Business stage & collateral
    new_business_only: Optional[bool] = Field(False, description="Available exclusively for new businesses")
    existing_business_allowed: Optional[bool] = Field(True, description="Available for existing businesses")
    collateral_required: Optional[bool] = Field(False, description="Whether collateral security is mandatory")

    # Information & guidance
    benefit: Optional[str] = Field(None, description="Key scheme benefit summary")
    eligibility_text: Optional[str] = Field(None, description="Human-readable statutory eligibility criteria")
    documents_required: Optional[str] = Field(None, description="Mandatory application documentation")
    application_url: Optional[str] = Field(None, description="Official portal or application link")

    # Status & metadata
    status: Optional[str] = Field("active", description="Operational status: active, closed, paused")
    last_verified: Optional[date] = Field(None, description="Last verification date of scheme guidelines")
    created_at: Optional[datetime] = Field(None, description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Record last updated timestamp")


class SchemeQueryParams(BaseModel):
    """Validated query parameters for scheme filtering."""
    state: Optional[str] = Field(None, description="Filter by state (e.g., 'Rajasthan', 'All India')")
    sector: Optional[str] = Field(None, description="Filter by sector (e.g., 'Micro Enterprise', 'Manufacturing')")
    scheme_type: Optional[str] = Field(None, description="Filter by type (e.g., 'loan', 'Credit', 'subsidy')")
    category: Optional[str] = Field(None, description="Filter by category (e.g., 'Direct Financing')")
    target_group: Optional[str] = Field(None, description="Filter by target group")
    business_type: Optional[str] = Field(None, description="Filter by business type")
    target_gender: Optional[str] = Field(None, description="Filter by target gender")
    rural_only: Optional[bool] = Field(None, description="Filter by rural restriction flag")
    include_all_india: bool = Field(True, description="When filtering by a specific state, also include nationwide schemes")
    skip: int = Field(default=0, ge=0, description="Number of records to skip for pagination")
    limit: int = Field(default=50, ge=1, le=100, description="Max records to return")
