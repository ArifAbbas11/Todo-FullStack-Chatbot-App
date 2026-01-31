# Data Model: AI-Powered Conversational Todo Management

**Feature**: 004-ai-todo-chatbot
**Date**: 2026-01-23
**Purpose**: Define database schema for conversation persistence and task management

## Overview

This data model extends the existing User and Task schema with Conversation and Message entities to support stateless conversational AI. All entities use UUID primary keys for security and are designed for efficient querying with proper indexes.

## Entity Relationship Diagram

```
User (existing)
  ├── id: UUID (PK)
  ├── email: string (unique)
  ├── hashed_password: string
  ├── created_at: datetime
  └── updated_at: datetime
      │
      ├─── has many ───> Task (existing)
      │                   ├── id: UUID (PK)
      │                   ├── user_id: UUID (FK → users.id)
      │                   ├── title: string
      │                   ├── description: string?
      │                   ├── is_completed: boolean
      │                   ├── created_at: datetime
      │                   └── updated_at: datetime
      │
      └─── has many ───> Conversation (NEW)
                          ├── id: UUID (PK)
                          ├── user_id: UUID (FK → users.id)
                          ├── created_at: datetime
                          └── updated_at: datetime
                              │
                              └─── has many ───> Message (NEW)
                                                  ├── id: UUID (PK)
                                                  ├── conversation_id: UUID (FK → conversations.id)
                                                  ├── role: string ('user' | 'assistant')
                                                  ├── content: text
                                                  ├── tool_calls: JSON?
                                                  └── created_at: datetime
```

## Entities

### 1. User (Existing - No Changes)

**Purpose**: Represents authenticated users in the system

**Fields**:
- `id` (UUID, PK): Unique user identifier
- `email` (string, unique, indexed): User's email address for login
- `hashed_password` (string): Bcrypt-hashed password
- `created_at` (datetime): Account creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relationships**:
- One-to-many with Task
- One-to-many with Conversation (NEW)

**Indexes**:
- Primary key on `id`
- Unique index on `email`

---

### 2. Task (Existing - No Changes)

**Purpose**: Represents todo items belonging to users

**Fields**:
- `id` (UUID, PK): Unique task identifier
- `user_id` (UUID, FK, indexed): Owner of the task
- `title` (string, max 500): Task title
- `description` (string?, max 5000): Optional task description
- `is_completed` (boolean, default false): Completion status
- `created_at` (datetime): Task creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relationships**:
- Many-to-one with User

**Indexes**:
- Primary key on `id`
- Foreign key index on `user_id`

**Validation Rules**:
- `title` is required and max 500 characters
- `description` is optional and max 5000 characters
- `user_id` must reference existing user

**State Transitions**:
- Created → Active (is_completed = false)
- Active → Completed (is_completed = true)
- Completed → Active (can be unmarked)
- Any state → Deleted (soft or hard delete)

---

### 3. Conversation (NEW)

**Purpose**: Represents a chat session between a user and the AI agent

**Fields**:
- `id` (UUID, PK): Unique conversation identifier
- `user_id` (UUID, FK, indexed): Owner of the conversation
- `created_at` (datetime, indexed): Conversation start timestamp
- `updated_at` (datetime): Last message timestamp

**Relationships**:
- Many-to-one with User
- One-to-many with Message

**Indexes**:
- Primary key on `id`
- Foreign key index on `user_id`
- Index on `created_at` for sorting recent conversations

