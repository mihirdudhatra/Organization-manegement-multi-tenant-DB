from rest_framework import serializers
from analytics.models import AnalyticsSnapshot


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "date",
            "project_name",
            "tasks_open",
            "tasks_in_progress",
            "tasks_blocked",
            "tasks_done",
            "avg_completion_seconds",
            "tasks_created",
            "tasks_completed",
        ]
