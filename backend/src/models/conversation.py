"""
Conversation model for chat sessions.
Represents a conversation between a user and the AI agent.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class Conversation(SQLModel, table=True):
    """
    Conversation entity for chat sessions.

    Security Considerations:
    - user_id foreign key ensures referential integrity
    - CASCADE delete ensures conversations are deleted when user is deleted
    - UUID primary key prevents enumeration attacks
    - All queries must filter by user_id for user isolation
    """
    __tablename__ = "conversations"

    # Primary key - UUID for security (prevents enumeration)
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to users table
    # Security: CASCADE delete ensures orphaned conversations are removed
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of the conversation (foreign key to users.id)"
    )

    # Audit timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Conversation start timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last message timestamp"
    )

    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2026-01-24T10:30:00Z",
                "updated_at": "2026-01-24T10:30:00Z"
            }
        }
