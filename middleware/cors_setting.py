"""
CORS policy
"""

from os import environ
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

FRONTEND_URL: str = environ.get("FRONTEND_URL", "http://localhost:5173")


def cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
