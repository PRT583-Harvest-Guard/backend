from rest_framework import serializers
from surveillance.models import Pest, SurveillancePlan, SamplingEvent, Observation, Block
from farm.serializers.admin_serializers import FarmAdminSerializer, BlockAdminSerializer


class PestAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pest
        fields = [
            'id', 'name', 'scientificName', 'type', 'description',
            'symptoms', 'controlMeasures', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class ObservationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = [
            'id', 'event', 'blockId', 'plantId', 'detectionResult',
            'severity', 'notes', 'createdAt'
        ]
        read_only_fields = ['id', 'createdAt']


class SamplingEventAdminSerializer(serializers.ModelSerializer):
    observations = ObservationAdminSerializer(many=True, read_only=True)
    blockDetails = BlockAdminSerializer(read_only=True)
    sampleSize = serializers.IntegerField(read_only=True)

    class Meta:
        model = SamplingEvent
        fields = [
            'id', 'plan', 'eventDate', 'blockDetails','sampleSize',
            'recommendations', 'createdAt', 'observations'
        ]
        read_only_fields = ['id', 'createdAt']


class SurveillancePlanAdminSerializer(serializers.ModelSerializer):
    farm = FarmAdminSerializer(read_only=True)
    blocks = BlockAdminSerializer(many=True, read_only=True)
    events = SamplingEventAdminSerializer(many=True, read_only=True)

    class Meta:
        model = SurveillancePlan
        fields = [
            'id', 'farm', 'pest', 'blocks', 'designPrevalence',
            'detectionConfidence', 'observerDetectionProb',
            'scheduleStart', 'scheduleFrequency', 'status',
            'createdAt', 'updatedAt', 'events'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class SurveillanceCreatePlanAdminSerializer(serializers.ModelSerializer):
    farm = FarmAdminSerializer(read_only=True)
    blocks = BlockAdminSerializer(many=True, read_only=True)
    events = SamplingEventAdminSerializer(many=True, read_only=True)

    class Meta:
        model = SurveillancePlan
        fields = [
            'id', 'farm', 'pest', 'blocks', 'designPrevalence',
            'detectionConfidence', 'observerDetectionProb',
            'scheduleStart', 'scheduleFrequency', 'status',
            'createdAt', 'updatedAt', 'events'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class SamplingEventUpdateAdminSerializer(serializers.ModelSerializer):
    eventDate = serializers.DateTimeField(required=False)
    sampleSize = serializers.IntegerField(required=False)
    recommendations = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = SamplingEvent
        fields = ['eventDate', 'sampleSize', 'recommendations', 'status', 'notes']
        read_only_fields = ['plan']

    def validate(self, data):
        # Ensure at least one field is being updated
        if len(data) <= 1:  # Only ID is provided
            raise serializers.ValidationError("At least one field must be updated besides the ID")
        return data 