from django.db import models
import uuid


class Farm(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='farms', blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    location_point_1 = models.CharField(max_length=255)
    location_point_2 = models.CharField(max_length=255)
    location_point_3 = models.CharField(max_length=255)
    location_point_4 = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    size = models.FloatField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Block(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='blocks')
    name = models.CharField(max_length=255)
    area = models.FloatField(blank=True, null=True)
    location_point_1 = models.CharField(max_length=255)
    location_point_2 = models.CharField(max_length=255)
    location_point_3 = models.CharField(max_length=255)
    location_point_4 = models.CharField(max_length=255)
    totalTrees = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.farm.name})"