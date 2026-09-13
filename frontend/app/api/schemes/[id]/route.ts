import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';
import { FALLBACK_PROGRAMS } from '@/lib/fallback-data';

export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const program = await backendApiClient.getProgramById(params.id);
    return NextResponse.json({ program, scheme: program });
  } catch (error: any) {
    const fallback = FALLBACK_PROGRAMS.find(
      (p) => String(p.id) === String(params.id) || p.code?.toLowerCase() === params.id.toLowerCase()
    );
    if (fallback) {
      return NextResponse.json({ program: fallback, scheme: fallback });
    }
    return NextResponse.json({ error: error.message || 'Programme not found' }, { status: 404 });
  }
}
