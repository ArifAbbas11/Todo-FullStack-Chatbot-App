# Implementation Plan: AI-Powered Conversational Todo Management

**Branch**: `004-ai-todo-chatbot` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-todo-chatbot/spec.md`

## Summary

Transform the existing REST API todo application into an AI-powered conversational interface where users manage tasks through natural language. The system uses Google Gemini API for intent interpretation, MCP (Model Context Protocol) tools for all task operations, and a stateless FastAPI backend that persists conversation history in Neon PostgreSQL. The architecture enforces strict separation: ChatKit UI handles presentation, Gemini Agent handles reasoning, MCP tools handle data mutations, and the database handles all persistence.

**Key Technical Approach**:
- Extend existing FastAPI backend with chat endpoint and MCP server
- Add Conversation and Message models to existing User/Task schema
- Implement 5 MCP tools (create_task, list_tasks, update_task, delete_task, complete_task)
- Configure Google Gemini API with MCP tools and system prompt
- Replace Next.js frontend with ChatKit for conversational UI
- Maintain stateless request cycle: load history → process → save → respond

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.109+, SQLModel 0.0.14+, google-generativeai (latest), MCP SDK (official Python), psycopg2-binary 2.9+, python-jose 3.3+ (JWT), passlib 1.7+ (bcrypt)
- Frontend: ChatKit (latest), React 19+
**Storage**: Neon Serverless PostgreSQL (cloud-hosted, connection pooling enabled)
**Testing**: pytest (backend), manual conversational testing (frontend)
**Target Platform**: Linux server (backend), Web browser (frontend)
**Project Type**: Web application (separate frontend + backend)
**Performance Goals**:
- Chat response time < 3 seconds (excluding Gemini API latency)
- Support 50 concurrent users
- 90% intent interpretation accuracy
**Constraints**:
- Stateless backend (no in-memory sessions)
- All state in database
- MCP tools only interface to task data
- JWT authentication on all endpoints
**Scale/Scope**: Hackathon demo supporting multiple users with conversation persistence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Natural Language First ✅
- **Requirement**: Users manage tasks through conversation, not forms
- **Implementation**: ChatKit UI + Google Gemini API for intent interpretation
- **Validation**: User stories P1-P4 all use natural language commands

### Principle II: Agentic Design ✅
- **Requirement**: AI agents use MCP tools for ALL task operations
- **Implementation**: 5 MCP tools registered with agent, no direct DB access outside tools
- **Validation**: All task CRUD operations go through MCP tools

### Principle III: Stateless Backend Architecture ✅
- **Requirement**: No conversation state in memory, all in database
- **Implementation**: Chat endpoint loads history from DB on each request
- **Validation**: Server restart doesn't break conversations (User Story P3)

### Principle IV: Tool-Driven Actions ✅
- **Requirement**: All task operations through MCP tools
- **Implementation**: MCP tools enforce authorization, validation, business logic
- **Validation**: No direct database writes outside tool layer

### Principle V: Security by Default ✅
- **Requirement**: JWT authentication on all endpoints, user isolation
- **Implementation**: Existing JWT middleware + user_id passed to all MCP tools
- **Validation**: User Story P4 tests multi-user isolation

### Principle VI: Spec-Driven Reproducibility ✅
- **Requirement**: Follow Spec-Kit Plus workflow
- **Implementation**: This plan follows specify → plan → tasks → implement
- **Validation**: All artifacts generated via Claude Code

### Principle VII: Graceful Error Handling ✅
- **Requirement**: Friendly conversational error responses
- **Implementation**: Agent interprets tool failures and responds naturally
- **Validation**: Edge cases documented in spec

**Gate Status**: ✅ PASSED - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-todo-chatbot/
├── plan.md              # This file
├── research.md          # Architectural decisions and patterns
├── data-model.md        # Database schema for conversations
├── quickstart.md        # Setup and running instructions
├── contracts/           # MCP tool specifications
│   ├── create_task.json
│   ├── list_tasks.json
│   ├── update_task.json
│   ├── delete_task.json
│   └── complete_task.json
└── checklists/
    └── requirements.md  # Spec validation (already created)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # Existing
│   │   ├── task.py              # Existing
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model
│   ├── api/
│   │   ├── auth.py              # Existing
│   │   ├── tasks.py             # Existing (may deprecate)
│   │   └── chat.py              # NEW: Chat endpoint
│   ├── mcp_tools/               # NEW: MCP tool implementations
│   │   ├── __init__.py
│   │   ├── create_task.py
│   │   ├── list_tasks.py
│   │   ├── update_task.py
│   │   ├── delete_task.py
│   │   └── complete_task.py
│   ├── agents/                  # NEW: Gemini API config
│   │   ├── __init__.py
│   │   ├── gemini_agent.py      # Agent configuration
│   │   └── system_prompt.py     # Agent behavior definition
│   ├── core/
│   │   ├── config.py            # Existing (add GEMINI_API_KEY)
│   │   ├── database.py          # Existing
│   │   └── security.py          # Existing (JWT verification)
│   ├── schemas/
│   │   ├── auth.py              # Existing
│   │   ├── task.py              # Existing
│   │   └── chat.py              # NEW: Chat request/response schemas
│   ├── services/
│   │   ├── auth.py              # Existing
│   │   ├── task.py              # Existing (may deprecate)
│   │   └── conversation.py      # NEW: Conversation management
│   └── main.py                  # Existing (register chat router)
├── alembic/
│   └── versions/
│       └── XXXX_add_conversations.py  # NEW: Migration for conversations
├── requirements.txt             # Add: google-generativeai, mcp-sdk
├── .env                         # Add: GEMINI_API_KEY
└── README.md                    # Update with new architecture

frontend/
├── app/
│   ├── page.tsx                 # NEW: ChatKit integration
│   └── chat/
│       └── page.tsx             # NEW: Chat interface
├── components/
│   ├── ChatInterface.tsx        # NEW: ChatKit wrapper
│   └── MessageList.tsx          # NEW: Message display
├── lib/
│   └── api.ts                   # NEW: Chat API client
├── package.json                 # Add: chatkit library
└── README.md                    # Update with ChatKit setup
```

