from typing import Literal

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    decision: str = Field(min_length=2, max_length=80)
    comment: str | None = Field(default=None, max_length=2000)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=200)


RoleName = Literal['research_viewer', 'risk_analyst', 'model_governance', 'data_steward', 'platform_admin']


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80, pattern=r'^[a-zA-Z0-9_.-]+$')
    password: str = Field(min_length=8, max_length=200)
    role: RoleName


class UserUpdate(BaseModel):
    role: RoleName | None = None
    is_active: bool | None = None
    reason: str = Field(min_length=3, max_length=500)
    confirmed: bool = False
