# Research: AI-Powered Conversational Todo Management

**Date**: 2026-01-23
**Feature**: 004-ai-todo-chatbot
**Purpose**: Document architectural decisions and implementation patterns for conversational todo management with Google Gemini API and MCP tools

## 1. Google Gemini API Integration

### Decision: Use Google Gemini API for Intent Interpretation

**Rationale**:
- Proven accuracy for natural language understanding
- Built-in tool orchestration and function calling
- Handles conversation context management
- Reduces development time compared to custom NLP
- Cost-effective and performant for agentic systems

**Implementation Pattern**:

```python
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)

# Agent configuration with MCP tools
def create_agent():
    return genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=SYSTEM_PROMPT,
        tools=[
            create_task_schema,
            list_tasks_schema,
            update_task_schema,
            delete_task_schema,
            complete_task_schema
        ]
    )

# Process message with agent
def process_message(conversation_history, new_message, user_id):
    # Initialize model
    model = create_agent()

    # Build conversation history for Gemini
    history = []
    for msg in conversation_history:
        history.append({
            "role": msg.role,
            "parts": [msg.content]
        })

    # Start chat with history
    chat = model.start_chat(history=history)

    # Send message and get response
    response = chat.send_message(new_message)

    # Handle function calls if present
    if response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                # Execute MCP tool
                tool_name = part.function_call.name
                tool_args = dict(part.function_call.args)
                tool_args["user_id"] = user_id

                # Execute tool
                tool_result = MCP_TOOLS[tool_name](**tool_args)

                # Send tool result back to model
                response = chat.send_message(
                    genai.types.FunctionResponse(
                        name=tool_name,
                        response=tool_result
                    )
                )

    # Extract final text response
    return response.text
```

**System Prompt Design**:

```python
SYSTEM_PROMPT = """You are a helpful todo assistant that helps users manage their tasks through natural conversation.

Your capabilities:
- Create new tasks when users describe what they need to do
- List all tasks when users ask to see their tasks
- Update task details when users want to modify them
- Mark tasks as complete when users finish them
- Delete tasks when users no longer need them

Guidelines:
- Be friendly and conversational
- Confirm actions with clear messages (e.g., "I've added 'buy groceries' to your tasks")
- When listing tasks, present them in a readable format with IDs
- If a request is ambiguous, ask clarifying questions
- Handle errors gracefully without exposing technical details
- Use conversation context to understand references like "the first one" or "that task"

Always use the provided tools to perform task operations. Never make up task data.
"""
```

**Alternatives Considered**:
- Custom NLP with spaCy/transformers: More control but requires training data and maintenance
- LangChain agents: Additional abstraction layer, less direct control
- OpenAI API with function calling: Similar capability but Gemini API more cost-effective
- Claude API with function calling: Similar capability but Gemini API better for this use case

**Trade-offs**:
- ✅ High accuracy, proven patterns, fast development, cost-effective
- ❌ External API dependency, cost per request, latency

---

## 2. MCP Server SDK Implementation

### Decision: Implement MCP Tools as Python Functions with JSON Schemas

**Rationale**:
- MCP (Model Context Protocol) provides standardized tool interface
- Clear separation between agent reasoning and data operations
- Enables observability and auditing of all tool calls
- Enforces consistent input/output contracts
- Simplifies testing and validation

**Implementation Pattern**:

```python
# MCP Tool Schema Definition
create_task_schema = {
    "name": "create_task",
    "description": "Create a new todo task for the user",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The task title (required, max 500 characters)"
            },
            "description": {
                "type": "string",
                "description": "Optional task description (max 2000 characters)"
            }
        },
        "required": ["title"]
    }
}

# MCP Tool Implementation
def create_task_tool(title: str, description: str = None, user_id: UUID = None):
    """
    Create a new task for the authenticated user.

    Args:
        title: Task title (required)
        description: Optional task description
        user_id: Authenticated user ID (injected from JWT)

    Returns:
        dict: {task_id, success, message}
    """
    try:
        # Validate input
        if not title or len(title) > 500:
            return {
                "success": False,
                "message": "Task title is required and must be under 500 characters"
            }

        # Create task in database
        task = Task(
            user_id=user_id,
            title=title,
            description=description
        )

        with Session(engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

        return {
            "success": True,
            "task_id": str(task.id),
            "message": f"Task '{title}' created successfully"
        }

    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {
            "success": False,
            "message": "Failed to create task. Please try again."
        }

# Tool Registration
MCP_TOOLS = {
    "create_task": create_task_tool,
    "list_tasks": list_tasks_tool,
    "update_task": update_task_tool,
    "delete_task": delete_task_tool,
    "complete_task": complete_task_tool
}

# Tool Execution with User Context
def execute_mcp_tools(tool_calls, user_id):
    """Execute MCP tools with user context from JWT."""
    tool_outputs = []

    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # Inject user_id into tool arguments
        tool_args["user_id"] = user_id

        # Execute tool
        tool_function = MCP_TOOLS[tool_name]
        result = tool_function(**tool_args)

        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": json.dumps(result)
        })

    return tool_outputs
```

**Alternatives Considered**:
- Direct service layer calls: Less observability, harder to audit
- GraphQL mutations: More complex, not standard for agent tools
- REST API calls from agent: Additional network overhead

**Trade-offs**:
- ✅ Clear contracts, easy testing, full observability
- ❌ Additional abstraction layer, slight performance overhead

---

## 3. Conversation Storage Schema

