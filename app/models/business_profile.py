from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class BusinessProfile(Base):
    """Enterprise profile representing an MSME or entrepreneurial venture."""

    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_name = Column(String(255), nullable=False, index=True)
    registration_type = Column(String(100), nullable=True)  # Proprietorship, Partnership, Pvt Ltd, etc.
    udyam_registration_number = Column(String(50), unique=True, index=True, nullable=True)
    enterprise_type = Column(String(50), nullable=True)  # Micro, Small, Medium
    sector = Column(String(100), nullable=True, index=True)  # Manufacturing, Services, Trading
    nic_code = Column(String(20), nullable=True)  # NIC Activity Code
    state = Column(String(100), nullable=True, index=True)
    district = Column(String(150), nullable=True)
    is_rural = Column(Boolean, default=False, nullable=True)
    annual_turnover = Column(Numeric(14, 2), nullable=True)
    investment_in_plant = Column(Numeric(14, 2), nullable=True)
    employee_count = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="business_profiles")
    research_requests = relationship("ResearchRequest", back_populates="business_profile")

    def __repr__(self) -> str:
        return f"<BusinessProfile id={self.id} name='{self.business_name}' user_id={self.user_id}>"
