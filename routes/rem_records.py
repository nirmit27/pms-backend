"""
Remove records

- Router for removing patient records
"""

from fastapi import APIRouter, HTTPException

from services.db import delete_patient, get_patient_by_id, log_activity

router = APIRouter(prefix="/discharge", tags=["Discharge_Patients"])


@router.delete("/{pid}")
def delete_handler(pid: str):
    try:
        # Get patient info before deletion for logging
        patient_info = get_patient_by_id(pid)
        patient_name = "Unknown"

        if patient_info and isinstance(patient_info, dict):
            patient_name = patient_info.get("name", "Unknown")

        if delete_patient(pid):
            # Log the discharge activity
            log_activity(
                action_type="patient_discharged",
                patient_id=pid,
                patient_name=patient_name,
                description="Patient record removed from system",
            )
            return {"message": f"Patient [{pid}] has been discharged."}
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{pid}' not found."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
