from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomAccountManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must be assigned to is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be assigned to is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)
    



class User(AbstractUser, PermissionsMixin):
    # role choices
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('stakeholder', 'Stakeholder'),
    ]
    # fields
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('name'), max_length=255)
    phone = models.CharField(_('phone number'), max_length=255, blank=True)
    role = models.CharField(_('role'), max_length=255, choices=ROLE_CHOICES, default='farmer')
    address = models.CharField(_('address'), max_length=255, blank=True)
    bio = models.TextField(_('bio'), blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    username = None

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name
    
    
# Create your models here.
