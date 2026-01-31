# Tasks: AI-Powered Conversational Todo Management

**Input**: Design documents from `/specs/004-ai-todo-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded. Focus is on implementation and manual conversational testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/`
- Web application structure with separate frontend and backend

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install Google Gemini API SDK in backend/requirements.txt (google-generativeai>=0.3.0)
- [X] T002 [P] Install MCP SDK for Python in backend/requirements.txt (mcp-sdk>=0.1.0)
- [X] T003 [P] Add GEMINI_API_KEY to backend/.env configuration
- [X] T004 [P] Install ChatKit package in frontend/package.json (@chatscope/chat-ui-kit-react)
- [X] T005 [P] Configure CORS in backend to allow frontend origin
- [X] T006 Create backend/src/mcp_tools/ directory structure
- [X] T007 [P] Create backend/src/agents/ directory structure
- [X] T008 [P] Create backend/src/schemas/chat.py for chat request/response schemas

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [X] T009 Create Conversation model in backend/src/models/conversation.py with SQLModel
- [X] T010 [P] Create Message model in backend/src/models/message.py with SQLModel and JSON tool_calls field
- [X] T011 Create Alembic migration for conversations and messages tables in backend/alembic/versions/
- [X] T012 Run Alembic migration to create tables in Neon PostgreSQL database
- [X] T013 [P] Create conversation service in backend/src/services/conversation.py for CRUD operations

### MCP Tools Infrastructure

- [X] T014 Create MCP tool registry in backend/src/mcp_tools/__init__.py
- [X] T015 [P] Define MCP tool schemas for all 5 tools in backend/src/mcp_tools/schemas.py
- [X] T016 [P] Create base MCP tool executor function in backend/src/mcp_tools/executor.py

### Gemini API Configuration

- [X] T017 Create system prompt definition in backend/src/agents/system_prompt.py
- [X] T018 Create Gemini agent initialization in backend/src/agents/gemini_agent.py
- [X] T019 Configure Gemini model with MCP tool schemas in backend/src/agents/gemini_agent.py
- [X] T020 Implement conversation history formatting for Gemini API in backend/src/agents/gemini_agent.py

### Authentication Integration

- [X] T021 Verify JWT authentication middleware in backend/src/core/security.py
- [X] T022 Create user_id extraction helper for MCP tools in backend/src/core/security.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and List Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks and view their task list using natural conversational language

**Independent Test**: Send "Add a task to buy groceries" and "Show me my tasks" through chat interface, verify task creation and listing

### MCP Tools for User Story 1

- [X] T023 [P] [US1] Implement create_task MCP tool in backend/src/mcp_tools/create_task.py
- [X] T024 [P] [US1] Implement list_tasks MCP tool in backend/src/mcp_tools/list_tasks.py
- [X] T025 [US1] Register create_task and list_tasks tools with MCP registry in backend/src/mcp_tools/__init__.py

### Chat Endpoint for User Story 1

- [X] T026 [US1] Create chat router in backend/src/api/chat.py
- [X] T027 [US1] Implement POST /api/chat endpoint with JWT authentication in backend/src/api/chat.py
- [X] T028 [US1] Add conversation creation logic for new conversations in backend/src/api/chat.py
- [X] T029 [US1] Integrate Gemini agent with create_task and list_tasks tools in backend/src/api/chat.py
- [X] T030 [US1] Implement message persistence (user and assistant) in backend/src/api/chat.py
- [X] T031 [US1] Add tool call logging to message records in backend/src/api/chat.py
- [X] T032 [US1] Register chat router in backend/src/main.py

### Frontend for User Story 1

- [X] T033 [US1] Create ChatInterface component in frontend/components/ChatInterface.tsx
- [X] T034 [US1] Integrate ChatKit UI components in frontend/components/ChatInterface.tsx
- [X] T035 [US1] Create chat API client in frontend/lib/api.ts
- [X] T036 [US1] Implement message sending and receiving in frontend/components/ChatInterface.tsx
- [X] T037 [US1] Add conversation_id persistence in localStorage in frontend/components/ChatInterface.tsx
- [X] T038 [US1] Create chat page in frontend/app/chat/page.tsx
- [X] T039 [US1] Add authentication check to chat page in frontend/app/chat/page.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create and list tasks via natural language

---

## Phase 4: User Story 2 - Update, Complete, and Delete Tasks (Priority: P2)

**Goal**: Users can modify existing tasks, mark them as complete, or delete them using natural language

**Independent Test**: Create tasks using US1, then issue commands like "Mark task 2 as complete", "Update task 1 to 'Buy organic groceries'", "Delete task 3"

### MCP Tools for User Story 2

