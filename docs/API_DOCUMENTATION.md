# InsightFlow API Documentation

## Overview

InsightFlow provides a comprehensive REST API for multi-tenant AI-powered knowledge management. The API is built with FastAPI and provides secure, organization-isolated access to document management, AI querying, and user administration.

## Base URL
- **Development**: `http://localhost:8001`
- **Production**: `https://api.insightflow.com`

## Authentication

### JWT Token Authentication
All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### Token Claims
JWT tokens contain the following claims:
- `user_id`: Unique user identifier
- `org_id`: Organization identifier for multi-tenant isolation
- `email`: User email address
- `role`: User role (admin, employee)
- `exp`: Token expiration timestamp

## API Endpoints

### Authentication Endpoints

#### POST /auth/login
Authenticate user and return JWT token with organization context.

**Request Body:**
```json
{
  "email": "user@company.com",
  "password": "securepassword123",
  "org_id": "optional-org-uuid"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user_id": "user-uuid",
    "org_id": "org-uuid",
    "role": "admin"
  },
  "user": {
    "user_id": "user-uuid",
    "email": "user@company.com",
    "full_name": "John Doe",
    "role": "admin",
    "org_id": "org-uuid",
    "org_name": "Company Name"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

#### POST /auth/register/{org_id}
Register a new user within an existing organization.

**Path Parameters:**
- `org_id` (string): UUID of the organization

**Request Body:**
```json
{
  "email": "newuser@company.com",
  "full_name": "Jane Smith",
  "password": "securepassword123",
  "role": "employee"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "user_id": "new-user-uuid",
  "message": "User registered successfully"
}
```

#### GET /auth/profile
Get current user profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "user_id": "user-uuid",
  "email": "user@company.com",
  "full_name": "John Doe",
  "role": "admin",
  "org_id": "org-uuid",
  "org_name": "Company Name",
  "last_login": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T09:00:00Z"
}
```

### Organization Endpoints

#### POST /organizations/register
Create a new organization with admin user. This is the primary onboarding endpoint.

**Request Body:**
```json
{
  "org_name": "My Company",
  "domain": "mycompany.com",
  "plan_type": "starter",
  "admin_name": "John Admin",
  "admin_email": "admin@mycompany.com",
  "admin_password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "org_id": "new-org-uuid",
  "message": "Organization 'My Company' created successfully",
  "admin_user_id": "admin-user-uuid",
  "next_steps": [
    "Set up authentication for admin user",
    "Upload first documents to knowledge base",
    "Invite team members",
    "Configure RAG settings"
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Organization with name 'My Company' already exists"
}
```

#### GET /organizations/{org_id}
Get organization details and settings.

**Path Parameters:**
- `org_id` (string): UUID of the organization

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "org_id": "org-uuid",
  "org_name": "My Company",
  "domain": "mycompany.com",
  "plan_type": "professional",
  "is_active": true,
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

#### PUT /organizations/{org_id}
Update organization settings (Admin only).

