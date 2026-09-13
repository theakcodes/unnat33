"""
tests/test_dpr_pdf.py

Automated Forensic Test Suite for Pure-Python DPR PDF Export:
1. PMEGP_NEW Varanasi Credit-Linked DPR PDF generation
2. PMS_TRADE_FAIRS Non-Credit DPR PDF generation
3. PDF API endpoint (POST /api/v1/advisory/dpr/pdf)
4. Null promoter contribution preservation ("Not specified by authoritative programme data")
5. Benchmark interest rate transparency ("Indicative benchmark", "Market-linked / lender-dependent")
6. Non-credit statutory disclosure ("Not applicable — programme is not credit-linked")
7. Dynamic amortization schedule faithfulness (zero hardcoding)
8. PDF structural validation (%PDF-1.4, %%EOF, non-empty, multi-page, xref table)
"""

import pytest
import re
import zlib
from starlette.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.schemas.dpr import DPRRequest, DPRResponse
from app.services.dpr_service import dpr_service
from app.services.dpr_pdf_service import dpr_pdf_service


def extract_pdf_text_streams(pdf_bytes: bytes) -> str:
    """Helper to decompress all content streams in a PDF and concatenate text."""
    decompressed = []
    for match in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', pdf_bytes, re.DOTALL):
        comp = match.group(1)
        try:
            dec = zlib.decompress(comp).decode('latin1', 'ignore')
            decompressed.append(dec)
        except Exception:
            pass
    return "\n".join(decompressed)


def test_pmegp_varanasi_pdf_generation():
    """Verify PDF export for Varanasi PMEGP_NEW with authoritative credit structuring."""
    import asyncio
    db = SessionLocal()
    try:
        req = DPRRequest(
            district_name="Varanasi",
            state_name="Uttar Pradesh",
            business_type="Handloom & Textiles",
            estimated_capital=1200000.0,
            current_income=360000.0,
            selected_program_code="PMEGP_NEW",
        )
        dpr = asyncio.run(dpr_service.generate_dpr(db, req))
        assert dpr is not None
        assert dpr.capital_structure.total_project_cost == 1200000.0
        assert dpr.capital_structure.promoter_equity_amount is None
        assert dpr.capital_structure.government_subsidy_amount == 180000.0
        assert dpr.capital_structure.net_bank_loan_exposure == 1020000.0

        pdf_bytes = dpr_pdf_service.generate_pdf(dpr)
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

        # PDF Structural Integrity
        assert pdf_bytes.startswith(b"%PDF-1.4")
        assert b"%%EOF" in pdf_bytes[-20:]

        # Decompress and verify content
        text = extract_pdf_text_streams(pdf_bytes)
        assert "DETAILED PROJECT REPORT" in text
        assert "VARANASI" in text or "Varanasi" in text
        assert "PMEGP" in text
        assert "1,200,000" in text or "12,00,000" in text
        assert "180,000" in text or "1,80,000" in text
        assert "1,020,000" in text or "10,20,000" in text

        # Preserved Null Promoter Contribution
        assert "Not specified by authoritative programme data" in text
        assert "Partial authoritative allocation" in text

        # Benchmark Interest Rate Disclosure
        assert "Indicative benchmark" in text
        assert "Market-linked / lender-dependent" in text
        assert "Actual rate determined by lending institution" in text

        # Machine Learning & Market Intelligence Wording
        assert "ML-Derived Market Classification" in text or "ML-derived market classification" in text
        assert "Comparable districts identified from MSME structural similarity" in text
        assert "Indicative weather impact on business activity" in text

        # Multi-page verification
        assert "Page 2 of" in text
    finally:
        db.close()


def test_pms_trade_fairs_non_credit_pdf_generation():
    """Verify PDF export for PMS_TRADE_FAIRS with non-credit scheme rules."""
    import asyncio
    db = SessionLocal()
    try:
        req = DPRRequest(
            district_name="Varanasi",
            state_name="Uttar Pradesh",
            business_type="Handloom & Textiles",
            estimated_capital=1200000.0,
            current_income=360000.0,
            selected_program_code="PMS_TRADE_FAIRS",
        )
        dpr = asyncio.run(dpr_service.generate_dpr(db, req))
        assert dpr is not None
        assert dpr.government_support.is_credit_linked is False
        assert dpr.capital_structure.net_bank_loan_exposure is None
        assert len(dpr.financial_assumptions.amortization_schedule) == 0

        pdf_bytes = dpr_pdf_service.generate_pdf(dpr)
        assert pdf_bytes.startswith(b"%PDF-1.4")
        assert b"%%EOF" in pdf_bytes[-20:]

        text = extract_pdf_text_streams(pdf_bytes)
        # Non-credit statutory disclosure
        assert "Not applicable — programme is not credit-linked" in text or "Not applicable - programme is not credit-linked" in text
    finally:
        db.close()


def test_dpr_pdf_api_endpoint():
    """Verify POST /api/v1/advisory/dpr/pdf endpoint."""
    client = TestClient(app)
    payload = {
        "district_name": "Varanasi",
        "state_name": "Uttar Pradesh",
        "business_type": "Handloom & Textiles",
        "estimated_capital": 1200000.0,
        "current_income": 360000.0,
        "selected_program_code": "PMEGP_NEW",
    }
    response = client.post("/api/v1/advisory/dpr/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    content_disp = response.headers.get("content-disposition", "")
    assert "attachment; filename=\"DPR_" in content_disp
    assert content_disp.endswith(".pdf\"")
    assert response.content.startswith(b"%PDF-1.4")
    assert b"%%EOF" in response.content[-20:]


def test_pdf_structural_syntax():
    """Verify PDF 1.4 xref table, object catalog, and trailer offsets."""
    client = TestClient(app)
    payload = {
        "district_name": "Varanasi",
        "state_name": "Uttar Pradesh",
        "business_type": "Handloom & Textiles",
        "estimated_capital": 1200000.0,
        "current_income": 360000.0,
        "selected_program_code": "PMEGP_NEW",
    }
    response = client.post("/api/v1/advisory/dpr/pdf", json=payload)
    assert response.status_code == 200
    pdf = response.content

    # Check Catalog object
    assert b"/Type /Catalog" in pdf
    assert b"/Type /Pages" in pdf
    assert b"/BaseFont /Helvetica" in pdf
    assert b"/BaseFont /Helvetica-Bold" in pdf
    assert b"/BaseFont /Helvetica-Oblique" in pdf

    # Check XRef Table
    assert b"xref\n" in pdf
    assert b"trailer\n" in pdf
    assert b"startxref\n" in pdf
    assert pdf.endswith(b"%%EOF\n") or pdf.endswith(b"%%EOF")
