from django.contrib import admin
from .models import Farm, Block




class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_point_1', 'location_point_2', 'location_point_3', 'location_point_4')
    search_fields = ('name', 'location_point_1', 'location_point_2', 'location_point_3', 'location_point_4')
    list_filter = ('name', 'location_point_1', 'location_point_2', 'location_point_3', 'location_point_4')
    ordering = ('name',)


admin.site.register(Farm, FarmAdmin)