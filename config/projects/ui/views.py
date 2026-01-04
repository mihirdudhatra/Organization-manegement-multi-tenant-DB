import requests
from django.shortcuts import render, redirect
from projects.services.project_service import ProjectService
from system.tenant_context import set_current_tenant_db as set_current_tenant
from django.conf import settings


def project_list_ui(request):

    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    access_token = request.session.get("access_token")

    if not tenant_id or not access_token:
        return redirect("login-ui")

    # Call backend API with JWT
    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/projects/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Tenant-ID": tenant_id,
        },
    )

    if response.status_code != 200:
        return redirect("login-ui")

    projects = response.json()

    return render(
        request,
        "projects/list.html",
        {"projects": projects},
    )


def project_create_ui(request):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    access_token = request.session.get("access_token")
    tenant_id = request.session.get("tenant_id")

    if not access_token or not tenant_id:
        return redirect("login-ui")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            return render(
                request,
                "projects/create.html",
                {"error": "Project name is required"},
            )

        response = requests.post(
            f"{settings.API_BASE_URL}/api/v1/projects/",
            json={
                "name": name,
                "description": description,
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Tenant-ID": tenant_id,
            },
            timeout=5,
        )

        if response.status_code == 201:
            return redirect("project-list")

        if response.status_code in (401, 403):
            # Token expired or permission denied
            request.session.flush()
            return redirect("login-ui")

        return render(
            request,
            "projects/create.html",
            {"error": response.json()},
        )

    return render(request, "projects/create.html")

def project_update_ui(request, project_id):

    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    access_token = request.session.get("access_token")
    tenant_id = request.session.get("tenant_id")

    if not access_token or not tenant_id:
        return redirect("login-ui")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Tenant-ID": tenant_id,
    }

    if request.method == "POST":
        response = requests.put(
            f"{settings.API_BASE_URL}/api/v1/projects/{project_id}/",
            json={
                "name": request.POST.get("name"),
                "description": request.POST.get("description", ""),
            },
            headers=headers,
            timeout=5,
        )

        if response.status_code in (200, 204):
            return redirect("project-list")

        if response.status_code in (401, 403):
            request.session.flush()
            return redirect("login-ui")

        try:
            error = response.json()
        except ValueError:
            error = response.text or "Update failed"

        return render(
            request,
            "projects/update.html",
            {"error": error},
        )

    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/projects/{project_id}/",
        headers=headers,
        timeout=5,
    )

    if response.status_code == 200:
        return render(
            request,
            "projects/update.html",
            {"project": response.json()},
        )

    return redirect("project-list")

def project_delete_ui(request, project_id):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    access_token = request.session.get("access_token")
    tenant_id = request.session.get("tenant_id")

    if not access_token or not tenant_id:
        return redirect("login-ui")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Tenant-ID": tenant_id,
    }

    if request.method == "POST":
        response = requests.delete(
            f"{settings.API_BASE_URL}/api/v1/projects/{project_id}/",
            headers=headers,
            timeout=5,
        )

        if response.status_code in (204, 200):
            return redirect("project-list")

        if response.status_code in (401, 403):
            request.session.flush()
            return redirect("login-ui")

        try:
            error = response.json()
        except ValueError:
            error = response.text or "Delete failed"

        return render(
            request,
            "projects/delete.html",
            {"error": error},
        )

    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/projects/{project_id}/",
        headers=headers,
        timeout=5,
    )

    if response.status_code == 200:
        return render(
            request,
            "projects/delete.html",
            {"project": response.json()},
        )

    return redirect("project-list")
