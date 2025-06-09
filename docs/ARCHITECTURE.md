# InsightFlow Architecture

## System Overview

InsightFlow is a high-performance AI agent application built with modern technologies for intelligent query processing, document retrieval, and conversation memory management.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React)       │    │   (FastAPI)     │    │   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                      │                      │
│ ┌─────────────────┐  │ ┌─────────────────┐  │ ┌─────────────────┐
│ │ React Components│  │ │ FastAPI Router  │  │ │ Google Gemini   │
│ │ - Dashboard     │  │ │ - /query        │  │ │ 2.0 Flash Exp   │
│ │ - Chat Interface│  │ │ - /upload       │  │ └─────────────────┘
│ │ - Analytics     │  │ │ - /memory       │  │
│ └─────────────────┘  │ └─────────────────┘  │ ┌─────────────────┐
│                      │         │            │ │ External APIs   │
│ ┌─────────────────┐  │ ┌─────────────────┐  │ │ - Weather       │
│ │ TypeScript      │  │ │ LangGraph Agent │  │ │ - Web Search    │
│ │ - Type Safety   │  │ │ - Query Router  │  │ │ - News          │
│ │ - State Mgmt    │  │ │ - Memory Mgmt   │  │ └─────────────────┘
│ │ - API Client    │  │ │ - Tool Router   │  │
│ └─────────────────┘  │ └─────────────────┘  │
│                      │         │            │
│ ┌─────────────────┐  │ ┌─────────────────┐  │
│ │ Tailwind CSS    │  │ │ Vector Store    │  │
│ │ - Responsive    │  │ │ - FAISS Index   │  │
│ │ - Modern UI     │  │ │ - Embeddings    │  │ 
│ │ - Animations    │  │ │ - Documents     │  │
│ └─────────────────┘  │ └─────────────────┘  │
                       │         │            │
                       │ ┌─────────────────┐  │
                       │ │ Tool Registry   │  │
                       │ │ - Calculator    │  │
                       │ │ - DateTime      │  │
                       │ │ - Web Search    │  │
                       │ └─────────────────┘  │
```

## Technology Stack

### Frontend
- **React 18.2** - Modern component-based UI framework
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Fast build tool and development server
- **Axios** - HTTP client for API communication

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.9+** - Core programming language
- **LangGraph** - Agent orchestration and workflow management
- **LangChain** - LLM integration and tool management
- **Pydantic** - Data validation and serialization

### AI & ML
- **Google Gemini 2.0 Flash Experimental** - Primary language model
- **SentenceTransformers** - Text embeddings (all-MiniLM-L6-v2)
- **FAISS** - Vector similarity search and indexing
- **RAG (Retrieval Augmented Generation)** - Document-based responses

### Data Storage
- **FAISS Vector Store** - High-performance vector similarity search
- **In-Memory Conversation Cache** - Fast conversation context storage
- **File-based Document Storage** - PDF and text document management

### Performance & Infrastructure
- **Asyncio** - Asynchronous Python programming
- **ThreadPoolExecutor** - Parallel task execution
- **Singleton Pattern** - Optimized agent initialization
- **Uvicorn** - ASGI server for FastAPI

## Component Architecture

### 1. Query Processing Flow

```
User Query → Query Classifier → Router → [Retrieval|Tools|Direct] → Response Generator
                    ↓
              Conversation Memory
```

#### Query Classification
- **Rule-based**: Fast keyword matching
- **Context-aware**: Uses conversation history
- **Types**: retrieval, tool_use, direct

#### Query Routing
- **Retrieval Path**: Document search + RAG
- **Tool Path**: Calculator, DateTime, Web Search
- **Direct Path**: General knowledge responses

### 2. Memory Management

```
┌─────────────────────────────────────────────────────────────┐
│                    Conversation Memory                      │
├─────────────────────────────────────────────────────────────┤
│ conversation_id → [                                         │
│   {                                                         │
│     "question": "user query",                               │
│     "answer": "ai response (800 chars)",                    │
│     "query_type": "retrieval|tool_use|direct",              │
│     "timestamp": 1672531200.0                               │
│   }                                                         │
│ ]                                                           │
└─────────────────────────────────────────────────────────────┘
```

### 3. Vector Store Architecture

```
Documents → Text Chunking → Embeddings → FAISS Index → Similarity Search
     ↓             ↓            ↓           ↓              ↓
   PDF/TXT    512-char     all-MiniLM    Vector DB    Top-K Results
            chunks        L6-v2
