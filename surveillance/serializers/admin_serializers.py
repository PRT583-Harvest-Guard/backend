from rest_framework import serializers
from surveillance.models import Pest, SurveillancePlan, SamplingEvent, Observation
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