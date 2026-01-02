# from rest_framework import serializers
# from projects.models import Project


# class ProjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Project
#         fields = ["id", "name", "description", "created_at"]
# projects/api/serializers.py
from rest_framework import serializers
from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]
