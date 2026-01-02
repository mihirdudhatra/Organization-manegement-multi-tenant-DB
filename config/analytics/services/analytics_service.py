from datetime import date
from django.db.models import Avg
from tasks.models import Task, TaskSLA
from analytics.models import AnalyticsSnapshot


class AnalyticsService:
    """
    Computes daily analytics per project.
    """

    @staticmethod
    def generate_daily_snapshot(*, project, snapshot_date=None):
        snapshot_date = snapshot_date or date.today()

        tasks = Task.objects.filter(
            project=project,
            is_deleted=False,
        )

        snapshot, _ = AnalyticsSnapshot.objects.update_or_create(
            project=project,
            date=snapshot_date,
            defaults={
                "tasks_open": tasks.filter(status=Task.Status.OPEN).count(),
                "tasks_in_progress": tasks.filter(
                    status=Task.Status.IN_PROGRESS
                ).count(),
                "tasks_blocked": tasks.filter(
                    status=Task.Status.BLOCKED
                ).count(),
                "tasks_done": tasks.filter(status=Task.Status.DONE).count(),
                "tasks_created": tasks.filter(
                    created_at__date=snapshot_date
                ).count(),
                "tasks_completed": tasks.filter(
                    status=Task.Status.DONE,
                    updated_at__date=snapshot_date,
                ).count(),
                "avg_completion_seconds": int(
                    TaskSLA.objects.filter(
                        task__project=project
                    ).aggregate(
                        avg=Avg("in_progress_seconds")
                    )["avg"] or 0
                ),
            },
        )

        return snapshot
