from fastapi import FastAPI, HTTPException
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
    """List available tools"""
    from tools.mock_tools import ToolRegistry
    registry = ToolRegistry()
    return registry.list_tools()

@app.post("/tools/{tool_name}/{method}")
async def execute_tool(tool_name: str, method: str, params: Dict[str, Any]):
    """Execute a tool method"""
    try:
        from tools.mock_tools import ToolRegistry
        registry = ToolRegistry()
        result = registry.execute_tool(tool_name, method, **params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query using LangGraph agent"""
    try:
        from graphs.agent_graph import InsightFlowAgent
        
        # Initialize agent (in production, this would be cached)
        agent = InsightFlowAgent()
        
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