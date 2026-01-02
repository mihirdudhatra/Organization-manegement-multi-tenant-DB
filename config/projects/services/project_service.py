from projects.models import Project
from django.core.exceptions import PermissionDenied
from config.permissions import Permissions
from system.tenant_context import set_current_tenant_db as set_current_tenant


class ProjectService:

    @staticmethod
    def list_projects(*, user):
        # Ensure tenant context is set for the user's tenant
        # set_current_tenant(user.tenant)
        print('user.tenant: ', user.tenant)
        return Project.objects.filter(is_deleted=False)

    @staticmethod
    def create_project(*, user, name: str, description: str = "") -> Project:
        if not Permissions.can_create_project(user):
            raise PermissionDenied("Not allowed to create project")

        # Ensure tenant context is set for the user's tenant
        set_current_tenant(user.tenant)

        return Project.objects.using("tenant").create(
            name=name,
            description=description,
            created_by=user,
        )

    @staticmethod
    def get_project(*, user, project_id):
        set_current_tenant(user.tenant)
        return Project.objects.using("tenant").get(id=project_id, is_deleted=False)

    @staticmethod
    def update_project(*, user, project_id, name: str, description: str = ""):
        if not Permissions.can_update_project(user):  # assuming such permission
            raise PermissionDenied("Not allowed to update project")

        set_current_tenant(user.tenant)
        project = Project.objects.using("tenant").get(id=project_id, is_deleted=False)
        project.name = name
        project.description = description
        project.save()
        return project

    @staticmethod
    def delete_project(*, user, project_id):
        if not Permissions.can_delete_project(user):  # assuming
            raise PermissionDenied("Not allowed to delete project")

        set_current_tenant(user.tenant)
        project = Project.objects.using("tenant").get(id=project_id, is_deleted=False)
        project.is_deleted = True
        project.save()
