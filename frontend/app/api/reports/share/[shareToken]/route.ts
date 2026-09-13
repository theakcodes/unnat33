import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(req: Request, { params }: { params: { shareToken: string } }) {
  try {
    const sharedLink = await prisma.sharedLink.findUnique({
      where: { shareToken: params.shareToken },
      include: { report: true }
    });

    if (!sharedLink) {
      return NextResponse.json({ error: 'Shared report link not found' }, { status: 404 });
    }

    if (new Date() > new Date(sharedLink.expiresAt)) {
      return NextResponse.json({ error: 'This shared report link has expired (7 days expiry).' }, { status: 410 });
    }

    // Increment view count
    await prisma.sharedLink.update({
      where: { id: sharedLink.id },
      data: {
        viewCount: { increment: 1 },
        lastViewedAt: new Date()
      }
    });

    return NextResponse.json({
      report: sharedLink.report.jsonData,
      expiresAt: sharedLink.expiresAt,
      viewCount: sharedLink.viewCount + 1
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
