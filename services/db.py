"""
DB integration
"""

from pymongo import MongoClient, errors
from pytz import timezone as tz
from datetime import datetime, timedelta

from auth.password_manager import hash_password
from models.models import Patient, PatientUpdate, User
from models.roles import Role
from config.constants import (
    DB,
    MONGO_URI,
    SERVER_SELECTION_TIMEOUT,
    USERS_COLLECTION,
    RECORDS_COLLECTION,
    ACTIVITES_COLLECTION,
    TIMEZONE,
)

client, db, records_collection, users_collection = None, None, None, None


# NOTE: Check for missing env. vars.

req_vars: dict[str, str | int | float] = {
    "DB": DB,
    "MONGO_URI": MONGO_URI,
    "USERS_COLLECTION": USERS_COLLECTION,
    "RECORDS_COLLECTION": RECORDS_COLLECTION,
    "ACTIVITIES_COLLECTION": ACTIVITES_COLLECTION,
    "SERVER_SELECTION_TIMEOUT": SERVER_SELECTION_TIMEOUT,
}
missing_vars: list[str] = [var for var, val in req_vars.items() if val == ""]


# NOTE: Database connection

if missing_vars:
    print(f"\nWarning: Missing environment variables : {', '.join(missing_vars)}\n")
    client = None
    db = None
    records_collection = None
else:
    try:
        client = MongoClient(
            MONGO_URI, serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT
        )
        db = client[DB]
        records_collection = db[RECORDS_COLLECTION]
        users_collection = db[USERS_COLLECTION]
    except errors.PyMongoError as e:
        print(f"\nError : {e}\n")
        client = None
        db = None
        records_collection = None


# NOTE: Auth helpers


def get_user_by_username(username: str) -> User | None:
    """Fetch a user by username from the configured users collection."""
    if users_collection is not None:
        result = users_collection.find_one({"username": username}, {"_id": 0})
        if result is None:
            return None
        return User(**result)

    return None


def get_user_by_email(email: str) -> User | None:
    """
    Fetch a user by email (case-insensitive, trimmed).
    """
    if users_collection is None:
        return None
    if not email:
        return None
    normalized = email.strip().lower()
    result = users_collection.find_one(
        {"email": {"$regex": f"^{normalized}$", "$options": "i"}}, {"_id": 0}
    )
    if result is None:
        return None
    return User(**result)


def create_user(user_data: dict) -> dict | None:
    """Create a new user document in the configured users collection."""
    if users_collection is None:
        return None

    try:
        payload = dict(user_data)
        payload.setdefault("is_active", True)
        payload.setdefault("role", Role.PATIENT.value)
        payload["password_hash"] = hash_password(payload["password_hash"])
        result = users_collection.insert_one(payload)
        if not result.inserted_id:
            return None
        payload["id"] = str(result.inserted_id)
        return payload
    except Exception as exc:
        print(f"\nError creating user: {exc}\n")
        return None


def user_exists(username: str, email: str | None = None) -> bool:
    """Check whether a username or email already exists in the users collection."""
    if users_collection is None:
        return False

    query = {"$or": [{"username": username}]}
    if email is not None:
        query["$or"].append({"email": email})

    return users_collection.find_one(query) is not None


# NOTE: CRUD operation handlers


# NOTE: CREATE operation
def add_patient(p_data: Patient) -> dict | None:
    """Creating a new patient record."""
    if records_collection is None:
        return None

    try:
        temp: dict = p_data.model_dump().copy()

        if "date_of_admission" in temp.keys() and temp["date_of_admission"]:
            temp["date_of_admission"] = str(temp["date_of_admission"])

        if "date_of_discharge" in temp.keys() and temp["date_of_discharge"]:
            temp["date_of_discharge"] = str(temp["date_of_discharge"])

        result = records_collection.insert_one(temp)
        return temp if result.inserted_id else None

    except Exception as e:
        print(f"\nError adding patient record : {e}\n")
        return None


# NOTE: READ operations
def get_all_patients() -> list[dict] | None:
    """Retrieves all the patient records."""
    if records_collection is None:
        return None

    return list(records_collection.find({}, {"_id": 0}))


def get_patient_by_id(pid: str) -> dict | str | None:
    """Retrieves the patient record with the matching ID."""
    if records_collection is None:
        return None

    result = records_collection.find_one({"pid": pid}, {"_id": 0})

    if result is None:
        return f"Patient with PID '{pid}' does not exist."

    return result


