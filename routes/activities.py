"""
Activity routes

- Router for fetching system activities
"""

from fastapi import APIRouter, HTTPException, Query

from services.db import get_recent_activities

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/recent")
def fetch_recent_activities(limit: int = Query(10, ge=1, le=50)):
    """Fetch recent system activities."""
    data: list[dict] | None = get_recent_activities(limit)

    if data is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch recent activities."
        )

    return {"activities": data, "total": len(data)}
