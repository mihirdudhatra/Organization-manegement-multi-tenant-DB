from django.urls import path
from projects.ui.views import project_list_ui, project_create_ui, project_update_ui, project_delete_ui

urlpatterns = [
    path("projects/", project_list_ui, name="project-list"),
    path("projects/create/", project_create_ui, name="project-create"),
    path("projects/<int:project_id>/update/", project_update_ui, name="project-update"),
    path("projects/<int:project_id>/delete/", project_delete_ui, name="project-delete"),
]
