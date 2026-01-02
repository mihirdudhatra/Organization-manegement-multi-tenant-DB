from rest_framework.views import APIView
from rest_framework.response import Response
from system.models import Tenant
from system.api.serializers import TenantSerializer
from drf_yasg.utils import swagger_auto_schema
from config.swagger import TENANT_HEADER


class TenantListAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(responses={200: TenantSerializer(many=True)})
    def get(self, request):
        tenants = Tenant.objects.filter(is_active=True)
        return Response(TenantSerializer(tenants, many=True).data)
    