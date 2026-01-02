from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

TENANT_HEADER = openapi.Parameter(
    name="X-Tenant-ID",
    in_=openapi.IN_HEADER,
    description="Tenant UUID",
    type=openapi.TYPE_STRING,
    required=True,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Multi-Tenant Task Platform API",
        default_version="v1",
        description="Scalable Multi-Tenant Task & Analytics Platform",
    ),
    public=True,
    permission_classes=[AllowAny],
)
