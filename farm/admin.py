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
                '<path:object_id>/export-documents/',
                self.admin_site.admin_view(self.export_farm_documents),
                name='farm-export-documents',
            ),
        ]
        return custom_urls + urls
    
    def export_farm_documents(self, request, object_id):
        """Export farm documents as PDF."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        farm = Farm.objects.get(pk=object_id)
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object, using the buffer as its "file"
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        
        # Get the default style sheet
        styles = getSampleStyleSheet()
        
        # Create a list to store the flowables
        elements = []
        
        # Add farm information
        elements.append(Paragraph(f"Farm Information", styles['Heading1']))
        elements.append(Spacer(1, 12))
        
        farm_data = [
            ["Farm Name:", farm.name],
            ["Size:", str(farm.size)],
            ["Plant Type:", farm.plant_type],
            ["Created At:", farm.created_at.strftime("%Y-%m-%d %H:%M:%S")],
            ["User:", farm.user.name]
        ]
        
        farm_table = Table(farm_data, colWidths=[100, 400])
        farm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(farm_table)
        elements.append(Spacer(1, 20))
        
        # Add boundary points
        elements.append(Paragraph("Boundary Points", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        boundary_data = [["Latitude", "Longitude", "Description", "Timestamp"]]
        for bp in farm.boundary_points.all():
            boundary_data.append([
                str(bp.latitude),
                str(bp.longitude),
                bp.description or "",
                bp.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        if len(boundary_data) > 1:  # If there are boundary points
            boundary_table = Table(boundary_data, colWidths=[100, 100, 200, 150])
            boundary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(boundary_table)
        else:
            elements.append(Paragraph("No boundary points found.", styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Add observation points
        elements.append(Paragraph("Observation Points", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        observation_data = [["Latitude", "Longitude", "Status", "Name", "Segment", "Confidence", "Target"]]
        for op in farm.observation_points.all():
            observation_data.append([
                str(op.latitude),
                str(op.longitude),
                op.observation_status,
                op.name or "",
                str(op.segment),
                op.confidence_level or "",
                op.target_entity or ""
            ])
        
        if len(observation_data) > 1:  # If there are observation points
            observation_table = Table(observation_data, colWidths=[80, 80, 80, 100, 60, 80, 100])
            observation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(observation_table)
        else:
            elements.append(Paragraph("No observation points found.", styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Add inspection suggestions
        elements.append(Paragraph("Inspection Suggestions", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        suggestion_data = [["Target Entity", "Confidence Level", "Area Size", "Density of Plant", "Created At"]]
        for suggestion in farm.inspection_suggestions.all():
            suggestion_data.append([
                suggestion.target_entity,
                suggestion.confidence_level,
                str(suggestion.area_size),
                str(suggestion.density_of_plant),
                suggestion.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        if len(suggestion_data) > 1:  # If there are inspection suggestions
            suggestion_table = Table(suggestion_data, colWidths=[120, 100, 80, 100, 150])
            suggestion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(suggestion_table)
        else:
            elements.append(Paragraph("No inspection suggestions found.", styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Add inspection observations
        elements.append(Paragraph("Inspection Observations", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        observation_data = [["Date", "Confidence", "Status", "Target Entity", "Severity"]]
        for observation in farm.observations.all():
            observation_data.append([
                observation.date.strftime("%Y-%m-%d %H:%M:%S"),
                observation.confidence,
                observation.status,
                observation.target_entity or "",
                observation.severity or ""
            ])
        
        if len(observation_data) > 1:  # If there are inspection observations
            observation_table = Table(observation_data, colWidths=[150, 80, 80, 120, 80])
            observation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(observation_table)
        else:
            elements.append(Paragraph("No inspection observations found.", styles['Normal']))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create the HttpResponse object with PDF header
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="farm_{farm.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        response.write(pdf)
        
        return response
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change_view to add export button."""
        extra_context = extra_context or {}
        extra_context['show_export_button'] = True
        extra_context['export_url'] = f'{object_id}/export-documents/'
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
