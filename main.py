"""Root of the microservice"""

from os import environ
from dotenv import load_dotenv

from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from utils import sort_fields, new_pid
from models import Patient, PatientUpdate

from datetime import datetime
from pytz import timezone as tz

from db import (
    add_patient,
    delete_patient,
    update_patient,
    get_all_patients,
    get_patient_by_id,
    get_patients_by_name,
    sort_records_by_param,
)

# Env. vars.
load_dotenv()

TIMEZONE: str = environ.get("TIMEZONE", "Asia/Kolkata")
FRONTEND_URL: str = environ.get("FRONTEND_URL", "http://localhost:5173")

# App. config.
app = FastAPI()

# CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Route handlers


@app.get("/")
def index():
    return {"message": "Patient Management System 🏥"}


@app.get("/about")
def about():
    return {"message": "This is a microservice for managing patient records."}


@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "time": f"{datetime.now(tz=tz(TIMEZONE)).isoformat()}",
    }


@app.get("/view")
def view():
    data: list[dict] | None = get_all_patients()

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch patient records.")

    if len(data) == 0:
        return {"message": "No patient records found."}

    data.append({"Number of patients": len(data)})
    return list(data)


@app.get("/patient/id/{patient_id}")
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


@app.get("/patients/name")
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


@app.get("/patients/sort")
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


@app.post("/new-patient")
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


@app.put("/update-patient")
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


@app.delete("/delete-patient/{pid}")
def delete_handler(pid: str):
    try:
        if delete_patient(pid):
            return {"message": f"Patient record [{pid}] has been deleted."}
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{pid}' not found."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
