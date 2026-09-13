from typing import Optional
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """OAuth2 compatible token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration window in seconds")


class LoginRequest(BaseModel):
    """JSON payload for user login."""
    email: Optional[str] = Field(None, description="Registered email address")
    username: Optional[str] = Field(None, description="Username or email (OAuth2 field alias)")
    password: str = Field(..., description="Account plaintext password")


class RegisterRequest(BaseModel):
    """JSON payload for user self-registration."""
    email: str = Field(..., description="Unique user email address")
    password: str = Field(..., min_length=6, description="Account password (at least 6 characters)")
    full_name: Optional[str] = Field(None, description="Full name of applicant or entrepreneur")
    phone_number: Optional[str] = Field(None, description="Contact phone number")
