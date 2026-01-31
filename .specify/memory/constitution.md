<!--
Sync Impact Report:
- Version: 1.0.0 → 2.0.0 (Major architectural shift to AI-powered conversational interface)
- Rationale: MAJOR version bump due to backward-incompatible changes:
  - User interface paradigm shift: Traditional forms → Natural language conversation
  - New architectural pattern: MCP tools + OpenAI Agents SDK integration
  - Frontend technology change: Next.js → OpenAI ChatKit
  - Backend becomes stateless with conversation persistence
  - Tool-driven architecture replaces direct database operations
- Modified Principles:
  - "Feature Accuracy" → "Natural Language First" (principle redefined)
  - "API Contract Clarity" → "Agentic Design" (new focus on tool-based architecture)
  - "Security-First Development" → Enhanced with stateless authentication requirements
  - "Spec-Driven Reproducibility" → Maintained with updated workflow
  - "Multi-User Data Isolation" → Maintained with tool-level enforcement
  - "Responsive Design" → Removed (ChatKit handles UI)
- Added Sections:
  - Principle II: Agentic Design (MCP tools, OpenAI Agents SDK)
  - Principle III: Stateless Backend Architecture
  - Principle IV: Tool-Driven Actions
  - Enhanced security requirements for chat endpoints
- Removed Sections:
  - Principle VI: Responsive Design (no longer applicable with ChatKit)
  - Next.js specific frontend requirements
- Templates Status:
  ✅ spec-template.md - Compatible, user story approach still applies
  ✅ tasks-template.md - Compatible, task breakdown structure still applies
  ✅ plan-template.md - Compatible, constitution check will reflect new principles
  ⚠ May need new templates for MCP tool specifications and agent behavior definitions
- Follow-up TODOs:
  - Consider creating MCP tool specification template
  - Consider creating agent behavior specification template
  - Update quickstart.md with new setup instructions for OpenAI Agents SDK and MCP Server
-->

# AI-Powered Todo Chatbot Constitution

## Core Principles

### I. Natural Language First

Users MUST manage tasks through natural conversation, not traditional forms or UI controls. The system MUST interpret user intent from conversational input and execute appropriate actions through AI agents. All task operations MUST be accessible via natural language commands.

**Conversational Requirements**:
- Users express intent in plain English (e.g., "Add a task to buy groceries")
- AI agent interprets intent and selects appropriate MCP tools
- System responds with friendly, conversational feedback
- No forms, buttons, or traditional CRUD interfaces required
- Conversation history provides context for follow-up requests

**Rationale**: Natural language interfaces reduce friction and make task management more intuitive. Users should interact with the system as they would with a human assistant, not navigate complex UIs.

### II. Agentic Design

AI agents MUST use MCP (Model Context Protocol) tools for ALL task operations. Agents MUST NOT directly access the database or perform operations outside the defined tool set. Tool selection MUST be driven by user intent interpretation, not hardcoded logic.

**Agent Requirements**:
- OpenAI Agents SDK handles conversation and tool orchestration
- MCP Server provides standardized tools for task operations (create, read, update, delete, list)
- Agents select tools based on user intent analysis
- Tool calls MUST be logged and returned in API responses
- Agent behavior MUST follow defined specification for consistency

**Tool Architecture**:
- MCP tools are the ONLY interface to task data
- Each tool has clear input/output contracts
- Tools handle validation, authorization, and database operations
- Tools return structured responses for agent interpretation
- No direct database writes outside MCP tools

**Rationale**: Tool-driven architecture ensures consistent behavior, enables observability, and maintains clear separation between AI reasoning and data operations. MCP provides standardization for tool interfaces.

### III. Stateless Backend Architecture

The backend server MUST hold no conversation state in memory. All conversation history MUST persist in the database. Each chat request MUST be self-contained with full conversation context. Server restarts MUST NOT break ongoing conversations.

**Stateless Requirements**:
- Chat endpoint receives full conversation history with each request
- Backend reconstructs context from database on every request
- No in-memory session storage or conversation caching
- Conversation history stored in database with user_id association
- Server can scale horizontally without session affinity

