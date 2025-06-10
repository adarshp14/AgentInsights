"""
Pydantic schemas for User-related API operations
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=255, description="User full name")
    role: str = Field("employee", description="User role in organization")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'employee']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()

class UserResponse(BaseModel):
    """Schema for user data in responses"""
    user_id: uuid.UUID
    org_id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['admin', 'employee']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of: {allowed_roles}')
        return v

class UserInvite(BaseModel):
    """Schema for inviting users to organization"""
    email: EmailStr = Field(..., description="Email address to invite")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name of invitee")
    role: str = Field("employee", description="Role to assign")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'employee']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")
    org_domain: Optional[str] = Field(None, description="Organization domain (optional)")

class UserLoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    organization: dict

class UserSession(BaseModel):
    """Schema for user session data"""
    session_id: str
    user_id: Optional[uuid.UUID]
    org_id: uuid.UUID
    created_at: datetime
    last_active: datetime
    message_count: int
    total_queries: int
    rag_queries: int
    direct_queries: int

class UserStats(BaseModel):
    """Schema for user activity statistics"""
    total_searches: int
    searches_this_week: int
    favorite_topics: List[str]
    avg_session_duration_minutes: float
    most_active_day: str