**Structure Decision**: Web application structure (Option 2) selected because project has separate frontend and backend. Backend extends existing FastAPI structure with new directories for MCP tools and agents. Frontend replaces Next.js pages with ChatKit integration.

## Complexity Tracking

> **No violations** - All constitution principles satisfied without additional complexity.

## Phase 0: Research & Architectural Decisions

See [research.md](./research.md) for detailed architectural decisions including:
- Google Gemini API configuration patterns
- MCP Server SDK integration with FastAPI
- Conversation storage schema design
- Stateless request cycle implementation
- JWT authentication with agent context

## Phase 1: Design Artifacts

### Database Schema

See [data-model.md](./data-model.md) for complete schema including:
- Conversation model (id, user_id, created_at)
- Message model (id, conversation_id, role, content, tool_calls, created_at)
- Relationships: User → Conversations → Messages
- Indexes for efficient history loading

### MCP Tool Contracts

See [contracts/](./contracts/) directory for JSON schemas of all 5 MCP tools:
- create_task: {title: string, description?: string} → {task_id, success, message}
- list_tasks: {} → {tasks: Task[], count}
- update_task: {task_id, title?, description?} → {success, message}
- delete_task: {task_id} → {success, message}
- complete_task: {task_id} → {success, message}

All tools receive user_id from JWT context automatically.

### Setup Instructions

See [quickstart.md](./quickstart.md) for:
- Environment setup (Google Gemini API key, database)
- Backend installation and migration
- Frontend ChatKit configuration
- Running both servers
- Testing conversational flows

## Phase 2: Implementation Phases

### Phase 2.1: Database Layer (Foundation)
**Goal**: Add conversation persistence to existing schema

**Tasks**:
1. Create Conversation model (SQLModel)
2. Create Message model with tool_calls JSON field
3. Create Alembic migration
4. Add conversation service for CRUD operations
5. Test: Create conversation, add messages, load history

**Dependencies**: Existing User and Task models
**Validation**: Can persist and retrieve conversation history

---

### Phase 2.2: MCP Tools Layer (Data Interface)
**Goal**: Implement 5 MCP tools as only interface to task data

**Tasks**:
1. Install MCP SDK for Python
2. Create mcp_tools/ directory structure
3. Implement create_task tool with user_id filtering
4. Implement list_tasks tool with user_id filtering
5. Implement update_task tool with ownership validation
6. Implement delete_task tool with ownership validation
7. Implement complete_task tool with ownership validation
8. Register all tools with MCP server
9. Test: Each tool executes correctly with user isolation

**Dependencies**: Existing Task model, database layer
**Validation**: All tools enforce user isolation, return structured responses

---

### Phase 2.3: Agent Layer (Intent Interpretation)
**Goal**: Configure Google Gemini API with MCP tools

**Tasks**:
1. Install google-generativeai SDK
2. Create agents/ directory structure
3. Define system prompt for task management behavior
4. Configure Gemini model with 5 MCP tools (function calling)
5. Implement agent initialization function
6. Test: Agent selects correct tool for various natural language inputs

**Dependencies**: MCP tools layer
**Validation**: Agent correctly interprets "Add task", "Show tasks", etc.

---

### Phase 2.4: Chat API Layer (Stateless Endpoint)
**Goal**: Implement stateless chat endpoint

