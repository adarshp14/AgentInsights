# InsightFlow Multi-Tenant Architecture

## System Overview

InsightFlow is a production-ready multi-tenant SaaS platform for AI-powered knowledge management. Built with modern technologies, it provides secure organization-isolated document processing, intelligent query handling, and comprehensive user management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MULTI-TENANT SAAS PLATFORM                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│ │ Authentication  │ │ Dashboard       │ │ Admin Panel     │               │
│ │ - Login Flow    │ │ - Chat Interface│ │ - User Mgmt     │               │
│ │ - Onboarding    │ │ - Document View │ │ - Org Settings  │               │
│ │ - Org Selection │ │ - Analytics     │ │ - Role Control  │               │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘               │
│                                                                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│ │ UI Components   │ │ State Mgmt      │ │ Security        │               │
│ │ - SaaS Design   │ │ - JWT Tokens    │ │ - Token Storage │               │
│ │ - Responsive    │ │ - Org Context   │ │ - Auto Logout   │               │
│ │ - Modern UX     │ │ - User Profile  │ │ - Route Guards  │               │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                               BACKEND LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│ │ API Routes      │ │ Authentication  │ │ Authorization   │               │
│ │ - /auth/*       │ │ - JWT Tokens    │ │ - Role-based    │               │
│ │ - /orgs/*       │ │ - Password Hash │ │ - Org Isolation │               │
│ │ - /docs/*       │ │ - Session Mgmt  │ │ - Admin/Employee│               │
│ │ - /query/*      │ │ - Multi-tenant  │ │ - Secure Access │               │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘               │
│                                                                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│ │ Services Layer  │ │ AI Agents       │ │ Vector Store    │               │
│ │ - OrgService    │ │ - Gemini 2.0    │ │ - ChromaDB      │               │
│ │ - AuthService   │ │ - LangGraph     │ │ - Org Isolation │               │
│ │ - DocumentService│ │ - RAG Pipeline  │ │ - Embeddings    │               │
│ │ - UserService   │ │ - Tool Router   │ │ - Search Index  │               │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│ │ Organizations   │ │ Users           │ │ Documents       │               │
│ │ - org_id (PK)   │ │ - user_id (PK)  │ │ - doc_id (PK)   │               │
│ │ - org_name      │ │ - org_id (FK)   │ │ - org_id (FK)   │               │
│ │ - domain        │ │ - email         │ │ - filename      │               │
│ │ - plan_type     │ │ - password_hash │ │ - file_path     │               │
│ │ - settings      │ │ - role          │ │ - uploaded_by   │               │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘               │
│                                                                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│ │ Embeddings      │ │ Sessions        │ │ Search Logs     │               │
│ │ - embed_id (PK) │ │ - session_id    │ │ - log_id (PK)   │               │
│ │ - doc_id (FK)   │ │ - user_id (FK)  │ │ - user_id (FK)  │               │
│ │ - org_id (FK)   │ │ - org_id (FK)   │ │ - org_id (FK)   │               │
│ │ - chunk_text    │ │ - session_data  │ │ - query_text    │               │
│ │ - vector        │ │ - created_at    │ │ - timestamp     │               │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Multi-Tenant Architecture

### Organization Isolation
- **Complete Data Separation**: Each organization has isolated data at database and vector store levels
- **Secure Authentication**: JWT tokens contain org_id claims for context-aware access control
- **Role-Based Access**: Admin and employee roles with different permissions within organizations
- **Custom Domains**: Optional domain-based organization detection

### Security Model
- **JWT Authentication**: Stateless tokens with organization context
- **Password Security**: bcrypt hashing with secure salt rounds
- **API Authorization**: Every endpoint validates org membership and role permissions
- **Vector Store Isolation**: Separate ChromaDB collections per organization (org_{hash}_docs)

### Database Schema
- **Foreign Key Relationships**: All entities linked to org_id for data integrity
- **Audit Trail**: Created/updated timestamps on all records
- **Soft Deletes**: Maintain data integrity while allowing logical deletion
- **Indexing**: Optimized queries with proper database indexes

## Technology Stack

### Frontend
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for modern, responsive design
- **Vite** for fast development and optimized builds
- **SaaS-inspired UI** with professional authentication flows

### Backend
- **FastAPI** with async support for high performance
- **SQLAlchemy** ORM with Alembic migrations
- **Pydantic** for data validation and serialization
- **JWT** for stateless authentication
- **bcrypt** for secure password hashing

### AI & ML
- **Google Gemini 2.0 Flash** for intelligent responses
- **LangGraph** for complex AI agent workflows
- **ChromaDB** for vector embeddings and similarity search
- **Sentence Transformers** for document embeddings

### Infrastructure
- **SQLite/PostgreSQL** for reliable data storage
- **ChromaDB** for vector operations
- **File System** for document storage with organization isolation
- **RESTful APIs** with OpenAPI documentation

## Deployment Architecture

### Development
- **Frontend**: Vite dev server (http://localhost:5173)
- **Backend**: Uvicorn ASGI server (http://localhost:8001)
- **Database**: SQLite for rapid development
- **Vector Store**: Local ChromaDB instance

### Production (Recommended)
- **Frontend**: Static files served via CDN (Vercel, Netlify)
- **Backend**: Containerized FastAPI with gunicorn
- **Database**: PostgreSQL with connection pooling
- **Vector Store**: ChromaDB cluster or cloud service
- **Load Balancer**: nginx for SSL termination and routing

## API Endpoints

### Authentication
- `POST /auth/login` - User authentication with org context
- `POST /auth/register/{org_id}` - Register user within organization
- `GET /auth/profile` - Get current user profile
- `PUT /auth/password` - Update user password

### Organizations
- `POST /organizations/register` - Create new organization with admin
- `GET /organizations/{org_id}` - Get organization details
- `PUT /organizations/{org_id}` - Update organization settings
- `GET /organizations/{org_id}/stats` - Organization analytics

### Documents
- `POST /documents/upload` - Upload document to org vector store
- `GET /documents` - List organization documents
- `DELETE /documents/{doc_id}` - Remove document from org
- `GET /documents/{doc_id}/status` - Check processing status

### AI Query
- `POST /query/ask` - Process query with RAG pipeline
- `POST /query/stream` - Streaming query responses
- `GET /query/history` - User query history
- `POST /query/feedback` - Submit response feedback

## Security Considerations

### Data Protection
- **Encryption at Rest**: Sensitive data encrypted in database
- **TLS in Transit**: All API communications over HTTPS
- **Input Validation**: Comprehensive validation using Pydantic
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy

### Access Control
- **JWT Validation**: Every protected endpoint validates tokens
- **Organization Isolation**: Strict org_id filtering on all data operations
- **Role Enforcement**: Admin/employee permissions properly enforced
- **Rate Limiting**: API rate limits to prevent abuse

### Compliance
- **Data Retention**: Configurable retention policies per organization
- **Audit Logging**: Comprehensive logging of user actions
- **Privacy Controls**: User data deletion and export capabilities
- **GDPR Ready**: Architecture supports compliance requirements

## Performance Optimizations

### Database
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Indexed foreign keys and common queries
- **Lazy Loading**: Efficient relationship loading strategies

### Vector Operations
- **Batch Processing**: Bulk embedding operations
- **Caching**: Frequently accessed embeddings cached
- **Parallel Processing**: Concurrent document processing

### API Performance
- **Async Operations**: Non-blocking I/O throughout
- **Response Caching**: Cache static and computed data
- **Compression**: Gzip compression for API responses

## Monitoring & Observability

### Application Metrics
- **Response Times**: API endpoint performance tracking
- **Error Rates**: Exception monitoring and alerting
- **User Analytics**: Query patterns and usage statistics

### Infrastructure Metrics
- **Database Performance**: Query execution times and connections
- **Vector Store Health**: Embedding operations and search latency
- **Resource Utilization**: CPU, memory, and disk usage

This architecture provides a robust foundation for a scalable, secure, and maintainable multi-tenant AI knowledge management platform.