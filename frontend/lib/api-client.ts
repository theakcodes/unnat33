/**
 * Centralized API client for communicating with the authoritative FastAPI backend.
 * Base URL is configured via BACKEND_URL (server-side) or NEXT_PUBLIC_BACKEND_URL (client-side).
 */

import { API_BASE_URL } from './constants';

const getBackendUrl = (): string => {
  if (typeof window === 'undefined') {
    return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || API_BASE_URL;
  }
  return process.env.NEXT_PUBLIC_BACKEND_URL || API_BASE_URL;
};

// ============================================================================
// 1. Programmes Schemas (60 Central Sector / Centrally Sponsored Programmes)
// ============================================================================

export interface ProgramSector {
  id: number;
  sector_code?: string | null;
  sector_name: string;
}

export interface ProgramResponse {
  id: number;
  program_code: string;
  program_name: string;
  owning_ministry: string;
  nodal_agency?: string | null;
  official_portal_url: string;
  primary_type: string;
  secondary_types?: string[];
  actionability_type: string;
  hierarchy_level: string;
  parent_program_id?: number | null;
  description?: string | null;
  benefit_summary: string;
  benefit_type: string;
  benefit_headline_numeric?: number | null;
  benefit_headline_percentage?: number | null;
  target_beneficiary_summary?: string | null;
  status: string;
  legacy_scheme_id?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
  sectors: ProgramSector[];
}

export interface ProgramEligibility {
  rural_eligible?: boolean | null;
  urban_eligible?: boolean | null;
  male_eligible?: boolean | null;
  female_eligible?: boolean | null;
  other_gender_eligible?: boolean | null;
  general_eligible?: boolean | null;
  sc_eligible?: boolean | null;
  st_eligible?: boolean | null;
  obc_eligible?: boolean | null;
  minority_eligible?: boolean | null;
  pwd_eligible?: boolean | null;
  ex_servicemen_eligible?: boolean | null;
  min_age?: number | null;
  max_age?: number | null;
  max_annual_income?: number | null;
  notes?: string | null;
}

export interface ProgramCreditDetail {
  min_loan_amount?: number | null;
  max_loan_amount?: number | null;
  interest_rate_min?: number | null;
  interest_rate_max?: number | null;
  tenure_years?: number | null;
  moratorium_months?: number | null;
  collateral_required?: boolean | null;
  promoter_contribution_pct?: number | null;
}

export interface ProgramGuaranteeDetail {
  max_credit_limit: number;
  guarantee_coverage_pct: number;
  annual_guarantee_fee_pct?: number | null;
  hybrid_security_allowed?: boolean | null;
  eligible_lending_institutions?: string | null;
}

export interface ProgramSubsidyDetail {
  subsidy_pct?: number | null;
  max_subsidy_amount?: number | null;
  min_project_cost?: number | null;
  max_project_cost?: number | null;
  beneficiary_contribution_pct?: number | null;
  disbursement_type?: string | null;
}

export interface ProgramDetailResponse extends ProgramResponse {
  eligibility?: ProgramEligibility | null;
  credit_details?: ProgramCreditDetail | null;
  guarantee_details?: ProgramGuaranteeDetail | null;
  subsidy_details?: ProgramSubsidyDetail | null;
}

export interface ProgramQueryParams {
  status?: string;
  primary_type?: string;
  actionability_type?: string;
  ministry?: string;
  sector?: string;
  skip?: number;
  limit?: number;
}

// ============================================================================
// 2. Recommendation Engine Schemas (POST /api/v1/recommendations/recommend)
// ============================================================================

export interface ScoringBreakdown {
  eligibility_confidence_score: number;
  financial_fit_score: number;
  sector_fit_score: number;
  actionability_score: number;
  beneficiary_stage_score: number;
  market_context_score: number;
  total_score: number;
}

