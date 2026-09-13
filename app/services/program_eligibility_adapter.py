"""
app/services/program_eligibility_adapter.py

Adapter that normalizes GovernmentProgram records into an EvaluatableProgram
container suitable for the deterministic statutory eligibility engine.

Handles both:
A. Legacy-linked programmes (legacy_scheme_id IS NOT NULL) -> extracts from legacy Scheme relationships
B. New programmes (legacy_scheme_id IS NULL) -> extracts from program_eligibility,
   program_sectors, program_credit_details, program_guarantee_details, program_subsidy_details.
"""

from dataclasses import dataclass, field
from typing import Optional, Set
from app.models.program_models import GovernmentProgram
from app.schemas.eligibility import FinancialConstraints


VALID_CANONICAL_SECTORS = {"MFG", "SRV", "TRD", "AGR", "ART"}


@dataclass
class EvaluatableProgram:
    """Normalized, uniform representation of a government programme for statutory eligibility evaluation."""
    program_id: int
    program_code: str
    program_name: str
    primary_type: str
    actionability_type: str
    official_portal_url: Optional[str] = None
    benefit_summary: Optional[str] = None
    legacy_scheme_id: Optional[int] = None

    # Demographics
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    male_eligible: Optional[bool] = None
    female_eligible: Optional[bool] = None
    other_gender_eligible: Optional[bool] = None
    general_eligible: Optional[bool] = None
    sc_eligible: Optional[bool] = None
    st_eligible: Optional[bool] = None
    obc_eligible: Optional[bool] = None
    minority_eligible: Optional[bool] = None
    pwd_eligible: Optional[bool] = None
    ex_servicemen_eligible: Optional[bool] = None
    rural_eligible: Optional[bool] = None
    urban_eligible: Optional[bool] = None
    max_annual_income: Optional[float] = None

    # Canonical Sectors (strictly subset of MFG, SRV, TRD, AGR, ART)
    sector_codes: Set[str] = field(default_factory=set)

    # Financial Constraints
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

    # Business Stage & Location Scope
    new_business_only: Optional[bool] = None
    existing_business_allowed: Optional[bool] = None
    state: Optional[str] = None

    # Authoritative Notes & Operational Criteria
    notes: Optional[str] = None

    # Program Mandates & Domain Metadata
    target_gender: Optional[str] = None
    target_social_categories: Optional[str] = None
    artisan_mandate: bool = False
    street_vendor_mandate: bool = False
    startup_mandate: bool = False
    owning_ministry: Optional[str] = None

    def to_financial_constraints(self) -> Optional[FinancialConstraints]:
        """Convert financial parameters to the API schema model if any exist."""
        has_financials = any(
            v is not None
            for v in [
                self.min_loan_amount,
                self.max_loan_amount,
                self.min_project_cost,
                self.max_project_cost,
                self.max_subsidy_amount,
                self.subsidy_percentage,
                self.max_guarantee_limit,
                self.guarantee_coverage_pct,
                self.interest_rate_min,
                self.interest_rate_max,
            ]
        )
        if not has_financials:
            return None

        return FinancialConstraints(
            min_loan_amount=self.min_loan_amount,
            max_loan_amount=self.max_loan_amount,
            min_project_cost=self.min_project_cost,
            max_project_cost=self.max_project_cost,
            max_subsidy_amount=self.max_subsidy_amount,
            subsidy_percentage=self.subsidy_percentage,
            max_guarantee_limit=self.max_guarantee_limit,
            guarantee_coverage_pct=self.guarantee_coverage_pct,
            interest_rate_min=self.interest_rate_min,
            interest_rate_max=self.interest_rate_max,
        )


