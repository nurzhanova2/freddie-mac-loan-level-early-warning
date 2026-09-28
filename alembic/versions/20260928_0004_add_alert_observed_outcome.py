"""Add post-window observed-outcome fields to the alert audit trail.

Revision ID: 20260928_0004
Revises: 20260921_0003
"""
from alembic import op
import sqlalchemy as sa


revision = '20260928_0004'
down_revision = '20260921_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('observed_outcome', sa.Integer(), nullable=True))
    op.add_column('alerts', sa.Column('outcome_observed_at', sa.String(length=10), nullable=True))


def downgrade() -> None:
    op.drop_column('alerts', 'outcome_observed_at')
    op.drop_column('alerts', 'observed_outcome')
