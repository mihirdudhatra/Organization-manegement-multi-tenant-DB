import uuid
from django.conf import settings
from django.db import connections, transaction
from system.services.db_utils import create_postgres_database, register_tenant_db
from system.services.migration_utils import migrate_tenant_database
from system.models import Tenant, TenantDatabase, User
from system.tenant_context import set_current_tenant_db as set_current_tenant
from rest_framework.exceptions import ValidationError
from users.models import TenantUser


class TenantService:
    @staticmethod
    # @transaction.atomic
    def create_tenant(
        *,
        tenant_name: str,
        admin_username: str,
        admin_password: str,
    ) -> Tenant:
        """
        Creates tenant + database + admin user.

        Time: O(M) where M = number of migrations
        Space: O(1)
        """
        if Tenant.objects.filter(name=tenant_name).exists():
            raise ValidationError(
                {"tenant_name": "Tenant with this name already exists"}
            )

        # create tenant in master db
        tenant = Tenant.objects.create(name=tenant_name)

        # Prepare DB config
        db_name = f"tenant_{tenant.id.hex}"

        create_postgres_database(
            db_name=db_name,
            user=settings.DB_SUPERUSER,
            password=settings.DB_SUPERUSER_PASSWORD,
            host="localhost",
            port="5432",
        )

        # save db credentials
        tenant_db = TenantDatabase.objects.create(
            tenant=tenant,
            db_name=db_name,
            db_user=settings.DB_SUPERUSER,
            db_password=settings.DB_SUPERUSER_PASSWORD,
            db_host="localhost",
            db_port="5432",
        )

        register_tenant_db(
            alias="tenant",
            db_config={
                "NAME": tenant_db.db_name,
                "USER": tenant_db.db_user,
                "PASSWORD": tenant_db.db_password,
                "HOST": tenant_db.db_host,
                "PORT": tenant_db.db_port,
                "CONN_MAX_AGE": 60,
            },
        )

        # initialize tenant db connection
        connections.databases["tenant"] = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": tenant_db.db_name,
            "USER": tenant_db.db_user,
            "PASSWORD": tenant_db.db_password,
            "HOST": tenant_db.db_host,
            "PORT": tenant_db.db_port,
            "CONN_MAX_AGE": 60,
            "ATOMIC_REQUESTS": False,
            "AUTOCOMMIT": True,
            "OPTIONS": {},
            "TIME_ZONE": "UTC", 
            "CONN_HEALTH_CHECKS": False,
        }

        # runs migrations
        migrate_tenant_database("tenant")

        set_current_tenant(tenant)

        # create admin user in master DB
        admin_user = User.objects.create(
            username=admin_username,
            password=admin_password,
            role=User.Role.ADMIN,
            tenant=tenant,
            is_staff=True,
            is_superuser=True,
        )

        # add user to tenant DB
        user = TenantUser.objects.using("tenant").create(
            auth_user = admin_user.id,
            tenant = tenant.id,
            role ="Admin"
        )

        return tenant, admin_user