### Decision: Store Conversations and Messages in PostgreSQL with JSON Tool Calls

**Rationale**:
- Leverages existing Neon PostgreSQL infrastructure
- ACID properties ensure data consistency
- Efficient querying with proper indexes
- JSON field for flexible tool call storage
- Supports conversation history reconstruction

**Database Schema**:

```python
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """Conversation between user and AI agent."""
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    """Individual message within a conversation."""
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True
    )
    role: str = Field(
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        description="Message text content"
    )
    tool_calls: Optional[dict] = Field(
        default=None,
        sa_type=JSON,
        description="Tool calls made by assistant (JSON)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True
    )
```

**Indexes for Performance**:
```sql
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**Conversation Loading Pattern**:

```python
def load_conversation_history(conversation_id: UUID, user_id: UUID):
    """Load conversation history for stateless request."""
    with Session(engine) as session:
        # Verify conversation ownership
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Load messages in chronological order
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()

        return messages
```

**Alternatives Considered**:
- Redis for conversation cache: Faster but less durable, adds complexity
- MongoDB for flexible schema: Adds another database, PostgreSQL JSON sufficient
- In-memory storage: Violates stateless requirement

**Trade-offs**:
- ✅ Durable, consistent, leverages existing infrastructure
- ❌ Slightly higher latency than in-memory, database load on each request

---

## 4. Stateless Request Cycle Design

### Decision: Load Full History from Database on Each Request

**Rationale**:
- Enables horizontal scaling without session affinity
- Survives server restarts without data loss
- Simplifies deployment and operations
- Aligns with constitution principle III

**Request Cycle Implementation**:

```python
@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Stateless chat endpoint.

    Request: {message, conversation_id?}
    Response: {response, tool_calls, conversation_id}
    """

    # Step 1: Load or create conversation
    if request.conversation_id:
        conversation_id = request.conversation_id
        history = load_conversation_history(conversation_id, current_user.id)
    else:
        conversation_id = create_conversation(current_user.id)
        history = []

    # Step 2: Process message with agent
    response, tool_calls = process_message(
        conversation_history=history,
        new_message=request.message,
        user_id=current_user.id
    )

    # Step 3: Save messages to database
    save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )
    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response,
        tool_calls=tool_calls
    )

    # Step 4: Return response
    return ChatResponse(
        response=response,
        tool_calls=tool_calls,
        conversation_id=conversation_id
    )
```

**Performance Optimization**:
- Limit history to last 100 messages (configurable)
- Use database connection pooling (already configured in Neon)
- Index on conversation_id and created_at for fast queries
- Consider caching for very active conversations (future optimization)

**Alternatives Considered**:
- In-memory session storage: Violates stateless requirement, doesn't survive restarts
- Redis session cache: Adds complexity, still needs database backup
- WebSocket streaming: Not required for hackathon scope

**Trade-offs**:
- ✅ Reliable, scalable, simple deployment
- ❌ Database query on every request, slightly higher latency

---

## 5. JWT Authentication with Agent Context

### Decision: Extract user_id from JWT and Inject into All MCP Tools

**Rationale**:
- Leverages existing JWT authentication infrastructure
- Enforces user isolation at tool level
- Prevents cross-user data access
- Aligns with constitution principle V

**Authentication Flow**:

```python
# JWT Middleware (existing)
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    """Extract and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: UUID = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)

        # Load user from database
        user = get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401)

        return user

    except JWTError:
        raise HTTPException(status_code=401)

# Tool Execution with User Context
def execute_mcp_tools(tool_calls, user_id: UUID):
    """
    Execute MCP tools with authenticated user context.
    User ID is automatically injected into all tool calls.
    """
    tool_outputs = []

    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # CRITICAL: Inject user_id for authorization
        tool_args["user_id"] = user_id

        # Execute tool
        result = MCP_TOOLS[tool_name](**tool_args)

        # Log tool execution for observability
        logger.info(f"Tool executed: {tool_name} by user {user_id}")

        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": json.dumps(result)
        })

    return tool_outputs
```

**Security Best Practices**:
- Never trust tool arguments for user_id (always use JWT)
- Validate ownership in every tool before operations
- Return generic errors to avoid information leakage
- Log all tool executions for audit trail

**Alternatives Considered**:
- Session-based auth: Violates stateless requirement
- API keys: Less secure, harder to manage
- OAuth2 with refresh tokens: Overkill for hackathon scope

**Trade-offs**:
- ✅ Secure, leverages existing infrastructure, stateless
- ❌ Token must be included in every request

---

## Summary of Key Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| Google Gemini API | Proven accuracy, fast development, cost-effective | External API dependency |
| MCP Tool Architecture | Observability, clear contracts | Additional abstraction |
| PostgreSQL Storage | Durable, consistent, existing infra | Database load per request |
| Stateless Design | Scalable, reliable, simple deployment | Slightly higher latency |
| JWT Authentication | Secure, existing infrastructure | Token in every request |

## References

- Google Gemini API: https://ai.google.dev/docs
- Gemini Function Calling: https://ai.google.dev/docs/function_calling
- Model Context Protocol: https://modelcontextprotocol.io/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Neon PostgreSQL: https://neon.tech/docs/introduction

## Next Steps

1. Implement database models (Conversation, Message)
2. Create MCP tool implementations
3. Configure Google Gemini API
4. Build stateless chat endpoint
5. Integrate ChatKit frontend
6. Test end-to-end conversational flows
