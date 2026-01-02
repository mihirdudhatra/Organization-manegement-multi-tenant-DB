from django.core.management import call_command
from django.db import connections
from django.conf import settings


def migrate_tenant_database(db_alias: str) -> None:
    """
    Applies all migrations to tenant DB.
    """
    # call_command(
    #     "migrate",
    #     database=db_alias,
    #     interactive=False,
    # )
    for app in settings.TENANT_APPS:
        call_command(
            "migrate",
            app,
            database=db_alias,
            interactive=False,
            verbosity=0,
        )
