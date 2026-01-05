from celery import shared_task
from projects.models import Project
from analytics.services.analytics_service import AnalyticsService


from celery import shared_task
from system.db_registry import ensure_tenant_db_registered
from system.tenant_context import set_current_tenant_db
from projects.models import Project
from analytics.services.analytics_service import AnalyticsService


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def generate_project_snapshot(self, *, db: str, project_id: int, snapshot_date=None,) -> None:

    set_current_tenant_db(db)

    try:
        project = Project.objects.using(db).get(id=project_id)
    except Project.DoesNotExist:
        return

    AnalyticsService.generate_daily_snapshot(
        db=db,
        project=project,
        snapshot_date=snapshot_date,
    )

