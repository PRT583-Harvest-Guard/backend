from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from accounts.models import UserProfile


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = ("id", "email", "password", "name")
        extra_kwargs = {"password": {"write_only": True}}


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    user = UserCreateSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_synced', 'sync_status')

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating UserProfile.
    """
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = (
            'first_name', 'last_name', 'email', 'phone_number',
            'bio', 'company', 'job_title', 'address'
        )

    def update(self, instance, validated_data):
        # Update User model fields
        user = instance.user
        if 'first_name' in validated_data:
            user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user.last_name = validated_data.pop('last_name')
        if 'email' in validated_data:
            user.email = validated_data.pop('email')
        user.save()

        # Update UserProfile fields
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance




class ProfilePictureSerializer(serializers.ModelSerializer):
    """
    Serializer for updating profile picture.
    """
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)