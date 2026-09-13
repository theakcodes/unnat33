import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    const user = await getCurrentUser().catch(() => null);
    if (!user) return NextResponse.json({ advisories: [] });

    try {
      const advisories = await prisma.advisory.findMany({
        where: { userId: user.id },
        include: {
          business: true,
          schemeMatches: true,
        },
        orderBy: { createdAt: 'desc' },
      });
      return NextResponse.json({ advisories });
    } catch (dbErr) {
      console.warn('Advisory history DB query warning, returning empty list:', dbErr);
      return NextResponse.json({ advisories: [] });
    }
  } catch (error: any) {
    console.error('Error fetching advisory history:', error);
    return NextResponse.json({ advisories: [] });
  }
}
