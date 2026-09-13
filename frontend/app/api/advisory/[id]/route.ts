import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function GET(req: Request, { params }: { params: { id: string } }) {
  try {
    const user = await getCurrentUser();

    const advisory = await prisma.advisory.findUnique({
      where: { id: params.id },
      include: {
        business: true,
        schemeMatches: true,
        reports: true,
      },
    });

    if (!advisory) {
      return NextResponse.json({ error: 'Advisory not found' }, { status: 404 });
    }

    // Allow owner or public demo records
    if (user && advisory.userId !== user.id && advisory.userId !== 'demo-user') {
      // If signed in under different user, allow read-only advisory access if matching
    }

    const parsedPlan = typeof advisory.planJson === 'string' ? JSON.parse(advisory.planJson) : advisory.planJson;
    const parsedFinancial = typeof advisory.financialJson === 'string' ? JSON.parse(advisory.financialJson) : advisory.financialJson;

    return NextResponse.json({
      advisory: {
        ...advisory,
        planJson: parsedPlan,
        financialJson: parsedFinancial,
      }
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function DELETE(req: Request, { params }: { params: { id: string } }) {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    await prisma.advisory.delete({ where: { id: params.id } });
    return NextResponse.json({ deleted: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
