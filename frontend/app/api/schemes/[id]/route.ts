import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';

export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const program = await backendApiClient.getProgramById(params.id);
    return NextResponse.json({ program, scheme: program });
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Programme not found' }, { status: 404 });
  }
}
