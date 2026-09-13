"""
tests/test_program_models.py

Unit and integration tests for Phase 4 SQLAlchemy models in app/models/program_models.py:
- GovernmentProgram
- ProgramSector
- ProgramEligibility
- ProgramCreditDetail
- ProgramGuaranteeDetail
- ProgramSubsidyDetail
- UnifiedProgramSector
- UnifiedProgramEligibility

Verifies ORM query execution, relationship eager loading, foreign key integrity,
and unified view mapping without modifying any existing scheme models or data.
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.program_models import (
    GovernmentProgram,
    ProgramSector,
    ProgramEligibility,
    ProgramCreditDetail,
    ProgramGuaranteeDetail,
    ProgramSubsidyDetail,
    UnifiedProgramSector,
    UnifiedProgramEligibility,
)
from app.models.scheme import Scheme
from app.models.master import Sector, SchemeEligibility, SchemeSector


def test_government_program_total_count(db_session: Session):
    """Verify exactly 60 GovernmentProgram records exist (12 legacy + 48 new)."""
    count = db_session.query(GovernmentProgram).count()
    assert count == 60


def test_legacy_program_linkage(db_session: Session):
    """Verify exactly 12 legacy programs are mapped 1:1 to schemes 1-12."""
    legacy_programs = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.legacy_scheme_id.isnot(None))
        .all()
    )
    assert len(legacy_programs) == 12

    linked_scheme_ids = {p.legacy_scheme_id for p in legacy_programs}
    assert linked_scheme_ids == set(range(1, 13))

    # Verify ORM relationship to Scheme
    shishu = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.program_code == "PM_MUDRA_SHISHU")
        .first()
    )
    assert shishu is not None
    assert shishu.legacy_scheme is not None
    assert shishu.legacy_scheme.id == 1
    assert "PM MUDRA - Shishu" in shishu.legacy_scheme.name


def test_new_programs_count_and_null_legacy_id(db_session: Session):
    """Verify all 48 new programs have legacy_scheme_id as NULL."""
    new_programs = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.legacy_scheme_id.is_(None))
        .all()
    )
    assert len(new_programs) == 48


def test_program_credit_details_orm(db_session: Session):
    """Verify credit details relationship for credit-type programs (e.g., STANDUP_INDIA)."""
    su_india = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.program_code == "STANDUP_INDIA")
        .first()
    )
    assert su_india is not None
    assert su_india.primary_type == "CREDIT / LOAN"
    assert su_india.credit_details is not None
    assert su_india.credit_details.min_loan_amount == Decimal("1000000.00")
    assert su_india.credit_details.max_loan_amount == Decimal("10000000.00")
    assert su_india.credit_details.collateral_required is False


def test_program_guarantee_details_orm(db_session: Session):
    """Verify guarantee details relationship for guarantee-type programs (e.g., CGTMSE)."""
    cgtmse = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.program_code == "CGTMSE")
        .first()
    )
    assert cgtmse is not None
    assert cgtmse.primary_type == "CREDIT GUARANTEE"
    assert cgtmse.guarantee_details is not None
    assert cgtmse.guarantee_details.max_credit_limit == Decimal("100000000.00")
    assert cgtmse.guarantee_details.guarantee_coverage_pct == Decimal("85.00")


def test_program_subsidy_details_orm(db_session: Session):
    """Verify subsidy details relationship for subsidy-type programs (e.g., PMFME)."""
    pmfme = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.program_code == "PMFME")
        .first()
    )
    assert pmfme is not None
    assert pmfme.primary_type == "SUBSIDY / CAPITAL ASSISTANCE"
    assert pmfme.subsidy_details is not None
    assert pmfme.subsidy_details.subsidy_pct == Decimal("35.00")
    assert pmfme.subsidy_details.max_subsidy_amount == Decimal("1000000.00")


def test_program_eligibility_orm(db_session: Session):
    """Verify program eligibility criteria can be loaded via ORM."""
    zed = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.program_code == "MSME_ZED")
        .first()
    )
    assert zed is not None
    assert zed.eligibility is not None
    assert zed.eligibility.general_eligible is True
    assert zed.eligibility.sc_eligible is True
    assert zed.eligibility.st_eligible is True
    assert zed.eligibility.female_eligible is True
    assert "Udyam" in (zed.eligibility.notes or "")


def test_program_sectors_orm(db_session: Session):
    """Verify many-to-many sector relationship on GovernmentProgram for new programs."""
    su_india = (
        db_session.query(GovernmentProgram)
        .filter(GovernmentProgram.program_code == "STANDUP_INDIA")
        .first()
    )
    assert su_india is not None
    mapped_codes = {s.sector_code for s in su_india.sectors}
    assert "MFG" in mapped_codes
    assert "SRV" in mapped_codes
    assert "TRD" in mapped_codes
    assert "AGR" in mapped_codes


def test_unified_program_sectors_view(db_session: Session):
    """Verify read-only model UnifiedProgramSector maps to v_unified_program_sectors."""
    total_view_sectors = db_session.query(UnifiedProgramSector).count()
    assert total_view_sectors == 118

    # Query legacy scheme through view
    shishu_sectors = (
        db_session.query(UnifiedProgramSector)
        .filter(UnifiedProgramSector.program_code == "PM_MUDRA_SHISHU")
        .all()
    )
    assert len(shishu_sectors) > 0

    # Query new program through view
    su_sectors = (
        db_session.query(UnifiedProgramSector)
        .filter(UnifiedProgramSector.program_code == "STANDUP_INDIA")
        .all()
    )
    assert len(su_sectors) == 4


def test_unified_program_eligibility_view(db_session: Session):
    """Verify read-only model UnifiedProgramEligibility maps to v_unified_program_eligibility."""
    total_view_eligibility = db_session.query(UnifiedProgramEligibility).count()
    assert total_view_eligibility == 60

    # Test legacy scheme record in view
    legacy_rec = (
        db_session.query(UnifiedProgramEligibility)
        .filter(UnifiedProgramEligibility.program_code == "PM_MUDRA_SHISHU")
        .first()
    )
    assert legacy_rec is not None
    assert legacy_rec.rural_eligible is True
    assert legacy_rec.urban_eligible is True

    # Test new program record in view
    new_rec = (
        db_session.query(UnifiedProgramEligibility)
        .filter(UnifiedProgramEligibility.program_code == "MSME_ZED")
        .first()
    )
    assert new_rec is not None
    assert new_rec.general_eligible is True


def test_legacy_schemes_untouched(db_session: Session):
    """Verify existing schemes table and relationships remain completely untouched."""
    scheme_count = db_session.query(Scheme).count()
    assert scheme_count == 12

    sector_count = db_session.query(Sector).count()
    assert sector_count == 5

    scheme_sector_count = db_session.query(SchemeSector).count()
    assert scheme_sector_count == 25

    scheme_elig_count = db_session.query(SchemeEligibility).count()
    assert scheme_elig_count == 12
