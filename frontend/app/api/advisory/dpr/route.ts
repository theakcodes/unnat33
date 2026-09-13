import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { backendApiClient, DPRRequest } from '@/lib/api-client';
import { resolvePrimaryBusiness } from '@/lib/business-resolver';

export async function POST(req: Request) {
  try {
    const user = await getCurrentUser();
    const body = await req.json();

    let resolvedDistrict = body.district_name || body.district;
    let resolvedState = body.state_name || body.state;
    let resolvedBusinessType = body.business_type || body.sector;
    let resolvedCapital = Number(body.estimated_capital || body.project_cost || body.investmentInPlant || 1000000);
    let resolvedIncome = Number(body.current_income || body.annual_turnover || body.monthly_income ? (body.monthly_income * 12) : 360000);
    let promoterName = body.promoter_name || user?.name || 'Entrepreneur';

    // If user is logged in, attempt to enrich with primary business profile if fields are missing
    if (user && (!resolvedDistrict || !resolvedBusinessType)) {
      try {
        const primaryBiz: any = await resolvePrimaryBusiness(user.id);
        if (primaryBiz) {
          if (!resolvedDistrict) resolvedDistrict = primaryBiz.district || user.district;
          if (!resolvedState) resolvedState = primaryBiz.state || user.state;
          if (!resolvedBusinessType) resolvedBusinessType = primaryBiz.sector || primaryBiz.type;
          if (!body.estimated_capital && (primaryBiz.projectCost || primaryBiz.estimatedCapital)) {
            resolvedCapital = Number(primaryBiz.projectCost || primaryBiz.estimatedCapital);
          }
          if (!body.current_income && (primaryBiz.annualTurnover || primaryBiz.monthlyIncome)) {
            resolvedIncome = Number(primaryBiz.annualTurnover || (primaryBiz.monthlyIncome * 12));
          }
        }
      } catch (err) {
        console.warn('Could not resolve primary business for DPR:', err);
      }
    }

    if (!resolvedDistrict) {
      resolvedDistrict = user?.district || 'Varanasi';
    }
    if (!resolvedState) {
      resolvedState = user?.state || 'Uttar Pradesh';
    }
    if (!resolvedBusinessType) {
      resolvedBusinessType = 'Handloom & Textiles';
    }

    const anyUser: any = user;
    const dprPayload: DPRRequest = {
      user_id: user?.id,
      business_id: body.business_id || body.businessId,
      project_name: body.project_name || `${resolvedBusinessType} Enterprise`,
      promoter_name: promoterName,
      business_type: resolvedBusinessType,
      sub_type: body.sub_type,
      target_market: body.target_market,
      experience_level: body.experience_level,
      estimated_capital: resolvedCapital,
      current_income: resolvedIncome,
      existing_debt: body.existing_debt ? Number(body.existing_debt) : undefined,
      district_name: resolvedDistrict,
      state_name: resolvedState,
      lg_dt_code: body.lg_dt_code,
      location_type: body.location_type || (body.is_rural ? 'RURAL' : 'URBAN'),
      category: body.category || body.social_category || anyUser?.category || 'GENERAL',
      gender: body.gender || anyUser?.gender || 'MALE',
      education_level: body.education_level || 'GRADUATE',
      is_differently_abled: body.is_differently_abled || false,
      is_ex_serviceman: body.is_ex_serviceman || false,
      selected_program_code: body.selected_program_code || body.programCode,
      qualitative_overrides: body.qualitative_overrides,
    };

    const dpr = await backendApiClient.generateDPR(dprPayload);
    return NextResponse.json(dpr);
  } catch (error: any) {
    console.error('Error generating structured DPR in /api/advisory/dpr:', error);
    return NextResponse.json(
      { error: error?.message || 'Failed to generate structured Detailed Project Report' },
      { status: 500 }
    );
  }
}
