from system.models import User

class Permissions:
    """
    Centralized permission management for the application.
    """

    # Define permissions as sets of allowed roles
    CREATE_TASK = {"ADMIN", "MANAGER", "MEMBER"}
    UPDATE_TASK_STATUS = {"ADMIN", "MANAGER", "MEMBER"}
    DELETE_TASK = {"ADMIN"}

    CREATE_PROJECT = {"ADMIN", "MANAGER"}
    UPDATE_PROJECT = {"ADMIN", "MANAGER"}
    DELETE_PROJECT = {"ADMIN"}

    CREATE_USER = {"ADMIN", "MANAGER"}
    UPDATE_USER = {"ADMIN"}
    DELETE_USER = {"ADMIN"}

    @staticmethod
    def has_permission(user: User, permission: set) -> bool:
        """
        Check if user has the required permission based on their role.
        """
        if not user or not user.is_authenticated:
            return False
        return user.role in permission

    @staticmethod
    def can_create_task(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.CREATE_TASK)

    @staticmethod
    def can_update_task_status(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.UPDATE_TASK_STATUS)

    @staticmethod
    def can_delete_task(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.DELETE_TASK)

    @staticmethod
    def can_create_project(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.CREATE_PROJECT)

    @staticmethod
    def can_update_project(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.UPDATE_PROJECT)

    @staticmethod
    def can_delete_project(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.DELETE_PROJECT)

    @staticmethod
    def can_create_user(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.CREATE_USER)

    @staticmethod
    def can_update_user(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.UPDATE_USER)

    @staticmethod
    def can_delete_user(user: User) -> bool:
        return Permissions.has_permission(user, Permissions.DELETE_USER)