from django.shortcuts import render, redirect
from tasks.services.task_service import TaskService
from projects.services.project_service import ProjectService
from system.tenant_context import set_current_tenant_db as set_current_tenant
from tasks.models import Task


def task_list_ui(request, project_id=None):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    set_current_tenant(request.user.tenant)
    tasks = TaskService.list_tasks(user=request.user, project_id=project_id)

    return render(
        request,
        "tasks/list.html",
        {
            "tasks": tasks,
            "project_id": project_id,
        },
    )


def task_create_ui(request, project_id=None):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    if request.method == 'POST':
        set_current_tenant(request.user.tenant)
        try:
            # Get project
            project = ProjectService.get_project(user=request.user, project_id=request.POST['project'])
            task = TaskService.create_task(
                user=request.user,
                project=project,
                title=request.POST['title'],
                description = request.POST['description']
            )
            # Update other fields
            updates = {
                'description': request.POST.get('description', ''),
                'status': request.POST['status'],
            }
            if request.POST.get('assigned_to'):
                updates['assigned_to'] = request.POST['assigned_to']
            TaskService.update_task(user=request.user, task=task, **updates)
            return redirect('project-tasks-ui', project_id=request.POST['project'])
        except Exception as e:
            return render(request, 'tasks/create.html', {'error': str(e), 'project_id': project_id})

    # GET: need projects and users for dropdowns
    set_current_tenant(request.user.tenant)
    projects = ProjectService.list_projects(user=request.user)
    users = [] 
    return render(request, 'tasks/create.html', {
        'projects': projects,
        'users': users,
        'project_id': project_id
    })


def task_update_ui(request, task_id):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    if request.method == 'POST':
        set_current_tenant(request.user.tenant)
        try:
            task = TaskService.get_task(user=request.user, task_id=task_id)
            updates = {
                'title': request.POST['title'],
                'description': request.POST.get('description', ''),
                'status': request.POST['status'],
            }
            if request.POST.get('assigned_to'):
                updates['assigned_to_id'] = int(request.POST['assigned_to'])
            TaskService.update_task(user=request.user, task=task, **updates)
            return redirect('project-tasks-ui', project_id=task.project_id)
        except Exception as e:
            return render(request, 'tasks/update.html', {'error': str(e), 'task_id': task_id})

    # GET: fetch task and users
    set_current_tenant(request.user.tenant)
    try:
        task = TaskService.get_task(user=request.user, task_id=task_id)
        users = []  # TODO
        return render(request, 'tasks/update.html', {'task': task, 'users': users})
    except Task.DoesNotExist:
        return redirect('task-list-ui')


def task_detail_ui(request, task_id):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    set_current_tenant(request.user.tenant)
    try:
        task = TaskService.get_task(user=request.user, task_id=task_id)
        return render(request, 'tasks/detail.html', {'task': task})
    except Task.DoesNotExist:
        return redirect('task-list-ui')


def task_delete_ui(request, task_id):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    if request.method == 'POST':
        set_current_tenant(request.user.tenant)
        try:
            task = TaskService.get_task(user=request.user, task_id=task_id)
            TaskService.soft_delete(user=request.user, task=task)
        except Exception:
            pass
        return redirect('task-list-ui')

    # GET: show confirmation
    set_current_tenant(request.user.tenant)
    try:
        task = TaskService.get_task(user=request.user, task_id=task_id)
        return render(request, 'tasks/delete.html', {'task': task})
    except Task.DoesNotExist:
        return redirect('task-list-ui')


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


