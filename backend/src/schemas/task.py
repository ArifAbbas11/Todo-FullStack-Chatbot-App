"""
Task request and response schemas.
Defines Pydantic models for task API input validation and output serialization.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List


# ============================================================================
# Request Schemas (Input Validation)
# ============================================================================

class CreateTaskRequest(BaseModel):
    """
    Create task request schema.

    Validations:
    - Title is required and cannot be empty or whitespace-only
    - Title maximum length: 500 characters
    - Description is optional
    - Description maximum length: 5000 characters
    - AI enhancement fields are all optional
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task title (required, max 500 characters)",
        examples=["Buy groceries"]
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Optional task description (max 5000 characters)",
        examples=["Milk, eggs, bread"]
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Task deadline (optional)",
        examples=["2026-02-01T17:00:00Z"]
    )
    priority: Optional[str] = Field(
        None,
        description="Priority: low, medium, high, urgent (optional)",
        examples=["high"]
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Category: work, personal, shopping, health, etc. (optional)",
        examples=["shopping"]
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Array of tags (optional)",
        examples=[["groceries", "weekly"]]
    )
    parent_task_id: Optional[UUID] = Field(
        None,
        description="Parent task ID for subtasks (optional)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    @field_validator('title')
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """
        Validate title is not just whitespace.

        Security: Prevents users from creating tasks with whitespace-only titles.
        """
        if not v or v.strip() == "":
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Trim description if provided.
        """
        if v is not None:
            v = v.strip()
            # Return None if description is empty after stripping
            return v if v else None
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }


class UpdateTaskRequest(BaseModel):
    """
    Update task request schema.

    Validations:
    - Title is required and cannot be empty or whitespace-only
    - Title maximum length: 500 characters
    - Description is optional
    - Description maximum length: 5000 characters
    - AI enhancement fields are all optional
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Updated task title (required, max 500 characters)",
        examples=["Buy groceries and supplies"]
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Updated task description (max 5000 characters)",
        examples=["Milk, eggs, bread, paper towels"]
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Task deadline (optional)",
        examples=["2026-02-01T17:00:00Z"]
    )
    priority: Optional[str] = Field(
        None,
        description="Priority: low, medium, high, urgent (optional)",
        examples=["high"]
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Category: work, personal, shopping, health, etc. (optional)",
        examples=["shopping"]
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Array of tags (optional)",
        examples=[["groceries", "weekly"]]
    )

    @field_validator('title')
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """
        Validate title is not just whitespace.
        """
        if not v or v.strip() == "":
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Trim description if provided.
        """
        if v is not None:
            v = v.strip()
            # Return None if description is empty after stripping
            return v if v else None
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and supplies",
                "description": "Milk, eggs, bread, paper towels"
            }
        }


# ============================================================================
# Response Schemas (Output Serialization)
# ============================================================================

class TaskData(BaseModel):
    """
    Task data schema for API responses.

    Security: Includes all task fields for the authenticated user.
    """
    id: UUID = Field(
        ...,
        description="Task unique identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    user_id: UUID = Field(
        ...,
        description="Owner's user ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    title: str = Field(
        ...,
        description="Task title",
        examples=["Buy groceries"]
    )
    description: Optional[str] = Field(
        None,
        description="Task description",
        examples=["Milk, eggs, bread"]
    )
    is_completed: bool = Field(
        ...,
        description="Completion status",
        examples=[False]
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Task deadline",
        examples=["2026-02-01T17:00:00Z"]
    )
    priority: Optional[str] = Field(
        None,
        description="Priority level",
        examples=["high"]
    )
    category: Optional[str] = Field(
        None,
        description="Task category",
        examples=["shopping"]
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Task tags",
        examples=[["groceries", "weekly"]]
    )
    parent_task_id: Optional[UUID] = Field(
        None,
        description="Parent task ID for subtasks",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp",
        examples=["2026-01-14T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp",
        examples=["2026-01-14T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
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


class TaskResponse(BaseModel):
    """
    Single task response schema.

    Returns task data on successful operations (create, get, update, toggle).
    """
    data: dict = Field(
        ...,
        description="Response data containing task"
    )
    message: str = Field(
        ...,
        description="Success message",
        examples=["Task created successfully", "Task updated successfully"]
    )
    error: Optional[dict] = Field(
        None,
        description="Error object (null on success)"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "data": {
                    "task": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "is_completed": False,
                        "created_at": "2026-01-14T10:30:00Z",
                        "updated_at": "2026-01-14T10:30:00Z"
                    }
                },
                "message": "Task created successfully",
                "error": None
            }
        }


class TaskListResponse(BaseModel):
    """
    Task list response schema.

    Returns array of tasks and count for list operations.
    """
    data: dict = Field(
        ...,
        description="Response data containing tasks array and count"
    )
    message: str = Field(
        ...,
        description="Success message",
        examples=["Tasks retrieved successfully", "No tasks found"]
    )
    error: Optional[dict] = Field(
        None,
        description="Error object (null on success)"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "data": {
                    "tasks": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Buy groceries",
                            "description": "Milk, eggs, bread",
                            "is_completed": False,
                            "created_at": "2026-01-14T10:30:00Z",
                            "updated_at": "2026-01-14T10:30:00Z"
                        }
                    ],
                    "count": 1
                },
                "message": "Tasks retrieved successfully",
                "error": None
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response schema.

    Used for all error responses (400, 401, 404, 500).
    """
    data: Optional[dict] = Field(
        None,
        description="Data object (null on error)"
    )
    message: Optional[str] = Field(
        None,
        description="Message (null on error)"
    )
    error: dict = Field(
        ...,
        description="Error details"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "data": None,
                "message": None,
                "error": {
                    "code": "TASK_NOT_FOUND",
                    "message": "Task not found",
                    "details": {}
                }
            }
        }
