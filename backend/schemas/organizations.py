"""
Pydantic schemas for Organization-related API operations
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class OrganizationCreate(BaseModel):
    """Schema for creating a new organization"""
    org_name: str = Field(..., min_length=2, max_length=255, description="Organization name")
    domain: Optional[str] = Field(None, max_length=255, description="Custom domain (optional)")
    plan_type: str = Field("starter", description="Subscription plan")
    admin_email: EmailStr = Field(..., description="Admin user email")
    admin_name: str = Field(..., min_length=2, max_length=255, description="Admin user full name")
    admin_password: str = Field(..., min_length=8, description="Admin user password")
    
    @validator('org_name')
    def validate_org_name(cls, v):
        if not v.strip():
            raise ValueError('Organization name cannot be empty')
        return v.strip()
    
    @validator('plan_type')
    def validate_plan_type(cls, v):
        allowed_plans = ['starter', 'professional', 'enterprise']
        if v not in allowed_plans:
            raise ValueError(f'Plan type must be one of: {allowed_plans}')
        return v
    
    @validator('domain')
    def validate_domain(cls, v):
        if v:
            # Basic domain validation
            if not v.replace('-', '').replace('.', '').isalnum():
                raise ValueError('Invalid domain format')
        return v

class OrganizationResponse(BaseModel):
    """Schema for organization data in responses"""
    org_id: uuid.UUID
    org_name: str
    domain: Optional[str]
    plan_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationUpdate(BaseModel):
    """Schema for updating organization settings"""
    org_name: Optional[str] = Field(None, min_length=2, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    plan_type: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    
    @validator('plan_type')
    def validate_plan_type(cls, v):
        if v is not None:
            allowed_plans = ['starter', 'professional', 'enterprise']
            if v not in allowed_plans:
                raise ValueError(f'Plan type must be one of: {allowed_plans}')
        return v

class OrganizationSettings(BaseModel):
    """Schema for organization RAG settings"""
    similarity_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_documents_per_query: Optional[int] = Field(5, ge=1, le=20)
    response_style: Optional[str] = Field("balanced", pattern="^(concise|balanced|detailed)$")
    enable_source_attribution: Optional[bool] = True
    llm_model: Optional[str] = Field("gemini-2.0-flash-exp")
    custom_prompt_template: Optional[str] = None

class OrganizationStats(BaseModel):
    """Schema for organization statistics"""
    total_documents: int
    total_users: int
    total_searches_this_month: int
    storage_used_mb: float
    plan_limits: Dict[str, Any]
    
class OrganizationRegistrationResponse(BaseModel):
    """Schema for organization registration response"""
    success: bool
    org_id: uuid.UUID
    message: str
    admin_user_id: uuid.UUID
    next_steps: List[str]