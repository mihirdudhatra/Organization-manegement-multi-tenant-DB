import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_postgres_database(
    *,
    db_name: str,
    user: str,
    password: str,
    host: str,
    port: str,
) -> None:
    """
    Time: O(1)
    Space: O(1)
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host=host,
        port=port,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()
    cursor.execute(f'CREATE DATABASE "{db_name}"')
    cursor.close()
    conn.close()

from django.conf import settings
from django.db import connections
import copy


def register_tenant_db(alias: str, db_config: dict) -> None:
    """
    Safely registers a tenant DB with all required Django keys.
    """

    base = copy.deepcopy(settings.DATABASES["default"])
    base.update(db_config)

    base.setdefault("ATOMIC_REQUESTS", False)
    base.setdefault("AUTOCOMMIT", True)
    base.setdefault("CONN_HEALTH_CHECKS", False)
    base.setdefault("OPTIONS", {})
    base.setdefault("TIME_ZONE", "UTC")

    connections.databases[alias] = base
