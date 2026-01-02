from django.db import models
from projects.models import Project


class AnalyticsSnapshot(models.Model):
    """
    Daily pre-aggregated analytics per project.
    """
    _tenant_model = True
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="analytics_snapshots",
    )

    date = models.DateField()

    tasks_open = models.PositiveIntegerField(default=0)
    tasks_in_progress = models.PositiveIntegerField(default=0)
    tasks_blocked = models.PositiveIntegerField(default=0)
    tasks_done = models.PositiveIntegerField(default=0)

    avg_completion_seconds = models.PositiveIntegerField(default=0)

    tasks_created = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "date")
        ordering = ["-date"]
