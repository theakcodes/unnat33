import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';

export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const result = await backendApiClient.getMarketIntelligence(body);
    return NextResponse.json(result);
  } catch (error: any) {
    console.error('Error fetching market intelligence:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to retrieve market intelligence.' },
      { status: 500 }
    );
  }
}
