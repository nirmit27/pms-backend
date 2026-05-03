"""
Fetch records

- Router for fetching patient records
"""

from fastapi import APIRouter, Path, HTTPException, Query

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


@router.get("/")
def view():
    data: list[dict] | None = get_all_patients()

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient records.")

    if len(data) == 0:
        return {"message": "No patient records found."}

    data.append({"Number of patient(s)": len(data)})
    return list(data)


@router.get("/id/{patient_id}")
def view_patient_by_id(
    patient_id: str = Path(
        ..., description="Patient ID in the database.", examples=["P001"]
    )
):
    data: dict | str | None = get_patient_by_id(patient_id)

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient record.")

    if isinstance(data, str) != 0:
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{patient_id}' not found."
        )

    return data


@router.get("/name")
def view_patients_by_name(
    patient_name: str = Query(
        ..., description="Patient name in the database.", examples=["John Doe"]
    )
):
    data: list[dict] | None = get_patients_by_name(patient_name)

    if data is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch patient record(s)."
        )

    if data == []:
        raise HTTPException(
            status_code=404,
            detail=f"Patient(s) with name : '{patient_name}' not found.",
        )

    return data


@router.get("/name/search")
def search_patients_by_name_fuzzy(
    patient_name: str = Query(
        ...,
        description="Patient name (partial match with fuzzy search).",
        examples=["John"],
    )
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

    # Return empty list instead of 404 for fuzzy search (for autocomplete UX)
    return data


@router.get("/recent-admissions")
def get_recent_admissions_count():
    """
    Returns the number of patients admitted in the last 24 hours.
    """
    data: list[dict] | None = get_recent_admissions()

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch recent patient admissions.")

    return {"count": len(data)}


@router.get("/sort")
def sort_patients(
    sort_by: str = Query(
        ...,
        description="Sort records on the basis of height, weight or bmi.",
    ),
    order: str = Query("asc", description="Sort in ascending or descending order."),
):
    # NOTE: Debugging
    # print(sort_by, order)

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

    if data == []:
        return {"message": "No patient records found."}

    return data
