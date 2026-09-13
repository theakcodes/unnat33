from typing import List, Union
from sqlalchemy.orm import Session

from app.core.exceptions import ProgramNotFoundException
from app.models.program_models import GovernmentProgram
from app.repositories.program_repository import program_repository
from app.schemas.program import (
    ProgramQueryParams,
    ProgramResponse,
    ProgramDetailResponse,
    ProgramSectorResponse,
    ProgramEligibilityResponse,
    ProgramCreditDetailResponse,
    ProgramGuaranteeDetailResponse,
    ProgramSubsidyDetailResponse,
)


class ProgramService:
    """Service class managing business logic and serialization for government programmes."""

    @staticmethod
    def _format_sectors(program: GovernmentProgram) -> List[ProgramSectorResponse]:
        """Resolve applicable sectors from legacy scheme or new program sectors."""
        sectors = []
        if program.legacy_scheme and program.legacy_scheme.sectors_mapped:
            sectors = [
                ProgramSectorResponse(
                    id=s.id,
                    sector_code=s.sector_code,
                    sector_name=s.sector_name,
                )
                for s in program.legacy_scheme.sectors_mapped
            ]
        elif program.sectors:
            sectors = [
                ProgramSectorResponse(
                    id=s.id,
                    sector_code=s.sector_code,
                    sector_name=s.sector_name,
                )
                for s in program.sectors
            ]
        return sectors

    @classmethod
    def _format_program_summary(cls, program: GovernmentProgram) -> ProgramResponse:
        """Serialize a GovernmentProgram model into ProgramResponse summary."""
        sectors = cls._format_sectors(program)

        return ProgramResponse(
            id=program.id,
            program_code=program.program_code,
            program_name=program.program_name,
            owning_ministry=program.owning_ministry,
            nodal_agency=program.nodal_agency,
            official_portal_url=program.official_portal_url,
            primary_type=program.primary_type,
            secondary_types=program.secondary_types or [],
            actionability_type=program.actionability_type,
            hierarchy_level=program.hierarchy_level,
            parent_program_id=program.parent_program_id,
            description=program.description,
            benefit_summary=program.benefit_summary,
            benefit_type=program.benefit_type,
            benefit_headline_numeric=(
                float(program.benefit_headline_numeric)
                if program.benefit_headline_numeric is not None
                else None
            ),
            benefit_headline_percentage=(
                float(program.benefit_headline_percentage)
                if program.benefit_headline_percentage is not None
                else None
            ),
            target_beneficiary_summary=program.target_beneficiary_summary,
            status=program.status,
            legacy_scheme_id=program.legacy_scheme_id,
            created_at=program.created_at,
            updated_at=program.updated_at,
            sectors=sectors,
        )

    @classmethod
    def _format_program_detail(cls, program: GovernmentProgram) -> ProgramDetailResponse:
        """Serialize a GovernmentProgram model into ProgramDetailResponse with sub-details."""
        summary = cls._format_program_summary(program)

        # Resolve eligibility criteria (from legacy scheme or program_eligibility)
        elig_obj = None
        raw_elig = None
        if program.legacy_scheme and program.legacy_scheme.eligibility_criteria:
            raw_elig = program.legacy_scheme.eligibility_criteria
        elif program.eligibility:
            raw_elig = program.eligibility

        if raw_elig:
            elig_obj = ProgramEligibilityResponse(
                rural_eligible=raw_elig.rural_eligible,
                urban_eligible=raw_elig.urban_eligible,
                male_eligible=raw_elig.male_eligible,
                female_eligible=raw_elig.female_eligible,
                other_gender_eligible=raw_elig.other_gender_eligible,
                general_eligible=raw_elig.general_eligible,
                sc_eligible=raw_elig.sc_eligible,
                st_eligible=raw_elig.st_eligible,
                obc_eligible=raw_elig.obc_eligible,
                minority_eligible=raw_elig.minority_eligible,
                pwd_eligible=raw_elig.pwd_eligible,
                ex_servicemen_eligible=raw_elig.ex_servicemen_eligible,
                min_age=raw_elig.min_age,
                max_age=raw_elig.max_age,
                max_annual_income=(
                    float(raw_elig.max_annual_income)
                    if raw_elig.max_annual_income is not None
                    else None
                ),
                notes=raw_elig.notes,
            )

        # Credit details
        credit_obj = None
        if program.credit_details:
            cd = program.credit_details
            credit_obj = ProgramCreditDetailResponse(
                min_loan_amount=(
                    float(cd.min_loan_amount)
                    if cd.min_loan_amount is not None
                    else None
                ),
                max_loan_amount=(
                    float(cd.max_loan_amount)
                    if cd.max_loan_amount is not None
                    else None
                ),
                interest_rate_min=(
                    float(cd.interest_rate_min)
                    if cd.interest_rate_min is not None
                    else None
                ),
                interest_rate_max=(
                    float(cd.interest_rate_max)
                    if cd.interest_rate_max is not None
                    else None
                ),
                tenure_years=(
                    float(cd.tenure_years)
                    if cd.tenure_years is not None
                    else None
                ),
                moratorium_months=cd.moratorium_months,
                collateral_required=cd.collateral_required,
                promoter_contribution_pct=(
                    float(cd.promoter_contribution_pct)
                    if cd.promoter_contribution_pct is not None
                    else None
                ),
            )

        # Guarantee details
        guarantee_obj = None
        if program.guarantee_details:
            gd = program.guarantee_details
            guarantee_obj = ProgramGuaranteeDetailResponse(
                max_credit_limit=float(gd.max_credit_limit),
                guarantee_coverage_pct=float(gd.guarantee_coverage_pct),
                annual_guarantee_fee_pct=(
                    float(gd.annual_guarantee_fee_pct)
                    if gd.annual_guarantee_fee_pct is not None
                    else None
                ),
                hybrid_security_allowed=gd.hybrid_security_allowed,
                eligible_lending_institutions=gd.eligible_lending_institutions,
            )

        # Subsidy details
        subsidy_obj = None
        if program.subsidy_details:
            sd = program.subsidy_details
            subsidy_obj = ProgramSubsidyDetailResponse(
                subsidy_pct=(
                    float(sd.subsidy_pct)
                    if sd.subsidy_pct is not None
                    else None
                ),
                max_subsidy_amount=(
                    float(sd.max_subsidy_amount)
                    if sd.max_subsidy_amount is not None
                    else None
                ),
                min_project_cost=(
                    float(sd.min_project_cost)
                    if sd.min_project_cost is not None
                    else None
                ),
                max_project_cost=(
                    float(sd.max_project_cost)
                    if sd.max_project_cost is not None
                    else None
                ),
                beneficiary_contribution_pct=(
                    float(sd.beneficiary_contribution_pct)
                    if sd.beneficiary_contribution_pct is not None
                    else None
                ),
                disbursement_type=sd.disbursement_type,
            )

        return ProgramDetailResponse(
            **summary.model_dump(),
            eligibility=elig_obj,
            credit_details=credit_obj,
            guarantee_details=guarantee_obj,
            subsidy_details=subsidy_obj,
        )

    @classmethod
    def get_programs(
        cls,
        db: Session,
        filters: ProgramQueryParams,
    ) -> List[ProgramResponse]:
        """Retrieve programmes applying query filters and pagination."""
        programs = program_repository.get_all(db, filters=filters)
        return [cls._format_program_summary(p) for p in programs]

    @classmethod
    def get_program_by_identifier(
        cls,
        db: Session,
        identifier: Union[int, str],
    ) -> ProgramDetailResponse:
        """Retrieve detailed single programme or raise ProgramNotFoundException."""
        program = program_repository.get_by_identifier(db, identifier=identifier)
        if not program:
            raise ProgramNotFoundException(identifier=identifier)
        return cls._format_program_detail(program)


program_service = ProgramService()
