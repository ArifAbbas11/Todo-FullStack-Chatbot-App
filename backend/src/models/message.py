"""
Message model for conversation history.
Represents individual messages within a conversation.
"""
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Message(SQLModel, table=True):
    """
    Message entity for conversation history.

    Stores both user messages and assistant responses.
    Tool calls are stored as JSON for observability and debugging.

    Security Considerations:
    - conversation_id foreign key ensures referential integrity
    - CASCADE delete ensures messages are deleted when conversation is deleted
    - UUID primary key prevents enumeration attacks
    - Role validation ensures only 'user' or 'assistant' values
    """
    __tablename__ = "messages"

    # Primary key - UUID for security (prevents enumeration)
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to conversations table
    # Security: CASCADE delete ensures orphaned messages are removed
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation (foreign key to conversations.id)"
    )

    # Message metadata
    role: str = Field(
        description="Message role: 'user' or 'assistant'"
    )

    # Message content
    content: str = Field(
        description="Message text content"
    )

    # Tool calls (JSON field for assistant messages)
    # Stores array of tool call objects: [{tool_name, arguments, result}, ...]
    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Tool calls made by assistant (JSON, nullable)"
    )

    # Audit timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Message timestamp"
    )

    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "user",
                "content": "Add a task to buy groceries",
                "tool_calls": None,
                "created_at": "2026-01-24T10:30:00Z"
            }
        }
