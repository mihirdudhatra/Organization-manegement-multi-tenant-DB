import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from system.services.tenant_service import TenantService
from system.models import Tenant, User

# def signup_ui_view(request):
#     if request.method == "POST":
#         tenant_name = request.POST["tenant_name"]
#         username = request.POST["username"]
#         password = request.POST["password"]
#         email = request.POST["email"]
        
#         try:
#             tenant, user = TenantService.create_tenant(
#                 tenant_name=tenant_name,
#                 admin_username=username,
#                 admin_password=password,
#             )
#             # Update the created user with email
#             user.email = email
#             user.save()
            
#             # Log in the user
#             login(request, user)
#             request.session["tenant_id"] = str(user.tenant.id)
#             request.session.save()
#             return redirect("project-list")
#         except Exception as e:
#             return render(
#                 request,
#                 "auth/signup.html",
#                 {"error": str(e)},
#             )

#     return render(request, "auth/signup.html")
def signup_ui_view(request):
    if request.method == "POST":
        tenant_name = request.POST["tenant_name"]
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]

        # 1️⃣ Call signup API
        signup_res = requests.post(
            f"{settings.API_BASE_URL}/tenants/signup/",
            json={
                "tenant_name": tenant_name,
                "username": username,
                "password": password,
                "email": email,
            },
            # timeout=5,
        )

        if signup_res.status_code != 201:
            return render(
                request,
                "auth/signup.html",
                {"error": "Signup failed"},
            )

        # 2️⃣ Login via JWT
        login_res = requests.post(
            f"{settings.API_BASE_URL}/api/v1/auth/login/",
            json={
                "username": username,
                "password": password,
            },
            timeout=5,
        )

        if login_res.status_code != 200:
            return render(
                request,
                "auth/signup.html",
                {"error": "Login failed after signup"},
            )

        data = login_res.json()

        # 3️⃣ Store JWT
        request.session["access_token"] = data["access"]
        request.session["refresh_token"] = data["refresh"]
        request.session["tenant_id"] = data["tenant_id"]
        request.session["role"] = data["role"]
        request.session.save()

        return redirect("project-list")

    return render(request, "auth/signup.html")
# def login_ui_view(request):
#     if request.method == "POST":
#         response = requests.post(
#             f"{settings.API_BASE_URL}/api/v1/auth/login/",
#             json={
#                 "username": request.POST["username"],
#                 "password": request.POST["password"],
#             },
#             headers={
#                 "X-Tenant-ID": request.session.get("tenant_id"),
#             },
#             timeout=5,
#         )

#         if response.status_code == 200:
#             request.session["user"] = response.json()
#             user_data = response.json()
#             user = User.objects.get(id=user_data['id'])
#             request.session["tenant_id"] = str(user.tenant.id)
#             return redirect("project-list") 

#         return render(
#             request,
#             "auth/login.html",
#             {"error": "Invalid credentials"},
#         )

#     return render(request, "auth/login.html")
def login_ui_view(request):
    if request.method == "POST":
        response = requests.post(
            f"{settings.API_BASE_URL}/api/v1/auth/login/",
            json={
                "username": request.POST["username"],
                "password": request.POST["password"],
            },
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()

            request.session["access_token"] = data["access"]
            request.session["refresh_token"] = data["refresh"]

            # Optional (useful for UI logic)
            request.session["role"] = data.get("role")
            request.session["tenant_id"] = data.get("tenant_id")
            request.session["is_authenticated"] = True

            request.session.save()

            return redirect("project-list")

        return render(
            request,
            "auth/login.html",
            {"error": "Invalid username or password"},
        )

    return render(request, "auth/login.html")


def logout_ui_view(request):
    logout(request)
    request.session.flush()
    return redirect("login-ui")


def user_list_ui(request):
    tenant_id = request.session.get("tenant_id", str(request.user.tenant.id))

    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/users/",
        headers={
            "X-Tenant-ID": tenant_id,
        },
        timeout=5,
    )

    return render(
        request,
        "users/list.html",
        {"users": response.json()},
    )


def user_create_ui(request):
    tenant_id = request.session.get("tenant_id", str(request.user.tenant.id))

    if request.method == 'POST':
        response = requests.post(
            f"{settings.API_BASE_URL}/api/v1/users/",
            json={
                'username': request.POST['username'],
                'email': request.POST['email'],
                'password': request.POST['password'],
                'role': request.POST['role'],
            },
            headers={
                "X-Tenant-ID": tenant_id,
            },
            timeout=5,
        )
        if response.status_code == 201:
            return redirect('user-list')
        else:
            try:
                error_data = response.json()
                error = error_data.get('detail', str(error_data))
            except requests.exceptions.JSONDecodeError:
                error = f"API Error: {response.status_code} - {response.text[:100]}"
            return render(request, 'users/create.html', {'error': error})

    return render(request, 'users/create.html')


def user_update_ui(request, user_id):
    tenant_id = request.session.get("tenant_id", str(request.user.tenant.id))

    if request.method == 'POST':
        data = {
            'username': request.POST['username'],
            'email': request.POST['email'],
            'role': request.POST['role'],
        }
        if request.POST.get('password'):
            data['password'] = request.POST['password']
        response = requests.put(
            f"{settings.API_BASE_URL}/api/v1/users/{user_id}/",
            json=data,
            headers={"X-Tenant-ID": tenant_id},
            timeout=5,
        )
        if response.status_code == 200:
            return redirect('user-list')
        else:
            error = response.json()
            return render(request, 'users/update.html', {'error': error, 'user_id': user_id})

    # GET: fetch current data
    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/users/{user_id}/",
        headers={"X-Tenant-ID": tenant_id},
        timeout=5,
    )
    if response.status_code == 200:
        user = response.json()
        return render(request, 'users/update.html', {'user': user})
    else:
        return redirect('user-list')


def user_delete_ui(request, user_id):
    tenant_id = request.session.get("tenant_id", str(request.user.tenant.id))

    if request.method == 'POST':
        response = requests.delete(
            f"{settings.API_BASE_URL}/api/v1/users/{user_id}/",
            headers={"X-Tenant-ID": tenant_id},
            timeout=5,
        )
        return redirect('user-list')

    # GET: show confirmation
    response = requests.get(
        f"{settings.API_BASE_URL}/api/v1/users/{user_id}/",
        headers={"X-Tenant-ID": tenant_id},
        timeout=5,
    )
    if response.status_code == 200:
        user = response.json()
        return render(request, 'users/delete.html', {'user': user})
    else:
        return redirect('user-list')


def tenant_list_ui(request):
    # Assuming master user has role ADMIN or special check
    if request.user.role != 'ADMIN':
        return redirect('project-list')
    
    tenants = Tenant.objects.all()
    return render(request, 'system/tenant_list.html', {'tenants': tenants})


def tenant_create_ui(request):
    if request.user.role != 'ADMIN':
        return redirect('project-list')
    
    if request.method == 'POST':
        tenant_name = request.POST['tenant_name']
        admin_username = request.POST['admin_username']
        admin_password = request.POST['admin_password']
        email = request.POST['email']
        
        try:
            tenant, user = TenantService.create_tenant(
                tenant_name=tenant_name,
                admin_username=admin_username,
                admin_password=admin_password,
            )
            user.email = email
            user.save()
            return redirect('tenant-list')
        except Exception as e:
            return render(request, 'system/tenant_create.html', {'error': str(e)})
    
def tenant_select_ui(request, tenant_id):
    if request.user.role != 'ADMIN':
        return redirect('project-list')
    
    request.session["tenant_id"] = str(tenant_id)
    return redirect('user-list')