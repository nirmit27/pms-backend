"""
App. - Root
"""

from fastapi import FastAPI

from middleware.cors_setting import cors_middleware

from routes.health import router as health_router

from routes.add_records import router as admit_patient_router
from routes.fetch_records import router as fetch_records_router
from routes.update_records import router as update_records_router
from routes.rem_records import router as discharge_patient_router


# App.
app = FastAPI(
    title="Patient Management System 🏥",
    description="A microservice for managing patient records.",
    version="1.2.0",
)

# CORS
cors_middleware(app)

# Routers

# NOTE: Health checks
app.include_router(health_router)

# Record Mgmt.
app.include_router(fetch_records_router)
app.include_router(admit_patient_router)
app.include_router(update_records_router)
app.include_router(discharge_patient_router)
