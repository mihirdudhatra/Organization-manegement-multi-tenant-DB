from celery import shared_task
from projects.models import Project
from analytics.services.analytics_service import AnalyticsService


@shared_task
def generate_project_snapshot(project_id: int, snapshot_date=None):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return

    AnalyticsService.generate_daily_snapshot(project=project, snapshot_date=snapshot_date)
