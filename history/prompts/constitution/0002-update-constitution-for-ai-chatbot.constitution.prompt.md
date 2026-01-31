---
id: 0002
title: Update constitution for AI chatbot
stage: constitution
date: 2026-01-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: arifabbas-ubuntu
command: /sp.constitution
labels: ["constitution", "ai-chatbot", "mcp", "openai-agents", "phase-iii"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Project: AI-Powered Todo Chatbot with MCP and OpenAI Agents

Core principles:
- Natural language first: Users manage tasks through conversation, not forms
- Agentic design: AI agents must use MCP tools for all task operations
- Stateless backend: Server holds no memory; all state persists in database
- Tool-driven actions: No direct DB writes outside MCP tools
- Security by default: All chat and tool calls require authenticated users
- Reproducibility: Entire system built via Spec-Kit Plus + Claude Code workflow

Key standards:
- All task operations must be executed through MCP tools
- AI agents must follow the defined behavior specification
- Conversation history must persist in the database
- Chat API must be stateless per request
- JWT authentication must be enforced on all endpoints
- User isolation must be guaranteed
- Errors must be handled gracefully with friendly responses
- Tool calls must be logged and returned in API responses

Constraints:
- Technology stack:
  - Frontend: OpenAI ChatKit
  - Backend: Python FastAPI
  - AI Framework: OpenAI Agents SDK
  - MCP Server: Official MCP SDK
  - ORM: SQLModel
  - Database: Neon Serverless PostgreSQL
  - Auth: Better Auth (JWT)
- No manual coding; all implementation via Claude Code
- MCP tools must match the provided specification exactly
- Chat endpoint must follow stateless request cycle
- Only basic Todo features supported (no advanced AI features)
- Timeline: Hackathon Phase III

Success criteria:
- Users can manage todos using natural language
- AI agent correctly selects MCP tools for user intent
- All tool actions persist in the database
- Conversation history is restored across requests
- Server restarts do not break conversations
- Unauthorized users receive 401 responses
- Users can only access their own data
- System follows full Agentic Dev Stack workflow

## Response snapshot

Updated project constitution from v1.0.0 to v2.0.0 with major architectural changes for AI-powered conversational interface.

**Version Change**: 1.0.0 → 2.0.0 (MAJOR)

**Rationale for MAJOR bump**:
- Backward-incompatible architectural paradigm shift
- User interface changed from traditional forms to natural language conversation
- Frontend technology changed from Next.js to OpenAI ChatKit
- Backend architecture changed to stateless with conversation persistence
- New architectural pattern: MCP tools + OpenAI Agents SDK integration
- Tool-driven architecture replaces direct database operations

**Modified Principles**:
1. "Feature Accuracy" → "Natural Language First" (principle redefined)
2. "API Contract Clarity" → "Agentic Design" (new focus on tool-based architecture)
3. "Security-First Development" → "Security by Default" (enhanced with stateless requirements)
4. "Spec-Driven Reproducibility" → Maintained with updated workflow
5. "Multi-User Data Isolation" → Maintained with tool-level enforcement
6. "Responsive Design" → Removed (ChatKit handles UI)

**Added Principles**:
- Principle II: Agentic Design (MCP tools, OpenAI Agents SDK)
- Principle III: Stateless Backend Architecture
- Principle IV: Tool-Driven Actions
- Principle VII: Graceful Error Handling

**Technology Stack Changes**:
- Frontend: Next.js → OpenAI ChatKit
- Added: OpenAI Agents SDK for AI orchestration
- Added: Official MCP SDK for tool standardization
- Backend, Database, Auth remain the same

**Template Compatibility**:
- ✅ spec-template.md - Compatible (user story approach still applies)
- ✅ tasks-template.md - Compatible (task breakdown structure still applies)
- ✅ plan-template.md - Compatible (constitution check will reflect new principles)

## Outcome

- ✅ Impact: Constitution updated to v2.0.0 with 7 core principles for AI-powered chatbot architecture. Major architectural shift from traditional web app to conversational interface with MCP tools and OpenAI Agents SDK.
- 🧪 Tests: N/A (constitution updates are governance documents)
- 📁 Files: Updated .specify/memory/constitution.md (288 lines)
- 🔁 Next prompts: Run `/sp.specify` to create feature specification for AI chatbot with conversational scenarios and MCP tool definitions
- 🧠 Reflection: This represents a fundamental architectural shift. The constitution now enforces tool-driven architecture, stateless backend, and natural language interaction. All future development must follow these new principles.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution updates don't have automated graders)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider creating dedicated templates for MCP tool specifications and agent behavior definitions to support the new architecture
