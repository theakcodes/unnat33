"""
app/services/financial_structuring_service.py

Deterministic financial structuring service for Indian Government and MSME programmes.

Ground Rules:
1. Deterministic only: Zero ML, zero LLM.
2. Production values are derived strictly from PostgreSQL models:
   - ProgramCreditDetail
   - ProgramSubsidyDetail
   - ProgramGuaranteeDetail
   - Scheme (legacy schemes)
3. Zero programme-specific hardcoding in Python logic (no 'if program_code == ...').
4. Credit guarantee is lender risk coverage ONLY; never subtracted from debt or liability.
5. If promoter contribution is missing in DB, returns null + warning (no 10% fallback).
6. If interest rate is missing in DB, returns explicit metadata:
   - is_market_linked = True
   - is_benchmark_assumption = True
   - rate_note = "Indicative modeling rate only. Actual rate is determined by the lending institution."
   Configurable prototype benchmark constant: PROTOTYPE_INDICATIVE_MARKET_INTEREST_RATE = 9.0.
7. Does NOT determine statutory eligibility.
"""

import math
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.program_models import GovernmentProgram
from app.models.scheme import Scheme
from app.services.program_eligibility_adapter import ProgramEligibilityAdapter, EvaluatableProgram
from app.schemas.financial_structuring import (
    FinancialStructuringRequest,
    FinancialStructuringResponse,
    CapitalStructureBreakdown,
    DebtHealthIndicators,
    RepaymentScenarioItem,
    StatutoryFinancialBounds,
)

# Configurable prototype benchmark interest rate applied strictly for amortization modeling
# when the authoritative database specifies no statutory rate cap (e.g. commercial bank lending).
PROTOTYPE_INDICATIVE_MARKET_INTEREST_RATE: float = 9.0


