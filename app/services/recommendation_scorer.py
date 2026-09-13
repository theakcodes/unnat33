"""
app/services/recommendation_scorer.py

Transparent, explainable 100-point recommendation scoring engine for MSME government programmes.

Ground rules:
1. Operates strictly downstream of the deterministic statutory eligibility hard-gate.
2. Zero ML, zero LLM, zero external API calls.
3. 6 independent, explainable scoring components summing to exactly 100.0 points maximum:
   - Eligibility Confidence / Status: 0 to 20 pts
   - Financial Fit & Subsidies: 0 to 25 pts
   - Sector / Activity Fit: 0 to 20 pts
   - Programme Actionability: 0 to 15 pts
   - Target Beneficiary & Stage Fit: 0 to 10 pts
   - District Market Context Signal: 0 to 10 pts
4. Full traceability: Every positive score contributor generates a human-readable recommendation driver,
   and every operational requirement or financial caveat generates a cautionary note.
"""

from typing import Optional, List, Tuple
from app.schemas.eligibility import UserProfile
from app.schemas.district_msme import DistrictMarketContext
from app.schemas.recommendation import ScoringBreakdown, ProgramRecommendationItem
from app.services.program_eligibility_adapter import EvaluatableProgram
from app.services.eligibility_service import CANONICAL_SECTOR_MAP, CANONICAL_SECTOR_NAMES


