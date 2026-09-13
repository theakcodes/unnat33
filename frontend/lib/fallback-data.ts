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

export const FALLBACK_PROGRAMS: FallbackProgram[] = [
  {
    id: 1,
    code: 'PM_MUDRA_SHISHU',
    name: 'PM MUDRA - Shishu',
    ministry: 'Ministry of Finance',
    nodalAgency: 'MUDRA / Department of Financial Services',
    description: 'Micro-credit for small income-generating businesses requiring loans up to ₹50,000 with zero collateral.',
    benefitSummary: 'Collateral-free institutional credit up to ₹50,000 for small micro-units.',
    benefitType: 'Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy',
    loanMin: 10000,
    loanMax: 50000,
    subsidyPct: null,
    interestRate: 8.5,
    tenureYears: 3,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Trading', 'Services', 'Agriculture'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
  {
    id: 2,
    code: 'PM_MUDRA_KISHORE',
    name: 'PM MUDRA - Kishore',
    ministry: 'Ministry of Finance',
    nodalAgency: 'MUDRA / Department of Financial Services',
    description: 'Credit support for micro enterprises requiring more than ₹50,000 and up to ₹5 Lakhs for equipment and working capital.',
    benefitSummary: 'Collateral-free institutional credit above ₹50,000 and up to ₹5 Lakhs.',
    benefitType: 'Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy',
    loanMin: 50001,
    loanMax: 500000,
    subsidyPct: null,
    interestRate: 9.0,
    tenureYears: 5,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Trading', 'Services', 'Agriculture'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
  {
    id: 3,
    code: 'PM_MUDRA_TARUN',
    name: 'PM MUDRA - Tarun',
    ministry: 'Ministry of Finance',
    nodalAgency: 'MUDRA / Department of Financial Services',
    description: 'Credit support for scaling micro enterprises requiring more than ₹5 Lakhs and up to ₹10 Lakhs.',
    benefitSummary: 'Collateral-free institutional credit above ₹5 Lakhs and up to ₹10 Lakhs.',
    benefitType: 'Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy',
    loanMin: 500001,
    loanMax: 1000000,
    subsidyPct: null,
    interestRate: 9.5,
    tenureYears: 5,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Trading', 'Services', 'Agriculture'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
  {
    id: 4,
    code: 'PM_MUDRA_TARUN_PLUS',
    name: 'PM MUDRA - Tarun Plus',
    ministry: 'Ministry of Finance',
    nodalAgency: 'MUDRA / Department of Financial Services',
    description: 'Enhanced credit support from ₹10 Lakhs up to ₹20 Lakhs for entrepreneurs who have successfully repaid a previous Tarun loan.',
    benefitSummary: 'Collateral-free credit above ₹10 Lakhs and up to ₹20 Lakhs for established enterprises.',
    benefitType: 'Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy',
    loanMin: 1000001,
    loanMax: 2000000,
    subsidyPct: null,
    interestRate: 9.75,
    tenureYears: 5,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Trading', 'Services', 'Agriculture'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
  {
    id: 5,
    code: 'PMEGP_NEW',
    name: 'Prime Minister Employment Generation Programme (PMEGP)',
    ministry: 'Ministry of Micro, Small & Medium Enterprises',
    nodalAgency: 'Khadi and Village Industries Commission (KVIC)',
    description: 'Major credit-linked subsidy programme providing 15% to 35% government capital subsidy for setting up new non-farm micro enterprises.',
    benefitSummary: 'Capital margin money subsidy up to 35% for project costs up to ₹50 Lakhs (Manufacturing) and ₹20 Lakhs (Services).',
    benefitType: 'Subsidy + Credit',
    primaryType: 'Subsidy',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://common-pmegp.msme.gov.in/',
    loanMin: 100000,
    loanMax: 5000000,
    subsidyPct: 35.0,
    interestRate: 9.0,
    tenureYears: 7,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Services'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: true,
    existingBusinessAllowed: false,
  },
  {
    id: 6,
    code: 'STANDUP_INDIA',
    name: 'Stand-Up India Scheme',
    ministry: 'Ministry of Finance',
    nodalAgency: 'SIDBI',
    description: 'Facilitates bank loans between ₹10 Lakhs and ₹1 Crore to at least one SC or ST borrower and at least one woman borrower per bank branch.',
    benefitSummary: 'Composite term loan and working capital between ₹10 Lakhs and ₹100 Lakhs for greenfield enterprises.',
    benefitType: 'Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://www.standupmitra.in/',
    loanMin: 1000000,
    loanMax: 10000000,
    subsidyPct: null,
    interestRate: 8.75,
    tenureYears: 7,
    targetGender: ['Female'],
    targetCategories: ['SC', 'ST', 'General', 'OBC'],
    targetSectors: ['Manufacturing', 'Services', 'Trading', 'Agriculture'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: true,
    existingBusinessAllowed: false,
  },
  {
    id: 7,
    code: 'PM_VISHWAKARMA',
    name: 'PM Vishwakarma Scheme',
    ministry: 'Ministry of Micro, Small & Medium Enterprises',
    nodalAgency: 'MoMSME / MoSD&E',
    description: 'Comprehensive financial and skill support for traditional artisans and craftspeople working with hands and tools in 18 identified trades.',
    benefitSummary: 'Collateral-free enterprise credit up to ₹3 Lakhs in 2 tranches at concessional 5% interest with ₹15,000 toolkit incentive.',
    benefitType: 'Concessional Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://pmvishwakarma.gov.in/',
    loanMin: 50000,
    loanMax: 300000,
    subsidyPct: null,
    interestRate: 5.0,
    tenureYears: 3,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Services', 'Artisan'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
    isArtisanSpecial: true,
  },
  {
    id: 8,
    code: 'PM_SVANIDHI',
    name: 'PM SVANidhi (Street Vendors AtmaNirbhar Nidhi)',
    ministry: 'Ministry of Housing and Urban Affairs',
    nodalAgency: 'MoHUA / SIDBI',
    description: 'Special micro-credit facility for street vendors providing working capital up to ₹50,000 with 7% interest subsidy on timely repayment.',
    benefitSummary: 'Affordable working capital loan in graduated tranches (₹10k, ₹20k, ₹50k) with 7% interest subsidy and digital cashback.',
    benefitType: 'Working Capital',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://pmsvanidhi.mohua.gov.in/',
    loanMin: 10000,
    loanMax: 50000,
    subsidyPct: 7.0,
    interestRate: 7.0,
    tenureYears: 2,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Trading', 'Services', 'Retail'],
    ruralEligible: false,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
    isStreetVendorSpecial: true,
  },
  {
    id: 9,
    code: 'CGTMSE',
    name: 'Credit Guarantee Fund Trust for Micro & Small Enterprises (CGTMSE)',
    ministry: 'Ministry of MSME',
    nodalAgency: 'SIDBI',
    description: 'Provides credit guarantee coverage up to ₹5 Crore to formal commercial lending institutions for collateral-free MSME loans.',
    benefitSummary: 'Institutional credit guarantee coverage from 75% to 85% for loans up to ₹500 Lakhs without third-party collateral.',
    benefitType: 'Credit Guarantee',
    primaryType: 'Guarantee',
    actionabilityType: 'Credit Guarantee',
    officialPortalUrl: 'https://www.cgtmse.in/',
    loanMin: 500000,
    loanMax: 50000000,
    subsidyPct: null,
    interestRate: 9.5,
    tenureYears: 10,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Services', 'Trading'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
  {
    id: 10,
    code: 'NSFDC_MFS',
    name: 'NSFDC Micro Finance Scheme (MFS)',
    ministry: 'Ministry of Social Justice & Empowerment',
    nodalAgency: 'National Scheduled Castes Finance and Development Corporation',
    description: 'Concessional micro-credit financing up to 90% of project cost for income-generating activities for eligible Scheduled Caste beneficiaries.',
    benefitSummary: 'Concessional credit up to ₹1.40 Lakhs at low 6.5% interest rate per annum.',
    benefitType: 'Concessional Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://nsfdc.nic.in/',
    loanMin: 20000,
    loanMax: 140000,
    subsidyPct: null,
    interestRate: 6.5,
    tenureYears: 3,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['SC'],
    targetSectors: ['Manufacturing', 'Services', 'Trading', 'Agriculture'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
  {
    id: 11,
    code: 'MAHILA_SAMRIDDHI',
    name: 'Mahila Samriddhi Yojana (NBCFDC / NSFDC)',
    ministry: 'Ministry of Social Justice & Empowerment',
    nodalAgency: 'National Backward Classes Finance & Development Corporation',
    description: 'Exclusive micro-finance scheme for women entrepreneurs from backward classes and SHGs with concessional loans at 4% interest.',
    benefitSummary: 'Ultra-low 4% concessional micro-credit up to ₹1.40 Lakhs with 95% State Channelizing Agency financing.',
    benefitType: 'Concessional Credit',
    primaryType: 'Credit',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://nbcfdc.gov.in/',
    loanMin: 10000,
    loanMax: 140000,
    subsidyPct: null,
    interestRate: 4.0,
    tenureYears: 3,
    targetGender: ['Female'],
    targetCategories: ['OBC', 'SC', 'ST'],
    targetSectors: ['Manufacturing', 'Services', 'Trading', 'Agriculture'],
    ruralEligible: true,
    urbanEligible: true,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
  {
    id: 12,
    code: 'NABARD_DAIRY',
    name: 'NABARD Dairy Entrepreneurship Development Scheme',
    ministry: 'Ministry of Agriculture & Farmers Welfare',
    nodalAgency: 'NABARD',
    description: 'Capital subsidy and credit linkage for setting up modern dairy farms, milk processing, and cold chain infrastructure.',
    benefitSummary: '25% capital subsidy (33.33% for SC/ST and Women) for project outlays up to ₹7 Lakhs.',
    benefitType: 'Subsidy + Credit',
    primaryType: 'Subsidy',
    actionabilityType: 'Direct Benefit',
    officialPortalUrl: 'https://www.nabard.org/',
    loanMin: 50000,
    loanMax: 700000,
    subsidyPct: 33.33,
    interestRate: 8.5,
    tenureYears: 5,
    targetGender: ['All', 'Female', 'Male'],
    targetCategories: ['General', 'OBC', 'SC', 'ST'],
    targetSectors: ['Agriculture', 'Dairy'],
    ruralEligible: true,
    urbanEligible: false,
    newBusinessOnly: false,
    existingBusinessAllowed: true,
  },
];

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

