"""
AI Enhancement Services for Task Management
Provides natural language date parsing, auto-categorization, task breakdown, and productivity insights
"""
import dateparser
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import re


# ============================================================================
# Category Keywords Mapping
# ============================================================================

CATEGORY_KEYWORDS = {
    'work': ['meeting', 'project', 'deadline', 'presentation', 'report', 'email', 'call', 'client', 'conference', 'review', 'proposal', 'contract'],
    'personal': ['birthday', 'anniversary', 'family', 'friend', 'hobby', 'read', 'learn', 'visit', 'celebrate'],
    'shopping': ['buy', 'purchase', 'shop', 'groceries', 'store', 'order', 'amazon', 'mall', 'market'],
    'health': ['doctor', 'dentist', 'gym', 'exercise', 'workout', 'medicine', 'appointment', 'checkup', 'fitness'],
    'finance': ['pay', 'bill', 'invoice', 'tax', 'bank', 'budget', 'expense', 'payment', 'transfer'],
    'home': ['clean', 'repair', 'maintenance', 'organize', 'laundry', 'dishes', 'vacuum', 'fix'],
    'education': ['study', 'homework', 'assignment', 'exam', 'course', 'class', 'lecture', 'research', 'paper']
}


# ============================================================================
# Natural Language Date Parsing
# ============================================================================

def parse_natural_language_date(text: str) -> Optional[datetime]:
    """
    Parse natural language date expressions into datetime objects.

    Examples:
    - "tomorrow" -> tomorrow's date
    - "next Friday" -> next Friday's date
    - "in 3 days" -> 3 days from now
    - "January 15" -> January 15 of current/next year
    - "Friday at 5pm" -> next Friday at 5pm

    Args:
        text: Natural language date string

    Returns:
        datetime object or None if parsing fails
    """
    try:
        # Use dateparser with settings for better accuracy
        parsed_date = dateparser.parse(
            text,
            settings={
                'PREFER_DATES_FROM': 'future',  # Prefer future dates
                'RELATIVE_BASE': datetime.now(),
                'RETURN_AS_TIMEZONE_AWARE': False,
                'PREFER_DAY_OF_MONTH': 'first'  # For ambiguous dates
            }
        )

        # Only return if date is in the future (or today)
        if parsed_date and parsed_date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            return parsed_date

        return None
    except Exception:
        return None


def extract_date_from_task_text(title: str, description: Optional[str] = None) -> Optional[datetime]:
    """
    Extract date information from task title and description.

    Looks for patterns like:
    - "by Friday"
    - "due tomorrow"
    - "deadline next week"
    - "on January 15"
    - "until Monday"

    Args:
        title: Task title
        description: Optional task description

    Returns:
        Extracted datetime or None
    """
    # Common date indicator patterns
    date_patterns = [
        r'by\s+(.+?)(?:\s|$)',
        r'due\s+(.+?)(?:\s|$)',
        r'deadline\s+(.+?)(?:\s|$)',
        r'on\s+(.+?)(?:\s|$)',
        r'until\s+(.+?)(?:\s|$)',
        r'before\s+(.+?)(?:\s|$)'
    ]

    combined_text = f"{title} {description or ''}"

    # Try each pattern
    for pattern in date_patterns:
        match = re.search(pattern, combined_text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            # Extract up to 30 characters after the keyword (reasonable date length)
            date_str = date_str[:30].strip()
            parsed_date = parse_natural_language_date(date_str)
            if parsed_date:
                return parsed_date

    # If no pattern matched, try parsing the entire text
    # This catches cases like "Submit report Friday"
    parsed_date = parse_natural_language_date(combined_text)
    if parsed_date:
        return parsed_date

    return None


# ============================================================================
# Auto-Categorization
# ============================================================================

def auto_categorize_task(title: str, description: Optional[str] = None) -> Optional[str]:
    """
    Automatically categorize a task based on keywords in title and description.

    Uses keyword matching to assign one of the predefined categories:
    - work, personal, shopping, health, finance, home, education

    Args:
        title: Task title
        description: Optional task description

    Returns:
        Category name or None if no match found
    """
    combined_text = f"{title} {description or ''}".lower()

    # Count keyword matches for each category
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in combined_text)
        if score > 0:
            category_scores[category] = score

    # Return category with highest score
    if category_scores:
        return max(category_scores, key=category_scores.get)

    return None


# ============================================================================
# Task Breakdown Suggestions
# ============================================================================

