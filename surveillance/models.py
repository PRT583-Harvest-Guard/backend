from django.db import models
from farm.models import Farm, Block
import uuid


class Pest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    scientificName = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    controlMeasures = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SurveillancePlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='plans')
    pest = models.ForeignKey(Pest, on_delete=models.CASCADE, related_name='plans')
    blocks = models.ManyToManyField(Block, related_name='plans')
    designPrevalence = models.FloatField()
    detectionConfidence = models.FloatField()
    observerDetectionProb = models.FloatField()
    # sampleSize = models.IntegerField()
    scheduleStart = models.DateTimeField()
    scheduleFrequency = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="draft")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plan for {self.farm.name} - {self.pest.name}"


class SamplingEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(SurveillancePlan, on_delete=models.CASCADE, related_name='events')
    eventDate = models.DateTimeField()
    blockDetails = models.ForeignKey(Block, related_name='sampling_events', on_delete=models.CASCADE)
    recommendations = models.TextField()  # Stored as JSON string, consider using JSONField in PostgreSQL
    sampleSize = models.IntegerField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sampling on {self.eventDate.strftime('%Y-%m-%d')} for {self.plan}"


class Observation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(SamplingEvent, on_delete=models.CASCADE, related_name='observations')
    blockId = models.CharField(max_length=255)  # Consider making this a ForeignKey to Block
    plantId = models.CharField(max_length=255)
    detectionResult = models.BooleanField()
    severity = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Observation {self.id} for plant {self.plantId}"
