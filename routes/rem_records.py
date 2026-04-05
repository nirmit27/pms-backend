"""
Remove records

- Router for removing patient records
"""

from fastapi import APIRouter, HTTPException

from services.db import delete_patient


router = APIRouter(prefix="/discharge", tags=["Discharge_Patients"])


@router.delete("/{pid}")
def delete_handler(pid: str):
    try:
        if delete_patient(pid):
            return {"message": f"Patient [{pid}] has been discharged."}
        raise HTTPException(
            status_code=404, detail=f"Patient with ID : '{pid}' not found."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")
