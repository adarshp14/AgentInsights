# InsightFlow API Documentation

## Overview

InsightFlow is a high-performance AI agent backend powered by Google Gemini, LangGraph, and real-time memory management. It provides intelligent query processing with automatic routing between document retrieval (RAG), tool usage, and direct responses.

## Base URL

```
http://localhost:8000
```

## API Endpoints

### Health & Status

#### GET `/`
**Description**: Root endpoint - API status check
**Response**: 
```json
{
  "message": "InsightFlow Backend - Optimized"
}
```

#### GET `/health`
**Description**: Health check endpoint
**Response**:
```json
{
  "status": "healthy"
}
```

### Query Processing

#### POST `/query`
**Description**: Process user queries with intelligent routing and memory management
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "question": "string (required) - User's question",
  "conversation_id": "string (optional) - Conversation identifier for memory persistence"
}
```

**Response**:
```json
{
  "answer": "string - AI-generated response",
  "steps": [
    {
      "node": "string - Processing node name",
      "status": "string - completed|error|in_progress", 
      "timestamp": "number - Unix timestamp in milliseconds",
      "data": {
        "query_type": "string - retrieval|tool_use|direct",
        "processing_time_ms": "number - Processing time",
        "tool_selected": "string - Tool used (if applicable)",
        "documents_found": "number - Documents retrieved (if applicable)",
        "memory_context_used": "boolean - Whether conversation memory was used"
      }
    }
  ],
  "conversation_id": "string - Conversation identifier",
  "metadata": {
    "query_type": "string - Classification result",
    "total_processing_time_ms": "number - Total processing time",
    "documents_used": "number - Number of documents used",
    "steps_executed": "number - Processing steps count",
    "model_used": "string - AI model identifier",
    "memory_enabled": "boolean - Memory system status",
    "performance_optimized": "boolean - Performance optimization status"
  }
}
```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the tax deductions for freelancers in Canada?",
    "conversation_id": "user_123_session"
  }'
```

**Example Response**:
```json
{
  "answer": "As a freelancer in Canada, you can deduct various business expenses...",
  "steps": [
    {
      "node": "QueryClassifier", 
      "status": "completed",
      "timestamp": 1749466800000,
      "data": {
        "query_type": "retrieval",
        "classification_reasoning": "Tax-related query requiring document search",
        "processing_time_ms": 250
      }
    }
  ],
  "conversation_id": "user_123_session",
  "metadata": {
    "query_type": "retrieval",
    "total_processing_time_ms": 1200,
    "documents_used": 3,
    "steps_executed": 4,
    "model_used": "gemini-2.0-flash-exp",
    "memory_enabled": true,
    "performance_optimized": true
  }
}
```

### Memory Management

#### GET `/memory/stats`
**Description**: Get memory and performance statistics
**Response**:
```json
{
  "conversation_cache_size": "number - Cached conversations count",
  "cached_conversations": ["array of conversation IDs"],
  "memory_store_initialized": "boolean - Memory system status",
  "performance_optimizations": ["array of optimization features"]
}
```

#### DELETE `/memory/cache`
**Description**: Clear conversation cache
**Response**:
```json
{
  "status": "success",
  "message": "Cleared X cached conversations"
}
```

### Document Management

#### POST `/upload-document`
**Description**: Upload documents to the vector store
**Content-Type**: `multipart/form-data`

**Request**: 
- `file`: Document file (PDF or TXT)

**Response**:
```json
{
  "status": "success",
  "message": "Document 'filename.pdf' uploaded successfully",
  "filename": "string - Uploaded filename",
  "file_size": "number - File size in bytes", 
  "vector_store_stats": {
    "total_documents": "number",
    "total_chunks": "number"
  }
}
```

#### GET `/vector-store/stats`
**Description**: Get vector store statistics
**Response**:
```json
{
  "total_documents": "number - Total documents in store",
  "total_chunks": "number - Total document chunks",
  "embedding_model": "string - Embedding model used"
}
```

### Tools

