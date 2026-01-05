from django.core.exceptions import PermissionDenied
from django.utils import timezone
from typing import Optional, Dict, Any

from tasks.models import Task, TaskSLA
from tasks.services.task_activity_service import TaskActivityService
from projects.models import Project
from config.permissions import Permissions
from system.tenant_context import set_current_tenant_db as set_current_tenant
from system.models import User
from system.db_registry import ensure_tenant_db_registered
# Import Celery tasks (created in analytics.tasks)
from analytics.tasks import generate_project_snapshot
from tasks.notifications import notify_assignment, notify_status_change
from users.models import TenantUser

class TaskService:
    ALLOWED_TRANSITIONS = {
        Task.Status.OPEN: [Task.Status.IN_PROGRESS],
        Task.Status.IN_PROGRESS: [Task.Status.BLOCKED, Task.Status.DONE],
        Task.Status.BLOCKED: [Task.Status.IN_PROGRESS],
    }


    @staticmethod
    def _validate_assignment(*, actor: User, assignee: Optional[TenantUser]) -> int:
        """
        Validates task assignment based on role.

        Time: O(1)
        Space: O(1)
        """
        if assignee is None:
            return None

        # Member can only assign to themselves
        if actor.role == User.Role.MEMBER:
            if assignee.id != actor.id:
                raise PermissionDenied(
                    "Members can only assign tasks to themselves"
                )

        return assignee.id

    @staticmethod
    def get_task(*, user, task_id):
        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)
        return Task.objects.using(db).get(id=task_id, is_deleted=False)

    @staticmethod
    def create_task(*, user, project: Project, title: str, description: str, assigned_to: Optional[TenantUser] = None) -> Task:
        if not Permissions.can_create_task(user):
            raise PermissionDenied("Not allowed to create tasks")

        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)

        assignee_id = TaskService._validate_assignment(
            actor=user,
            assignee=assigned_to,
        )

        task = Task.objects.using(db).create(
            project=project, 
            title=title,
            description = description,
            assigned_to = assignee_id
        )

        TaskActivityService.log(
            db=db,
            task=task,
            action="CREATE",
            user_id=user.id,
        )

        # Initialize SLA tracking for the task
        TaskSLA.objects.using(db).create(
            task=task,
            last_status=task.status,
            last_status_changed_at=timezone.now(),
            open_seconds=0,
            in_progress_seconds=0,
            blocked_seconds=0,
        )

        # Trigger async analytics update for the project (idempotent)
        try:
            generate_project_snapshot(
                db=db,
                project_id=project.id,
            )
        except Exception:
            pass


        return task
    
    @staticmethod
    def list_tasks(*, user, project_id=None):
        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)

        qs = Task.objects.using(db).filter(is_deleted=False)

        if project_id:
            qs = qs.filter(project_id=project_id)

        return qs.order_by("-created_at")

    @staticmethod
    def update_task(*, user, task: Task, **updates) -> Task:
        if not Permissions.can_update_task_status(user): 
            raise PermissionDenied("Not allowed to update tasks")

        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)
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
                sla = TaskSLA.objects.using(db).create(
                    task=task,
                    last_status=old_values['status'],
                    last_status_changed_at=now,
                )

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
                db=db,
                task=task,
                action=action,
                user_id=user.id,
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
                pass

        try:
            generate_project_snapshot(
                db=db,
                project_id=task.project.id,
            )
        except Exception:
            pass

        return task

    @staticmethod
    def soft_delete(*, user: User, task: Task) -> None:
        if not Permissions.can_delete_task(user):
            raise PermissionDenied("Only admin can delete")

        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)

        task.is_deleted = True
        task.save(update_fields=["is_deleted"])

        TaskActivityService.log(
            db=db,
            task=task,
            action="DELETE",
            user=user,
        )
