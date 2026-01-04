from system.db_registry import ensure_tenant_db_registered
from system.tenant_context import set_current_tenant_db


class TenantDatabaseMiddleware:
    """
    Registers tenant DB per request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated and hasattr(user, "tenant"):
            alias = ensure_tenant_db_registered(user.tenant)
            set_current_tenant_db(alias)

        return self.get_response(request)
