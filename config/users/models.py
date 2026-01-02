from django.db import models

class TenantUser(models.Model):
    _tenant_model = True
    auth_user = models.ImageField()
    tenant = models.ImageField()
    role = models.CharField(
        max_length=20,
        choices=[("admin", "Admin"), ("manager", "Manager"), ("member", "Member")]
    )