**Tasks**:
1. Create chat.py router
2. Implement POST /api/chat endpoint
3. Add JWT authentication middleware
4. Load conversation history from database
5. Send history + new message to agent
6. Save agent response and tool calls to database
7. Return response + tool_calls + conversation_id
8. Test: Stateless request cycle, server restart doesn't break conversations

**Dependencies**: Agent layer, conversation service
**Validation**: Conversations persist across requests and restarts

---

### Phase 2.5: Frontend Layer (ChatKit UI)
**Goal**: Replace Next.js UI with ChatKit conversational interface

**Tasks**:
1. Install ChatKit package (@chatscope/chat-ui-kit-react)
2. Create ChatInterface component
3. Integrate with /api/chat endpoint
4. Persist conversation_id in localStorage
5. Display messages and tool call results
6. Handle loading and error states
7. Test: Can send messages, see responses, conversation persists

**Dependencies**: Chat API layer
**Validation**: Users can manage tasks via natural language

---

### Phase 2.6: Security & Authentication
**Goal**: Enforce JWT authentication and user isolation

**Tasks**:
1. Add JWT verification to chat endpoint
2. Extract user_id from token
3. Pass user_id to all MCP tools
4. Test multi-user isolation
5. Test unauthorized access (401 responses)

**Dependencies**: Existing JWT infrastructure
**Validation**: User Story P4 acceptance scenarios pass

---

### Phase 2.7: Integration & Validation
**Goal**: End-to-end testing of conversational flows

**Tasks**:
1. Test User Story P1: Create and list tasks
2. Test User Story P2: Update, complete, delete tasks
3. Test User Story P3: Conversation persistence
4. Test User Story P4: Multi-user isolation
5. Test all edge cases from spec
6. Verify all success criteria met

**Dependencies**: All previous phases
**Validation**: All acceptance scenarios pass

## Key Architectural Decisions

### Decision 1: MCP Tool-Based Architecture
**Rationale**: Enforces separation of concerns, enables observability, makes system auditable
**Alternatives Considered**: Direct service calls from agent
**Trade-off**: Additional abstraction layer, but gains consistency and testability

### Decision 2: Stateless Chat Design
**Rationale**: Enables horizontal scaling, simplifies deployment, ensures persistence
**Alternatives Considered**: In-memory session storage
**Trade-off**: Database load on each request, but gains reliability and scalability

### Decision 3: Google Gemini API
**Rationale**: Handles tool orchestration via function calling, proven intent interpretation, cost-effective
**Alternatives Considered**: OpenAI API, Claude API, Custom NLP with spaCy/transformers
**Trade-off**: External API dependency, but gains accuracy and development speed

### Decision 4: Conversation Storage in PostgreSQL
**Rationale**: Leverages existing database, ensures ACID properties
**Alternatives Considered**: Redis for conversation cache
**Trade-off**: Slightly higher latency, but gains durability and consistency

### Decision 5: ChatKit for Frontend
**Rationale**: Purpose-built for conversational interfaces, handles message display
**Alternatives Considered**: Custom React chat UI
**Trade-off**: Less customization, but gains development speed and UX patterns

## Validation Strategy

### Conversational Flow Testing
- "Add a task to buy groceries" → creates task
- "Show me my tasks" → lists tasks
- "Complete task 1" → marks complete
- "Delete task 2" → removes task
- Follow-up: "Actually, make that organic groceries" → uses context

### Tool Correctness Testing
- Each MCP tool returns correct schema
- User isolation enforced (User A can't see User B's tasks)
- Validation errors handled gracefully
- Database transactions atomic

### Persistence Testing
- Create conversation, restart server, continue conversation
- Long conversation (100+ messages) loads correctly
- Concurrent requests don't corrupt state

### Authentication Testing
- Invalid JWT returns 401
- Expired JWT returns 401
- Missing JWT returns 401
- User_id correctly extracted and passed to tools

## Success Metrics

- ✅ Users create tasks in < 10 seconds via natural language
- ✅ 90%+ intent interpretation accuracy
- ✅ 100% conversation persistence across restarts
- ✅ 100% user isolation (zero cross-user data leaks)
- ✅ < 3 second response time (excluding Gemini latency)
- ✅ 100% tool call observability
- ✅ 50 concurrent users supported
- ✅ 95% first-attempt task creation success rate
- ✅ 100% graceful error handling
- ✅ 10+ message context maintained

## Next Steps

1. Review this plan with stakeholders
2. Run `/sp.tasks` to generate detailed task breakdown
3. Begin implementation with Phase 2.1 (Database Layer)
4. Use specialized agents:
   - `neon-db-manager` for database schema
   - `fastapi-backend-dev` for MCP tools and chat endpoint
   - `auth-security` for JWT integration
5. Document decisions in ADRs as needed
6. Create PHRs for each implementation phase
