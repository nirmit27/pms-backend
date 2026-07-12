"""
Constants
"""

from os import getenv
from dotenv import load_dotenv

load_dotenv()


# NOTE: Database connection env. vars.
MONGO_URI: str = getenv("MONGO_URI", "")
TIMEZONE: str = getenv("TIMEZONE", "Asia/Kolkata")
SERVER_SELECTION_TIMEOUT = int(getenv("SERVER_SELECTION_TIMEOUT", "3000"))

DB: str = getenv("DB", "")
USERS_COLLECTION: str = getenv("USERS_COLLECTION", "")
RECORDS_COLLECTION: str = getenv("RECORDS_COLLECTION", "")
ACTIVITES_COLLECTION: str = getenv("ACTIVITES_COLLECTION", "")


# NOTE: Auth. env. vars.
JWT_SECRET = getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = float(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