#### GET `/tools`
**Description**: List available tools and their capabilities
**Response**:
```json
{
  "web_search": {
    "description": "Search the web for current information",
    "methods": ["search"],
    "parameters": {"query": "string", "num_results": "integer"},
    "requires_api": true
  },
  "calculator": {
    "description": "Perform mathematical calculations",
    "methods": ["calculate"], 
    "parameters": {"expression": "string"},
    "requires_api": false
  },
  "datetime": {
    "description": "Get current date and time information",
    "methods": ["get_current_datetime", "get_today_date"],
    "parameters": {"timezone_name": "string"},
    "requires_api": false
  }
}
```

#### POST `/tools/{tool_name}/{method}`
**Description**: Execute a specific tool method
**Content-Type**: `application/json`

**Example**:
```bash
curl -X POST "http://localhost:8000/tools/datetime/get_today_date" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Query Types & Routing

The system automatically classifies queries into three types:

### 1. Retrieval (RAG)
**Triggers**: Tax rules, legal requirements, business regulations, compliance questions
**Process**: Document search → Context analysis → Response generation
**Example**: "What are the GST requirements for freelancers?"

### 2. Tool Use  
**Triggers**: Calculations, current data, date/time queries
**Process**: Tool selection → Tool execution → Response generation
**Example**: "Calculate 15% of 5000" or "What's the date today?"

### 3. Direct Response
**Triggers**: General knowledge, definitions, casual conversation
**Process**: Direct LLM response using general knowledge
**Example**: "What is artificial intelligence?"

## Memory & Context

### Conversation Memory
- **Automatic**: Conversations are automatically stored per `conversation_id`
- **Context-Aware**: Subsequent queries use previous conversation context
- **Persistent**: Memory persists across sessions
- **Efficient**: Only essential context is stored for performance

### Memory Features
- **Context Continuity**: Understands references to previous topics
- **Smart Classification**: Uses conversation history for better query routing
- **Natural Flow**: Responses flow naturally without explicit context mentions

## Performance Features

### Optimization
- **Singleton Agent**: Initialized once at startup for speed
- **Async Processing**: All operations are asynchronous
- **Thread Pool**: Parallel execution for CPU-intensive tasks
- **Conversation Caching**: In-memory conversation storage
- **Smart Fallbacks**: Robust error handling with intelligent fallbacks

### Response Times
- **Direct Queries**: ~1 second
- **Tool Usage**: ~0.7 seconds  
- **Document Retrieval**: ~1.5 seconds
- **Overall**: 80-90% faster than previous versions

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message describing the issue"
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error
- `503`: Service Unavailable (agent not initialized)

## Rate Limiting & Quotas

### Google Gemini API
- **Model**: gemini-2.0-flash-exp
- **Rate Limits**: Based on Google Cloud quotas
- **Fallback**: Intelligent error handling when limits exceeded

### Recommendations
- **Production**: Implement your own rate limiting
- **API Keys**: Use your own Google API key for production
- **Monitoring**: Monitor API usage and costs

## Security Considerations

### API Security
- **CORS**: Configured for development (update for production)
- **Input Validation**: All inputs are validated
- **Error Handling**: Sensitive information is not exposed in errors

### Production Deployment
1. **API Keys**: Store in secure environment variables
2. **HTTPS**: Use HTTPS in production
3. **Authentication**: Implement API authentication as needed
4. **Rate Limiting**: Add production-grade rate limiting

## Integration Examples

### Python
```python
import requests

def query_agent(question, conversation_id="default"):
    response = requests.post(
        "http://localhost:8000/query",
        json={"question": question, "conversation_id": conversation_id}
    )
    return response.json()

# Example usage
result = query_agent("What are business expense deductions?")
print(result["answer"])
```

### JavaScript/Node.js
```javascript
async function queryAgent(question, conversationId = "default") {
  const response = await fetch("http://localhost:8000/query", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      question: question,
      conversation_id: conversationId
    })
  });
  return await response.json();
}

// Example usage
const result = await queryAgent("Calculate 15% of 2500");
console.log(result.answer);
```

### cURL
```bash
# Simple query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is GST in Canada?"}'

# With conversation memory
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What about the rate?", "conversation_id": "user_123"}'
```

## API Versioning

**Current Version**: 2.0.0 (Optimized)
**Base Path**: `/` (no versioning prefix currently)
**Future**: Versioning will be added as `/v2/` when needed

## Support & Resources

- **GitHub Repository**: [AgentInsights](https://github.com/adarshp14/AgentInsights)
- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: This document and README.md
- **Model**: Google Gemini 2.0 Flash Experimental