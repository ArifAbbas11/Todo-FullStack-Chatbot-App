"""add task enhancements for AI features

Revision ID: 004_add_task_enhancements
Revises: 003_add_conversations
Create Date: 2026-01-30 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_add_task_enhancements'
down_revision: Union[str, None] = '003_add_conversations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add new fields for AI-enhanced task management:
    - due_date: Optional datetime for task deadlines
    - priority: Low, Medium, High, Urgent (nullable for backward compatibility)
    - category: Main category (work, personal, shopping, health, etc.)
    - tags: JSON array for multiple tags
    - parent_task_id: Self-referential FK for subtasks
    """

    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('priority', sa.String(length=20), nullable=True))
    op.add_column('tasks', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('tasks', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Add foreign key for parent_task_id (self-referential)
    op.create_foreign_key(
        'fk_tasks_parent_task_id',
        'tasks',
        'tasks',
        ['parent_task_id'],
        ['id'],
        ondelete='CASCADE'  # Delete subtasks when parent is deleted
    )

    # Create indexes for performance
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'], unique=False)
    op.create_index('ix_tasks_priority', 'tasks', ['priority'], unique=False)
    op.create_index('ix_tasks_category', 'tasks', ['category'], unique=False)
    op.create_index('ix_tasks_parent_task_id', 'tasks', ['parent_task_id'], unique=False)

    # Create composite index for common queries (user_id + due_date)
    op.create_index('ix_tasks_user_due_date', 'tasks', ['user_id', 'due_date'], unique=False)


def downgrade() -> None:
    """Remove task enhancement fields"""
    # Drop indexes
    op.drop_index('ix_tasks_user_due_date', table_name='tasks')
    op.drop_index('ix_tasks_parent_task_id', table_name='tasks')
    op.drop_index('ix_tasks_category', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_index('ix_tasks_due_date', table_name='tasks')

    # Drop foreign key
    op.drop_constraint('fk_tasks_parent_task_id', 'tasks', type_='foreignkey')

    # Drop columns
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'category')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'due_date')
