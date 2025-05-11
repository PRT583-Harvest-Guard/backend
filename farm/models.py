from django.db import models

# Create your models here.
# api/models.py
from django.db import models
from django.conf import settings

class Farm(models.Model):
    name = models.CharField(max_length=255)
    size = models.FloatField()
    plant_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')

class BoundaryPoint(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='boundary_points')
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ObservationPoint(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='observation_points')
    latitude = models.FloatField()
    longitude = models.FloatField()
    observation_status = models.CharField(max_length=50, default='Nil')
    name = models.CharField(max_length=255, blank=True, null=True)
    segment = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    inspection_suggestion = models.ForeignKey('InspectionSuggestion', on_delete=models.SET_NULL,
                                             related_name='observation_points', null=True, blank=True)
    confidence_level = models.CharField(max_length=50, blank=True, null=True)
    target_entity = models.CharField(max_length=255, blank=True, null=True)

    # Sync-related fields
    mobile_id = models.IntegerField(unique=True, null=True, blank=True)
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

    class Meta:
        indexes = [
            models.Index(fields=['farm']),
            models.Index(fields=['mobile_id']),
            models.Index(fields=['sync_status']),
        ]

    def __str__(self):
        return f"Observation Point {self.id} - Farm {self.farm_id} - Segment {self.segment}"


class InspectionSuggestion(models.Model):
    target_entity = models.CharField(max_length=255)
    confidence_level = models.CharField(max_length=50)
    property_location = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='inspection_suggestions')
    area_size = models.FloatField()
    density_of_plant = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inspection_suggestions')

    # Sync-related fields
    mobile_id = models.IntegerField(unique=True, null=True, blank=True)
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

    class Meta:
        indexes = [
            models.Index(fields=['property_location']),
            models.Index(fields=['user']),
            models.Index(fields=['mobile_id']),
            models.Index(fields=['sync_status']),
        ]

    def __str__(self):
        return f"Inspection Suggestion {self.id} - {self.target_entity} - Farm {self.property_location_id}"

class InspectionObservation(models.Model):
    date = models.DateTimeField()
    inspection = models.ForeignKey(InspectionSuggestion, on_delete=models.CASCADE, related_name='observations')
    confidence = models.CharField(max_length=50)
    section = models.ForeignKey(BoundaryPoint, on_delete=models.CASCADE, related_name='observations', null=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='observations')
    plant_per_section = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    target_entity = models.CharField(max_length=255, blank=True, null=True)
    severity = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='inspection_images/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='observations')
