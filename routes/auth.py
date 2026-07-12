"""
Auth

- Router for user authentication and authorization
"""

import json
from json import JSONDecodeError
from typing import Annotated, Any
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, ValidationError

from auth.dependencies import (
    authenticate_user,
    authenticate_user_by_email,
    get_current_user,
)
from auth.jwt_handler import create_access_token
from services.db import create_user, user_exists

from models.models import User
from models.roles import Role
from models.auth import Token, UserOut, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login payload — email-based authentication."""

    email: EmailStr
    password: str


@router.post("/login", response_model=Token)
async def login_for_access_token(request: Request):
    email: str | None = None
    password: str | None = None
    username: str | None = None  # backward-compat for clients still sending username

    try:
        body = await request.json()
        if isinstance(body, dict):
            email = body.get("email")
            password = body.get("password")
            username = body.get("username")
    except (JSONDecodeError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        try:
            form_data = await request.form()
            email = form_data.get("email") or None  # type: ignore
            password = form_data.get("password") or None  # type: ignore
            username = form_data.get("username") or None  # type: ignore
        except Exception:
            raw_body = await request.body()
            if raw_body:
                try:
                    parsed_body = json.loads(raw_body.decode("utf-8"))
                    if isinstance(parsed_body, dict):
                        email = parsed_body.get("email")
                        password = parsed_body.get("password")
                        username = parsed_body.get("username")
                except (ValueError, JSONDecodeError, UnicodeDecodeError):
                    pass

    if not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is required.",
        )

    if not email and not username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email is required.",
        )

    # Resolve user by email (preferred) or fall back to username (legacy)
    user: User | None = None
    if email:
        user = authenticate_user_by_email(str(email).strip().lower(), password)
    if user is None and username:
        user = authenticate_user(username, password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
        expires_delta=timedelta(minutes=60),
    )
    return Token(access_token=token, token_type="bearer")


@router.post("/register", response_model=UserOut)
async def register_user(request: Request):
    try:
        body = await request.json()
    except (JSONDecodeError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        try:
            raw_body = await request.body()
            if not raw_body:
                raise HTTPException(status_code=400, detail="Request body is required.")
            parsed_body = json.loads(raw_body.decode("utf-8"))
        except (
            ValueError,
            JSONDecodeError,
            UnicodeDecodeError,
        ) as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON body.") from exc
    else:
        parsed_body = body

    if not isinstance(parsed_body, dict):
        raise HTTPException(
            status_code=400, detail="Request body must be a JSON object."
        )

    try:
        payload = RegisterRequest(**parsed_body)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    # NOTE: Self-registration is restricted to the PATIENT role.
    # Admin, doctor, and staff accounts must be provisioned out of band.
    if payload.role != Role.PATIENT:
        raise HTTPException(
            status_code=403,
            detail="Self-registration is restricted to the patient role. Contact an administrator.",
        )

    if not payload.username.strip():
        raise HTTPException(status_code=400, detail="Username is required.")
    if not payload.password.strip():
        raise HTTPException(status_code=400, detail="Password is required.")

    normalized_email = str(payload.email).strip().lower()
    if user_exists(payload.username, normalized_email):
        raise HTTPException(status_code=409, detail="User already exists.")

    created_user = create_user(
        {
            "id": payload.username,
            "username": payload.username,
            "email": normalized_email,
            "password_hash": payload.password,
            "role": payload.role.value,
            "is_active": True,
        }
    )

    if created_user is None:
        raise HTTPException(status_code=500, detail="Failed to create user.")

    return UserOut(**created_user)


@router.get("/me", response_model=UserOut)
def get_authenticated_user(current_user: Annotated[User, Depends(get_current_user)]):
    return UserOut(**current_user.model_dump())
