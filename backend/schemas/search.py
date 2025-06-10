"""
Pydantic schemas for Search/Query operations
"""
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class SearchQuery(BaseModel):
    """Schema for search/query requests"""
    query: str = Field(..., min_length=1, max_length=2000, description="Search query text")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    conversation_id: Optional[str] = Field(None, description="Conversation ID (legacy)")
    include_sources: bool = Field(True, description="Include document sources in response")
    max_documents: Optional[int] = Field(5, ge=1, le=20, description="Max documents to retrieve")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class SearchResponse(BaseModel):
    """Schema for search responses"""
    response_id: uuid.UUID
    query: str
    response_text: str
    response_type: str  # "rag", "direct", "hybrid"
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_time_ms: int
    
    # RAG-specific data
    documents_used: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    max_similarity_score: Optional[float] = None
    
    # Metadata
    timestamp: datetime
    session_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentSource(BaseModel):
    """Schema for document sources in responses"""
    document_id: uuid.UUID
    filename: str
    file_type: str
    chunk_text: str
    similarity_score: float
    page_number: Optional[int] = None
    section: Optional[str] = None

class QueryAnalytics(BaseModel):
    """Schema for query analytics"""
    query_id: uuid.UUID
    query_text: str
    response_type: str
    response_time_ms: int
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = None
    documents_retrieved: int
    timestamp: datetime

class SearchFeedback(BaseModel):
    """Schema for user feedback on search results"""
    response_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    is_helpful: bool = Field(..., description="Whether the response was helpful")
    
class SearchSuggestion(BaseModel):
    """Schema for search suggestions"""
    suggestion_text: str
    relevance_score: float
    based_on_documents: List[str]  # document filenames
    
class SearchHistory(BaseModel):
    """Schema for user search history"""
    searches: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int

class QueryRouting(BaseModel):
    """Schema for query routing decisions"""
    query: str
    route_decision: str  # "rag", "direct", "hybrid"
    confidence: float
    reasoning: str
    document_relevance_scores: List[float]
    fallback_reason: Optional[str] = None

class SearchMetrics(BaseModel):
    """Schema for search metrics and KPIs"""
    total_searches: int
    rag_percentage: float
    direct_percentage: float
    avg_response_time_ms: float
    avg_user_rating: float
    popular_queries: List[Dict[str, Any]]
    search_success_rate: float
    
class SmartSuggestions(BaseModel):
    """Schema for AI-powered search suggestions"""
    query: str
    suggestions: List[str]
    related_documents: List[str]
    follow_up_questions: List[str]