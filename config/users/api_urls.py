from django.urls import path
from users.api.views import LoginAPIView, UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view()),
    path("users/", UserListCreateAPIView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserRetrieveUpdateDestroyAPIView.as_view(), name="user-detail"),
]
