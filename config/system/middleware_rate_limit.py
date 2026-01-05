# import time
# from django.conf import settings
# from django.http import JsonResponse
# from django.utils.deprecation import MiddlewareMixin
# import redis
#
# from system.tenant_context import get_current_tenant_db as get_current_tenant
#
# # Simple per-tenant token-bucket rate limiter using Redis
# # Configurable via settings.RATE_LIMIT = {"requests": 100, "window_seconds": 60}
#
#
# class TenantRateLimitMiddleware(MiddlewareMixin):
#     def __init__(self, get_response=None):
#         super().__init__(get_response)
#         redis_url = getattr(settings, "REDIS_URL", "redis://redis:6379/1")
#         try:
#             self.redis = redis.from_url(redis_url)
#         except Exception:
#             self.redis = None
#         cfg = getattr(settings, "RATE_LIMIT", {"requests": 100, "window_seconds": 60})
#         self.max_requests = int(cfg.get("requests", 100))
#         self.window = int(cfg.get("window_seconds", 60))
#
#     def process_request(self, request):
#         tenant = get_current_tenant()
#         # apply only to authenticated users (and API endpoints)
#         if not tenant:
#             return None
#
#         key = f"rl:tenant:{tenant.id}:window"
#         now = int(time.time())
#         window_start = now - (now % self.window)
#         redis_key = f"{key}:{window_start}"
#
#         # If Redis isn't available, fail-open to avoid blocking traffic
#         if not self.redis:
#             return None
#
#         try:
#             count = self.redis.incr(redis_key)
#             if count == 1:
#                 # set expiry slightly longer than window
#                 self.redis.expire(redis_key, self.window + 5)
#         except Exception:
#             return None
#
#         if count > self.max_requests:
#             try:
#                 ttl = self.redis.ttl(redis_key) or self.window
#             except Exception:
#                 ttl = self.window
#             return JsonResponse({"detail": "Rate limit exceeded", "retry_after": ttl}, status=429)
#
#         return None
import time
import redis
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class TenantRateLimitMiddleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        super().__init__(get_response)

        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
        self.redis = None

        try:
            self.redis = redis.from_url(
                redis_url,
                socket_connect_timeout=1,
                socket_timeout=1,
                retry_on_timeout=True,
            )
        except Exception:
            self.redis = None

        cfg = getattr(
            settings,
            "RATE_LIMIT",
            {"requests": 100, "window_seconds": 60},
        )

        self.max_requests = int(cfg.get("requests", 100))
        self.window = int(cfg.get("window_seconds", 60))

    def process_request(self, request):
        if not request.path.startswith("/api/"):
            return None

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None

        tenant = getattr(user, "tenant", None)
        if not tenant:
            return None

        if not self.redis:
            return None

        now = int(time.time())
        window_start = now - (now % self.window)

        redis_key = f"rl:tenant:{tenant.id}:{window_start}"

        try:
            count = self.redis.incr(redis_key)
            if count == 1:
                self.redis.expire(redis_key, self.window + 5)
        except Exception:
            return None 

        if count > self.max_requests:
            try:
                retry_after = self.redis.ttl(redis_key)
            except Exception:
                retry_after = self.window

            response = JsonResponse(
                {
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after,
                },
                status=429,
            )
            response["Retry-After"] = retry_after
            return response

        return None
