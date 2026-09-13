"""
app/models/program_models.py

SQLAlchemy declarative models for Government Programme architecture:
- GovernmentProgram
- ProgramSector
- ProgramEligibility
- ProgramCreditDetail
- ProgramGuaranteeDetail
- ProgramSubsidyDetail
- UnifiedProgramSector (Read-only view model)
- UnifiedProgramEligibility (Read-only view model)

Completely isolated from legacy Scheme models.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Numeric,
    DateTime,
    ForeignKey,
)
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class GovernmentProgram(Base):
    """SQLAlchemy model for the 'government_programs' table.
    
    Represents Government of India schemes, subsidies, guarantees, infrastructure,
    and capability support programmes.
    """

    __tablename__ = "government_programs"

    id = Column(Integer, primary_key=True, index=True)
    program_code = Column(String(50), unique=True, nullable=False, index=True)
    program_name = Column(String(255), nullable=False, index=True)
    owning_ministry = Column(String(255), nullable=False, index=True)
    nodal_agency = Column(String(255), nullable=True)
    official_portal_url = Column(Text, nullable=False)
    primary_type = Column(String(50), nullable=False, index=True)
    secondary_types = Column(JSON, nullable=True)
    actionability_type = Column(String(50), nullable=False, index=True)
    hierarchy_level = Column(String(50), nullable=False)
    parent_program_id = Column(
        Integer,
        ForeignKey("government_programs.id", ondelete="SET NULL"),
        nullable=True,
    )
    description = Column(Text, nullable=True)
    benefit_summary = Column(Text, nullable=False)
    benefit_type = Column(String(50), nullable=False)
    benefit_headline_numeric = Column(Numeric(14, 2), nullable=True)
    benefit_headline_percentage = Column(Numeric(5, 2), nullable=True)
    target_beneficiary_summary = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False, index=True)
    legacy_scheme_id = Column(
        Integer,
        ForeignKey("schemes.id", ondelete="RESTRICT"),
        unique=True,
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)

    # Self-referential hierarchy
    parent = relationship(
        "GovernmentProgram",
        remote_side=[id],
        backref="sub_programs",
    )

    # Relationship to legacy Scheme (if applicable)
    legacy_scheme = relationship(
        "Scheme",
        foreign_keys=[legacy_scheme_id],
        uselist=False,
    )

    # Normalized relational extensions
    sectors = relationship(
        "Sector",
        secondary="program_sectors",
        backref="programs_mapped",
        viewonly=True,
    )
    program_sectors = relationship(
        "ProgramSector",
        back_populates="program",
        cascade="all, delete-orphan",
    )
    eligibility = relationship(
        "ProgramEligibility",
        back_populates="program",
        uselist=False,
        cascade="all, delete-orphan",
    )
    credit_details = relationship(
        "ProgramCreditDetail",
        back_populates="program",
        uselist=False,
        cascade="all, delete-orphan",
    )
    guarantee_details = relationship(
        "ProgramGuaranteeDetail",
        back_populates="program",
        uselist=False,
        cascade="all, delete-orphan",
    )
    subsidy_details = relationship(
        "ProgramSubsidyDetail",
        back_populates="program",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<GovernmentProgram id={self.id} code='{self.program_code}' name='{self.program_name}'>"


class ProgramSector(Base):
    """Many-to-many link between government_programs and sectors."""

    __tablename__ = "program_sectors"

    program_id = Column(
        Integer,
        ForeignKey("government_programs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    sector_id = Column(
        Integer,
        ForeignKey("sectors.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=True)

    program = relationship("GovernmentProgram", back_populates="program_sectors")
    sector = relationship("Sector")

    def __repr__(self) -> str:
        return f"<ProgramSector program_id={self.program_id} sector_id={self.sector_id}>"


class ProgramEligibility(Base):
    """Detailed eligibility criteria for government_programs (Option-A semantics)."""

    __tablename__ = "program_eligibility"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(
        Integer,
        ForeignKey("government_programs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    rural_eligible = Column(Boolean, nullable=True)
    urban_eligible = Column(Boolean, nullable=True)
    male_eligible = Column(Boolean, nullable=True)
    female_eligible = Column(Boolean, nullable=True)
    other_gender_eligible = Column(Boolean, nullable=True)
    general_eligible = Column(Boolean, nullable=True)
    sc_eligible = Column(Boolean, nullable=True)
    st_eligible = Column(Boolean, nullable=True)
    obc_eligible = Column(Boolean, nullable=True)
    minority_eligible = Column(Boolean, nullable=True)
    pwd_eligible = Column(Boolean, nullable=True)
    ex_servicemen_eligible = Column(Boolean, nullable=True)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    max_annual_income = Column(Numeric(14, 2), nullable=True)
    target_gender = Column(String(50), nullable=True)
    target_social_categories = Column(String(100), nullable=True)
    artisan_mandate = Column(Boolean, default=False, nullable=True)
    street_vendor_mandate = Column(Boolean, default=False, nullable=True)
    startup_mandate = Column(Boolean, default=False, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)

    program = relationship("GovernmentProgram", back_populates="eligibility")

    def __repr__(self) -> str:
        return f"<ProgramEligibility program_id={self.program_id}>"


class ProgramCreditDetail(Base):
    """Authoritative credit/loan parameters for credit-type programmes."""

    __tablename__ = "program_credit_details"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(
        Integer,
        ForeignKey("government_programs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    min_loan_amount = Column(Numeric(14, 2), nullable=True)
    max_loan_amount = Column(Numeric(14, 2), nullable=True)
    interest_rate_min = Column(Numeric(5, 2), nullable=True)
    interest_rate_max = Column(Numeric(5, 2), nullable=True)
    tenure_years = Column(Numeric(5, 2), nullable=True)
    moratorium_months = Column(Integer, nullable=True)
    collateral_required = Column(Boolean, default=False, nullable=True)
    promoter_contribution_pct = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)

    program = relationship("GovernmentProgram", back_populates="credit_details")

    def __repr__(self) -> str:
        return f"<ProgramCreditDetail program_id={self.program_id} max_loan={self.max_loan_amount}>"


class ProgramGuaranteeDetail(Base):
    """Authoritative guarantee parameters for credit guarantee programmes."""

    __tablename__ = "program_guarantee_details"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(
        Integer,
        ForeignKey("government_programs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    max_credit_limit = Column(Numeric(14, 2), nullable=False)
    guarantee_coverage_pct = Column(Numeric(5, 2), nullable=False)
    annual_guarantee_fee_pct = Column(Numeric(5, 2), nullable=True)
    hybrid_security_allowed = Column(Boolean, default=False, nullable=True)
    eligible_lending_institutions = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)

    program = relationship("GovernmentProgram", back_populates="guarantee_details")

    def __repr__(self) -> str:
        return f"<ProgramGuaranteeDetail program_id={self.program_id} max_limit={self.max_credit_limit}>"


class ProgramSubsidyDetail(Base):
    """Authoritative capital subsidy / grant parameters for subsidy programmes."""

    __tablename__ = "program_subsidy_details"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(
        Integer,
        ForeignKey("government_programs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    subsidy_pct = Column(Numeric(5, 2), nullable=True)
    max_subsidy_amount = Column(Numeric(14, 2), nullable=True)
    min_project_cost = Column(Numeric(14, 2), nullable=True)
    max_project_cost = Column(Numeric(14, 2), nullable=True)
    beneficiary_contribution_pct = Column(Numeric(5, 2), nullable=True)
    disbursement_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)

    program = relationship("GovernmentProgram", back_populates="subsidy_details")

    def __repr__(self) -> str:
        return f"<ProgramSubsidyDetail program_id={self.program_id} max_subsidy={self.max_subsidy_amount}>"


# Read-only View Models
class UnifiedProgramSector(Base):
    """Read-only model mapping to SQL view 'v_unified_program_sectors'."""

    __tablename__ = "v_unified_program_sectors"

    program_id = Column(Integer, primary_key=True)
    sector_id = Column(Integer, primary_key=True)
    program_code = Column(String(50))
    sector_code = Column(String(20))
    sector_name = Column(String(150))

    def __repr__(self) -> str:
        return f"<UnifiedProgramSector program={self.program_code} sector={self.sector_code}>"


class UnifiedProgramEligibility(Base):
    """Read-only model mapping to SQL view 'v_unified_program_eligibility'."""

    __tablename__ = "v_unified_program_eligibility"

    program_id = Column(Integer, primary_key=True)
    program_code = Column(String(50))
    rural_eligible = Column(Boolean)
    urban_eligible = Column(Boolean)
    male_eligible = Column(Boolean)
    female_eligible = Column(Boolean)
    other_gender_eligible = Column(Boolean)
    general_eligible = Column(Boolean)
    sc_eligible = Column(Boolean)
    st_eligible = Column(Boolean)
    obc_eligible = Column(Boolean)
    minority_eligible = Column(Boolean)
    pwd_eligible = Column(Boolean)
    ex_servicemen_eligible = Column(Boolean)
    min_age = Column(Integer)
    max_age = Column(Integer)
    max_annual_income = Column(Numeric(14, 2))
    notes = Column(Text)

    def __repr__(self) -> str:
        return f"<UnifiedProgramEligibility program={self.program_code}>"
