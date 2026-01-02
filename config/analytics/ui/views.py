from django.shortcuts import render, redirect
from config.utils.api_client import api_get


def project_analytics_ui(request, project_id):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    try:
        snapshots = api_get(request, f"/api/v1/analytics/projects/{project_id}/",)
    except Exception:
        snapshots = []
    return render(request, "analytics/project_dashboard.html", {"snapshots": snapshots})
