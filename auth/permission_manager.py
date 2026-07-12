"""
Permission helpers for RBAC.
"""

from models.permissions import Permission, ROLE_PERMISSIONS
from models.roles import Role


def has_permission(role: Role | str, permission: Permission | str) -> bool:
    """Return whether a role is allowed to perform a permission."""
    normalized_role = role if isinstance(role, Role) else Role(str(role))
    normalized_permission = (
        permission
        if isinstance(permission, Permission)
        else Permission(str(permission))
    )

    return normalized_permission in ROLE_PERMISSIONS.get(normalized_role, [])
