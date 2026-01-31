"""
MCP Tool Definitions for Task Management

These tools define the interface between the LLM and task operations.
Each tool has a schema that the LLM uses to understand what it can do.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class CreateTaskInput(BaseModel):
    """Input schema for creating a task"""
    title: str = Field(..., description="The title/description of the task to create")
    description: str | None = Field(None, description="Optional detailed description of the task")
    due_date_text: str | None = Field(None, description="Natural language due date (e.g., 'tomorrow', 'next Friday', 'in 3 days')")
    priority: str | None = Field(None, description="Priority level: low, medium, high, urgent")
    category: str | None = Field(None, description="Category: work, personal, shopping, health, finance, home, education")


class SuggestSubtasksInput(BaseModel):
    """Input schema for suggesting subtasks"""
    task_title: str = Field(..., description="The main task title to break down into subtasks")
    task_description: str | None = Field(None, description="Optional task description for context")


class ShowInsightsInput(BaseModel):
    """Input schema for showing productivity insights"""
    pass  # No parameters needed


class ListTasksInput(BaseModel):
    """Input schema for listing tasks"""
    pass  # No parameters needed


class CompleteTaskInput(BaseModel):
    """Input schema for completing/toggling a task"""
    task_identifier: str = Field(
        ...,
        description="Either the task number (e.g., '1', '2') or the task title/partial title to search for"
    )


class DeleteTaskInput(BaseModel):
    """Input schema for deleting a task"""
    task_identifier: str = Field(
        ...,
        description="Either the task number (e.g., '1', '2') or the task title/partial title to search for"
    )


# MCP Tool Definitions
# These are the tools that the LLM can call
TASK_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user with AI-enhanced features. Automatically extracts due dates from natural language, suggests priority, and categorizes tasks. Use this when the user wants to add, create, or make a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or description of the task to create"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    },
                    "due_date_text": {
                        "type": "string",
                        "description": "Natural language due date (e.g., 'tomorrow', 'next Friday', 'in 3 days', 'by Monday'). The AI will parse this automatically."
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level: low, medium, high, urgent. If not provided, AI will suggest based on keywords."
                    },
                    "category": {
                        "type": "string",
                        "description": "Category: work, personal, shopping, health, finance, home, education. If not provided, AI will auto-categorize."
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user. Use this when the user wants to see, view, list, or show their tasks.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a single task as complete or toggle its completion status. Use this when the user wants to complete, finish, mark as done, or toggle ONE specific task. The task_identifier can be a task number (1, 2, 3) or a task title/partial title. DO NOT use this for completing multiple tasks or all tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Either the task number (e.g., '1', '2') or the task title/partial title to search for"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_all_tasks",
            "description": "Mark ALL tasks as complete. Use this ONLY when the user explicitly wants to complete all tasks, mark all as done, or finish everything. This will mark every single task as completed.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a single task permanently. Use this when the user wants to delete, remove, or get rid of ONE specific task. The task_identifier can be a task number (1, 2, 3) or a task title/partial title. DO NOT use this for deleting multiple tasks or all tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "Either the task number (e.g., '1', '2') or the task title/partial title to search for"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_all_tasks",
            "description": "Delete ALL tasks permanently. Use this ONLY when the user explicitly wants to delete all tasks, clear all tasks, or remove everything. This will delete every single task the user has.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_subtasks",
            "description": "Suggest subtasks for a complex task. Use this when the user wants to break down a large task into smaller steps, or when they ask 'how should I approach this' or 'what are the steps'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {
                        "type": "string",
                        "description": "The main task title to break down into subtasks"
                    },
                    "task_description": {
                        "type": "string",
                        "description": "Optional task description for additional context"
                    }
                },
                "required": ["task_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "show_insights",
            "description": "Show productivity insights and statistics. Use this when the user asks for stats, insights, progress, how they're doing, completion rate, or wants to see their productivity metrics.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
