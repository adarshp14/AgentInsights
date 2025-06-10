"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from database.database import get_db
from schemas.auth import (
    UserLogin, 
    UserRegister, 
    TokenResponse, 
    PasswordUpdate,
    UserProfile
)
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get auth service"""
    return AuthService(db)

def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract token from Authorization header"""
    return credentials.credentials

@router.post("/register/{org_id}", response_model=Dict[str, Any])
async def register_user(
    org_id: str,
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user within an organization
    Requires valid org_id
    """
    try:
        org_uuid = uuid.UUID(org_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format"
        )
    
    result = auth_service.register_user(org_uuid, user_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {
        "success": True,
        "user_id": str(result["user_id"]),
        "message": result["message"]
    }

@router.post("/login", response_model=Dict[str, Any])
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    User login with email and password
    Returns JWT token with org context
    """
    result = auth_service.authenticate_user(login_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    return {
        "success": True,
        "token": result["token"],
        "user": result["user"]
    }

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    token: str = Depends(get_current_user_token),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user profile from token
    """
    profile = auth_service.get_user_profile(token)
    
    if "error" in profile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=profile["error"]
        )
    
    return UserProfile(**profile)

@router.post("/change-password")
async def change_password(
    password_data: PasswordUpdate,
    token: str = Depends(get_current_user_token),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change user password
    """
    result = auth_service.change_password(
        token,
        password_data.current_password,
        password_data.new_password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/verify")
async def verify_token(
    token: str = Depends(get_current_user_token),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify if token is valid and get user info
    """
    user = auth_service.get_user_by_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {
        "valid": True,
        "user_id": str(user.user_id),
        "org_id": str(user.org_id),
        "email": user.email,
        "role": user.role
    }

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard token)
    """
    return {"message": "Logged out successfully"}