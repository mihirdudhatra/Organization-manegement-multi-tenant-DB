from .celery import app as celery_app

# Expose Celery app as a module-level variable for Django startup
__all__ = ('celery_app',)