def suggest_task_breakdown(title: str, description: Optional[str] = None) -> List[str]:
    """
    Suggest subtasks for complex tasks using keyword-based heuristics.

    Recognizes common complex task patterns and suggests appropriate subtasks.

    Args:
        title: Task title
        description: Optional task description

    Returns:
        List of suggested subtask titles
    """
    # Common complex task patterns and their subtasks
    task_patterns = {
        'wedding': [
            'Book venue',
            'Send invitations',
            'Choose catering menu',
            'Select photographer',
            'Plan decorations',
            'Arrange music/DJ',
            'Order wedding cake'
        ],
        'move': [
            'Pack belongings',
            'Hire moving company',
            'Update address with post office',
            'Transfer utilities',
            'Clean old place',
            'Unpack at new place'
        ],
        'vacation': [
            'Book flights',
            'Reserve accommodation',
            'Plan itinerary',
            'Pack luggage',
            'Arrange transportation',
            'Get travel insurance'
        ],
        'project': [
            'Define requirements',
            'Create timeline',
            'Assign tasks to team',
            'Review progress',
            'Finalize deliverables',
            'Present results'
        ],
        'event': [
            'Choose date and venue',
            'Create guest list',
            'Send invitations',
            'Plan activities',
            'Arrange catering',
            'Set up decorations'
        ],
        'party': [
            'Choose venue',
            'Create guest list',
            'Send invitations',
            'Plan menu',
            'Buy decorations',
            'Prepare music playlist'
        ],
        'trip': [
            'Book transportation',
            'Reserve accommodation',
            'Plan activities',
            'Pack essentials',
            'Arrange pet care',
            'Set up mail hold'
        ],
        'presentation': [
            'Research topic',
            'Create outline',
            'Design slides',
            'Practice delivery',
            'Prepare handouts',
            'Test equipment'
        ],
        'launch': [
            'Finalize product',
            'Create marketing materials',
            'Set up distribution',
            'Train support team',
            'Announce to customers',
            'Monitor feedback'
        ],
        'campaign': [
            'Define goals',
            'Identify target audience',
            'Create content',
            'Set up tracking',
            'Launch campaign',
            'Analyze results'
        ]
    }

    combined_text = f"{title} {description or ''}".lower()

    # Check for pattern matches
    for pattern, subtasks in task_patterns.items():
        if pattern in combined_text:
            return subtasks

    # If no specific pattern matched, check for generic "plan" keyword
    if 'plan' in combined_text:
        return [
            'Research and gather information',
            'Create detailed plan',
            'Identify resources needed',
            'Set timeline',
            'Execute plan',
            'Review and adjust'
        ]

    return []


# ============================================================================
# Productivity Insights
# ============================================================================

def calculate_productivity_insights(tasks: List[Any]) -> Dict[str, Any]:
    """
    Calculate productivity insights from user's tasks.

    Provides statistics on:
    - Total tasks, completed tasks, active tasks
    - Completion rate
    - Overdue tasks
    - Tasks by category
    - Tasks by priority

    Args:
        tasks: List of Task objects

    Returns:
        Dictionary with insights
    """
    if not tasks:
        return {
            'total_tasks': 0,
            'completed_tasks': 0,
            'active_tasks': 0,
            'completion_rate': 0,
            'overdue_tasks': 0,
            'tasks_by_category': {},
            'tasks_by_priority': {},
            'upcoming_tasks': []
        }

    now = datetime.now()
    completed = [t for t in tasks if t.is_completed]
    active = [t for t in tasks if not t.is_completed]
    overdue = [t for t in tasks if t.due_date and t.due_date < now and not t.is_completed]

    # Category breakdown
    category_counts = {}
    for task in tasks:
        if task.category:
            category_counts[task.category] = category_counts.get(task.category, 0) + 1

    # Priority breakdown
    priority_counts = {}
    for task in tasks:
        if task.priority:
            priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1

    # Upcoming tasks (next 7 days)
    upcoming = []
    seven_days_from_now = now + timedelta(days=7)
    for task in active:
        if task.due_date and now <= task.due_date <= seven_days_from_now:
            upcoming.append({
                'title': task.title,
                'due_date': task.due_date.strftime('%B %d, %Y'),
                'priority': task.priority or 'none'
            })

    # Sort upcoming by due date
    upcoming.sort(key=lambda x: x['due_date'])

    return {
        'total_tasks': len(tasks),
        'completed_tasks': len(completed),
        'active_tasks': len(active),
        'completion_rate': round((len(completed) / len(tasks)) * 100, 1) if tasks else 0,
        'overdue_tasks': len(overdue),
        'tasks_by_category': category_counts,
        'tasks_by_priority': priority_counts,
        'upcoming_tasks': upcoming[:5]  # Limit to 5 upcoming tasks
    }


# ============================================================================
# Priority Suggestion
# ============================================================================

def suggest_priority(title: str, description: Optional[str] = None) -> Optional[str]:
    """
    Suggest task priority based on keywords indicating urgency.

    Urgency indicators:
    - urgent, asap, critical, emergency -> urgent
    - important, deadline, soon -> high
    - later, eventually, someday -> low
    - default -> medium

    Args:
        title: Task title
        description: Optional task description

    Returns:
        Suggested priority: urgent, high, medium, low, or None
    """
    combined_text = f"{title} {description or ''}".lower()

    # Urgent indicators
    urgent_keywords = ['urgent', 'asap', 'critical', 'emergency', 'immediately', 'now']
    if any(keyword in combined_text for keyword in urgent_keywords):
        return 'urgent'

    # High priority indicators
    high_keywords = ['important', 'deadline', 'soon', 'priority', 'must', 'need to']
    if any(keyword in combined_text for keyword in high_keywords):
        return 'high'

    # Low priority indicators
    low_keywords = ['later', 'eventually', 'someday', 'maybe', 'consider', 'think about']
    if any(keyword in combined_text for keyword in low_keywords):
        return 'low'

    # Default to medium if no specific indicators
    return 'medium'
