from rest_framework import serializers
from surveillance.models import Pest, SurveillancePlan, SamplingEvent, Observation
from farm.serializers.client_serializers import FarmClientSerializer, BlockClientSerializer


class PestClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pest
        fields = [
            'id', 'name', 'type', 'description', 'symptoms', 'controlMeasures'
        ]
        read_only_fields = ['id']


class ObservationClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = [
            'id', 'plantId', 'detectionResult', 'severity', 'notes'
        ]
        read_only_fields = ['id']


class SamplingEventClientSerializer(serializers.ModelSerializer):
    observations = ObservationClientSerializer(many=True, read_only=True)
    blockDetails = BlockClientSerializer(read_only=True)

    class Meta:
        model = SamplingEvent
        fields = [
            'id', 'eventDate', 'blockDetails', 'recommendations', 'observations'
        ]
        read_only_fields = ['id']


class SurveillancePlanClientSerializer(serializers.ModelSerializer):
    farm = FarmClientSerializer(read_only=True)
    pest = PestClientSerializer(read_only=True)
    blocks = BlockClientSerializer(many=True, read_only=True)
    events = SamplingEventClientSerializer(many=True, read_only=True)

    class Meta:
        model = SurveillancePlan
        fields = [
            'id', 'farm', 'pest', 'blocks', 'sampleSize',
            'scheduleStart', 'scheduleFrequency', 'status', 'events'
        ]
        read_only_fields = ['id'] 