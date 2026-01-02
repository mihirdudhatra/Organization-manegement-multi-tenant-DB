from django.core.exceptions import PermissionDenied
from django.utils import timezone
from typing import Optional, Dict, Any

from tasks.models import Task, TaskSLA
from tasks.services.task_activity_service import TaskActivityService
from projects.models import Project
from config.permissions import Permissions
from system.tenant_context import set_current_tenant_db as set_current_tenant
from system.models import User

# Import Celery tasks (created in analytics.tasks)
from analytics.tasks import generate_project_snapshot
from tasks.notifications import notify_assignment, notify_status_change

class TaskService:
    ALLOWED_TRANSITIONS = {
        Task.Status.OPEN: [Task.Status.IN_PROGRESS],
        Task.Status.IN_PROGRESS: [Task.Status.BLOCKED, Task.Status.DONE],
        Task.Status.BLOCKED: [Task.Status.IN_PROGRESS],
    }

    @staticmethod
    def get_task(*, user, task_id):
        set_current_tenant(user.tenant)
        return Task.objects.using('tenant').get(id=task_id, is_deleted=False)

    @staticmethod
    def create_task(*, user, project: Project, title: str, description: str) -> Task:
        if not Permissions.can_create_task(user):
            raise PermissionDenied("Not allowed to create tasks")

        set_current_tenant(user.tenant)

        task = Task.objects.using('tenant').create(
            project=project, 
            title=title,
            description = description
        )

        TaskActivityService.log(
            task=task,
            action="CREATE",
            user=user,
        )

        # Initialize SLA tracking for the task
        TaskSLA.objects.using('tenant').create(
            task=task,
            last_status=task.status,
            last_status_changed_at=timezone.now(),
            open_seconds=0,
            in_progress_seconds=0,
            blocked_seconds=0,
        )

        # Trigger async analytics update for the project (idempotent)
        try:
            generate_project_snapshot.delay(project.id)
        except Exception:
            # Do not fail the request if analytics worker is unavailable
            pass

        return task
    
    @staticmethod
    def list_tasks(*, user, project_id=None):
        set_current_tenant(user.tenant)

        qs = Task.objects.using('tenant').filter(is_deleted=False)

        if project_id:
            qs = qs.filter(project_id=project_id)

        return qs.order_by("-created_at")

    @staticmethod
    def update_task(*, user, task: Task, **updates) -> Task:
        if not Permissions.can_update_task_status(user):  # Assuming same permission for updates
            raise PermissionDenied("Not allowed to update tasks")

        set_current_tenant(user.tenant)
        old_values = {}

        # Handle status change specially to update SLA and emit background jobs
        if 'status' in updates:
            new_status = updates['status']

            # Idempotent: no-op if same status
            if new_status == task.status:
                return task

            # Validate allowed transition
            if new_status not in TaskService.ALLOWED_TRANSITIONS.get(task.status, []):
                raise ValueError("Invalid status transition")

            # record old value and set
            old_values['status'] = task.status
            task.status = new_status

            # Update SLA timings
            now = timezone.now()
            try:
                sla = task.sla
            except TaskSLA.DoesNotExist:
                sla = TaskSLA.objects.create(
                    task=task,
                    last_status=old_values['status'],
                    last_status_changed_at=now,
                )

            # compute elapsed seconds for previous status
            elapsed = int((now - sla.last_status_changed_at).total_seconds()) if sla.last_status_changed_at else 0

            if sla.last_status == Task.Status.OPEN:
                sla.open_seconds += elapsed
            elif sla.last_status == Task.Status.IN_PROGRESS:
                sla.in_progress_seconds += elapsed
            elif sla.last_status == Task.Status.BLOCKED:
                sla.blocked_seconds += elapsed

            sla.last_status = new_status
            sla.last_status_changed_at = now
            sla.save()

        # Handle other updatable fields
        for field in ['title', 'description', 'assigned_to']:
            if field in updates:
                old_values[field] = getattr(task, field)
                setattr(task, field, updates[field])

        task.save()

        # Log the update or status change
        if old_values:
            action = "STATUS_CHANGE" if 'status' in old_values else "UPDATE"
            TaskActivityService.log(
                task=task,
                action=action,
                user=user,
                old_value=str(old_values),
                new_value=str(updates),
            )

            # Fire notifications asynchronously for relevant changes
            try:
                if 'assigned_to' in old_values and task.assigned_to is not None:
                    # Notify when a new assignee is set or changed
                    if old_values['assigned_to'] is None or old_values['assigned_to'] != task.assigned_to:
                        new_assignee = task.assigned_to
                        if new_assignee:
                            notify_assignment.delay(new_assignee.id, task.id)

                if 'status' in old_values:
                    notify_status_change.delay(task.id, old_values['status'], task.status)
            except Exception:
                # best-effort, never fail the request
                pass

        # Trigger async analytics update for the project (best-effort)
        try:
            generate_project_snapshot.delay(task.project.id)
        except Exception:
            pass

        return task

    @staticmethod
    def soft_delete(*, user: User, task: Task) -> None:
        if not Permissions.can_delete_task(user):
            raise PermissionDenied("Only admin can delete")

        set_current_tenant(user.tenant)

        task.is_deleted = True
        task.save(update_fields=["is_deleted"])

        TaskActivityService.log(
            task=task,
            action="DELETE",
            user=user,
        )
