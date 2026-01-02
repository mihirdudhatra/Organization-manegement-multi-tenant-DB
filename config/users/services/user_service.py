from system.models import User
from django.core.exceptions import PermissionDenied
from config.permissions import Permissions
from system.tenant_context import get_current_tenant_db as get_current_tenant


class UserService:

    @staticmethod
    def list_users(*, user):
        if not Permissions.can_create_user(user):  # Only admins can see users
            raise PermissionDenied("Not allowed to view users")
        tenant = get_current_tenant()
        if not tenant:
            raise PermissionDenied("No tenant context")
        if user.role != 'ADMIN' and tenant != user.tenant:
            raise PermissionDenied("Not allowed to access other tenants")
        return User.objects.filter(tenant=tenant)

    @staticmethod
    def create_user(*, user, username: str, email: str, password: str, role: str) -> User:
        if not Permissions.can_create_user(user):
            raise PermissionDenied("Not allowed to create users")

        tenant = get_current_tenant()
        if not tenant:
            raise PermissionDenied("No tenant context")
        if user.role != 'ADMIN' and tenant != user.tenant:
            raise PermissionDenied("Not allowed to create users in other tenants")

        # Ensure the created user is associated with the current tenant
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            tenant=tenant,
        )

    @staticmethod
    def update_user(*, user, target_user: User, **updates) -> User:
        if not Permissions.can_update_user(user):
            raise PermissionDenied("Not allowed to update users")

        tenant = get_current_tenant()
        if not tenant or target_user.tenant != tenant:
            raise PermissionDenied("Not allowed to update users in other tenants")
        if user.role != 'ADMIN' and tenant != user.tenant:
            raise PermissionDenied("Not allowed to update users in other tenants")

        for key, value in updates.items():
            if key == 'password':
                target_user.set_password(value)
            else:
                setattr(target_user, key, value)
        target_user.save()
        return target_user

    @staticmethod
    def delete_user(*, user, target_user: User) -> None:
        if not Permissions.can_delete_user(user):
            raise PermissionDenied("Not allowed to delete users")

        tenant = get_current_tenant()
        if not tenant or target_user.tenant != tenant:
            raise PermissionDenied("Not allowed to delete users in other tenants")
        if user.role != 'ADMIN' and tenant != user.tenant:
            raise PermissionDenied("Not allowed to delete users in other tenants")

        target_user.delete()