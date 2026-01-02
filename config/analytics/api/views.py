from rest_framework.views import APIView
from rest_framework.response import Response
from analytics.models import AnalyticsSnapshot
from analytics.api.serializers import AnalyticsSnapshotSerializer


class ProjectAnalyticsAPIView(APIView):
    def get(self, request, project_id):
        snapshots = AnalyticsSnapshot.objects.filter(
            project_id=project_id
        )
        return Response(
            AnalyticsSnapshotSerializer(snapshots, many=True).data
        )
