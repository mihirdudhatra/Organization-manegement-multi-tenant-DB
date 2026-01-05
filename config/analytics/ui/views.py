from django.shortcuts import render, redirect
from config.utils.api_client import api_get
import requests
from django.conf import settings

def _auth_headers(request):
    token = request.session.get("access_token")
    tenant_id = request.session.get("tenant_id")

    if not token or not tenant_id:
        return None

    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id,
    }


def project_analytics_ui(request, project_id):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    headers = _auth_headers(request)
    if not headers:
        return redirect("login-ui")

    try:
        snapshots = requests.get(f"{settings.API_BASE_URL}/api/v1/analytics/projects/{project_id}/", headers, )
    except Exception:
        snapshots = []

    return render(
        request,
        "analytics/project_dashboard.html",
        {"snapshots": snapshots},
    )
