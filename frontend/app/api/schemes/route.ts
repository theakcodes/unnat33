import { NextResponse } from 'next/server';
import { backendApiClient } from '@/lib/api-client';
import { FALLBACK_PROGRAMS } from '@/lib/fallback-data';

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

      // Map to backwards-compatible scheme structure for existing UI components with additive aliases
      const mappedSchemes = programs.map((p) => ({
        id: p.id,
        program_code: p.program_code,
        programCode: p.program_code,
        code: p.program_code,
        name: p.program_name,
        program_name: p.program_name,
        programName: p.program_name,
        ministry: p.owning_ministry,
        owning_ministry: p.owning_ministry,
        nodalAgency: p.nodal_agency,
        nodal_agency: p.nodal_agency,
        description: p.description || p.benefit_summary,
        benefitSummary: p.benefit_summary,
        benefit_summary: p.benefit_summary,
        benefitType: p.benefit_type,
        benefit_type: p.benefit_type,
        primaryType: p.primary_type,
        primary_type: p.primary_type,
        actionabilityType: p.actionability_type,
        actionability_type: p.actionability_type,
        officialPortalUrl: p.official_portal_url,
        official_portal_url: p.official_portal_url,
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
      console.warn('FastAPI getPrograms failed, serving fallback directory:', backendError);
      const mappedSchemes = FALLBACK_PROGRAMS.map((p) => ({
        id: p.id,
        programCode: p.code,
        name: p.name,
        ministry: p.ministry,
        nodalAgency: p.nodalAgency,
        description: p.description || p.benefitSummary,
        benefitSummary: p.benefitSummary,
        benefitType: p.benefitType,
        primaryType: p.primaryType,
        actionabilityType: p.actionabilityType,
        officialPortalUrl: p.officialPortalUrl,
        sectors: p.targetSectors || [],
        status: 'active',
        loanMin: p.loanMin,
        loanMax: p.loanMax,
        interestRate: p.interestRate,
        tenure: p.tenureYears ? p.tenureYears * 12 : null,
        state: 'All India',
      }));

      return NextResponse.json({
        programs: FALLBACK_PROGRAMS,
        schemes: mappedSchemes,
        count: mappedSchemes.length,
        source: 'Built-in Central Government Statutory Directory',
      });
    }
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Internal server error' }, { status: 500 });
  }
}
