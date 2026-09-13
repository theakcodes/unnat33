"""
app/api/v1/dpr.py

Advisory and Detailed Project Report (DPR) API Endpoints:
- POST /api/v1/advisory/dpr: Generates the canonical 13-section Structured DPR
  combining official district MSME data, scikit-learn ML & NearestNeighbors,
  weather activity signals, authoritative government recommendations,
  deterministic financial structuring, and bank-grade AI qualitative narrative.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dpr import DPRRequest, DPRResponse
from app.services.dpr_service import dpr_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advisory", tags=["Advisory & DPR"])


@router.post(
    "/dpr",
    response_model=DPRResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate canonical 13-section Structured Detailed Project Report (DPR)",
)
async def generate_dpr(
    payload: DPRRequest,
    db: Session = Depends(get_db),
) -> DPRResponse:
    """
    Generate a bank-ready, 13-section Detailed Project Report (DPR).
    
    Architectural Invariants & Zero-Fabrication Contract:
    - Financial structuring and subsidy computations are deterministic backend calculations.
    - District enterprise density and composition are sourced directly from the PostgreSQL Udyam census.
    - Market classification uses scikit-learn KMeans (K=4); market similarity uses scikit-learn NearestNeighbors.
    - Weather activity signals are transparent product heuristics.
    - Qualitative narrative is synthesized server-side with strict grounding.
    - Every section carries an explicit provenance tag.
    """
    if not payload.business_type or not payload.district_name or payload.estimated_capital <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="business_type, district_name, and a positive estimated_capital are mandatory fields.",
        )

    try:
        response = await dpr_service.generate_dpr(db=db, request=payload)
        return response
    except Exception as e:
        logger.error("Failed to generate DPR: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DPR generation failed: {str(e)}",
        )


@router.post(
    "/dpr/pdf",
    summary="Download Official DPR PDF generated directly from canonical DPRResponse",
)
async def generate_dpr_pdf(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Generate an official downloadable PDF directly from canonical DPRResponse.
    Accepts canonical DPRResponse or DPRRequest.
    Zero frontend math or PDF-side calculations.
    """
    try:
        # 1. If payload contains executive_summary and capital_structure, it is a canonical DPRResponse
        if "capital_structure" in payload and "executive_summary" in payload:
            dpr_obj = DPRResponse.model_validate(payload)
        else:
            # 2. Otherwise generate authoritative DPRResponse first
            req_obj = DPRRequest.model_validate(payload)
            dpr_obj = await dpr_service.generate_dpr(db=db, request=req_obj)

        from app.services.dpr_pdf_service import dpr_pdf_service
        pdf_bytes = dpr_pdf_service.generate_pdf(dpr_obj)
        report_id = dpr_obj.report_id or "REPORT"

        from fastapi import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": f'attachment; filename="DPR_{report_id}.pdf"',
            },
        )
    except Exception as e:
        logger.error("Failed to generate DPR PDF: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DPR PDF export failed: {str(e)}",
        )

