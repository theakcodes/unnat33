import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { generateReportData } from '@/lib/pdf';

export async function POST(req: Request) {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const body = await req.json();
    const { businessId, advisoryId } = body;

    if (!businessId) {
      return NextResponse.json({ error: 'businessId is required' }, { status: 400 });
    }

    const reportResult = await generateReportData(businessId, user.id, advisoryId);

    return NextResponse.json(reportResult);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