**Request Cycle**:
1. Client sends message + conversation_id (or null for new conversation)
2. Backend loads conversation history from database
3. Backend sends history + new message to OpenAI Agents SDK
4. Agent processes message, may call MCP tools
5. Backend saves updated conversation history to database
6. Backend returns agent response + tool call logs to client

**Rationale**: Stateless architecture enables horizontal scaling, simplifies deployment, and ensures conversation persistence across server restarts. Critical for production reliability.

### IV. Tool-Driven Actions

All task operations MUST be executed through MCP tools. No direct database writes are permitted outside the tool layer. Tools MUST enforce authorization, validation, and business logic. Agent responses MUST reflect tool execution results.

**Tool Enforcement**:
- Create task → `create_task` MCP tool
- List tasks → `list_tasks` MCP tool
- Update task → `update_task` MCP tool
- Delete task → `delete_task` MCP tool
- Mark complete → `complete_task` MCP tool
- Tools validate input and check user ownership
- Tools return success/failure with descriptive messages
- Agent interprets tool results and responds conversationally

**Rationale**: Tool-driven architecture provides a single source of truth for operations, enables consistent authorization enforcement, and makes the system auditable and testable.

### V. Security by Default

JWT-based authentication MUST be enforced on all chat and tool endpoints. User data isolation MUST be guaranteed at the tool level. Conversation history MUST be filtered by authenticated user. Unauthorized requests MUST return 401 responses.

**Security Requirements**:
- JWT token verified on every chat request
- User ID extracted from token and passed to tools
- MCP tools filter all queries by authenticated user_id
- Conversation history isolated per user
- Tool calls include user context for authorization
- Invalid/expired tokens return 401 Unauthorized
- No cross-user data access permitted

**Tool-Level Authorization**:
- Every MCP tool receives authenticated user_id
- Tools query database with WHERE user_id = {authenticated_user_id}
- Create operations automatically set user_id from token
- Update/Delete operations verify ownership before execution
- List operations return only current user's data

**Rationale**: Multi-user applications require strict security boundaries. Tool-level enforcement ensures no operation can bypass authorization checks.

### VI. Spec-Driven Reproducibility

Development MUST follow the Spec-Kit Plus workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding is permitted. All implementation decisions MUST be traceable to specification documents.

**Workflow Steps**:
1. `/sp.specify` - Create detailed feature specification with conversational scenarios
2. `/sp.plan` - Generate architectural plan including MCP tool definitions and agent behavior
3. `/sp.tasks` - Break down into testable, prioritized tasks
4. Implement using specialized agents (auth-security, fastapi-backend-dev, neon-db-manager)
5. Document with PHRs and ADRs

**Agent Usage**:
- `auth-security` for JWT authentication and user isolation
- `fastapi-backend-dev` for chat endpoint and MCP server implementation
- `neon-db-manager` for database schema and conversation storage
- General-purpose agent for OpenAI Agents SDK integration

**Rationale**: Reproducibility is a core evaluation criterion for hackathon projects. The development process itself demonstrates systematic engineering practices.

### VII. Graceful Error Handling

All errors MUST be handled gracefully with friendly, conversational responses. System failures MUST NOT expose technical details to users. Tool failures MUST be interpreted by the agent and communicated naturally. Conversation flow MUST continue even after errors.

**Error Handling Requirements**:
- Tool failures return structured error messages
- Agent interprets errors and responds conversationally
- No stack traces or technical jargon in user-facing responses
- Validation errors explained in plain language
- System errors result in "I'm having trouble with that" style responses
- Conversation history preserved even when errors occur

**Example Error Responses**:
- Tool validation failure → "I couldn't add that task because the title is required."
- Authorization failure → "I can only show you your own tasks."
- System error → "I'm having trouble completing that request right now. Please try again."

**Rationale**: Conversational interfaces must maintain natural interaction even during failures. Technical errors should be logged but not exposed to users.

## Technology Stack Constraints

