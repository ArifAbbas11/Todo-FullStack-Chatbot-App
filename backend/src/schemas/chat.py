"""
Chat request and response schemas for conversational todo management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Attributes:
        message: User's message text
        conversation_id: Optional conversation ID to continue existing conversation
    """
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID to continue")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": None
            }
        }


class ToolCall(BaseModel):
    """
    Tool call information for observability.

    Attributes:
        tool_name: Name of the MCP tool called
        arguments: Arguments passed to the tool
        result: Result returned by the tool
    """
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Attributes:
        response: Agent's response text
        conversation_id: Conversation ID for this exchange
        tool_calls: List of tool calls made during processing
    """
    response: str = Field(..., description="Agent's response text")
    conversation_id: UUID = Field(..., description="Conversation ID")
    tool_calls: Optional[List[ToolCall]] = Field(default=None, description="Tool calls made")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "I've added 'buy groceries' to your tasks",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "tool_calls": [
                    {
                        "tool_name": "create_task",
                        "arguments": {"title": "buy groceries"},
                        "result": {"success": True, "task_id": "123e4567-e89b-12d3-a456-426614174000"}
                    }
                ]
            }
        }
