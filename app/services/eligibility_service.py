from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.models.program_models import GovernmentProgram
from app.repositories.scheme_repository import scheme_repository
from app.repositories.program_repository import program_repository
from app.schemas.eligibility import (
    UserProfile,
    EligibilityResult,
    EligibilityAssessmentResponse,
    FinancialConstraints,
    ProgramEligibilityResult,
    ProgramEligibilityAssessmentResponse,
)
from app.services.program_eligibility_adapter import (
    ProgramEligibilityAdapter,
    EvaluatableProgram,
    VALID_CANONICAL_SECTORS,
)


CANONICAL_SECTOR_MAP = {
    # Manufacturing
    "mfg": "MFG",
    "manufacturing": "MFG",
    # Services
    "srv": "SRV",
    "service": "SRV",
    "services": "SRV",
    # Trading / Retail
    "trd": "TRD",
    "trading": "TRD",
    "retail": "TRD",
    "trading / retail": "TRD",
    "trading/retail": "TRD",
    # Agriculture and Allied Activities
    "agr": "AGR",
    "agriculture": "AGR",
    "allied": "AGR",
    "agriculture and allied activities": "AGR",
    "agriculture & allied activities": "AGR",
    "agriculture & allied": "AGR",
    "agriculture and allied": "AGR",
    # Artisans and Traditional Crafts
    "art": "ART",
    "artisan": "ART",
    "artisans": "ART",
    "craft": "ART",
    "crafts": "ART",
    "traditional crafts": "ART",
    "artisans and traditional crafts": "ART",
    "artisans & traditional crafts": "ART",
}

CANONICAL_SECTOR_NAMES = {
    "MFG": "Manufacturing",
    "SRV": "Services",
    "TRD": "Trading / Retail",
    "AGR": "Agriculture and Allied Activities",
    "ART": "Artisans and Traditional Crafts",
}


