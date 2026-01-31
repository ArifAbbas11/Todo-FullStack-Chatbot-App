# Quickstart Guide: AI-Powered Conversational Todo Management

**Feature**: 004-ai-todo-chatbot
**Date**: 2026-01-23
**Purpose**: Setup and running instructions for the conversational todo chatbot

## Overview

This guide walks you through setting up and running the AI-powered conversational todo management system. The system consists of:
- **Backend**: FastAPI server with Google Gemini API and MCP tools
- **Frontend**: ChatKit conversational interface
- **Database**: Neon Serverless PostgreSQL

## Prerequisites

### Required Software
- Python 3.11+ (backend)
- Node.js 18+ and npm (frontend)
- Git (for version control)

### Required Accounts
- Google Gemini API account with API key
- Neon PostgreSQL database (already provisioned)

### Environment Variables

You'll need the following environment variables:

**Backend (.env)**:
```bash
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# CORS
FRONTEND_URL=http://localhost:3000
```

**Frontend (.env.local)**:
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:7860
```

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies to add to requirements.txt**:
```
google-generativeai>=0.3.0
mcp-sdk>=0.1.0  # Official MCP SDK for Python
```

### 4. Configure Environment Variables

Create or update `.env` file:

```bash
cp .env.example .env
# Edit .env and add your Google Gemini API key
```

### 5. Run Database Migrations

```bash
# Create migration for conversations and messages
alembic revision --autogenerate -m "Add conversations and messages tables"

# Apply migration
alembic upgrade head
```

### 6. Verify Database Schema

```bash
# Connect to database and verify tables exist
psql $DATABASE_URL -c "\dt"

# Should show: users, tasks, conversations, messages, alembic_version
```

### 7. Start Backend Server

```bash
# Development mode
uvicorn src.main:app --reload --host 0.0.0.0 --port 7860

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 7860
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 8. Verify Backend Health

```bash
curl http://localhost:7860/health
# Expected: {"status":"healthy","message":"Todo API is running"}

curl http://localhost:7860/docs
# Should open Swagger UI in browser
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

**New dependencies to add to package.json**:
```json
{
  "dependencies": {
    "@chatscope/chat-ui-kit-react": "^2.0.0"
  }
}
```

### 3. Configure Environment Variables

Create or update `.env.local` file:

```bash
cp .env.local.example .env.local
# Edit .env.local and configure API URLs
```

### 4. Start Frontend Development Server

```bash
npm run dev
```

**Expected output**:
```
▲ Next.js 16.1.2 (Turbopack)
- Local:         http://localhost:3000
- Network:       http://10.255.255.254:3000

✓ Starting...
✓ Ready in 2.5s
```

### 5. Verify Frontend

Open browser to http://localhost:3000

You should see the ChatKit interface ready to accept messages.

---

## Testing the System

### 1. Create User Account

```bash
# Using curl
curl -X POST http://localhost:7860/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Expected response:
# {"access_token":"eyJ...", "token_type":"bearer"}
```

### 2. Test Conversational Flows

Open the frontend at http://localhost:3000 and try these commands:

**Create Tasks**:
- "Add a task to buy groceries"
- "Create a task to call mom tomorrow at 3pm"
- "Add three tasks: walk dog, finish report, and buy milk"

**List Tasks**:
- "Show me my tasks"
- "What's on my list?"
- "List all my todos"

**Update Tasks**:
- "Update task 1 to 'Buy organic groceries'"
- "Change the description of task 2"

**Complete Tasks**:
- "Mark task 1 as complete"
- "Complete the groceries task"
- "Mark all my tasks as done"

**Delete Tasks**:
- "Delete task 3"
- "Remove the task about calling mom"

**Conversation Context**:
- "Add a task to buy groceries"
- "Actually, make that organic groceries" (should update the task)

### 3. Test Persistence

1. Create a conversation and add some tasks
2. Note the conversation_id from the response
3. Restart the backend server
4. Continue the conversation - history should be restored

### 4. Test Multi-User Isolation

1. Create two user accounts
2. Have User A create tasks
3. Have User B create tasks
4. Verify User A cannot see User B's tasks

### 5. Test Authentication

```bash
# Try accessing chat endpoint without token
curl -X POST http://localhost:7860/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Show my tasks"}'

# Expected: 401 Unauthorized
```

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'google.generativeai'`
**Solution**: Install Google Gemini SDK: `pip install google-generativeai`

**Problem**: `Database connection failed`
**Solution**: Verify DATABASE_URL in .env and check Neon dashboard

