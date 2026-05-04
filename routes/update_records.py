"""
Update records

- Router for updating patient records
"""

from fastapi import APIRouter, HTTPException

from models.models import PatientUpdate
from services.db import update_patient, log_activity

router = APIRouter(prefix="/patient", tags=["Patients"])


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
            # Log the activity
            log_activity(
                action_type="patient_updated",
                patient_id=temp.pid,
                patient_name=updated_record.get("name", "Unknown"),
                description="Patient information modified",
            )
            return {
                "message": f"Patient record [{temp.pid}] updated.",
                "updated_record": updated_record,
            }
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{temp.pid}' not found."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
