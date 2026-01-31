"""
Chat API endpoint for conversational todo management.
Handles natural language interactions with the AI agent.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Annotated
import logging

from src.core.database import get_session
from src.api.deps import CurrentUser
from src.schemas.chat import ChatRequest, ChatResponse, ToolCall
from src.services.conversation import (
    create_conversation,
    get_conversation_by_id,
    load_conversation_history,
    save_message
)
from src.agents.groq_agent import process_message

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Router Configuration
# ============================================================================

router = APIRouter(
    prefix="/api",
    tags=["Chat"],
    responses={
        500: {
            "description": "Internal server error"
        }
    }
)


# ============================================================================
# Chat Endpoint
# ============================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to AI todo assistant",
    description="Process natural language messages for task management. Creates or continues conversations.",
    responses={
        200: {
            "description": "Message processed successfully",
            "model": ChatResponse
        },
        400: {
            "description": "Invalid request data"
        },
        401: {
            "description": "Unauthorized - invalid or missing JWT token"
        },
        404: {
            "description": "Conversation not found or not owned by user"
        }
    }
)
def chat(
    request: ChatRequest,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)]
) -> ChatResponse:
    """
    Process a user message with the AI todo assistant.

    This endpoint implements the full conversational AI flow:
    1. Create new conversation or load existing one
    2. Verify conversation ownership
    3. Load conversation history
    4. Save user message
    5. Process message with Groq agent (with MCP tool execution)
    6. Save assistant response with tool calls
    7. Return response to user

    Security Measures:
    - JWT authentication required (current_user from token)
    - Conversation ownership verified before access
    - user_id injected into all tool calls from JWT token
    - All database operations enforce user isolation

    Args:
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ChatResponse: Agent response with conversation_id and tool_calls

    Raises:
        HTTPException 400: If validation fails
        HTTPException 401: If JWT token is invalid
        HTTPException 404: If conversation not found or not owned by user
        HTTPException 500: If processing fails
    """
    try:
        # ====================================================================
        # Step 1: Handle Conversation Creation/Loading
        # ====================================================================

        if request.conversation_id is None:
            # Create new conversation for this user
            logger.info(f"Creating new conversation for user {current_user.id}")
            conversation = create_conversation(session, current_user.id)
            conversation_id = conversation.id
            conversation_history = []
        else:
            # Load existing conversation with ownership verification
            logger.info(f"Loading conversation {request.conversation_id} for user {current_user.id}")
            conversation = get_conversation_by_id(
                session,
                request.conversation_id,
                current_user.id
            )
            conversation_id = conversation.id

            # Load conversation history for context
            conversation_history = load_conversation_history(
                session,
                conversation_id,
                current_user.id,
                limit=100  # Last 100 messages for context
            )

        # ====================================================================
        # Step 2: Save User Message
        # ====================================================================

        logger.info(f"Saving user message to conversation {conversation_id}")
        user_message = save_message(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.id,
            role="user",
            content=request.message
        )

        # ====================================================================
        # Step 3: Process Message with Groq Agent
        # ====================================================================

        logger.info(f"Processing message with AI agent for user {current_user.id}")

        # Call AI agent with conversation history and new message
        # Security: user_id from JWT token is injected into all tool calls
        response_text, tool_calls_made = process_message(
            conversation_history=conversation_history,
            new_message=request.message,
            user_id=current_user.id,
            session=session  # Pass database session for task management
        )

        # ====================================================================
        # Step 4: Save Assistant Response
        # ====================================================================

        logger.info(f"Saving assistant response to conversation {conversation_id}")

        # Convert tool_calls_made to JSON-serializable format
        tool_calls_json = tool_calls_made if tool_calls_made else None

        assistant_message = save_message(
            session=session,
            conversation_id=conversation_id,
            user_id=current_user.id,
            role="assistant",
            content=response_text,
            tool_calls=tool_calls_json
        )

        # ====================================================================
        # Step 5: Format Response
        # ====================================================================

        # Convert tool calls to response schema
        tool_calls_response = None
        if tool_calls_made:
            tool_calls_response = [
                ToolCall(
                    tool_name=tc["tool"],
                    arguments=tc["args"] if tc["args"] is not None else {},
                    result=tc["result"]
                )
                for tc in tool_calls_made
            ]

        logger.info(f"Chat request processed successfully for user {current_user.id}")

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            tool_calls=tool_calls_response
        )

    except HTTPException as e:
        # Re-raise HTTP exceptions from service layer
        logger.warning(f"HTTP error in chat endpoint: {e.detail}")
        raise e

    except Exception as e:
        # Catch unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to process message. Please try again.",
                "details": {}
            }
        )
