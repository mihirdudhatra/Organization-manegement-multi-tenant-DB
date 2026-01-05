from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework import generics
from system.models import User
from users.api.serializers import UserSerializer, CustomTokenObtainPairSerializer, UserUpdateSerializer
from users.services.user_service import UserService
from rest_framework_simplejwt.views import TokenObtainPairView



class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return UserService.list_users(user=self.request.user)

    def perform_create(self, serializer):
        UserService.create_user(
            user=self.request.user,
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            role=serializer.validated_data['role'],
        )


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def perform_update(self, serializer):
        target_user = self.get_object()
        UserService.update_user(
            user=self.request.user,
            target_user=target_user,
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        UserService.delete_user(user=self.request.user, target_user=instance)
