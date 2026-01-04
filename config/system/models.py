from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
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

# class UserManager(BaseUserManager):
#     def create_user(self, username, password=None):
#         if not username:
#             raise ValueError("Username is required")
#         user = self.model(username=username)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, username, password):
#         user = self.create_user(username, password)
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user


class User(AbstractUser):
    """
    System User (MASTER DB).
    Uses Django auth + UUID primary key.
    """

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,)
    class Role(models.TextChoices):
        ADMIN = "ADMIN"
        MANAGER = "MANAGER"
        MEMBER = "MEMBER"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    class Meta:
        db_table = "system_user"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

