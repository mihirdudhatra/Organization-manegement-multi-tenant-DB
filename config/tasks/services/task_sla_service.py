from django.utils import timezone
from tasks.models import Task, TaskSLA


class TaskSLAService:
    """
    Handles SLA calculations.
    """

    @staticmethod
    def initialize(task: Task) -> None:
        TaskSLA.objects.create(
            task=task,
            last_status=task.status,
            last_status_changed_at=timezone.now(),
        )

    @staticmethod
    def update_on_status_change(
        *,
        task: Task,
        old_status: str,
        new_status: str,
    ) -> None:
        sla = task.sla
        now = timezone.now()

        elapsed = int(
            (now - sla.last_status_changed_at).total_seconds()
        )

        if old_status == Task.Status.OPEN:
            sla.open_seconds += elapsed
        elif old_status == Task.Status.IN_PROGRESS:
            sla.in_progress_seconds += elapsed
        elif old_status == Task.Status.BLOCKED:
            sla.blocked_seconds += elapsed

        sla.last_status = new_status
        sla.last_status_changed_at = now
        sla.save(
            update_fields=[
                "open_seconds",
                "in_progress_seconds",
                "blocked_seconds",
                "last_status",
                "last_status_changed_at",
            ]
        )
