from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "users"

urlpatterns = [
    # JWT Authentication
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Registration
    path("register/", views.RegisterView.as_view(), name="register"),
    # Profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    # Admin
    path("users/", views.AdminUserListView.as_view(), name="admin_user_list"),
    path("users/<uuid:pk>/", views.AdminUserDetailView.as_view(), name="admin_user_detail"),
]
