"""Store optional reviewer assessment of explanation usefulness.

Revision ID: 20260928_0005
Revises: 20260928_0004
"""
from alembic import op
import sqlalchemy as sa


revision = '20260928_0005'
down_revision = '20260928_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('expert_reviews', sa.Column('explanation_helpfulness', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('expert_reviews', 'explanation_helpfulness')
