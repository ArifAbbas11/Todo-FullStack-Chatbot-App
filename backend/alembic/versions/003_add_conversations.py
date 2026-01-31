"""add conversations and messages tables

Revision ID: 003_add_conversations
Revises: 002_create_tasks
Create Date: 2026-01-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_conversations'
down_revision: Union[str, None] = '002_create_tasks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create conversations and messages tables for AI chat persistence.

    Security Considerations:
    - UUID primary keys prevent enumeration attacks
    - Foreign keys ensure referential integrity
    - CASCADE delete ensures orphaned records are removed
    - Indexes on foreign keys and timestamps for performance
    - User isolation enforced at database level
    """
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_conversations_user_id',
            ondelete='CASCADE'  # Delete conversations when user is deleted
        )
    )

    # Create indexes on conversations table
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'], unique=False)
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'], unique=False)

    # Ensure trigger function exists (in case it was not created in previous migrations)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Apply updated_at trigger to conversations table
    op.execute("""
        CREATE TRIGGER update_conversations_updated_at
        BEFORE UPDATE ON conversations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversations.id'],
            name='fk_messages_conversation_id',
            ondelete='CASCADE'  # Delete messages when conversation is deleted
        )
    )

    # Create indexes on messages table
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)


def downgrade() -> None:
    """
    Drop conversations and messages tables.

    Security Note: This will permanently delete all conversations and messages.
    Use with extreme caution in production.
    """
    # Drop messages table first (due to foreign key dependency)
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.execute('DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;')
    op.drop_index('ix_conversations_created_at', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
