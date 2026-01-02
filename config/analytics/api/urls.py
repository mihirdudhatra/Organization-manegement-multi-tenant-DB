from django.urls import path
from analytics.api.views import ProjectAnalyticsAPIView

urlpatterns = [
    path(
        "analytics/projects/<int:project_id>/",
        ProjectAnalyticsAPIView.as_view(),
        name="project-analytics",
    ),
]