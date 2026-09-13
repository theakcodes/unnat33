import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function GET(req: Request, { params }: { params: { businessId: string } }) {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const business = await prisma.business.findUnique({
      where: { id: params.businessId },
      include: {
        advisories: {
          include: { schemeMatches: true },
          orderBy: { createdAt: 'desc' }
        },
        progressLogs: {
          orderBy: { month: 'asc' }
        }
      }
    });

    if (!business || business.userId !== user.id) {
      return NextResponse.json({ error: 'Business not found' }, { status: 404 });
    }

    return NextResponse.json({ business });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function PUT(req: Request, { params }: { params: { businessId: string } }) {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const body = await req.json();
    const { type, description, estimatedCapital, targetMonthlyIncome } = body;

    const business = await prisma.business.update({
      where: { id: params.businessId },
      data: {
        ...(type && { type }),
        ...(description !== undefined && { description }),
        ...(estimatedCapital && { estimatedCapital: parseFloat(estimatedCapital) }),
        ...(targetMonthlyIncome !== undefined && { targetMonthlyIncome: parseFloat(targetMonthlyIncome) }),
      }
    });

    return NextResponse.json({ business });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function DELETE(req: Request, { params }: { params: { businessId: string } }) {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    await prisma.business.delete({ where: { id: params.businessId } });
    return NextResponse.json({ deleted: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
