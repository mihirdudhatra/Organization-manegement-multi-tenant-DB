from django.urls import path
from tasks.ui.views import (
    task_list_ui,
    task_status_update_ui,
    task_audit_ui,
    task_sla_ui,
    task_create_ui,
    task_update_ui,
    task_delete_ui,
    task_detail_ui,
)

urlpatterns = [
    path("tasks/", task_list_ui, name="task-list-ui"),
    path("projects/<int:project_id>/tasks/", task_list_ui, name="project-tasks-ui",),
    path("tasks/<int:task_id>/", task_detail_ui, name="task-detail",),
    path("tasks/<int:task_id>/update/", task_status_update_ui, name="task-status-update",),
    path("tasks/<int:task_id>/audit/", task_audit_ui, name="task-audit-ui",),
    path("tasks/<int:task_id>/sla/", task_sla_ui, name="task-sla-ui",),
    path("projects/<int:project_id>/tasks/create/", task_create_ui, name="task-create",),
    path("tasks/<int:task_id>/update/", task_update_ui, name="task-update",),
    path("tasks/<int:task_id>/delete/", task_delete_ui, name="task-delete"),
]
