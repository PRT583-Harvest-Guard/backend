from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from accounts.models import UserProfile, User, RefreshToken, PasswordResetToken
from accounts.serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    ProfilePictureSerializer,
    UserCreateSerializer,
    LoginSerializer,
    LogoutSerializer,
    TokenRefreshSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer
)


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle for login attempts.
    """
    scope = 'login'


class OTPRateThrottle(AnonRateThrottle):
    """
    Throttle for OTP requests.
    """
    scope = 'otp'


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserProfile model.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the profile for the authenticated user.
        """
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """
        Get the profile for the authenticated user.
        """
        return self.request.user.profile

    def list(self, request, *args, **kwargs):
        """
        Return the profile for the authenticated user.
        """
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], serializer_class=UserProfileUpdateSerializer)
    def update_profile(self, request):
        """
        Update the user profile.
        """
        profile = self.get_object()
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Update sync status
            profile.last_synced = timezone.now()
            profile.sync_status = 'synced'
            profile.save()

            return Response(UserProfileSerializer(profile).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        serializer_class=ProfilePictureSerializer,
        parser_classes=[MultiPartParser, FormParser]
    )
    def upload_picture(self, request):
        """
        Upload a profile picture.
        """
        profile = self.get_object()
        serializer = ProfilePictureSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Update sync status
            profile.last_synced = timezone.now()
            profile.sync_status = 'synced'
            profile.save()

            return Response(UserProfileSerializer(profile).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Sync the user profile from the mobile app.

        This endpoint returns the latest profile data from the server.
        """
        profile = self.get_object()

        # Update last_synced timestamp
        profile.last_synced = timezone.now()
        profile.sync_status = 'synced'
        profile.save()

        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        # Check if is_mvp feature flag is enabled
        if not getattr(request.user, 'is_mvp', True):
            return Response(
                {"detail": _("This feature is not available yet.")},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Set user as active by default for MVP
        user.is_active = True
        user.save()
        
        return Response(
            {"detail": _("User registered successfully.")},
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            "access_token": serializer.validated_data['access_token'],
            "refresh_token": serializer.validated_data['refresh_token'],
            "user": UserCreateSerializer(serializer.validated_data['user']).data
        })


class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout.
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({"detail": _("Successfully logged out.")})


class TokenRefreshView(generics.GenericAPIView):
    """
    API endpoint for refreshing access token.
    """
    serializer_class = TokenRefreshSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        response_data = {
            "access_token": serializer.validated_data['access_token']
        }
        
        # Include new refresh token if it was rotated
        if 'refresh_token' in serializer.validated_data:
            response_data["refresh_token"] = serializer.validated_data['refresh_token']
        
        return Response(response_data)


class ForgotPasswordView(generics.GenericAPIView):
    """
    API endpoint for forgot password request.
    """
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        
        # Send OTP via email if email is provided
        if user.email:
            try:
                send_mail(
                    subject="Password Reset OTP",
                    message=f"Your OTP for password reset is: {otp}. It is valid for 10 minutes.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't expose it to the user
                print(f"Error sending email: {str(e)}")
        
        # In a real implementation, you would send the OTP via SMS for phone_number
        # For now, we'll just return it in the response for testing purposes
        
        return Response({
            "detail": _("OTP has been sent to your email/phone."),
            "otp": otp  # Remove this in production
        })


class ResetPasswordView(generics.GenericAPIView):
    """
    API endpoint for resetting password with OTP.
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"detail": _("Password has been reset successfully.")})


class ChangePasswordView(generics.GenericAPIView):
    """
    API endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Invalidate all refresh tokens for security
        RefreshToken.objects.filter(user=request.user, is_valid=True).update(is_valid=False)
        
        return Response({"detail": _("Password has been changed successfully.")})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """
    Get information about the authenticated user.
    """
    user = request.user
    serializer = UserCreateSerializer(user)
    return Response(serializer.data)
