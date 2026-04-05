"""
Patient management
"""

from fastapi import APIRouter, Path, HTTPException, Query

from models.models import Patient, PatientUpdate
from utils.utils import sort_fields, new_pid
from services.db import (
    add_patient,
    delete_patient,
    update_patient,
    get_all_patients,
    get_patient_by_id,
    get_patients_by_name,
    sort_records_by_param,
)

router = APIRouter(prefix="/patient", tags=["Patients"])


@router.get("/")
def view():
    data: list[dict] | None = get_all_patients()

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient records.")

    if len(data) == 0:
        return {"message": "No patient records found."}

    data.append({"Number of patients": len(data)})
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


@router.get("/sort")
def sort_patients(
    sort_by: str = Query(
        ...,
        description="Sort records on the basis of height, weight or bmi.",
    ),
    order: str = Query("asc", description="Sort in ascending or descending order."),
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

    if data == []:
        return {"message": "No patient records found."}

    return data


@router.post("/new")
def new_patient(patient_data: dict):
    try:
        npid: str | None = new_pid()

        if npid is None:
            raise Exception("Could not generate a new patient ID.")

        patient_data["pid"] = npid
        temp: Patient = Patient(**patient_data)

        res = add_patient(temp)
        if res is None:
            raise HTTPException(
                status_code=500, detail=f"Failed to add patient record."
            )
        else:
            return {"message": f"Patient record added successfully. [PID : {npid}]"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")


@router.put("/update")
def update_handler(updated_patient_data: dict):
    try:
        temp: PatientUpdate = PatientUpdate(**updated_patient_data)

        if not temp.pid:
            raise HTTPException(
                status_code=400, detail="Missing 'pid' value in request."
            )

        updated_record = update_patient(temp.pid, temp)
        if updated_record:
            return {
                "message": f"Patient record [{temp.pid}] updated.",
                "updated_record": updated_record,
            }
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{temp.pid}' not found."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")


@router.delete("/{pid}")
def delete_handler(pid: str):
    try:
        if delete_patient(pid):
            return {"message": f"Patient record [{pid}] has been deleted."}
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{pid}' not found."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
