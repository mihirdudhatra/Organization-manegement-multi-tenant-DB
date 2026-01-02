from django.urls import path
from django.views.generic import RedirectView
from analytics.ui.views import project_analytics_ui

urlpatterns = [
    path("projects/<int:project_id>/analytics/", project_analytics_ui, name="project-analytics"),
    path("analytics/", RedirectView.as_view(url='project-list'), name="analytics"),
]