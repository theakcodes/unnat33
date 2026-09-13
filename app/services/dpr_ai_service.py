"""
app/services/dpr_ai_service.py

AI DPR Composition Service:
- Synthesizes professional, bank-ready qualitative narratives for the canonical 13-section DPR.
- Data-grounded: Ingests the MarketResearchEvidence package, authoritative capital structure,
  and statutory programme details.
- CRITICAL BOUNDARY: Zero financial math, zero subsidy logic, zero eligibility calculations.
  Strictly consumes upstream deterministic outputs.
- Resilient failure isolation: Attempts Anthropic Claude 3.5 Sonnet; falls back cleanly to
  domain-specific deterministic empirical templates when offline, rate-limited, or unconfigured.
"""

import json
import logging
from typing import Optional, Dict, Any, List
import anthropic

from app.core.config import settings
from app.schemas.market_research import MarketResearchEvidence, CustomerSegmentItem
from app.schemas.dpr import (
    DPRBusinessModel,
    DPRCustomerSegments,
    DPRCompetition,
    DPRLocationAnalysis,
    DPROperationsPlan,
    DPRMarketingStrategy,
    DPRMilestoneItem,
    DPRIllustrativeAssumptions,
    DPRResearchGaps,
)

logger = logging.getLogger(__name__)

DPR_SYSTEM_PROMPT = """You are an authoritative Indian banking project finance consultant and micro-enterprise DPR specialist.
You write professional, bank-acceptable Detailed Project Reports (DPR) for MSME credit appraisal under Indian government schemes (such as PMEGP, Mudra, Stand-Up India).

CRITICAL CONSTRAINTS & INVARIANTS:
1. DO NOT invent or recalculate any financial amounts, interest rates, subsidies, loan figures, or EMI calculations.
   Use ONLY the authoritative financial figures provided in the prompt.
2. DO NOT invent customer counts, market share percentages, or fake competitor statistics.
3. Keep descriptions professional, data-grounded, and actionable for bank credit officers.
4. Output must be strictly valid JSON without any markdown ticks or conversational prefix.

JSON Schema to return:
{
  "executive_narrative": "A cohesive 2-paragraph summary explaining the project rationale, promoter background, market gap, and statutory funding fit.",
  "value_proposition": "Clear value proposition for customers.",
  "target_segments_summary": "Summary of primary and secondary customer segments.",
  "revenue_streams": ["List of 2-3 primary revenue lines"],
  "key_activities": ["List of 3-4 core operational activities"],
  "key_partners": ["List of 3-4 key suppliers, institutional partners, or distribution partners"],
  "cost_structure_summary": ["List of primary fixed and variable cost heads"],
  "customer_segments": [
    {
      "segment": "Segment name",
      "need": "Customer need",
      "buying_consideration": "Key buying criteria",
      "recommended_channel": "Sales channel"
    }
  ],
  "buying_behaviour_summary": "Summary of local consumer or B2B purchasing behavior.",
  "competition_intensity": "Low|Moderate|High|Very High",
  "competition_rationale": "Reasoning referencing MSME density and local enterprise concentration.",
  "market_structure_type": "e.g. Fragmented Micro-Enterprise Cluster / Organized Wholesale / Decentralized Retail",
  "differentiation_vectors": ["3 actionable differentiation vectors"],
  "field_survey_gaps": ["2-3 unrecorded local market nuances requiring field check"],
  "connectivity_advantages": ["3 logistics, road, rail, or commercial advantages of the district"],
  "raw_material_proximity": "Evaluation of local raw material access and sourcing resilience.",
  "labor_availability": "Evaluation of local skilled and semi-skilled workforce availability.",
  "workflow_steps": ["5 sequential operational/production workflow stages"],
  "key_machinery_equipment": ["4-5 required machinery, tools, or IT hardware items"],
  "utilities_and_power": ["Power, water, and waste management infrastructure requirements"],
  "workforce_roles": ["3-4 job roles required for operation"],
  "quality_assurance": "Standard operating procedures and quality control protocol.",
  "positioning_statement": "Clear market positioning statement.",
  "sales_channels": ["3 distribution channels"],
  "customer_acquisition_methods": ["3 customer acquisition tactics"],
  "pricing_framework": "Descriptive pricing model (e.g. Cost-plus margin, Tiered wholesale; NO fake unit prices)",
  "promotional_initiatives": ["3 marketing or promotional initiatives"],
  "identified_risks": [
    {"risk": "Risk name", "severity": "Medium|High", "mitigation": "Prudent mitigation action"}
  ],
  "contingency_mitigations": ["2-3 general operational and weather contingency measures"],
  "milestones": [
    {"phase_number": 1, "month_range": "Month 1", "activity": "Activity name", "critical_deliverable": "Deliverable"}
  ],
  "critical_path_notes": ["2 critical path implementation considerations"],
  "capacity_utilization_schedule": ["Year 1: 60%", "Year 2: 70%", "Year 3: 80%"],
  "working_capital_cycle_days": 45,
  "operating_expense_benchmarks": ["Raw materials: 50-60% of turnover", "Labor & overheads: 15-20%"],
  "break_even_commentary": "Indicative break-even typically achievable between 60-70% capacity utilization subject to actual cost controls.",
  "unorganized_data_gaps": ["Gaps in local unrecorded competitor data"],
  "recommended_field_checks": ["Specific field checks before disbursement"]
}"""


