import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { resolvePrimaryBusiness } from '@/lib/business-resolver';

async function getOrInitUser() {
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
  return user;
}

export async function GET(req: Request) {
  try {
    const user = await getOrInitUser();
    const fullUser = await prisma.user.findUnique({
      where: { id: user.id },
    });

    const url = new URL(req.url);
    const requestedBusinessId = url.searchParams.get('businessId');
    const business = await resolvePrimaryBusiness(user.id, requestedBusinessId);

    return NextResponse.json({
      user: fullUser,
      business: business || null,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const user = await getOrInitUser();
    const body = await req.json();

    const {
      name,
      email,
      phone,
      age,
      language,
      state,
      district,
      lgdDistrictCode,
      isRural,
      gender,
      socialCategory,
      isDifferentlyAbled,
      isExServiceman,
      isTraditionalArtisan,
      isStreetVendor,
      isStartup,
      // Business attributes
      sector,
      type,
      businessType,
      activity,
      stage,
      description,
      isNewBusiness,
      // Financial attributes
      projectCost,
      estimatedCapital,
      requestedFinancing,
      promoterContribution,
      annualIncome,
      annualTurnover,
      monthlyIncome,
      monthlyExpenses,
      existingDebt,
      existingMonthlyEmi,
    } = body;

    // --- Validation (Non-business-logic, input integrity only) ---
    if (age !== undefined && age !== null && age !== '') {
      const ageNum = parseInt(age.toString(), 10);
      if (isNaN(ageNum) || ageNum < 14 || ageNum > 120) {
        return NextResponse.json({ error: 'Age must be between 14 and 120 years' }, { status: 400 });
      }
    }

    const validateNonNegative = (val: any, fieldName: string) => {
      if (val !== undefined && val !== null && val !== '') {
        const num = parseFloat(val.toString());
        if (isNaN(num) || num < 0) {
          throw new Error(`${fieldName} must be a valid non-negative number`);
        }
      }
    };

    try {
      validateNonNegative(projectCost, 'Project cost');
      validateNonNegative(requestedFinancing, 'Requested financing');
      validateNonNegative(promoterContribution, 'Promoter contribution');
      validateNonNegative(annualIncome, 'Annual income');
      validateNonNegative(annualTurnover, 'Annual turnover');
      validateNonNegative(monthlyIncome, 'Monthly income');
      validateNonNegative(monthlyExpenses, 'Monthly expenses');
      validateNonNegative(existingDebt, 'Existing debt');
      validateNonNegative(existingMonthlyEmi, 'Existing monthly EMI');
    } catch (valErr: any) {
      return NextResponse.json({ error: valErr.message }, { status: 400 });
    }

    // --- Update User ---
    const updatedUser = await prisma.user.update({
      where: { id: user.id },
      data: {
        ...(name !== undefined && { name }),
        ...(email !== undefined && { email: email === '' ? null : email }),
        ...(age !== undefined && { age: age === null || age === '' ? null : parseInt(age.toString(), 10) }),
        ...(language !== undefined && { language }),
        ...(state !== undefined && { state }),
        ...(district !== undefined && { district }),
        ...(lgdDistrictCode !== undefined && { lgdDistrictCode: lgdDistrictCode === '' ? null : lgdDistrictCode }),
        ...(isRural !== undefined && { isRural: isRural === null ? null : Boolean(isRural) }),
        ...(gender !== undefined && { gender: gender === '' ? null : gender }),
        ...(socialCategory !== undefined && { socialCategory: socialCategory === '' ? null : socialCategory }),
        ...(isDifferentlyAbled !== undefined && { isDifferentlyAbled: isDifferentlyAbled === null ? null : Boolean(isDifferentlyAbled) }),
        ...(isExServiceman !== undefined && { isExServiceman: isExServiceman === null ? null : Boolean(isExServiceman) }),
        ...(isTraditionalArtisan !== undefined && { isTraditionalArtisan: isTraditionalArtisan === null ? null : Boolean(isTraditionalArtisan) }),
        ...(isStreetVendor !== undefined && { isStreetVendor: isStreetVendor === null ? null : Boolean(isStreetVendor) }),
        ...(isStartup !== undefined && { isStartup: isStartup === null ? null : Boolean(isStartup) }),
      },
    });

    // --- Upsert Primary Business ---
    const tradeType = businessType || type;
    const existingBusiness = body.businessId
      ? await prisma.business.findUnique({ where: { id: body.businessId } })
      : await resolvePrimaryBusiness(user.id);

    const parsedProjectCost = projectCost !== undefined && projectCost !== null && projectCost !== ''
      ? parseFloat(projectCost.toString())
      : (estimatedCapital !== undefined && estimatedCapital !== null && estimatedCapital !== '' ? parseFloat(estimatedCapital.toString()) : undefined);

    const businessData: any = {
      ...(sector !== undefined && { sector: sector === '' ? null : sector }),
      ...(tradeType !== undefined && { type: tradeType === '' ? 'General' : tradeType }),
      ...(activity !== undefined && { activity: activity === '' ? null : activity }),
      ...(stage !== undefined && { stage: stage === '' ? null : stage }),
      ...(description !== undefined && { description: description === '' ? null : description }),
      ...(isNewBusiness !== undefined && { isNewBusiness: isNewBusiness === null ? null : Boolean(isNewBusiness) }),
      ...(parsedProjectCost !== undefined && {
        projectCost: parsedProjectCost,
        estimatedCapital: parsedProjectCost,
      }),
      ...(requestedFinancing !== undefined && {
        requestedFinancing: requestedFinancing === null || requestedFinancing === '' ? null : parseFloat(requestedFinancing.toString()),
      }),
      ...(promoterContribution !== undefined && {
        promoterContribution: promoterContribution === null || promoterContribution === '' ? null : parseFloat(promoterContribution.toString()),
      }),
      ...(annualIncome !== undefined && {
        annualIncome: annualIncome === null || annualIncome === '' ? null : parseFloat(annualIncome.toString()),
      }),
      ...(annualTurnover !== undefined && {
        annualTurnover: annualTurnover === null || annualTurnover === '' ? null : parseFloat(annualTurnover.toString()),
      }),
      ...(monthlyIncome !== undefined && {
        monthlyIncome: monthlyIncome === null || monthlyIncome === '' ? null : parseFloat(monthlyIncome.toString()),
      }),
      ...(monthlyExpenses !== undefined && {
        monthlyExpenses: monthlyExpenses === null || monthlyExpenses === '' ? null : parseFloat(monthlyExpenses.toString()),
      }),
      ...(existingDebt !== undefined && {
        existingDebt: existingDebt === null || existingDebt === '' ? null : parseFloat(existingDebt.toString()),
      }),
      ...(existingMonthlyEmi !== undefined && {
        existingMonthlyEmi: existingMonthlyEmi === null || existingMonthlyEmi === '' ? null : parseFloat(existingMonthlyEmi.toString()),
      }),
    };

    let updatedBusiness: any = null;
    if (existingBusiness) {
      updatedBusiness = await prisma.business.update({
        where: { id: existingBusiness.id },
        data: businessData,
      });
    } else {
      updatedBusiness = await prisma.business.create({
        data: {
          userId: user.id,
          type: tradeType || 'General',
          estimatedCapital: parsedProjectCost || 0,
          ...businessData,
        },
      });
    }

    return NextResponse.json({
      user: updatedUser,
      business: updatedBusiness,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
