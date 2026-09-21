"""Create the initial SupTech prototype schema.

Revision ID: 20260921_0001
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = '20260921_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('username', sa.String(80), nullable=False, unique=True), sa.Column('role', sa.String(40), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('data_versions', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('version', sa.String(80), nullable=False, unique=True), sa.Column('classification', sa.String(80), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('model_versions', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('version', sa.String(80), nullable=False, unique=True), sa.Column('targets', sa.String(200), nullable=False), sa.Column('validation_summary', sa.String(240), nullable=False), sa.Column('use_status', sa.String(80), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('model_runs', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('run_reference', sa.String(100), nullable=False, unique=True), sa.Column('model_version_id', sa.Integer(), sa.ForeignKey('model_versions.id'), nullable=False), sa.Column('data_version_id', sa.Integer(), sa.ForeignKey('data_versions.id'), nullable=False), sa.Column('run_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('alerts', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('alert_id', sa.String(80), nullable=False, unique=True), sa.Column('loan_reference', sa.String(80), nullable=False), sa.Column('cohort', sa.String(20), nullable=False), sa.Column('reporting_month', sa.String(10), nullable=False), sa.Column('target', sa.String(80), nullable=False), sa.Column('risk_score', sa.Float(), nullable=False), sa.Column('trigger_threshold', sa.Float(), nullable=False), sa.Column('tier', sa.String(10), nullable=False), sa.Column('top_shap_driver', sa.String(120), nullable=False), sa.Column('top_shap_contribution', sa.Float(), nullable=False), sa.Column('review_status', sa.String(30), nullable=False), sa.Column('model_version_id', sa.Integer(), sa.ForeignKey('model_versions.id'), nullable=False), sa.Column('data_version_id', sa.Integer(), sa.ForeignKey('data_versions.id'), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('expert_reviews', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('alert_id', sa.Integer(), sa.ForeignKey('alerts.id'), nullable=False), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False), sa.Column('decision', sa.String(80), nullable=False), sa.Column('comment', sa.Text(), nullable=True), sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('audit_events', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('alert_id', sa.Integer(), sa.ForeignKey('alerts.id'), nullable=True), sa.Column('actor', sa.String(80), nullable=False), sa.Column('event_type', sa.String(80), nullable=False), sa.Column('payload_json', sa.Text(), nullable=False), sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('expert_reviews')
    op.drop_table('alerts')
    op.drop_table('model_runs')
    op.drop_table('model_versions')
    op.drop_table('data_versions')
    op.drop_table('users')
