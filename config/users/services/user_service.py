from system.models import User
from django.core.exceptions import PermissionDenied
from config.permissions import Permissions
from system.tenant_context import get_current_tenant_db as get_current_tenant, set_current_tenant_db as set_current_tenant
from system.db_registry import ensure_tenant_db_registered

class UserService:

    @staticmethod
    def list_users(*, user):
        base_qs = User.objects.filter(tenant_id=user.tenant.id)

        if user.role == User.Role.ADMIN:
            return base_qs

        if user.role == User.Role.MANAGER:
            return base_qs.filter(
                role__in=[User.Role.MANAGER, User.Role.MEMBER]
            )
        return base_qs.filter(role=User.Role.MEMBER)

    @staticmethod
    def create_user(*, user, username: str, email: str, password: str, role: str) -> User:
        if not Permissions.can_create_user(user):
            raise PermissionDenied("Not allowed to create users")

        # Ensure the created user is associated with the current tenant
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            tenant=user.tenant,
        )

    @staticmethod
    def update_user(*, user, target_user: User, **updates) -> User:
        if not Permissions.can_update_user(user):
            raise PermissionDenied("Not allowed to update users")

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