export interface ProgramRecommendationItem {
  rank: number;
  program_id: number;
  program_code: string;
  program_name: string;
  primary_type: string;
  actionability_type: string;
  eligibility_status: string;
  recommendation_score: number;
  fit_category: string;
  scoring_breakdown: ScoringBreakdown;
  recommendation_drivers: string[];
  cautionary_notes: string[];
  official_portal_url?: string | null;
  benefit_summary?: string | null;
}

// ============================================================================
// 1b. Deterministic Statutory Eligibility Schemas (POST /api/v1/programs/evaluate-eligibility)
// ============================================================================

export interface UserProfile {
  age?: number | null;
  gender?: string | null;
  social_category?: string | null;
  is_differently_abled?: boolean | null;
  is_ex_serviceman?: boolean | null;
  state?: string | null;
  district?: string | null;
  is_rural?: boolean | null;
  annual_income?: number | null;
  project_cost?: number | null;
  requested_loan_amount?: number | null;
  is_new_business?: boolean | null;
  sector?: string | null;
  business_type?: string | null;
  previous_tarun_repaid?: boolean | null;
  is_traditional_artisan?: boolean | null;
  is_street_vendor?: boolean | null;
}

export interface FinancialConstraints {
  min_loan_amount?: number | null;
  max_loan_amount?: number | null;
  min_project_cost?: number | null;
  max_project_cost?: number | null;
  max_subsidy_amount?: number | null;
  subsidy_percentage?: number | null;
  max_guarantee_limit?: number | null;
  guarantee_coverage_pct?: number | null;
  interest_rate_min?: number | null;
  interest_rate_max?: number | null;
}

export interface ProgramEligibilityResult {
  program_id: number;
  program_code: string;
  program_name: string;
  primary_type: string;
  actionability_type: string;
  is_eligible: boolean;
  status: 'Eligible' | 'Ineligible' | 'Partially Verified' | string;
  reasons: string[];
  disqualifying_reasons: string[];
  unverified_criteria: string[];
  financial_constraints?: FinancialConstraints | null;
  official_portal_url?: string | null;
  benefit_summary?: string | null;
}

export interface ProgramEligibilityAssessmentResponse {
  total_evaluated: number;
  total_eligible: number;
  total_ineligible: number;
  total_partially_verified: number;
  eligible_programs: ProgramEligibilityResult[];
  ineligible_programs: ProgramEligibilityResult[];
  partially_verified_programs: ProgramEligibilityResult[];
  directly_recommendable_count: number;
  component_recommendable_count: number;
  platform_count: number;
  framework_count: number;
}

export interface RecommendationUserProfile extends UserProfile {
  annual_turnover?: number;
  investment_in_plant?: number;
  enterprise_type?: string;
}

export interface RecommendationRequest {
  business_profile_id?: number | null;
  profile?: UserProfile | RecommendationUserProfile | null;
  target_financing_need?: number | null;
  preferred_assistance_type?: string | null;
  top_k?: number;
}

export interface RecommendationResponse {
  total_programs_evaluated: number;
  eligible_candidates_count: number;
  partially_verified_candidates_count: number;
  total_recommended: number;
  district_market_context?: any | null;
  recommendations: ProgramRecommendationItem[];
}

// ============================================================================
// 3. Financial Structuring Schemas (POST /api/v1/recommendations/financial-structuring)
// ============================================================================

export interface FinancialStructuringRequest {
  program_id?: number | null;
  program_code?: string | null;
  project_cost: number;
  requested_loan_amount?: number | null;
  monthly_income: number;
  monthly_expenses?: number;
  existing_monthly_emi?: number;
  applicant_social_category?: string | null;
  applicant_gender?: string | null;
  is_rural?: boolean | null;
  is_new_business?: boolean | null;
  preferred_tenure_months?: number | null;
}

export interface CapitalStructureBreakdown {
  project_cost: number;
  promoter_contribution_pct?: number | null;
  promoter_contribution_amount?: number | null;
  is_statutory_margin: boolean;
  subsidy_pct?: number | null;
  subsidy_amount: number;
  is_conditional_subsidy: boolean;
  subsidy_disbursement_type?: string | null;
  initial_bank_loan?: number | null;
  net_effective_debt?: number | null;
  credit_guarantee_eligible: boolean;
  guarantee_coverage_pct?: number | null;
  guaranteed_amount?: number | null;
  annual_guarantee_fee_pct?: number | null;
  guarantee_nature: string;
}

