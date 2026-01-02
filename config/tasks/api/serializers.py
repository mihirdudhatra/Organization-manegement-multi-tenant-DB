from rest_framework import serializers
from tasks.models import Task, TaskActivity, TaskSLA

class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "project_name",
            "title",
            "description",
            "status",
            "assigned_to_id",
            "created_at",
        ]


class TaskActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskActivity
        fields = [
            "id",
            "action",
            "old_value",
            "new_value",
            "comment",
            "performed_by_id",
            "created_at",
        ]

class TaskSLASerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSLA
        fields = [
            "open_seconds",
            "in_progress_seconds",
            "blocked_seconds",
            "updated_at",
        ]
