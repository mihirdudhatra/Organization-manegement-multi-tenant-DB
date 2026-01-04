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
from rest_framework import status
from system.db_registry import ensure_tenant_db_registered


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
        db = ensure_tenant_db_registered(user.tenant)

        project = get_object_or_404(
            Project.objects.using(db),
            id=request.data.get("project"),
        )

        task = TaskService.create_task(
            user=user,
            project=project,
            title=request.data.get("title"),
            description=request.data.get("description", ""),
        )

        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(manual_parameters=[TENANT_HEADER])
    def partial_update(self, request, pk=None):
        user = self.get_user(request)
        db = ensure_tenant_db_registered(user.tenant)

        task = get_object_or_404(
            Task.objects.using(db),
            pk=pk,
            is_deleted=False,
        )

        allowed_fields = {"title", "description", "status", "assigned_to"}
        updates = {
            k: v for k, v in request.data.items()
            if k in allowed_fields
        }

        updated_task = TaskService.update_task(
            user=user,
            task=task,
            **updates,
        )

        return Response(TaskSerializer(updated_task).data)


    @swagger_auto_schema(manual_parameters=[TENANT_HEADER])
    @action(detail=True, methods=["get"])
    def audit(self, request, pk=None):
        user = self.get_user(request)
        db = ensure_tenant_db_registered(user.tenant)

        task = get_object_or_404(
            Task.objects.using(db),
            pk=pk,
        )

        activities = task.activities.all()
        return Response(
            TaskActivitySerializer(activities, many=True).data
        )

    @swagger_auto_schema(manual_parameters=[TENANT_HEADER])
    @action(detail=True, methods=["get"])
    def sla(self, request, pk=None):
        user = self.get_user(request)
        db = ensure_tenant_db_registered(user.tenant)

        task = get_object_or_404(
            Task.objects.using(db),
            pk=pk,
        )

        try:
            sla = task.sla
            return Response(TaskSLASerializer(sla).data)
        except TaskSLA.DoesNotExist:
            return Response(
                {
                    "open_seconds": 0,
                    "in_progress_seconds": 0,
                    "blocked_seconds": 0,
                    "updated_at": task.created_at,
                }
            )