export interface DebtHealthIndicators {
  monthly_income: number;
  existing_monthly_emi: number;
  uncommitted_surplus: number;
  affordable_emi_cap: number;
  existing_dti_pct: number;
  dti_health_category: string;
}

export interface RepaymentScenarioItem {
  scenario_type: string; // 'CONSERVATIVE' | 'BALANCED' | 'EXTENDED'
  tenure_months: number;
  moratorium_months: number;
  annual_interest_rate_pct?: number | null;
  is_market_linked: boolean;
  is_benchmark_assumption: boolean;
  rate_note?: string | null;
  monthly_emi?: number | null;
  total_interest_payable?: number | null;
  total_repayment_amount?: number | null;
  projected_dti_pct?: number | null;
  is_affordable: boolean;
  is_recommended: boolean;
  affordability_notes: string[];
}

export interface StatutoryFinancialBounds {
  min_loan_amount?: number | null;
  max_loan_amount?: number | null;
  min_project_cost?: number | null;
  max_project_cost?: number | null;
  max_subsidy_amount?: number | null;
  interest_rate_min?: number | null;
  interest_rate_max?: number | null;
  tenure_years_max?: number | null;
  moratorium_months?: number | null;
  collateral_required: boolean;
}

export interface FinancialStructuringResponse {
  program_id: number;
  program_code: string;
  program_name: string;
  primary_type: string;
  actionability_type: string;
  is_financing_applicable: boolean;
  assistance_summary: string;
  capital_structure?: CapitalStructureBreakdown | null;
  debt_health: DebtHealthIndicators;
  loan_scenarios: RepaymentScenarioItem[];
  financial_constraints: StatutoryFinancialBounds;
  warnings: string[];
  statutory_checklist: string[];
  disclaimer: string;
}

// ============================================================================
// 4. District Research & Climate Context (GET /api/v1/research/district-market-context)
// ============================================================================

export interface DistrictCoordinates {
  district_id?: number | null;
  district_name: string;
  state_name: string;
  lg_dt_code?: string | null;
  latitude: number;
  longitude: number;
  elevation_meters?: number | null;
  source: string;
}

export interface DistrictMarketContext {
  geographic_level?: string;
  state_name: string;
  state_code?: string | null;
  district_name?: string | null;
  lg_dt_code?: string | null;
  total_msmes: number;
  micro_enterprises: number;
  small_enterprises: number;
  medium_enterprises: number;
  micro_share: number;
  small_share: number;
  medium_share: number;
  small_medium_share: number;
  national_rank?: number | null;
  total_districts_nationally?: number;
  state_rank?: number | null;
  total_districts_in_state?: number | null;
  is_fallback?: boolean;
  market_context_notes?: string[];
  // Backwards compatibility aliases
  total_enterprises?: number;
  state_rank_by_enterprises?: number | null;
  district_share_of_state_pct?: number | null;
  top_5_sectors?: string[] | null;
}

export interface CurrentWeatherMetrics {
  temperature_c: number;
  relative_humidity_pct: number;
  apparent_temperature_c: number;
  precipitation_mm: number;
  weather_code: number;
  weather_description: string;
  wind_speed_kmh: number;
  observed_at?: string | null;
}

export interface DailyForecastDay {
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  precipitation_sum_mm: number;
  precipitation_probability_pct?: number | null;
  wind_speed_max_kmh: number;
  evapotranspiration_mm?: number | null;
  weather_code: number;
  weather_description: string;
}

export interface DistrictWeatherContext {
  is_available: boolean;
  is_stale: boolean;
  source: string;
  fetched_at?: string | null;
  current?: CurrentWeatherMetrics | null;
  forecast_3days: DailyForecastDay[];
  weather_notes: string[];
  // Backwards compatibility aliases
  district_name?: string;
  state_name?: string;
  latitude?: number;
  longitude?: number;
  cached_at?: string | null;
  cache_expires_at?: string | null;
  is_cached?: boolean;
}

