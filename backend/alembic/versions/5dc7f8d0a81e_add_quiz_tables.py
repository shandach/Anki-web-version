"""Add quiz tables

Revision ID: 5dc7f8d0a81e
Revises: 001
Create Date: 2026-04-29 18:35:10.980302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dc7f8d0a81e'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create quiz_cards table
    op.create_table(
        'quiz_cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deck_id', sa.Integer(), nullable=False),
        sa.Column('source_deck_id', sa.Integer(), nullable=True),
        sa.Column('question', sa.String(), nullable=False),
        sa.Column('correct_answers', sa.JSON(), nullable=False),
        sa.Column('wrong_answers', sa.JSON(), nullable=False),
        sa.Column('is_multiple', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_deck_id'], ['decks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quiz_cards_deck_id', 'quiz_cards', ['deck_id'])

    # Create quiz_progress table
    op.create_table(
        'quiz_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quiz_card_id', sa.Integer(), nullable=False),
        sa.Column('ease_factor', sa.Float(), nullable=False, server_default='2.5'),
        sa.Column('interval_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('repetitions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('correct_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quiz_card_id'], ['quiz_cards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quiz_progress_user_id', 'quiz_progress', ['user_id'])
    op.create_index('ix_quiz_progress_quiz_card_id', 'quiz_progress', ['quiz_card_id'])
    op.create_index('ix_quiz_progress_due_date', 'quiz_progress', ['due_date'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_quiz_progress_due_date', 'quiz_progress')
    op.drop_index('ix_quiz_progress_quiz_card_id', 'quiz_progress')
    op.drop_index('ix_quiz_progress_user_id', 'quiz_progress')
    op.drop_table('quiz_progress')
    op.drop_index('ix_quiz_cards_deck_id', 'quiz_cards')
    op.drop_table('quiz_cards')

