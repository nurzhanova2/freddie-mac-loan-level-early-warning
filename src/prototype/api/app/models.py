from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    role: Mapped[str] = mapped_column(String(40))
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DataVersion(Base):
    __tablename__ = 'data_versions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(80), unique=True)
    classification: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ModelVersion(Base):
    __tablename__ = 'model_versions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(80), unique=True)
    targets: Mapped[str] = mapped_column(String(200))
    validation_summary: Mapped[str] = mapped_column(String(240))
    use_status: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ModelRun(Base):
    __tablename__ = 'model_runs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_reference: Mapped[str] = mapped_column(String(100), unique=True)
    model_version_id: Mapped[int] = mapped_column(ForeignKey('model_versions.id'))
    data_version_id: Mapped[int] = mapped_column(ForeignKey('data_versions.id'))
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Alert(Base):
    __tablename__ = 'alerts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(80), unique=True)
    loan_reference: Mapped[str] = mapped_column(String(80))
    cohort: Mapped[str] = mapped_column(String(20))
    reporting_month: Mapped[str] = mapped_column(String(10))
    target: Mapped[str] = mapped_column(String(80))
    risk_score: Mapped[float] = mapped_column(Float)
    trigger_threshold: Mapped[float] = mapped_column(Float)
    tier: Mapped[str] = mapped_column(String(10))
    top_shap_driver: Mapped[str] = mapped_column(String(120))
    top_shap_contribution: Mapped[float] = mapped_column(Float)
    review_status: Mapped[str] = mapped_column(String(30))
    model_version_id: Mapped[int] = mapped_column(ForeignKey('model_versions.id'))
    data_version_id: Mapped[int] = mapped_column(ForeignKey('data_versions.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ExpertReview(Base):
    __tablename__ = 'expert_reviews'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey('alerts.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    decision: Mapped[str] = mapped_column(String(80))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int | None] = mapped_column(ForeignKey('alerts.id'), nullable=True)
    actor: Mapped[str] = mapped_column(String(80))
    event_type: Mapped[str] = mapped_column(String(80))
    payload_json: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
