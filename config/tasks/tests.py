from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from unittest.mock import patch, MagicMock

from system.models import Tenant, User
from projects.models import Project
from tasks.models import Task, TaskSLA, TaskActivity
from tasks.services.task_service import TaskService


class TaskServiceTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Tenant")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password",
            tenant=self.tenant,
            role=User.Role.ADMIN
        )
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            created_by=self.user
        )

    @patch('tasks.services.task_service.set_current_tenant')
    def test_create_task_success(self, mock_set_tenant):
        mock_set_tenant.return_value = None

        with patch('tasks.services.task_service.TaskActivityService.log'), \
             patch('tasks.services.task_service.generate_project_snapshot.delay'), \
             patch('tasks.services.task_service.Permissions.can_create_task', return_value=True):

            task = TaskService.create_task(
                user=self.user,
                project=self.project,
                title="Test Task",
                description="Test Description"
            )

            self.assertEqual(task.title, "Test Task")
            self.assertEqual(task.project, self.project)
            self.assertEqual(task.status, Task.Status.OPEN)
            self.assertIsNotNone(task.sla)

    @patch('tasks.services.task_service.set_current_tenant')
    def test_create_task_permission_denied(self, mock_set_tenant):
        mock_set_tenant.return_value = None

        with patch('tasks.services.task_service.Permissions.can_create_task', return_value=False):
            with self.assertRaises(PermissionDenied):
                TaskService.create_task(
                    user=self.user,
                    project=self.project,
                    title="Test Task",
                    description="Test Description"
                )

    @patch('tasks.services.task_service.set_current_tenant')
    def test_update_task_status_transition(self, mock_set_tenant):
        mock_set_tenant.return_value = None

        task = Task.objects.create(
            project=self.project,
            title="Test Task",
            status=Task.Status.OPEN
        )
        TaskSLA.objects.create(
            task=task,
            last_status=Task.Status.OPEN,
            last_status_changed_at=timezone.now()
        )

        with patch('tasks.services.task_service.Permissions.can_update_task_status', return_value=True), \
             patch('tasks.services.task_service.TaskActivityService.log'), \
             patch('tasks.services.task_service.generate_project_snapshot.delay'), \
             patch('tasks.services.task_service.notify_status_change.delay'):

            updated_task = TaskService.update_task(
                user=self.user,
                task=task,
                status=Task.Status.IN_PROGRESS
            )

            self.assertEqual(updated_task.status, Task.Status.IN_PROGRESS)
            task.refresh_from_db()
            self.assertEqual(task.status, Task.Status.IN_PROGRESS)

    @patch('tasks.services.task_service.set_current_tenant')
    def test_update_task_invalid_transition(self, mock_set_tenant):
        mock_set_tenant.return_value = None

        task = Task.objects.create(
            project=self.project,
            title="Test Task",
            status=Task.Status.OPEN
        )

        with patch('tasks.services.task_service.Permissions.can_update_task_status', return_value=True):
            with self.assertRaises(ValueError):
                TaskService.update_task(
                    user=self.user,
                    task=task,
                    status=Task.Status.DONE  # Invalid transition from OPEN
                )

    @patch('tasks.services.task_service.set_current_tenant')
    def test_soft_delete_task(self, mock_set_tenant):
        mock_set_tenant.return_value = None

        task = Task.objects.create(
            project=self.project,
            title="Test Task"
        )

        with patch('tasks.services.task_service.Permissions.can_delete_task', return_value=True), \
             patch('tasks.services.task_service.TaskActivityService.log'):

            TaskService.soft_delete(user=self.user, task=task)

            task.refresh_from_db()
            self.assertTrue(task.is_deleted)
