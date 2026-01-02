import pytest
from datetime import timedelta
from django.utils import timezone

from system.models import User
from projects.models import Project
from tasks.models import Task, TaskSLA, TaskActivity
from tasks.services.task_service import TaskService


@pytest.mark.django_db
def test_status_transition_updates_sla(monkeypatch):
    # Prevent Celery calls from running during tests
    monkeypatch.setattr("analytics.tasks.generate_project_snapshot.delay", lambda *a, **k: None)

    user = User.objects.create_user(username="alice", password="pw")
    user.role = User.Role.ADMIN
    user.save()

    project = Project.objects.create(name="Test Project", created_by=user)

    task = TaskService.create_task(user=user, project=project, title="Task 1")

    # Simulate SLA last change in the past
    sla = task.sla
    past = timezone.now() - timedelta(seconds=3600)
    sla.last_status_changed_at = past
    sla.last_status = Task.Status.OPEN
    sla.save()

    # Transition to IN_PROGRESS
    TaskService.update_task(user=user, task=task, status=Task.Status.IN_PROGRESS)

    sla.refresh_from_db()
    assert sla.in_progress_seconds >= 0
    assert sla.open_seconds >= 3600 - 2  # allow a small delta

    # Ensure activity logged
    act = TaskActivity.objects.filter(task=task, action=TaskActivity.Action.STATUS_CHANGE).first()
    assert act is not None
    assert "OPEN" in (act.old_value or "")


@pytest.mark.django_db
def test_idempotent_status_update_no_change(monkeypatch):
    monkeypatch.setattr("analytics.tasks.generate_project_snapshot.delay", lambda *a, **k: None)

    user = User.objects.create_user(username="bob", password="pw")
    user.role = User.Role.ADMIN
    user.save()

    project = Project.objects.create(name="P2", created_by=user)
    task = TaskService.create_task(user=user, project=project, title="Task 2")

    # initial status is OPEN
    before_count = TaskActivity.objects.filter(task=task).count()

    # call update with same status
    TaskService.update_task(user=user, task=task, status=Task.Status.OPEN)

    after_count = TaskActivity.objects.filter(task=task).count()
    assert before_count == after_count
