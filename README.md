# InsightFlow - AI Agent Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript)](https://typescriptlang.org/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?style=flat&logo=google)](https://ai.google.dev/)

A high-performance AI agent platform powered by Google Gemini 2.0, featuring intelligent query processing, conversation memory, document retrieval (RAG), and real-time tool integration.

## 🚀 Features

### Core Capabilities
- **🧠 Intelligent Query Processing** - Automatic routing between RAG, tools, and direct responses
- **💾 Conversation Memory** - Persistent context across sessions with natural flow
- **📚 Document Retrieval (RAG)** - FAISS-powered vector search with embeddings
- **🛠️ Real-time Tools** - Calculator, DateTime, Web Search integration
- **⚡ High Performance** - 80-90% faster with async processing and caching
- **🔄 Real-time Dashboard** - Live query processing visualization

### Technical Highlights
- **Singleton Agent Pattern** - Optimized initialization and memory usage
- **LangGraph Orchestration** - Advanced workflow management
- **Thread Pool Execution** - Parallel processing for speed
- **Smart Classification** - Context-aware query routing
- **Public API** - Fully accessible REST endpoints

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│    Backend      │───▶│   AI Models     │
│   React + TS    │    │   FastAPI       │    │  Google Gemini  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                      │                      │
│ • Real-time UI       │ • LangGraph Agent   │ • Gemini 2.0 Flash
│ • Query Analytics    │ • Memory Management │ • SentenceTransformers
│ • Tool Integration   │ • Vector Store      │ • FAISS Indexing
│ • Performance Dash   │ • Tool Registry     │ • External APIs
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical architecture.

## 📋 Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Google API Key** for Gemini access
- **Git** for version control

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/AgentInsights.git
cd AgentInsights
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your_google_api_key_here"
# Optional API keys for enhanced features:
# export SERPAPI_API_KEY="your_search_api_key"
# export WEATHERAPI_KEY="your_weather_api_key"

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Required
GOOGLE_API_KEY=your_google_gemini_api_key

# Optional - for enhanced tool capabilities
SERPAPI_API_KEY=your_serpapi_key_for_web_search
WEATHERAPI_KEY=your_weather_api_key
OPENWEATHERMAP_API_KEY=your_openweather_key

# Server Configuration (optional)
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

### Getting API Keys

1. **Google Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and set as `GOOGLE_API_KEY`

