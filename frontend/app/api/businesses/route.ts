import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const businesses = await prisma.business.findMany({
      where: { userId: user.id },
      include: {
        advisories: {
          orderBy: { createdAt: 'desc' },
          take: 1
        },
        progressLogs: {
          orderBy: { month: 'desc' },
          take: 1
        }
      },
      orderBy: { createdAt: 'desc' }
    });

    return NextResponse.json({ businesses });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await req.json();
    const { type, description, estimatedCapital, targetMonthlyIncome } = body;

    if (!type || !estimatedCapital) {
      return NextResponse.json({ error: 'Business type and estimated capital are required' }, { status: 400 });
    }

    const business = await prisma.business.create({
      data: {
        userId: user.id,
        type,
        description,
        estimatedCapital: parseFloat(estimatedCapital),
        targetMonthlyIncome: targetMonthlyIncome ? parseFloat(targetMonthlyIncome) : null,
      }
    });

    return NextResponse.json({ business });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
