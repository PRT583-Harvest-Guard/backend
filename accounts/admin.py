from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile, RefreshToken, PasswordResetToken


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'email', 'name', 'role', 'is_active', 'is_staff', 'is_mvp')
    list_filter = ('role', 'is_active', 'is_staff', 'is_mvp', 'mfa_enabled')
    search_fields = ('phone_number', 'email', 'name')
    ordering = ('phone_number',)
    inlines = (UserProfileInline,)
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('name', 'email', 'role', 'address', 'bio')}),
        (_('Feature flags'), {'fields': ('is_mvp',)}),
        (_('MFA'), {'fields': ('mfa_enabled', 'mfa_secret')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'name', 'password1', 'password2'),
        }),
    )


class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_valid')
    list_filter = ('is_valid', 'created_at', 'expires_at')
    search_fields = ('user__phone_number', 'user__email', 'user__name', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('token',)
    
    def has_add_permission(self, request):
        return False


class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__phone_number', 'user__email', 'user__name', 'token')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)
admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)
