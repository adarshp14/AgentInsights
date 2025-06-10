from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
import asyncio
import json
import time
from contextlib import asynccontextmanager
from datetime import timedelta
from sse_starlette.sse import EventSourceResponse

# Import auth utilities
from auth.auth_utils import (
    authenticate_admin, 
    create_access_token, 
    admin_required,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Import multi-tenant components
from database.database import create_tables
from api.organizations import router as org_router
from api.analytics import router as analytics_router

# Global agent instances
agent_instance = None
streaming_agent_instance = None
vector_store_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and agents
    global agent_instance, streaming_agent_instance, vector_store_instance
    logger.info("Initializing multi-tenant platform...")
    
    try:
        # Initialize database tables
        create_tables()
        logger.info("✅ Database tables initialized")
        
        # Initialize streaming agent (primary)
        from graphs.streaming_agent_graph import get_streaming_agent
        streaming_agent_instance = get_streaming_agent()
        
        # Initialize fallback agent
        from graphs.fast_agent_graph import get_fast_agent
        agent_instance = get_fast_agent()
        
        # Initialize multi-tenant vector store
        from retriever.multi_tenant_vector_store import get_vector_store
        vector_store_instance = get_vector_store()
        logger.info("✅ Multi-tenant vector store initialized")
        
        logger.info("✅ All components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        raise
    
    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down...")

app = FastAPI(
    title="InsightFlow Backend - Enhanced", 
    version="3.0.0", 
    description="AI Agent platform with streaming, vector database, and admin dashboard",
    lifespan=lifespan
)

# CORS middleware - allowing all origins for public API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API access
    allow_credentials=False,  # Set to False when allowing all origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(org_router)

# Import and include auth router
from api.auth import router as auth_router
app.include_router(auth_router)

# Import and include documents router
from api.documents import router as docs_router
app.include_router(docs_router)

# Include analytics router
app.include_router(analytics_router)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class StreamQueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    stream: bool = True

class LoginRequest(BaseModel):
    username: str
    password: str

class DocumentUploadResponse(BaseModel):
    status: str
    document_id: Optional[str] = None
    filename: str
    file_type: str
    file_size: int
    chunks_created: Optional[int] = None
    error: Optional[str] = None

class AgentStep(BaseModel):
    node: str
    status: str
    timestamp: float
    data: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    answer: str
    steps: List[AgentStep]
    conversation_id: str
    metadata: Dict[str, Any] = {}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "InsightFlow Backend - Enhanced", 
        "version": "3.0.0",
        "status": "running",
        "description": "AI agent with streaming, vector database, and admin dashboard",
        "features": [
            "Streaming responses",
            "ChromaDB vector store", 
            "Document upload (PDF/TXT/DOCX)",
            "Admin dashboard",
            "Authentication"
        ],
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agents": {
            "streaming_agent": streaming_agent_instance is not None,
            "fallback_agent": agent_instance is not None
        },
        "vector_store": vector_store_instance is not None
    }

# Legacy auth endpoints removed - using multi-tenant auth system

