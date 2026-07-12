"""
Models - RBAC Permissions
"""

from enum import Enum
from models.roles import Role


class Permission(str, Enum):
    """Permissions for different CRUD ops."""

    VIEW_PATIENT = "view_patient"
    ADMIT_PATIENT = "admit_patient"
    DISCHARGE_PATIENT = "discharge_patient"
    UPDATE_PATIENT = "update_patient"
    VIEW_ACTIVITIES = "view_activities"
    MANAGE_USERS = "manage_users"


# NOTE: Role-based permission mappings
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.VIEW_PATIENT,
        Permission.ADMIT_PATIENT,
        Permission.DISCHARGE_PATIENT,
        Permission.UPDATE_PATIENT,
        Permission.VIEW_ACTIVITIES,
        Permission.MANAGE_USERS,
    ],
    Role.DOCTOR: [
        Permission.VIEW_PATIENT,
        Permission.ADMIT_PATIENT,
        Permission.DISCHARGE_PATIENT,
        Permission.UPDATE_PATIENT,
        Permission.VIEW_ACTIVITIES,
    ],
    Role.STAFF: [
        Permission.VIEW_PATIENT,
        Permission.UPDATE_PATIENT,
        Permission.VIEW_ACTIVITIES,
    ],
    Role.PATIENT: [
        Permission.VIEW_PATIENT,
    ],
}
