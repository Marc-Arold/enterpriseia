from databaseHandler import (
    get_roles_for_user,
    get_permissions_for_role
)
from ..models.user import User
from ..models.permissions import Permission

class AccessControl:
    """
    Checks if a user is allowed to perform certain actions based on
    roles and permissions stored in the database.
    """
    def user_has_permission(self, user: User, permission_name: str) -> bool:
        """
        Returns True if the user has a specific permission (directly or via roles).
        Fetches roles from the DB, then their permissions.
        """
        if not user:
            return False

        # Get the list of roles for the user.
        roles_data = get_roles_for_user(user.user_id)
        # Each role is assumed to be a tuple: (role_id, role_name, role_description, ...)
        for role in roles_data:
            role_id = role[0]  # Using tuple index since role is a tuple
            perms_data = get_permissions_for_role(role_id)
            # Each permission is assumed to be a tuple: (permission_id, permission_name, permission_description)
            for p in perms_data:
                # p[1] is the permission name.
                if p[1] == permission_name:
                    return True

        return False
