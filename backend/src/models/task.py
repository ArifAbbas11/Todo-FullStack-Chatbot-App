"""
Task model for todo items.
Represents a single todo task belonging to a user.
"""
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List


class Task(SQLModel, table=True):
    """
    Task entity for todo items.

    Security Considerations:
    - user_id foreign key ensures referential integrity
    - CASCADE delete ensures tasks are deleted when user is deleted
    - UUID primary key prevents enumeration attacks
    - All queries must filter by user_id for user isolation
    """
    __tablename__ = "tasks"

    # Primary key - UUID for security (prevents enumeration)
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to users table
    # Security: CASCADE delete ensures orphaned tasks are removed
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of the task (foreign key to users.id)"
    )

    # Task content
    title: str = Field(
        max_length=500,
        description="Task title (required, max 500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional task description (max 5000 characters)"
    )

    # Task status
    is_completed: bool = Field(
        default=False,
        description="Completion status (default: false)"
    )

    # AI Enhancement Fields (all nullable for backward compatibility)
    due_date: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Task deadline (nullable)"
    )
    priority: Optional[str] = Field(
        default=None,
        max_length=20,
        index=True,
        description="Priority: low, medium, high, urgent (nullable)"
    )
    category: Optional[str] = Field(
        default=None,
        max_length=50,
        index=True,
        description="Main category: work, personal, shopping, health, etc. (nullable)"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Array of tags (nullable JSON)"
    )
    parent_task_id: Optional[UUID] = Field(
        default=None,
        foreign_key="tasks.id",
        index=True,
        description="Parent task ID for subtasks (nullable, self-referential)"
    )

    # Audit timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )

    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "is_completed": False,
                "created_at": "2026-01-14T10:30:00Z",
                "updated_at": "2026-01-14T10:30:00Z"
            }
        }
