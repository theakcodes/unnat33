import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { generateBusinessPlanAI } from '@/lib/claude';
import { resolvePrimaryBusiness } from '@/lib/business-resolver';
import { backendApiClient } from '@/lib/api-client';
import { FALLBACK_USER, FALLBACK_BUSINESS, generateFallbackDPR } from '@/lib/fallback-data';

export async function POST(req: Request) {
  try {
    let user: any = null;
    try {
      user = await getCurrentUser();
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
    } catch (userErr) {
      console.warn('Prisma user lookup warning in business-plan route, using fallback user:', userErr);
      user = FALLBACK_USER;
    }

    const body = await req.json().catch(() => ({}));
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
    if (!businessId && user?.id) {
      try {
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
      } catch (busErr) {
        console.warn('Could not persist business in Prisma:', busErr);
        businessId = FALLBACK_BUSINESS.id;
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

    // 2.1 Authoritative Structured DPR from backend engine or in-process fallback
    let dpr: any = null;
    const dprPayload = {
      business_type: businessType,
      sub_type: subType,
      experience_level: experienceLevel || 'Experienced',
      target_market: targetMarket,
      estimated_capital: parseFloat(estimatedCapital),
      current_income: currentIncome ? parseFloat(currentIncome) : 360000,
      existing_debt: existingDebt ? parseFloat(existingDebt) : 0,
      district_name: user.district || 'Lucknow',
      state_name: user.state || 'Uttar Pradesh',
      selected_program_code: selectedProgramCode || 'PMEGP_NEW',
    };

    try {
      dpr = await backendApiClient.generateDPR(dprPayload);
    } catch (dprErr) {
      console.warn('Backend DPR generation failed in business-plan, using in-process statutory engine:', dprErr);
      dpr = generateFallbackDPR(dprPayload);
    }

    const finalPlanResult = {
      ...planResult,
      ...(dpr || {}),
      ...(selectedProgramCode && { selectedProgramCode }),
    };

    // 3. Save Advisory record in database safely
    let advisory: any = null;
    const planId = `plan-${Date.now()}`;
    try {
      if (user?.id) {
        advisory = await prisma.advisory.create({
          data: {
            businessId: businessId || 'demo-biz',
            userId: user.id,
            type: 'business_plan',
            planJson: JSON.stringify(finalPlanResult),
            status: 'active'
          }
        });
      }
    } catch (advErr) {
      console.warn('Could not persist advisory record in Prisma:', advErr);
    }

    return NextResponse.json({
      plan_id: advisory?.id || planId,
      businessId: businessId || 'demo-biz',
      advisory: advisory || {
        id: planId,
        businessId: businessId || 'demo-biz',
        userId: user.id,
        type: 'business_plan',
        planJson: finalPlanResult,
        status: 'active',
      },
      ...finalPlanResult
    });
  } catch (error: any) {
    console.error('Error generating business plan:', error);
    return NextResponse.json({ error: error.message || 'Error generating plan' }, { status: 500 });
  }
}
