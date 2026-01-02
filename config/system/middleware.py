from django.db import connections
from django.utils.deprecation import MiddlewareMixin
from system.models import TenantDatabase
from system.tenant_context import set_current_tenant_db
from django.http import HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser

# class TenantMiddleware(MiddlewareMixin):
#     """
#     Binds tenant DB connection per request/.
#     """

#     def process_request(self, request):
#         tenant_id = request.session.get("tenant_id") or request.headers.get("X-Tenant-ID")
#         if not tenant_id:
#             set_current_tenant(None)
#             return
        
#         try:
#             tenant_db = TenantDatabase.objects.select_related('tenant').get(tenant_id = tenant_id, tenant__is_active=True)
#         except TenantDatabase.DoesNotExist:
#             return HttpResponseForbidden("Invalid tenant.")
        
#         # Dynamically inject tenant Db config
#         connections.databases['tenant'] = {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': tenant_db.db_name,
#             'USER': tenant_db.db_user,
#             'PASSWORD': tenant_db.db_password,
#             'HOST': tenant_db.db_host,
#             'PORT': tenant_db.db_port,
#             'CONN_MAX_AGE': 60,
#             'ATOMIC_REQUESTS': False,
#             'AUTOCOMMIT': True,
#             'OPTIONS': {},
#             'TIME_ZONE': 'UTC',
#             'CONN_HEALTH_CHECKS': False,
#         }

#         set_current_tenant(tenant_db.tenant)

# def process_request(self, request):
#     ...
#     if request.user and not isinstance(request.user, AnonymousUser):
#         if request.user.is_authenticated:
#             # user DB already tenant-bound
#             pass
from rest_framework_simplejwt.authentication import JWTAuthentication
from system.models import TenantDatabase
from system.tenant_context import set_current_tenant_db
from django.http import HttpResponseForbidden


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        auth = self.jwt_auth.authenticate(request)

        if auth is None:
            return self.get_response(request)

        user, token = auth
        tenant_id = token.get("tenant_id")

        if not tenant_id:
            return HttpResponseForbidden("Tenant missing")

        try:
            tenant_db = TenantDatabase.objects.get(
                tenant_id=tenant_id,
                tenant__is_active=True,
            )
        except TenantDatabase.DoesNotExist:
            return HttpResponseForbidden("Invalid tenant")

        set_current_tenant_db(tenant_db.db_name)

        return self.get_response(request)

