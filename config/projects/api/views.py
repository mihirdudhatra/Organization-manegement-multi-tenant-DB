# # projects/api/views.py
# from rest_framework.viewsets import ViewSet
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.exceptions import PermissionDenied

# from projects.services.project_service import ProjectService
# from projects.api.serializers import ProjectSerializer
# from system.models import User
# from system.tenant_context import set_current_tenant


# class ProjectViewSet(ViewSet):
#     """
#     Tenant-scoped Project APIs.
#     """

#     def _get_user(self, request) -> User:
#         print('request: ', request.user)
#         user_id = request.META.get("HTTP_X_USER_ID")
#         print('user_id: ', user_id)
#         if not user_id:
#             raise PermissionDenied("User not authenticated")

#         try:
#             return User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             raise PermissionDenied("Invalid user")

#     def list(self, request):
#         """
#         Time: O(N)
#         Space: O(1)
#         """
#         user = self._get_user(request)

#         set_current_tenant(user.tenant)

#         projects = ProjectService.list_projects(user=user)
#         serializer = ProjectSerializer(projects, many=True)
#         return Response(serializer.data)

#     def create(self, request):
#         """
#         Time: O(1)
#         Space: O(1)
#         """
#         user = self._get_user(request)

#         set_current_tenant(user.tenant)

#         project = ProjectService.create_project(
#             user=user,
#             name=request.data["name"],
#             description=request.data.get("description", ""),
#         )

#         serializer = ProjectSerializer(project)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
# projects/api/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from projects.api.serializers import ProjectSerializer
from projects.services.project_service import ProjectService


class ProjectViewSet(ModelViewSet):
    """
    Tenant-scoped Project APIs.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Time: O(N)
        Space: O(1)
        """
        return ProjectService.list_projects(user=self.request.user)

    def perform_create(self, serializer):
        project = ProjectService.create_project(
            user=self.request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        serializer.instance = project
