import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';
import { generateFallbackMarketIntelligence } from '@/lib/fallback-data';

export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  let body: any = {};
  try {
    body = await req.json().catch(() => ({}));
  } catch {
    body = {};
  }

  try {
    const result = await backendApiClient.getMarketIntelligence(body);
    return NextResponse.json(result);
  } catch (error: any) {
    console.warn('FastAPI market intelligence unavailable, serving empirical fallback:', error.message || error);
    const fallback = generateFallbackMarketIntelligence(body);
    return NextResponse.json(fallback);
  }
}
