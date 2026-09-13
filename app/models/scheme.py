from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Numeric,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class Scheme(Base):
    """SQLAlchemy model for the 'schemes' table.
    
    Represents Indian Central/State Government schemes for MSMEs and entrepreneurs.
    Maps exactly to the live PostgreSQL 'schemes' table.
    """

    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)

    # Basic identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    ministry = Column(String(255), nullable=True, index=True)

    # Classification
    scheme_type = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    business_type = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True, index=True)
    target_group = Column(String(255), nullable=True)

    # Direct eligibility and geographical criteria
    state = Column(String(100), nullable=True, index=True)
    target_gender = Column(String(50), nullable=True)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    rural_only = Column(Boolean, default=False, nullable=True)
    income_limit = Column(Numeric(14, 2), nullable=True)

    # Financial & project cost parameters
    min_project_cost = Column(Numeric(14, 2), nullable=True)
    max_project_cost = Column(Numeric(14, 2), nullable=True)
    loan_percentage = Column(Numeric(5, 2), nullable=True)
    min_loan_amount = Column(Numeric(14, 2), nullable=True)
    max_loan_amount = Column(Numeric(14, 2), nullable=True)
    beneficiary_contribution_percentage = Column(Numeric(5, 2), nullable=True)

    # Subsidy details
    subsidy_percentage = Column(Numeric(5, 2), nullable=True)
    max_subsidy = Column(Numeric(14, 2), nullable=True)

    # Repayment terms
    interest_rate = Column(Numeric(5, 2), nullable=True)
    tenure_years = Column(Numeric(5, 2), nullable=True)
    moratorium_months = Column(Integer, nullable=True)
    repayment_frequency = Column(String(50), nullable=True)

    # Business stage & security requirements
    new_business_only = Column(Boolean, default=False, nullable=True)
    existing_business_allowed = Column(Boolean, default=True, nullable=True)
    collateral_required = Column(Boolean, default=False, nullable=True)

    # Informational / content fields
    benefit = Column(Text, nullable=True)
    eligibility_text = Column(Text, nullable=True)
    documents_required = Column(Text, nullable=True)
    application_url = Column(Text, nullable=True)

    # Status and tracking
    status = Column(String(50), default="active", nullable=True, index=True)
    last_verified = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    # Relationships to normalized schema tables
    eligibility_criteria = relationship(
        "SchemeEligibility",
        back_populates="scheme",
        uselist=False,
        cascade="all, delete-orphan",
    )
    states_mapped = relationship(
        "State",
        secondary="scheme_states",
        back_populates="schemes_mapped",
    )
    sectors_mapped = relationship(
        "Sector",
        secondary="scheme_sectors",
        back_populates="schemes_mapped",
    )

    def __repr__(self) -> str:
        return f"<Scheme id={self.id} name='{self.name}' type='{self.scheme_type}'>"


# Backwards compatibility alias
Schemes = Scheme
