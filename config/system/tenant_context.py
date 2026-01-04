# from threading import local
# from typing import Optional
# from system.models import Tenant

# _thread_locals = local()


# def set_current_tenant(tenant: Optional[Tenant]) -> None:
#     _thread_locals.tenant = tenant


# def get_current_tenant() -> Optional[Tenant]:
#     return getattr(_thread_locals, "tenant", None)
# system/tenant_context.py
# from contextvars import ContextVar
# from typing import Optional

# _current_tenant_db: ContextVar[Optional[str]] = ContextVar(
#     "current_tenant_db",
#     default=None,
# )

# def set_current_tenant_db(db_alias: Optional[str]) -> None:
#     _current_tenant_db.set(db_alias)

# def get_current_tenant_db() -> Optional[str]:
#     return _current_tenant_db.get()
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Optional
from django.db import connections

# Holds the current tenant DB alias for the active request/task
_current_tenant_db: ContextVar[Optional[str]] = ContextVar(
    "current_tenant_db",
    default=None,
)


def set_current_tenant_db(db_alias: Optional[str]) -> None:
    _current_tenant_db.set(db_alias)


def get_current_tenant_db() -> Optional[str]:
    return _current_tenant_db.get()


@contextmanager
def tenant_db_context(db_alias: str):
    try:
        yield connections[db_alias]
    finally:
        connections[db_alias].close()