**Problem**: `Gemini API key not found`
**Solution**: Add GEMINI_API_KEY to .env file

**Problem**: `Migration failed: table already exists`
**Solution**: Drop tables and re-run migrations, or use `alembic stamp head`

### Frontend Issues

**Problem**: `Cannot connect to backend`
**Solution**: Verify backend is running on port 7860 and NEXT_PUBLIC_API_URL is correct

**Problem**: `ChatKit not rendering`
**Solution**: Verify @chatscope/chat-ui-kit-react is installed: `npm install @chatscope/chat-ui-kit-react`

**Problem**: `CORS error`
**Solution**: Verify FRONTEND_URL in backend .env matches frontend URL

### Agent Issues

**Problem**: Agent not selecting correct tool
**Solution**: Review system prompt in `src/agents/system_prompt.py`

**Problem**: Tool execution fails
**Solution**: Check MCP tool implementation and user_id injection

**Problem**: Conversation history not loading
**Solution**: Verify conversation_id is being passed correctly

---

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit files in `backend/src/`
   - Server auto-reloads with `--reload` flag
   - Test with curl or Swagger UI at `/docs`

2. **Frontend Changes**:
   - Edit files in `frontend/app/` or `frontend/components/`
   - Next.js auto-reloads in development mode
   - Test in browser at http://localhost:3000

3. **Database Changes**:
   - Edit models in `backend/src/models/`
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Apply migration: `alembic upgrade head`

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Viewing Logs

**Backend logs**:
```bash
# Logs are printed to console
# For production, configure logging to file
```

**Database queries**:
```bash
# Enable SQL logging in src/core/database.py
engine = create_engine(DATABASE_URL, echo=True)
```

---

## Production Deployment

### Backend Deployment

1. Set environment variables in production environment
2. Run migrations: `alembic upgrade head`
3. Start with production server: `uvicorn src.main:app --host 0.0.0.0 --port 7860`
4. Use process manager (systemd, supervisor, or Docker)
5. Configure reverse proxy (nginx) for HTTPS

### Frontend Deployment

1. Build production bundle: `npm run build`
2. Start production server: `npm start`
3. Or deploy to Vercel: `vercel deploy`

### Environment Variables

Ensure all production environment variables are set:
- Use strong SECRET_KEY (generate with `openssl rand -hex 32`)
- Use production DATABASE_URL
- Use production GEMINI_API_KEY
- Set FRONTEND_URL to production domain
- Enable HTTPS in production

---

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:7860/health

# Database connection
curl http://localhost:7860/api/health/db
```

### Metrics to Monitor

- API response time (target: < 3 seconds)
- Google Gemini API latency
- Database query performance
- Conversation history load time
- Tool execution success rate
- Authentication failures

### Logging

Key events to log:
- User authentication attempts
- Tool executions (with user_id)
- Conversation creation
- Errors and exceptions
- Google Gemini API calls

---

## Security Checklist

- [ ] Google Gemini API key stored in environment variable (not hardcoded)
- [ ] JWT secret key is strong and unique
- [ ] Database credentials secured
- [ ] HTTPS enabled in production
- [ ] CORS configured to whitelist only frontend domain
- [ ] User isolation enforced in all MCP tools
- [ ] Input validation on all endpoints
- [ ] Rate limiting configured (future enhancement)

---

## Next Steps

1. **Review this guide** and ensure all prerequisites are met
2. **Set up backend** following steps above
3. **Set up frontend** following steps above
4. **Test conversational flows** to verify system works
5. **Review implementation plan** in [plan.md](./plan.md)
6. **Run `/sp.tasks`** to generate detailed task breakdown
7. **Begin implementation** with Phase 2.1 (Database Layer)

---

## Support

For issues or questions:
- Review [plan.md](./plan.md) for architectural details
- Review [research.md](./research.md) for implementation patterns
- Review [data-model.md](./data-model.md) for database schema
- Check [contracts/](./contracts/) for MCP tool specifications
- Consult Google Gemini API documentation at https://ai.google.dev/docs
- Consult Gemini Function Calling documentation at https://ai.google.dev/docs/function_calling
- Consult MCP documentation at https://modelcontextprotocol.io/

---

## Summary

This quickstart guide provides everything needed to set up and run the AI-powered conversational todo management system. The system is designed to be:

- **Easy to set up**: Clear step-by-step instructions
- **Easy to test**: Conversational test scenarios provided
- **Easy to debug**: Comprehensive troubleshooting section
- **Production-ready**: Deployment and monitoring guidance included

Follow the steps above to get started, and refer to the other planning documents for detailed architectural and implementation guidance.
