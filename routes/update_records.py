"""
Update records

- Router for updating patient records
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import get_current_user, require_permission
from models.models import PatientUpdate, User
from models.permissions import Permission
from models.roles import Role
from services.db import update_patient, log_activity

router = APIRouter(prefix="/patient", tags=["Patients"])


@router.put(
    "/update", dependencies=[Depends(require_permission(Permission.UPDATE_PATIENT))]
)
def update_handler(
    updated_patient_data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        # Normalize email if present
        if "email" in updated_patient_data and updated_patient_data["email"]:
            updated_patient_data["email"] = (
                str(updated_patient_data["email"]).strip().lower()
            )

        temp: PatientUpdate = PatientUpdate(**updated_patient_data)

        if not temp.pid:
            raise HTTPException(
                status_code=400, detail="Missing 'pid' value in request."
            )

        # NOTE: Patients can only update their own record
        if current_user.role == Role.PATIENT:
            from services.db import get_patient_by_id

            existing = get_patient_by_id(temp.pid)
            if isinstance(existing, dict):
                existing_email = str(existing.get("email", "")).strip().lower()
                user_email = (current_user.email or "").strip().lower()
                if existing_email != user_email:
                    raise HTTPException(
                        status_code=403,
                        detail="You can only update your own patient record.",
                    )

        updated_record = update_patient(temp.pid, temp)
        if updated_record:
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
