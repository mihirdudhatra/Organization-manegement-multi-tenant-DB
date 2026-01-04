# projects/models.py
from django.conf import settings
from django.db import models


class Project(models.Model):
    _tenant_model = True
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    created_by = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self) -> str:
        return self.name
