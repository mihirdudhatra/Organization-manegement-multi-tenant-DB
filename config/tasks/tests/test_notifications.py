import pytest
from system.models import User
from projects.models import Project
from tasks.services.task_service import TaskService


@pytest.mark.django_db
def test_assignment_triggers_notification(monkeypatch):
    user = User.objects.create_user(username="n1", password="pw", email="n1@example.com")
    user.role = User.Role.ADMIN
    user.save()

    project = Project.objects.create(name="notif-project", created_by=user)
    task = TaskService.create_task(user=user, project=project, title="t-notif")

    called = {}

    def fake_delay(u_id, t_id):
        called['assignment'] = (u_id, t_id)

    monkeypatch.setattr('tasks.notifications.notify_assignment.delay', fake_delay)

    # assign
    TaskService.update_task(user=user, task=task, assigned_to=user)

    assert 'assignment' in called
    assert called['assignment'][1] == task.id


@pytest.mark.django_db
def test_status_change_triggers_notification(monkeypatch):
    user = User.objects.create_user(username="n2", password="pw", email="n2@example.com")
    user.role = User.Role.ADMIN
    user.save()

    project = Project.objects.create(name="notif-project-2", created_by=user)
    task = TaskService.create_task(user=user, project=project, title="t-notif-2")

    called = {}

    def fake_delay(tid, old, new):
        called['status'] = (tid, old, new)

    monkeypatch.setattr('tasks.notifications.notify_status_change.delay', fake_delay)

    TaskService.update_task(user=user, task=task, status=task.Status.IN_PROGRESS)

    assert 'status' in called
    assert called['status'][0] == task.id
