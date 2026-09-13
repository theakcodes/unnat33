from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BusinessProfileBase(BaseModel):
    """Base fields for BusinessProfile."""
    business_name: str = Field(..., description="Trade or business entity name")
    registration_type: Optional[str] = Field(None, description="Legal structure (Proprietorship, Partnership, Pvt Ltd, etc.)")
    udyam_registration_number: Optional[str] = Field(None, description="Government UDYAM registration identifier")
    enterprise_type: Optional[str] = Field(None, description="Enterprise classification: Micro, Small, or Medium")
    sector: Optional[str] = Field(None, description="Sector: Manufacturing, Services, or Trading")
    nic_code: Optional[str] = Field(None, description="NIC activity classification code")
    state: Optional[str] = Field(None, description="Operational state")
    district: Optional[str] = Field(None, description="Operational district")
    is_rural: Optional[bool] = Field(False, description="Whether located in rural jurisdiction")
    annual_turnover: Optional[float] = Field(None, ge=0, description="Annual business turnover in INR")
    investment_in_plant: Optional[float] = Field(None, ge=0, description="Plant, machinery, or equipment investment in INR")
    employee_count: Optional[int] = Field(None, ge=0, description="Number of full-time employees")


class BusinessProfileCreate(BusinessProfileBase):
    """Schema for creating a new business profile."""
    pass


class BusinessProfileUpdate(BaseModel):
    """Schema for partial update of a business profile."""
    business_name: Optional[str] = None
    registration_type: Optional[str] = None
    udyam_registration_number: Optional[str] = None
    enterprise_type: Optional[str] = None
    sector: Optional[str] = None
    nic_code: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    is_rural: Optional[bool] = None
    annual_turnover: Optional[float] = None
    investment_in_plant: Optional[float] = None
    employee_count: Optional[int] = None


class BusinessProfileResponse(BusinessProfileBase):
    """Response schema returned by BusinessProfile API endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
