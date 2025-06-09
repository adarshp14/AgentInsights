from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging

app = FastAPI(title="InsightFlow Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

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

@app.get("/")
async def root():
    return {"message": "InsightFlow Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools():
    """List available real tools"""
    from tools.real_tools import RealToolRegistry
    registry = RealToolRegistry()
    return registry.list_tools()

@app.post("/tools/{tool_name}/{method}")
async def execute_tool(tool_name: str, method: str, params: Dict[str, Any]):
    """Execute a real tool method"""
    try:
        from tools.real_tools import RealToolRegistry
        registry = RealToolRegistry()
        result = registry.execute_tool(tool_name, method, **params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the vector store"""
    try:
        from retriever.real_vector_store import RealVectorStore
        from langchain.embeddings import SentenceTransformerEmbeddings
        
        # Initialize vector store
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = RealVectorStore(embeddings)
        
        # Read file content
        content = await file.read()
        
        # Process based on file type
        success = False
        if file.filename.lower().endswith('.pdf'):
            success = vector_store.add_document_from_pdf(content, file.filename)
        elif file.filename.lower().endswith(('.txt', '.md')):
            text_content = content.decode('utf-8')
            success = vector_store.add_document_from_text(
                text_content,
                {"source": file.filename, "type": "uploaded_text"}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or TXT files.")
        
        if success:
            vector_store.save_store()
            stats = vector_store.get_document_stats()
            
            return {
                "status": "success",
                "message": f"Document '{file.filename}' uploaded successfully",
                "filename": file.filename,
                "file_size": len(content),
                "vector_store_stats": stats
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to process document")
            
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-store/stats")
async def get_vector_store_stats():
    """Get statistics about the vector store"""
    try:
        from retriever.real_vector_store import RealVectorStore
        from langchain.embeddings import SentenceTransformerEmbeddings
        
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = RealVectorStore(embeddings)
        
        return vector_store.get_document_stats()
        
    except Exception as e:
        logger.error(f"Error getting vector store stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query using real LangGraph agent with Gemini"""
    try:
        from graphs.real_agent_graph import RealInsightFlowAgent
        
        # Initialize real agent (in production, this would be cached)
        agent = RealInsightFlowAgent()
        
        # Process the query
        result = await agent.process_query(
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)