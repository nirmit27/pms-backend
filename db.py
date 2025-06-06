"""Database integration"""

from os import environ
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

MONGO_URI: str = environ.get("MONGO_URI", "")
DB: str = environ.get("DB", "")
COLLECTION: str = environ.get("COLLECTION", "")

client, db, collection = None, None, None


# Check for missing env. vars.

req_vars: dict[str, str] = {
    "MONGO_URI": MONGO_URI,
    "DB": DB,
    "COLLECTION": COLLECTION,
}
missing_vars: list[str] = [var for var, val in req_vars.items() if val == ""]


# Database connection

if missing_vars:
    print(f"\nWarning: Missing environment variables : {', '.join(missing_vars)}\n")
    client = None
    db = None
    collection = None
else:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client[DB]
        collection = db[COLLECTION]
    except errors.PyMongoError as e:
        print(f"\nError : {e}\n")
        client = None
        db = None
        collection = None


# CRUD methods


# CREATE operations
...


# READ operations
def get_all_patients() -> list[dict] | None:
    """Retrieves all the patient records."""
    if collection is None:
        return None

    return list(collection.find({}, {"_id": 0}))


def get_patient_by_id(pid: str) -> dict | str | None:
    """Retrieves the patient record with the matching ID."""
    if collection is None:
        return None

    result = collection.find_one({"pid": pid}, {"_id": 0})

    if result is None:
        return f"Patient with PID '{pid}' does not exist."

    return result


def get_patients_by_name(name: str) -> list[dict] | None:
    """Retrieves the patient record(s) with the matching name."""
    if collection is None:
        return None

    return list(collection.find({"name": name}, {"_id": 0}))


def sort_records_by_param(sort_by: str, reverse: bool) -> list[dict] | None:
    """Retrieves patient records sorted by given parameter value in specified order."""
    if collection is None:
        return None

    return list(collection.find({}, {"_id": 0}).sort({sort_by: -1 if reverse else 1}))


# UPDATE operations
...


# DELETE operations
...
