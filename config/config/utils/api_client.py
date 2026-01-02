import requests
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Dict, Any


def _build_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return settings.API_BASE_URL.rstrip("/") + "/" + path.lstrip("/")


def _default_headers(request) -> Dict[str, str]:
    headers = {}
    tenant_id = request.session.get("tenant_id")
    if tenant_id:
        headers["X-Tenant-ID"] = str(tenant_id)

    if request.user.is_authenticated:
        headers["X-User-ID"] = str(request.user.id)

    return headers


def api_request(request, method: str, path: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, timeout: int = 5):
    url = _build_url(path)
    headers = _default_headers(request)

    # small retry (1 retry)
    for attempt in range(2):
        try:
            resp = requests.request(method, url, json=json, params=params, headers=headers, timeout=timeout)
            return resp
        except requests.RequestException:
            if attempt == 1:
                raise
    # fallback
    raise RuntimeError("unreachable")


def api_get(request, path, params=None, cache_for: Optional[int] = None):
    tenant_id = request.session.get("tenant_id")
    cache_key = None
    if cache_for:
        cache_key = f"ui:api:get:{tenant_id}:{path}:{params}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    print('path: ', path)
    print('params: ', params)
    resp = api_request(request, "GET", path, params=params)
    print('resp: ', resp.data)
    if resp.status_code == 200:
        data = resp.json()
        if cache_for and cache_key:
            cache.set(cache_key, data, cache_for)
        return data
    else:
        # raise for caller to handle
        resp.raise_for_status()


def api_post(request, path, json=None):
    resp = api_request(request, "POST", path, json=json)
    return resp


def api_patch(request, path, json=None):
    resp = api_request(request, "PATCH", path, json=json)
    return resp


def api_delete(request, path):
    resp = api_request(request, "DELETE", path)
    return resp