2. **Search API (Optional)**:
   - Visit [SerpAPI](https://serpapi.com/) for web search
   - Get free tier API key

3. **Weather API (Optional)**:
   - Visit [WeatherAPI](https://www.weatherapi.com/) or [OpenWeatherMap](https://openweathermap.org/api)
   - Get free tier API key

## 📖 API Usage

### Basic Query Processing
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the tax deductions for freelancers?",
    "conversation_id": "user_123"
  }'
```

### Response Format
```json
{
  "answer": "As a freelancer, you can deduct various business expenses...",
  "steps": [
    {
      "node": "QueryClassifier",
      "status": "completed",
      "timestamp": 1672531200000,
      "data": {
        "query_type": "retrieval",
        "processing_time_ms": 250
      }
    }
  ],
  "conversation_id": "user_123",
  "metadata": {
    "query_type": "retrieval",
    "total_processing_time_ms": 1200,
    "documents_used": 3,
    "model_used": "gemini-2.0-flash-exp"
  }
}
```

### Document Upload
```bash
curl -X POST "http://localhost:8000/upload-document" \
  -F "file=@document.pdf"
```

### Memory Management
```bash
# Get memory statistics
curl "http://localhost:8000/memory/stats"

# Clear conversation cache
curl -X DELETE "http://localhost:8000/memory/cache"
```

### Tool Execution
```bash
# Get current date
curl -X POST "http://localhost:8000/tools/datetime/get_today_date" \
  -H "Content-Type: application/json" -d '{}'

# Calculate percentage
curl -X POST "http://localhost:8000/tools/calculator/calculate" \
  -H "Content-Type: application/json" \
  -d '{"expression": "15% of 2500"}'
```

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for comprehensive API reference.

## 🛠️ Development

### Project Structure
```
AgentInsights/
├── backend/                    # FastAPI backend
│   ├── main.py                # FastAPI application
│   ├── graphs/                # LangGraph agent logic
│   │   └── fast_agent_graph.py
│   ├── tools/                 # Tool implementations
│   │   └── real_tools.py
│   ├── retriever/             # Vector store management
│   │   └── real_vector_store.py
│   └── requirements.txt
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   └── types/             # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
└── docs/                     # Documentation
    ├── API_DOCUMENTATION.md
    └── ARCHITECTURE.md
```

### Adding New Tools
1. Create tool class in `backend/tools/real_tools.py`:
```python
class MyCustomTool:
    def execute(self, **kwargs):
        # Your tool logic here
        return {"result": "tool output"}
```

2. Register in `RealToolRegistry`:
```python
self.tools["my_tool"] = MyCustomTool()
```

3. Update query classification in `fast_agent_graph.py`

### Adding New Documents
```python
# Via API
POST /upload-document (with file)

# Programmatically
from retriever.real_vector_store import RealVectorStore
vector_store = RealVectorStore(embeddings)
vector_store.add_document_from_text(content, metadata)
```

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## 📊 Performance

### Benchmarks
- **Direct Queries**: ~1 second average
- **Tool Usage**: ~0.7 seconds average  
- **Document Retrieval**: ~1.5 seconds average
- **Memory Operations**: <100ms
- **Overall Improvement**: 80-90% faster than previous versions

### Optimization Features
- **Singleton Pattern**: Single agent initialization
- **Async Processing**: Non-blocking I/O operations
- **Thread Pool**: Parallel execution for CPU tasks
- **Smart Caching**: In-memory conversation storage
- **Vector Optimization**: FAISS indexing with reduced retrieval

## 🔍 Query Types

The system automatically classifies and routes queries:

### 1. Retrieval (RAG)
**Triggers**: Tax rules, legal requirements, business regulations  
**Example**: "What are GST requirements for freelancers?"

### 2. Tool Use
**Triggers**: Calculations, current data, date/time queries  
**Example**: "Calculate 15% of 5000" or "What's the date today?"

### 3. Direct Response
**Triggers**: General knowledge, definitions, casual conversation  
**Example**: "What is artificial intelligence?"

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individually
docker build -t insightflow-backend backend/
docker build -t insightflow-frontend frontend/

docker run -p 8000:8000 insightflow-backend
docker run -p 3000:3000 insightflow-frontend
```

### Environment Setup
```bash
# Production environment variables
export GOOGLE_API_KEY="your_production_api_key"
export ENVIRONMENT="production"
export LOG_LEVEL="WARNING"
export PORT=8000
```

### Security Considerations
- **API Keys**: Store in secure environment variables
- **CORS**: Configure appropriate origins for production
- **Rate Limiting**: Implement API rate limiting
- **HTTPS**: Use HTTPS in production
- **Authentication**: Add API authentication as needed

## 🔮 Roadmap

### Upcoming Features
- [ ] **LangMem Integration** - Advanced memory management
- [ ] **Multi-language Support** - i18n for global users
- [ ] **Plugin System** - Custom tool development
- [ ] **Advanced Analytics** - Usage insights and metrics
- [ ] **Enterprise Features** - Authentication, rate limiting, monitoring
- [ ] **Mobile App** - React Native mobile client

### Performance Goals
- [ ] Sub-second response times for all query types
- [ ] Horizontal scaling support
- [ ] Advanced caching strategies
- [ ] Real-time streaming responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Add tests for new features
- Update documentation
- Ensure API compatibility

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/yourusername/AgentInsights/issues)
- **Documentation**: [API Docs](docs/API_DOCUMENTATION.md) | [Architecture](docs/ARCHITECTURE.md)
- **Examples**: See `examples/` directory

### Common Issues

**Agent not initializing**:
```bash
# Check API key
echo $GOOGLE_API_KEY

# Check dependencies
pip install -r requirements.txt
```

**CORS errors**:
- Ensure frontend URL is in CORS origins
- Check browser console for specific errors

**Memory not working**:
- Verify conversation_id is consistent
- Check `/memory/stats` endpoint

## 📈 Metrics & Analytics

### Real-time Monitoring
- Query processing times
- Memory usage statistics  
- Tool usage patterns
- Error rates and types
- User conversation flows

### Performance Tracking
- Response time percentiles
- Cache hit rates
- API endpoint usage
- Document retrieval efficiency

---

**Built with ❤️ using Google Gemini, FastAPI, React, and LangGraph**

For detailed technical documentation, see [docs/](docs/) directory.