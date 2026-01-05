from django.urls import path
from django.views.generic import RedirectView
from analytics.ui.views import project_analytics_ui
from django.urls import reverse_lazy

urlpatterns = [
    path("projects/<int:project_id>/analytics/", project_analytics_ui, name="project-analytics-ui"),
    path("analytics/", RedirectView.as_view(url=reverse_lazy("project-list")), name="analytics"),
]