from django.contrib import admin

# Register your models here.

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
