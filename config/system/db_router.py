# from system.tenant_context import get_current_tenant


# class TenantDatabaseRouter:
#     SYSTEM_APPS = {"users"}

#     def db_for_read(self, model, **hints):
#         if model._meta.app_label in self.SYSTEM_APPS:
#             return "default"
#         return "tenant" if get_current_tenant() else "default"

#     def db_for_write(self, model, **hints):
#         if model._meta.app_label in self.SYSTEM_APPS:
#             return "default"
#         return "tenant" if get_current_tenant() else "default"

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         if app_label in self.SYSTEM_APPS:
#             return db == "default"
#         return db == "tenant"
# from system.tenant_context import get_current_tenant_db
#
#
# class TenantDatabaseRouter:
#     SYSTEM_APPS = {"system_user"}
#
#     def db_for_read(self, model, **hints):
#         if getattr(model, "_tenant_model", False):
#             return get_current_tenant_db()
#         return "default"
#
#     def db_for_write(self, model, **hints):
#         if getattr(model, "_tenant_model", False):
#             return get_current_tenant_db()
#         return "default"
# system/db_router.py
from typing import Optional
from django.conf import settings


class TenantDatabaseRouter:
    """
    Routes:
    - system apps → master DB
    - tenant apps → tenant DB
    """

    def db_for_read(self, model, **hints) -> Optional[str]:
        if model._meta.app_label in settings.SYSTEM_APPS:
            return "default"
        return hints.get("database")

    def db_for_write(self, model, **hints) -> Optional[str]:
        if model._meta.app_label in settings.SYSTEM_APPS:
            return "default"
        return hints.get("database")

    def allow_relation(self, obj1, obj2, **hints) -> bool:
        return obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, **hints) -> bool:
        if app_label in settings.SYSTEM_APPS:
            return db == "default"
        if app_label in settings.TENANT_APPS:
            return db != "default"
        return False
