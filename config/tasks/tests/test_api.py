import pytest
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from system.models import Tenant, User
from projects.models import Project
from tasks.models import Task


@pytest.mark.django_db
class TaskAPITestCase(APITestCase):
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
        self.client.force_authenticate(user=self.user)

    def test_list_tasks(self):
        # Create some tasks
        Task.objects.create(project=self.project, title="Task 1")
        Task.objects.create(project=self.project, title="Task 2")

        url = reverse('task-list')
        response = self.client.get(url, {'project': self.project.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_task(self):
        url = reverse('task-list')
        data = {
            'project': self.project.id,
            'title': 'New Task',
            'description': 'Task description'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['status'], 'OPEN')

    def test_update_task_status(self):
        task = Task.objects.create(project=self.project, title="Test Task")

        url = reverse('task-detail', kwargs={'pk': task.id})
        data = {'status': 'IN_PROGRESS'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'IN_PROGRESS')

    def test_get_task_audit(self):
        task = Task.objects.create(project=self.project, title="Test Task")

        url = reverse('task-audit', kwargs={'pk': task.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have at least the CREATE activity
        self.assertGreater(len(response.data), 0)

    def test_get_task_sla(self):
        task = Task.objects.create(project=self.project, title="Test Task")

        url = reverse('task-sla', kwargs={'pk': task.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('open_seconds', response.data)