- [X] T040 [P] [US2] Implement update_task MCP tool in backend/src/mcp_tools/update_task.py
- [X] T041 [P] [US2] Implement complete_task MCP tool in backend/src/mcp_tools/complete_task.py
- [X] T042 [P] [US2] Implement delete_task MCP tool in backend/src/mcp_tools/delete_task.py
- [X] T043 [US2] Register update_task, complete_task, and delete_task tools with MCP registry in backend/src/mcp_tools/__init__.py

### Agent Configuration for User Story 2

- [X] T044 [US2] Update Gemini agent configuration to include update_task, complete_task, delete_task tools in backend/src/agents/gemini_agent.py
- [X] T045 [US2] Update system prompt to include update, complete, and delete capabilities in backend/src/agents/system_prompt.py

### Frontend Updates for User Story 2

- [X] T046 [US2] Update ChatInterface to display tool call results for update/complete/delete in frontend/components/ChatInterface.tsx
- [X] T047 [US2] Add visual feedback for task state changes in frontend/components/ChatInterface.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - full CRUD operations via natural language

---

## Phase 5: User Story 3 - Conversation Persistence and Context (Priority: P3)

**Goal**: Users can continue conversations across sessions with full context maintained

**Independent Test**: Create conversation, add tasks, close chat, reopen (or restart server), continue conversation with references like "Actually, make that organic groceries"

### Conversation History Implementation

- [X] T048 [US3] Implement conversation history loading in backend/src/services/conversation.py
- [X] T049 [US3] Add conversation history to Gemini agent context in backend/src/api/chat.py
- [X] T050 [US3] Implement conversation_id validation and ownership check in backend/src/api/chat.py
- [X] T051 [US3] Update conversation.updated_at timestamp on new messages in backend/src/services/conversation.py

### Context Management

- [X] T052 [US3] Implement conversation history formatting for Gemini API in backend/src/agents/gemini_agent.py
- [X] T053 [US3] Add context window management (limit to last 100 messages) in backend/src/services/conversation.py
- [X] T054 [US3] Handle conversation context in tool execution in backend/src/mcp_tools/executor.py

### Frontend Persistence

- [X] T055 [US3] Implement conversation restoration on page load in frontend/components/ChatInterface.tsx
- [X] T056 [US3] Add conversation history display in frontend/components/MessageList.tsx
- [X] T057 [US3] Handle conversation_id in URL or localStorage in frontend/app/chat/page.tsx

**Checkpoint**: At this point, all conversation context is preserved across sessions and server restarts

---

## Phase 6: User Story 4 - Multi-User Isolation and Security (Priority: P4)

**Goal**: Each user can only access and manage their own tasks with strict isolation enforced

**Independent Test**: Create two user accounts, have each create tasks, verify User A cannot see or modify User B's tasks

### Security Implementation

- [X] T058 [US4] Add user_id injection to all MCP tool calls in backend/src/mcp_tools/executor.py
- [X] T059 [US4] Implement ownership validation in create_task tool in backend/src/mcp_tools/create_task.py
- [X] T060 [US4] Implement ownership validation in list_tasks tool in backend/src/mcp_tools/list_tasks.py
- [X] T061 [US4] Implement ownership validation in update_task tool in backend/src/mcp_tools/update_task.py
- [X] T062 [US4] Implement ownership validation in complete_task tool in backend/src/mcp_tools/complete_task.py
- [X] T063 [US4] Implement ownership validation in delete_task tool in backend/src/mcp_tools/delete_task.py
- [X] T064 [US4] Add conversation ownership validation in backend/src/services/conversation.py
- [X] T065 [US4] Verify JWT token validation on chat endpoint in backend/src/api/chat.py

### Error Handling

- [X] T066 [US4] Implement generic error responses for unauthorized access in backend/src/mcp_tools/executor.py
- [X] T067 [US4] Add 401 error handling for invalid/expired tokens in backend/src/api/chat.py
- [X] T068 [US4] Implement friendly error messages for tool failures in backend/src/agents/gemini_agent.py

**Checkpoint**: All user stories complete with full security isolation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling & Validation

- [X] T069 [P] Add input validation for all MCP tools in backend/src/mcp_tools/
- [ ] T070 [P] Implement graceful error handling for Gemini API failures in backend/src/agents/gemini_agent.py
- [ ] T071 [P] Add database connection error handling in backend/src/core/database.py
- [ ] T072 [P] Implement frontend error display in frontend/components/ChatInterface.tsx

### Logging & Observability

- [ ] T073 [P] Add structured logging for all tool executions in backend/src/mcp_tools/executor.py
- [ ] T074 [P] Add logging for conversation creation and loading in backend/src/services/conversation.py
- [ ] T075 [P] Add logging for Gemini API calls in backend/src/agents/gemini_agent.py

### Documentation & Validation

