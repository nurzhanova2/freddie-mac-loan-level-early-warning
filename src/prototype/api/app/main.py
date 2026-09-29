from contextlib import asynccontextmanager
import json
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import SessionLocal, get_session
from .models import Alert, AuditEvent, DataVersion, ExpertReview, ModelRun, ModelVersion
from .repository import record_review, seed_demo_data, serialize_alert
from .schemas import LoginRequest, ReviewCreate, UserCreate, UserUpdate
from .security import issue_token, password_record, require_roles, verify_password
from .models import User
from .alert_contract import BROWSER_ALERT_FIELDS

API_VERSION = 'v1'

@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as session:
        seed_demo_data(session)
    yield


app = FastAPI(title='SupTech Research Prototype API', version=API_VERSION, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['*'])


def envelope(data, session: Session | None = None):
    classification = 'synthetic_demo_only'
    if session is not None:
        classification = session.scalar(select(DataVersion.classification).limit(1)) or classification
    return {'api_version': API_VERSION, 'data_classification': classification, 'data': data}


def get_alert_or_404(session: Session, alert_id: str) -> Alert:
    alert = session.scalar(select(Alert).where(Alert.alert_id == alert_id))
    if alert is None:
        raise HTTPException(status_code=404, detail='Alert not found')
    return alert


@app.get('/api/v1/health')
def health(session: Session = Depends(get_session)):
    classification = session.scalar(select(DataVersion.classification).limit(1)) or 'synthetic_demo_only'
    return envelope({'status': 'ok', 'service': 'suptech-api', 'database': 'postgresql', 'real_data_adapter_enabled': classification == 'approved_research_export'}, session)


@app.post('/api/v1/auth/login')
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.username == payload.username))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return envelope({'access_token': issue_token(user), 'token_type': 'bearer', 'role': user.role, 'username': user.username}, session)


def user_dto(user: User) -> dict:
    return {'username': user.username, 'role': user.role, 'is_active': user.is_active, 'created_at': user.created_at.isoformat()}


@app.get('/api/v1/admin/users')
def list_users(session: Session = Depends(get_session), _: User = Depends(require_roles('model_governance', 'platform_admin'))):
    users = list(session.scalars(select(User).order_by(User.username)))
    return envelope({'items': [user_dto(user) for user in users]}, session)


@app.post('/api/v1/admin/users', status_code=201)
def create_user(payload: UserCreate, session: Session = Depends(get_session), actor: User = Depends(require_roles('model_governance', 'platform_admin'))):
    if session.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(status_code=409, detail='Username already exists')
    user = User(username=payload.username, role=payload.role, password_hash=password_record(payload.password), is_active=True)
    session.add(user)
    session.flush()
    session.add(AuditEvent(actor=actor.username, event_type='user_created', payload_json=json.dumps({'username': user.username, 'role': user.role}, sort_keys=True)))
    session.commit()
    session.refresh(user)
    return envelope(user_dto(user), session)


@app.patch('/api/v1/admin/users/{username}')
def update_user(username: str, payload: UserUpdate, session: Session = Depends(get_session), actor: User = Depends(require_roles('model_governance', 'platform_admin'))):
    user = session.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    if actor.id == user.id:
        raise HTTPException(status_code=400, detail='A user cannot alter their own role or activation status')
    if not payload.confirmed:
        raise HTTPException(status_code=400, detail='Confirmed role or activation change is required')
    before = {'role': user.role, 'is_active': user.is_active}
    removes_active_admin = user.role == 'platform_admin' and user.is_active and (payload.role not in (None, 'platform_admin') or payload.is_active is False)
    if removes_active_admin:
        active_admins = session.scalar(select(func.count()).select_from(User).where(User.role == 'platform_admin', User.is_active.is_(True)))
        if active_admins <= 1:
            raise HTTPException(status_code=400, detail='The last active platform administrator cannot be removed or deactivated')
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    session.add(AuditEvent(actor=actor.username, event_type='user_access_updated', payload_json=json.dumps({'username': user.username, 'before': before, 'after': {'role': user.role, 'is_active': user.is_active}, 'reason': payload.reason}, sort_keys=True)))
    session.commit()
    session.refresh(user)
    return envelope(user_dto(user), session)


@app.get('/api/v1/contract')
def contract(session: Session = Depends(get_session), _: User = Depends(require_roles('research_viewer', 'risk_analyst', 'model_governance', 'data_steward'))):
    return envelope({'allowed_browser_fields': BROWSER_ALERT_FIELDS, 'forbidden_classes': ['raw_files', 'stable_loan_ids', 'full_feature_vectors', 'training_samples']}, session)


@app.get('/api/v1/alerts')
def list_alerts(tier: Literal['Red', 'Amber'] | None = None, review_status: Literal['Pending', 'In review', 'Reviewed'] | None = None, limit: int = Query(default=50, ge=1, le=100), session: Session = Depends(get_session), _: User = Depends(require_roles('research_viewer', 'risk_analyst', 'model_governance', 'data_steward'))):
    statement = select(Alert).order_by(Alert.reporting_month.desc(), Alert.risk_score.desc()).limit(limit)
    if tier:
        statement = statement.where(Alert.tier == tier)
    if review_status:
        statement = statement.where(Alert.review_status == review_status)
    alerts = list(session.scalars(statement))
    return envelope({'count': len(alerts), 'items': [serialize_alert(alert, session) for alert in alerts]}, session)


