from projects.models import Project
from django.core.exceptions import PermissionDenied
from config.permissions import Permissions
from system.tenant_context import set_current_tenant_db as set_current_tenant
from system.tenant_context import get_current_tenant_db
from system.db_registry import ensure_tenant_db_registered

class ProjectService:

    @staticmethod
    def list_projects(*, user):
        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)

        return Project.objects.using(db).filter(is_deleted=False)

    @staticmethod
    def create_project(*, user, name: str, description: str = "") -> Project:
        if not Permissions.can_create_project(user):
            raise PermissionDenied("Not allowed to create project")

        # Ensure tenant context is set for the user's tenant
        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)

        return Project.objects.using(db).create(
            name=name,
            description=description,
            created_by=user.id,
        )

    @staticmethod
    def get_project(*, user, project_id):
        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)
        return Project.objects.using(db).get(id=project_id, is_deleted=False)

    @staticmethod
    def update_project(*, user, project_id, name: str, description: str = ""):
        if not Permissions.can_update_project(user):  # assuming such permission
            raise PermissionDenied("Not allowed to update project")

        db = ensure_tenant_db_registered(user.tenant)
        set_current_tenant(db)
        project = Project.objects.using(db).get(id=project_id, is_deleted=False)
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