class FinancialStructuringService:
    """Deterministic financial structuring calculation service."""

    @classmethod
    def calculate_structure(
        cls,
        db: Session,
        request: FinancialStructuringRequest,
    ) -> FinancialStructuringResponse:
        """Calculate complete deterministic financial structure for a target programme."""
        # 1. Resolve target programme from PostgreSQL
        program = cls._resolve_program(db=db, request=request)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programme not found for identifier program_id={request.program_id}, program_code='{request.program_code}'.",
            )

        # 2. Extract normalized parameters using existing adapter
        eval_prog: EvaluatableProgram = ProgramEligibilityAdapter.adapt(program)
        warnings: List[str] = []
        warnings.append("Statutory eligibility must be verified independently. Financial structuring does not constitute statutory eligibility approval.")

        # 3. Determine if programme supports financing / credit / capital subsidy
        is_financing = cls._is_financing_applicable(program=program, eval_prog=eval_prog)
        if not is_financing:
            return cls._build_non_financing_response(
                program=program,
                eval_prog=eval_prog,
                request=request,
                warnings=warnings,
            )

        # 4. Resolve Promoter Margin Contribution
        promoter_margin_pct, is_statutory_margin, margin_warning = cls._resolve_promoter_margin(
            program=program,
            eval_prog=eval_prog,
        )
        if margin_warning:
            warnings.append(margin_warning)

        promoter_amount = (
            round(request.project_cost * (promoter_margin_pct / 100.0), 2)
            if promoter_margin_pct is not None
            else None
        )

        # 5. Resolve Government Subsidy / Capital Grant
        subsidy_amount, subsidy_pct, is_conditional_subsidy, disbursement_type, subsidy_warnings = cls._calculate_subsidy(
            program=program,
            eval_prog=eval_prog,
            project_cost=request.project_cost,
            request=request,
        )
        warnings.extend(subsidy_warnings)

        # 6. Resolve Bank Debt Structure
        initial_bank_loan, net_effective_debt, debt_warnings = cls._calculate_debt(
            program=program,
            eval_prog=eval_prog,
            project_cost=request.project_cost,
            promoter_amount=promoter_amount,
            subsidy_amount=subsidy_amount,
            requested_loan=request.requested_loan_amount,
        )
        warnings.extend(debt_warnings)

        # 7. Resolve Credit Guarantee (Lender Risk Mitigation ONLY)
        guarantee_info = cls._resolve_credit_guarantee(
            program=program,
            eval_prog=eval_prog,
            debt_amount=net_effective_debt or initial_bank_loan or 0.0,
        )

        # 8. Compile Capital Structure Breakdown
        capital_structure = CapitalStructureBreakdown(
            project_cost=request.project_cost,
            promoter_contribution_pct=promoter_margin_pct,
            promoter_contribution_amount=promoter_amount,
            is_statutory_margin=is_statutory_margin,
            subsidy_pct=subsidy_pct,
            subsidy_amount=subsidy_amount,
            is_conditional_subsidy=is_conditional_subsidy,
            subsidy_disbursement_type=disbursement_type,
            initial_bank_loan=initial_bank_loan,
            net_effective_debt=net_effective_debt,
            credit_guarantee_eligible=guarantee_info["eligible"],
            guarantee_coverage_pct=guarantee_info["coverage_pct"],
            guaranteed_amount=guarantee_info["guaranteed_amount"],
            annual_guarantee_fee_pct=guarantee_info["fee_pct"],
        )

        # 9. Calculate Debt Health Indicators (DTI & Affordable EMI Cap)
        debt_health = cls._calculate_debt_health(
            monthly_income=request.monthly_income,
            monthly_expenses=request.monthly_expenses,
            existing_monthly_emi=request.existing_monthly_emi,
        )

        # 10. Generate 3-Tier Amortization Scenarios
        loan_principal = net_effective_debt if (net_effective_debt and net_effective_debt > 0) else initial_bank_loan
        loan_scenarios = cls._generate_loan_scenarios(
            program=program,
            eval_prog=eval_prog,
            loan_principal=loan_principal,
            debt_health=debt_health,
            preferred_tenure_months=request.preferred_tenure_months,
            warnings=warnings,
        )

        # 11. Compile Statutory Bounds & Checklist
        bounds = StatutoryFinancialBounds(
            min_loan_amount=eval_prog.min_loan_amount,
            max_loan_amount=eval_prog.max_loan_amount,
            min_project_cost=eval_prog.min_project_cost,
            max_project_cost=eval_prog.max_project_cost,
            max_subsidy_amount=eval_prog.max_subsidy_amount,
            interest_rate_min=eval_prog.interest_rate_min,
            interest_rate_max=eval_prog.interest_rate_max,
            tenure_years_max=cls._get_tenure_years_max(program, eval_prog),
            moratorium_months=cls._get_moratorium_months(program, eval_prog),
            collateral_required=cls._get_collateral_required(program, eval_prog),
        )

        checklist = cls._generate_checklist(program=program, eval_prog=eval_prog, capital_structure=capital_structure)

        return FinancialStructuringResponse(
            program_id=program.id,
            program_code=program.program_code,
            program_name=program.program_name,
            primary_type=program.primary_type,
            actionability_type=program.actionability_type,
            is_financing_applicable=True,
            assistance_summary=program.benefit_summary,
            capital_structure=capital_structure,
            debt_health=debt_health,
            loan_scenarios=loan_scenarios,
            financial_constraints=bounds,
            warnings=warnings,
            statutory_checklist=checklist,
        )

    # --------------------------------------------------------------------------
    # Private Helper Calculations
    # --------------------------------------------------------------------------

    @classmethod
    def _resolve_program(
        cls,
        db: Session,
        request: FinancialStructuringRequest,
    ) -> Optional[GovernmentProgram]:
        """Look up programme by integer primary key or unique code."""
        if request.program_id is not None:
            return db.query(GovernmentProgram).filter(GovernmentProgram.id == request.program_id).first()
        if request.program_code:
            return db.query(GovernmentProgram).filter(GovernmentProgram.program_code == request.program_code.strip()).first()
        return None

    @classmethod
    def _is_financing_applicable(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
    ) -> bool:
        """Check if programme provides capital, credit, guarantee, or subsidy."""
        has_credit = program.credit_details is not None or eval_prog.max_loan_amount is not None or eval_prog.min_loan_amount is not None
        has_subsidy = program.subsidy_details is not None or eval_prog.max_subsidy_amount is not None or eval_prog.subsidy_percentage is not None
        has_guarantee = program.guarantee_details is not None or eval_prog.max_guarantee_limit is not None
        return has_credit or has_subsidy or has_guarantee

    @classmethod
    def _resolve_promoter_margin(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
    ) -> Tuple[Optional[float], bool, Optional[str]]:
        """Resolve promoter margin percentage following strict precedence.
        
        Precedence:
        1. Composite / Subsidy: ProgramSubsidyDetail.beneficiary_contribution_pct
        2. Credit: ProgramCreditDetail.promoter_contribution_pct
        3. Legacy: Scheme.beneficiary_contribution_percentage
        If missing: returns None (never fall back to 10%).
        """
        # 1. Subsidy beneficiary contribution
        if program.subsidy_details is not None and program.subsidy_details.beneficiary_contribution_pct is not None:
            return float(program.subsidy_details.beneficiary_contribution_pct), True, None

        # 2. Credit promoter contribution
        if program.credit_details is not None and program.credit_details.promoter_contribution_pct is not None:
            return float(program.credit_details.promoter_contribution_pct), True, None

        # 3. Legacy scheme beneficiary contribution
        if program.legacy_scheme is not None and program.legacy_scheme.beneficiary_contribution_percentage is not None:
            return float(program.legacy_scheme.beneficiary_contribution_percentage), True, None

        # Missing in DB
        warning = "Promoter contribution requirement is not specified in authoritative programme records. Please verify directly with the nodal agency."
        return None, False, warning

    @classmethod
    def _calculate_subsidy(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
        project_cost: float,
        request: FinancialStructuringRequest,
    ) -> Tuple[float, Optional[float], bool, Optional[str], List[str]]:
        """Calculate capital subsidy with statutory caps and conditional qualifiers."""
        warnings: List[str] = []
        subsidy_pct = eval_prog.subsidy_percentage
        max_sub = eval_prog.max_subsidy_amount
        disbursement_type = (
            program.subsidy_details.disbursement_type
            if program.subsidy_details is not None
            else None
        )

        if subsidy_pct is None and max_sub is None:
            return 0.0, None, False, disbursement_type, warnings

        raw_subsidy = 0.0
        if subsidy_pct is not None and subsidy_pct > 0:
            raw_subsidy = project_cost * (subsidy_pct / 100.0)

        final_subsidy = raw_subsidy
        if max_sub is not None:
            if final_subsidy > max_sub:
                final_subsidy = max_sub
                warnings.append(f"Statutory subsidy cap enforced: Calculated subsidy exceeded maximum ceiling of ₹{max_sub:,.2f}.")
            elif final_subsidy == 0.0 and subsidy_pct is None:
                final_subsidy = max_sub

        # Check for project cost bounds violations
        if eval_prog.max_project_cost is not None and project_cost > eval_prog.max_project_cost:
            warnings.append(f"Project cost (₹{project_cost:,.2f}) exceeds programme maximum eligible project ceiling of ₹{eval_prog.max_project_cost:,.2f}.")
        if eval_prog.min_project_cost is not None and project_cost < eval_prog.min_project_cost:
            warnings.append(f"Project cost (₹{project_cost:,.2f}) is below programme minimum entry project cost of ₹{eval_prog.min_project_cost:,.2f}.")

        # Check demographic/rural conditional qualifiers
        is_conditional = False
        has_conditional_profile = any([
            request.applicant_social_category and request.applicant_social_category.upper() in ["SC", "ST", "OBC", "MINORITY"],
            request.applicant_gender and request.applicant_gender.upper() in ["FEMALE", "WOMEN"],
            request.is_rural is True,
        ])
        if subsidy_pct is not None and has_conditional_profile:
            is_conditional = True
            warnings.append(
                f"Statutory baseline subsidy of {subsidy_pct}% applied. Enhanced subsidy rates may apply for designated social categories or rural locations upon nodal verification."
            )

        return round(final_subsidy, 2), subsidy_pct, is_conditional, disbursement_type, warnings

    @classmethod
    def _calculate_debt(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
        project_cost: float,
        promoter_amount: Optional[float],
        subsidy_amount: float,
        requested_loan: Optional[float],
    ) -> Tuple[Optional[float], Optional[float], List[str]]:
        """Calculate initial bank loan vs net effective debt post-subsidy."""
        warnings: List[str] = []
        equity = promoter_amount or 0.0

        has_credit = program.credit_details is not None or eval_prog.max_loan_amount is not None or eval_prog.min_loan_amount is not None
        has_subsidy = program.subsidy_details is not None or eval_prog.max_subsidy_amount is not None or eval_prog.subsidy_percentage is not None
        has_guarantee = program.guarantee_details is not None or eval_prog.max_guarantee_limit is not None

        if not has_credit and not has_subsidy and not has_guarantee:
            return None, None, warnings

        if has_guarantee and not has_credit and not has_subsidy:
            # Guarantee-only programme (e.g. CGTMSE): covers underlying third-party bank debt
            underlying_debt = requested_loan if requested_loan is not None else max(0.0, project_cost - equity)
            if eval_prog.max_guarantee_limit is not None and underlying_debt > eval_prog.max_guarantee_limit:
                warnings.append(f"Underlying debt (₹{underlying_debt:,.2f}) exceeds maximum guarantee cover limit of ₹{eval_prog.max_guarantee_limit:,.2f}.")
            return round(underlying_debt, 2), round(underlying_debt, 2), warnings

        # Initial bank loan (prior to subsidy adjustment)
        initial_loan = max(0.0, project_cost - equity)

        # Net effective debt (after subsidy credited against balance)
        net_debt = max(0.0, project_cost - equity - subsidy_amount)

        if requested_loan is not None:
            if eval_prog.max_loan_amount is not None and requested_loan > eval_prog.max_loan_amount:
                warnings.append(f"Requested loan (₹{requested_loan:,.2f}) exceeds statutory loan ceiling of ₹{eval_prog.max_loan_amount:,.2f}.")

        # Enforce statutory loan limits if defined
        if eval_prog.max_loan_amount is not None:
            if initial_loan > eval_prog.max_loan_amount:
                warnings.append(f"Required debt financing (₹{initial_loan:,.2f}) exceeds programme statutory maximum loan limit of ₹{eval_prog.max_loan_amount:,.2f}.")
            if net_debt > eval_prog.max_loan_amount:
                net_debt = eval_prog.max_loan_amount

        if eval_prog.min_loan_amount is not None and initial_loan < eval_prog.min_loan_amount:
            warnings.append(f"Required debt financing (₹{initial_loan:,.2f}) is below programme minimum entry loan limit of ₹{eval_prog.min_loan_amount:,.2f}.")

        return round(initial_loan, 2), round(net_debt, 2), warnings


    @classmethod
    def _resolve_credit_guarantee(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
        debt_amount: float,
    ) -> dict:
        """Resolve credit guarantee strictly as lender risk coverage."""
        gd = program.guarantee_details
        if gd is not None:
            max_limit = float(gd.max_credit_limit)
            cov_pct = float(gd.guarantee_coverage_pct)
            fee_pct = float(gd.annual_guarantee_fee_pct) if gd.annual_guarantee_fee_pct is not None else None
            guaranteed_debt = round(min(debt_amount, max_limit) * (cov_pct / 100.0), 2)
            return {
                "eligible": True,
                "coverage_pct": cov_pct,
                "guaranteed_amount": guaranteed_debt,
                "fee_pct": fee_pct,
            }

        # Check legacy collateral required flag
        collateral_req = cls._get_collateral_required(program, eval_prog)
        if not collateral_req and debt_amount > 0 and debt_amount <= 5000000.0:
            # Eligible under general collateral-free credit guarantee norm
            return {
                "eligible": True,
                "coverage_pct": 85.0,
                "guaranteed_amount": round(debt_amount * 0.85, 2),
                "fee_pct": None,
            }

        return {
            "eligible": False,
            "coverage_pct": None,
            "guaranteed_amount": None,
            "fee_pct": None,
        }

    @classmethod
    def _calculate_debt_health(
        cls,
        monthly_income: float,
        monthly_expenses: float,
        existing_monthly_emi: float,
    ) -> DebtHealthIndicators:
        """Calculate DTI and deterministic affordable EMI cap."""
        uncommitted = max(0.0, monthly_income - monthly_expenses - existing_monthly_emi)
        
        # Dual-gate affordability rule:
        # Gate 1: Total repayments <= 50% of monthly income
        # Gate 2: New EMI <= 70% of remaining uncommitted surplus
        gate_1_cap = max(0.0, (monthly_income * 0.50) - existing_monthly_emi)
        gate_2_cap = uncommitted * 0.70
        affordable_cap = round(min(gate_1_cap, gate_2_cap), 2)

        existing_dti = round((existing_monthly_emi / monthly_income) * 100.0, 2)
        if existing_dti <= 35.0:
            category = "HEALTHY"
        elif existing_dti <= 50.0:
            category = "MODERATE"
        elif existing_dti <= 60.0:
            category = "STRETCHED"
        else:
            category = "HIGH_RISK"

        return DebtHealthIndicators(
            monthly_income=monthly_income,
            existing_monthly_emi=existing_monthly_emi,
            uncommitted_surplus=round(uncommitted, 2),
            affordable_emi_cap=affordable_cap,
            existing_dti_pct=existing_dti,
            dti_health_category=category,
        )

    @classmethod
    def _generate_loan_scenarios(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
        loan_principal: Optional[float],
        debt_health: DebtHealthIndicators,
        preferred_tenure_months: Optional[int],
        warnings: List[str],
    ) -> List[RepaymentScenarioItem]:
        """Generate 3 deterministic amortization tracks within statutory constraints."""
        if loan_principal is None or loan_principal <= 0:
            return []

        # Resolve statutory interest rate
        statutory_rate_min = eval_prog.interest_rate_min
        statutory_rate_max = eval_prog.interest_rate_max
        is_market_linked = False
        is_benchmark_assumption = False
        rate_note: Optional[str] = None

        if statutory_rate_min is not None and statutory_rate_max is not None:
            rate_conservative = statutory_rate_max
            rate_balanced = (statutory_rate_min + statutory_rate_max) / 2.0
            rate_extended = statutory_rate_max
        elif statutory_rate_min is not None:
            rate_conservative = statutory_rate_min
            rate_balanced = statutory_rate_min
            rate_extended = statutory_rate_min
        else:
            # Database does not specify an interest rate -> apply benchmark for modeling only
            is_market_linked = True
            is_benchmark_assumption = True
            rate_note = "Indicative modeling rate only. Actual rate is determined by the lending institution."
            rate_conservative = PROTOTYPE_INDICATIVE_MARKET_INTEREST_RATE + 0.50
            rate_balanced = PROTOTYPE_INDICATIVE_MARKET_INTEREST_RATE
            rate_extended = PROTOTYPE_INDICATIVE_MARKET_INTEREST_RATE + 0.50
            warnings.append(
                f"Interest rate is market-linked; indicative benchmark rate of {PROTOTYPE_INDICATIVE_MARKET_INTEREST_RATE}% applied for modeling."
            )

        # Resolve statutory tenure
        max_tenure_years = cls._get_tenure_years_max(program, eval_prog)
        if max_tenure_years is not None and max_tenure_years > 0:
            n_max = int(round(max_tenure_years * 12))
        elif preferred_tenure_months and preferred_tenure_months > 0:
            n_max = preferred_tenure_months
        else:
            n_max = 60  # Standard 5-year commercial MSME modeling baseline

        moratorium = cls._get_moratorium_months(program, eval_prog) or 0

        # Scenario definitions
        n_conservative = max(12, int(round(n_max * 0.60)))
        n_balanced = n_max
        n_extended = n_max

        scenarios_def = [
            ("CONSERVATIVE", n_conservative, 0, rate_conservative, False, "Fastest debt retirement; lowest cumulative interest."),
            ("BALANCED", n_balanced, 0, rate_balanced, True, "Recommended: Optimal balance of cashflow and repayment burden."),
            ("EXTENDED", n_extended, moratorium, rate_extended, False, f"Maximum repayment flexibility with {moratorium}m moratorium."),
        ]

        scenarios: List[RepaymentScenarioItem] = []
        for name, tenure_m, morat_m, annual_rate, is_rec, note in scenarios_def:
            emi, total_interest, total_repay = cls._calculate_amortization(
                principal=loan_principal,
                annual_rate=annual_rate,
                tenure_months=tenure_m,
            )

            projected_dti = round(
                ((debt_health.existing_monthly_emi + emi) / debt_health.monthly_income) * 100.0, 2
            )
            is_affordable = (emi <= debt_health.affordable_emi_cap) and (projected_dti <= 50.0)

            aff_notes = [note]
            if is_affordable:
                aff_notes.append(f"DTI ({projected_dti}%) satisfies safe underwriting ceiling (<= 50%).")
            else:
                if projected_dti > 50.0:
                    aff_notes.append(f"Caution: Total DTI ({projected_dti}%) exceeds 50% prudent ceiling.")
                if emi > debt_health.affordable_emi_cap:
                    aff_notes.append(f"Caution: Monthly installment exceeds calculated safe capacity of ₹{debt_health.affordable_emi_cap:,.2f}.")

            scenarios.append(
                RepaymentScenarioItem(
                    scenario_type=name,
                    tenure_months=tenure_m,
                    moratorium_months=morat_m,
                    annual_interest_rate_pct=round(annual_rate, 2),
                    is_market_linked=is_market_linked,
                    is_benchmark_assumption=is_benchmark_assumption,
                    rate_note=rate_note,
                    monthly_emi=emi,
                    total_interest_payable=total_interest,
                    total_repayment_amount=total_repay,
                    projected_dti_pct=projected_dti,
                    is_affordable=is_affordable,
                    is_recommended=is_rec,
                    affordability_notes=aff_notes,
                )
            )

        return scenarios

    @classmethod
    def _calculate_amortization(
        cls,
        principal: float,
        annual_rate: float,
        tenure_months: int,
    ) -> Tuple[float, float, float]:
        """Compute monthly compounding amortization EMI, total interest, and total repayment."""
        if tenure_months <= 0 or principal <= 0:
            return 0.0, 0.0, 0.0

        if annual_rate <= 0:
            # Zero-interest concession
            emi = round(principal / float(tenure_months), 2)
            total_repay = round(principal, 2)
            return emi, 0.0, total_repay

        r = (annual_rate / 100.0) / 12.0
        n = float(tenure_months)
        compound = math.pow(1.0 + r, n)
        emi = (principal * r * compound) / (compound - 1.0)
        emi_rounded = round(emi, 2)
        total_repay = round(emi_rounded * tenure_months, 2)
        total_interest = round(total_repay - principal, 2)

        return emi_rounded, max(0.0, total_interest), total_repay

    @classmethod
    def _build_non_financing_response(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
        request: FinancialStructuringRequest,
        warnings: List[str],
    ) -> FinancialStructuringResponse:
        """Construct response for non-credit / capability / platform programmes."""
        warnings.append(
            "Programme provides non-repayable capability, training, infrastructure, or platform support. Debt structuring is not applicable."
        )
        debt_health = cls._calculate_debt_health(
            monthly_income=request.monthly_income,
            monthly_expenses=request.monthly_expenses,
            existing_monthly_emi=request.existing_monthly_emi,
        )
        bounds = StatutoryFinancialBounds(
            collateral_required=False,
        )
        checklist = [
            "Valid Udyam Registration Certificate",
            "Business Identity / PAN Verification",
            "Application through official portal",
        ]
        return FinancialStructuringResponse(
            program_id=program.id,
            program_code=program.program_code,
            program_name=program.program_name,
            primary_type=program.primary_type,
            actionability_type=program.actionability_type,
            is_financing_applicable=False,
            assistance_summary=program.benefit_summary,
            capital_structure=None,
            debt_health=debt_health,
            loan_scenarios=[],
            financial_constraints=bounds,
            warnings=warnings,
            statutory_checklist=checklist,
        )

    @classmethod
    def _get_tenure_years_max(cls, program: GovernmentProgram, eval_prog: EvaluatableProgram) -> Optional[float]:
        if program.credit_details and program.credit_details.tenure_years is not None:
            return float(program.credit_details.tenure_years)
        if program.legacy_scheme and program.legacy_scheme.tenure_years is not None:
            return float(program.legacy_scheme.tenure_years)
        return None

    @classmethod
    def _get_moratorium_months(cls, program: GovernmentProgram, eval_prog: EvaluatableProgram) -> Optional[int]:
        if program.credit_details and program.credit_details.moratorium_months is not None:
            return int(program.credit_details.moratorium_months)
        if program.legacy_scheme and program.legacy_scheme.moratorium_months is not None:
            return int(program.legacy_scheme.moratorium_months)
        return None

    @classmethod
    def _get_collateral_required(cls, program: GovernmentProgram, eval_prog: EvaluatableProgram) -> bool:
        if program.credit_details and program.credit_details.collateral_required is not None:
            return bool(program.credit_details.collateral_required)
        if program.legacy_scheme and program.legacy_scheme.collateral_required is not None:
            return bool(program.legacy_scheme.collateral_required)
        return False

    @classmethod
    def _generate_checklist(
        cls,
        program: GovernmentProgram,
        eval_prog: EvaluatableProgram,
        capital_structure: CapitalStructureBreakdown,
    ) -> List[str]:
        """Generate mandatory documentary verification checklist."""
        checklist = [
            "Udyam Registration Certificate",
            "PAN and Aadhaar identity verification",
            "Bank account statements for the preceding 6 months",
        ]
        if capital_structure.subsidy_amount > 0:
            checklist.append("Detailed Project Report (DPR) with activity-wise cost estimates")
        if capital_structure.is_conditional_subsidy:
            checklist.append("Caste / Special Category Certificate for enhanced subsidy verification")
            checklist.append("Rural Area Certificate signed by authorized local administrative body")
        if cls._get_collateral_required(program, eval_prog):
            checklist.append("Property / collateral documentation and valuation report")
        else:
            checklist.append("Self-declaration for collateral-free sanction under Credit Guarantee trust")
        return checklist


# Global service singleton instance
financial_structuring_service = FinancialStructuringService()
