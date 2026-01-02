from system.views import TenantSelectView, HomeView
from django.urls import path, include
from system.api.views import TenantListAPIView
from system.views import TenantSignupAPIView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("select-tenant/", TenantSelectView.as_view(), name="select-tenant"),
    path("api/v1/tenants/", TenantListAPIView.as_view(), name="tenant-list"),
    path("tenants/signup/", TenantSignupAPIView.as_view(), name="tenant-signup"),
    path("api/v1/auth/", include("users.api_urls")),
    path("", include("users.urls")),
]
