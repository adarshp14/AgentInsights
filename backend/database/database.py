"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
from .models import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./insightflow_multitenant.db"  # Default to SQLite for development
)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True  # Set to False in production
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=True  # Set to False in production
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    Use with FastAPI Depends()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Get database session for direct use
    Remember to close the session when done
    """
    return SessionLocal()

# Initialize database on import (for development)
if os.getenv("ENVIRONMENT", "development") == "development":
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")