```

### 4. Tool Registry

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Calculator    │  │    DateTime     │  │   Web Search    │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Math exprs    │  │ • Current date  │  │ • Live data     │
│ • Percentages   │  │ • Time info     │  │ • News/weather  │
│ • Arithmetic    │  │ • Timezone      │  │ • Current info  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Performance Optimizations

### 1. Singleton Pattern
- **Agent Instance**: Single initialization across requests
- **Component Caching**: Vector store and tools cached
- **Memory Efficiency**: Reduced object creation overhead

### 2. Async Processing
- **Non-blocking I/O**: All database and API calls async
- **Concurrent Execution**: Parallel tool execution
- **Thread Pool**: CPU-intensive tasks in background threads

### 3. Smart Caching
- **Conversation Memory**: In-memory conversation storage
- **Component Reuse**: Singleton pattern for expensive objects
- **Vector Cache**: FAISS index cached in memory

### 4. Query Optimization
- **Fast Classification**: Rule-based instead of LLM-based
- **Reduced Retrieval**: Top-3 documents instead of top-10
- **Quick Analysis**: Truncated content processing

## API Architecture

### RESTful Design
```
GET  /                    # Health check
POST /query               # Main query processing
GET  /health              # Detailed health status
GET  /memory/stats        # Memory statistics
DELETE /memory/cache      # Clear conversation cache
POST /upload-document     # Document upload
GET  /vector-store/stats  # Vector store statistics
GET  /tools               # Available tools
POST /tools/{tool}/{method} # Direct tool execution
```

### Response Format
```json
{
  "answer": "string",
  "steps": [...],
  "conversation_id": "string", 
  "metadata": {
    "query_type": "string",
    "total_processing_time_ms": "number",
    "documents_used": "number",
    "model_used": "string"
  }
}
```

## Security & Deployment

### Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_search_api_key (optional)
WEATHERAPI_KEY=your_weather_api_key (optional)
```

### CORS Configuration
- **Development**: Permissive CORS for local development
- **Production**: Restricted origins for security

### API Rate Limiting
- **Google Gemini**: Respects API quotas and rate limits
- **Error Handling**: Graceful fallbacks for rate limit errors
- **Retry Logic**: Intelligent retry with exponential backoff

## Monitoring & Analytics

### Performance Metrics
- **Response Time**: Per query and per component
- **Memory Usage**: Conversation cache size
- **Error Rates**: Failed requests and fallbacks
- **Query Classification**: Distribution of query types

### Real-time Dashboard
- **Processing Steps**: Live query processing visualization
- **Memory Stats**: Current cache usage
- **Performance**: Response time trends
- **Tool Usage**: Most used tools and success rates

## Scalability Considerations

### Horizontal Scaling
- **Stateless Design**: No server-side session storage
- **Memory Sharing**: Redis for distributed conversation memory
- **Load Balancing**: Multiple FastAPI instances

### Vertical Scaling
- **Thread Pool**: Configurable worker threads
- **Memory Limits**: Configurable conversation cache size
- **Vector Store**: Scalable FAISS indices

### Production Deployment
- **Docker**: Containerized deployment
- **Environment**: Production-ready configuration
- **Monitoring**: Health checks and metrics
- **Backup**: Vector store and conversation data backup

## Development Workflow

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend  
cd frontend
npm install
npm run dev
```

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end API testing
- **Performance Tests**: Response time and memory benchmarks
- **Load Tests**: Concurrent request handling

### Code Organization
```
backend/
├── main.py                 # FastAPI application
├── graphs/
│   └── fast_agent_graph.py # Main agent logic
├── tools/
│   └── real_tools.py       # Tool implementations
├── retriever/
│   └── real_vector_store.py # Vector store management
└── requirements.txt

frontend/
├── src/
│   ├── components/         # React components
│   ├── services/          # API client
│   └── types/             # TypeScript definitions
├── package.json
└── vite.config.ts
```

This architecture ensures high performance, scalability, and maintainability while providing intelligent AI-powered query processing with memory and context management.