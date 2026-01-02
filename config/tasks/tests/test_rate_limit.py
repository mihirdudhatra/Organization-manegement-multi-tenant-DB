import pytest
from django.test import Client
from system.models import User
from projects.models import Project
from system.models import Tenant
from system.tenant_context import set_current_tenant


@pytest.mark.django_db
def test_rate_limit_enforced(monkeypatch):
    # quick smoke test for middleware logic: create a tenant and simulate requests
    tenant = Tenant.objects.create(name="T1")
    set_current_tenant(tenant)

    user = User.objects.create_user(username="u1", password="pw")
    project = Project.objects.create(name="p", created_by=user)

    c = Client()
    # assuming a simple view exists at /projects/ (we won't actually call network)
    # Instead, exercise middleware directly by calling process_request
    from system.middleware_rate_limit import TenantRateLimitMiddleware
    mw = TenantRateLimitMiddleware()

    class DummyRequest:
        method = 'GET'
    req = DummyRequest()
    req._dont_enforce_csrf_checks = True

    # call until one beyond limit
    cfg = getattr(__import__('config.settings', fromlist=['settings']), 'settings').RATE_LIMIT
    max_req = cfg.get('requests', 100)
    for _ in range(max_req):
        assert mw.process_request(req) is None

    res = mw.process_request(req)
    assert res.status_code == 429
