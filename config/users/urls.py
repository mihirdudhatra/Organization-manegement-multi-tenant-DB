from django.urls import path, include
from users.ui.views import login_ui_view, logout_ui_view, signup_ui_view, user_list_ui, user_create_ui, user_update_ui, user_delete_ui, tenant_list_ui, tenant_create_ui, tenant_select_ui

urlpatterns = [
    path("api/v1/", include("users.api_urls")),
    path("signup/", signup_ui_view, name="signup-ui"),
    path("login/", login_ui_view, name="login-ui"),
    path("logout/", logout_ui_view, name="logout"),
    path("users/", user_list_ui, name="user-list"),
    path("users/create/", user_create_ui, name="user-create"),
    path("users/<int:user_id>/update/", user_update_ui, name="user-update"),
    path("users/<int:user_id>/delete/", user_delete_ui, name="user-delete"),
    # path("tenants/", tenant_list_ui, name="tenant-list"),
    # path("tenants/create/", tenant_create_ui, name="tenant-create"),
    # path("tenants/<uuid:tenant_id>/select/", tenant_select_ui, name="tenant-select"),
]
