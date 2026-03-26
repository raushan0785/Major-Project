"""Async authentication routes backed by MongoDB."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from ..dependencies import get_current_user, get_db
from ..schemas import Token, UserCreate, UserOut
from ..utils.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db=Depends(get_db)):
    """Register a new user."""
    user_doc = {
        "email": user_in.email.lower(),
        "full_name": user_in.full_name,
        "hashed_password": hash_password(user_in.password),
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.utcnow(),
    }

    try:
        result = await db.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc["_id"] = str(result.inserted_id)
    user_doc.pop("hashed_password", None)
    return UserOut(**user_doc)


@router.post("/login", response_model=Token)
async def login(credentials: LoginSchema, db=Depends(get_db)):
    """Authenticate a user and issue a JWT access token."""
    user = await db.users.find_one({"email": credentials.email.lower()})
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user["_id"])})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def read_me(current_user=Depends(get_current_user)):
    """Return the authenticated user's profile."""
    current_user.pop("hashed_password", None)
    current_user["_id"] = str(current_user["_id"])
    return UserOut(**current_user)
