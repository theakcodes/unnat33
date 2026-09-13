import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function GET(req: Request, { params }: { params: { businessId: string } }) {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const logs = await prisma.progressLog.findMany({
      where: { businessId: params.businessId },
      orderBy: { month: 'asc' }
    });

    return NextResponse.json({ logs });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function POST(req: Request, { params }: { params: { businessId: string } }) {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const body = await req.json();
    const { month, actualIncome, actualExpense, notes } = body;

    if (!month || actualIncome === undefined || actualExpense === undefined) {
      return NextResponse.json({ error: 'Month, income, and expense are required' }, { status: 400 });
    }

    const log = await prisma.progressLog.create({
      data: {
        businessId: params.businessId,
        userId: user.id,
        month,
        actualIncome: parseFloat(actualIncome),
        actualExpense: parseFloat(actualExpense),
        notes
      }
    });

    return NextResponse.json({ log });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