# Streaming query endpoint
@app.post("/query/stream")
async def stream_query(request: StreamQueryRequest):
    """Process query with streaming response"""
    global streaming_agent_instance
    
    if streaming_agent_instance is None:
        raise HTTPException(status_code=503, detail="Streaming agent not initialized")
    
    async def generate():
        try:
            async for chunk in streaming_agent_instance.process_query_stream(
                question=request.question,
                conversation_id=request.conversation_id or "default"
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming query: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return EventSourceResponse(generate())

# Standard query endpoint (fallback)
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query using optimized agent (non-streaming fallback)"""
    global agent_instance
    
    if agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Process the query using cached agent
        result = await agent_instance.process_query(
            question=request.question,
            conversation_id=request.conversation_id or "default"
        )
        
        # Convert to response format
        steps = [
            AgentStep(
                node=step["node"],
                status=step["status"],
                timestamp=step["timestamp"],
                data=step["data"]
            )
            for step in result["steps"]
        ]
        
        return QueryResponse(
            answer=result["answer"],
            steps=steps,
            conversation_id=result["conversation_id"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Document management endpoints
@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload document to vector store (public endpoint)"""
    global vector_store_instance
    
    if vector_store_instance is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        # Validate file type
        allowed_types = ['pdf', 'txt', 'docx', 'text']
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Process document
        result = vector_store_instance.add_document_from_file(
            file_content=content,
            filename=file.filename,
            file_type=file_extension,
            metadata={"uploaded_via": "public_api"}
        )
        
        if result["status"] == "success":
            return DocumentUploadResponse(
                status="success",
                document_id=result["document_id"],
                filename=result["filename"],
                file_type=result["file_type"],
                file_size=result["file_size"],
                chunks_created=result["chunks_created"]
            )
        else:
            return DocumentUploadResponse(
                status="error",
                filename=file.filename,
                file_type=file_extension,
                file_size=len(content),
                error=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return DocumentUploadResponse(
            status="error",
            filename=file.filename,
            file_type=file_extension,
            file_size=0,
            error=str(e)
        )

@app.get("/documents/list")
async def list_documents():
    """List all documents in vector store"""
    global vector_store_instance
    
    if vector_store_instance is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        documents = vector_store_instance.list_documents()
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/stats")
async def get_document_stats():
    """Get vector store statistics"""
    global vector_store_instance
    
    if vector_store_instance is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        stats = vector_store_instance.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin-only endpoints
@app.post("/admin/documents/upload", response_model=DocumentUploadResponse)
async def admin_upload_document(
    file: UploadFile = File(...),
    current_admin: str = Depends(admin_required)
):
    """Admin upload document to vector store"""
    global vector_store_instance
    
    if vector_store_instance is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        # Validate file type
        allowed_types = ['pdf', 'txt', 'docx', 'text']
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Process document with admin metadata
        result = vector_store_instance.add_document_from_file(
            file_content=content,
            filename=file.filename,
            file_type=file_extension,
            metadata={
                "uploaded_via": "admin_dashboard",
                "uploaded_by": current_admin
            }
        )
        
        if result["status"] == "success":
            return DocumentUploadResponse(
                status="success",
                document_id=result["document_id"],
                filename=result["filename"],
                file_type=result["file_type"],
                file_size=result["file_size"],
                chunks_created=result["chunks_created"]
            )
        else:
            return DocumentUploadResponse(
                status="error",
                filename=file.filename,
                file_type=file_extension,
                file_size=len(content),
                error=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin upload: {str(e)}")
        return DocumentUploadResponse(
            status="error",
            filename=file.filename,
            file_type=file_extension,
            file_size=0,
            error=str(e)
        )

@app.delete("/admin/documents/{document_id}")
async def admin_delete_document(
    document_id: str,
    current_admin: str = Depends(admin_required)
):
    """Admin delete document from vector store"""
    global vector_store_instance
    
    if vector_store_instance is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        success = vector_store_instance.delete_document(document_id)
        if success:
            return {"status": "success", "message": f"Document {document_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/documents/reset")
async def admin_reset_vector_store(current_admin: str = Depends(admin_required)):
    """Admin reset entire vector store"""
    global vector_store_instance
    
    if vector_store_instance is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        success = vector_store_instance.reset_collection()
        if success:
            return {"status": "success", "message": "Vector store reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset vector store")
    except Exception as e:
        logger.error(f"Error resetting vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/dashboard/stats")
async def admin_dashboard_stats(current_admin: str = Depends(admin_required)):
    """Get comprehensive stats for admin dashboard"""
    global vector_store_instance, streaming_agent_instance, agent_instance
    
    try:
        # Vector store stats
        vector_stats = {}
        if vector_store_instance:
            vector_stats = vector_store_instance.get_stats()
        
        # Memory stats
        memory_stats = {}
        if streaming_agent_instance:
            memory_stats = {
                "conversation_cache_size": len(streaming_agent_instance.conversation_memory),
                "cached_conversations": list(streaming_agent_instance.conversation_memory.keys())
            }
        elif agent_instance:
            memory_stats = {
                "conversation_cache_size": len(agent_instance.conversation_memory),
                "cached_conversations": list(agent_instance.conversation_memory.keys())
            }
        
        return {
            "vector_store": vector_stats,
            "memory": memory_stats,
            "agents": {
                "streaming_agent_active": streaming_agent_instance is not None,
                "fallback_agent_active": agent_instance is not None
            },
            "system": {
                "backend_version": "3.0.0",
                "features_enabled": [
                    "streaming_responses",
                    "chromadb_vector_store",
                    "document_upload",
                    "admin_authentication"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Memory management endpoints
@app.get("/memory/stats")
async def get_memory_stats():
    """Get memory and performance statistics"""
    global streaming_agent_instance, agent_instance
    
    active_agent = streaming_agent_instance or agent_instance
    if active_agent is None:
        raise HTTPException(status_code=503, detail="No agent initialized")
    
    try:
        sessions = getattr(active_agent, 'session_metadata', {})
        
        return {
            "conversation_cache_size": len(active_agent.conversation_memory),
            "cached_conversations": list(active_agent.conversation_memory.keys()),
            "total_sessions": len(sessions),
            "active_sessions": [sid for sid, meta in sessions.items() if time.time() - meta.get("last_active", 0) < 3600],
            "memory_store_initialized": hasattr(active_agent, 'conversation_memory'),
            "performance_optimizations": [
                "Singleton pattern",
                "Async processing", 
                "Thread pool execution",
                "Conversation caching",
                "Streaming responses",
                "Session management"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory/cache")
async def clear_memory_cache():
    """Clear conversation cache"""
    global streaming_agent_instance, agent_instance
    
    active_agent = streaming_agent_instance or agent_instance
    if active_agent is None:
        raise HTTPException(status_code=503, detail="No agent initialized")
    
    try:
        cache_size = len(active_agent.conversation_memory)
        active_agent.conversation_memory.clear()
        return {
            "status": "success",
            "message": f"Cleared {cache_size} cached conversations"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy tool endpoints (for backward compatibility)
@app.get("/tools")
async def list_tools():
    """List available tools"""
    global streaming_agent_instance, agent_instance
    
    active_agent = streaming_agent_instance or agent_instance
    if active_agent is None:
        raise HTTPException(status_code=503, detail="No agent initialized")
    
    try:
        from tools.real_tools import RealToolRegistry
        registry = RealToolRegistry()
        return registry.list_tools()
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/{tool_name}/{method}")
async def execute_tool(tool_name: str, method: str, params: Dict[str, Any]):
    """Execute a tool method"""
    try:
        from tools.real_tools import RealToolRegistry
        registry = RealToolRegistry()
        result = registry.execute_tool(tool_name, method, **params)
        return result
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    global streaming_agent_instance
    
    if streaming_agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        if hasattr(streaming_agent_instance, 'get_session_info'):
            session_info = streaming_agent_instance.get_session_info(session_id)
            if "error" in session_info:
                raise HTTPException(status_code=404, detail=session_info["error"])
            return session_info
        else:
            raise HTTPException(status_code=501, detail="Session info not supported")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/cleanup")
async def cleanup_sessions(max_age_hours: int = 24):
    """Clean up old inactive sessions"""
    global streaming_agent_instance
    
    if streaming_agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        if hasattr(streaming_agent_instance, 'cleanup_old_sessions'):
            streaming_agent_instance.cleanup_old_sessions(max_age_hours)
            return {"status": "success", "message": f"Cleaned up sessions older than {max_age_hours} hours"}
        else:
            return {"status": "success", "message": "Session cleanup not supported"}
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)