**Validation Rules**:
- `user_id` must reference existing user
- Cannot be deleted if messages exist (cascade delete)

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    """
    Conversation entity for chat sessions.

    Security: user_id foreign key ensures referential integrity
    and enables efficient user isolation queries.
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of the conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Conversation start timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last message timestamp"
    )
```

---

### 4. Message (NEW)

**Purpose**: Represents individual messages within a conversation

**Fields**:
- `id` (UUID, PK): Unique message identifier
- `conversation_id` (UUID, FK, indexed): Parent conversation
- `role` (string, enum): Message role ('user' or 'assistant')
- `content` (text): Message text content
- `tool_calls` (JSON?, nullable): Tool calls made by assistant (optional)
- `created_at` (datetime, indexed): Message timestamp

**Relationships**:
- Many-to-one with Conversation

**Indexes**:
- Primary key on `id`
- Foreign key index on `conversation_id`
- Index on `created_at` for chronological ordering

**Validation Rules**:
- `conversation_id` must reference existing conversation
- `role` must be 'user' or 'assistant'
- `content` is required
- `tool_calls` is optional JSON field (only for assistant messages)

**Tool Calls JSON Schema**:

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "tool_name": {"type": "string"},
      "arguments": {"type": "object"},
      "result": {"type": "object"}
    }
  }
}
```

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Message(SQLModel, table=True):
    """
    Message entity for conversation history.

    Stores both user messages and assistant responses.
    Tool calls are stored as JSON for observability.
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation"
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
        index=True,
        description="Message timestamp"
    )
```

---

## Database Migration

### Alembic Migration Script

```python
"""Add conversations and messages tables

Revision ID: add_conversations
Revises: previous_migration
Create Date: 2026-01-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('conversation_id', UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Query Patterns

### Load Conversation History

```python
def load_conversation_history(conversation_id: UUID, user_id: UUID):
    """Load all messages for a conversation in chronological order."""
    with Session(engine) as session:
        # Verify ownership
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404)

        # Load messages
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()

        return messages
```

### Create New Conversation

```python
def create_conversation(user_id: UUID) -> UUID:
    """Create a new conversation for a user."""
    with Session(engine) as session:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation.id
```

### Save Message

```python
def save_message(
    conversation_id: UUID,
    role: str,
    content: str,
    tool_calls: dict = None
):
    """Save a message to the conversation."""
    with Session(engine) as session:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        session.add(message)

        # Update conversation timestamp
        conversation = session.get(Conversation, conversation_id)
        conversation.updated_at = datetime.utcnow()

        session.commit()
```

### List User Conversations

```python
def list_user_conversations(user_id: UUID, limit: int = 20):
    """List recent conversations for a user."""
    with Session(engine) as session:
        conversations = session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        ).all()

        return conversations
```

---

## Performance Considerations

### Indexes

All critical query paths are indexed:
- `conversations.user_id` - Fast user conversation lookup
- `conversations.created_at` - Sorting recent conversations
- `messages.conversation_id` - Fast message loading
- `messages.created_at` - Chronological ordering

### Query Optimization

- Limit conversation history to last 100 messages (configurable)
- Use database connection pooling (Neon provides this)
- Consider pagination for very long conversations
- Cache frequently accessed conversations (future optimization)

### Storage Estimates

- Average message: ~500 bytes (content + metadata)
- 100 messages per conversation: ~50 KB
- 1000 users with 10 conversations each: ~500 MB
- Well within PostgreSQL capacity

---

## Security Considerations

### User Isolation

- All queries filter by `user_id` from JWT token
- Foreign key constraints enforce referential integrity
- Cascade deletes ensure orphaned records are removed

### Data Privacy

- Conversations and messages are private to each user
- No cross-user data access possible through queries
- Tool calls logged for observability but not exposed to other users

### Audit Trail

- All messages timestamped for audit purposes
- Tool calls stored in JSON for debugging and compliance
- Conversation history provides complete interaction log

---

## Future Enhancements

### Potential Additions (Not in Current Scope)

- **Conversation Titles**: Auto-generate from first message
- **Message Reactions**: User feedback on assistant responses
- **Conversation Sharing**: Share conversations between users
- **Message Editing**: Allow users to edit their messages
- **Conversation Archiving**: Soft delete old conversations
- **Full-Text Search**: Search across conversation history

---

## Summary

This data model extends the existing User/Task schema with Conversation and Message entities to support stateless conversational AI. The design prioritizes:

- **Durability**: All state persists in PostgreSQL
- **Performance**: Proper indexes for efficient queries
- **Security**: User isolation enforced at database level
- **Observability**: Tool calls logged for debugging
- **Scalability**: Stateless design enables horizontal scaling

The schema is production-ready and aligns with all constitution principles.
