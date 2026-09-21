"""Add password material for local development authentication.

Revision ID: 20260921_0002
Revises: 20260921_0001
"""
from alembic import op
import sqlalchemy as sa


revision = '20260921_0002'
down_revision = '20260921_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'password_hash')
