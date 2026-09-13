import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';

export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const primaryType = searchParams.get('primary_type') || searchParams.get('type') || undefined;
    const actionability = searchParams.get('actionability') || undefined;
    const ministry = searchParams.get('ministry') || undefined;
    const sector = searchParams.get('sector') || undefined;
    const status = searchParams.get('status') || 'active';
    const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 60;
    const skip = searchParams.get('skip') ? parseInt(searchParams.get('skip')!) : 0;

    try {
      const programs = await backendApiClient.getPrograms({
        status,
        primary_type: primaryType,
        actionability_type: actionability,
        ministry,
        sector,
        limit,
        skip,
      });

      // Map to backwards-compatible scheme structure for existing UI components
      const mappedSchemes = programs.map((p) => ({
        id: p.id,
        programCode: p.program_code,
        name: p.program_name,
        ministry: p.owning_ministry,
        nodalAgency: p.nodal_agency,
        description: p.description || p.benefit_summary,
        benefitSummary: p.benefit_summary,
        benefitType: p.benefit_type,
        primaryType: p.primary_type,
        actionabilityType: p.actionability_type,
        officialPortalUrl: p.official_portal_url,
        sectors: p.sectors,
        status: p.status,
        loanMin: null,
        loanMax: p.benefit_headline_numeric || null,
        interestRate: null,
        tenure: null,
        state: 'All India',
      }));

      return NextResponse.json({
        programs,
        schemes: mappedSchemes,
        count: programs.length,
        source: 'FastAPI (PostgreSQL goi_schemes)',
      });
    } catch (backendError: any) {
      console.error('FastAPI getPrograms failed:', backendError);
      return NextResponse.json(
        { error: backendError.message || 'Authoritative government programmes directory is currently unavailable.' },
        { status: 502 }
      );
    }
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Internal server error' }, { status: 500 });
  }
}
