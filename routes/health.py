"""
Health check
"""

from os import environ
from dotenv import load_dotenv

from datetime import datetime
from pytz import timezone as tz

from fastapi import APIRouter

load_dotenv()
TIMEZONE: str = environ.get("TIMEZONE", "Asia/Kolkata")

router = APIRouter(tags=["Health"])


@router.get("/")
def index():
    return {"message": "Patient Management System 🏥"}


@router.get("/about")
def about():
    return {"message": "This is a microservice for managing patient records."}


@router.get("/health")
def health():
    return {
        "status": "All is well. ✈️",
        "time": f"{datetime.now(tz=tz(TIMEZONE)).isoformat()}",
    }
