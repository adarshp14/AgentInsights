"""
Organization service for multi-tenant operations
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
import uuid
import hashlib
from passlib.context import CryptContext

from database.models import Organization, User
from schemas.organizations import OrganizationCreate, OrganizationUpdate
from schemas.users import UserCreate

class OrganizationService:
    """Service for organization management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_organization(self, org_data: OrganizationCreate) -> Dict[str, Any]:
        """
        Create a new organization with admin user
        Returns: {"success": bool, "org_id": UUID, "admin_user_id": UUID, "message": str}
        """
        try:
            # Check if organization name already exists
            existing_org = self.db.query(Organization).filter(
                Organization.org_name == org_data.org_name
            ).first()
            
            if existing_org:
                return {
                    "success": False,
                    "message": f"Organization with name '{org_data.org_name}' already exists"
                }
            
            # Check if domain is already taken (if provided)
            if org_data.domain and org_data.domain.strip():
                existing_domain = self.db.query(Organization).filter(
                    Organization.domain == org_data.domain.strip()
                ).first()
                
                if existing_domain:
                    return {
                        "success": False,
                        "message": f"Domain '{org_data.domain.strip()}' is already taken"
                    }
            
            # Check if admin email already exists
            existing_user = self.db.query(User).filter(
                User.email == org_data.admin_email
            ).first()
            
            if existing_user:
                return {
                    "success": False,
                    "message": f"User with email '{org_data.admin_email}' already exists"
                }
            
            # Create organization
            # Convert empty domain string to None for proper NULL handling
            domain_value = org_data.domain if org_data.domain and org_data.domain.strip() else None
            
            org = Organization(
                org_name=org_data.org_name,
                domain=domain_value,
                plan_type=org_data.plan_type,
                settings={
                    "similarity_threshold": 0.7,
                    "max_documents_per_query": 5,
                    "response_style": "balanced",
                    "enable_source_attribution": True,
                    "llm_model": "gemini-2.0-flash-exp"
                }
            )
            
            self.db.add(org)
            self.db.flush()  # Get the org_id
            
            # Create admin user with hashed password
            password_hash = self.pwd_context.hash(org_data.admin_password)
            admin_user = User(
                org_id=org.org_id,
                email=org_data.admin_email,
                full_name=org_data.admin_name,
                password_hash=password_hash,
                role="admin",
                is_active=True
            )
            
            self.db.add(admin_user)
            self.db.commit()
            
            return {
                "success": True,
                "org_id": org.org_id,
                "admin_user_id": admin_user.user_id,
                "message": f"Organization '{org_data.org_name}' created successfully",
                "next_steps": [
                    "Set up authentication for admin user",
                    "Upload first documents to knowledge base",
                    "Invite team members",
                    "Configure RAG settings"
                ]
            }
            
        except IntegrityError as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Database error: {str(e)}"
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def get_organization(self, org_id: uuid.UUID) -> Optional[Organization]:
        """Get organization by ID"""
        return self.db.query(Organization).filter(
            Organization.org_id == org_id,
            Organization.is_active == True
        ).first()
    
    def get_organization_by_domain(self, domain: str) -> Optional[Organization]:
        """Get organization by domain"""
        return self.db.query(Organization).filter(
            Organization.domain == domain,
            Organization.is_active == True
        ).first()
    
    def update_organization(self, org_id: uuid.UUID, updates: OrganizationUpdate) -> Dict[str, Any]:
        """Update organization settings"""
        try:
            org = self.get_organization(org_id)
            if not org:
                return {"success": False, "message": "Organization not found"}
            
            # Update fields
            update_data = updates.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(org, field):
                    setattr(org, field, value)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Organization updated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error updating organization: {str(e)}"
            }
    
    def get_organization_stats(self, org_id: uuid.UUID) -> Dict[str, Any]:
        """Get organization statistics"""
        org = self.get_organization(org_id)
        if not org:
            return {"error": "Organization not found"}
        
        # Count related entities
        total_users = self.db.query(User).filter(
            User.org_id == org_id,
            User.is_active == True
        ).count()
        
        total_documents = len(org.documents)
        
        # Calculate storage used (would need to implement)
        storage_used_mb = sum(doc.file_size for doc in org.documents) / (1024 * 1024)
        
        # Get plan limits
        plan_limits = self._get_plan_limits(org.plan_type)
        
        return {
            "total_documents": total_documents,
            "total_users": total_users,
            "total_searches_this_month": 0,  # TODO: Implement
            "storage_used_mb": round(storage_used_mb, 2),
            "plan_limits": plan_limits
        }
    
    def _get_plan_limits(self, plan_type: str) -> Dict[str, Any]:
        """Get limits for different subscription plans"""
        plans = {
            "starter": {
                "max_documents": 100,
                "max_users": 10,
                "max_storage_gb": 1,
                "searches_per_month": 1000
            },
            "professional": {
                "max_documents": 1000,
                "max_users": 100,
                "max_storage_gb": 10,
                "searches_per_month": 10000
            },
            "enterprise": {
                "max_documents": "unlimited",
                "max_users": "unlimited",
                "max_storage_gb": "unlimited",
                "searches_per_month": "unlimited"
            }
        }
        
        return plans.get(plan_type, plans["starter"])
    
    def create_org_collection_name(self, org_id: uuid.UUID) -> str:
        """Generate consistent collection name for organization's vector store"""
        # Create a short, consistent identifier from org_id
        org_str = str(org_id).replace('-', '')
        hash_obj = hashlib.md5(org_str.encode())
        short_hash = hash_obj.hexdigest()[:8]
        
        return f"org_{short_hash}_docs"
    
    def deactivate_organization(self, org_id: uuid.UUID) -> Dict[str, Any]:
        """Deactivate an organization (soft delete)"""
        try:
            org = self.get_organization(org_id)
            if not org:
                return {"success": False, "message": "Organization not found"}
            
            org.is_active = False
            
            # Deactivate all users
            self.db.query(User).filter(User.org_id == org_id).update(
                {"is_active": False}
            )
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Organization deactivated successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error deactivating organization: {str(e)}"
            }