**Path Parameters:**
- `org_id` (string): UUID of the organization

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "org_name": "Updated Company Name",
  "domain": "newdomain.com",
  "plan_type": "enterprise",
  "settings": {
    "similarity_threshold": 0.8,
    "max_documents_per_query": 10,
    "response_style": "detailed"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Organization updated successfully"
}
```

### Document Management Endpoints

#### POST /documents/upload
Upload a document to the organization's knowledge base.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Form Data:**
```
file: <binary_file_data>
```

**Supported File Types:**
- PDF (.pdf)
- Text files (.txt)
- Word documents (.docx)

**Response (200 OK):**
```json
{
  "success": true,
  "document_id": "doc-uuid",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024768,
  "chunks_created": 15,
  "processing_status": "completed",
  "message": "Document uploaded and processed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Unsupported file type. Please upload PDF, TXT, or DOCX files."
}
```

#### GET /documents
List all documents in the organization.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `skip` (int, optional): Number of documents to skip (default: 0)
- `limit` (int, optional): Maximum number of documents to return (default: 50)
- `status` (string, optional): Filter by processing status

**Response (200 OK):**
```json
{
  "documents": [
    {
      "document_id": "doc-uuid-1",
      "filename": "company-handbook.pdf",
      "original_filename": "Company Handbook 2024.pdf",
      "file_type": "pdf",
      "file_size": 2048576,
      "processing_status": "completed",
      "chunks_created": 25,
      "uploaded_by": "user-uuid",
      "upload_date": "2024-01-10T14:30:00Z",
      "processed_date": "2024-01-10T14:32:15Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

#### DELETE /documents/{document_id}
Delete a document from the organization's knowledge base.

**Path Parameters:**
- `document_id` (string): UUID of the document

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

#### GET /documents/{document_id}/status
Get processing status of a specific document.

**Path Parameters:**
- `document_id` (string): UUID of the document

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "document_id": "doc-uuid",
  "filename": "document.pdf",
  "processing_status": "processing",
  "chunks_created": 10,
  "total_chunks_expected": 15,
  "processing_progress": 67,
  "started_at": "2024-01-15T10:00:00Z",
  "estimated_completion": "2024-01-15T10:05:00Z"
}
```

### AI Query Endpoints

#### POST /query/ask
Process a query against the organization's knowledge base using RAG.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What is our company policy on remote work?",
  "conversation_id": "optional-conversation-uuid",
  "max_documents": 5,
  "similarity_threshold": 0.7
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response": "Based on the company handbook, our remote work policy allows employees to work from home up to 3 days per week with manager approval...",
  "sources": [
    {
      "document_id": "doc-uuid",
      "filename": "company-handbook.pdf",
      "chunk_text": "Remote work policy: Employees may work remotely...",
      "relevance_score": 0.92,
      "page_number": 15
    }
  ],
  "conversation_id": "conversation-uuid",
  "query_id": "query-uuid",
  "processing_time_ms": 1250
}
```

#### POST /query/stream
Process a query with streaming response for real-time AI interaction.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Explain our quarterly sales process",
  "conversation_id": "conversation-uuid"
}
```

**Response (200 OK - Server-Sent Events):**
```
data: {"type": "start", "query_id": "query-uuid"}

data: {"type": "thinking", "message": "Searching relevant documents..."}

data: {"type": "sources", "documents": [{"filename": "sales-process.pdf", "relevance": 0.89}]}

data: {"type": "content", "text": "Our quarterly"}

data: {"type": "content", "text": " sales process consists"}

data: {"type": "content", "text": " of four main phases..."}

data: {"type": "complete", "total_time_ms": 2500}
```

#### GET /query/history
Get user's query history within the organization.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `limit` (int, optional): Maximum number of queries to return (default: 20)
- `offset` (int, optional): Number of queries to skip (default: 0)

**Response (200 OK):**
```json
{
  "queries": [
    {
      "query_id": "query-uuid",
      "query_text": "What is our company policy on remote work?",
      "response_summary": "Remote work policy allows 3 days per week...",
      "timestamp": "2024-01-15T14:30:00Z",
      "processing_time_ms": 1250,
      "sources_count": 3
    }
  ],
  "total": 25,
  "limit": 20,
  "offset": 0
}
```

### Health and System Endpoints

#### GET /health
Check system health and component status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "agents": {
    "streaming_agent": true,
    "fallback_agent": true
  },
  "vector_store": true,
  "database": true,
  "timestamp": "2024-01-15T15:30:00Z"
}
```

#### GET /docs
Access interactive API documentation (Swagger UI).

#### GET /redoc
Access alternative API documentation (ReDoc).

## Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T15:30:00Z"
}
```

### HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters or body
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Common Error Codes
- `INVALID_TOKEN`: JWT token is invalid or expired
- `ORGANIZATION_NOT_FOUND`: Specified organization does not exist
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `DOCUMENT_PROCESSING_FAILED`: Document upload or processing failed
- `QUERY_TIMEOUT`: AI query processing timed out
- `RATE_LIMIT_EXCEEDED`: Too many requests from user/organization

## Rate Limiting

### Limits by Endpoint Type
- **Authentication**: 10 requests per minute per IP
- **Document Upload**: 5 requests per minute per user
- **AI Queries**: 50 requests per hour per user
- **General API**: 1000 requests per hour per organization

### Rate Limit Headers
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642284600
```

## SDKs and Integration

### cURL Examples

**Organization Registration:**
```bash
curl -X POST "http://localhost:8001/organizations/register" \
  -H "Content-Type: application/json" \
  -d '{
    "org_name": "My Company",
    "domain": "mycompany.com",
    "plan_type": "starter",
    "admin_name": "John Admin",
    "admin_email": "admin@mycompany.com",
    "admin_password": "securepassword123"
  }'
```

**User Login:**
```bash
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@mycompany.com",
    "password": "securepassword123"
  }'
```

**Document Upload:**
```bash
curl -X POST "http://localhost:8001/documents/upload" \
  -H "Authorization: Bearer <jwt_token>" \
  -F "file=@document.pdf"
```

**AI Query:**
```bash
curl -X POST "http://localhost:8001/query/ask" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are our sales targets for Q2?",
    "max_documents": 5
  }'
```

### Python SDK Example
```python
import requests

class InsightFlowClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
    
    def login(self, email, password):
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data["token"]["access_token"]
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })
        return data
    
    def query(self, text, conversation_id=None):
        return self.session.post(
            f"{self.base_url}/query/ask",
            json={
                "query": text,
                "conversation_id": conversation_id
            }
        ).json()

# Usage
client = InsightFlowClient("http://localhost:8001")
client.login("admin@company.com", "password123")
result = client.query("What is our remote work policy?")
print(result["response"])
```

## Security Best Practices

### API Key Management
- Store JWT tokens securely (e.g., httpOnly cookies, secure storage)
- Implement token refresh before expiration
- Clear tokens on logout or session end

### Request Security
- Always use HTTPS in production
- Validate and sanitize all input data
- Implement proper CORS policies
- Use rate limiting to prevent abuse

### Data Protection
- Encrypt sensitive data in transit and at rest
- Implement proper access controls
- Log security-relevant events
- Regular security audits and updates

This API provides a comprehensive foundation for building secure, scalable multi-tenant AI applications with InsightFlow.