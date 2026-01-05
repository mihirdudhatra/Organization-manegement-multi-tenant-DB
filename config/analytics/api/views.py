from rest_framework.views import APIView
from rest_framework.response import Response
from analytics.models import AnalyticsSnapshot
from analytics.api.serializers import AnalyticsSnapshotSerializer
from system.db_registry import ensure_tenant_db_registered


class ProjectAnalyticsAPIView(APIView):
    def get(self, request, project_id):
        user = request.user
        db = ensure_tenant_db_registered(user.tenant)

        snapshots = AnalyticsSnapshot.objects.using(db).filter(
            project_id=project_id
        ).order_by("-date")

        return Response(
            AnalyticsSnapshotSerializer(snapshots, many=True).data
        )
