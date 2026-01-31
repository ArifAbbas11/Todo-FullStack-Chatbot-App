"""
Agents Module - AI Agent Configuration and Management.

This module provides the Groq AI agent infrastructure for conversational
todo management.

Usage:
    from src.agents.groq_agent import process_message

    # Process a user message
    response, tool_calls = process_message(
        conversation_history=messages,
        new_message="Add a task to buy groceries",
        user_id=user_id,
        session=db_session
    )
"""

# Groq agent is imported directly where needed (src.agents.groq_agent)

__all__ = []
