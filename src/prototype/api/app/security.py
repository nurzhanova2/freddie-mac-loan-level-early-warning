"""Local development authentication; replace with managed identity before deployment."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_session
from .models import User

bearer = HTTPBearer(auto_error=False)
TOKEN_TTL_SECONDS = 60 * 60 * 8


def password_hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 200_000).hex()


def password_record(password: str) -> str:
    salt = secrets.token_hex(16)
    return f'{salt}${password_hash(password, salt)}'


def verify_password(password: str, record: str | None) -> bool:
    if not record or '$' not in record:
        return False
    salt, expected = record.split('$', 1)
    return hmac.compare_digest(password_hash(password, salt), expected)


def _secret() -> bytes:
    return os.environ.get('SUPTECH_AUTH_SECRET', 'replace-this-local-development-secret').encode()


def issue_token(user: User) -> str:
    payload = {'sub': user.username, 'role': user.role, 'exp': int(time.time()) + TOKEN_TTL_SECONDS}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode()).decode().rstrip('=')
    signature = hmac.new(_secret(), encoded.encode(), hashlib.sha256).hexdigest()
    return f'{encoded}.{signature}'


def decode_token(token: str) -> dict:
    try:
        encoded, signature = token.rsplit('.', 1)
        expected = hmac.new(_secret(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)))
        if payload['exp'] < time.time():
            raise ValueError
        return payload
    except (ValueError, KeyError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired access token')


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), session: Session = Depends(get_session)) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Bearer token required')
    payload = decode_token(credentials.credentials)
    user = session.scalar(select(User).where(User.username == payload['sub']))
    if user is None or not user.is_active or user.role != payload['role']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is unavailable')
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient role')
        return user
    return dependency