- [ ] T076 [P] Update backend README with Gemini API setup instructions in backend/README.md
- [ ] T077 [P] Update frontend README with ChatKit setup instructions in frontend/README.md
- [ ] T078 Run quickstart.md validation scenarios
- [ ] T079 Verify all acceptance scenarios from spec.md
- [ ] T080 Test edge cases documented in spec.md

### Performance Optimization

- [ ] T081 [P] Add database indexes for conversation queries in Alembic migration
- [ ] T082 [P] Implement conversation history pagination if needed in backend/src/services/conversation.py
- [ ] T083 [P] Optimize Gemini API request payload size in backend/src/agents/gemini_agent.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Extends US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - Adds persistence to US1/US2
  - User Story 4 (P4): Can start after Foundational - Adds security to all stories
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - Core conversational task management
- **User Story 2 (P2)**: Independent - Extends task operations but doesn't break US1
- **User Story 3 (P3)**: Independent - Adds persistence without changing US1/US2 behavior
- **User Story 4 (P4)**: Independent - Adds security layer to all existing functionality

### Within Each User Story

- MCP tools before agent configuration
- Agent configuration before chat endpoint
- Chat endpoint before frontend integration
- Core implementation before error handling

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T004, T005, T007, T008)
- All Foundational tasks marked [P] can run in parallel within their subsections
- MCP tools within a user story marked [P] can run in parallel
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all MCP tools for User Story 1 together:
Task: "Implement create_task MCP tool in backend/src/mcp_tools/create_task.py"
Task: "Implement list_tasks MCP tool in backend/src/mcp_tools/list_tasks.py"

# Then sequentially:
Task: "Register create_task and list_tasks tools with MCP registry"
Task: "Implement POST /api/chat endpoint with JWT authentication"
Task: "Create ChatInterface component in frontend/components/ChatInterface.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch all MCP tools for User Story 2 together:
Task: "Implement update_task MCP tool in backend/src/mcp_tools/update_task.py"
Task: "Implement complete_task MCP tool in backend/src/mcp_tools/complete_task.py"
Task: "Implement delete_task MCP tool in backend/src/mcp_tools/delete_task.py"

# Then sequentially:
Task: "Register update_task, complete_task, and delete_task tools with MCP registry"
Task: "Update Gemini agent configuration to include new tools"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T022) - CRITICAL
3. Complete Phase 3: User Story 1 (T023-T039)
4. **STOP and VALIDATE**: Test conversational task creation and listing
5. Deploy/demo if ready

**MVP Deliverable**: Users can create and list tasks via natural language conversation

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Full CRUD)
4. Add User Story 3 → Test independently → Deploy/Demo (Persistence)
5. Add User Story 4 → Test independently → Deploy/Demo (Security)
6. Add Polish → Final validation → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T022)
2. Once Foundational is done:
   - Developer A: User Story 1 (T023-T039)
   - Developer B: User Story 2 (T040-T047)
   - Developer C: User Story 3 (T048-T057)
   - Developer D: User Story 4 (T058-T068)
3. Stories complete and integrate independently
4. Team completes Polish together (T069-T083)

---

## Task Summary

- **Total Tasks**: 83
- **Setup Phase**: 8 tasks
- **Foundational Phase**: 14 tasks (BLOCKING)
- **User Story 1 (P1)**: 17 tasks - MVP
- **User Story 2 (P2)**: 8 tasks
- **User Story 3 (P3)**: 10 tasks
- **User Story 4 (P4)**: 11 tasks
- **Polish Phase**: 15 tasks

### Parallel Opportunities Identified

- **Setup**: 6 parallel tasks (T002, T003, T004, T005, T007, T008)
- **Foundational**: 5 parallel tasks (T010, T013, T015, T016, T022)
- **User Story 1**: 2 parallel tasks (T023, T024)
- **User Story 2**: 3 parallel tasks (T040, T041, T042)
- **User Story 4**: 6 parallel tasks (T059-T063, T064)
- **Polish**: 12 parallel tasks (T069-T075, T076-T077, T081-T083)

### Independent Test Criteria

- **User Story 1**: Send "Add a task to buy groceries" and "Show me my tasks" - verify task creation and listing
- **User Story 2**: Issue "Mark task 2 as complete", "Update task 1", "Delete task 3" - verify all operations work
- **User Story 3**: Create conversation, restart server, continue conversation - verify context preserved
- **User Story 4**: Create two users, verify User A cannot access User B's tasks - verify isolation

### Suggested MVP Scope

**Minimum Viable Product**: User Story 1 only (T001-T039)
- Users can create and list tasks via natural language
- Demonstrates core conversational AI architecture
- Showcases Google Gemini API integration
- Proves MCP tool orchestration works
- Delivers immediate value to hackathon judges

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks use Google Gemini API (not OpenAI)
- Environment variable: GEMINI_API_KEY
- Package: google-generativeai
- Model: gemini-1.5-pro