export interface DistrictResearchContextResponse {
  district_id?: number | null;
  district_name: string;
  state_name: string;
  lg_dt_code?: string | null;
  geographic_coordinates?: DistrictCoordinates | null;
  msme_market_context?: DistrictMarketContext | null;
  weather_context?: DistrictWeatherContext | null;
  research_observations: string[];
  operational_cautions: string[];
  disclaimer: string;
}

export interface BusinessProfileContext {
  business_type?: string | null;
  sub_type?: string | null;
  experience_level?: string | null;
  target_market?: string | null;
  current_income?: number | null;
  estimated_capital?: number | null;
  existing_debt?: number | null;
  additional_context?: string | null;
}

export interface MarketIntelligenceRequest {
  district_name?: string | null;
  state_name?: string | null;
  lg_dt_code?: string | null;
  business_profile?: BusinessProfileContext | null;
}

export interface ClusterQuantitativeIndicators {
  total_msmes: number;
  micro_enterprises: number;
  small_enterprises: number;
  medium_enterprises: number;
  micro_share: number;
  small_share: number;
  medium_share: number;
  small_medium_share: number;
  national_density_percentile: number;
  state_density_percentile: number;
  sme_depth_score: number;
  market_research_indicator: number;
  cluster_mean_total_msmes: number;
  cluster_mean_micro_share: number;
  cluster_mean_sme_share: number;
}

export interface MarketResearchMLAnalysis {
  is_available: boolean;
  cluster_id: number;
  cluster_label: string;
  cluster_description: string;
  features_used: string[];
  quantitative_indicators: ClusterQuantitativeIndicators;
  cluster_distribution_summary: Record<string, number>;
  methodology_notes: string[];
}

export interface QualitativeLLMAnalysis {
  is_available: boolean;
  source: string;
  market_interpretation: string;
  opportunities: string[];
  operational_considerations: string[];
  competitive_considerations: string[];
  risks: string[];
  practical_recommendations: string[];
  qualitative_notes: string[];
}

export interface WeatherRiskSignals {
  heat_stress: string;
  rain_disruption: string;
  outdoor_activity: string;
  logistics_disruption: string;
}

export interface DailyWeatherOutlookItem {
  date: string;
  day_name: string;
  temp_range: string;
  precipitation_sum_mm: number;
  precipitation_probability_pct?: number | null;
  weather_description: string;
  impact_score: number;
  impact_label: string;
  outdoor_activity_signal: string;
}

export interface WeatherActivityImpactAnalysis {
  is_available: boolean;
  activity_impact_score?: number | null;
  activity_impact_label?: string | null;
  potential_footfall_effect?: string | null;
  risk_signals?: WeatherRiskSignals | null;
  business_type_implication?: string | null;
  weather_outlook_3days: DailyWeatherOutlookItem[];
  methodology_disclaimer: string;
  heuristic_notes: string[];
}

export interface MarketIntelligenceResponse {
  district_id?: number | null;
  district_name: string;
  state_name: string;
  lg_dt_code?: string | null;
  geographic_coordinates?: DistrictCoordinates | null;
  market_context?: DistrictMarketContext | null;
  weather_context?: DistrictWeatherContext | null;
  ml_analysis: MarketResearchMLAnalysis;
  llm_analysis: QualitativeLLMAnalysis;
  weather_activity_impact?: WeatherActivityImpactAnalysis | null;
  comparable_markets?: ComparableMarketContext | null;
  research_observations: string[];
  operational_cautions: string[];
  disclaimer: string;
}

// ============================================================================
// 4.1 NearestNeighbors Market Similarity Schemas
// ============================================================================

export interface ComparableDistrictItem {
  district_id?: number | null;
  district_name: string;
  state_name: string;
  similarity_rank: number;
  similarity_distance: number;
  total_msmes: number;
  micro_share: number;
  small_medium_share: number;
  cluster_label?: string | null;
  qualitative_observation: string;
  provenance: string;
}