def get_patients_by_name(name: str) -> list[dict] | None:
    """Retrieves the patient record(s) with the matching name."""
    if records_collection is None:
        return None

    return list(records_collection.find({"name": name}, {"_id": 0}))


def get_patients_by_name_fuzzy(name: str) -> list[dict] | None:
    """Retrieves patient records with fuzzy name matching.
    Returns results sorted by relevance (exact matches first, then partial matches).
    """
    if records_collection is None:
        return None

    if not name.strip():
        return []

    # NOTE: Create a case-insensitive regex pattern for partial matching
    pattern = f".*{name}.*"

    results = list(
        records_collection.find(
            {"name": {"$regex": pattern, "$options": "i"}}, {"_id": 0}
        )
    )

    # NOTE: Sort results by relevance (exact match first, then by length of name)
    results.sort(
        key=lambda x: (
            not x["name"].lower() == name.lower(),  # Exact matches first
            len(x["name"]),  # Then shorter names (more likely exact matches)
        )
    )

    return results


def sort_records_by_param(sort_by: str, reverse: bool) -> list[dict] | None:
    """Retrieves patient records sorted by given parameter value in specified order."""
    if records_collection is None:
        return None

    return list(
        records_collection.find({}, {"_id": 0}).sort([(sort_by, -1 if reverse else 1)])
    )


def get_recent_admissions() -> list[dict] | None:
    """Retrieves patient records admitted within the last 24 hours."""
    if records_collection is None:
        return None

    try:
        ts_prev_day = datetime.now(tz=tz(TIMEZONE)) - timedelta(days=1)

        # NOTE: Query for records where date_of_admission is greater than or equal to 24 hours ago
        results = list(
            records_collection.find(
                {"date_of_admission": {"$gte": ts_prev_day.isoformat()}},
                {"_id": 0},
            )
        )
        return results
    except Exception as e:
        print(f"\nError fetching recent admissions: {e}\n")
        return None


# NOTE: UPDATE operations
def update_patient(pid: str, updates: PatientUpdate) -> dict | None:
    """Update a patient record by PID."""
    if records_collection is None:
        return None

    try:
        update_dict = updates.model_dump(exclude_unset=True)

        if "date_of_admission" in update_dict and update_dict["date_of_admission"]:
            update_dict["date_of_admission"] = str(update_dict["date_of_admission"])

        if "date_of_discharge" in update_dict and update_dict["date_of_discharge"]:
            update_dict["date_of_discharge"] = str(update_dict["date_of_discharge"])

        result = records_collection.update_one({"pid": pid}, {"$set": update_dict})

        if result.modified_count > 0:
            updated_doc = records_collection.find_one({"pid": pid})

            if updated_doc and "_id" in dict(updated_doc).keys():
                updated_doc["_id"] = str(updated_doc["_id"])
            return updated_doc

        return None
    except Exception as e:
        print(f"\nError updating patient record [PID : {pid}] : {e}\n")
        return None


# NOTE: DELETE operations
def delete_patient(pid: str) -> bool:
    """Delete a patient record by PID."""
    if records_collection is None:
        return False

    try:
        result = records_collection.delete_one({"pid": pid})
        return result.deleted_count > 0
    except Exception as e:
        print(f"\nError deleting patient record [PID: {pid}] : {e}\n")
        return False


# NOTE: ACTIVITY logging
activity_collection = None

if client is not None and db is not None:
    try:
        activity_collection = db[ACTIVITES_COLLECTION]
    except Exception as e:
        print(f"\nError setting up activities collection: {e}\n")


def log_activity(
    action_type: str,
    patient_id: str = "",
    patient_name: str = "",
    description: str = "",
) -> bool:
    """Log an activity to the activity collection."""
    if activity_collection is None:
        return False

    try:
        activity_doc = {
            "action_type": action_type,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "description": description,
            "timestamp": str(datetime.now(tz=tz(TIMEZONE)).isoformat()),
        }
        result = activity_collection.insert_one(activity_doc)
        return result.inserted_id is not None
    except Exception as e:
        print(f"\nError logging activity: {e}\n")
        return False


def get_recent_activities(limit: int = 10) -> list[dict] | None:
    """Retrieve recent activities sorted by timestamp (newest first)."""
    if activity_collection is None:
        return None

    try:
        results = list(
            activity_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        )
        return results
    except Exception as e:
        print(f"\nError fetching recent activities: {e}\n")
        return None
