from celery import shared_task
from projects.models import Project
from analytics.services.analytics_service import AnalyticsService


@shared_task
def generate_daily_project_analytics():
    for project in Project.objects.all():
        AnalyticsService.generate_daily_snapshot(project=project)
