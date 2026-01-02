from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from projects.models import Project
from tasks.models import Task, TaskSLA
from tasks.api.serializers import (
    TaskSerializer,
    TaskActivitySerializer,
    TaskSLASerializer,
)
from tasks.services.task_service import TaskService
from drf_yasg.utils import swagger_auto_schema
from config.swagger import TENANT_HEADER
from system.models import User


class TaskViewSet(ViewSet):
    """
    Single source of truth for Task APIs.
    """

    def get_user(self, request):
        return request.user

    @swagger_auto_schema(manual_parameters=[TENANT_HEADER])
    def list(self, request):
        user = self.get_user(request)
        project_id = request.query_params.get("project")
        tasks = TaskService.list_tasks(
            user=user,
            project_id=project_id,
        )
        return Response(TaskSerializer(tasks, many=True).data)

    @swagger_auto_schema(manual_parameters=[TENANT_HEADER])
    def create(self, request):
        user = self.get_user(request)
        project = get_object_or_404(
            Project,
            id=request.data["project"],
        )

        task = TaskService.create_task(
            user=user,
            project=project,
            title=request.data["title"],
            
        )
        return Response(TaskSerializer(task).data, status=201)

    @swagger_auto_schema(manual_parameters=[TENANT_HEADER])
    def partial_update(self, request, pk=None):
        user = self.get_user(request)
        task = get_object_or_404(Task, pk=pk)
        
        # Allow updating title, description, status, assigned_to
        allowed_fields = ['title', 'description', 'status', 'assigned_to']
        updates = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        TaskService.update_task(user=user, task=task, **updates)
        return Response(TaskSerializer(task).data)

    @swagger_auto_schema(manual_parameters=[TENANT_HEADER])
    @action(detail=True, methods=["get"], url_path="audit")
    def audit(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        activities = task.activities.all()
        return Response(
            TaskActivitySerializer(activities, many=True).data
        )

    @action(detail=True, methods=["get"])
    def sla(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        try:
            sla = task.sla
        except TaskSLA.DoesNotExist:
            # Return default SLA data if not exists
            sla_data = {
                "open_seconds": 0,
                "in_progress_seconds": 0,
                "blocked_seconds": 0,
                "updated_at": task.created_at,
            }
            return Response(sla_data)
        return Response(TaskSLASerializer(sla).data)