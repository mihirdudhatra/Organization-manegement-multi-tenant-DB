from django.shortcuts import render, redirect

from tasks.services.task_service import TaskService
from projects.services.project_service import ProjectService
from system.tenant_context import set_current_tenant_db as set_current_tenant
from tasks.models import Task
import requests
from django.shortcuts import redirect
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



def task_list_ui(request, project_id=None):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    headers = _auth_headers(request)
    if not headers:
        return redirect("login-ui")

    url = "/api/v1/tasks/"
    if project_id:
        url += f"?project={project_id}"

    response = requests.get(
        f"{settings.API_BASE_URL}{url}",
        headers=headers,
        timeout=5,
    )

    tasks = response.json() if response.status_code == 200 else []

    return render(
        request,
        "tasks/list.html",
        {"tasks": tasks, "project_id": project_id},
    )

def task_create_ui(request, project_id=None):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    headers = _auth_headers(request)
    if not headers:
        return redirect("login-ui")

    if request.method == "POST":
        payload = {
            "project": request.POST.get("project"),
            "title": request.POST.get("title"),
            "description": request.POST.get("description", ""),
            "status": request.POST.get("status"),
            "assigned_to": request.POST.get("assigned_to") or None,
        }

        response = requests.post(
            f"{settings.API_BASE_URL}/api/v1/tasks/",
            json=payload,
            headers=headers,
            timeout=5,
        )

        if response.status_code == 201:
            return redirect("project-tasks-ui", project_id=payload["project"])

        if response.status_code in (401, 403):
            request.session.flush()
            return redirect("login-ui")

        return render(
            request,
            "tasks/create.html",
            {"error": response.text},
        )

    projects_res = requests.get(
        f"{settings.API_BASE_URL}/api/v1/projects/",
        headers=headers,
    )

    return render(
        request,
        "tasks/create.html",
        {
            "projects": projects_res.json() if projects_res.status_code == 200 else [],
            "project_id": project_id,
            "users": [],  
        },
    )

def task_update_ui(request, task_id):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    headers = _auth_headers(request)
    if not headers:
        return redirect("login-ui")

    if request.method == "POST":
        payload = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description", ""),
            "status": request.POST.get("status"),
            "assigned_to": request.POST.get("assigned_to") or None,
        }

        response = requests.put(
            f"{settings.API_BASE_URL}/api/v1/tasks/{task_id}/",
            json=payload,
            headers=headers,
            timeout=5,
        )

        if response.status_code in (200, 204):
            return redirect("task-list-ui")

        return render(
            request,
            "tasks/update.html",
            {"error": response.text},
        )

    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/tasks/{task_id}/",
        headers=headers,
    )

    if response.status_code != 200:
        return redirect("task-list-ui")

    return render(
        request,
        "tasks/update.html",
        {"task": response.json(), "users": []},
    )


def task_detail_ui(request, task_id):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    headers = _auth_headers(request)
    if not headers:
        return redirect("login-ui")

    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/tasks/{task_id}/",
        headers=headers,
    )

    if response.status_code != 200:
        return redirect("task-list-ui")

    return render(
        request,
        "tasks/detail.html",
        {"task": response.json()},
    )

def task_delete_ui(request, task_id):
    if not request.session.get("is_authenticated"):
        return redirect("login-ui")

    headers = _auth_headers(request)
    if not headers:
        return redirect("login-ui")

    if request.method == "POST":
        response = requests.delete(
            f"{settings.API_BASE_URL}/api/v1/tasks/{task_id}/",
            headers=headers,
            timeout=5,
        )

        return redirect("task-list-ui")

    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/tasks/{task_id}/",
        headers=headers,
    )

    return render(
        request,
        "tasks/delete.html",
        {"task": response.json() if response.status_code == 200 else None},
    )


def task_status_update_ui(request, task_id):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    if request.method == 'POST' and 'status' in request.POST:
        set_current_tenant(request.user.tenant)
        try:
            task = TaskService.get_task(user=request.user, task_id=task_id)
            TaskService.update_task(user=request.user, task=task, status=request.POST["status"])
        except Exception:
            pass
    return redirect("task-list-ui")

def task_audit_ui(request, task_id):
    try:
        activities = api_get(request, f"/api/v1/tasks/{task_id}/audit/")
    except Exception:
        activities = []
    return render(request, "tasks/audit.html", {"activities": activities})

def task_sla_ui(request, task_id):
    try:
        sla = api_get(request, f"/api/v1/tasks/{task_id}/sla/")
    except Exception:
        sla = {"error": "Failed to load SLA data"}
    return render(
        request,
        "tasks/sla.html",
        {"sla": sla},
    )


