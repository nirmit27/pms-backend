"""
RBAC roles
"""

# from dataclasses import dataclass
from enum import Enum


# TODO: Implement RBAC roles.


class Role(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    STAFF = "staff"
    PATIENT = "patient"
