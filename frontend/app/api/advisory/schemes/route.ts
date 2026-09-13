import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { findMatchingSchemes } from '@/lib/vector';

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

    const [dbUser, dbBusiness] = await Promise.all([
      prisma.user.findUnique({ where: { id: user.id } }),
      prisma.business.findFirst({ where: { userId: user.id }, orderBy: { createdAt: 'desc' } }),
    ]);

    const body = await req.json().catch(() => ({}));

    // Assemble profile exclusively from saved user & business profile or explicit caller overrides
    const state = body.state || dbUser?.state || undefined;
    const district = body.district || dbUser?.district || undefined;

    // Check mandatory geographic parameters required by statutory matching
    const missingFields: string[] = [];
    if (!state) missingFields.push('state');
    if (!district) missingFields.push('district');

    if (missingFields.length > 0) {
      return NextResponse.json(
        {
          error: `Please complete your location profile (${missingFields.join(', ')}) to run authoritative government scheme matching.`,
          missingFields,
          schemes: [],
        },
        { status: 400 }
      );
    }

    const projectCost = body.project_cost != null
      ? parseFloat(body.project_cost.toString())
      : (body.estimatedCapital != null
          ? parseFloat(body.estimatedCapital.toString())
          : (dbBusiness?.projectCost ?? dbBusiness?.estimatedCapital ?? undefined));

    const requestedLoanAmount = body.requested_loan_amount != null
      ? parseFloat(body.requested_loan_amount.toString())
      : (dbBusiness?.requestedFinancing ?? projectCost ?? undefined);

    const gender = body.gender || dbUser?.gender || (body.isWoman === true ? 'Female' : (body.isWoman === false ? 'Male' : undefined));
    const socialCategory = body.social_category || dbUser?.socialCategory || body.category || undefined;
    const sector = body.sector || dbBusiness?.sector || body.businessType || dbBusiness?.type || undefined;
    const businessType = body.business_type || dbBusiness?.type || body.businessType || undefined;
    const isRural = body.is_rural !== undefined ? body.is_rural : (dbUser?.isRural ?? undefined);
    const isNewBusiness = body.is_new_business !== undefined ? body.is_new_business : (dbBusiness?.isNewBusiness ?? undefined);
    const age = body.age != null ? parseInt(body.age.toString()) : (dbUser?.age ?? undefined);

    const result = await findMatchingSchemes({
      state,
      district,
      sector,
      business_type: businessType,
      project_cost: projectCost,
      requested_loan_amount: requestedLoanAmount,
      target_financing_need: body.target_financing_need != null ? parseFloat(body.target_financing_need.toString()) : (requestedLoanAmount || projectCost),
      gender,
      social_category: socialCategory,
      is_rural: isRural,
      is_new_business: isNewBusiness,
      age,
      is_differently_abled: body.is_differently_abled !== undefined ? body.is_differently_abled : (dbUser?.isDifferentlyAbled ?? undefined),
      is_ex_serviceman: body.is_ex_serviceman !== undefined ? body.is_ex_serviceman : (dbUser?.isExServiceman ?? undefined),
      is_traditional_artisan: body.is_traditional_artisan !== undefined ? body.is_traditional_artisan : (dbUser?.isTraditionalArtisan ?? undefined),
      is_street_vendor: body.is_street_vendor !== undefined ? body.is_street_vendor : (dbUser?.isStreetVendor ?? undefined),
      annual_income: body.annual_income != null ? parseFloat(body.annual_income.toString()) : (dbBusiness?.annualIncome ?? undefined),
      top_k: body.top_k || 12,
    });

    return NextResponse.json({
      schemes: result.schemes,
      eligibilitySummary: result.eligibilitySummary,
      totalMatches: result.schemes.length,
      userLocation: { state, district },
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'The authoritative recommendation service is currently unavailable.' },
      { status: 502 }
    );
  }
}
