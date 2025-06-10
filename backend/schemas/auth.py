"""
Authentication schemas for multi-tenant system
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    org_id: Optional[str] = None  # Can be provided or derived from email domain

class UserRegister(BaseModel):
    """User registration within organization"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8)
    role: str = Field("employee", pattern="^(admin|employee)$")

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    org_id: str
    role: str

class TokenData(BaseModel):
    """Token payload data"""
    user_id: uuid.UUID
    org_id: uuid.UUID
    email: str
    role: str
    exp: int

class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr
    org_id: Optional[str] = None

class PasswordUpdate(BaseModel):
    """Password update request"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserProfile(BaseModel):
    """User profile response"""
    user_id: str
    email: str
    full_name: str
    role: str
    org_id: str
    org_name: str
    is_active: bool
    last_login: Optional[str] = None
    created_at: str