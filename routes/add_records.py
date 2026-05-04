"""
Add records

- Router for adding patient records
"""

from fastapi import APIRouter, HTTPException

from models.models import Patient
from utils.utils import new_pid
from services.db import add_patient, log_activity

router = APIRouter(prefix="/admit", tags=["Admit_Patients"])


@router.post("")
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
            # Log the activity
            log_activity(
                action_type="patient_admitted",
                patient_id=npid,
                patient_name=patient_data.get("name", "Unknown"),
                description=f"Patient record created in system",
            )
            return {"message": f"Patient admitted successfully. [PID : {npid}]"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
