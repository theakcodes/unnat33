import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { generateBusinessPlanAI } from '@/lib/claude';
import { resolvePrimaryBusiness } from '@/lib/business-resolver';
import { backendApiClient } from '@/lib/api-client';

export async function POST(req: Request) {
  try {
    let user = await getCurrentUser();
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
      businessType,
      subType,
      experienceLevel,
      targetMarket,
      currentIncome,
      estimatedCapital,
      existingDebt,
      additionalContext,
      targetProgramCode,
      programCode,
      businessId: existingBusinessId
    } = body;

    if (!businessType || !estimatedCapital) {
      return NextResponse.json({ error: 'Business type and capital are required' }, { status: 400 });
    }

    // 1. Resolve existing business or create only if none exists
    let businessId = existingBusinessId;
    if (!businessId) {
      const existing = await resolvePrimaryBusiness(user.id);
      if (existing) {
        businessId = existing.id;
      } else {
        const newBus = await prisma.business.create({
          data: {
            userId: user.id,
            type: businessType,
            description: subType ? `${businessType} - ${subType}` : businessType,
            estimatedCapital: parseFloat(estimatedCapital),
            projectCost: parseFloat(estimatedCapital),
            monthlyIncome: currentIncome ? parseFloat(currentIncome) : null,
            targetMonthlyIncome: currentIncome ? parseFloat(currentIncome) * 1.5 : null,
            existingDebt: existingDebt ? parseFloat(existingDebt) : null,
          }
        });
        businessId = newBus.id;
      }
    }

    // 2. Call Claude AI Business Plan generator service
    const planResult = await generateBusinessPlanAI({
      businessType,
      subType,
      experienceLevel: experienceLevel || 'Beginner',
      targetMarket: targetMarket || 'Local Village / District',
      currentIncome: currentIncome ? parseFloat(currentIncome) : 0,
      estimatedCapital: parseFloat(estimatedCapital),
      existingDebt: existingDebt ? parseFloat(existingDebt) : 0,
      state: user.state || 'Uttar Pradesh',
      district: user.district || 'Lucknow',
      additionalContext,
      language: user.language || 'en'
    });

    const selectedProgramCode = targetProgramCode || programCode || null;

    // 2.1 Authoritative Structured DPR from backend engine
    let dpr: any = null;
    try {
      dpr = await backendApiClient.generateDPR({
        business_type: businessType,
        sub_type: subType,
        experience_level: experienceLevel || 'Experienced',
        target_market: targetMarket,
        estimated_capital: parseFloat(estimatedCapital),
        current_income: currentIncome ? parseFloat(currentIncome) : 360000,
        existing_debt: existingDebt ? parseFloat(existingDebt) : 0,
        district_name: user.district || 'Varanasi',
        state_name: user.state || 'Uttar Pradesh',
        selected_program_code: selectedProgramCode,
      });
    } catch (dprErr) {
      console.warn('Backend DPR generation non-critical warning:', dprErr);
    }

    const finalPlanResult = {
      ...planResult,
      ...(dpr || {}),
      ...(selectedProgramCode && { selectedProgramCode }),
    };

    // 3. Save Advisory record in database
    const advisory = await prisma.advisory.create({
      data: {
        businessId,
        userId: user.id,
        type: 'business_plan',
        planJson: JSON.stringify(finalPlanResult),
        status: 'active'
      }
    });

    return NextResponse.json({
      plan_id: advisory.id,
      businessId,
      advisory,
      ...finalPlanResult
    });
  } catch (error: any) {
    console.error('Error generating business plan:', error);
    return NextResponse.json({ error: error.message || 'Error generating plan' }, { status: 500 });
  }
}