The following technology stack is MANDATORY and MUST NOT be substituted:

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | OpenAI ChatKit | Latest |
| Backend | Python FastAPI | Latest stable |
| AI Framework | OpenAI Agents SDK | Latest |
| MCP Server | Official MCP SDK | Latest |
| ORM | SQLModel | Latest stable |
| Database | Neon Serverless PostgreSQL | Latest |
| Authentication | Better Auth (JWT tokens) | Latest |
| Development | Claude Code + Spec-Kit Plus | Current |

**Additional Constraints**:
- Backend MUST implement both chat endpoint and MCP server
- Chat endpoint MUST be stateless (no in-memory conversation state)
- MCP tools MUST match specification exactly (create, read, update, delete, list, complete)
- Conversation history MUST persist in database with user_id association
- Environment variables MUST be used for all configuration (OpenAI API keys, database URLs, JWT secrets)
- Database migrations MUST be version-controlled and reversible
- CORS MUST be configured to allow frontend-backend communication

**Rationale**: Technology stack is specified by hackathon Phase III requirements. OpenAI Agents SDK and MCP Server are core to the agentic architecture.

## Development Workflow

### Spec-Driven Development Process

1. **Specification Phase** (`/sp.specify`)
   - Write conversational scenarios (user says X, system does Y)
   - Define MCP tool specifications (inputs, outputs, behavior)
   - Define agent behavior specification (how to interpret intent)
   - Identify acceptance criteria for conversational interactions
   - Prioritize scenarios (P1, P2, P3)

2. **Planning Phase** (`/sp.plan`)
   - Research OpenAI Agents SDK and MCP Server integration
   - Design conversation storage schema
   - Define MCP tool implementations
   - Design stateless chat endpoint architecture
   - Document in `plan.md`, `research.md`, `data-model.md`, `contracts/`

3. **Task Breakdown** (`/sp.tasks`)
   - Generate dependency-ordered task list
   - Group tasks by scenario for independent implementation
   - Mark parallel tasks with [P] flag
   - Include exact file paths in task descriptions
   - Output to `tasks.md`

4. **Implementation Phase**
   - Use specialized agents for each domain:
     - `auth-security` for JWT authentication
     - `fastapi-backend-dev` for chat endpoint and MCP server
     - `neon-db-manager` for database schema and conversation storage
   - Implement tasks in priority order (P1 → P2 → P3)
   - Each scenario MUST be independently testable
   - Commit after each completed task or logical group

5. **Documentation Phase**
   - Create Prompt History Records (PHRs) for all significant work
   - Suggest ADRs for architectural decisions (MCP tool design, agent behavior)
   - Update quickstart.md with setup instructions for OpenAI Agents SDK

### Agent Usage Rules

- **Authentication work** → MUST use `auth-security` agent
- **Chat endpoint and MCP server** → MUST use `fastapi-backend-dev` agent
- **Database schema and conversation storage** → MUST use `neon-db-manager` agent
- **OpenAI Agents SDK integration** → Use general-purpose agent with clear scope
- **Cross-cutting concerns** → Use general-purpose agent with clear scope

### Quality Gates

Before considering any phase complete:
- [ ] All placeholders in documents resolved
- [ ] Constitution principles verified
- [ ] No hardcoded secrets or API keys
- [ ] MCP tool contracts documented and consistent
- [ ] User isolation enforced in all tools
- [ ] Conversation history persists correctly
- [ ] Stateless backend verified (server restart doesn't break conversations)
- [ ] Agent behavior follows specification

## Governance

### Amendment Process

This constitution supersedes all other development practices. Amendments require:
1. Documented justification for the change
2. Impact analysis on existing specifications and code
3. Version bump following semantic versioning
4. Update to all dependent templates and documentation

### Versioning Policy

Constitution versions follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Backward-incompatible changes (principle removal, technology stack change, architectural paradigm shift)
- **MINOR**: New principles added or existing principles materially expanded
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Review

All pull requests and code reviews MUST verify:
- Adherence to core principles
- Technology stack compliance
- Security requirements met
- Spec-driven workflow followed
- Proper agent usage for specialized tasks
- MCP tools used for all task operations
- Stateless backend architecture maintained

### Complexity Justification

Any deviation from simplicity principles MUST be justified in the implementation plan's Complexity Tracking section. Unjustified complexity will be rejected in code review.

**Version**: 2.0.0 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-01-23
