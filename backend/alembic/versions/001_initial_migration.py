"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-04-29 12:33:42.383000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create decks table
    op.create_table('decks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decks_id'), 'decks', ['id'], unique=False)

    # Create cards table
    op.create_table('cards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deck_id', sa.Integer(), nullable=False),
    sa.Column('front', sa.Text(), nullable=False),
    sa.Column('back', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cards_id'), 'cards', ['id'], unique=False)

    # Create progress table
    op.create_table('progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('card_id', sa.Integer(), nullable=False),
    sa.Column('ease_factor', sa.Float(), nullable=True),
    sa.Column('interval_days', sa.Integer(), nullable=True),
    sa.Column('repetitions', sa.Integer(), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=False),
    sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_progress_id'), 'progress', ['id'], unique=False)

    # Create reviews table
    op.create_table('reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('card_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.String(), nullable=False),
    sa.Column('old_interval_days', sa.Integer(), nullable=True),
    sa.Column('new_interval_days', sa.Integer(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_reviews_id'), table_name='reviews')
    op.drop_table('reviews')
    op.drop_index(op.f('ix_progress_id'), table_name='progress')
    op.drop_table('progress')
    op.drop_index(op.f('ix_cards_id'), table_name='cards')
    op.drop_table('cards')
    op.drop_index(op.f('ix_decks_id'), table_name='decks')
    op.drop_table('decks')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
