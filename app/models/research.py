from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class ResearchRequest(Base):
    """User-submitted or system-triggered market research request."""

    __tablename__ = "research_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    business_profile_id = Column(
        Integer,
        ForeignKey("business_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(255), nullable=False)
    target_sector = Column(String(100), nullable=True, index=True)
    target_state = Column(String(100), nullable=True, index=True)
    target_district = Column(String(150), nullable=True)
    query_text = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    parameters = Column(JSON, nullable=True)  # Filter params, constraints, thresholds

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="research_requests")
    business_profile = relationship("BusinessProfile", back_populates="research_requests")
    reports = relationship("ResearchReport", back_populates="research_request", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ResearchRequest id={self.id} title='{self.title}' status='{self.status}'>"


class ResearchReport(Base):
    """Generated market opportunity and scheme recommendation report."""

    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True, index=True)
    research_request_id = Column(
        Integer,
        ForeignKey("research_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    market_analysis = Column(JSON, nullable=True)  # Analytical output from MSME data
    recommended_schemes = Column(JSON, nullable=True)  # Ranked scheme IDs with scores/reasons
    llm_insights = Column(Text, nullable=True)  # Future LLM-generated narrative summary
    status = Column(String(50), default="draft", nullable=False, index=True)  # draft, final, archived

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    research_request = relationship("ResearchRequest", back_populates="reports")

    def __repr__(self) -> str:
        return f"<ResearchReport id={self.id} title='{self.title}'>"


class DataSource(Base):
    """Catalog of datasets and source registries (UDYAM, Schemes, RBI, etc.)."""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # government_portal, csv_ingestion, api, database
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    record_count = Column(BigInteger, default=0, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    metadata_info = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<DataSource id={self.id} name='{self.name}'>"
