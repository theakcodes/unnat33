import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';
import { generateFallbackMarketIntelligence } from '@/lib/fallback-data';

export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const district = searchParams.get('district_name') || searchParams.get('district') || 'Lucknow';
  const state = searchParams.get('state_name') || searchParams.get('state') || 'Uttar Pradesh';
  const lgDtCode = searchParams.get('lg_dt_code') || undefined;

  try {
    const context = await backendApiClient.getDistrictResearchContext({
      district_name: district,
      state_name: state,
      lg_dt_code: lgDtCode,
    });

    return NextResponse.json(context);
  } catch (error: any) {
    console.warn('FastAPI district context unavailable, serving fallback:', error.message || error);
    const intel = generateFallbackMarketIntelligence({ district_name: district, state_name: state });
    return NextResponse.json({
      district_id: intel.district_id,
      district_name: intel.district_name,
      state_name: intel.state_name,
      lg_dt_code: intel.lg_dt_code,
      geographic_coordinates: intel.geographic_coordinates,
      msme_market_context: intel.market_context,
      weather_context: intel.weather_context,
      research_observations: intel.research_observations,
      operational_cautions: intel.operational_cautions,
    });
  }
}
