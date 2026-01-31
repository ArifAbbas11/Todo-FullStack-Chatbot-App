"""
Task service layer.
Handles task CRUD operations with user isolation and validation.
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import List
from uuid import UUID
from datetime import datetime

from src.models.task import Task
from src.schemas.task import CreateTaskRequest, UpdateTaskRequest


# ============================================================================
# Task Service Functions
# ============================================================================

def create_task(session: Session, user_id: UUID, request: CreateTaskRequest) -> Task:
    """
    Create a new task for the authenticated user.

    Security Measures:
    - user_id is set from JWT token (not from request body)
    - Title is validated to not be empty or whitespace-only
    - Description is optional and trimmed

    Args:
        session: Database session
        user_id: Authenticated user's ID from JWT token
        request: Create task request with title and optional description

    Returns:
        Task: Created task

    Raises:
        HTTPException 400: If validation fails
        HTTPException 500: If database error occurs
    """
    # Validation is already done by Pydantic, but we double-check
    # Security: Ensure title is not empty after trimming
    if not request.title or request.title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TITLE",
                "message": "Task title is required",
                "details": {}
            }
        )

    # Create new task
    # Security: user_id is set from JWT token, not from request
    new_task = Task(
        user_id=user_id,
        title=request.title.strip(),
        description=request.description.strip() if request.description else None,
        is_completed=False,  # Default to incomplete
        due_date=request.due_date,
        priority=request.priority,
        category=request.category,
        tags=request.tags,
        parent_task_id=request.parent_task_id
    )

    try:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to create task",
                "details": {}
            }
        )


def get_user_tasks(session: Session, user_id: UUID) -> List[Task]:
    """
    Retrieve all tasks for the authenticated user.

    Security Measures:
    - Filters by user_id to ensure user isolation
    - Only returns tasks belonging to the authenticated user

    Args:
        session: Database session
        user_id: Authenticated user's ID from JWT token

    Returns:
        List[Task]: List of tasks ordered by created_at DESC (newest first)

    Raises:
        HTTPException 500: If database error occurs
    """
    try:
        # Security: Filter by user_id to ensure user isolation
        # Performance: Order by created_at DESC (newest first)
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        tasks = session.exec(statement).all()
        return list(tasks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to retrieve tasks",
                "details": {}
            }
        )


def get_task_by_id(session: Session, task_id: UUID, user_id: UUID) -> Task:
    """
    Retrieve a single task by ID with ownership verification.

    Security Measures:
    - Verifies task belongs to authenticated user
    - Returns 404 if task not found or not owned by user

    Args:
        session: Database session
        task_id: Task ID to retrieve
        user_id: Authenticated user's ID from JWT token

    Returns:
        Task: Retrieved task

    Raises:
        HTTPException 404: If task not found or not owned by user
        HTTPException 500: If database error occurs
    """
    try:
        # Security: Filter by both task_id AND user_id for ownership verification
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "TASK_NOT_FOUND",
                    "message": "Task not found",
                    "details": {}
                }
            )

        return task
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to retrieve task",
                "details": {}
            }
        )


def update_task(
    session: Session,
    task_id: UUID,
    user_id: UUID,
    request: UpdateTaskRequest
) -> Task:
    """
    Update a task's title and/or description with ownership verification.

    Security Measures:
    - Verifies task belongs to authenticated user before updating
    - Title is validated to not be empty or whitespace-only
    - Updates updated_at timestamp automatically

    Args:
        session: Database session
        task_id: Task ID to update
        user_id: Authenticated user's ID from JWT token
        request: Update task request with title and optional description

    Returns:
        Task: Updated task

    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If task not found or not owned by user
        HTTPException 500: If database error occurs
    """
    # Get task with ownership verification
    task = get_task_by_id(session, task_id, user_id)

    # Validation is already done by Pydantic, but we double-check
    if not request.title or request.title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TITLE",
                "message": "Task title is required",
                "details": {}
            }
        )

    try:
        # Update task fields
        task.title = request.title.strip()
        task.description = request.description.strip() if request.description else None
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to update task",
                "details": {}
            }
        )


def delete_task(session: Session, task_id: UUID, user_id: UUID) -> None:
    """
    Delete a task with ownership verification.

    Security Measures:
    - Verifies task belongs to authenticated user before deleting
    - Permanently deletes task from database

    Args:
        session: Database session
        task_id: Task ID to delete
        user_id: Authenticated user's ID from JWT token

    Returns:
        None

    Raises:
        HTTPException 404: If task not found or not owned by user
        HTTPException 500: If database error occurs
    """
    # Get task with ownership verification
    task = get_task_by_id(session, task_id, user_id)

    try:
        session.delete(task)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to delete task",
                "details": {}
            }
        )


def toggle_task_completion(session: Session, task_id: UUID, user_id: UUID) -> Task:
    """
    Toggle task completion status with ownership verification.

    Security Measures:
    - Verifies task belongs to authenticated user before toggling
    - Updates updated_at timestamp automatically

    Args:
        session: Database session
        task_id: Task ID to toggle
        user_id: Authenticated user's ID from JWT token

    Returns:
        Task: Updated task with toggled completion status

    Raises:
        HTTPException 404: If task not found or not owned by user
        HTTPException 500: If database error occurs
    """
    # Get task with ownership verification
    task = get_task_by_id(session, task_id, user_id)

    try:
        # Toggle completion status
        task.is_completed = not task.is_completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to toggle task completion",
                "details": {}
            }
        )