export interface ComparableMarketContext {
  is_available: boolean;
  target_district: string;
  target_state: string;
  comparable_districts: ComparableDistrictItem[];
  features_used: string[];
  methodology_notes: string[];
  disclaimer: string;
}

// ============================================================================
// 4.2 Canonical 13-Section Structured DPR Schemas
// ============================================================================

export interface CustomerSegmentItem {
  segment: string;
  need: string;
  buying_consideration: string;
  recommended_channel: string;
  provenance: string;
}

export interface DPRRequest {
  user_id?: string | null;
  business_id?: string | null;
  project_name?: string | null;
  promoter_name?: string | null;
  business_type: string;
  sub_type?: string | null;
  target_market?: string | null;
  experience_level?: string | null;
  estimated_capital: number;
  current_income?: number | null;
  existing_debt?: number | null;
  district_name: string;
  state_name?: string | null;
  lg_dt_code?: string | null;
  location_type?: string | null;
  category?: string | null;
  gender?: string | null;
  education_level?: string | null;
  is_differently_abled?: boolean | null;
  is_ex_serviceman?: boolean | null;
  selected_program_code?: string | null;
  qualitative_overrides?: Record<string, any> | null;
}

export interface DPRExecutiveSummary {
  project_name: string;
  promoter_name: string;
  business_type: string;
  sub_type?: string | null;
  location_district: string;
  location_state: string;
  total_project_cost: number;
  recommended_program_code: string;
  recommended_program_name: string;
  promoter_contribution_amount?: number | null;
  bank_loan_amount: number;
  eligible_subsidy_amount: number;
  monthly_emi: number;
  executive_narrative: string;
  provenance: string;
}

export interface DPRBusinessModel {
  value_proposition: string;
  target_segments_summary: string;
  revenue_streams: string[];
  key_activities: string[];
  key_partners: string[];
  cost_structure_summary: string[];
  provenance: string;
}

export interface DPRMarketAnalysis {
  total_msmes_in_district: number;
  micro_enterprise_share: number;
  small_medium_share: number;
  national_rank?: number | null;
  state_rank?: number | null;
  cluster_archetype_label: string;
  cluster_archetype_description: string;
  market_research_indicator: number;
  comparable_districts: ComparableDistrictItem[];
  demand_drivers: string[];
  market_barriers: string[];
  provenance: string;
}

export interface DPRCustomerSegments {
  customer_segments: CustomerSegmentItem[];
  buying_behaviour_summary: string;
  provenance: string;
}

export interface DPRCompetition {
  competition_intensity: string;
  competition_rationale: string;
  market_structure_type: string;
  differentiation_vectors: string[];
  field_survey_gaps: string[];
  provenance: string;
}

export interface DPRLocationAnalysis {
  district_name: string;
  state_name: string;
  lg_dt_code?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  elevation_meters?: number | null;
  connectivity_advantages: string[];
  raw_material_proximity: string;
  labor_availability: string;
  provenance: string;
}

export interface DPROperationsPlan {
  workflow_steps: string[];
  key_machinery_equipment: string[];
  utilities_and_power: string[];
  workforce_roles: string[];
  quality_assurance: string;
  provenance: string;
}

export interface DPRMarketingStrategy {
  positioning_statement: string;
  sales_channels: string[];
  customer_acquisition_methods: string[];
  pricing_framework: string;
  promotional_initiatives: string[];
  provenance: string;
}

export interface DPRGovernmentSupport {
  program_code: string;
  program_name: string;
  ministry: string;
  program_category: string;
  is_credit_linked: boolean;
  eligible_subsidy_rate_pct?: number | null;
  eligible_subsidy_amount: number;
  max_subsidy_allowed?: number | null;
  eligible_criteria_met: string[];
  mandatory_statutory_conditions: string[];
  nodal_agency: string;
  provenance: string;
}

