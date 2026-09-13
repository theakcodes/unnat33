import { prisma } from './prisma';

export async function generateReportData(businessId: string, userId: string, advisoryId?: string) {
  const business = await prisma.business.findUnique({
    where: { id: businessId },
    include: {
      user: true,
      advisories: {
        orderBy: { createdAt: 'desc' },
        take: 3,
        include: { schemeMatches: true }
      },
      progressLogs: {
        orderBy: { month: 'asc' }
      }
    }
  });

  if (!business) throw new Error('Business not found');

  const mainAdvisory = advisoryId
    ? business.advisories.find(a => a.id === advisoryId)
    : business.advisories[0];

  const reportData = {
    title: `UnnatE Hyper-Local Business Advisory & DPR Report`,
    generatedAt: new Date().toISOString(),
    user: {
      name: business.user.name,
      phone: business.user.phone,
      state: business.user.state,
      district: business.user.district,
    },
    business: {
      id: business.id,
      type: business.type,
      description: business.description,
      estimatedCapital: business.estimatedCapital,
      targetMonthlyIncome: business.targetMonthlyIncome,
    },
    advisory: mainAdvisory ? {
      id: mainAdvisory.id,
      type: mainAdvisory.type,
      planJson: mainAdvisory.planJson,
      financialJson: mainAdvisory.financialJson,
      schemeMatches: mainAdvisory.schemeMatches
    } : null,
    progress: business.progressLogs
  };

  // Set report expiration to 7 days
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 7);

  const report = await prisma.report.create({
    data: {
      businessId,
      userId,
      advisoryId: mainAdvisory?.id || null,
      jsonData: reportData as any,
      expiresAt,
    }
  });

  // Create shareable token link
  const shareToken = `unnate_rpt_${Math.random().toString(36).substring(2, 12)}_${Date.now()}`;
  const sharedLink = await prisma.sharedLink.create({
    data: {
      reportId: report.id,
      shareToken,
      expiresAt,
    }
  });

  return {
    reportId: report.id,
    shareToken: sharedLink.shareToken,
    shareUrl: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/reports/share/${sharedLink.shareToken}`,
    expiresAt: report.expiresAt,
    reportData
  };
}
