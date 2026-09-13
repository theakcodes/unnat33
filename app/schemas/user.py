from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    """Base fields for User."""
    email: str = Field(..., description="Unique email address")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    phone_number: Optional[str] = Field(None, description="Contact phone number")
    is_active: bool = Field(True, description="Account active status")
    is_superuser: bool = Field(False, description="Superuser access flag")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: Optional[str] = Field(None, min_length=6, description="Plaintext password (will be hashed with Argon2)")


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    email: Optional[str] = Field(None, description="Updated email address")
    full_name: Optional[str] = Field(None, description="Updated full name")
    phone_number: Optional[str] = Field(None, description="Updated phone number")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    password: Optional[str] = Field(None, min_length=6, description="New password if updating")


class UserResponse(UserBase):
    """Schema returned by User API endpoints. Does not expose password hash."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
