"""
Conversation service layer.
Handles conversation and message CRUD operations with user isolation and validation.
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from src.models.conversation import Conversation
from src.models.message import Message


# ============================================================================
# Conversation Service Functions
# ============================================================================

def create_conversation(session: Session, user_id: UUID) -> Conversation:
    """
    Create a new conversation for the authenticated user.

    Security Measures:
    - user_id is set from JWT token (not from request body)
    - Conversation is automatically associated with the user

    Args:
        session: Database session
        user_id: Authenticated user's ID from JWT token

    Returns:
        Conversation: Created conversation

    Raises:
        HTTPException 500: If database error occurs
    """
    try:
        # Create new conversation
        # Security: user_id is set from JWT token
        new_conversation = Conversation(user_id=user_id)

        session.add(new_conversation)
        session.commit()
        session.refresh(new_conversation)
        return new_conversation
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to create conversation",
                "details": {}
            }
        )


def get_conversation_by_id(session: Session, conversation_id: UUID, user_id: UUID) -> Conversation:
    """
    Retrieve a single conversation by ID with ownership verification.

    Security Measures:
    - Verifies conversation belongs to authenticated user
    - Returns 404 if conversation not found or not owned by user

    Args:
        session: Database session
        conversation_id: Conversation ID to retrieve
        user_id: Authenticated user's ID from JWT token

    Returns:
        Conversation: Retrieved conversation

    Raises:
        HTTPException 404: If conversation not found or not owned by user
        HTTPException 500: If database error occurs
    """
    try:
        # Security: Filter by both conversation_id AND user_id for ownership verification
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CONVERSATION_NOT_FOUND",
                    "message": "Conversation not found",
                    "details": {}
                }
            )

        return conversation
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to retrieve conversation",
                "details": {}
            }
        )


def load_conversation_history(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    limit: int = 100
) -> List[Message]:
    """
    Load all messages for a conversation in chronological order.

    Security Measures:
    - Verifies conversation belongs to authenticated user
    - Only returns messages from user's conversations
    - Limits message count to prevent memory issues

    Args:
        session: Database session
        conversation_id: Conversation ID to load messages from
        user_id: Authenticated user's ID from JWT token
        limit: Maximum number of messages to load (default: 100)

    Returns:
        List[Message]: List of messages ordered by created_at ASC (oldest first)

    Raises:
        HTTPException 404: If conversation not found or not owned by user
        HTTPException 500: If database error occurs
    """
    # Verify ownership first
    conversation = get_conversation_by_id(session, conversation_id, user_id)

    try:
        # Load messages in chronological order (oldest first)
        # Performance: Limit to last N messages to prevent memory issues
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = session.exec(statement).all()
        return list(messages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to load conversation history",
                "details": {}
            }
        )


def save_message(
    session: Session,
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    tool_calls: Optional[Dict[str, Any]] = None
) -> Message:
    """
    Save a message to the conversation.

    Security Measures:
    - Verifies conversation belongs to authenticated user
    - Validates role is 'user' or 'assistant'
    - Updates conversation timestamp automatically

    Args:
        session: Database session
        conversation_id: Conversation ID to add message to
        user_id: Authenticated user's ID from JWT token
        role: Message role ('user' or 'assistant')
        content: Message text content
        tool_calls: Optional tool calls made by assistant (JSON)

    Returns:
        Message: Created message

    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If conversation not found or not owned by user
        HTTPException 500: If database error occurs
    """
    # Verify ownership first
    conversation = get_conversation_by_id(session, conversation_id, user_id)

    # Validate role
    if role not in ['user', 'assistant']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ROLE",
                "message": "Role must be 'user' or 'assistant'",
                "details": {}
            }
        )

    # Validate content is not empty
    if not content or content.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CONTENT",
                "message": "Message content is required",
                "details": {}
            }
        )

    try:
        # Create new message
        new_message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content.strip(),
            tool_calls=tool_calls
        )

        session.add(new_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        session.commit()
        session.refresh(new_message)
        return new_message
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to save message",
                "details": {}
            }
        )


def list_user_conversations(
    session: Session,
    user_id: UUID,
    limit: int = 20
) -> List[Conversation]:
    """
    List recent conversations for the authenticated user.

    Security Measures:
    - Filters by user_id to ensure user isolation
    - Only returns conversations belonging to the authenticated user

    Args:
        session: Database session
        user_id: Authenticated user's ID from JWT token
        limit: Maximum number of conversations to return (default: 20)

    Returns:
        List[Conversation]: List of conversations ordered by updated_at DESC (most recent first)

    Raises:
        HTTPException 500: If database error occurs
    """
    try:
        # Security: Filter by user_id to ensure user isolation
        # Performance: Order by updated_at DESC (most recent first)
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        conversations = session.exec(statement).all()
        return list(conversations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to retrieve conversations",
                "details": {}
            }
        )


def delete_conversation(session: Session, conversation_id: UUID, user_id: UUID) -> None:
    """
    Delete a conversation with ownership verification.

    Security Measures:
    - Verifies conversation belongs to authenticated user before deleting
    - Cascade delete removes all associated messages automatically

    Args:
        session: Database session
        conversation_id: Conversation ID to delete
        user_id: Authenticated user's ID from JWT token

    Returns:
        None

    Raises:
        HTTPException 404: If conversation not found or not owned by user
        HTTPException 500: If database error occurs
    """
    # Get conversation with ownership verification
    conversation = get_conversation_by_id(session, conversation_id, user_id)

    try:
        session.delete(conversation)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to delete conversation",
                "details": {}
            }
        )
