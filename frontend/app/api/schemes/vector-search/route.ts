import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { findMatchingSchemes } from '@/lib/vector';

export async function POST(req: Request) {
  try {
    const user = await getCurrentUser();
    const [dbUser, dbBusiness] = user ? await Promise.all([
      prisma.user.findUnique({ where: { id: user.id } }),
      prisma.business.findFirst({ where: { userId: user.id }, orderBy: { createdAt: 'desc' } }),
    ]) : [null, null];

    const body = await req.json();
    const { businessType, estimatedCapital, state, district, category, isWoman } = body;

    const finalState = state || dbUser?.state;
    const finalDistrict = district || dbUser?.district;

    if (!finalState || !finalDistrict) {
      return NextResponse.json(
        { error: 'State and district location are required to match government schemes.' },
        { status: 400 }
      );
    }

    const advisory = await findMatchingSchemes({
      businessType: businessType || dbBusiness?.sector || undefined,
      estimatedCapital: estimatedCapital ? parseFloat(estimatedCapital.toString()) : (dbBusiness?.projectCost ?? undefined),
      state: finalState,
      district: finalDistrict,
      category: category || dbUser?.socialCategory || undefined,
      isWoman: isWoman !== undefined ? !!isWoman : (dbUser?.gender === 'Female' ? true : undefined),
    });

    return NextResponse.json({
      topMatches: advisory.schemes.slice(0, 10),
      totalMatches: advisory.schemes.length,
      eligibilitySummary: advisory.eligibilitySummary,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
