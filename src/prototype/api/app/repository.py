import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Alert, AuditEvent, DataVersion, ExpertReview, ModelRun, ModelVersion, User
from .security import password_record
from .adapters.score_export import load_approved_alert_export


def seed_demo_data(session: Session) -> None:
    model_version = session.scalar(select(ModelVersion).limit(1))
    if model_version is None:
        source_alerts, classification = load_approved_alert_export()
        data_version = DataVersion(version='fannie_panel_v01', classification=classification)
        model_version = ModelVersion(version='calibrated_xgboost_v01', targets='formal_adverse_6m,early_deterioration_6m', validation_summary='temporal validation + out-of-time test', use_status='research_prototype_only')
        session.add_all([data_version, model_version])
        session.flush()
        session.add(ModelRun(run_reference='demo-run-2025-09-12', model_version_id=model_version.id, data_version_id=data_version.id))
        for source in source_alerts:
            session.add(Alert(**{key: source[key] for key in ('alert_id', 'loan_reference', 'cohort', 'reporting_month', 'target', 'risk_score', 'trigger_threshold', 'tier', 'top_shap_driver', 'top_shap_contribution', 'review_status')}, model_version_id=model_version.id, data_version_id=data_version.id))
    password = __import__('os').environ.get('SUPTECH_DEMO_PASSWORD', 'demo-password-change-me')
    for username, role in [('demo_research_viewer', 'research_viewer'), ('demo_risk_analyst', 'risk_analyst'), ('demo_model_governance', 'model_governance'), ('demo_data_steward', 'data_steward'), ('demo_platform_admin', 'platform_admin')]:
        user = session.scalar(select(User).where(User.username == username))
        if user is None:
            session.add(User(username=username, role=role, password_hash=password_record(password)))
        elif not user.password_hash:
            user.password_hash = password_record(password)
    session.commit()


def serialize_alert(alert: Alert, session: Session) -> dict:
    model = session.get(ModelVersion, alert.model_version_id)
    data = session.get(DataVersion, alert.data_version_id)
    latest_review = session.scalar(select(ExpertReview).where(ExpertReview.alert_id == alert.id).order_by(ExpertReview.reviewed_at.desc()).limit(1))
    return {
        'alert_id': alert.alert_id, 'loan_reference': alert.loan_reference, 'cohort': alert.cohort,
        'reporting_month': alert.reporting_month, 'target': alert.target, 'risk_score': alert.risk_score,
        'trigger_threshold': alert.trigger_threshold, 'tier': alert.tier, 'top_shap_driver': alert.top_shap_driver,
        'top_shap_contribution': alert.top_shap_contribution, 'review_status': alert.review_status,
        'expert_decision': latest_review.decision if latest_review else None,
        'model_version': model.version, 'data_version': data.version,
    }


def record_review(session: Session, alert: Alert, decision: str, comment: str | None, reviewer: User) -> ExpertReview:
    review = ExpertReview(alert_id=alert.id, user_id=reviewer.id, decision=decision, comment=comment)
    alert.review_status = 'Reviewed'
    session.add(review)
    session.flush()
    session.add(AuditEvent(alert_id=alert.id, actor=reviewer.username, event_type='expert_review_recorded', payload_json=json.dumps({'decision': decision, 'comment': comment, 'model_version_id': alert.model_version_id, 'data_version_id': alert.data_version_id}, sort_keys=True)))
    session.commit()
    session.refresh(review)
    return review
