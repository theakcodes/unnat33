import { NextResponse } from 'next/server';
import { API_BASE_URL } from '@/lib/constants';
import { logger } from '@/lib/logger';

const getBackendUrl = (): string => {
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || API_BASE_URL;
};

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const backendUrl = getBackendUrl();

    // Proxy canonical DPR data to FastAPI backend PDF export endpoint
    const response = await fetch(`${backendUrl}/api/v1/advisory/dpr/pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/pdf',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errText = await response.text();
      logger.error('Backend DPR PDF generation failed:', response.status, errText);
      return NextResponse.json(
        { error: `PDF export failed on backend (${response.status}): ${errText}` },
        { status: response.status }
      );
    }

    const pdfBuffer = await response.arrayBuffer();
    const reportId = body.report_id || body.reportId || 'REPORT';
    const filename = `DPR_${reportId}.pdf`;

    return new Response(pdfBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error: any) {
    logger.error('Error generating DPR PDF:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error while exporting DPR PDF' },
      { status: 500 }
    );
  }
}
