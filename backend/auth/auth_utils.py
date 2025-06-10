import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Password encryption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Admin credentials (in production, use a proper database)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

# If no hash is provided, create one for default password "admin123"
if not ADMIN_PASSWORD_HASH:
    ADMIN_PASSWORD_HASH = pwd_context.hash("admin123")
    logger.warning("Using default admin password 'admin123'. Change this in production!")

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_admin(username: str, password: str) -> bool:
    """Authenticate admin user"""
    if username != ADMIN_USERNAME:
        return False
    return verify_password(password, ADMIN_PASSWORD_HASH)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current authenticated admin user"""
    try:
        payload = verify_token(credentials.credentials)
        username = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return username
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

class AdminRequired:
    """Dependency class for admin authentication"""
    
    def __init__(self):
        pass
    
    async def __call__(self, current_admin: str = Depends(get_current_admin)) -> str:
        return current_admin

# Create instance for dependency injection
admin_required = AdminRequired()