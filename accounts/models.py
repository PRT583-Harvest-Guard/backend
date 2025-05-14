from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class CustomAccountManager(BaseUserManager):
    def create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError(_('You must provide a phone number'))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must be assigned to is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be assigned to is_superuser=True'))
        
        return self.create_user(phone_number, password, **extra_fields)
    



class User(AbstractUser, PermissionsMixin):
    # role choices
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('stakeholder', 'Stakeholder'),
    ]
    # fields
    email = models.EmailField(_('email address'),blank=True, null=True, unique=True)
    name = models.CharField(_('name'), max_length=255)
    phone_number = PhoneNumberField(unique=True, null=False, blank=False)
    role = models.CharField(_('role'), max_length=255, choices=ROLE_CHOICES, default='farmer')
    address = models.CharField(_('address'), max_length=255, blank=True)
    bio = models.TextField(_('bio'), blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # Feature flag for MVP features
    is_mvp = models.BooleanField(default=True)
    # MFA fields (feature-flagged)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True, null=True)

    username = None

    objects = CustomAccountManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']


    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name


    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Extended user profile model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Sync-related fields
    last_synced = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('synced', 'Synced'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"Profile for {self.user.name}"


class RefreshToken(models.Model):
    """
    Model to store refresh tokens in the database.
    This allows for token invalidation (logout) and tracking.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)
    device_info = models.TextField(blank=True, null=True)  # Store device information for mobile app

    def __str__(self):
        return f"Token for {self.user.name} - {'Valid' if self.is_valid else 'Invalid'}"


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens/OTPs.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=6)  # 6-digit OTP
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Reset token for {self.user.name} - {'Used' if self.is_used else 'Not Used'}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
