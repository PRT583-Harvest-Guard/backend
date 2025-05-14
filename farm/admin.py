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
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.platypus import (
            SimpleDocTemplate,
            Table,
            TableStyle,
            Paragraph,
            Spacer,
        )
        from io import BytesIO
        
        farm = Farm.objects.get(pk=object_id)
    # Create buffer and PDF document with tight margins
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            leftMargin=24,
            rightMargin=24,
            topMargin=24,
            bottomMargin=24,
        )

        # Base stylesheet + custom paragraph styles
        styles = getSampleStyleSheet()
        if "SectionHeading" not in styles:
            styles.add(ParagraphStyle(
                name="SectionHeading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#2E4057"),
                spaceAfter=12,
            ))
        if "CustomBody" not in styles:
            styles.add(ParagraphStyle(
                name="CustomBody",
                parent=styles["BodyText"],
                fontSize=10,
                leading=12,
                spaceAfter=6,
            ))

        def styled_table(data, col_widths):
            """Helper to create a table with header styling, alternate rows, and padding."""
            tbl = Table(data, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(TableStyle([
                # Header row
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                # Body rows
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F4F4F4"), colors.white]),
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                # Grid & padding
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            return tbl

        elements = []

        # --- Farm Information ---
        elements.append(Paragraph("Farm Information", styles["Heading1"]))
        elements.append(Spacer(1, 12))
        farm_data = [
            ["Field", "Value"],
            ["Farm Name", farm.name],
            ["Size", f"{farm.size}"],
            ["Plant Type", farm.plant_type],
            ["Created At", farm.created_at.strftime("%Y-%m-%d %H:%M:%S")],
            ["User", farm.user.name],
        ]
        elements.append(styled_table(farm_data, col_widths=[120, 380]))
        elements.append(Spacer(1, 20))

        # --- Boundary Points ---
        elements.append(Paragraph("Boundary Points", styles["SectionHeading"]))
        elements.append(Spacer(1, 6))
        boundary_data = [["Latitude", "Longitude", "Description", "Timestamp"]]
        for bp in farm.boundary_points.all():
            boundary_data.append([
                f"{bp.latitude:.6f}",
                f"{bp.longitude:.6f}",
                bp.description or "—",
                bp.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        if len(boundary_data) > 1:
            elements.append(styled_table(boundary_data, col_widths=[100, 100, 240, 160]))
        else:
            elements.append(Paragraph("No boundary points found.", styles["CustomBody"]))
        elements.append(Spacer(1, 20))

        # --- Observation Points ---
        elements.append(Paragraph("Observation Points", styles["SectionHeading"]))
        elements.append(Spacer(1, 6))
        obs_data = [["Latitude", "Longitude", "Status", "Name", "Segment", "Confidence", "Target"]]
        for op in farm.observation_points.all():
            obs_data.append([
                f"{op.latitude:.6f}",
                f"{op.longitude:.6f}",
                op.observation_status,
                op.name or "—",
                str(op.segment),
                str(op.confidence_level or "—"),
                op.target_entity or "—",
            ])
        if len(obs_data) > 1:
            elements.append(styled_table(obs_data, col_widths=[80, 80, 80, 100, 60, 80, 100]))
        else:
            elements.append(Paragraph("No observation points found.", styles["CustomBody"]))
        elements.append(Spacer(1, 20))

        # --- Inspection Suggestions ---
        elements.append(Paragraph("Inspection Suggestions", styles["SectionHeading"]))
        elements.append(Spacer(1, 6))
        sug_data = [["Target", "Confidence", "Area Size", "Density", "Created At"]]
        for s in farm.inspection_suggestions.all():
            sug_data.append([
                s.target_entity,
                str(s.confidence_level),
                f"{s.area_size}",
                f"{s.density_of_plant}",
                s.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        if len(sug_data) > 1:
            elements.append(styled_table(sug_data, col_widths=[120, 100, 80, 100, 150]))
        else:
            elements.append(Paragraph("No inspection suggestions found.", styles["CustomBody"]))
        elements.append(Spacer(1, 20))

        # --- Inspection Observations ---
        elements.append(Paragraph("Inspection Observations", styles["SectionHeading"]))
        elements.append(Spacer(1, 6))
        insp_data = [["Date", "Confidence", "Status", "Target", "Severity"]]
        for o in farm.observations.all():
            insp_data.append([
                o.date.strftime("%Y-%m-%d %H:%M:%S"),
                str(o.confidence),
                o.status,
                o.target_entity or "—",
                o.severity or "—",
            ])
        if len(insp_data) > 1:
            elements.append(styled_table(insp_data, col_widths=[150, 80, 80, 120, 80]))
        else:
            elements.append(Paragraph("No inspection observations found.", styles["CustomBody"]))

        # Build PDF
        doc.build(elements)

        # Return as response
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type="application/pdf")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response["Content-Disposition"] = f'attachment; filename="farm_{farm.name}_{timestamp}.pdf"'
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
