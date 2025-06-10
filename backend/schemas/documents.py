"""
Pydantic schemas for Document-related API operations
"""
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class DocumentUpload(BaseModel):
    """Schema for document upload metadata"""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (pdf, txt, docx, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom metadata")
    
    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['pdf', 'txt', 'docx', 'doc', 'md', 'html']
        if v.lower() not in allowed_types:
            raise ValueError(f'File type must be one of: {allowed_types}')
        return v.lower()

class DocumentResponse(BaseModel):
    """Schema for document data in responses"""
    document_id: uuid.UUID
    org_id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    processing_status: str
    chunks_created: int
    embedding_model: Optional[str]
    uploaded_by: uuid.UUID
    upload_date: datetime
    processed_date: Optional[datetime]
    extracted_text_length: int
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True

class DocumentProcessingStatus(BaseModel):
    """Schema for document processing status"""
    document_id: uuid.UUID
    status: str  # pending, processing, completed, failed
    progress_percentage: int = Field(ge=0, le=100)
    chunks_processed: int
    total_chunks: int
    error_message: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class DocumentUpdate(BaseModel):
    """Schema for updating document metadata"""
    filename: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentSearch(BaseModel):
    """Schema for document search within organization"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    file_types: Optional[List[str]] = Field(None, description="Filter by file types")
    date_from: Optional[datetime] = Field(None, description="Filter by upload date from")
    date_to: Optional[datetime] = Field(None, description="Filter by upload date to")

class DocumentSearchResult(BaseModel):
    """Schema for document search results"""
    document_id: uuid.UUID
    filename: str
    file_type: str
    relevance_score: float
    matched_chunks: List[Dict[str, Any]]
    upload_date: datetime
    uploader_name: str

class DocumentStats(BaseModel):
    """Schema for document statistics"""
    total_documents: int
    total_size_mb: float
    documents_by_type: Dict[str, int]
    processing_status_counts: Dict[str, int]
    upload_trend_last_30_days: List[Dict[str, Any]]
    most_accessed_documents: List[Dict[str, Any]]

class BulkDocumentOperation(BaseModel):
    """Schema for bulk document operations"""
    document_ids: List[uuid.UUID] = Field(..., min_items=1, max_items=100)
    operation: str = Field(..., regex="^(delete|reprocess|update_metadata)$")
    metadata: Optional[Dict[str, Any]] = None

class DocumentChunk(BaseModel):
    """Schema for document chunk data"""
    chunk_index: int
    chunk_text: str
    chunk_metadata: Dict[str, Any]
    similarity_score: Optional[float] = None

class DocumentAnalytics(BaseModel):
    """Schema for document usage analytics"""
    document_id: uuid.UUID
    filename: str
    view_count: int
    search_hits: int
    last_accessed: Optional[datetime]
    top_queries: List[str]
    avg_relevance_score: float