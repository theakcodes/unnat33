"""
app/schemas/dpr.py

Pydantic schemas for the Canonical 13-Section Structured Detailed Project Report (DPR):
- Strict separation between Authoritative Deterministic Engines and AI Narrative Composition.
- Zero frontend calculations: All financial, debt, subsidy, and statutory data come from backend engines.
- Strict Provenance tracking on every section and metric:
  1. USER PROVIDED
  2. GOVERNMENT / DATASET DERIVED
  3. MODELLED INDICATOR
  4. AI INTERPRETATION
  5. ILLUSTRATIVE ASSUMPTION (with mandatory statutory disclaimer)
  6. BACKEND DETERMINISTIC CALCULATION
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.market_research import CustomerSegmentItem
from app.schemas.market_similarity import ComparableDistrictItem


# -------------------------------------------------------------------------
# Request Schema
# -------------------------------------------------------------------------
class DPRRequest(BaseModel):
    """Payload to generate a structured 13-section Detailed Project Report."""
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[str] = None
    business_id: Optional[str] = None
    project_name: Optional[str] = Field(None, description="Enterprise project name")
    promoter_name: Optional[str] = Field(None, description="Promoter or applicant name")
    business_type: str = Field(..., description="Primary business sector (e.g. 'Handloom', 'Food Processing')")
    sub_type: Optional[str] = Field(None, description="Specific trade sub-type")
    target_market: Optional[str] = Field(None, description="Target customer segment")
    experience_level: Optional[str] = Field(None, description="Years of experience")
    
    # Financial Inputs
    estimated_capital: float = Field(..., gt=0, description="Total planned project cost in INR")
    current_income: Optional[float] = Field(None, description="Current annual revenue in INR")
    existing_debt: Optional[float] = Field(None, description="Current outstanding debt in INR")
    
    # Location
    district_name: str = Field(..., description="Target district name")
    state_name: Optional[str] = Field(None, description="Target state name")
    lg_dt_code: Optional[str] = Field(None, description="Official LGD district code")
    location_type: Optional[str] = Field("URBAN", description="'RURAL' or 'URBAN'")
    
    # Demographic / Statutory Profile
    category: Optional[str] = Field("GENERAL", description="Social category: 'GENERAL', 'OBC', 'SC', 'ST'")
    gender: Optional[str] = Field("MALE", description="'MALE', 'FEMALE', 'TRANSGENDER'")
    education_level: Optional[str] = Field("GRADUATE", description="Educational qualification")
    is_differently_abled: Optional[bool] = Field(False, description="Special category status")
    is_ex_serviceman: Optional[bool] = Field(False, description="Ex-serviceman status")
    
    # Scheme Selection Override
    selected_program_code: Optional[str] = Field(
        None, description="Explicit government program code override (e.g. 'PMEGP_NEW', 'MUDRA_KISHORE')"
    )
    
    # User-Edited Qualitative Overrides
    qualitative_overrides: Optional[Dict[str, Any]] = Field(
        None, description="User edits to qualitative narrative fields, tagged as USER EDITED"
    )


# -------------------------------------------------------------------------
# 13 Canonical Sections
# -------------------------------------------------------------------------

class DPRExecutiveSummary(BaseModel):
    """Section 1: Executive Summary."""
    model_config = ConfigDict(from_attributes=True)

    project_name: str
    promoter_name: str
    business_type: str
    sub_type: Optional[str] = None
    location_district: str
    location_state: str
    total_project_cost: float
    recommended_program_code: str
    recommended_program_name: str
    promoter_contribution_amount: Optional[float] = None
    bank_loan_amount: float
    eligible_subsidy_amount: float
    monthly_emi: float
    executive_narrative: str
    provenance: str = "BACKEND DETERMINISTIC CALCULATION + AI INTERPRETATION"


class DPRBusinessModel(BaseModel):
    """Section 2: Business Model & Value Proposition."""
    model_config = ConfigDict(from_attributes=True)

    value_proposition: str
    target_segments_summary: str
    revenue_streams: List[str]
    key_activities: List[str]
    key_partners: List[str]
    cost_structure_summary: List[str]
    provenance: str = "USER PROVIDED + AI INTERPRETATION"


class DPRMarketAnalysis(BaseModel):
    """Section 3: District Market Analysis."""
    model_config = ConfigDict(from_attributes=True)

    total_msmes_in_district: int
    micro_enterprise_share: float
    small_medium_share: float
    national_rank: Optional[int] = None
    state_rank: Optional[int] = None
    cluster_archetype_label: str
    cluster_archetype_description: str
    market_research_indicator: float
    comparable_districts: List[ComparableDistrictItem]
    demand_drivers: List[str]
    market_barriers: List[str]
    provenance: str = "GOVERNMENT / DATASET DERIVED + MODELLED INDICATOR + AI INTERPRETATION"


class DPRCustomerSegments(BaseModel):
    """Section 4: Target Customer Segments."""
    model_config = ConfigDict(from_attributes=True)

    customer_segments: List[CustomerSegmentItem]
    buying_behaviour_summary: str
    provenance: str = "AI INTERPRETATION"


class DPRCompetition(BaseModel):
    """Section 5: Competitive Landscape & Market Structure."""
    model_config = ConfigDict(from_attributes=True)

    competition_intensity: str  # 'Low', 'Moderate', 'High', 'Very High'
    competition_rationale: str
    market_structure_type: str
    differentiation_vectors: List[str]
    field_survey_gaps: List[str]
    provenance: str = "MODELLED INDICATOR + AI INTERPRETATION"


class DPRLocationAnalysis(BaseModel):
    """Section 6: Location & Infrastructure Suitability."""
    model_config = ConfigDict(from_attributes=True)

    district_name: str
    state_name: str
    lg_dt_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_meters: Optional[float] = None
    connectivity_advantages: List[str]
    raw_material_proximity: str
    labor_availability: str
    provenance: str = "GOVERNMENT / DATASET DERIVED + AI INTERPRETATION"


class DPROperationsPlan(BaseModel):
    """Section 7: Operations & Production Plan."""
    model_config = ConfigDict(from_attributes=True)

    workflow_steps: List[str]
    key_machinery_equipment: List[str]
    utilities_and_power: List[str]
    workforce_roles: List[str]
    quality_assurance: str
    provenance: str = "USER PROVIDED + AI INTERPRETATION"


class DPRMarketingStrategy(BaseModel):
    """Section 8: Marketing, Distribution & Sales Strategy."""
    model_config = ConfigDict(from_attributes=True)

    positioning_statement: str
    sales_channels: List[str]
    customer_acquisition_methods: List[str]
    pricing_framework: str
    promotional_initiatives: List[str]
    provenance: str = "AI INTERPRETATION"


class DPRGovernmentSupport(BaseModel):
    """Section 9: Government Scheme Support & Statutory Eligibility."""
    model_config = ConfigDict(from_attributes=True)

    program_code: str
    program_name: str
    ministry: str
    program_category: str
    is_credit_linked: bool
    eligible_subsidy_rate_pct: Optional[float] = None
    eligible_subsidy_amount: float = 0.0
    max_subsidy_allowed: Optional[float] = None
    eligible_criteria_met: List[str]
    mandatory_statutory_conditions: List[str]
    nodal_agency: str
    provenance: str = "GOVERNMENT / DATASET DERIVED + BACKEND DETERMINISTIC CALCULATION"


class DPRCapitalStructure(BaseModel):
    """Section 10: Authoritative Capital Structure."""
    model_config = ConfigDict(from_attributes=True)

    total_project_cost: float
    promoter_equity_amount: Optional[float] = None
    promoter_equity_pct: Optional[float] = None
    initial_bank_loan: Optional[float] = None
    net_bank_loan_exposure: Optional[float] = None
    term_loan_amount: Optional[float] = None
    term_loan_pct: Optional[float] = None
    working_capital_amount: Optional[float] = None
    working_capital_pct: Optional[float] = None
    government_subsidy_amount: float = 0.0
    government_subsidy_pct: Optional[float] = None
    is_statutorily_balanced: bool = False
    structuring_notes: List[str] = Field(default_factory=list)
    provenance: str = "BACKEND DETERMINISTIC CALCULATION"


class DebtServiceRepaymentYear(BaseModel):
    """Annual loan amortization summary."""
    model_config = ConfigDict(from_attributes=True)

    year: int
    opening_balance: float
    annual_principal: float
    annual_interest: float
    total_annual_payment: float
    closing_balance: float


class DPRFinancialAssumptions(BaseModel):
    """Section 11: Financial Assumptions & Debt Amortization."""
    model_config = ConfigDict(from_attributes=True)

    annual_interest_rate_pct: Optional[float] = None
    loan_tenure_months: Optional[int] = None
    moratorium_months: Optional[int] = None
    monthly_emi: float = 0.0
    annual_debt_service: float = 0.0
    total_interest_payable: float = 0.0
    total_debt_outflow: float = 0.0
    is_market_linked: bool = False
    is_benchmark_assumption: bool = False
    rate_type: Optional[str] = None
    rate_display_text: Optional[str] = None
    rate_note: Optional[str] = None
    amortization_schedule: List[DebtServiceRepaymentYear] = Field(default_factory=list)
    methodology_notes: List[str] = Field(default_factory=list)
    provenance: str = "BACKEND DETERMINISTIC CALCULATION"


class DPRRiskAnalysis(BaseModel):
    """Section 12: Risk Analysis & Climate / Operational Mitigation."""
    model_config = ConfigDict(from_attributes=True)

    weather_activity_impact_score: Optional[float] = None
    weather_activity_impact_label: Optional[str] = None
    heat_stress_level: Optional[str] = None
    rain_disruption_level: Optional[str] = None
    outdoor_activity_signal: Optional[str] = None
    logistics_disruption_level: Optional[str] = None
    identified_risks: List[Dict[str, str]]
    contingency_mitigations: List[str]
    provenance: str = "MODELLED INDICATOR + AI INTERPRETATION"


class DPRMilestoneItem(BaseModel):
    """Implementation timeline item."""
    model_config = ConfigDict(from_attributes=True)

    phase_number: int
    month_range: str
    activity: str
    critical_deliverable: str


class DPRImplementationPlan(BaseModel):
    """Section 13: Project Implementation Schedule (Months 1-6)."""
    model_config = ConfigDict(from_attributes=True)

    milestones: List[DPRMilestoneItem]
    critical_path_notes: List[str]
    provenance: str = "AI INTERPRETATION"


# -------------------------------------------------------------------------
# Auxiliary Sections: Illustrative Assumptions, Research Gaps & Provenance
# -------------------------------------------------------------------------

class DPRIllustrativeAssumptions(BaseModel):
    """Auxiliary Section: Illustrative Operational Assumptions."""
    model_config = ConfigDict(from_attributes=True)

    capacity_utilization_schedule: List[str]
    working_capital_cycle_days: int
    operating_expense_benchmarks: List[str]
    break_even_commentary: str
    disclaimer: str = Field(
        default="Illustrative assumption — validate with actual business records, quotations and local market checks.",
        description="Mandatory statutory zero-fabrication disclaimer",
    )
    provenance: str = "ILLUSTRATIVE ASSUMPTION"


class DPRResearchGaps(BaseModel):
    """Auxiliary Section: Empirical Gaps & Local Verification Checklist."""
    model_config = ConfigDict(from_attributes=True)

    unorganized_data_gaps: List[str]
    recommended_field_checks: List[str]
    provenance: str = "AI INTERPRETATION"


# -------------------------------------------------------------------------
# Complete DPR Response
# -------------------------------------------------------------------------

class DPRResponse(BaseModel):
    """
    Canonical 13-Section Detailed Project Report (DPR).
    Assembles authoritative backend calculations and qualitative AI synthesis into a unified report.
    """
    model_config = ConfigDict(from_attributes=True)

    report_id: str
    generated_at: str
    project_name: str
    promoter_name: str
    business_type: str
    sub_type: Optional[str] = None
    district_name: str
    state_name: str
    lg_dt_code: Optional[str] = None

    # 13 Canonical Sections
    executive_summary: DPRExecutiveSummary
    business_model: DPRBusinessModel
    market_analysis: DPRMarketAnalysis
    customer_segments: DPRCustomerSegments
    competition: DPRCompetition
    location_analysis: DPRLocationAnalysis
    operations_plan: DPROperationsPlan
    marketing_strategy: DPRMarketingStrategy
    government_support: DPRGovernmentSupport
    capital_structure: DPRCapitalStructure
    financial_assumptions: DPRFinancialAssumptions
    risk_analysis: DPRRiskAnalysis
    implementation_plan: DPRImplementationPlan

    # Auxiliary & Audit Sections
    illustrative_assumptions: DPRIllustrativeAssumptions
    research_gaps: DPRResearchGaps

    # Provenance Audit Trail
    provenance_legend: Dict[str, str] = Field(
        default_factory=lambda: {
            "USER PROVIDED": "Entered by entrepreneur or profile input.",
            "GOVERNMENT / DATASET DERIVED": "Direct official figures from PostgreSQL Udyam census or statutory scheme gazettes.",
            "MODELLED INDICATOR": "Quantitative metrics computed via scikit-learn (KMeans clustering, NearestNeighbors) or weather heuristics.",
            "AI INTERPRETATION": "Qualitative business strategy and operational narrative synthesized from empirical evidence.",
            "ILLUSTRATIVE ASSUMPTION": "Typical planning benchmarks requiring field validation: validate with actual business records, quotations and local market checks.",
            "BACKEND DETERMINISTIC CALCULATION": "Authoritative non-LLM statutory calculations (subsidy, promoter equity, bank loan, EMI).",
        }
    )
    disclaimer: str = Field(
        default=(
            "CONFIDENTIAL DETAILED PROJECT REPORT (DPR): Prepared for bank loan appraisal and government scheme applications. "
            "Financial structuring and subsidy computations reflect official statutory guidelines. "
            "Market indicators and operational narratives are advisory and do not guarantee credit sanction."
        )
    )
