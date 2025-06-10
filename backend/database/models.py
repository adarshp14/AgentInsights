"""
Multi-tenant database models for RAG Platform
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Organization(Base):
    """Organization/Tenant entity"""
    __tablename__ = "organizations"
    
    org_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=True)  # Optional custom domain
    plan_type = Column(String(50), default="starter")  # starter, professional, enterprise
    settings = Column(JSON, default={})  # RAG config, LLM preferences, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")
    search_logs = relationship("SearchLog", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    """User entity with organization association"""
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="employee")  # admin, employee
    password_hash = Column(String(255), nullable=True)  # For JWT auth
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    search_logs = relationship("SearchLog", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    """Document entity with organization isolation"""
    __tablename__ = "documents"
    
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, docx, etc.
    file_size = Column(Integer, nullable=False)  # bytes
    file_path = Column(String(1000), nullable=False)  # storage path
    
    # Processing metadata
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    chunks_created = Column(Integer, default=0)
    embedding_model = Column(String(100), nullable=True)  # model used for embeddings
    
    # Upload metadata
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime, nullable=True)
    
    # Content metadata
    content_hash = Column(String(64), nullable=True)  # SHA-256 for deduplication
    extracted_text_length = Column(Integer, default=0)
    doc_metadata = Column(JSON, default={})  # custom metadata, tags, etc.
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
    uploader = relationship("User")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")

class DocumentEmbedding(Base):
    """Vector embeddings for document chunks"""
    __tablename__ = "document_embeddings"
    
    embedding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    
    # Chunk data
    chunk_index = Column(Integer, nullable=False)  # position in document
    chunk_text = Column(Text, nullable=False)
    chunk_metadata = Column(JSON, default={})  # page number, section, etc.
    
    # Vector data (stored in ChromaDB, referenced here)
    chroma_id = Column(String(255), nullable=False)  # ID in ChromaDB
    embedding_model = Column(String(100), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")
    organization = relationship("Organization")

class UserSession(Base):
    """User session tracking with organization context"""
    __tablename__ = "user_sessions"
    
    session_id = Column(String(255), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)  # nullable for anonymous
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    
    # Session metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    
    # Conversation metadata
    message_count = Column(Integer, default=0)
    total_queries = Column(Integer, default=0)
    rag_queries = Column(Integer, default=0)  # queries that used documents
    direct_queries = Column(Integer, default=0)  # queries that used LLM only
    
    # Relationships
    user = relationship("User")
    organization = relationship("Organization")
    search_logs = relationship("SearchLog", back_populates="session", cascade="all, delete-orphan")

class SearchLog(Base):
    """Search/query analytics and logging"""
    __tablename__ = "search_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("user_sessions.session_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    
    # Query data
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=False)  # rag, direct, hybrid
    
    # Response data
    response_text = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # RAG specific data
    documents_retrieved = Column(Integer, default=0)
    max_similarity_score = Column(Float, nullable=True)
    documents_used = Column(JSON, default=[])  # list of document_ids
    
    # User feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 stars or thumbs up/down
    user_feedback = Column(Text, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    search_metadata = Column(JSON, default={})
    
    # Relationships
    session = relationship("UserSession", back_populates="search_logs")
    user = relationship("User", back_populates="search_logs")
    organization = relationship("Organization", back_populates="search_logs")

class Usage(Base):
    """Usage tracking for billing and analytics"""
    __tablename__ = "usage"
    
    usage_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    
    # Usage metrics
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Document metrics
    documents_stored = Column(Integer, default=0)
    total_document_size = Column(Integer, default=0)  # bytes
    
    # Query metrics
    total_queries = Column(Integer, default=0)
    rag_queries = Column(Integer, default=0)
    direct_queries = Column(Integer, default=0)
    
    # User metrics
    active_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    
    # Storage metrics
    vector_embeddings_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")