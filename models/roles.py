"""
RBAC roles
"""

# from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    STAFF = "staff"
    PATIENT = "patient"
