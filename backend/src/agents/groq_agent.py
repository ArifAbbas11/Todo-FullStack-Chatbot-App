"""
Groq AI Agent with MCP Tools for Task Management

This agent uses Groq's fast LLM inference with function calling
to provide natural language task management capabilities.
"""

import os
import json
import logging
from typing import List, Dict, Any, Tuple
from groq import Groq
from sqlmodel import Session

from src.mcp_tools.task_tools import TASK_TOOLS
from src.services.task import create_task, get_user_tasks, toggle_task_completion, delete_task, update_task
from src.schemas.task import CreateTaskRequest, UpdateTaskRequest
from src.services.ai_enhancements import (
    parse_natural_language_date,
    extract_date_from_task_text,
    auto_categorize_task,
    suggest_priority,
    suggest_task_breakdown,
    calculate_productivity_insights
)

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_client = None

def get_groq_client():
    """Get or create Groq client"""
    global groq_client
    if groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your-groq-api-key-here":
            raise ValueError(
                "GROQ_API_KEY not set. Please get a free API key from https://console.groq.com/keys "
                "and add it to your .env file"
            )
        groq_client = Groq(api_key=api_key)
    return groq_client


def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    session: Session,
    user_id: str
) -> Dict[str, Any]:
    """
    Execute a tool call and return the result

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        session: Database session
        user_id: User ID for task operations

    Returns:
        Dictionary with success status and result/error message
    """
    try:
        if tool_name == "create_task":
            title = tool_args.get("title")
            description = tool_args.get("description")
            due_date_text = tool_args.get("due_date_text")
            priority = tool_args.get("priority")
            category = tool_args.get("category")

            # AI Enhancement: Parse natural language due date
            due_date = None
            if due_date_text:
                due_date = parse_natural_language_date(due_date_text)
                if not due_date:
                    # Try extracting from title/description
                    due_date = extract_date_from_task_text(title, description)
            else:
                # Try extracting from title/description even if not explicitly provided
                due_date = extract_date_from_task_text(title, description)

            # AI Enhancement: Auto-categorize if not provided
            if not category:
                category = auto_categorize_task(title, description)

            # AI Enhancement: Suggest priority if not provided
            if not priority:
                priority = suggest_priority(title, description)

            task_request = CreateTaskRequest(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                category=category
            )
            task = create_task(session, user_id, task_request)

            # Format response with AI-enhanced fields
            result = f"✅ Task created successfully!\n\n"
            result += f"Title: {task.title}\n"
            if task.description:
                result += f"Description: {task.description}\n"
            if task.due_date:
                result += f"📅 Due: {task.due_date.strftime('%B %d, %Y at %I:%M %p')}\n"
            if task.priority:
                priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
                result += f"{priority_emoji} Priority: {task.priority.capitalize()}\n"
            if task.category:
                result += f"🏷️ Category: {task.category.capitalize()}\n"
            result += f"Status: {'✅ Completed' if task.is_completed else '⭕ Not completed'}\n\n"
            result += "IMPORTANT: Do NOT list all tasks. Just show this confirmation message."

            return {
                "success": True,
                "result": result
            }

        elif tool_name == "list_tasks":
            tasks = get_user_tasks(session, user_id)

            if not tasks:
                return {
                    "success": True,
                    "result": "You don't have any tasks yet. Create one by saying 'Create a task to [description]'"
                }

            # Format task list - MUST show ALL tasks
            result = f"📋 Your Tasks ({len(tasks)} total):\n\n"
            for idx, task in enumerate(tasks, 1):
                status = "✅" if task.is_completed else "⭕"
                result += f"{idx}. {status} {task.title}\n"

            result += f"\n[SYSTEM: All {len(tasks)} tasks listed above. Show this exact list to the user without modification.]"

            return {
                "success": True,
                "result": result
            }

        elif tool_name == "complete_task":
            task_identifier = tool_args.get("task_identifier", "").strip()
            tasks = get_user_tasks(session, user_id)

            if not tasks:
                return {
                    "success": False,
                    "error": "You don't have any tasks to complete."
                }

            # Try to parse as task number
            try:
                task_number = int(task_identifier)
                if 1 <= task_number <= len(tasks):
                    task = tasks[task_number - 1]
                    updated_task = toggle_task_completion(session, task.id, user_id)
                    status = "completed" if updated_task.is_completed else "marked as incomplete"
                    return {
                        "success": True,
                        "result": f"✅ Task {status}!\n\n{updated_task.title}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Task number {task_number} doesn't exist. You have {len(tasks)} tasks."
                    }
            except ValueError:
                # Not a number, search by title
                search_term = task_identifier.lower()
                matching_tasks = [t for t in tasks if search_term in t.title.lower()]

                if len(matching_tasks) == 1:
                    task = matching_tasks[0]
                    updated_task = toggle_task_completion(session, task.id, user_id)
                    status = "completed" if updated_task.is_completed else "marked as incomplete"
                    return {
                        "success": True,
                        "result": f"✅ Task {status}!\n\n{updated_task.title}"
                    }
                elif len(matching_tasks) > 1:
                    result = f"I found {len(matching_tasks)} tasks matching '{task_identifier}':\n\n"
                    for task in matching_tasks:
                        status = "✅" if task.is_completed else "⭕"
                        task_idx = tasks.index(task) + 1
                        result += f"{task_idx}. {status} {task.title}\n"
                    result += f"\nPlease specify the task number. For example: 'Complete task {tasks.index(matching_tasks[0]) + 1}' or 'Delete task {tasks.index(matching_tasks[0]) + 1}'"
                    return {
                        "success": False,
                        "error": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"I couldn't find a task matching '{task_identifier}'."
                    }

        elif tool_name == "complete_all_tasks":
            tasks = get_user_tasks(session, user_id)

            if not tasks:
                return {
                    "success": False,
                    "error": "You don't have any tasks to complete."
                }

            # Complete all tasks
            completed_count = 0
            for task in tasks:
                if not task.is_completed:
                    toggle_task_completion(session, task.id, user_id)
                    completed_count += 1

            result = f"✅ All tasks completed successfully!\n\nMarked {completed_count} tasks as complete."
            result += "\n\nIMPORTANT: Do NOT list the tasks. Just confirm the action was successful."

            return {
                "success": True,
                "result": result
            }

        elif tool_name == "delete_task":
            task_identifier = tool_args.get("task_identifier", "").strip()
            tasks = get_user_tasks(session, user_id)

            if not tasks:
                return {
                    "success": False,
                    "error": "You don't have any tasks to delete."
                }

            # Try to parse as task number
            try:
                task_number = int(task_identifier)
                if 1 <= task_number <= len(tasks):
                    task = tasks[task_number - 1]
                    task_title = task.title
                    delete_task(session, task.id, user_id)
                    return {
                        "success": True,
                        "result": f"🗑️ Task deleted successfully!\n\n{task_title}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Task number {task_number} doesn't exist. You have {len(tasks)} tasks."
                    }
            except ValueError:
                # Not a number, search by title
                search_term = task_identifier.lower()
                matching_tasks = [t for t in tasks if search_term in t.title.lower()]

                if len(matching_tasks) == 1:
                    task = matching_tasks[0]
                    task_title = task.title
                    delete_task(session, task.id, user_id)
                    return {
                        "success": True,
                        "result": f"🗑️ Task deleted successfully!\n\n{task_title}"
                    }
                elif len(matching_tasks) > 1:
                    result = f"I found {len(matching_tasks)} tasks matching '{task_identifier}':\n\n"
                    for task in matching_tasks:
                        status = "✅" if task.is_completed else "⭕"
                        task_idx = tasks.index(task) + 1
                        result += f"{task_idx}. {status} {task.title}\n"
                    result += f"\nPlease specify the task number. For example: 'Complete task {tasks.index(matching_tasks[0]) + 1}' or 'Delete task {tasks.index(matching_tasks[0]) + 1}'"
                    return {
                        "success": False,
                        "error": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"I couldn't find a task matching '{task_identifier}'."
                    }

        elif tool_name == "update_task":
            task_identifier = tool_args.get("task_identifier", "").strip()
            new_title = tool_args.get("new_title")
            new_description = tool_args.get("new_description")

            # Validate that at least one field is being updated
            if not new_title and not new_description:
                return {
                    "success": False,
                    "error": "Please provide either a new title or new description to update."
                }

            tasks = get_user_tasks(session, user_id)

            if not tasks:
                return {
                    "success": False,
                    "error": "You don't have any tasks to update."
                }

            # Try to parse as task number
            try:
                task_number = int(task_identifier)
                if 1 <= task_number <= len(tasks):
                    task = tasks[task_number - 1]

                    # Prepare update request
                    update_request = UpdateTaskRequest(
                        title=new_title if new_title else task.title,
                        description=new_description if new_description else task.description
                    )

                    updated_task = update_task(session, task.id, user_id, update_request)

                    result = f"✏️ Task updated successfully!\n\n"
                    result += f"Title: {updated_task.title}\n"
                    if updated_task.description:
                        result += f"Description: {updated_task.description}\n"

                    return {
                        "success": True,
                        "result": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Task number {task_number} doesn't exist. You have {len(tasks)} tasks."
                    }
            except ValueError:
                # Not a number, search by title
                search_term = task_identifier.lower()
                matching_tasks = [t for t in tasks if search_term in t.title.lower()]

                if len(matching_tasks) == 1:
                    task = matching_tasks[0]

                    # Prepare update request
                    update_request = UpdateTaskRequest(
                        title=new_title if new_title else task.title,
                        description=new_description if new_description else task.description
                    )

                    updated_task = update_task(session, task.id, user_id, update_request)

                    result = f"✏️ Task updated successfully!\n\n"
                    result += f"Title: {updated_task.title}\n"
                    if updated_task.description:
                        result += f"Description: {updated_task.description}\n"

                    return {
                        "success": True,
                        "result": result
                    }
                elif len(matching_tasks) > 1:
                    result = f"I found {len(matching_tasks)} tasks matching '{task_identifier}':\n\n"
                    for task in matching_tasks:
                        status = "✅" if task.is_completed else "⭕"
                        task_idx = tasks.index(task) + 1
                        result += f"{task_idx}. {status} {task.title}\n"
                    result += f"\nPlease specify the task number. For example: 'Update task {tasks.index(matching_tasks[0]) + 1}'"
                    return {
                        "success": False,
                        "error": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"I couldn't find a task matching '{task_identifier}'."
                    }

        elif tool_name == "delete_all_tasks":
            tasks = get_user_tasks(session, user_id)

            if not tasks:
                return {
                    "success": False,
                    "error": "You don't have any tasks to delete."
                }

            # Delete all tasks
            task_count = len(tasks)
            for task in tasks:
                delete_task(session, task.id, user_id)

            return {
                "success": True,
                "result": f"🗑️ All tasks deleted successfully!\n\nDeleted {task_count} tasks."
            }

        elif tool_name == "suggest_subtasks":
            task_title = tool_args.get("task_title")
            task_description = tool_args.get("task_description")

            # AI Enhancement: Suggest subtasks for complex tasks
            subtasks = suggest_task_breakdown(task_title, task_description)

            if not subtasks:
                return {
                    "success": True,
                    "result": f"I don't have specific subtask suggestions for '{task_title}'. However, you could break it down by:\n\n1. Identifying the main steps needed\n2. Setting deadlines for each step\n3. Prioritizing the most important parts\n\nWould you like me to create the main task for you?"
                }

            result = f"💡 Here are suggested subtasks for '{task_title}':\n\n"
            for idx, subtask in enumerate(subtasks, 1):
                result += f"{idx}. {subtask}\n"
            result += f"\nWould you like me to create these as separate tasks?"

            return {
                "success": True,
                "result": result
            }

        elif tool_name == "show_insights":
            tasks = get_user_tasks(session, user_id)

            # AI Enhancement: Calculate productivity insights
            insights = calculate_productivity_insights(tasks)

            if insights['total_tasks'] == 0:
                return {
                    "success": True,
                    "result": "📊 You don't have any tasks yet. Create your first task to start tracking your productivity!"
                }

            result = f"📊 Your Productivity Insights:\n\n"
            result += f"📝 Total Tasks: {insights['total_tasks']}\n"
            result += f"✅ Completed: {insights['completed_tasks']}\n"
            result += f"⭕ Active: {insights['active_tasks']}\n"
            result += f"📈 Completion Rate: {insights['completion_rate']}%\n"

            if insights['overdue_tasks'] > 0:
                result += f"⚠️ Overdue: {insights['overdue_tasks']}\n"

            if insights['tasks_by_category']:
                result += f"\n🏷️ Tasks by Category:\n"
                for category, count in insights['tasks_by_category'].items():
                    result += f"  • {category.capitalize()}: {count}\n"

            if insights['tasks_by_priority']:
                result += f"\n🎯 Tasks by Priority:\n"
                priority_order = ['urgent', 'high', 'medium', 'low']
                for priority in priority_order:
                    if priority in insights['tasks_by_priority']:
                        count = insights['tasks_by_priority'][priority]
                        emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                        result += f"  {emoji} {priority.capitalize()}: {count}\n"

            if insights['upcoming_tasks']:
                result += f"\n📅 Upcoming Tasks (Next 7 Days):\n"
                for task in insights['upcoming_tasks']:
                    priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
                    result += f"  {priority_emoji} {task['title']} - Due: {task['due_date']}\n"

            return {
                "success": True,
                "result": result
            }

        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {
            "success": False,
            "error": f"Error executing {tool_name}: {str(e)}"
        }


