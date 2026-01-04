from django.conf import settings
from django.db import connections
from system.models import TenantDatabase

def ensure_tenant_db_registered(tenant) -> str:
    """
    Ensures tenant DB alias exists in current execution context.
    """
    alias = f"tenant_{tenant.id.hex}"

    if alias in connections.databases:
        return alias

    tenant_db = TenantDatabase.objects.get(tenant=tenant)

    # 🔑 Clone default DB settings (VERY IMPORTANT)
    base_config = settings.DATABASES["default"].copy()

    base_config.update(
        {
            "NAME": tenant_db.db_name,
            "USER": tenant_db.db_user,
            "PASSWORD": tenant_db.db_password,
            "HOST": tenant_db.db_host,
            "PORT": tenant_db.db_port,
        }
    )

    connections.databases[alias] = base_config

    return alias
