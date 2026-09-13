import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';

export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const district = searchParams.get('district_name') || searchParams.get('district') || undefined;
    const state = searchParams.get('state_name') || searchParams.get('state') || undefined;
    const lgDtCode = searchParams.get('lg_dt_code') || undefined;

    if (!district && !state && !lgDtCode) {
      return NextResponse.json(
        { error: 'At least one of district_name, state_name, or lg_dt_code must be provided.' },
        { status: 400 }
      );
    }

    const context = await backendApiClient.getDistrictResearchContext({
      district_name: district,
      state_name: state,
      lg_dt_code: lgDtCode,
    });

    return NextResponse.json(context);
  } catch (error: any) {
    console.error('Error fetching district research context:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to retrieve district research context.' },
      { status: 500 }
    );
  }
}
