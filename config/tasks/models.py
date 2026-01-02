from django.db import models
from projects.models import Project
from system.models import User


class Task(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN"
        IN_PROGRESS = "IN_PROGRESS"
        BLOCKED = "BLOCKED"
        DONE = "DONE"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    assigned_to = models.IntegerField()

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



class TaskActivity(models.Model):
    """
    Immutable audit log for task actions.
    """
    _tenant_model = True
    class Action(models.TextChoices):
        CREATE = "CREATE"
        STATUS_CHANGE = "STATUS_CHANGE"
        ASSIGN = "ASSIGN"
        COMMENT = "COMMENT"
        DELETE = "DELETE"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    action = models.CharField(
        max_length=30,
        choices=Action.choices,
    )

    old_value = models.CharField(max_length=255, null=True, blank=True)
    new_value = models.CharField(max_length=255, null=True, blank=True)

    comment = models.TextField(blank=True)

    performed_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"TaskActivity(id={self.id}, action={self.action}, task_id={self.task.id})"
    
class TaskSLA(models.Model):
    """
    Stores time spent in each status for a task.
    """

    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name="sla",
    )

    open_seconds = models.PositiveIntegerField(default=0)
    in_progress_seconds = models.PositiveIntegerField(default=0)
    blocked_seconds = models.PositiveIntegerField(default=0)

    last_status = models.CharField(max_length=20)
    last_status_changed_at = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)
