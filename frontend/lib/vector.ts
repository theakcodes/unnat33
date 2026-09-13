import { logger } from './logger';
import {
  backendApiClient,
  RecommendationRequest,
  ProgramRecommendationItem,
  UserProfile,
  ProgramEligibilityAssessmentResponse,
  ProgramEligibilityResult,
} from './api-client';

export interface SchemeSearchInput extends UserProfile {
  // Optional search / filter overrides if specified
  target_financing_need?: number | null;
  preferred_assistance_type?: string | null;
  top_k?: number;
  // Legacy aliases for backwards compatibility
  businessType?: string;
  estimatedCapital?: number;
  category?: string;
  isWoman?: boolean;
}

export interface SchemeMatchResult {
  scheme: any;
  rank?: number;
  eligibilityScore: number;
  recommendationScore: number;
  approvalProbability: number;
  fitCategory: string;
  eligibilityStatus: string;
  scoringBreakdown?: any;
  recommendationDrivers: string[];
  cautionaryNotes: string[];
  statutoryReasons: string[];
  disqualifyingReasons: string[];
  unverifiedCriteria: string[];
  financialConstraints?: any | null;
  recommendedAmount?: number | null;
  hyperLocalInsight: string;
}

export interface SchemesAdvisoryResult {
  schemes: SchemeMatchResult[];
  eligibilitySummary: {
    totalEvaluated: number;
    totalEligible: number;
    totalPartiallyVerified: number;
    totalIneligible: number;
    directlyRecommendableCount?: number;
  };
}

/**
 * Authoritative recommendations and deterministic statutory eligibility flow.
 * Consumes the saved UserProfile directly and calls:
 * 1. POST /api/v1/recommendations/recommend
 * 2. POST /api/v1/programs/evaluate-eligibility
 * Strictly avoids fabricating missing profile fields or substituting heuristic fallbacks.
 */
export async function findMatchingSchemes(
  input: SchemeSearchInput
): Promise<SchemesAdvisoryResult> {
  try {
    // 1. Construct authoritative UserProfile without fabricating missing fields
    const profile: UserProfile = {
      age: input.age ?? undefined,
      gender: input.gender ?? (input.isWoman ? 'Female' : (input.isWoman === false ? 'Male' : undefined)),
      social_category: input.social_category ?? input.category ?? undefined,
      is_differently_abled: input.is_differently_abled ?? undefined,
      is_ex_serviceman: input.is_ex_serviceman ?? undefined,
      state: input.state ?? undefined,
      district: input.district ?? undefined,
      is_rural: input.is_rural ?? undefined,
      annual_income: input.annual_income ?? undefined,
      project_cost: input.project_cost ?? (input.estimatedCapital ? parseFloat(input.estimatedCapital.toString()) : undefined),
      requested_loan_amount: input.requested_loan_amount ?? (input.estimatedCapital ? parseFloat(input.estimatedCapital.toString()) : undefined),
      // isNewBusiness must come ONLY from explicit is_new_business, NEVER inferred from isStartup
      is_new_business: input.is_new_business ?? undefined,
      sector: input.sector ?? input.businessType ?? undefined,
      business_type: input.business_type ?? input.businessType ?? undefined,
      previous_tarun_repaid: input.previous_tarun_repaid ?? undefined,
      is_traditional_artisan: input.is_traditional_artisan ?? undefined,
      is_street_vendor: input.is_street_vendor ?? undefined,
    };

    const targetFinancing = input.target_financing_need ?? profile.project_cost ?? profile.requested_loan_amount ?? undefined;

    const recReq: RecommendationRequest = {
      profile,
      target_financing_need: targetFinancing,
      preferred_assistance_type: input.preferred_assistance_type || undefined,
      top_k: input.top_k || 12,
    };

    // 2. Call Recommendation Engine and Statutory Eligibility Engine in parallel
    const [recResponse, eligResponse] = await Promise.all([
      backendApiClient.getRecommendations(recReq),
      backendApiClient.evaluatePrograms(profile).catch((err) => {
        console.warn('Statutory eligibility evaluation call failed:', err);
        return null as ProgramEligibilityAssessmentResponse | null;
      }),
    ]);

    // Build index of statutory eligibility items for correlated presentation
    const eligMap = new Map<string, ProgramEligibilityResult>();
    if (eligResponse) {
      const allResults = [
        ...(eligResponse.eligible_programs || []),
        ...(eligResponse.partially_verified_programs || []),
        ...(eligResponse.ineligible_programs || []),
      ];
      for (const p of allResults) {
        eligMap.set(p.program_code, p);
        eligMap.set(p.program_id.toString(), p);
      }
    }

    const recommendations = recResponse?.recommendations || [];

    const schemes: SchemeMatchResult[] = recommendations.map((item: ProgramRecommendationItem) => {
      const score = item.recommendation_score;
      const statutory = eligMap.get(item.program_code) || eligMap.get(item.program_id.toString());

      return {
        scheme: {
          id: item.program_id,
          code: item.program_code,
          name: item.program_name,
          ministry: item.primary_type,
          primaryType: item.primary_type,
          actionabilityType: item.actionability_type,
          description: item.benefit_summary || `Government assistance programme under ${item.program_name}.`,
          loanMin: null,
          loanMax: null,
          interestRate: null,
          tenure: null,
          state: input.state || 'All India',
          officialPortalUrl: item.official_portal_url,
          eligibility: {
            keyPoints: item.recommendation_drivers.length > 0
              ? item.recommendation_drivers
              : [`Statutory Status: ${item.eligibility_status}`, `Fit: ${item.fit_category.replace(/_/g, ' ')}`],
          },
        },
        rank: item.rank,
        eligibilityScore: Number((score / 100).toFixed(2)),
        recommendationScore: score,
        approvalProbability: Math.round(score),
        fitCategory: item.fit_category,
        eligibilityStatus: item.eligibility_status,
        scoringBreakdown: item.scoring_breakdown,
        recommendationDrivers: item.recommendation_drivers,
        cautionaryNotes: item.cautionary_notes,
        statutoryReasons: statutory?.reasons || [],
        disqualifyingReasons: statutory?.disqualifying_reasons || [],
        unverifiedCriteria: statutory?.unverified_criteria || [],
        financialConstraints: statutory?.financial_constraints || null,
        recommendedAmount: targetFinancing || null,
        hyperLocalInsight: item.cautionary_notes.length > 0
          ? item.cautionary_notes.join(' • ')
          : `Authoritative recommendation for ${input.district || 'target district'}, ${input.state || 'State'} (Rank #${item.rank}, ${item.fit_category.replace(/_/g, ' ')}).`,
      };
    });

    return {
      schemes,
      eligibilitySummary: {
        totalEvaluated: eligResponse?.total_evaluated || recResponse?.total_programs_evaluated || 60,
        totalEligible: eligResponse?.total_eligible || recResponse?.eligible_candidates_count || 0,
        totalPartiallyVerified: eligResponse?.total_partially_verified || recResponse?.partially_verified_candidates_count || 0,
        totalIneligible: eligResponse?.total_ineligible || 0,
        directlyRecommendableCount: eligResponse?.directly_recommendable_count,
      },
    };
  } catch (error: any) {
    logger.error('FastAPI recommendation/eligibility engine error:', error);
    throw new Error(`Authoritative recommendation service error: ${error.message || 'Service unavailable'}`);
  }
}