export interface DPRCapitalStructure {
  total_project_cost: number;
  promoter_equity_amount?: number | null;
  promoter_equity_pct?: number | null;
  initial_bank_loan?: number | null;
  net_bank_loan_exposure?: number | null;
  term_loan_amount?: number | null;
  term_loan_pct?: number | null;
  working_capital_amount?: number | null;
  working_capital_pct?: number | null;
  government_subsidy_amount: number;
  government_subsidy_pct?: number | null;
  is_statutorily_balanced: boolean;
  structuring_notes: string[];
  provenance: string;
}

export interface DebtServiceRepaymentYear {
  year: number;
  opening_balance: number;
  annual_principal: number;
  annual_interest: number;
  total_annual_payment: number;
  closing_balance: number;
}

export interface DPRFinancialAssumptions {
  annual_interest_rate_pct?: number | null;
  loan_tenure_months?: number | null;
  moratorium_months?: number | null;
  monthly_emi: number;
  annual_debt_service: number;
  total_interest_payable: number;
  total_debt_outflow: number;
  is_market_linked?: boolean;
  is_benchmark_assumption?: boolean;
  rate_type?: string | null;
  rate_display_text?: string | null;
  rate_note?: string | null;
  amortization_schedule: DebtServiceRepaymentYear[];
  methodology_notes: string[];
  provenance: string;
}

export interface DPRRiskAnalysis {
  weather_activity_impact_score?: number | null;
  weather_activity_impact_label?: string | null;
  heat_stress_level?: string | null;
  rain_disruption_level?: string | null;
  outdoor_activity_signal?: string | null;
  logistics_disruption_level?: string | null;
  identified_risks: Array<{ risk: string; severity: string; mitigation: string }>;
  contingency_mitigations: string[];
  provenance: string;
}

export interface DPRMilestoneItem {
  phase_number: number;
  month_range: string;
  activity: string;
  critical_deliverable: string;
}

export interface DPRImplementationPlan {
  milestones: DPRMilestoneItem[];
  critical_path_notes: string[];
  provenance: string;
}

export interface DPRIllustrativeAssumptions {
  capacity_utilization_schedule: string[];
  working_capital_cycle_days: number;
  operating_expense_benchmarks: string[];
  break_even_commentary: string;
  disclaimer: string;
  provenance: string;
}

export interface DPRResearchGaps {
  unorganized_data_gaps: string[];
  recommended_field_checks: string[];
  provenance: string;
}

export interface DPRResponse {
  report_id: string;
  generated_at: string;
  project_name: string;
  promoter_name: string;
  business_type: string;
  sub_type?: string | null;
  district_name: string;
  state_name: string;
  lg_dt_code?: string | null;
  executive_summary: DPRExecutiveSummary;
  business_model: DPRBusinessModel;
  market_analysis: DPRMarketAnalysis;
  customer_segments: DPRCustomerSegments;
  competition: DPRCompetition;
  location_analysis: DPRLocationAnalysis;
  operations_plan: DPROperationsPlan;
  marketing_strategy: DPRMarketingStrategy;
  government_support: DPRGovernmentSupport;
  capital_structure: DPRCapitalStructure;
  financial_assumptions: DPRFinancialAssumptions;
  risk_analysis: DPRRiskAnalysis;
  implementation_plan: DPRImplementationPlan;
  illustrative_assumptions: DPRIllustrativeAssumptions;
  research_gaps: DPRResearchGaps;
  provenance_legend: Record<string, string>;
  disclaimer: string;
}

// ============================================================================
// 5. API Client Implementation
// ============================================================================

class BackendApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = getBackendUrl();
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options.headers,
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMsg = `HTTP ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
          }
        } catch {
          // use default status message
        }
        throw new Error(errorMsg);
      }

      return response.json() as Promise<T>;
    } catch (err: any) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error('Backend request timed out (5s). Is the Python FastAPI server running?');
      }
      throw err;
    }
  }

  /**
   * List 60 government programmes with multi-parameter filtering and pagination
   */
  async getPrograms(filters: ProgramQueryParams = {}): Promise<ProgramResponse[]> {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.primary_type) params.append('primary_type', filters.primary_type);
    if (filters.actionability_type) params.append('actionability_type', filters.actionability_type);
    if (filters.ministry) params.append('ministry', filters.ministry);
    if (filters.sector) params.append('sector', filters.sector);
    if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

    const qs = params.toString();
    const endpoint = `/api/v1/programs${qs ? `?${qs}` : ''}`;
    return this.request<ProgramResponse[]>(endpoint, { method: 'GET' });
  }

  /**
   * Get single government programme by database ID or canonical code
   */
  async getProgramById(programIdOrCode: string | number): Promise<ProgramDetailResponse> {
    return this.request<ProgramDetailResponse>(`/api/v1/programs/${programIdOrCode}`, { method: 'GET' });
  }

  /**
   * Generate ranked, explainable programme recommendations (POST /api/v1/recommendations/recommend)
   */
  async getRecommendations(req: RecommendationRequest): Promise<RecommendationResponse> {
    return this.request<RecommendationResponse>('/api/v1/recommendations/recommend', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  /**
   * Generate deterministic financial structuring and amortization scenarios (POST /api/v1/recommendations/financial-structuring)
   */
  async getFinancialStructuring(req: FinancialStructuringRequest): Promise<FinancialStructuringResponse> {
    return this.request<FinancialStructuringResponse>('/api/v1/recommendations/financial-structuring', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  /**
   * Unified district research intelligence (GET /api/v1/research/district-market-context)
   */
  async getDistrictResearchContext(params: {
    district_name?: string;
    state_name?: string;
    lg_dt_code?: string;
  }): Promise<DistrictResearchContextResponse> {
    const search = new URLSearchParams();
    if (params.district_name) search.append('district_name', params.district_name);
    if (params.state_name) search.append('state_name', params.state_name);
    if (params.lg_dt_code) search.append('lg_dt_code', params.lg_dt_code);

    const qs = search.toString();
    return this.request<DistrictResearchContextResponse>(
      `/api/v1/research/district-market-context${qs ? `?${qs}` : ''}`,
      { method: 'GET' }
    );
  }

  /**
   * Unified district market intelligence synthesizing ML clustering and qualitative LLM pipelines
   * POST /api/v1/research/market-intelligence
   */
  async getMarketIntelligence(req: MarketIntelligenceRequest): Promise<MarketIntelligenceResponse> {
    return this.request<MarketIntelligenceResponse>(
      '/api/v1/research/market-intelligence',
      {
        method: 'POST',
        body: JSON.stringify(req),
      }
    );
  }

  /**
   * Evaluate user/business profile against all 60 government programmes using deterministic statutory rules
   * POST /api/v1/programs/evaluate-eligibility
   */
  async evaluatePrograms(profile: UserProfile): Promise<ProgramEligibilityAssessmentResponse> {
    return this.request<ProgramEligibilityAssessmentResponse>('/api/v1/programs/evaluate-eligibility', {
      method: 'POST',
      body: JSON.stringify(profile),
    });
  }

  /**
   * List 12 legacy schemes with optional filtering
   */
  async getLegacySchemes(params: Record<string, string> = {}): Promise<any[]> {
    const search = new URLSearchParams(params);
    const qs = search.toString();
    return this.request<any[]>(`/api/v1/schemes${qs ? `?${qs}` : ''}`, { method: 'GET' });
  }

  /**
   * Get single legacy scheme by ID
   */
  async getLegacySchemeById(schemeId: number): Promise<any> {
    return this.request<any>(`/api/v1/schemes/${schemeId}`, { method: 'GET' });
  }

  /**
   * Generate canonical 13-section Structured Detailed Project Report (DPR)
   * POST /api/v1/advisory/dpr
   */
  async generateDPR(payload: DPRRequest): Promise<DPRResponse> {
    return this.request<DPRResponse>('/api/v1/advisory/dpr', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
}

export const backendApiClient = new BackendApiClient();
export default backendApiClient;

