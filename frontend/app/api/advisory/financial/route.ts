import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { backendApiClient, FinancialStructuringRequest } from '@/lib/api-client';
import { resolvePrimaryBusiness } from '@/lib/business-resolver';

const KNOWN_PROGRAM_ALIASES: Record<string, string> = {
  'PMEGP': 'PMEGP_NEW',
  'PMEGP_NEW': 'PMEGP_NEW',
  'STAND_UP_INDIA': 'STANDUP_INDIA',
  'STANDUP_INDIA': 'STANDUP_INDIA',
  'MUDRA_TARUN': 'PM_MUDRA_TARUN',
  'PM_MUDRA_TARUN': 'PM_MUDRA_TARUN',
  'MUDRA_KISHORE': 'PM_MUDRA_KISHORE',
  'PM_MUDRA_KISHORE': 'PM_MUDRA_KISHORE',
  'MUDRA_SHISHU': 'PM_MUDRA_SHISHU',
  'PM_MUDRA_SHISHU': 'PM_MUDRA_SHISHU',
  'CGTMSE': 'CGTMSE',
};

export async function POST(req: Request) {
  try {
    let user = await getCurrentUser();

    // If unauthenticated, ensure a demo guest user exists for public evaluation
    if (!user) {
      user = await prisma.user.upsert({
        where: { phone: '9999999999' },
        update: {},
        create: {
          phone: '9999999999',
          name: 'Demo Entrepreneur',
          language: 'en',
          state: 'Uttar Pradesh',
          district: 'Lucknow',
        },
      });
    }

    const body = await req.json();
    const {
      businessId,
      monthlyIncome,
      monthlyExpenses,
      existingLoans,
      creditHistory,
      loanNeeded,
      projectCost: rawProjectCost,
      purpose,
      preferredTenure,
      collateralAvailable,
      programId,
      programCode,
      advisoryId,
    } = body;

    const [dbUser, dbBusiness] = await Promise.all([
      prisma.user.findUnique({ where: { id: user.id } }),
      businessId
        ? prisma.business.findUnique({ where: { id: businessId } })
        : resolvePrimaryBusiness(user.id),
    ]);

    // Financial Inputs without Fabrication: Require explicit or saved values
    const income = monthlyIncome != null && monthlyIncome !== ''
      ? parseFloat(monthlyIncome.toString())
      : (dbBusiness?.monthlyIncome ?? null);

    const projectCost = rawProjectCost != null && rawProjectCost !== ''
      ? parseFloat(rawProjectCost.toString())
      : (loanNeeded != null && loanNeeded !== ''
          ? parseFloat(loanNeeded.toString())
          : (dbBusiness?.projectCost ?? dbBusiness?.estimatedCapital ?? null));

    const requestedLoan = loanNeeded != null && loanNeeded !== ''
      ? parseFloat(loanNeeded.toString())
      : (body.requestedFinancing != null && body.requestedFinancing !== ''
          ? parseFloat(body.requestedFinancing.toString())
          : (dbBusiness?.requestedFinancing ?? projectCost ?? null));

    if (income == null || isNaN(income) || income <= 0) {
      return NextResponse.json(
        { error: 'Verified monthly disposable income (monthlyIncome > 0) is required for debt serviceability evaluation. Please provide it in your profile or form.' },
        { status: 400 }
      );
    }

    if (projectCost == null || isNaN(projectCost) || projectCost <= 0) {
      return NextResponse.json(
        { error: 'Total project cost (projectCost > 0) is required for deterministic capital structuring. Please provide it in your profile or form.' },
        { status: 400 }
      );
    }

    // Resolve Canonical Scheme Code (zero-fabrication: never default unknown or missing schemes to PMEGP_NEW)
    let resolvedProgramCode: string | undefined = undefined;
    if (programCode && programCode.toString().trim() !== '') {
      const cleanUpper = programCode.toString().trim().toUpperCase();
      resolvedProgramCode = KNOWN_PROGRAM_ALIASES[cleanUpper] || programCode.toString().trim();
    }

    if (!programId && !resolvedProgramCode) {
      return NextResponse.json(
        { error: 'A valid government programme (programId or canonical programCode) is required for deterministic financial structuring. Please select a statutory programme.' },
        { status: 400 }
      );
    }

    const expenses = monthlyExpenses != null && monthlyExpenses !== ''
      ? parseFloat(monthlyExpenses.toString())
      : (dbBusiness?.monthlyExpenses ?? 0.0);

    const existingLoansList = Array.isArray(existingLoans) ? existingLoans : [];
    const totalExistingEmi = existingLoansList.reduce(
      (acc: number, curr: any) => acc + (parseFloat(curr?.emi?.toString() || '0') || 0),
      0
    );
    const finalExistingEmi = totalExistingEmi > 0 ? totalExistingEmi : (dbBusiness?.existingMonthlyEmi ?? 0.0);

    // Demographics and Operational Parameters from Saved Profile (Zero Fabrication)
    const applicantSocialCategory = body.applicant_social_category || body.socialCategory || dbUser?.socialCategory || undefined;
    const applicantGender = body.applicant_gender || body.gender || dbUser?.gender || undefined;
    const isRural = body.is_rural !== undefined ? body.is_rural : (dbUser?.isRural ?? undefined);
    const isNewBusiness = body.is_new_business !== undefined ? body.is_new_business : (dbBusiness?.isNewBusiness ?? undefined);

    // 1. Authoritative Call to FastAPI Backend Core
    const structReq: FinancialStructuringRequest = {
      program_id: programId ? parseInt(programId.toString()) : undefined,
      program_code: resolvedProgramCode,
      project_cost: projectCost,
      requested_loan_amount: requestedLoan || undefined,
      monthly_income: income,
      monthly_expenses: expenses,
      existing_monthly_emi: finalExistingEmi,
      preferred_tenure_months: preferredTenure ? parseInt(preferredTenure.toString()) : undefined,
      applicant_social_category: applicantSocialCategory,
      applicant_gender: applicantGender,
      is_rural: isRural,
      is_new_business: isNewBusiness,
    };

    let financialResult: any;

    try {
      const structResp = await backendApiClient.getFinancialStructuring(structReq);

      const conservativeScenario = structResp.loan_scenarios.find(s => s.scenario_type === 'CONSERVATIVE')
        || structResp.loan_scenarios[0];
      const balancedScenario = structResp.loan_scenarios.find(s => s.scenario_type === 'BALANCED' || s.is_recommended)
        || structResp.loan_scenarios[1]
        || structResp.loan_scenarios[0];
      const extendedScenario = structResp.loan_scenarios.find(s => s.scenario_type === 'EXTENDED')
        || structResp.loan_scenarios[2]
        || structResp.loan_scenarios[structResp.loan_scenarios.length - 1];

      const mapScenario = (s: typeof conservativeScenario) => {
        if (!s) return null;
        return {
          scenarioType: s.scenario_type,
          tenureMonths: s.tenure_months,
          moratoriumMonths: s.moratorium_months,
          interestRate: s.annual_interest_rate_pct ?? null,
          isMarketLinked: s.is_market_linked,
          isBenchmarkAssumption: s.is_benchmark_assumption,
          rateNote: s.rate_note || null,
          monthlyEMI: s.monthly_emi != null ? Math.round(s.monthly_emi) : null,
          totalInterest: s.total_interest_payable != null ? Math.round(s.total_interest_payable) : null,
          totalRepayment: s.total_repayment_amount != null ? Math.round(s.total_repayment_amount) : null,
          projectedDTI: s.projected_dti_pct != null ? Number(s.projected_dti_pct.toFixed(1)) : null,
          isAffordable: s.is_affordable,
          isRecommended: s.is_recommended,
          affordabilityNotes: s.affordability_notes || [],
        };
      };

      financialResult = {
        programId: structResp.program_id,
        programCode: structResp.program_code,
        programName: structResp.program_name,
        primaryType: structResp.primary_type,
        actionabilityType: structResp.actionability_type,
        isFinancingApplicable: structResp.is_financing_applicable,
        assistanceSummary: structResp.assistance_summary,
        debtToIncomeRatio: Number(structResp.debt_health.existing_dti_pct.toFixed(1)),
        affordableEMI: Math.round(structResp.debt_health.affordable_emi_cap),
        uncommittedSurplus: Math.round(structResp.debt_health.uncommitted_surplus),
        creditAssessment: `${structResp.debt_health.dti_health_category.replace(/_/g, ' ')} Risk`,
        dtiHealthCategory: structResp.debt_health.dti_health_category,
        structures: {
          conservative: mapScenario(conservativeScenario),
          balanced: mapScenario(balancedScenario),
          extended: mapScenario(extendedScenario),
        },
        rawScenarios: structResp.loan_scenarios,
        preApprovalChecklist: structResp.statutory_checklist || [],
        capitalBreakdown: structResp.capital_structure,
        statutoryConstraints: structResp.financial_constraints,
        warnings: structResp.warnings,
        disclaimer: structResp.disclaimer,
        source: 'FastAPI Backend Core (Deterministic Financial Structuring)',
      };
    } catch (backendError: any) {
      console.error('FastAPI financial structuring engine error:', backendError);
      return NextResponse.json(
        {
          error: backendError.message || 'The authoritative financial structuring engine is temporarily unavailable.',
        },
        { status: 502 }
      );
    }

    // Link or create business record in Prisma
    let busId = businessId || dbBusiness?.id;
    if (!busId) {
      const bus = await prisma.business.create({
        data: {
          userId: user.id,
          type: purpose || 'General',
          estimatedCapital: projectCost,
          projectCost: projectCost,
          monthlyIncome: income,
        },
      });
      busId = bus.id;
    }

    // Save or update Advisory entity
    let savedAdvisoryId = advisoryId;
    if (savedAdvisoryId) {
      try {
        await prisma.advisory.update({
          where: { id: savedAdvisoryId },
          data: {
            financialJson: JSON.stringify(financialResult),
          },
        });
      } catch (err) {
        console.warn('Could not update existing advisory:', err);
      }
    } else {
      const newAdv = await prisma.advisory.create({
        data: {
          businessId: busId,
          userId: user.id,
          type: 'financial',
          financialJson: JSON.stringify(financialResult),
          status: 'active',
        },
      });
      savedAdvisoryId = newAdv.id;
    }

    return NextResponse.json({
      advisoryId: savedAdvisoryId,
      businessId: busId,
      ...financialResult,
    });
  } catch (error: any) {
    console.error('Error in financial advisory handler:', error);
    return NextResponse.json({ error: error.message || 'Error generating financial advice' }, { status: 500 });
  }
}
