from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from farm.models import Farm, BoundaryPoint, ObservationPoint, InspectionSuggestion, InspectionObservation
import csv
from datetime import datetime


# Register your models here.

class BoundaryPointInline(admin.TabularInline):
    model = BoundaryPoint
    extra = 0
    fields = ('latitude', 'longitude', 'description')
    can_delete = True
    show_change_link = True

class ObservationPointInline(admin.TabularInline):
    model = ObservationPoint
    extra = 0
    fields = ('latitude', 'longitude', 'observation_status', 'name', 'segment', 'confidence_level', 'target_entity')
    can_delete = True
    show_change_link = True

class InspectionSuggestionInline(admin.TabularInline):
    model = InspectionSuggestion
    extra = 0
    fields = ('target_entity', 'confidence_level', 'area_size', 'density_of_plant')
    can_delete = True
    show_change_link = True
    fk_name = 'property_location'

class InspectionObservationInline(admin.TabularInline):
    model = InspectionObservation
    extra = 0
    fields = ('date', 'inspection', 'confidence', 'status', 'target_entity', 'severity')
    can_delete = True
    show_change_link = True

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'plant_type', 'created_at', 'user')
    list_filter = ('plant_type', 'created_at')
    search_fields = ('name', 'user__email')
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [BoundaryPointInline, ObservationPointInline, InspectionSuggestionInline, InspectionObservationInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:farm_id>/export-documents/',
                self.admin_site.admin_view(self.export_farm_documents),
                name='farm-export-documents',
            ),
        ]
        return custom_urls + urls
    
    def export_farm_documents(self, request, farm_id):
        """Export farm documents as CSV."""
        farm = Farm.objects.get(pk=farm_id)
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="farm_{farm.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Farm Information'])
        writer.writerow(['Name', 'Size', 'Plant Type', 'Created At', 'User'])
        writer.writerow([farm.name, farm.size, farm.plant_type, farm.created_at, farm.user.name])
        
        writer.writerow([])  # Empty row for separation
        
        # Add boundary points
        writer.writerow(['Boundary Points'])
        writer.writerow(['Latitude', 'Longitude', 'Description', 'Timestamp'])
        for bp in farm.boundary_points.all():
            writer.writerow([bp.latitude, bp.longitude, bp.description, bp.timestamp])
        
        writer.writerow([])  # Empty row for separation
        
        # Add observation points
        writer.writerow(['Observation Points'])
        writer.writerow(['Latitude', 'Longitude', 'Status', 'Name', 'Segment', 'Created At'])
        for op in farm.observation_points.all():
            writer.writerow([op.latitude, op.longitude, op.observation_status, op.name, op.segment, op.created_at])
        
        writer.writerow([])  # Empty row for separation
        
        # Add inspection suggestions
        writer.writerow(['Inspection Suggestions'])
        writer.writerow(['Target Entity', 'Confidence Level', 'Area Size', 'Density of Plant', 'Created At'])
        for suggestion in farm.inspection_suggestions.all():
            writer.writerow([suggestion.target_entity, suggestion.confidence_level, suggestion.area_size, suggestion.density_of_plant, suggestion.created_at])
        
        writer.writerow([])  # Empty row for separation
        
        # Add inspection observations
        writer.writerow(['Inspection Observations'])
        writer.writerow(['Date', 'Confidence', 'Status', 'Target Entity', 'Severity', 'Created At'])
        for observation in farm.observations.all():
            writer.writerow([observation.date, observation.confidence, observation.status, observation.target_entity, observation.severity, observation.created_at])
        
        return response
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change_view to add export button."""
        extra_context = extra_context or {}
        extra_context['show_export_button'] = True
        extra_context['export_url'] = f'../../../farm/farm/{object_id}/export-documents/'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

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
    list_display = ('target_entity', 'confidence_level', 'property_location', 'area_size', 'density_of_plant', 'user', 'created_at')
    list_filter = ('confidence_level', 'property_location', 'user')
    search_fields = ('target_entity', 'property_location__name', 'user__name')
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(InspectionObservation)
class InspectionObservationAdmin(admin.ModelAdmin):
    list_display = ('target_entity', 'status', 'farm', 'confidence', 'severity', 'date', 'created_at')
    list_filter = ('status', 'confidence', 'severity', 'farm')
    search_fields = ('target_entity', 'farm__name')
    ordering = ('-created_at',)
    list_per_page = 20
