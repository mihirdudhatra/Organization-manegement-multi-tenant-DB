from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Tenant(models.Model):
    """
    Represents an organization.
    Lives in MASTER DB.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TenantDatabase(models.Model):
    """
    DB connection details per tenant.
    """
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255)
    db_user = models.CharField(max_length=255)
    db_password = models.CharField(max_length=255)
    db_host = models.CharField(max_length=255, default="localhost")
    db_port = models.CharField(max_length=10, default="5432")

class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    System User (MASTER DB ONLY)
    No Django Groups
    No PermissionsMixin
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN"
        MANAGER = "MANAGER"
        MEMBER = "MEMBER"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="users",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"
