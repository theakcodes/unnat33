import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    const user = await getCurrentUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const advisories = await prisma.advisory.findMany({
      where: { userId: user.id },
      include: {
        business: true,
        schemeMatches: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    return NextResponse.json({ advisories });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
