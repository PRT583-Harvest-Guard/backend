from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.models import UserProfile
from accounts.serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    ProfilePictureSerializer
)



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