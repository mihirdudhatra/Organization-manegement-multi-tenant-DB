from rest_framework import serializers
from tasks.models import Task, TaskActivity, TaskSLA
from system.models import User

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
            "assigned_to",
            "created_at",
        ]


class TaskActivitySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()
    old_value = serializers.SerializerMethodField()
    new_value = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",read_only=True)

    class Meta:
        model = TaskActivity
        fields = (
            "id",
            "action",
            "old_value",
            "new_value",
            "performed_by_name",
            "created_at",
        )

    def _parse_value(self, value):
        """
        """
        if not value:
            return "-"

        try:
            parsed = ast.literal_eval(value)
            return ", ".join(f"{k}: {v}" for k, v in parsed.items())
        except Exception:
            return value

    def get_old_value(self, obj):
        return self._parse_value(obj.old_value)

    def get_new_value(self, obj):
        return self._parse_value(obj.new_value)

    def get_performed_by_name(self, obj):
        try:
            user = User.objects.get(id=obj.performed_by)
            return user.username
        except User.DoesNotExist:
            return "System"
class TaskSLASerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSLA
        fields = [
            "open_seconds",
            "in_progress_seconds",
            "blocked_seconds",
            "updated_at",
        ]
