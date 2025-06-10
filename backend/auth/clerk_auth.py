"""
Clerk authentication utilities for backend JWT validation
"""
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, JWTError
import logging

logger = logging.getLogger(__name__)

# Clerk configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWKS_URL = "https://clerk.dev/.well-known/jwks"

if not CLERK_SECRET_KEY:
    logger.warning("CLERK_SECRET_KEY not found in environment variables")

security = HTTPBearer()

class ClerkJWTBearer:
    """Clerk JWT token validator"""
    
    def __init__(self):
        self.jwks_cache = None
        self.algorithm = "RS256"
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Clerk"""
        if self.jwks_cache:
            return self.jwks_cache
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(CLERK_JWKS_URL)
                response.raise_for_status()
                self.jwks_cache = response.json()
                return self.jwks_cache
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to validate token"
            )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Clerk JWT token"""
        try:
            # Get JWKS for signature verification
            jwks = await self.get_jwks()
            
            # Decode header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get("kid")
            
            if not key_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token header"
                )
            
            # Find the matching key
            key = None
            for jwk_key in jwks.get("keys", []):
                if jwk_key.get("kid") == key_id:
                    key = jwk_key
                    break
            
            if not key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token key"
                )
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                key,
                algorithms=[self.algorithm],
                options={"verify_aud": False}  # Clerk doesn't use standard aud claim
            )
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed"
            )

# Global instance
clerk_jwt = ClerkJWTBearer()

async def get_current_user_clerk(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current user from Clerk JWT token
    Returns user information from the token payload
    """
    token = credentials.credentials
    payload = await clerk_jwt.verify_token(token)
    
    # Extract user information from Clerk token
    user_info = {
        "user_id": payload.get("sub"),  # Subject is user ID in Clerk
        "email": payload.get("email"),
        "org_id": payload.get("org_id"),
        "org_role": payload.get("org_role"),
        "session_id": payload.get("sid"),
        "issued_at": payload.get("iat"),
        "expires_at": payload.get("exp")
    }
    
    if not user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token"
        )
    
    return user_info

# Backward compatibility function for existing endpoints
async def get_current_user_compatible(
    user_info: Dict[str, Any] = Depends(get_current_user_clerk)
) -> Dict[str, Any]:
    """
    Compatibility wrapper that transforms Clerk user info 
    to match existing user model structure
    """
    return {
        "user_id": user_info["user_id"],
        "email": user_info["email"],
        "role": "admin" if user_info.get("org_role") == "org:admin" else "employee",
        "org_id": user_info["org_id"],
        "is_active": True  # Clerk handles user activation
    }