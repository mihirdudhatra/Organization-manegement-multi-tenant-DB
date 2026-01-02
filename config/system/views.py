# from django.shortcuts import render, redirect
# from system.models import Tenant


# def select_tenant_view(request):
#     tenants = Tenant.objects.filter(is_active=True)

#     if request.method == "POST":
#         tenant_id = request.POST["tenant_id"]
#         request.session["tenant_id"] = tenant_id
#         return redirect("login")

#     return render(
#         request,
#         "system/select_tenant.html",
#         {"tenants": tenants},
#     )
from django.views.generic import FormView
from django.shortcuts import redirect
from system.forms import TenantSelectForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from system.services.tenant_service import TenantService
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class TenantSelectView(FormView):
    template_name = "system/select_tenant.html"
    form_class = TenantSelectForm

    def form_valid(self, form):
        tenant = form.cleaned_data["tenant_id"]
        self.request.session["tenant_id"] = str(tenant.id)
        return redirect("login-ui")

@method_decorator(login_required, name='dispatch')
class HomeView(FormView):
    def get(self, request):
        return redirect("project-list")

class TenantSignupAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        tenant_name = request.data["tenant_name"]
        username = request.data["username"]
        password = request.data["password"]
        email = request.data["email"]

        tenant, user = TenantService.create_tenant(
            tenant_name=tenant_name,
            admin_username=username,
            admin_password=password,
        )

        user.email = email
        user.save(update_fields=["email"])

        return Response(
            {"tenant_id": str(tenant.id)},
            status=status.HTTP_201_CREATED,
        )
