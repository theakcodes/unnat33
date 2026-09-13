from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class SchemeEligibility(Base):
    """Detailed criteria mapped to 'scheme_eligibility' table."""

    __tablename__ = "scheme_eligibility"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(
        Integer,
        ForeignKey("schemes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    rural_eligible = Column(Boolean, default=True, nullable=True)
    urban_eligible = Column(Boolean, default=True, nullable=True)

    male_eligible = Column(Boolean, default=True, nullable=True)
    female_eligible = Column(Boolean, default=True, nullable=True)
    other_gender_eligible = Column(Boolean, default=True, nullable=True)

    general_eligible = Column(Boolean, default=True, nullable=True)
    sc_eligible = Column(Boolean, default=False, nullable=True)
    st_eligible = Column(Boolean, default=False, nullable=True)
    obc_eligible = Column(Boolean, default=False, nullable=True)

    minority_eligible = Column(Boolean, default=False, nullable=True)
    pwd_eligible = Column(Boolean, default=False, nullable=True)
    ex_servicemen_eligible = Column(Boolean, default=False, nullable=True)

    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    max_annual_income = Column(Numeric(14, 2), nullable=True)
    notes = Column(Text, nullable=True)

    scheme = relationship("Scheme", back_populates="eligibility_criteria")


class State(Base):
    """Model for Indian States/UTs in 'states' table."""

    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    state_code = Column(String(10), unique=True, nullable=True)
    state_name = Column(String(100), nullable=False, unique=True)
    region = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=True)

    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")
    schemes_mapped = relationship(
        "Scheme",
        secondary="scheme_states",
        back_populates="states_mapped",
    )
    msme_records = relationship("MsmeStateData", back_populates="state")


class District(Base):
    """Model for Districts in 'districts' table."""

    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    district_code = Column(String(20), unique=True, nullable=True)
    district_name = Column(String(150), nullable=False)
    state_id = Column(
        Integer,
        ForeignKey("states.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, nullable=True)

    state = relationship("State", back_populates="districts")
    msme_records = relationship("MsmeDistrictData", back_populates="district")

    __table_args__ = (
        UniqueConstraint("state_id", "district_name", name="uq_state_district"),
    )


class Sector(Base):
    """Model for Industry/Business Sectors in 'sectors' table."""

    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    sector_code = Column(String(20), unique=True, nullable=True)
    sector_name = Column(String(150), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    activities = relationship("NicActivity", back_populates="sector")
    schemes_mapped = relationship(
        "Scheme",
        secondary="scheme_sectors",
        back_populates="sectors_mapped",
    )


class NicActivity(Base):
    """National Industrial Classification activities in 'nic_activities' table."""

    __tablename__ = "nic_activities"

    id = Column(Integer, primary_key=True, index=True)
    nic_code = Column(String(20), unique=True, nullable=False)
    section_code = Column(String(10), nullable=True)
    division_code = Column(String(10), nullable=True)
    group_code = Column(String(10), nullable=True)
    class_code = Column(String(10), nullable=True)
    activity_name = Column(String(255), nullable=False)
    sector_id = Column(
        Integer,
        ForeignKey("sectors.id", ondelete="SET NULL"),
        nullable=True,
    )
    description = Column(Text, nullable=True)

    sector = relationship("Sector", back_populates="activities")


class SchemeSector(Base):
    """Many-to-many junction table 'scheme_sectors'."""

    __tablename__ = "scheme_sectors"

    scheme_id = Column(
        Integer,
        ForeignKey("schemes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    sector_id = Column(
        Integer,
        ForeignKey("sectors.id", ondelete="CASCADE"),
        primary_key=True,
    )


class SchemeState(Base):
    """Many-to-many junction table 'scheme_states'."""

    __tablename__ = "scheme_states"

    scheme_id = Column(
        Integer,
        ForeignKey("schemes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    state_id = Column(
        Integer,
        ForeignKey("states.id", ondelete="CASCADE"),
        primary_key=True,
    )


class MsmeStateData(Base):
    """Macro MSME demographic data aggregated by State in 'msme_state_data'."""

    __tablename__ = "msme_state_data"

    id = Column(BigInteger, primary_key=True, index=True)
    state_id = Column(
        Integer,
        ForeignKey("states.id", ondelete="CASCADE"),
        nullable=False,
    )
    reporting_date = Column(Date, nullable=True)

    micro_enterprises = Column(BigInteger, default=0, nullable=True)
    small_enterprises = Column(BigInteger, default=0, nullable=True)
    medium_enterprises = Column(BigInteger, default=0, nullable=True)

    manufacturing_enterprises = Column(BigInteger, default=0, nullable=True)
    service_enterprises = Column(BigInteger, default=0, nullable=True)
    trading_enterprises = Column(BigInteger, default=0, nullable=True)

    employment = Column(BigInteger, default=0, nullable=True)

    male_owned = Column(BigInteger, default=0, nullable=True)
    female_owned = Column(BigInteger, default=0, nullable=True)
    other_gender_owned = Column(BigInteger, default=0, nullable=True)

    sc_enterprises = Column(BigInteger, default=0, nullable=True)
    st_enterprises = Column(BigInteger, default=0, nullable=True)
    obc_enterprises = Column(BigInteger, default=0, nullable=True)

    source_name = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)

    state = relationship("State", back_populates="msme_records")


class MsmeDistrictData(Base):
    """Macro MSME demographic data aggregated by District in 'msme_district_data'."""

    __tablename__ = "msme_district_data"

    id = Column(BigInteger, primary_key=True, index=True)
    district_id = Column(
        Integer,
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=False,
    )
    reporting_date = Column(Date, nullable=True)

    micro_enterprises = Column(BigInteger, default=0, nullable=True)
    small_enterprises = Column(BigInteger, default=0, nullable=True)
    medium_enterprises = Column(BigInteger, default=0, nullable=True)

    manufacturing_enterprises = Column(BigInteger, default=0, nullable=True)
    service_enterprises = Column(BigInteger, default=0, nullable=True)
    trading_enterprises = Column(BigInteger, default=0, nullable=True)

    employment = Column(BigInteger, default=0, nullable=True)

    male_owned = Column(BigInteger, default=0, nullable=True)
    female_owned = Column(BigInteger, default=0, nullable=True)

    sc_enterprises = Column(BigInteger, default=0, nullable=True)
    st_enterprises = Column(BigInteger, default=0, nullable=True)
    obc_enterprises = Column(BigInteger, default=0, nullable=True)

    source_name = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)

    district = relationship("District", back_populates="msme_records")


class MsmeActivityData(Base):
    """MSME activity data by sector/NIC code in 'msme_activity_data'."""

    __tablename__ = "msme_activity_data"

    id = Column(BigInteger, primary_key=True, index=True)
    state_id = Column(
        Integer,
        ForeignKey("states.id", ondelete="CASCADE"),
        nullable=True,
    )
    district_id = Column(
        Integer,
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=True,
    )
    nic_activity_id = Column(
        Integer,
        ForeignKey("nic_activities.id", ondelete="SET NULL"),
        nullable=True,
    )
    reporting_date = Column(Date, nullable=True)

    enterprise_count = Column(BigInteger, default=0, nullable=True)
    employment = Column(BigInteger, default=0, nullable=True)
    micro_enterprises = Column(BigInteger, default=0, nullable=True)
    small_enterprises = Column(BigInteger, default=0, nullable=True)
    medium_enterprises = Column(BigInteger, default=0, nullable=True)

    source_name = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