class EligibilityService:
    """Deterministic, rule-based eligibility evaluation engine.
    
    Operates strictly on statutory criteria, verified rules, and thresholds.
    Completely isolated from ML ranking and LLM explanation services.
    """

    @classmethod
    def evaluate_scheme(cls, scheme: Scheme, profile: UserProfile) -> EligibilityResult:
        """Evaluate a single scheme against a user/business profile."""
        reasons: List[str] = []
        disqualifying_reasons: List[str] = []
        elig = scheme.eligibility_criteria

        # 1. Age Verification (prefer normalized criteria, fallback to scheme columns)
        min_age = elig.min_age if (elig and elig.min_age is not None) else scheme.min_age
        max_age = elig.max_age if (elig and elig.max_age is not None) else scheme.max_age

        if profile.age is not None:
            if min_age is not None and profile.age < min_age:
                disqualifying_reasons.append(
                    f"Applicant age ({profile.age}) is below minimum requirement of {min_age} years"
                )
            elif max_age is not None and profile.age > max_age:
                disqualifying_reasons.append(
                    f"Applicant age ({profile.age}) exceeds maximum ceiling of {max_age} years"
                )
            else:
                if min_age is not None or max_age is not None:
                    reasons.append(
                        f"Applicant age ({profile.age}) satisfies age range ({min_age or 'None'} to {max_age or 'No limit'})"
                    )

        # 2. Rural / Urban Location Check (Normalized SchemeEligibility criteria)
        if profile.is_rural is not None:
            if elig is not None:
                if profile.is_rural:
                    # Rural applicant
                    if elig.rural_eligible is False:
                        disqualifying_reasons.append(
                            "Scheme is designated exclusively for urban locations; rural applicants are not eligible"
                        )
                    else:
                        reasons.append("Location satisfies rural eligibility criteria")
                else:
                    # Urban applicant
                    if elig.urban_eligible is False or scheme.rural_only:
                        disqualifying_reasons.append(
                            "Scheme is exclusively reserved for rural enterprise locations; urban applicants are not eligible"
                        )
                    else:
                        reasons.append("Location satisfies urban eligibility criteria")
            else:
                # Fallback to legacy column
                if not profile.is_rural and scheme.rural_only:
                    disqualifying_reasons.append("Scheme is exclusively reserved for rural enterprise locations")
                else:
                    reasons.append("Location satisfies rural requirement")

        # 3. Annual / Family Income Check (Normalized criteria ceiling preferred)
        income_ceiling = None
        if elig is not None and elig.max_annual_income is not None:
            income_ceiling = float(elig.max_annual_income)
        elif scheme.income_limit is not None:
            income_ceiling = float(scheme.income_limit)

        if profile.annual_income is not None and income_ceiling is not None:
            if profile.annual_income > income_ceiling:
                disqualifying_reasons.append(
                    f"Annual income (₹{profile.annual_income:,.2f}) exceeds scheme ceiling of ₹{income_ceiling:,.2f}"
                )
            else:
                reasons.append(
                    f"Annual income (₹{profile.annual_income:,.2f}) is within eligible limit (₹{income_ceiling:,.2f})"
                )

        # 4. Business Stage Check (New vs Existing)
        if profile.is_new_business is not None:
            if profile.is_new_business:
                # Applicant is setting up a new business
                if scheme.id == 6 or "2nd loan" in scheme.name.lower() or "upgradation" in scheme.name.lower():
                    disqualifying_reasons.append("Scheme is available only for established existing enterprises")
                else:
                    stage_desc = "new business"
                    reasons.append(f"Enterprise stage ({stage_desc}) is eligible under scheme terms")
            else:
                # Applicant is an established existing business
                if scheme.new_business_only or (scheme.existing_business_allowed is False):
                    disqualifying_reasons.append("Scheme is available exclusively for setting up new enterprises")
                else:
                    stage_desc = "existing business"
                    reasons.append(f"Enterprise stage ({stage_desc}) is eligible under scheme terms")

        # 5. Project Cost Check
        if profile.project_cost is not None:
            if scheme.min_project_cost is not None and profile.project_cost < float(scheme.min_project_cost):
                disqualifying_reasons.append(
                    f"Project cost (₹{profile.project_cost:,.2f}) is below scheme threshold of ₹{float(scheme.min_project_cost):,.2f}"
                )
            elif scheme.max_project_cost is not None and profile.project_cost > float(scheme.max_project_cost):
                disqualifying_reasons.append(
                    f"Project cost (₹{profile.project_cost:,.2f}) exceeds scheme ceiling of ₹{float(scheme.max_project_cost):,.2f}"
                )
            else:
                reasons.append(f"Project cost (₹{profile.project_cost:,.2f}) is within eligible bounds")

        # 6. Requested Loan Amount Check
        if profile.requested_loan_amount is not None:
            if scheme.min_loan_amount is not None and profile.requested_loan_amount < float(scheme.min_loan_amount):
                disqualifying_reasons.append(
                    f"Requested loan (₹{profile.requested_loan_amount:,.2f}) is below minimum loan amount (₹{float(scheme.min_loan_amount):,.2f})"
                )
            elif scheme.max_loan_amount is not None and profile.requested_loan_amount > float(scheme.max_loan_amount):
                disqualifying_reasons.append(
                    f"Requested loan (₹{profile.requested_loan_amount:,.2f}) exceeds maximum loan amount (₹{float(scheme.max_loan_amount):,.2f})"
                )
            else:
                reasons.append(f"Requested loan (₹{profile.requested_loan_amount:,.2f}) is within acceptable range")

        # 7. State Applicability
        if profile.state and scheme.state:
            scheme_state = scheme.state.strip().lower()
            user_state = profile.state.strip().lower()
            if scheme_state != "all india" and user_state not in scheme_state:
                disqualifying_reasons.append(
                    f"Scheme is designated for {scheme.state}, but applicant is in {profile.state}"
                )
            else:
                if scheme_state == "all india":
                    reasons.append("Applicable across all States and Union Territories (Central Scheme)")
                else:
                    reasons.append(f"State location ({profile.state}) matches scheme coverage")

        # 8. Social Category Earmarking via Normalized Criteria (Option A Semantics)
        if elig is not None:
            # Check if scheme has SC exclusivity (sc_eligible is True and general_eligible is False)
            if elig.sc_eligible is True and elig.general_eligible is False:
                if profile.social_category:
                    cat = profile.social_category.strip().upper()
                    if cat in ["SC", "SCHEDULED CASTE"]:
                        reasons.append("Applicant satisfies Scheduled Caste (SC) statutory eligibility requirement")
                    else:
                        disqualifying_reasons.append(
                            f"Scheme is exclusively reserved for Scheduled Caste (SC) beneficiaries; applicant profile specifies {profile.social_category}"
                        )
                else:
                    disqualifying_reasons.append(
                        "Scheme is exclusively reserved for Scheduled Caste (SC) beneficiaries; applicant social category must be specified as SC"
                    )
            elif elig.sc_eligible is None and elig.general_eligible is None:
                # Option A: NULL indicates no statutory caste restriction (universal scheme)
                reasons.append("Scheme has no restrictive caste requirement (open to all categories)")
            elif elig.general_eligible is True and elig.sc_eligible is True:
                # Broad category inclusion (e.g. PMEGP)
                if profile.social_category:
                    reasons.append(f"Applicant social category ({profile.social_category}) is eligible under scheme terms")
                else:
                    reasons.append("Scheme has broad social category eligibility")
        else:
            # Fallback to legacy string check if criteria record is absent
            if scheme.target_group and "scheduled caste" in scheme.target_group.lower():
                if profile.social_category:
                    cat = profile.social_category.strip().upper()
                    if cat not in ["SC", "SCHEDULED CASTE"]:
                        disqualifying_reasons.append(
                            f"Scheme is dedicated to Scheduled Caste (SC) beneficiaries; applicant profile specifies {profile.social_category}"
                        )
                    else:
                        reasons.append("Applicant satisfies Scheduled Caste criteria")
                else:
                    disqualifying_reasons.append(
                        "Scheme is exclusively reserved for Scheduled Caste (SC) beneficiaries; applicant social category must be specified as SC"
                    )

        # 9. Scheme Specific Conditions
        # PM MUDRA Tarun Plus requires repaid Tarun loan
        if scheme.id == 4 or "tarun plus" in scheme.name.lower():
            if profile.previous_tarun_repaid is False:
                disqualifying_reasons.append("Requires prior availing and successful repayment of a MUDRA Tarun loan")
            elif profile.previous_tarun_repaid is True:
                reasons.append("Applicant has confirmed prior repayment of MUDRA Tarun loan")

        # PM Vishwakarma requires artisan trade
        if scheme.id == 7 or "vishwakarma" in scheme.name.lower():
            if profile.is_traditional_artisan is False:
                disqualifying_reasons.append("Exclusively for traditional artisans and craftspeople working with hands and tools")
            elif profile.is_traditional_artisan is True:
                reasons.append("Applicant is a recognized traditional artisan/craftsperson")

        # PM SVANidhi requires street vending
        if scheme.id == 8 or "svanidhi" in scheme.name.lower():
            if profile.is_street_vendor is False:
                disqualifying_reasons.append("Exclusively for urban street vendors and hawkers")
            elif profile.is_street_vendor is True:
                reasons.append("Applicant is an identified street vendor")

        # 10. Enterprise Sector Compatibility Check (Normalized Exact/Canonical Resolution)
        if profile.sector:
            applicant_input = profile.sector.strip().lower()
            applicant_code = CANONICAL_SECTOR_MAP.get(applicant_input)
            if applicant_code is None and profile.sector.strip().upper() in CANONICAL_SECTOR_NAMES:
                applicant_code = profile.sector.strip().upper()

            if applicant_code is None:
                disqualifying_reasons.append(
                    f"Applicant sector '{profile.sector}' is not a recognized eligible sector"
                )
            else:
                scheme_sector_codes = (
                    {s.sector_code for s in scheme.sectors_mapped}
                    if scheme.sectors_mapped
                    else set()
                )

                if scheme_sector_codes:
                    # Normalized sector mappings exist for this scheme
                    if applicant_code in scheme_sector_codes:
                        sec_name = CANONICAL_SECTOR_NAMES.get(applicant_code, applicant_code)
                        reasons.append(
                            f"Applicant sector ({profile.sector}) matches eligible canonical sector '{sec_name}' ({applicant_code})"
                        )
                    else:
                        allowed_codes = sorted(list(scheme_sector_codes))
                        allowed_names = [CANONICAL_SECTOR_NAMES.get(c, c) for c in allowed_codes]
                        disqualifying_reasons.append(
                            f"Applicant sector ({profile.sector} -> {applicant_code}) is not eligible for this scheme (eligible sectors: {', '.join(allowed_names)})"
                        )
                else:
                    # Schemes with NO normalized sector mappings (Schemes 8, 10, 12)
                    # DO NOT treat them as implicitly mapped to every applicant sector!
                    if scheme.id == 8 or "svanidhi" in scheme.name.lower():
                        # PM SVANidhi: designated exclusively for urban street vendors/hawkers
                        if applicant_code in ["MFG", "AGR"]:
                            disqualifying_reasons.append(
                                f"PM SVANidhi is designated for street vendors; industrial sector '{profile.sector}' is not compatible"
                            )
                        elif profile.is_street_vendor is True or (profile.business_type and any(k in profile.business_type.lower() for k in ["street vendor", "vendor", "hawker"])):
                            reasons.append("Applicant activity qualifies under street vendor criteria")
                        elif profile.is_street_vendor is False:
                            # Already disqualified in step 9
                            pass
                    elif scheme.id == 10:
                        # NSFDC AMY: Microcredit for small income-generating micro-enterprises
                        reasons.append(
                            "Scheme provides micro-finance credit under general micro-enterprise criteria rather than a sector-specific grant"
                        )
                    elif scheme.id == 12:
                        # NSFDC UNY: Education Loan Scheme for professional education/training
                        if applicant_code in ["MFG", "AGR", "TRD", "ART", "SRV"]:
                            disqualifying_reasons.append(
                                f"NSFDC Education Loan Scheme is designated for educational courses and training, not commercial {profile.sector} enterprise activities"
                            )
                        else:
                            reasons.append(
                                "Scheme provides educational loan assistance for eligible courses rather than commercial enterprise sector activities"
                            )
                    else:
                        reasons.append("Scheme has no restrictive sector reservation")

        is_eligible = len(disqualifying_reasons) == 0
        status = "Eligible" if is_eligible else "Ineligible"

        return EligibilityResult(
            scheme_id=scheme.id,
            scheme_name=scheme.name,
            scheme_type=scheme.scheme_type,
            is_eligible=is_eligible,
            status=status,
            reasons=reasons,
            disqualifying_reasons=disqualifying_reasons,
            application_url=scheme.application_url,
            benefit=scheme.benefit,
        )

    @classmethod
    def evaluate_all(
        cls,
        db: Session,
        profile: UserProfile,
    ) -> EligibilityAssessmentResponse:
        """Evaluate user profile against all active schemes in the database."""
        schemes = scheme_repository.get_all(db)
        eligible_schemes: List[EligibilityResult] = []
        ineligible_schemes: List[EligibilityResult] = []

        for s in schemes:
            result = cls.evaluate_scheme(s, profile)
            if result.is_eligible:
                eligible_schemes.append(result)
            else:
                ineligible_schemes.append(result)

        return EligibilityAssessmentResponse(
            total_evaluated=len(schemes),
            total_eligible=len(eligible_schemes),
            total_ineligible=len(ineligible_schemes),
            eligible_schemes=eligible_schemes,
            ineligible_schemes=ineligible_schemes,
        )

    @classmethod
    def evaluate_program(
        cls,
        program: GovernmentProgram,
        profile: UserProfile,
    ) -> ProgramEligibilityResult:
        """Evaluate a single government programme against user/business profile deterministically.
        
        Evaluates demographic criteria, canonical sectors, loan/project/guarantee financial bounds,
        enterprise stages, and identifies operational/institutional criteria.
        """
        ep: EvaluatableProgram = ProgramEligibilityAdapter.adapt(program)
        reasons: List[str] = []
        disqualifying_reasons: List[str] = []
        unverified_criteria: List[str] = []

        # 1. Age Verification
        if profile.age is not None:
            if ep.min_age is not None and profile.age < ep.min_age:
                disqualifying_reasons.append(
                    f"Applicant age ({profile.age}) is below statutory minimum requirement of {ep.min_age} years"
                )
            elif ep.max_age is not None and profile.age > ep.max_age:
                disqualifying_reasons.append(
                    f"Applicant age ({profile.age}) exceeds statutory maximum ceiling of {ep.max_age} years"
                )
            else:
                if ep.min_age is not None or ep.max_age is not None:
                    reasons.append(
                        f"Applicant age ({profile.age}) satisfies statutory age range ({ep.min_age or 'None'} to {ep.max_age or 'No limit'} years)"
                    )
        else:
            if ep.min_age is not None or ep.max_age is not None:
                unverified_criteria.append(
                    f"Statutory age requirement ({ep.min_age or 'None'} to {ep.max_age or 'No limit'} years) requires verification"
                )

        # 2. Gender Exclusivity & Eligibility
        if ep.female_eligible is True and ep.male_eligible is False:
            # Exclusively for women
            if profile.gender is not None:
                gen = profile.gender.strip().lower()
                if gen in ["female", "woman", "women"]:
                    reasons.append("Applicant satisfies target gender criteria (Exclusively for women entrepreneurs)")
                else:
                    disqualifying_reasons.append(
                        f"Programme is exclusively designated for female beneficiaries; applicant profile specifies {profile.gender}"
                    )
            else:
                disqualifying_reasons.append(
                    "Programme is exclusively designated for female beneficiaries; applicant gender must be specified as Female"
                )
        elif ep.male_eligible is True and ep.female_eligible is True:
            if profile.gender is not None:
                reasons.append(f"Applicant gender ({profile.gender}) is eligible under programme terms")

        # 3. Social Category Earmarking & Statutory Reservations
        if ep.general_eligible is False:
            allowed_categories = []
            if ep.sc_eligible is True:
                allowed_categories.append("SC")
            if ep.st_eligible is True:
                allowed_categories.append("ST")
            if ep.obc_eligible is True:
                allowed_categories.append("OBC")
            if ep.minority_eligible is True:
                allowed_categories.append("MINORITY")

            cat_label = "/".join(allowed_categories) if allowed_categories else "Reserved"
            if profile.social_category is not None:
                user_cat = profile.social_category.strip().upper()
                if user_cat in ["SC", "SCHEDULED CASTE", "SCHEDULED CASTES"]:
                    norm_cat = "SC"
                elif user_cat in ["ST", "SCHEDULED TRIBE", "SCHEDULED TRIBES"]:
                    norm_cat = "ST"
                elif user_cat in ["OBC", "OTHER BACKWARD CLASS", "OTHER BACKWARD CLASSES", "BACKWARD CLASS", "BACKWARD CLASSES"]:
                    norm_cat = "OBC"
                elif user_cat in ["MINORITY", "MINORITY COMMUNITY", "MINORITY COMMUNITIES"]:
                    norm_cat = "MINORITY"
                else:
                    norm_cat = user_cat

                if norm_cat in allowed_categories:
                    reasons.append(f"Applicant satisfies statutory social category requirement ({cat_label})")
                else:
                    disqualifying_reasons.append(
                        f"Programme is exclusively designated for {cat_label} beneficiaries; applicant profile specifies {profile.social_category}"
                    )
            else:
                disqualifying_reasons.append(
                    f"Programme is exclusively designated for {cat_label} beneficiaries; applicant social category must be specified as {cat_label}"
                )
        elif ep.general_eligible is True or (ep.general_eligible is None and ep.sc_eligible is None):
            if profile.social_category is not None:
                reasons.append(f"Applicant social category ({profile.social_category}) is eligible under programme terms")
            else:
                reasons.append("Programme has broad social category eligibility (open to all categories)")

        # 4. Rural / Urban Location Check
        if profile.is_rural is not None:
            if profile.is_rural:
                # Rural applicant
                if ep.rural_eligible is False:
                    disqualifying_reasons.append(
                        "Programme is designated exclusively for urban locations; rural applicants are not eligible"
                    )
                else:
                    reasons.append("Location satisfies rural eligibility criteria")
            else:
                # Urban applicant
                if ep.urban_eligible is False:
                    disqualifying_reasons.append(
                        "Programme is exclusively reserved for rural enterprise locations; urban applicants are not eligible"
                    )
                else:
                    reasons.append("Location satisfies urban eligibility criteria")
        else:
            if ep.rural_eligible is True and ep.urban_eligible is False:
                unverified_criteria.append("Statutory location requirement (exclusively rural) requires verification")
            elif ep.rural_eligible is False and ep.urban_eligible is True:
                unverified_criteria.append("Statutory location requirement (exclusively urban) requires verification")

        # 5. Annual Income Ceiling
        if ep.max_annual_income is not None:
            if profile.annual_income is not None:
                if profile.annual_income > ep.max_annual_income:
                    disqualifying_reasons.append(
                        f"Annual income (₹{profile.annual_income:,.2f}) exceeds programme ceiling of ₹{ep.max_annual_income:,.2f}"
                    )
                else:
                    reasons.append(
                        f"Annual income (₹{profile.annual_income:,.2f}) is within eligible limit (₹{ep.max_annual_income:,.2f})"
                    )
            else:
                unverified_criteria.append(
                    f"Annual income verification required (Statutory ceiling: ₹{ep.max_annual_income:,.2f})"
                )

        # 6. PwD & Ex-Servicemen
        if profile.is_differently_abled is True and ep.pwd_eligible is False:
            disqualifying_reasons.append("Programme does not cover differently-abled category concessions")
        if profile.is_ex_serviceman is True and ep.ex_servicemen_eligible is False:
            disqualifying_reasons.append("Programme does not cover ex-servicemen category concessions")

        # 7. Financial Constraints Check
        # 7a. Loan / Credit Amount Check (Credit and Guarantee details)
        if profile.requested_loan_amount is not None:
            if ep.min_loan_amount is not None and profile.requested_loan_amount < ep.min_loan_amount:
                disqualifying_reasons.append(
                    f"Requested loan (₹{profile.requested_loan_amount:,.2f}) is below minimum loan amount (₹{ep.min_loan_amount:,.2f})"
                )
            elif ep.max_loan_amount is not None and profile.requested_loan_amount > ep.max_loan_amount:
                disqualifying_reasons.append(
                    f"Requested loan (₹{profile.requested_loan_amount:,.2f}) exceeds maximum loan amount (₹{ep.max_loan_amount:,.2f})"
                )
            elif ep.min_loan_amount is not None or ep.max_loan_amount is not None:
                reasons.append(f"Requested loan (₹{profile.requested_loan_amount:,.2f}) is within acceptable range")

            # Credit Guarantee ceiling
            if ep.max_guarantee_limit is not None:
                if profile.requested_loan_amount > ep.max_guarantee_limit:
                    disqualifying_reasons.append(
                        f"Requested credit (₹{profile.requested_loan_amount:,.2f}) exceeds guarantee ceiling of ₹{ep.max_guarantee_limit:,.2f}"
                    )
                else:
                    reasons.append(
                        f"Requested credit is within credit guarantee ceiling (up to ₹{ep.max_guarantee_limit:,.2f})"
                    )

        # 7b. Project Cost Check (Subsidy / Capital Assistance)
        if profile.project_cost is not None:
            if ep.min_project_cost is not None and profile.project_cost < ep.min_project_cost:
                disqualifying_reasons.append(
                    f"Project cost (₹{profile.project_cost:,.2f}) is below programme threshold of ₹{ep.min_project_cost:,.2f}"
                )
            elif ep.max_project_cost is not None and profile.project_cost > ep.max_project_cost:
                disqualifying_reasons.append(
                    f"Project cost (₹{profile.project_cost:,.2f}) exceeds programme ceiling of ₹{ep.max_project_cost:,.2f}"
                )
            elif ep.min_project_cost is not None or ep.max_project_cost is not None:
                reasons.append(f"Project cost (₹{profile.project_cost:,.2f}) is within eligible bounds")

        # 8. Business Stage Check
        if profile.is_new_business is not None:
            if profile.is_new_business:
                if ep.program_code in ["PMEGP_UPGRADATION", "CGSSD"] or "upgradation" in ep.program_name.lower():
                    disqualifying_reasons.append("Programme is available only for established existing enterprises seeking upgradation")
                else:
                    reasons.append("Enterprise stage (new business) is eligible under programme terms")
            else:
                if ep.program_code == "STANDUP_INDIA":
                    disqualifying_reasons.append("Stand-Up India is exclusively for greenfield (new) enterprises")
                elif ep.new_business_only or (ep.existing_business_allowed is False):
                    disqualifying_reasons.append("Programme is available exclusively for setting up new enterprises")
                else:
                    reasons.append("Enterprise stage (existing business) is eligible under programme terms")

        # 9. Enterprise Sector Compatibility Check (Canonical Sector Codes)
        if profile.sector:
            applicant_input = profile.sector.strip().lower()
            applicant_code = CANONICAL_SECTOR_MAP.get(applicant_input)
            if applicant_code is None and profile.sector.strip().upper() in CANONICAL_SECTOR_NAMES:
                applicant_code = profile.sector.strip().upper()

            if applicant_code is None:
                disqualifying_reasons.append(
                    f"Applicant sector '{profile.sector}' is not a recognized eligible sector"
                )
            else:
                if ep.sector_codes:
                    # Normalized sector mappings exist for this programme
                    if applicant_code in ep.sector_codes:
                        sec_name = CANONICAL_SECTOR_NAMES.get(applicant_code, applicant_code)
                        reasons.append(
                            f"Applicant sector ({profile.sector}) matches eligible canonical sector '{sec_name}' ({applicant_code})"
                        )
                    else:
                        allowed_codes = sorted(list(ep.sector_codes))
                        allowed_names = [CANONICAL_SECTOR_NAMES.get(c, c) for c in allowed_codes]
                        disqualifying_reasons.append(
                            f"Applicant sector ({profile.sector} -> {applicant_code}) is not eligible for this programme (eligible sectors: {', '.join(allowed_names)})"
                        )
                else:
                    # Programmes with NO normalized sector mappings in DB
                    if ep.program_code == "PM_SVANIDHI" or ep.legacy_scheme_id == 8:
                        if applicant_code in ["MFG", "AGR"]:
                            disqualifying_reasons.append(
                                f"PM SVANidhi is designated for street vendors; industrial sector '{profile.sector}' is not compatible"
                            )
                        elif profile.is_street_vendor is True or (profile.business_type and any(k in profile.business_type.lower() for k in ["street vendor", "vendor", "hawker"])):
                            reasons.append("Applicant activity qualifies under street vendor criteria")
                    elif ep.program_code == "NSFDC_AMY" or ep.legacy_scheme_id == 10:
                        reasons.append(
                            "Scheme provides micro-finance credit under general micro-enterprise criteria rather than a sector-specific grant"
                        )
                    elif ep.program_code == "NSFDC_UNY" or ep.legacy_scheme_id == 12:
                        if applicant_code in ["MFG", "AGR", "TRD", "ART", "SRV"]:
                            disqualifying_reasons.append(
                                f"NSFDC Education Loan Scheme is designated for educational courses and training, not commercial {profile.sector} enterprise activities"
                            )
                        else:
                            reasons.append(
                                "Scheme provides educational loan assistance for eligible courses rather than commercial enterprise sector activities"
                            )
                    elif ep.actionability_type in ["PLATFORM", "FRAMEWORK"]:
                        reasons.append(
                            f"Programme is an operational {ep.actionability_type.lower()} accessible across multiple sectors"
                        )
                    else:
                        reasons.append("Programme has no restrictive sector reservation")

        # 10. Specific Programme Conditions
        if ep.program_code in ["PM_MUDRA_TARUN_PLUS"] or ep.legacy_scheme_id == 4:
            if profile.previous_tarun_repaid is False:
                disqualifying_reasons.append("Requires prior availing and successful repayment of a MUDRA Tarun loan")
            elif profile.previous_tarun_repaid is True:
                reasons.append("Applicant has confirmed prior repayment of MUDRA Tarun loan")
            else:
                unverified_criteria.append("Prior availing and successful repayment of a MUDRA Tarun loan requires verification")

        if ep.program_code in ["PM_VISHWAKARMA"] or ep.legacy_scheme_id == 7:
            if profile.is_traditional_artisan is False:
                disqualifying_reasons.append("Exclusively for traditional artisans and craftspeople working with hands and tools")
            elif profile.is_traditional_artisan is True:
                reasons.append("Applicant is a recognized traditional artisan/craftsperson")
            else:
                unverified_criteria.append("Recognition as a traditional artisan or craftsperson requires verification")

        if ep.program_code in ["PM_SVANIDHI"] or ep.legacy_scheme_id == 8:
            if profile.is_street_vendor is False:
                disqualifying_reasons.append("Exclusively for urban street vendors and hawkers")
            elif profile.is_street_vendor is True:
                reasons.append("Applicant is an identified street vendor")
            else:
                unverified_criteria.append("Street vendor identification or Certificate of Vending requires verification")

        # 11. Operational & Institutional Criteria from Authoritative Database Notes
        if ep.notes:
            notes_lower = ep.notes.lower()
            if "sma-2 or npa" in notes_lower:
                unverified_criteria.append("Operational MSME account must be classified as SMA-2 or NPA by lending institution")
            if "dpiit" in notes_lower:
                unverified_criteria.append("DPIIT startup recognition required")
            if "drug manufacturing license" in notes_lower:
                unverified_criteria.append("Valid drug manufacturing license required")
            if "handloom weaver pehchan card" in notes_lower:
                unverified_criteria.append("Valid Handloom Weaver Pehchan Card required")
            if "nabl" in notes_lower:
                unverified_criteria.append("Testing must be performed at NABL-accredited or government laboratories")
            if "udyam" in notes_lower and "valid udyam" in notes_lower:
                unverified_criteria.append("Valid Udyam Registration required")
            if "iec" in notes_lower and "valid iec" in notes_lower:
                unverified_criteria.append("Valid Importer-Exporter Code (IEC) required")

        # 12. Final Status Determination
        if len(disqualifying_reasons) > 0:
            is_eligible = False
            status = "Ineligible"
        elif len(unverified_criteria) > 0:
            is_eligible = True
            status = "Partially Verified"
        else:
            is_eligible = True
            status = "Eligible"

        return ProgramEligibilityResult(
            program_id=ep.program_id,
            program_code=ep.program_code,
            program_name=ep.program_name,
            primary_type=ep.primary_type,
            actionability_type=ep.actionability_type,
            is_eligible=is_eligible,
            status=status,
            reasons=reasons,
            disqualifying_reasons=disqualifying_reasons,
            unverified_criteria=unverified_criteria,
            financial_constraints=ep.to_financial_constraints(),
            official_portal_url=ep.official_portal_url,
            benefit_summary=ep.benefit_summary,
        )

    @classmethod
    def evaluate_all_programs(
        cls,
        db: Session,
        profile: UserProfile,
    ) -> ProgramEligibilityAssessmentResponse:
        """Evaluate user profile against all government programmes deterministically."""
        programs = program_repository.get_all(db)
        eligible_programs: List[ProgramEligibilityResult] = []
        ineligible_programs: List[ProgramEligibilityResult] = []
        partially_verified_programs: List[ProgramEligibilityResult] = []

        directly_recommendable_count = 0
        component_recommendable_count = 0
        platform_count = 0
        framework_count = 0

        for p in programs:
            # Actionability aggregation across all loaded programmes
            act_type = (p.actionability_type or "").upper()
            if act_type == "DIRECTLY_RECOMMENDABLE":
                directly_recommendable_count += 1
            elif act_type == "COMPONENT_RECOMMENDABLE":
                component_recommendable_count += 1
            elif act_type == "PLATFORM":
                platform_count += 1
            elif act_type == "FRAMEWORK":
                framework_count += 1

            result = cls.evaluate_program(p, profile)
            if result.status == "Eligible":
                eligible_programs.append(result)
            elif result.status == "Partially Verified":
                partially_verified_programs.append(result)
            else:
                ineligible_programs.append(result)

        return ProgramEligibilityAssessmentResponse(
            total_evaluated=len(programs),
            total_eligible=len(eligible_programs),
            total_ineligible=len(ineligible_programs),
            total_partially_verified=len(partially_verified_programs),
            eligible_programs=eligible_programs,
            ineligible_programs=ineligible_programs,
            partially_verified_programs=partially_verified_programs,
            directly_recommendable_count=directly_recommendable_count,
            component_recommendable_count=component_recommendable_count,
            platform_count=platform_count,
            framework_count=framework_count,
        )


eligibility_service = EligibilityService()

