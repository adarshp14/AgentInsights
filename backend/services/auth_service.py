"""
Authentication service for multi-tenant system
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
import uuid
import hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from database.models import User, Organization
from schemas.auth import UserLogin, UserRegister, TokenData
import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for user authentication within organizations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user: User) -> Dict[str, Any]:
        """Create JWT access token with org context"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": str(user.user_id),
            "user_id": str(user.user_id),
            "org_id": str(user.org_id),
            "email": user.email,
            "role": user.role,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": str(user.user_id),
            "org_id": str(user.org_id),
            "role": user.role
        }
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            user_id = payload.get("user_id")
            org_id = payload.get("org_id")
            email = payload.get("email")
            role = payload.get("role")
            exp = payload.get("exp")
            
            if not all([user_id, org_id, email, role]):
                return None
            
            return TokenData(
                user_id=uuid.UUID(user_id),
                org_id=uuid.UUID(org_id),
                email=email,
                role=role,
                exp=exp
            )
        except JWTError:
            return None
    
    def register_user(self, org_id: uuid.UUID, user_data: UserRegister) -> Dict[str, Any]:
        """Register a new user within an organization"""
        try:
            # Check if organization exists and is active
            org = self.db.query(Organization).filter(
                Organization.org_id == org_id,
                Organization.is_active == True
            ).first()
            
            if not org:
                return {
                    "success": False,
                    "message": "Organization not found or inactive"
                }
            
            # Check if user already exists
            existing_user = self.db.query(User).filter(
                User.email == user_data.email
            ).first()
            
            if existing_user:
                return {
                    "success": False,
                    "message": f"User with email '{user_data.email}' already exists"
                }
            
            # Create new user
            hashed_password = self.hash_password(user_data.password)
            
            user = User(
                org_id=org_id,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                password_hash=hashed_password,
                is_active=True
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            return {
                "success": True,
                "user_id": user.user_id,
                "message": f"User '{user_data.full_name}' registered successfully"
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
    
    def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return token"""
        try:
            # Find user by email
            user = self.db.query(User).filter(
                User.email == login_data.email,
                User.is_active == True
            ).first()
            
            if not user:
                return {
                    "success": False,
                    "message": "Invalid email or password"
                }
            
            # Check if org_id matches (if provided)
            if login_data.org_id:
                try:
                    org_uuid = uuid.UUID(login_data.org_id)
                    if user.org_id != org_uuid:
                        return {
                            "success": False,
                            "message": "Invalid organization"
                        }
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid organization ID format"
                    }
            
            # Verify password
            if not self.verify_password(login_data.password, user.password_hash):
                return {
                    "success": False,
                    "message": "Invalid email or password"
                }
            
            # Check if organization is active
            org = self.db.query(Organization).filter(
                Organization.org_id == user.org_id,
                Organization.is_active == True
            ).first()
            
            if not org:
                return {
                    "success": False,
                    "message": "Organization is inactive"
                }
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            # Create token
            token_data = self.create_access_token(user)
            
            return {
                "success": True,
                "token": token_data,
                "user": {
                    "user_id": str(user.user_id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "org_id": str(user.org_id),
                    "org_name": org.org_name
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Authentication error: {str(e)}"
            }
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """Get user from valid token"""
        token_data = self.verify_token(token)
        if not token_data:
            return None
        
        user = self.db.query(User).filter(
            User.user_id == token_data.user_id,
            User.org_id == token_data.org_id,
            User.is_active == True
        ).first()
        
        return user
    
    def get_user_profile(self, token: str) -> Dict[str, Any]:
        """Get user profile from token"""
        user = self.get_user_by_token(token)
        if not user:
            return {"error": "Invalid or expired token"}
        
        org = self.db.query(Organization).filter(
            Organization.org_id == user.org_id
        ).first()
        
        return {
            "user_id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": str(user.org_id),
            "org_name": org.org_name if org else "Unknown",
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat()
        }
    
    def change_password(self, token: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        user = self.get_user_by_token(token)
        if not user:
            return {"success": False, "message": "Invalid or expired token"}
        
        # Verify current password
        if not self.verify_password(current_password, user.password_hash):
            return {"success": False, "message": "Current password is incorrect"}
        
        # Update password
        try:
            user.password_hash = self.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {"success": True, "message": "Password updated successfully"}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error updating password: {str(e)}"}