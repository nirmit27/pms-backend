"""
Add records

- Router for adding patient records
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import get_current_user, require_permission
from models.models import Patient, User
from models.permissions import Permission
from utils.utils import new_pid
from services.db import add_patient, log_activity

router = APIRouter(prefix="/admit", tags=["Admit_Patients"])


@router.post("", dependencies=[Depends(require_permission(Permission.ADMIT_PATIENT))])
def new_patient(
    patient_data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        npid: str | None = new_pid()

        if npid is None:
            raise HTTPException(
                status_code=500,
                detail="Could not generate a new patient ID.",
            )

        # Normalize email to lowercase/trimmed so it can be matched against
        # the authenticated user's email in /records/me
        if "email" in patient_data and patient_data["email"]:
            patient_data["email"] = str(patient_data["email"]).strip().lower()

        patient_data["pid"] = npid
        temp: Patient = Patient(**patient_data)

        res = add_patient(temp)
        if res is None:
            raise HTTPException(status_code=500, detail="Failed to add patient record.")

        # Log the activity
        log_activity(
            action_type="patient_admitted",
            patient_id=npid,
            patient_name=patient_data.get("name", "Unknown"),
            description="Patient record created in system",
        )
        return {"message": f"Patient admitted successfully. [PID : {npid}]"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
