"""
Fetch records

- Router for fetching patient records
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException, Query

from auth.dependencies import get_current_user, require_permission
from models.models import User
from models.permissions import Permission
from models.roles import Role
from utils.utils import sort_fields
from services.db import (
    get_all_patients,
    get_patient_by_id,
    get_patients_by_name,
    get_recent_admissions,
    sort_records_by_param,
    get_patients_by_name_fuzzy,
)

router = APIRouter(prefix="/records", tags=["Fetch_Records"])


def filter_records_for_user(records: list[dict] | None, current_user: User):
    if records is None:
        return None

    if current_user.role != Role.PATIENT:
        return records

    user_email = (current_user.email or "").strip().lower()
    return [
        record
        for record in records
        if str(record.get("email", "")).strip().lower() == user_email
    ]


@router.get("/me", dependencies=[Depends(require_permission(Permission.VIEW_PATIENT))])
def view_my_record(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Return the patient record associated with the currently authenticated patient.
    Restricted to the PATIENT role.
    """
    if current_user.role != Role.PATIENT:
        raise HTTPException(
            status_code=403,
            detail="Only patients can access this endpoint.",
        )

    data: list[dict] | None = get_all_patients()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient records.")

    data = filter_records_for_user(data, current_user)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="No patient record is associated with your account yet.",
        )

    return data[0]


@router.get("/", dependencies=[Depends(require_permission(Permission.VIEW_PATIENT))])
def view(current_user: Annotated[User, Depends(get_current_user)]):
    data: list[dict] | None = get_all_patients()

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient records.")

    data = filter_records_for_user(data, current_user)

    if len(data) == 0:
        return []

    return list(data)


@router.get(
    "/id/{patient_id}",
    dependencies=[Depends(require_permission(Permission.VIEW_PATIENT))],
)
def view_patient_by_id(
    patient_id: str = Path(
        ..., description="Patient ID in the database.", examples=["P001"]
    ),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    data: dict | str | None = get_patient_by_id(patient_id)

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient record.")

    if isinstance(data, str):
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{patient_id}' not found."
        )

    if current_user.role == Role.PATIENT:
        user_email = (current_user.email or "").strip().lower()
        record_email = str(data.get("email", "")).strip().lower()
        if record_email != user_email:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own patient record.",
            )

    return data


@router.get(
    "/name", dependencies=[Depends(require_permission(Permission.VIEW_PATIENT))]
)
def view_patients_by_name(
    patient_name: str = Query(
        ..., description="Patient name in the database.", examples=["John Doe"]
    ),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    data: list[dict] | None = get_patients_by_name(patient_name)

    if data is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch patient record(s)."
        )

    data = filter_records_for_user(data, current_user)

    if data == []:
        raise HTTPException(
            status_code=404,
            detail=f"Patient(s) with name : '{patient_name}' not found.",
        )

    return data


@router.get(
    "/name/search", dependencies=[Depends(require_permission(Permission.VIEW_PATIENT))]
)
def search_patients_by_name_fuzzy(
    patient_name: str = Query(
        ...,
        description="Patient name (partial match with fuzzy search).",
        examples=["John"],
    ),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Fuzzy search for patients by name.
    Returns partial matches sorted by relevance (exact matches first).
    Case-insensitive matching.
    """
    if not patient_name or not patient_name.strip():
        raise HTTPException(status_code=400, detail="Patient name cannot be empty.")

    data: list[dict] | None = get_patients_by_name_fuzzy(patient_name)

    if data is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch patient record(s)."
        )

    data = filter_records_for_user(data, current_user)
    return data


@router.get(
    "/recent-admissions",
    dependencies=[Depends(require_permission(Permission.VIEW_PATIENT))],
)
def get_recent_admissions_count(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Returns the number of patients admitted in the last 24 hours.
    """
    data: list[dict] | None = get_recent_admissions()

    if data is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch recent patient admissions."
        )

    data = filter_records_for_user(data, current_user)
    return {"count": len(data)}


@router.get(
    "/sort", dependencies=[Depends(require_permission(Permission.VIEW_PATIENT))]
)
def sort_patients(
    sort_by: str = Query(
        ...,
        description="Sort records on the basis of height, weight or bmi.",
    ),
    order: str = Query("asc", description="Sort in ascending or descending order."),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    if sort_by not in sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sorting field. Select from {', '.join(sort_fields)}.",
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sorting order. Select either 'asc' or 'desc'.",
        )

    data: list[dict] | None = sort_records_by_param(
        sort_by, True if order == "desc" else False
    )

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient records.")

    data = filter_records_for_user(data, current_user)

    if data == []:
        return {"message": "No patient records found."}

    return data
