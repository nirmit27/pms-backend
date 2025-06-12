"""Database integration"""

from os import environ
from dotenv import load_dotenv
from pymongo import MongoClient, errors

from models import Patient, PatientUpdate

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


# CREATE operation
def add_patient(p_data: Patient) -> dict | None:
    """Creating a new patient record."""
    if collection is None:
        return None

    try:
        temp: dict = p_data.model_dump().copy()

        if "date_of_admission" in temp.keys() and temp["date_of_admission"]:
            temp["date_of_admission"] = str(temp["date_of_admission"])

        if "date_of_discharge" in temp.keys() and temp["date_of_discharge"]:
            temp["date_of_discharge"] = str(temp["date_of_discharge"])

        result = collection.insert_one(temp)
        return temp if result.inserted_id else None

    except Exception as e:
        print(f"\nError adding patient record : {e}\n")
        return None


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
def update_patient(pid: str, updates: PatientUpdate) -> dict | None:
    """Update a patient record by PID."""
    if collection is None:
        return None

    try:
        update_dict = updates.model_dump(exclude_unset=True)

        if "date_of_admission" in update_dict and update_dict["date_of_admission"]:
            update_dict["date_of_admission"] = str(update_dict["date_of_admission"])

        if "date_of_discharge" in update_dict and update_dict["date_of_discharge"]:
            update_dict["date_of_discharge"] = str(update_dict["date_of_discharge"])

        result = collection.update_one({"pid": pid}, {"$set": update_dict})

        if result.modified_count > 0:
            updated_doc = collection.find_one({"pid": pid})

            if updated_doc and "_id" in dict(updated_doc).keys():
                updated_doc["_id"] = str(updated_doc["_id"])
            return updated_doc

        return None
    except Exception as e:
        print(f"\nError updating patient record [PID : {pid}] : {e}\n")
        return None


# DELETE operations
def delete_patient(pid: str) -> bool:
    """Delete a patient record by PID."""
    if collection is None:
        return False

    try:
        result = collection.delete_one({"pid": pid})
        return result.deleted_count > 0
    except Exception as e:
        print(f"\nError deleting patient record [PID: {pid}] : {e}\n")
        return False
