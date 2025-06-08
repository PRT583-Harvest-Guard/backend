from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
import random
import string

from accounts.models import UserProfile, RefreshToken, PasswordResetToken

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    """
    Serializer for user registration.
    """
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "phone_number", "email", "password", "password_confirm", "name", "is_mvp")
        extra_kwargs = {
            "password": {"write_only": True},
            "is_mvp": {"read_only": True}
        }
    
    def validate(self, attrs):
        # Check if is_mvp is True (feature flag)
        if not self.context['request'].user.is_authenticated and not getattr(self.context['request'].user, 'is_mvp', True):
            raise serializers.ValidationError(_("This feature is not available yet."))
        
        # Validate password
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": _("Passwords do not match.")})
        
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({"password": list(e)})
        
        return attrs


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    phone_number = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    device_info = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        device_info = attrs.get('device_info', '')
        
        if phone_number and password:
            user = authenticate(request=self.context.get('request'), 
                               username=phone_number, password=password)
            
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "phone_number" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        
        # Generate tokens
        refresh = JWTRefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Store refresh token in database
        expires_at = timezone.now() + timedelta(days=1)  # Match SIMPLE_JWT settings
        RefreshToken.objects.create(
            user=user,
            token=refresh_token,
            expires_at=expires_at,
            device_info=device_info
        )
        
        attrs['user'] = user
        attrs['access_token'] = access_token
        attrs['refresh_token'] = refresh_token
        return attrs


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout.
    """
    refresh_token = serializers.CharField()
    
    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        
        try:
            token = RefreshToken.objects.get(token=refresh_token, is_valid=True)
            token.is_valid = False
            token.save()
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError(_('Invalid token.'))
        
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for refreshing access token.
    """
    refresh_token = serializers.CharField()
    
    def validate(self, attrs):
        refresh_token_str = attrs.get('refresh_token')
        
        try:
            # Check if token exists and is valid
            token_obj = RefreshToken.objects.get(token=refresh_token_str, is_valid=True)
            
            # Check if token is expired
            if token_obj.expires_at < timezone.now():
                token_obj.is_valid = False
                token_obj.save()
                raise serializers.ValidationError(_('Refresh token expired.'))
            
            # Create new tokens
            refresh = JWTRefreshToken(refresh_token_str)
            access_token = str(refresh.access_token)
            
            # If ROTATE_REFRESH_TOKENS is True, create new refresh token
            if getattr(settings, 'SIMPLE_JWT', {}).get('ROTATE_REFRESH_TOKENS', False):
                # Invalidate old token
                token_obj.is_valid = False
                token_obj.save()
                
                # Create new refresh token
                new_refresh = JWTRefreshToken.for_user(token_obj.user)
                new_refresh_token = str(new_refresh)
                
                # Store new refresh token
                expires_at = timezone.now() + timedelta(days=1)
                RefreshToken.objects.create(
                    user=token_obj.user,
                    token=new_refresh_token,
                    expires_at=expires_at,
                    device_info=token_obj.device_info
                )
                
                attrs['refresh_token'] = new_refresh_token
            
            attrs['access_token'] = access_token
            return attrs
            
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError(_('Invalid refresh token.'))
        except Exception as e:
            raise serializers.ValidationError(str(e))


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password request.
    """
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        email = attrs.get('email')
        
        if not phone_number and not email:
            raise serializers.ValidationError(_('Please provide either phone number or email.'))
        
        # Find user by phone or email
        if phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                raise serializers.ValidationError(_('User with this phone number does not exist.'))
        else:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(_('User with this email does not exist.'))
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store OTP
        expires_at = timezone.now() + timedelta(minutes=10)
        PasswordResetToken.objects.create(
            user=user,
            token=otp,
            expires_at=expires_at
        )
        
        attrs['user'] = user
        attrs['otp'] = otp
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting password with OTP.
    """
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        email = attrs.get('email')
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if not phone_number and not email:
            raise serializers.ValidationError(_('Please provide either phone number or email.'))
        
        # Find user by phone or email
        if phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                raise serializers.ValidationError(_('User with this phone number does not exist.'))
        else:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(_('User with this email does not exist.'))
        
        # Verify OTP
        try:
            token = PasswordResetToken.objects.get(
                user=user,
                token=otp,
                is_used=False,
                expires_at__gt=timezone.now()
            )
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError(_('Invalid or expired OTP.'))
        
        # Validate passwords
        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})
        
        try:
            validate_password(new_password)
        except Exception as e:
            raise serializers.ValidationError({'new_password': list(e)})
        
        # Mark token as used
        token.is_used = True
        token.save()
        
        attrs['user'] = user
        return attrs
    
    def save(self):
        user = self.validated_data['user']
        password = self.validated_data['new_password']
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        user = self.context['request'].user
        
        # Check old password
        if not user.check_password(old_password):
            raise serializers.ValidationError({'old_password': _('Wrong password.')})
        
        # Validate new password
        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})
        
        # try:
        #     validate_password(new_password, user=user)
        # except Exception as e:
        #     raise serializers.ValidationError({'new_password': list(e)})
        
        return attrs
    
    def save(self):
        user = self.context['request'].user
        password = self.validated_data['new_password']
        user.set_password(password)
        user.save()
        return user


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
