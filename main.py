"""
Application - Root
"""

from fastapi import FastAPI
from middleware.cors_setting import cors_middleware
from routes.health import router as health_router
from routes.patients import router as patients_router


# App. config.
app = FastAPI(
    title="Patient Management System",
    description="Microservice for managing patient records",
    version="1.2.0",
)

# CORS
cors_middleware(app)

# Routers
app.include_router(health_router)
app.include_router(patients_router)