class RecommendationScorer:
    """Deterministic, transparent 100-point scoring engine."""

    @classmethod
    def score_eligibility_confidence(
        cls,
        status: str,
        unverified_criteria: List[str],
    ) -> Tuple[float, List[str], List[str]]:
        """Evaluate statutory eligibility confidence (0 to 20 pts).
        
        - 'Eligible': 20.0 pts (Full statutory verification confirmed).
        - 'Partially Verified': 12.0 pts (8.0 pt deduction for unverified operational criteria).
        - Ineligible candidates are gated out prior to scoring (0.0 pts fallback).
        """
        drivers: List[str] = []
        notes: List[str] = []

        if status == "Eligible":
            score = 20.0
            drivers.append("Statutory eligibility fully confirmed with zero unverified conditions (+20.0 pts)")
        elif status == "Partially Verified":
            score = 12.0
            drivers.append("Meets statutory demographic and financial criteria (+12.0 pts)")
            notes.append("Partially Verified: 8.0 pt deduction due to unverified operational/institutional criteria")
            for c in unverified_criteria:
                notes.append(f"Requires external verification: {c}")
        else:
            score = 0.0
            notes.append("Programme fails statutory eligibility criteria")

        return round(score, 2), drivers, notes

    @classmethod
    def score_financial_fit(
        cls,
        eval_prog: EvaluatableProgram,
        target_amount: Optional[float],
    ) -> Tuple[float, List[str], List[str]]:
        """Evaluate financial sweet-spot and capital/guarantee relief (0 to 25 pts).
        
        - Sub-component A: Financing Sweet-Spot Alignment (0 to 15 pts)
        - Sub-component B: Capital Subsidy / Credit Guarantee / Interest Concession (0 to 10 pts)
        """
        drivers: List[str] = []
        notes: List[str] = []

        # Resolve programme financial bounds
        min_bound = eval_prog.min_loan_amount if eval_prog.min_loan_amount is not None else eval_prog.min_project_cost
        max_bound = eval_prog.max_loan_amount if eval_prog.max_loan_amount is not None else eval_prog.max_project_cost

        # Check if program provides capital / financing components
        has_financial_components = any([
            min_bound is not None,
            max_bound is not None,
            eval_prog.max_subsidy_amount is not None,
            eval_prog.subsidy_percentage is not None,
            eval_prog.max_guarantee_limit is not None,
            eval_prog.guarantee_coverage_pct is not None,
        ])

        # --- Sub-component A: Financing Sweet-Spot (0 to 15 pts) ---
        if target_amount is None or target_amount <= 0:
            sweet_score = 7.5
            drivers.append("Target financing need not specified; baseline financial fit applied (+7.5 pts)")
        else:
            if min_bound is None and max_bound is None:
                if not has_financial_components:
                    # Non-capital / capability / training programme
                    sweet_score = 5.0
                    drivers.append("Non-capital / capability programme: baseline financial fit applied for capital request (+5.0 pts)")
                    notes.append("Programme provides capability, training, or enablement rather than direct capital/credit financing")
                else:
                    # Open assistance with guarantee or subsidy without restrictive loan cap
                    sweet_score = 10.0
                    drivers.append("Flexible assistance without restrictive statutory loan caps (+10.0 pts)")
            elif min_bound is not None and max_bound is not None:
                if min_bound <= target_amount <= max_bound:
                    sweet_score = 15.0
                    drivers.append(
                        f"Target financing need (₹{target_amount:,.0f}) is within statutory bounds "
                        f"(₹{min_bound:,.0f} to ₹{max_bound:,.0f}) (+15.0 pts)"
                    )
                elif target_amount < min_bound:
                    ratio = target_amount / min_bound if min_bound > 0 else 0.5
                    sweet_score = max(0.0, round(15.0 * ratio, 2))
                    notes.append(f"Target amount (₹{target_amount:,.0f}) is below minimum assistance threshold of ₹{min_bound:,.0f}")
                else:  # target_amount > max_bound
                    ratio = max_bound / target_amount if target_amount > 0 else 0.5
                    sweet_score = max(0.0, round(15.0 * ratio, 2))
                    notes.append(f"Target amount (₹{target_amount:,.0f}) exceeds maximum financing ceiling of ₹{max_bound:,.0f}")
            elif max_bound is not None:
                if target_amount <= max_bound:
                    sweet_score = 15.0
                    drivers.append(
                        f"Target financing need (₹{target_amount:,.0f}) is within maximum ceiling of ₹{max_bound:,.0f} (+15.0 pts)"
                    )
                else:
                    ratio = max_bound / target_amount if target_amount > 0 else 0.5
                    sweet_score = max(0.0, round(15.0 * ratio, 2))
                    notes.append(f"Target amount (₹{target_amount:,.0f}) exceeds statutory ceiling of ₹{max_bound:,.0f}")
            elif min_bound is not None:
                if target_amount >= min_bound:
                    sweet_score = 15.0
                    drivers.append(
                        f"Target financing need (₹{target_amount:,.0f}) satisfies minimum entry threshold of ₹{min_bound:,.0f} (+15.0 pts)"
                    )
                else:
                    ratio = target_amount / min_bound if min_bound > 0 else 0.5
                    sweet_score = max(0.0, round(15.0 * ratio, 2))
                    notes.append(f"Target amount (₹{target_amount:,.0f}) is below entry threshold of ₹{min_bound:,.0f}")
            else:
                sweet_score = 7.5

        # --- Sub-component B: Capital Subsidy / Guarantee / Concession (0 to 10 pts) ---
        benefit_score = 0.0
        # 1. Capital Subsidy
        if eval_prog.subsidy_percentage is not None and eval_prog.subsidy_percentage >= 25.0:
            benefit_score = max(benefit_score, 10.0)
            drivers.append(f"High upfront capital subsidy of {eval_prog.subsidy_percentage}% available (+10.0 pts)")
        elif eval_prog.max_subsidy_amount is not None and eval_prog.max_subsidy_amount >= 500000:
            benefit_score = max(benefit_score, 10.0)
            drivers.append(f"Substantial capital subsidy cap of ₹{eval_prog.max_subsidy_amount:,.0f} (+10.0 pts)")
        elif eval_prog.subsidy_percentage is not None and eval_prog.subsidy_percentage > 0:
            benefit_score = max(benefit_score, 7.0)
            drivers.append(f"Capital subsidy of {eval_prog.subsidy_percentage}% available (+7.0 pts)")

        # 2. Credit Guarantee
        if eval_prog.guarantee_coverage_pct is not None and eval_prog.guarantee_coverage_pct >= 75.0:
            benefit_score = max(benefit_score, 10.0)
            drivers.append(f"Extensive credit guarantee coverage of {eval_prog.guarantee_coverage_pct}% minimizing collateral risk (+10.0 pts)")
        elif eval_prog.guarantee_coverage_pct is not None and eval_prog.guarantee_coverage_pct > 0:
            benefit_score = max(benefit_score, 7.0)
            drivers.append(f"Credit guarantee coverage of {eval_prog.guarantee_coverage_pct}% available (+7.0 pts)")

        # 3. Interest Concession
        if eval_prog.interest_rate_min is not None and eval_prog.interest_rate_min <= 7.0:
            benefit_score = max(benefit_score, 6.0)
            drivers.append(f"Concessional interest rate structure starting at {eval_prog.interest_rate_min}% (+6.0 pts)")

        total_financial = min(25.0, sweet_score + benefit_score)
        return round(total_financial, 2), drivers, notes

    @classmethod
    def score_sector_fit(
        cls,
        eval_prog: EvaluatableProgram,
        profile: UserProfile,
    ) -> Tuple[float, List[str]]:
        """Evaluate canonical sector and sub-sector/activity domain compatibility (0 to 20 pts).
        
        - Exact canonical sector match without domain clash: 20.0 pts.
        - Specialized ministry / sector with peripheral alignment (no sub-sector specified): 10.0 pts.
        - Sub-sector domain mismatch (e.g. IT service vs agricultural machinery): 5.0 pts.
        - Universal / sector-agnostic programme: 14.0 pts.
        - No sector specified in applicant profile: 10.0 to 15.0 pts neutral.
        """
        drivers: List[str] = []

        # Domain classification keywords
        AGRI_KEYWORDS = {"agri", "farm", "crop", "harvest", "horticulture", "dairy", "machinery", "tractor", "farmer", "fishery", "livestock"}
        TECH_KEYWORDS = {"it", "software", "tech", "consult", "consulting", "digital", "bpo", "cyber", "web", "data", "cloud", "saas"}
        FOOD_KEYWORDS = {"food", "beverage", "bakery", "grain", "spice", "pickle", "processing", "edible", "agro"}
        TEXTILE_KEYWORDS = {"textile", "weaver", "weaving", "handloom", "garment", "apparel", "fabric", "cloth", "yarn"}

        bt_text = (profile.business_type or "").lower()
        has_tech_bt = any(kw in bt_text for kw in TECH_KEYWORDS)
        has_agri_bt = any(kw in bt_text for kw in AGRI_KEYWORDS)
        has_food_bt = any(kw in bt_text for kw in FOOD_KEYWORDS)
        has_textile_bt = any(kw in bt_text for kw in TEXTILE_KEYWORDS)

        # Check if program has specialized domain
        ministry = (eval_prog.owning_ministry or "").lower()
        is_agri_domain = "agriculture" in ministry or "farmers welfare" in ministry or "fisheries" in ministry or "AGR" in eval_prog.sector_codes
        is_food_domain = "food processing" in ministry
        is_textile_domain = "textile" in ministry or "handloom" in ministry

        if profile.sector:
            canonical_code = CANONICAL_SECTOR_MAP.get(profile.sector.strip().lower())
            if canonical_code:
                if canonical_code in eval_prog.sector_codes:
                    # Check for cross-sector / domain specialization clash
                    if is_agri_domain and canonical_code == "SRV":
                        if has_tech_bt:
                            score = 5.0
                            drivers.append(
                                "Cross-domain limitation: Programme operates under agricultural/farm mandate; applicant activity is IT/consulting (+5.0 pts)"
                            )
                        elif not has_agri_bt and profile.business_type:
                            score = 5.0
                            drivers.append(
                                f"Specialized domain: Programme requires agricultural/farm operations (+5.0 pts)"
                            )
                        elif not has_agri_bt:
                            # Generic services without agricultural activity specified
                            score = 10.0
                            drivers.append(
                                f"Peripheral sector alignment: Agricultural/farm allied service mandate under {eval_prog.owning_ministry or 'Agriculture'} (+10.0 pts)"
                            )
                        else:
                            score = 20.0
                            drivers.append("Exact match: Agricultural allied service and custom operations (+20.0 pts)")
                    elif is_food_domain and canonical_code in ["MFG", "SRV"]:
                        if has_tech_bt:
                            score = 5.0
                            drivers.append(
                                "Cross-domain limitation: Programme requires food processing activities; applicant activity is IT/consulting (+5.0 pts)"
                            )
                        elif not has_food_bt and profile.business_type:
                            score = 7.5
                            drivers.append(
                                "Specialized mandate: Food processing enterprise requirement (+7.5 pts)"
                            )
                        else:
                            score = 20.0
                            drivers.append("Exact canonical sector match for Food Processing (+20.0 pts)")
                    elif is_textile_domain and canonical_code in ["MFG", "SRV"]:
                        if has_tech_bt:
                            score = 5.0
                            drivers.append(
                                "Cross-domain limitation: Programme focuses on textile/weaver craft; applicant activity is IT/consulting (+5.0 pts)"
                            )
                        elif not has_textile_bt and profile.business_type:
                            score = 7.5
                            drivers.append(
                                "Specialized mandate: Textile/weaving enterprise requirement (+7.5 pts)"
                            )
                        else:
                            score = 20.0
                            drivers.append("Exact canonical sector match for Textile / Handloom (+20.0 pts)")
                    else:
                        sector_name = CANONICAL_SECTOR_NAMES.get(canonical_code, canonical_code)
                        score = 20.0
                        drivers.append(f"Exact canonical sector match for {sector_name} (+20.0 pts)")
                elif len(eval_prog.sector_codes) == 0:
                    score = 14.0
                    drivers.append("Universal sector-agnostic programme applicable across all MSME activities (+14.0 pts)")
                else:
                    score = 5.0
                    drivers.append(f"Applicant sector ({profile.sector}) is broader than programme focus (+5.0 pts)")
            else:
                if len(eval_prog.sector_codes) == 0:
                    score = 14.0
                    drivers.append("Universal sector-agnostic programme (+14.0 pts)")
                else:
                    score = 10.0
                    drivers.append("General sector alignment (+10.0 pts)")
        else:
            if len(eval_prog.sector_codes) == 0:
                score = 15.0
                drivers.append("Universal MSME assistance applicable without sector restriction (+15.0 pts)")
            else:
                score = 10.0
                drivers.append("Open eligibility across designated priority sectors (+10.0 pts)")

        return round(score, 2), drivers

    @classmethod
    def score_actionability(
        cls,
        eval_prog: EvaluatableProgram,
    ) -> Tuple[float, List[str]]:
        """Evaluate programme actionability level (0 to 15 pts).
        
        - DIRECTLY_RECOMMENDABLE: 15.0 pts (immediate direct MSME application).
        - COMPONENT_RECOMMENDABLE: 10.0 pts (actionable via implementing partner / sub-component).
        - PLATFORM: 6.0 pts (statutory registration / digital enablement).
        - FRAMEWORK: 3.0 pts (guideline / institutional framework).
        """
        drivers: List[str] = []
        act_type = (eval_prog.actionability_type or "").upper()

        if act_type == "DIRECTLY_RECOMMENDABLE":
            score = 15.0
            drivers.append("Directly actionable programme for immediate MSME application (+15.0 pts)")
        elif act_type == "COMPONENT_RECOMMENDABLE":
            score = 10.0
            drivers.append("Component of larger national scheme; actionable via nodal implementing agency (+10.0 pts)")
        elif act_type == "PLATFORM":
            score = 6.0
            drivers.append("Statutory digital enablement / registration platform (+6.0 pts)")
        elif act_type == "FRAMEWORK":
            score = 3.0
            drivers.append("Policy guideline / institutional framework (+3.0 pts)")
        else:
            score = 5.0
            drivers.append(f"Assistance classified under {eval_prog.actionability_type or 'General'} (+5.0 pts)")

        return round(score, 2), drivers

    @classmethod
    def score_beneficiary_and_stage(
        cls,
        eval_prog: EvaluatableProgram,
        profile: UserProfile,
    ) -> Tuple[float, List[str]]:
        """Evaluate target beneficiary earmarking and business stage compatibility (0 to 10 pts).
        
        - Demographic Mandate (0 to 5 pts): Earmarked focus for women, SC/ST, artisans, street vendors.
        - Business Lifecycle Stage (0 to 5 pts): Greenfield (new) vs Brownfield (existing/expansion).
        """
        drivers: List[str] = []

        # --- Demographic mandate (0 to 5 pts) ---
        dem_score = 3.5

        # Check gender priority
        if profile.gender and profile.gender.lower() == "female":
            if (eval_prog.target_gender and eval_prog.target_gender.upper() == "FEMALE") or (
                eval_prog.female_eligible and not eval_prog.male_eligible
            ):
                dem_score = 5.0
                drivers.append("Exclusive statutory mandate dedicated to women entrepreneurs (+5.0 pts)")
            elif eval_prog.target_gender and "FEMALE" in eval_prog.target_gender.upper():
                dem_score = 5.0
                drivers.append("Statutory priority alignment for women-led enterprises (+5.0 pts)")

        # Check social category priority
        if profile.social_category:
            cat = profile.social_category.upper()
            target_cats = [c.strip().upper() for c in (eval_prog.target_social_categories or "").split(",") if c.strip()]
            if cat in target_cats or (cat in ["SC", "ST"] and eval_prog.sc_eligible and not eval_prog.general_eligible):
                dem_score = 5.0
                drivers.append(f"Statutory priority alignment for {cat} entrepreneurs (+5.0 pts)")

        # Check artisan / craftsperson priority
        if profile.is_traditional_artisan:
            if eval_prog.artisan_mandate or "ART" in eval_prog.sector_codes:
                dem_score = 5.0
                drivers.append("Direct statutory mandate for recognized traditional artisans and craftspersons (+5.0 pts)")

        # Check street vendor priority
        if profile.is_street_vendor:
            if eval_prog.street_vendor_mandate:
                dem_score = 5.0
                drivers.append("Direct statutory mandate for urban street vendors and micro-hawkers (+5.0 pts)")

        # Check startup priority
        if eval_prog.startup_mandate and profile.is_new_business is True:
            dem_score = 5.0
            drivers.append("Direct statutory mandate for early-stage and innovative startups (+5.0 pts)")

        # --- Lifecycle stage (0 to 5 pts) ---
        stage_score = 3.5
        if profile.is_new_business is True:
            if eval_prog.new_business_only is True:
                stage_score = 5.0
                drivers.append("Greenfield mandate: Specifically designated for new enterprise creation (+5.0 pts)")
            elif eval_prog.existing_business_allowed is False:
                stage_score = 5.0
                drivers.append("Prioritizes greenfield venture establishment (+5.0 pts)")
            else:
                stage_score = 4.5
                drivers.append("Permits greenfield / new business establishment (+4.5 pts)")
        elif profile.is_new_business is False:
            if eval_prog.new_business_only is True:
                stage_score = 1.0
            elif eval_prog.existing_business_allowed is True or eval_prog.existing_business_allowed is None:
                stage_score = 5.0
                drivers.append("Expansion mandate: Aligned with operational scaling of existing MSMEs (+5.0 pts)")

        total_bs = min(10.0, dem_score + stage_score)
        return round(total_bs, 2), drivers

    @classmethod
    def score_market_context(
        cls,
        eval_prog: EvaluatableProgram,
        profile: UserProfile,
        market_context: Optional[DistrictMarketContext],
        target_amount: Optional[float],
    ) -> Tuple[float, List[str], List[str]]:
        """Evaluate empirical district MSME market-context indicators (0 to 10 pts).
        
        - Scale Concentration Alignment (0 to 5 pts): Local micro vs small/medium composition.
        - District Formalization & Enterprise Density Tier (0 to 5 pts): National ranking tier.
        
        IMPORTANT: Market context metrics are empirical indicators only and do not
        guarantee individual business success or scheme approval.
        """
        drivers: List[str] = []
        notes: List[str] = []

        if not market_context:
            return 5.0, ["Baseline market context prior applied (+5.0 pts)"], notes

        if market_context.is_fallback:
            notes.append(
                f"District not directly identified; market indicators derived from {market_context.state_name} state-level aggregates."
            )
            return 5.0, ["State-level market baseline prior applied (+5.0 pts)"], notes

        # --- Sub-component A: Scale Concentration Alignment (0 to 5 pts) ---
        is_micro_scale = (
            (target_amount is not None and target_amount <= 1000000)
            or (profile.annual_income is not None and profile.annual_income <= 5000000)
            or (profile.is_street_vendor or profile.is_traditional_artisan)
        )

        if is_micro_scale:
            if market_context.micro_share >= 90.0:
                scale_score = 5.0
                drivers.append(
                    f"District scale alignment: High local micro-enterprise concentration ({market_context.micro_share}%) "
                    f"matches applicant scale (+5.0 pts)"
                )
            else:
                scale_score = 3.5
        else:
            if market_context.small_medium_share >= 2.0:
                scale_score = 5.0
                drivers.append(
                    f"District industrial ecosystem: Significant local small/medium enterprise base "
                    f"({market_context.small_medium_share}%) supports operational growth (+5.0 pts)"
                )
            else:
                scale_score = 3.5

        # --- Sub-component B: Enterprise Density & Formalization Tier (0 to 5 pts) ---
        density_score = 2.5
        if market_context.national_rank is not None:
            rank = market_context.national_rank
            if rank <= 100:
                density_score = 5.0
                drivers.append(
                    f"Major MSME cluster: {market_context.district_name} ranks #{rank} nationally "
                    f"out of 785 districts in total registered MSMEs (+5.0 pts)"
                )
            elif rank <= 300:
                density_score = 4.0
                drivers.append(
                    f"Established MSME hub: {market_context.district_name} ranks #{rank} nationally "
                    f"in registered MSME density (+4.0 pts)"
                )
            elif rank <= 500:
                density_score = 3.0
            else:
                density_score = 2.0

        total_mc = min(10.0, scale_score + density_score)
        return round(total_mc, 2), drivers, notes

    @classmethod
    def calculate_score(
        cls,
        eval_prog: EvaluatableProgram,
        profile: UserProfile,
        market_context: Optional[DistrictMarketContext],
        target_amount: Optional[float],
        eligibility_status: str,
        unverified_criteria: List[str],
    ) -> ProgramRecommendationItem:
        """Calculate aggregate 100-point transparent score and compile full explainability output."""
        # 1. Component scores
        s_elig, d_elig, n_elig = cls.score_eligibility_confidence(eligibility_status, unverified_criteria)
        s_fin, d_fin, n_fin = cls.score_financial_fit(eval_prog, target_amount)
        s_sec, d_sec = cls.score_sector_fit(eval_prog, profile)
        s_act, d_act = cls.score_actionability(eval_prog)
        s_ben, d_ben = cls.score_beneficiary_and_stage(eval_prog, profile)
        s_mkt, d_mkt, n_mkt = cls.score_market_context(eval_prog, profile, market_context, target_amount)

        # 2. Total score aggregation strictly capped to [0.0, 100.0]
        raw_total = s_elig + s_fin + s_sec + s_act + s_ben + s_mkt
        total_score = round(min(100.0, max(0.0, raw_total)), 2)

        # 3. Fit category mapping
        if total_score >= 80.0:
            fit_category = "EXCELLENT_FIT"
        elif total_score >= 65.0:
            fit_category = "STRONG_FIT"
        elif total_score >= 50.0:
            fit_category = "MODERATE_FIT"
        else:
            fit_category = "LOW_FIT"

        # 4. Compile explainability drivers and cautionary notes
        all_drivers: List[str] = d_elig + d_fin + d_sec + d_act + d_ben + d_mkt
        all_notes: List[str] = n_elig + n_fin + n_mkt

        scoring_breakdown = ScoringBreakdown(
            eligibility_confidence_score=s_elig,
            financial_fit_score=s_fin,
            sector_fit_score=s_sec,
            actionability_score=s_act,
            beneficiary_stage_score=s_ben,
            market_context_score=s_mkt,
            total_score=total_score,
        )

        return ProgramRecommendationItem(
            rank=0,  # Assigned after sorting in RecommendationService
            program_id=eval_prog.program_id,
            program_code=eval_prog.program_code,
            program_name=eval_prog.program_name,
            primary_type=eval_prog.primary_type,
            actionability_type=eval_prog.actionability_type,
            eligibility_status=eligibility_status,
            recommendation_score=total_score,
            fit_category=fit_category,
            scoring_breakdown=scoring_breakdown,
            recommendation_drivers=all_drivers,
            cautionary_notes=all_notes,
            official_portal_url=eval_prog.official_portal_url,
            benefit_summary=eval_prog.benefit_summary,
        )


recommendation_scorer = RecommendationScorer()
