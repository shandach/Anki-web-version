"""add explanation to quiz cards

Revision ID: 003_add_explanation
Revises: 2ee30a14d2f2
Create Date: 2026-05-01 07:43:36.192000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_explanation'
down_revision = '2ee30a14d2f2'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем поле explanation в таблицу quiz_cards
    op.add_column('quiz_cards', sa.Column('explanation', sa.Text(), nullable=True))


def downgrade():
    # Удаляем поле explanation из таблицы quiz_cards
    op.drop_column('quiz_cards', 'explanation')
