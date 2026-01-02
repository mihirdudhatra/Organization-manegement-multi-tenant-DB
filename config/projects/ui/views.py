from django.shortcuts import render, redirect
from projects.services.project_service import ProjectService
from system.tenant_context import set_current_tenant_db as set_current_tenant


def project_list_ui(request):
    print('request: ', request.user)
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("login-ui")

    set_current_tenant(request.user.tenant)
    projects = ProjectService.list_projects(user=request.user)

    return render(request, "projects/list.html", {"projects": projects})


def project_create_ui(request):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    if request.method == 'POST':
        set_current_tenant(request.user.tenant)
        try:
            project = ProjectService.create_project(
                user=request.user,
                name=request.POST['name'],
                description=request.POST.get('description', '')
            )
            return redirect('project-list')
        except Exception as e:
            return render(request, 'projects/create.html', {'error': str(e)})

    return render(request, 'projects/create.html')


def project_update_ui(request, project_id):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    if request.method == 'POST':
        set_current_tenant(request.user.tenant)
        try:
            project = ProjectService.update_project(
                user=request.user,
                project_id=project_id,
                name=request.POST['name'],
                description=request.POST.get('description', '')
            )
            return redirect('project-list')
        except Exception as e:
            return render(request, 'projects/update.html', {'error': str(e), 'project_id': project_id})

    # GET: fetch current data
    set_current_tenant(request.user.tenant)
    try:
        project = ProjectService.get_project(user=request.user, project_id=project_id)
        return render(request, 'projects/update.html', {'project': project})
    except Project.DoesNotExist:
        return redirect('project-list')


def project_delete_ui(request, project_id):
    if not request.user.is_authenticated:
        return redirect("login-ui")

    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("select-tenant")

    if request.method == 'POST':
        set_current_tenant(request.user.tenant)
        try:
            ProjectService.delete_project(user=request.user, project_id=project_id)
            return redirect('project-list')
        except Exception:
            pass  # or handle

    # GET: show confirmation
    set_current_tenant(request.user.tenant)
    try:
        project = ProjectService.get_project(user=request.user, project_id=project_id)
        return render(request, 'projects/delete.html', {'project': project})
    except Project.DoesNotExist:
        return redirect('project-list')
