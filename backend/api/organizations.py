"""
API routes for organization management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.organizations import (
    OrganizationCreate, 
    OrganizationResponse, 
    OrganizationUpdate,
    OrganizationStats,
    OrganizationRegistrationResponse
)
from services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("/register", response_model=OrganizationRegistrationResponse)
async def register_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new organization with admin user
    This is the main entry point for new organizations
    """
    service = OrganizationService(db)
    result = service.create_organization(org_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return OrganizationRegistrationResponse(
        success=result["success"],
        org_id=result["org_id"],
        message=result["message"],
        admin_user_id=result["admin_user_id"],
        next_steps=result["next_steps"]
    )

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db)
):
    """Get organization details"""
    service = OrganizationService(db)
    
    try:
        org = service.get_organization(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return OrganizationResponse.from_orm(org)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format"
        )

@router.put("/{org_id}", response_model=dict)
async def update_organization(
    org_id: str,
    updates: OrganizationUpdate,
    db: Session = Depends(get_db)
):
    """Update organization settings"""
    service = OrganizationService(db)
    
    try:
        result = service.update_organization(org_id, updates)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format"
        )

@router.get("/{org_id}/stats", response_model=OrganizationStats)
async def get_organization_stats(
    org_id: str,
    db: Session = Depends(get_db)
):
    """Get organization statistics and usage data"""
    service = OrganizationService(db)
    
    try:
        stats = service.get_organization_stats(org_id)
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=stats["error"]
            )
        
        return OrganizationStats(**stats)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format"
        )

@router.delete("/{org_id}")
async def deactivate_organization(
    org_id: str,
    db: Session = Depends(get_db)
):
    """Deactivate an organization (soft delete)"""
    service = OrganizationService(db)
    
    try:
        result = service.deactivate_organization(org_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format"
        )

@router.get("/domain/{domain}", response_model=OrganizationResponse)
async def get_organization_by_domain(
    domain: str,
    db: Session = Depends(get_db)
):
    """Get organization by custom domain"""
    service = OrganizationService(db)
    org = service.get_organization_by_domain(domain)
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No organization found for domain '{domain}'"
        )
    
    return OrganizationResponse.from_orm(org)