"""
Authentication dependencies.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.jwt_handler import decode_access_token
from auth.password_manager import verify_password
from auth.permission_manager import has_permission
from models.models import User
from models.permissions import Permission
from services.db import get_user_by_username, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def authenticate_user(username: str, password: str) -> User | None:
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def authenticate_user_by_email(email: str, password: str) -> User | None:
    """
    Authenticate a user via email + password.
    Performs a case-insensitive, trimmed email lookup.
    """
    normalized_email = (email or "").strip().lower()
    user = get_user_by_email(normalized_email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(token)
    user = get_user_by_username(payload.get("username", ""))

    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    return user


def require_permission(permission: Permission):
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return permission_checker
