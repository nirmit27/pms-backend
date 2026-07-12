"""
Activity routes

- Router for fetching system activities
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from auth.dependencies import get_current_user, require_permission
from models.models import User
from models.permissions import Permission
from services.db import get_recent_activities

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get(
    "/recent", dependencies=[Depends(require_permission(Permission.VIEW_ACTIVITIES))]
)
def fetch_recent_activities(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=50),
):
    """Fetch recent system activities."""
    data: list[dict] | None = get_recent_activities(limit)

    if data is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch recent activities."
        )

    return {"activities": data, "total": len(data)}
