from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import (
    UserProfileViewSet,
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    get_user_info
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('me/', get_user_info, name='user_info'),
]
