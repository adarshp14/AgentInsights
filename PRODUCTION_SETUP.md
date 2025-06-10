# AgentInsights Production Setup Guide

## 🚀 Enterprise-Ready Multi-Tenant SaaS Platform

This guide will help you deploy AgentInsights to production with enterprise-grade security, authentication, and multi-tenant support.

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and pip
- Git
- Domain name (for production deployment)

## 🔑 Required API Keys

### 1. Google API Key (Required)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. **IMPORTANT:** Delete any compromised keys:
   - `AIzaSyCFms8dpbNDruOOg8Oasy3_wc_D3AqNUbM` (if it exists)

### 2. Clerk Authentication (Required)
1. Create account at [Clerk Dashboard](https://dashboard.clerk.com/)
2. Create a new application
3. **IMPORTANT:** Delete any compromised keys:
   - `pk_test_ZGVzdGluZWQtYmx1ZWdpbGwtMTEuY2xlcmsuYWNjb3VudHMuZGV2JA`
   - `sk_test_c8z2Ar5Lx46gXhg5Y9XuNerua79Do4LXjPWiGcc7zk`
4. Get your new publishable and secret keys

### 3. Configure Clerk Organizations
1. In Clerk Dashboard, go to **Organization Settings**
2. Enable **Organizations** feature
3. Configure **Organization Roles**:
   - `org:admin` - Full access to organization management
   - `org:member` - Employee access to knowledge base
4. Set **Organization Creation** to "Admins only" or "Anyone"

## ⚙️ Environment Setup

### Backend Configuration

Create `/backend/.env`:
```bash
# Google AI Configuration
GOOGLE_API_KEY=your_new_google_api_key_here

# Clerk Authentication
CLERK_SECRET_KEY=your_new_clerk_secret_key_here

# Database (SQLite for development, PostgreSQL for production)
DATABASE_URL=sqlite:///./multi_tenant_app.db

# CORS Origins (update for production domains)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Optional: Web Search
GOOGLE_CSE_ID=your_custom_search_engine_id
GOOGLE_CSE_API_KEY=your_search_api_key
```

### Frontend Configuration

Create `/frontend/.env`:
```bash
# Clerk Authentication
VITE_CLERK_PUBLISHABLE_KEY=your_new_clerk_publishable_key_here

# Backend API URL (update for production)
VITE_API_URL=https://api.yourdomain.com
```

## 🛠️ Installation & Deployment

### 1. Clone Repository
```bash
git clone https://github.com/adarshp14/AgentInsights.git
cd AgentInsights
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Start Development
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🏭 Production Deployment

### Backend (FastAPI)
**Recommended: Railway, Render, or AWS Lambda**

1. **Environment Variables**: Set all `.env` variables in your deployment platform
2. **Database**: Upgrade to PostgreSQL for production:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```
3. **HTTPS**: Ensure SSL/TLS certificates are configured
4. **CORS**: Update `CORS_ORIGINS` with your production domains

### Frontend (React/Vite)
**Recommended: Vercel, Netlify, or CloudFlare Pages**

1. **Build Command**: `npm run build`
2. **Output Directory**: `dist`
3. **Environment Variables**: Set `VITE_CLERK_PUBLISHABLE_KEY` and `VITE_API_URL`
4. **Custom Domain**: Configure your domain in the platform settings

## 🔐 Security Configuration

### 1. Clerk Security Settings
- Enable **Multi-Factor Authentication**
- Set up **Session Management** policies
- Configure **Password Requirements**
- Enable **Suspicious Activity** monitoring

### 2. API Security
- Enable **Rate Limiting** in production
- Set up **Request Logging** and monitoring
- Configure **CORS** for specific domains only
- Use **HTTPS only** in production

### 3. Database Security
- Use **environment variables** for all credentials
- Enable **connection encryption**
- Set up **regular backups**
- Implement **access logging**

## 👥 User Management

### Organization Admins Can:
- Create and manage organizations
- Invite and manage team members
- Upload and organize documents
- Configure organization settings
- View analytics and usage metrics

### Employees Can:
- Access AI-powered knowledge base
- Ask questions about organization documents
- View their query history
- Search and browse documents
- Manage their profile settings

## 📊 Features Overview

### ✅ Authentication & Security
- Enterprise-grade authentication with Clerk
- Multi-tenant organization support
- Role-based access control (RBAC)
- Secure JWT token validation
- Organization isolation

### ✅ Document Management
- Multi-format support (PDF, DOCX, TXT)
- Automatic text extraction and chunking
- Vector store with semantic search
- Organization-scoped document access
- Upload progress tracking

### ✅ AI-Powered Knowledge Base
- Google Gemini 2.0 Flash integration
- Retrieval Augmented Generation (RAG)
- Real-time streaming responses
- Context-aware conversations
- Intelligent query routing

### ✅ Modern SaaS Interface
- Professional dashboard layouts
- Real-time metrics and analytics
- Responsive design for all devices
- Dark/light mode support
- Organization switching

## 🚨 Security Checklist

- [ ] All API keys regenerated and secure
- [ ] HTTPS enabled in production
- [ ] CORS configured for specific domains
- [ ] Environment variables set (no hardcoded secrets)
- [ ] Database access secured
- [ ] Clerk security features enabled
- [ ] Regular security monitoring enabled
- [ ] Backup procedures established

## 📈 Monitoring & Analytics

### Built-in Metrics
- Document upload and processing status
- User engagement and query metrics
- Organization-level usage statistics
- Real-time system health monitoring

### Recommended Additional Tools
- **Error Tracking**: Sentry
- **Performance Monitoring**: DataDog or New Relic
- **Uptime Monitoring**: Pingdom or UptimeRobot
- **Log Management**: LogRocket or Papertrail

## 🆘 Support & Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Clerk keys are correctly set
   - Check CORS configuration
   - Ensure organization settings are enabled

2. **Document Upload Failures**
   - Verify Google API key is valid
   - Check file size limits (10MB default)
   - Ensure proper file format (PDF, DOCX, TXT)

3. **API Connection Issues**
   - Verify backend URL in frontend `.env`
   - Check firewall and port configurations
   - Ensure SSL certificates are valid

### Getting Help
- Check logs in your deployment platform
- Review Clerk dashboard for authentication issues
- Monitor Google AI Studio for API usage and quotas

---

## 🎉 Congratulations!

Your AgentInsights platform is now ready for enterprise deployment with:
- **10,000 free monthly active users** (Clerk)
- **100 free organizations** (Clerk)
- **Unlimited documents** and AI queries
- **Enterprise-grade security** and authentication
- **Multi-tenant architecture** with complete isolation

Ready to scale your organization's knowledge management! 🚀