class ProgramEligibilityAdapter:
    """Adapts a GovernmentProgram SQLAlchemy entity into an EvaluatableProgram."""

    @classmethod
    def adapt(cls, program: GovernmentProgram) -> EvaluatableProgram:
        """Extract and normalize all eligibility, sector, and financial parameters."""
        eval_prog = EvaluatableProgram(
            program_id=program.id,
            program_code=program.program_code,
            program_name=program.program_name,
            primary_type=program.primary_type,
            actionability_type=program.actionability_type,
            official_portal_url=program.official_portal_url,
            benefit_summary=program.benefit_summary,
            legacy_scheme_id=program.legacy_scheme_id,
            owning_ministry=program.owning_ministry,
        )

        if program.legacy_scheme_id is not None and program.legacy_scheme is not None:
            # --- SOURCE A: Legacy Scheme linked programme ---
            ls = program.legacy_scheme
            elig = ls.eligibility_criteria

            # Mandates & Special Beneficiary Types
            if ls.target_gender:
                eval_prog.target_gender = ls.target_gender.upper() if ls.target_gender.upper() != "ALL" else None
            if ls.target_group and "Scheduled Caste" in ls.target_group:
                eval_prog.target_social_categories = "SC"
            if (ls.target_group and "artisan" in ls.target_group.lower()) or (ls.scheme_type and "artisan" in ls.scheme_type.lower()):
                eval_prog.artisan_mandate = True
            if ls.target_group and "street vendor" in ls.target_group.lower():
                eval_prog.street_vendor_mandate = True

            # Demographics
            eval_prog.min_age = elig.min_age if (elig and elig.min_age is not None) else ls.min_age
            eval_prog.max_age = elig.max_age if (elig and elig.max_age is not None) else ls.max_age

            if elig is not None:
                eval_prog.male_eligible = elig.male_eligible
                eval_prog.female_eligible = elig.female_eligible
                eval_prog.other_gender_eligible = elig.other_gender_eligible
                eval_prog.general_eligible = elig.general_eligible
                eval_prog.sc_eligible = elig.sc_eligible
                eval_prog.st_eligible = elig.st_eligible
                eval_prog.obc_eligible = elig.obc_eligible
                eval_prog.minority_eligible = elig.minority_eligible
                eval_prog.pwd_eligible = elig.pwd_eligible
                eval_prog.ex_servicemen_eligible = elig.ex_servicemen_eligible
                eval_prog.rural_eligible = elig.rural_eligible
                eval_prog.urban_eligible = False if ls.rural_only else elig.urban_eligible
                eval_prog.notes = elig.notes
            else:
                eval_prog.rural_eligible = None
                eval_prog.urban_eligible = False if ls.rural_only else None
                eval_prog.notes = ls.eligibility_text

            # Income ceiling
            if elig is not None and elig.max_annual_income is not None:
                eval_prog.max_annual_income = float(elig.max_annual_income)
            elif ls.income_limit is not None:
                eval_prog.max_annual_income = float(ls.income_limit)

            # Sectors (normalized canonical sector codes)
            if ls.sectors_mapped:
                eval_prog.sector_codes = {
                    s.sector_code.upper()
                    for s in ls.sectors_mapped
                    if s.sector_code and s.sector_code.upper() in VALID_CANONICAL_SECTORS
                }

            # Financial constraints
            if ls.min_loan_amount is not None:
                eval_prog.min_loan_amount = float(ls.min_loan_amount)
            if ls.max_loan_amount is not None:
                eval_prog.max_loan_amount = float(ls.max_loan_amount)
            if ls.min_project_cost is not None:
                eval_prog.min_project_cost = float(ls.min_project_cost)
            if ls.max_project_cost is not None:
                eval_prog.max_project_cost = float(ls.max_project_cost)
            if ls.max_subsidy is not None:
                eval_prog.max_subsidy_amount = float(ls.max_subsidy)
            if ls.subsidy_percentage is not None:
                eval_prog.subsidy_percentage = float(ls.subsidy_percentage)
            if ls.interest_rate is not None:
                eval_prog.interest_rate_min = float(ls.interest_rate)
                eval_prog.interest_rate_max = float(ls.interest_rate)

            # Business stage & scope
            eval_prog.new_business_only = ls.new_business_only
            eval_prog.existing_business_allowed = ls.existing_business_allowed
            eval_prog.state = ls.state

        else:
            # --- SOURCE B: New Government Programme ---
            elig = program.eligibility
            if elig is not None:
                eval_prog.min_age = elig.min_age
                eval_prog.max_age = elig.max_age
                eval_prog.male_eligible = elig.male_eligible
                eval_prog.female_eligible = elig.female_eligible
                eval_prog.other_gender_eligible = elig.other_gender_eligible
                eval_prog.general_eligible = elig.general_eligible
                eval_prog.sc_eligible = elig.sc_eligible
                eval_prog.st_eligible = elig.st_eligible
                eval_prog.obc_eligible = elig.obc_eligible
                eval_prog.minority_eligible = elig.minority_eligible
                eval_prog.pwd_eligible = elig.pwd_eligible
                eval_prog.ex_servicemen_eligible = elig.ex_servicemen_eligible
                eval_prog.rural_eligible = elig.rural_eligible
                eval_prog.urban_eligible = elig.urban_eligible
                eval_prog.notes = elig.notes
                if elig.max_annual_income is not None:
                    eval_prog.max_annual_income = float(elig.max_annual_income)
                eval_prog.target_gender = elig.target_gender
                eval_prog.target_social_categories = elig.target_social_categories
                eval_prog.artisan_mandate = bool(elig.artisan_mandate)
                eval_prog.street_vendor_mandate = bool(elig.street_vendor_mandate)
                eval_prog.startup_mandate = bool(elig.startup_mandate)

            # Sectors (normalized canonical sector codes)
            if program.sectors:
                eval_prog.sector_codes = {
                    s.sector_code.upper()
                    for s in program.sectors
                    if s.sector_code and s.sector_code.upper() in VALID_CANONICAL_SECTORS
                }

            # Credit details
            if program.credit_details is not None:
                cd = program.credit_details
                if cd.min_loan_amount is not None:
                    eval_prog.min_loan_amount = float(cd.min_loan_amount)
                if cd.max_loan_amount is not None:
                    eval_prog.max_loan_amount = float(cd.max_loan_amount)
                if cd.interest_rate_min is not None:
                    eval_prog.interest_rate_min = float(cd.interest_rate_min)
                if cd.interest_rate_max is not None:
                    eval_prog.interest_rate_max = float(cd.interest_rate_max)

            # Guarantee details
            if program.guarantee_details is not None:
                gd = program.guarantee_details
                if gd.max_credit_limit is not None:
                    eval_prog.max_guarantee_limit = float(gd.max_credit_limit)
                if gd.guarantee_coverage_pct is not None:
                    eval_prog.guarantee_coverage_pct = float(gd.guarantee_coverage_pct)

            # Subsidy details
            if program.subsidy_details is not None:
                sd = program.subsidy_details
                if sd.min_project_cost is not None:
                    eval_prog.min_project_cost = float(sd.min_project_cost)
                if sd.max_project_cost is not None:
                    eval_prog.max_project_cost = float(sd.max_project_cost)
                if sd.max_subsidy_amount is not None:
                    eval_prog.max_subsidy_amount = float(sd.max_subsidy_amount)
                if sd.subsidy_pct is not None:
                    eval_prog.subsidy_percentage = float(sd.subsidy_pct)

            # Default geographical scope for Central Government programmes
            eval_prog.state = "All India"

        return eval_prog
