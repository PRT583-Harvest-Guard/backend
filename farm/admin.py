from django.contrib import admin
from farm. models import Farm, BoundaryPoint, ObservationPoint, InspectionSuggestion, InspectionObservation


# Register your models here.

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'plant_type', 'created_at', 'user')
    list_filter = ('plant_type', 'created_at')
    search_fields = ('name', 'user__email')
    ordering = ('-created_at',)
    list_per_page = 20

@admin.register(BoundaryPoint)
class BoundaryPointAdmin(admin.ModelAdmin):
    list_display = ('farm', 'latitude', 'longitude', 'description', 'timestamp')
    list_filter = ('farm',)
    search_fields = ('farm__name', 'description')
    ordering = ('-timestamp',)
    list_per_page = 20


@admin.register(ObservationPoint)
class ObservationPointAdmin(admin.ModelAdmin):
    list_display = ('farm', 'latitude', 'longitude', 'observation_status', 'name', 'segment', 'created_at')
    list_filter = ('farm', 'observation_status', 'segment')
    search_fields = ('farm__name', 'name')
    ordering = ('-created_at',)
    list_per_page = 20

@admin.register(InspectionSuggestion)
class InspectionSuggestionAdmin(admin.ModelAdmin):
    list_display = ('target_entity', 'confidence_level', 'created_at')
    list_filter = ('target_entity',)
    search_fields = ('target_entity',)
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(InspectionObservation)
class InspectionObservationAdmin(admin.ModelAdmin):
    list_display = ('created_at', )
    search_fields = ('observation_point__name',)
    ordering = ('-created_at',)
    list_per_page = 20
