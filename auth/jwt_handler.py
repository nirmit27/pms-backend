"""
JWT-handling utilities
"""

from typing import Any
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError

from config.constants import (
    JWT_SECRET,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from models.roles import Role

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(
    user_id: str,
    username: str,
    role: Role,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Creates a JWT access token.

    Args:
        user_id: Unique ID of the authenticated user.
        username: Username.
        role: User role.
        expires_delta: Optional custom expiry duration.

    Returns:
        Encoded JWT.
    """

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload: dict[str, Any] = {
        "sub": user_id,
        "username": username,
        "role": role.value,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.

    Raises:
        HTTPException(401) if the token is invalid or expired.

    Returns:
        Decoded payload.
    """

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("sub") is None:
            raise credentials_exception

        return payload

    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    except InvalidTokenError as exc:
        raise credentials_exception from exc
