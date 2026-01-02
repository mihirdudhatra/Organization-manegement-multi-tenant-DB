from locust import HttpUser, task, between
from random import choice, randint
import json


class TaskPlatformUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "admin_tenantA",
            "password": "password"
        })
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            self.token = None

    @task(3)
    def list_tasks(self):
        if self.token:
            self.client.get("/api/v1/tasks/", headers=self.headers)

    @task(2)
    def create_task(self):
        if self.token:
            projects = [1, 2]  # Sample project IDs
            task_data = {
                "project": choice(projects),
                "title": f"Load Test Task {randint(1, 1000)}",
                "description": "Task created during load testing"
            }
            self.client.post("/api/v1/tasks/", json=task_data, headers=self.headers)

    @task(1)
    def update_task_status(self):
        if self.token:
            # Assume some task IDs exist
            task_id = randint(1, 100)
            status_options = ["OPEN", "IN_PROGRESS", "BLOCKED", "DONE"]
            update_data = {
                "status": choice(status_options)
            }
            self.client.patch(f"/api/v1/tasks/{task_id}/", json=update_data, headers=self.headers)

    @task(2)
    def get_analytics(self):
        if self.token:
            project_id = choice([1, 2])
            self.client.get(f"/api/v1/analytics/projects/{project_id}/", headers=self.headers)

    @task(1)
    def get_task_audit(self):
        if self.token:
            task_id = randint(1, 100)
            self.client.get(f"/api/v1/tasks/{task_id}/audit/", headers=self.headers)


class AnalyticsHeavyUser(HttpUser):
    wait_time = between(2, 5)

    def on_start(self):
        # Login as analytics user
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "manager_tenantA",
            "password": "password"
        })
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

    @task
    def analytics_dashboard(self):
        if hasattr(self, 'token') and self.token:
            # Simulate dashboard loading - multiple analytics calls
            self.client.get("/api/v1/analytics/projects/1/", headers=self.headers)
            self.client.get("/api/v1/analytics/projects/2/", headers=self.headers)
            self.client.get("/api/v1/tasks/?project=1", headers=self.headers)