"""Pydantic schemas for Mongo-backed auth flows (simplified)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserOut(UserBase):
    id: str = Field(alias="_id")
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