class DPRAIService:
    """Service to compose bank-grade DPR qualitative narrative with AI or deterministic fallback."""

    def __init__(self):
        self.api_key = getattr(settings, "ANTHROPIC_API_KEY", "") or ""

    async def compose_dpr_narrative(
        self,
        evidence: MarketResearchEvidence,
        promoter_name: str,
        project_name: str,
        program_name: str,
        total_project_cost: float,
        promoter_equity: Optional[float] = None,
        bank_loan: float = 0.0,
        subsidy_amount: float = 0.0,
        monthly_emi: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Compose qualitative narrative for DPR.
        Attempts Claude 3.5 Sonnet; falls back cleanly to deterministic empirical templates upon error.
        """
        if self.api_key and self.api_key.strip():
            try:
                user_prompt = self._build_prompt(
                    evidence=evidence,
                    promoter_name=promoter_name,
                    project_name=project_name,
                    program_name=program_name,
                    total_project_cost=total_project_cost,
                    promoter_equity=promoter_equity,
                    bank_loan=bank_loan,
                    subsidy_amount=subsidy_amount,
                    monthly_emi=monthly_emi,
                )

                client = anthropic.AsyncAnthropic(api_key=self.api_key.strip(), timeout=20.0)
                message = await client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2500,
                    system=DPR_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )

                raw = message.content[0].text.strip()
                if raw.startswith("```"):
                    raw = raw.strip("`").removeprefix("json").strip()

                parsed = json.loads(raw)
                return parsed
            except Exception as e:
                logger.warning(
                    "Anthropic Claude DPR composition failed (%s: %s). Using deterministic domain template.",
                    type(e).__name__,
                    e,
                )

        # Resilient Empirical Fallback
        return self._build_deterministic_template(
            evidence=evidence,
            promoter_name=promoter_name,
            project_name=project_name,
            program_name=program_name,
            total_project_cost=total_project_cost,
            promoter_equity=promoter_equity,
            bank_loan=bank_loan,
            subsidy_amount=subsidy_amount,
            monthly_emi=monthly_emi,
        )

    def _build_prompt(
        self,
        evidence: MarketResearchEvidence,
        promoter_name: str,
        project_name: str,
        program_name: str,
        total_project_cost: float,
        promoter_equity: Optional[float],
        bank_loan: float,
        subsidy_amount: float,
        monthly_emi: float,
    ) -> str:
        promoter_equity_str = (
            f"INR {promoter_equity:,.2f}"
            if promoter_equity is not None
            else "Not specified by authoritative programme data"
        )
        return f"""Generate a structured, bank-ready Detailed Project Report (DPR) qualitative narrative for:

PROJECT OVERVIEW:
- Project Name: {project_name}
- Promoter Name: {promoter_name}
- Primary Sector: {evidence.business_type} (Sub-type: {evidence.sub_type or 'Standard'})
- Location: {evidence.district_name}, {evidence.state_name}
- Target Market: {evidence.target_market or 'Local and Regional'}
- Experience Level: {evidence.experience_level or 'Experienced'}

OFFICIAL DISTRICT MSME PROFILE (PostgreSQL Census):
- Total Registered MSMEs: {evidence.total_msmes:,}
- Micro-Enterprise Share: {evidence.micro_share:.1f}%
- Small & Medium Enterprise Share: {evidence.small_medium_share:.1f}%
- National Density Rank: {evidence.national_rank or 'N/A'} of 785 districts
- State Density Rank: {evidence.state_rank or 'N/A'}
- Cluster Archetype: {evidence.cluster_label or 'Commercial District'}
- Market Research Indicator (MRI): {evidence.market_research_indicator or '50.0'}/100

NEAREST NEIGHBOURS (Comparable Districts):
{chr(10).join(['- ' + s for s in evidence.comparable_districts_summary[:3]]) or '- Comparable commercial districts in region'}

WEATHER & ACTIVITY CONTEXT:
- Weather Condition: {evidence.weather_condition or 'Seasonal normal'}
- Activity Impact Score: {evidence.activity_impact_score or 'Neutral'} ({evidence.activity_impact_label or 'Neutral'})

AUTHORITATIVE FINANCIAL STRUCTURE (DO NOT RECALCULATE):
- Total Project Cost: INR {total_project_cost:,.2f}
- Government Scheme: {program_name}
- Promoter Margin Contribution: {promoter_equity_str}
- Bank Term/Working Capital Loan: INR {bank_loan:,.2f}
- Government Margin Money / Subsidy: INR {subsidy_amount:,.2f}
- Estimated Monthly Debt Service (EMI): INR {monthly_emi:,.2f}

Provide the requested JSON schema with rich, defensible, professional consulting content."""

    def _build_deterministic_template(
        self,
        evidence: MarketResearchEvidence,
        promoter_name: str,
        project_name: str,
        program_name: str,
        total_project_cost: float,
        promoter_equity: Optional[float],
        bank_loan: float,
        subsidy_amount: float,
        monthly_emi: float,
    ) -> Dict[str, Any]:
        """High-quality deterministic fallback tailored to business sector and district data."""
        btype = (evidence.business_type or "General Enterprise").lower()
        dname = evidence.district_name
        sname = evidence.state_name
        tot_msmes = evidence.total_msmes
        mic_share = evidence.micro_share

        # Sector-specific customization
        if "food" in btype or "agro" in btype or "bakery" in btype:
            workflow = [
                "Procurement & inspection of farm-gate / wholesale agricultural raw materials",
                "Sorting, cleaning, pre-processing, and hygienic staging",
                "Value-added processing, batch formulation, and cooking/milling",
                "Food-grade tamper-evident packaging, FSSAI batch labeling, and cold/dry staging",
                "Direct delivery to retail stockists and wholesale regional distribution",
            ]
            equipment = [
                "Commercial grade food processing / pulverizing / mixing units",
                "Stainless steel 304 food contact preparation tables and storage vats",
                "Automated volumetric packaging and continuous band sealer",
                "Dry storage racking and commercial refrigeration / cooling unit",
            ]
            utilities = ["3-phase commercial electric connection (10-15 kW)", "Potable water connection with RO purification", "Hygienic drainage and wet waste segregation"]
            segments = [
                {"segment": "Local Retail Consumers", "need": "Hygienic, fresh, unadulterated food products", "buying_consideration": "Taste, cleanliness, competitive local pricing", "recommended_channel": "Direct retail counters & local kirana stores"},
                {"segment": "Institutional & Hospitality Buyers", "need": "Consistent bulk supply for catering and eateries", "buying_consideration": "Reliable delivery schedules and volume pricing", "recommended_channel": "B2B direct contracts"},
            ]
            diffs = ["Standardized hygienic packaging compliant with FSSAI regulations", "Local farm-gate sourcing delivering superior freshness over long-distance brands", "Flexible batch sizes catering to regional culinary taste preferences"]
        elif "textile" in btype or "handloom" in btype or "garment" in btype:
            workflow = [
                "Yarn and fabric sourcing from certified mills / regional weavers",
                "Pattern drafting, grading, fabric inspection, and precision cutting",
                "Component stitching, assembly, embroidery, and reinforcement",
                "Finishing, buttoning, thread trimming, and steam pressing",
                "Quality inspection, barcode tagging, packaging, and dispatch",
            ]
            equipment = [
                "Industrial lockstitch and overlock sewing machines",
                "Heavy-duty fabric cutting table and straight-knife cutting machine",
                "Industrial steam iron press with vacuum suction table",
                "Material inspection and dispatch staging racks",
            ]
            utilities = ["Commercial single/3-phase electricity (5-8 kW)", "Adequate glare-free LED task lighting and ergonomic workstation setup", "Ventilated, dust-free fabric storage area"]
            segments = [
                {"segment": "Local & Regional Apparel Retailers", "need": "Fast turnaround on high-demand ethnic and daily wear", "buying_consideration": "Consistent stitching quality and credit terms", "recommended_channel": "Wholesale distributor network"},
                {"segment": "End-user Consumers & Custom Orders", "need": "Made-to-measure tailoring and tailored design", "buying_consideration": "Fitting precision, fabric durability, timely delivery", "recommended_channel": "Direct retail boutique & word-of-mouth"},
            ]
            diffs = ["Superior fabric durability and reinforced seam stitching", "Agile small-batch production reacting rapidly to seasonal fashion trends", "Direct relationship with regional wholesale buyers eliminating intermediary commissions"]
        elif "service" in btype or "it" in btype or "repair" in btype:
            workflow = [
                "Client inquiry intake, problem diagnosis, and job-order estimation",
                "Resource scheduling, spare part allocation, and technician assignment",
                "Service execution adhering to standard operating protocols",
                "Testing, quality verification, and client demonstration",
                "Billing, digital payment receipt, warranty issuance, and feedback collection",
            ]
            equipment = [
                "Specialized diagnostic testing equipment and precision hand tools",
                "Workstations with enterprise management and billing software",
                "Safety equipment, ESD mats, and protective gear",
                "Spare parts inventory racking and secure lockers",
            ]
            utilities = ["High-speed broadband internet with secondary redundancy", "Regulated UPS/inverter power backup (2-5 kVA)", "Accessible customer reception and demonstration counter"]
            segments = [
                {"segment": "Local Residents & Households", "need": "Reliable, transparent diagnostic and repair services", "buying_consideration": "Speed of response, honest pricing, service guarantee", "recommended_channel": "Physical service center & WhatsApp booking"},
                {"segment": "Commercial Establishments & MSMEs", "need": "Annual maintenance contracts and preventive servicing", "buying_consideration": "Minimal business downtime and GST-compliant invoicing", "recommended_channel": "Direct corporate sales outreach"},
            ]
            diffs = ["Transparent upfront quotation with zero hidden charges", "Prompt turnaround time supported by ready inventory of common spares", "Post-service warranty providing customer peace of mind"]
        else:
            workflow = [
                "Raw material procurement, grade verification, and inventory intake",
                "Batch scheduling, setup preparation, and staging",
                "Primary fabrication / manufacturing / assembly process",
                "Finishing, inspection, and dimensional / functional quality testing",
                "Protective packaging, warehouse storage, and dispatch logistics",
            ]
            equipment = [
                "Primary production machinery and specialized tooling",
                "Assembly workbenches and material handling equipment",
                "Measuring instruments and quality testing apparatus",
                "Heavy-duty storage racking and pallet staging area",
            ]
            utilities = ["Standard commercial electricity with adequate load sanction", "Clean water supply and industrial waste disposal compliant with local norms", "Ventilated workspace with fire safety compliance"]
            segments = [
                {"segment": "Regional Commercial Distributors", "need": "Dependable volume supplies at structured wholesale pricing", "buying_consideration": "Consistent supply regularity and product compliance", "recommended_channel": "Regional sales representative network"},
                {"segment": "Direct Local Buyers", "need": "Immediate product availability without transit delays", "buying_consideration": "Proximity, competitive rates, local service support", "recommended_channel": "Direct factory outlet / counter sales"},
            ]
            diffs = ["Direct local availability bypassing interstate freight lead-times", "Dedicated after-sales support and regional responsiveness", "Flexible custom batch capabilities for regional buyers"]

        promoter_equity_desc = (
            f"a promoter margin contribution of INR {promoter_equity:,.2f}"
            if promoter_equity is not None
            else "promoter margin contribution as specified under nodal scheme norms"
        )
        return {
            "executive_narrative": (
                f"This Detailed Project Report establishes the commercial and financial framework for {project_name}, "
                f"a proposed enterprise in the {evidence.business_type} domain promoted by {promoter_name} in {dname}, {sname}. "
                f"The district features a dynamic commercial base of {tot_msmes:,} registered MSMEs, characterized by {mic_share:.1f}% "
                f"micro-enterprise concentration, demonstrating substantial local economic activity and established commercial trade channels.\n\n"
                f"The project has an aggregate capital outlay of INR {total_project_cost:,.2f}, supported through the {program_name} scheme. "
                f"The financing structure comprises {promoter_equity_desc}, supplemented by bank debt of "
                f"INR {bank_loan:,.2f} and statutory government margin money/subsidy of INR {subsidy_amount:,.2f}. The projected monthly debt service "
                f"(EMI) of INR {monthly_emi:,.2f} is well within conservative operational cash flow capacity."
            ),
            "value_proposition": f"High-quality, locally accessible {evidence.business_type} solutions delivering consistent reliability, transparent pricing, and dependable supply to {dname} and adjoining regional markets.",
            "target_segments_summary": f"Primary demand centers on retail and commercial buyers across {dname}, complemented by regional wholesale distribution in {sname}.",
            "revenue_streams": [
                f"Direct sales of core {evidence.business_type} product/service offerings to retail and commercial clients",
                "Value-added custom orders and specialized batches for institutional customers",
                "Recurring seasonal demand and repeat regional wholesale orders",
            ],
            "key_activities": [
                "Raw material sourcing and quality intake inspection",
                "Standardized production, fabrication, or service execution",
                "Packaging, dispatch logistics, and client inventory fulfillment",
                "Client relationship management and working capital oversight",
            ],
            "key_partners": [
                "Certified regional raw material and component suppliers",
                "Local commercial transport and logistics service providers",
                "District DIC / MSME support agencies and financing partner bank",
                "Retail merchant associations and local trade stockists",
            ],
            "cost_structure_summary": [
                "Raw material procurement and consumables (primary cost driver)",
                "Skilled and semi-skilled staff remuneration",
                "Utility charges (electricity, water, communications)",
                "Packaging, freight, distribution, and local marketing",
                "Statutory debt service (bank EMI) and routine maintenance",
            ],
            "customer_segments": segments,
            "buying_behaviour_summary": f"Buyers in {dname} prioritize consistent product quality, immediate availability, and fair regional pricing over distant branded alternatives.",
            "competition_intensity": "Moderate",
            "competition_rationale": f"The district supports {tot_msmes:,} MSMEs with {mic_share:.1f}% micro-enterprise presence, indicating a decentralized, competitive market with strong scope for quality-differentiated operators.",
            "market_structure_type": "Decentralized Micro-Enterprise Market Cluster",
            "differentiation_vectors": diffs,
            "field_survey_gaps": [
                "Unrecorded localized pricing variations among informal micro-vendors",
                "Granular seasonal demand swings during agricultural harvest cycles",
                "Exact credit period expectations demanded by regional retail stockists",
            ],
            "connectivity_advantages": [
                f"Well-connected road and arterial highway network connecting {dname} to regional consumption centers in {sname}",
                "Established local logistics and transport carrier booking offices",
                "Proximity to primary commercial mandi or wholesale distribution hub",
            ],
            "raw_material_proximity": f"Adequate raw material and input availability through established regional wholesale supply networks in and around {dname}.",
            "labor_availability": f"Abundant availability of local semi-skilled and skilled workforce readily trainable for {evidence.business_type} operations.",
            "workflow_steps": workflow,
            "key_machinery_equipment": equipment,
            "utilities_and_power": utilities,
            "workforce_roles": [
                "Production / Operations Supervisor (1)",
                "Skilled Technicians / Machine Operators (2)",
                "Semi-skilled Assistants / Material Handlers (2)",
                "Promoter-led Administration & Sales Management (1)",
            ],
            "quality_assurance": "Standard Operating Procedures (SOPs) implemented across all stages with incoming raw material checks and pre-dispatch quality verification.",
            "positioning_statement": f"Positioned as a trusted, high-quality, regionally accessible {evidence.business_type} provider known for reliability and fair pricing.",
            "sales_channels": [
                "Direct sales from enterprise premises / processing unit",
                "Wholesale distribution through selected retail merchants in the district",
                "Digital outreach via localized B2B directories and WhatsApp business channels",
            ],
            "customer_acquisition_methods": [
                "Direct product sampling and initial promotional margin offers to local retailers",
                "Active outreach to institutional, hospitality, or commercial bulk buyers",
                "Customer referral incentives and consistent on-time order fulfillment",
            ],
            "pricing_framework": "Structured cost-plus pricing framework ensuring competitive retail prices while maintaining healthy gross operating margins; zero speculative price assumptions.",
            "promotional_initiatives": [
                "Promotional introductory displays at local trade fairs and weekly markets",
                "Signage, branded packaging, and verified Google Business profile listing",
                "Direct relationship visits by the promoter to retail stockists",
            ],
            "identified_risks": [
                {"risk": "Raw Material Price Fluctuations", "severity": "Medium", "mitigation": "Establish multi-supplier agreements and maintain 15-30 days buffer stock of critical inputs."},
                {"risk": "Working Capital Delay from Credit Customers", "severity": "Medium", "mitigation": "Strict credit terms (max 15 days), prompt billing, and early payment cash discounts."},
                {"risk": "Power Outages or Seasonal Weather Disruptions", "severity": "Low", "mitigation": "Dedicated generator / inverter backup and weather-aligned production scheduling."},
            ],
            "contingency_mitigations": [
                "Diversified vendor base across neighbouring districts to buffer supply shocks",
                "Maintaining an emergency liquidity reserve equal to 3 months of loan EMI",
                "Adequate multi-peril commercial insurance covering plant, machinery, and inventory",
            ],
            "milestones": [
                {"phase_number": 1, "month_range": "Month 1", "activity": "Statutory registrations, bank loan sanction & lease execution", "critical_deliverable": "Bank sanction letter, Udyam registration, and site handover"},
                {"phase_number": 2, "month_range": "Month 2", "activity": "Civil modifications, power sanction & machinery ordering", "critical_deliverable": "Sanctioned electrical load and machinery dispatch receipts"},
                {"phase_number": 3, "month_range": "Month 3", "activity": "Machinery installation, trial testing & supplier contracts", "critical_deliverable": "Successful test batch run and raw material supply agreements"},
                {"phase_number": 4, "month_range": "Month 4", "activity": "Commercial trial production, packaging & stockist outreach", "critical_deliverable": "Initial commercial batch staged and first 10 retailer commitments"},
                {"phase_number": 5, "month_range": "Month 5", "activity": "Official commercial launch and order fulfillment", "critical_deliverable": "Active invoicing and regular dispatches"},
                {"phase_number": 6, "month_range": "Month 6", "activity": "Operations stabilization and working capital review", "critical_deliverable": "Achieving steady monthly production volume and prompt EMI servicing"},
            ],
            "critical_path_notes": [
                "Timely release of bank loan disbursements is critical to preventing machinery delivery delays.",
                "Fast-track processing of required utility load sanctions and statutory local permits.",
            ],
            "capacity_utilization_schedule": [
                "Year 1: 60% Capacity Utilization (Ramp-up & market penetration)",
                "Year 2: 70% Capacity Utilization (Operations stabilization)",
                "Year 3: 80% Capacity Utilization (Optimal operating plateau)",
            ],
            "working_capital_cycle_days": 45,
            "operating_expense_benchmarks": [
                "Raw materials & inputs: 55-65% of gross revenue",
                "Direct wages & labor: 10-15% of gross revenue",
                "Utilities, rent & consumables: 5-8% of gross revenue",
                "Administrative & marketing overheads: 3-5% of gross revenue",
            ],
            "break_even_commentary": "Commercial break-even point is estimated at approximately 45-50% of installed operational capacity, providing a prudent safety margin for bank debt servicing.",
            "unorganized_data_gaps": [
                "Granular local sales volume of unorganized informal roadside units",
                "Unrecorded cash transactions in traditional village haat markets",
            ],
            "recommended_field_checks": [
                "Verify actual commercial rental quotations for proposed unit location",
                "Collect written machinery proforma invoices from at least 2 certified manufacturers",
                "Conduct 10 in-person interviews with local retail shopkeepers to confirm product appetite",
            ],
        }


# Singleton Instance
dpr_ai_service = DPRAIService()