def process_message(
    conversation_history: List[Dict[str, str]],
    new_message: str,
    user_id: str,
    session: Session
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Process a user message using Groq LLM with function calling

    Args:
        conversation_history: List of previous messages
        new_message: The new user message
        user_id: User ID for task operations
        session: Database session

    Returns:
        Tuple of (response_text, tool_calls_made)
    """
    try:
        client = get_groq_client()

        # Build messages for Groq API
        messages = []

        # System message
        messages.append({
            "role": "system",
            "content": """You are a helpful AI-powered todo assistant with advanced capabilities. You can help users:

Core Features:
- Create new tasks with AI-enhanced features
- List all their tasks
- Update existing tasks (title and/or description)
- Complete/toggle tasks
- Delete tasks

AI-Powered Features:
- Natural Language Due Dates: Extract dates from phrases like "tomorrow", "next Friday", "in 3 days", "by Monday"
- Smart Auto-Categorization: Automatically categorize tasks as work, personal, shopping, health, finance, home, or education
- Priority Suggestion: Suggest priority levels (urgent, high, medium, low) based on keywords
- Task Breakdown: Suggest subtasks for complex tasks like "plan wedding", "move house", "organize event"
- Productivity Insights: Show completion rates, overdue tasks, category breakdowns, and upcoming deadlines

CRITICAL RULES:
- When the list_tasks tool returns results, you MUST show ALL tasks exactly as returned by the tool
- DO NOT filter, remove, or modify the task list in any way
- DO NOT try to "clean up" or "correct" the task list
- DO NOT make assumptions about which tasks the user wants to see
- The tool returns the complete and accurate list - show it exactly as provided
- If the tool says "10 total", you must show all 10 tasks, not a subset

Guidelines:
- Be conversational and friendly in your responses
- When users mention dates naturally (e.g., "submit report by Friday"), automatically extract and set the due date
- Automatically categorize tasks based on their content (e.g., "buy groceries" → shopping)
- Suggest priority based on urgency keywords (e.g., "urgent", "asap" → urgent priority)
- Offer to break down complex tasks into subtasks when appropriate
- Provide productivity insights when users ask about their progress or stats
- Always confirm actions and provide clear feedback about what was done
- When users refer to tasks by name or description, you can search for them. When they use numbers, treat those as task positions in the list.
- When users want to UPDATE a task (change title, edit description, modify), use the update_task tool, NOT create_task

Examples:
- User: "Create task to submit report by Friday" → Extract "Friday" as due date, suggest priority
- User: "Add task to buy groceries" → Auto-categorize as "shopping"
- User: "Plan wedding" → Offer to suggest subtasks
- User: "Show my stats" → Display productivity insights with completion rate, categories, priorities
- User: "List all my tasks" → Show ALL tasks exactly as returned by the list_tasks tool, without filtering
- User: "Update task 1 title to 'Complete project report'" → Use update_task tool to modify the existing task
- User: "Change the description of 'buy groceries' to 'milk, bread, eggs'" → Use update_task tool"""
        })

        # Add conversation history (last 10 messages to keep context manageable)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add new message
        messages.append({
            "role": "user",
            "content": new_message
        })

        logger.info(f"Sending request to Groq for user {user_id}")

        # Call Groq API with tools
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated: llama-3.1-70b-versatile was decommissioned
            messages=messages,
            tools=TASK_TOOLS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1024
        )

        assistant_message = response.choices[0].message
        tool_calls_made = []

        # Check if the model wants to call tools
        if assistant_message.tool_calls:
            logger.info(f"Model requested {len(assistant_message.tool_calls)} tool calls")

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                # Execute the tool
                tool_result = execute_tool(tool_name, tool_args, session, user_id)
                tool_calls_made.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": tool_result
                })

                # Add tool result to messages for final response
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": tool_call.function.arguments
                        }
                    }]
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            # Get final response from model after tool execution
            final_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Updated: llama-3.1-70b-versatile was decommissioned
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )

            response_text = final_response.choices[0].message.content
        else:
            # No tool calls, just return the response
            response_text = assistant_message.content

        logger.info(f"Generated response for user {user_id}")
        return response_text, tool_calls_made

    except ValueError as e:
        # API key not set
        logger.error(f"Configuration error: {e}")
        return str(e), []
    except Exception as e:
        logger.error(f"Error processing message with Groq: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try again.", []
