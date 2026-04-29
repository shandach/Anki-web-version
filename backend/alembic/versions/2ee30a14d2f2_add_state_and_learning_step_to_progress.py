"""add_state_and_learning_step_to_progress

Revision ID: 2ee30a14d2f2
Revises: 5dc7f8d0a81e
Create Date: 2026-04-30 01:20:29.264638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ee30a14d2f2'
down_revision: Union[str, Sequence[str], None] = '5dc7f8d0a81e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('progress', sa.Column('state', sa.String(), nullable=True))
    op.add_column('progress', sa.Column('learning_step', sa.Integer(), nullable=True))

    # Set default values for existing rows
    op.execute("UPDATE progress SET state = 'review' WHERE state IS NULL")
    op.execute("UPDATE progress SET learning_step = 0 WHERE learning_step IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('progress', 'learning_step')
    op.drop_column('progress', 'state')
