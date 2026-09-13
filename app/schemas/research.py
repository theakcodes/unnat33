from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ResearchRequestBase(BaseModel):
    """Base fields for a research request."""
    title: str = Field(..., description="Research query title")
    target_sector: Optional[str] = Field(None, description="Focus sector for market exploration")
    target_state: Optional[str] = Field(None, description="Target state")
    target_district: Optional[str] = Field(None, description="Target district")
    query_text: Optional[str] = Field(None, description="Detailed problem statement or market query")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extensible query parameters")


class ResearchRequestCreate(ResearchRequestBase):
    """Schema to trigger a research request."""
    user_id: Optional[int] = None
    business_profile_id: Optional[int] = None


class ResearchRequestResponse(ResearchRequestBase):
    """Response schema for a research request."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    business_profile_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime


class ResearchReportResponse(BaseModel):
    """Generated research report schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    research_request_id: int
    title: str
    summary: Optional[str] = None
    market_analysis: Optional[Dict[str, Any]] = None
    recommended_schemes: Optional[Dict[str, Any]] = None
    llm_insights: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class DataSourceBase(BaseModel):
    """Base schema for a data source entry."""
    name: str = Field(..., description="Dataset name (e.g., UDYAM, Schemes, RBI)")
    source_type: str = Field(..., description="Source medium: government_portal, api, csv_ingestion, database")
    description: Optional[str] = None
    url: Optional[str] = None
    record_count: int = 0
    status: str = "active"
    metadata_info: Optional[Dict[str, Any]] = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceResponse(DataSourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
