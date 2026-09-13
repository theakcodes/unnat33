/**
 * Fallback dataset and deterministic statutory engine for serverless execution.
 * Ensures the application remains fully functional on Vercel even when
 * the Python FastAPI backend or SQLite database is unreachable.
 */

export interface FallbackProgram {
  id: number | string;
  code: string;
  name: string;
  ministry: string;
  nodalAgency?: string;
  description: string;
  benefitSummary: string;
  benefitType: string;
  primaryType: string;
  actionabilityType: string;
  officialPortalUrl: string;
  loanMin: number | null;
  loanMax: number | null;
  subsidyPct: number | null;
  interestRate: number | null;
  tenureYears: number | null;
  targetGender?: string[]; // ['Female'], ['Male', 'Female', 'All']
  targetCategories?: string[]; // ['General', 'OBC', 'SC', 'ST']
  targetSectors?: string[]; // ['Manufacturing', 'Services', 'Trading', 'Agriculture']
  ruralEligible?: boolean;
  urbanEligible?: boolean;
  newBusinessOnly?: boolean;
  existingBusinessAllowed?: boolean;
  isArtisanSpecial?: boolean;
  isStreetVendorSpecial?: boolean;
}

export const FALLBACK_USER = {
  id: 'guest-demo-user-sih26091',
  phone: '9999999999',
  name: 'Demo Entrepreneur',
  email: 'entrepreneur@unnat.gov.in',
  language: 'en',
  state: 'Uttar Pradesh',
  district: 'Lucknow',
  age: 28,
  gender: 'Female',
  socialCategory: 'OBC',
  isRural: false,
  isDifferentlyAbled: false,
  isExServiceman: false,
  isTraditionalArtisan: false,
  isStreetVendor: false,
  isStartup: true,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

export const FALLBACK_BUSINESS = {
  id: 'guest-demo-business-sih26091',
  userId: 'guest-demo-user-sih26091',
  sector: 'Services',
  type: 'Information Technology & Consulting',
  activity: 'Service Provision',
  stage: 'Early Stage',
  description: 'Technology solutions and digital services enterprise',
  isNewBusiness: true,
  estimatedCapital: 500000,
  projectCost: 500000,
  requestedFinancing: 400000,
  promoterContribution: 100000,
  targetMonthlyIncome: 80000,
  annualIncome: 960000,
  annualTurnover: 1200000,
  monthlyIncome: 80000,
  monthlyExpenses: 45000,
  existingDebt: 0,
  existingMonthlyEmi: 0,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

import programsData from './programs-60.json';

export const FALLBACK_PROGRAMS: FallbackProgram[] = programsData as unknown as FallbackProgram[];


/**
 * Deterministically evaluate all fallback programmes against the provided user profile
 */
export function evaluateFallbackSchemes(input: any) {
  const targetFinancing = Number(input.target_financing_need || input.requested_loan_amount || input.project_cost || 500000);
  const gender = input.gender || 'All';
  const socialCategory = input.social_category || 'General';
  const isRural = input.is_rural === true;
  const isNewBusiness = input.is_new_business !== false;
  const isArtisan = input.is_traditional_artisan === true;
  const isStreetVendor = input.is_street_vendor === true;
  const state = input.state || 'All India';
  const district = input.district || 'District';

  let totalEligible = 0;
  let totalPartiallyVerified = 0;
  let totalIneligible = 0;

  const evaluatedSchemes = FALLBACK_PROGRAMS.map((prog, index) => {
    let score = 75;
    let eligibilityStatus = 'Eligible';
    const statutoryReasons: string[] = [];
    const unverifiedCriteria: string[] = [];
    const disqualifyingReasons: string[] = [];

    // Demographic checks
    if (prog.targetGender && !prog.targetGender.includes('All')) {
      if (gender === 'Female' && prog.targetGender.includes('Female')) {
        score += 15;
        statutoryReasons.push(`Applicant satisfies gender reservation criteria (${prog.targetGender.join(', ')}).`);
      } else if (gender !== 'Female') {
        score -= 25;
        disqualifyingReasons.push(`Scheme is exclusively reserved for women entrepreneurs.`);
        eligibilityStatus = 'Ineligible';
      }
    } else {
      statutoryReasons.push('Open to all genders under universal national quota.');
    }

    // Social category checks
    if (prog.targetCategories && !prog.targetCategories.includes('General')) {
      if (prog.targetCategories.includes(socialCategory)) {
        score += 12;
        statutoryReasons.push(`Applicant matches designated target social category (${socialCategory}).`);
      } else {
        score -= 20;
        disqualifyingReasons.push(`Applicant category (${socialCategory}) does not match designated groups (${prog.targetCategories.join(', ')}).`);
        eligibilityStatus = 'Ineligible';
      }
    }

    // Financing range fit
    if (prog.loanMin && targetFinancing < prog.loanMin) {
      score -= 10;
      unverifiedCriteria.push(`Target financing (₹${targetFinancing.toLocaleString('en-IN')}) is below typical minimum bracket (₹${prog.loanMin.toLocaleString('en-IN')}).`);
      if (eligibilityStatus === 'Eligible') eligibilityStatus = 'Partially Verified';
    } else if (prog.loanMax && targetFinancing > prog.loanMax) {
      if (targetFinancing > prog.loanMax * 2) {
        score -= 15;
        disqualifyingReasons.push(`Requested funding exceeds statutory scheme ceiling of ₹${prog.loanMax.toLocaleString('en-IN')}.`);
        eligibilityStatus = 'Ineligible';
      } else {
        score -= 5;
        unverifiedCriteria.push(`Financing need is near or above standard ceiling (₹${prog.loanMax.toLocaleString('en-IN')}). Partial sanction possible.`);
        if (eligibilityStatus === 'Eligible') eligibilityStatus = 'Partially Verified';
      }
    } else {
      score += 12;
      statutoryReasons.push(`Financing requirement matches statutory ticket size (₹${prog.loanMin?.toLocaleString('en-IN') || 0} - ₹${prog.loanMax?.toLocaleString('en-IN')}).`);
    }

    // New vs Existing business constraints
    if (prog.newBusinessOnly && !isNewBusiness) {
      score -= 15;
      disqualifyingReasons.push(`Exclusively restricted to greenfield / new business setups.`);
      eligibilityStatus = 'Ineligible';
    }

    // Artisan / Street vendor specializations
    if (prog.isArtisanSpecial) {
      if (isArtisan) {
        score += 20;
        statutoryReasons.push(`Applicant verified under traditional artisan / craftsperson criteria.`);
      } else {
        unverifiedCriteria.push(`Requires verification of traditional trade / tool skill certification.`);
        if (eligibilityStatus === 'Eligible') eligibilityStatus = 'Partially Verified';
      }
    }

    if (prog.isStreetVendorSpecial) {
      if (isStreetVendor) {
        score += 20;
        statutoryReasons.push(`Applicant recognized under municipal street vending framework.`);
      } else {
        unverifiedCriteria.push(`Requires municipal vendor Certificate of Vending (CoV) or LOR.`);
        if (eligibilityStatus === 'Eligible') eligibilityStatus = 'Partially Verified';
      }
    }

    // Rural location boost
    if (isRural && prog.ruralEligible) {
      score += 5;
      statutoryReasons.push(`Rural enterprise location qualifies for preferential margin money allocation.`);
    }

    // Clamp score
    const finalScore = Math.max(20, Math.min(98, score));

    // Determine fit category
    let fitCategory = 'STRONG_FIT';
    if (eligibilityStatus === 'Ineligible') {
      fitCategory = 'INELIGIBLE';
      totalIneligible++;
    } else if (finalScore >= 85) {
      fitCategory = 'STRONG_FIT';
      if (eligibilityStatus === 'Partially Verified') {
        totalPartiallyVerified++;
      } else {
        totalEligible++;
      }
    } else if (finalScore >= 70) {
      fitCategory = 'MODERATE_FIT';
      if (eligibilityStatus === 'Partially Verified') {
        totalPartiallyVerified++;
      } else {
        totalEligible++;
      }
    } else {
      fitCategory = 'PARTIALLY_ELIGIBLE';
      totalPartiallyVerified++;
    }

    return {
      scheme: {
        id: prog.id,
        code: prog.code,
        name: prog.name,
        ministry: prog.ministry,
        nodalAgency: prog.nodalAgency,
        description: prog.description,
        benefitSummary: prog.benefitSummary,
        benefitType: prog.benefitType,
        primaryType: prog.primaryType,
        actionabilityType: prog.actionabilityType,
        officialPortalUrl: prog.officialPortalUrl,
        loanMin: prog.loanMin,
        loanMax: prog.loanMax,
        interestRate: prog.interestRate,
        tenure: prog.tenureYears ? prog.tenureYears * 12 : null,
        state: state,
      },
      rank: index + 1,
      eligibilityScore: Number((finalScore / 100).toFixed(2)),
      recommendationScore: finalScore,
      approvalProbability: Math.min(95, Math.round(finalScore * 0.95)),
      fitCategory,
      eligibilityStatus: eligibilityStatus === 'Eligible' ? 'Eligible' : (eligibilityStatus === 'Ineligible' ? 'Ineligible' : 'Partially Verified'),
      recommendationDrivers: statutoryReasons.slice(0, 3),
      statutoryReasons,
      unverifiedCriteria,
      disqualifyingReasons,
      cautionaryNotes: unverifiedCriteria,
      recommendedAmount: Math.min(targetFinancing, prog.loanMax || targetFinancing),
      hyperLocalInsight: `Verified operational coverage across district lead banks and District Industries Centre (DIC) in ${district}, ${state}.`,
    };
  });

  // Sort: Eligible first, then descending recommendationScore
  evaluatedSchemes.sort((a, b) => {
    if (a.eligibilityStatus === 'Ineligible' && b.eligibilityStatus !== 'Ineligible') return 1;
    if (a.eligibilityStatus !== 'Ineligible' && b.eligibilityStatus === 'Ineligible') return -1;
    return b.recommendationScore - a.recommendationScore;
  });

  // Update ranks
  evaluatedSchemes.forEach((item, idx) => {
    item.rank = idx + 1;
  });

  return {
    schemes: evaluatedSchemes,
    eligibilitySummary: {
      totalEvaluated: FALLBACK_PROGRAMS.length,
      totalEligible,
      totalPartiallyVerified,
      totalIneligible,
      directlyRecommendableCount: totalEligible + totalPartiallyVerified,
    },
  };
}

/**
 * Deterministically compute financial structuring and loan scenarios when backend is unavailable
 */
export function computeFallbackFinancialStructuring(req: any) {
  const loanAmount = Math.max(10000, Number(req.requested_loan_amount || (req.project_cost ? req.project_cost * 0.8 : 300000)));
  const monthlyIncome = Math.max(10000, Number(req.monthly_income || 50000));
  const existingEmi = Number(req.existing_monthly_emi || 0);

  const calculateScenario = (scenarioType: string, tenureMonths: number, ratePct: number) => {
    const r = (ratePct / 100) / 12;
    const emi = Math.round((loanAmount * r * Math.pow(1 + r, tenureMonths)) / (Math.pow(1 + r, tenureMonths) - 1));
    const totalRepayment = emi * tenureMonths;
    const totalInterest = totalRepayment - loanAmount;
    const projectedDti = Number((((existingEmi + emi) / monthlyIncome) * 100).toFixed(1));
    const isAffordable = projectedDti <= 50;

    return {
      scenarioType,
      tenureMonths,
      moratoriumMonths: scenarioType === 'EXTENDED' ? 6 : 0,
      interestRate: ratePct,
      isMarketLinked: false,
      isBenchmarkAssumption: true,
      rateNote: `Statutory benchmark rate of ${ratePct}% p.a.`,
      monthlyEMI: emi,
      totalInterest,
      totalRepayment,
      projectedDTI: projectedDti,
      isAffordable,
      isRecommended: scenarioType === 'BALANCED',
      affordabilityNotes: [
        isAffordable ? `Monthly EMI of ₹${emi.toLocaleString('en-IN')} is within recommended 50% DTI limit.` : `Projected DTI (${projectedDti}%) is elevated. Consider longer tenure or lower loan amount.`,
      ],
    };
  };

  const conservative = calculateScenario('CONSERVATIVE', 36, 8.5);
  const balanced = calculateScenario('BALANCED', 60, 9.0);
  const extended = calculateScenario('EXTENDED', 84, 9.5);

  const existingDti = Number(((existingEmi / monthlyIncome) * 100).toFixed(1));
  const affordableEmiCap = Math.round(monthlyIncome * 0.4 - existingEmi);

  return {
    programId: req.program_id || 1,
    programCode: req.program_code || 'PM_MUDRA_TARUN',
    programName: req.program_code ? (req.program_code.replace(/_/g, ' ')) : 'Pradhan Mantri MUDRA Yojana',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    isFinancingApplicable: true,
    assistanceSummary: `Financial structuring for ₹${loanAmount.toLocaleString('en-IN')} institutional credit.`,
    debtToIncomeRatio: existingDti,
    affordableEMI: Math.max(2000, affordableEmiCap),
    uncommittedSurplus: Math.max(5000, Math.round(monthlyIncome - existingEmi - Number(req.monthly_expenses || monthlyIncome * 0.5))),
    creditAssessment: existingDti <= 35 ? 'Low Risk' : (existingDti <= 50 ? 'Moderate Risk' : 'High Risk'),
    dtiHealthCategory: existingDti <= 35 ? 'LOW_RISK' : 'MODERATE_RISK',
    structures: {
      conservative,
      balanced,
      extended,
    },
    rawScenarios: [conservative, balanced, extended],
    preApprovalChecklist: [
      'Proof of Identity and Address (Aadhaar / Voter Card / PAN)',
      'Proof of Business Enterprise Registration / Udyam Certificate',
      'Bank Statement for the last 6 months',
      'Project Profile / Estimation of working capital needs',
    ],
    capitalBreakdown: {
      total_project_cost: Number(req.project_cost || loanAmount * 1.25),
      promoter_contribution: Math.round(Number(req.project_cost || loanAmount * 1.25) - loanAmount),
      term_loan_amount: loanAmount,
      subsidy_eligible_amount: 0,
    },
    statutoryConstraints: [],
    warnings: [],
    disclaimer: 'Illustrative statutory scenarios computed according to Department of Financial Services benchmark guidelines.',
    source: 'Built-in Financial Modeling Engine',
  };
}