@app.get('/api/v1/alerts/{alert_id}')
def alert_detail(alert_id: str, session: Session = Depends(get_session), _: User = Depends(require_roles('research_viewer', 'risk_analyst', 'model_governance', 'data_steward'))):
    return envelope(serialize_alert(get_alert_or_404(session, alert_id), session), session)


@app.get('/api/v1/alerts/{alert_id}/explanation')
def alert_explanation(alert_id: str, session: Session = Depends(get_session), _: User = Depends(require_roles('research_viewer', 'risk_analyst', 'model_governance', 'data_steward'))):
    alert = get_alert_or_404(session, alert_id)
    model = session.get(ModelVersion, alert.model_version_id)
    return envelope({'alert_id': alert.alert_id, 'method': 'SHAP', 'top_driver': alert.top_shap_driver, 'top_contribution': alert.top_shap_contribution, 'model_version': model.version}, session)


@app.post('/api/v1/alerts/{alert_id}/reviews', status_code=201)
def create_review(alert_id: str, payload: ReviewCreate, session: Session = Depends(get_session), user: User = Depends(require_roles('risk_analyst', 'model_governance'))):
    alert = get_alert_or_404(session, alert_id)
    review = record_review(session, alert, payload.decision, payload.comment, payload.explanation_helpfulness, user)
    return envelope({'review_id': review.id, 'alert_id': alert.alert_id, 'decision': review.decision, 'comment': review.comment, 'explanation_helpfulness': review.explanation_helpfulness, 'reviewed_at': review.reviewed_at.isoformat(), 'review_status': alert.review_status}, session)


@app.get('/api/v1/audit-events')
def audit_events(limit: int = Query(default=50, ge=1, le=100), session: Session = Depends(get_session), _: User = Depends(require_roles('model_governance', 'data_steward'))):
    events = list(session.scalars(select(AuditEvent).order_by(AuditEvent.occurred_at.desc()).limit(limit)))
    return envelope({'count': len(events), 'items': [{'event_id': event.id, 'alert_id': session.get(Alert, event.alert_id).alert_id if event.alert_id else None, 'actor': event.actor, 'event_type': event.event_type, 'payload': json.loads(event.payload_json), 'occurred_at': event.occurred_at.isoformat()} for event in events]}, session)


@app.get('/api/v1/metrics/overview')
def overview_metrics(session: Session = Depends(get_session), _: User = Depends(require_roles('research_viewer', 'risk_analyst', 'model_governance', 'data_steward'))):
    count = lambda condition: session.scalar(select(func.count()).select_from(Alert).where(condition))
    return envelope({'alert_count': session.scalar(select(func.count()).select_from(Alert)), 'red_alert_count': count(Alert.tier == 'Red'), 'amber_alert_count': count(Alert.tier == 'Amber'), 'requires_review_count': count(Alert.review_status != 'Reviewed')}, session)


@app.get('/api/v1/evaluation/summary')
def evaluation_summary(session: Session = Depends(get_session), _: User = Depends(require_roles('research_viewer', 'risk_analyst', 'model_governance', 'data_steward'))):
    """Operational-use metrics; no claim of a prospective user study is made."""
    alerts = list(session.scalars(select(Alert)))
    reviews = list(session.scalars(select(ExpertReview)))
    reviewed_ids = {review.alert_id for review in reviews}
    tiers = []
    for tier in ('Red', 'Amber'):
        subset = [alert for alert in alerts if alert.tier == tier]
        observed = [alert for alert in subset if alert.observed_outcome is not None]
        tiers.append({
            'tier': tier,
            'alerts': len(subset),
            'reviewed_alerts': sum(alert.id in reviewed_ids for alert in subset),
            'pending_alerts': sum(alert.review_status != 'Reviewed' for alert in subset),
            'outcomes_observed': len(observed),
            'confirmed_alerts': sum(alert.observed_outcome == 1 for alert in observed),
            'confirmed_alert_rate': (sum(alert.observed_outcome == 1 for alert in observed) / len(observed)) if observed else None,
        })
    ratings = [review.explanation_helpfulness for review in reviews if review.explanation_helpfulness is not None]
    return envelope({'tiers': tiers, 'review_actions': len(reviews), 'explanation_ratings_count': len(ratings), 'mean_explanation_helpfulness': (sum(ratings) / len(ratings)) if ratings else None, 'status': 'instrumented_for_user_evaluation_not_a_completed_user_study'}, session)


@app.get('/api/v1/model-registry')
def model_registry(session: Session = Depends(get_session), _: User = Depends(require_roles('model_governance', 'data_steward'))):
    model = session.scalar(select(ModelVersion).limit(1))
    data = session.scalar(select(DataVersion).limit(1))
    tree_oot_run = session.scalar(select(ModelRun).where(ModelRun.run_reference == 'tree-model-oot-governance-v01'))
    registry_decision = None
    if tree_oot_run is not None:
        registry_decision = {
            'status': 'No registry change',
            'message': 'v02 Q1+Q3 tree-model evaluation completed; no registry change.',
            'active_model': model.version,
        }
    return envelope({'model_version': model.version, 'data_version': data.version, 'targets': model.targets.split(','), 'validation': model.validation_summary, 'use_status': model.use_status, 'registry_decision': registry_decision}, session)
