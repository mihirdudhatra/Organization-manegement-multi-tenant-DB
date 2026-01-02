from django.core.management.base import BaseCommand
from system.models import Tenant, User
from projects.models import Project
from tasks.models import Task, TaskActivity, TaskSLA
from analytics.models import AnalyticsSnapshot
from datetime import date, timedelta
from django.utils import timezone
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Create sample data for testing multi-tenant system'

    def handle(self, *args, **options):
        fake = Faker()
        # Create tenants
        tenant_names = ['TechCorp', 'InnovateLabs', 'GlobalSolutions', 'NextGen', 'DataDriven']
        tenants = []
        for name in tenant_names:
            tenant, created = Tenant.objects.get_or_create(
                name=name,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'Created tenant: {tenant.name}')
            tenants.append(tenant)

        # Create sample data for each tenant
        for tenant in tenants:
            self.create_tenant_data(tenant, fake)

        self.stdout.write('Sample data creation completed.')

    def create_tenant_data(self, tenant, fake):
        # Create users
        roles = [User.Role.ADMIN, User.Role.MANAGER, User.Role.MEMBER]
        users = []
        for i in range(5):  # 5 users per tenant
            role = random.choice(roles)
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}_{tenant.name.lower()}"
            email = f"{username}@{tenant.name.lower()}.com"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'tenant': tenant,
                }
            )
            user.set_password('password123')
            user.save()
            users.append(user)

        # Create projects
        projects = []
        for i in range(random.randint(3, 6)):  # 3-6 projects per tenant
            project = Project.objects.create(
                name=fake.company() + ' Project',
                description=fake.text(max_nb_chars=200),
                created_by=random.choice(users)
            )
            projects.append(project)

        # Create tasks
        task_statuses = [Task.Status.OPEN, Task.Status.IN_PROGRESS, Task.Status.DONE, Task.Status.BLOCKED]
        tasks = []
        for project in projects:
            for i in range(random.randint(5, 10)):  # 5-10 tasks per project
                task = Task.objects.create(
                    project=project,
                    title=fake.sentence(nb_words=6),
                    description=fake.text(max_nb_chars=300),
                    status=random.choice(task_statuses),
                    assigned_to=random.choice(users)
                )
                tasks.append(task)

        # Create task activities
        actions = [TaskActivity.Action.CREATE, TaskActivity.Action.STATUS_CHANGE, TaskActivity.Action.ASSIGN, TaskActivity.Action.COMMENT]
        for task in tasks[:len(tasks)//2]:  # Activities for half the tasks
            for i in range(random.randint(1, 3)):
                action = random.choice(actions)
                activity = TaskActivity.objects.create(
                    task=task,
                    action=action,
                    performed_by=random.choice(users),
                    comment=fake.sentence() if action == TaskActivity.Action.COMMENT else '',
                    old_value=random.choice(task_statuses) if action == TaskActivity.Action.STATUS_CHANGE else '',
                    new_value=random.choice(task_statuses) if action in [TaskActivity.Action.STATUS_CHANGE, TaskActivity.Action.ASSIGN] else ''
                )

        # Create task SLAs
        for task in tasks:
            now = timezone.now()
            sla = TaskSLA.objects.create(
                task=task,
                open_seconds=random.randint(3600, 86400),  # 1 hour to 1 day
                in_progress_seconds=random.randint(3600, 172800) if task.status in [Task.Status.IN_PROGRESS, Task.Status.DONE] else 0,
                blocked_seconds=random.randint(1800, 36000) if task.status == Task.Status.BLOCKED else 0,
                last_status=task.status,
                last_status_changed_at=now - timedelta(seconds=random.randint(3600, 604800))  # 1 hour to 1 week ago
            )

        # Create analytics snapshots for the last 30 days
        today = date.today()
        for project in projects:
            for i in range(30):
                snapshot_date = today - timedelta(days=i)
                AnalyticsSnapshot.objects.create(
                    project=project,
                    date=snapshot_date,
                    tasks_open=random.randint(0, 10),
                    tasks_in_progress=random.randint(0, 5),
                    tasks_blocked=random.randint(0, 3),
                    tasks_done=random.randint(0, 20),
                    avg_completion_seconds=random.randint(3600, 604800),  # 1 hour to 1 week
                    tasks_created=random.randint(0, 3),
                    tasks_completed=random.randint(0, 3)
                )

        self.stdout.write(f'Created sample data for tenant: {tenant.name} - {len(users)} users, {len(projects)} projects, {len(tasks)} tasks')