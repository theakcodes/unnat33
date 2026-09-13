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
        advisories: { orderBy: { createdAt: 'desc' }, take: 1 },
        progressLogs: { orderBy: { month: 'asc' } }
      }
    });

    if (!business) return NextResponse.json({ error: 'Business not found' }, { status: 404 });

    const latestPlan: any = business.advisories[0]?.planJson;
    const targetMonthlyIncome = business.targetMonthlyIncome || 50000;

    const chartData = business.progressLogs.map(log => {
      const netProfit = log.actualIncome - log.actualExpense;
      const targetProfit = targetMonthlyIncome * 0.35;
      return {
        month: log.month,
        actualIncome: log.actualIncome,
        actualExpense: log.actualExpense,
        actualProfit: netProfit,
        plannedProfit: targetProfit,
        exceeded: netProfit >= targetProfit
      };
    });

    return NextResponse.json({
      businessId: business.id,
      type: business.type,
      targetMonthlyIncome,
      chartData,
      totalActualIncome: business.progressLogs.reduce((acc, curr) => acc + curr.actualIncome, 0),
      totalActualExpense: business.progressLogs.reduce((acc, curr) => acc + curr.actualExpense, 0),
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
