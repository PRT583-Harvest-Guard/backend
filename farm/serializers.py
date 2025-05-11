# farmserializers.py
from rest_framework import serializers
from .models import Farm, BoundaryPoint, ObservationPoint, InspectionSuggestion, InspectionObservation

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'

class BoundaryPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoundaryPoint
        fields = '__all__'

class ObservationPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationPoint
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_synced', 'sync_status')

class ObservationPointBulkSyncSerializer(serializers.Serializer):
    """
    Serializer for bulk syncing observation points.
    """
    observation_points = serializers.ListField(
        child=serializers.JSONField(),
        required=True
    )

    read_only_fields = ('id', 'created_at', 'updated_at', 'last_synced', 'sync_status', 'user')


class InspectionSuggestionBulkSyncSerializer(serializers.Serializer):
    """
    Serializer for bulk syncing inspection suggestions.
    """
    inspection_suggestions = serializers.ListField(
        child=serializers.JSONField(),
        required=True
    )


class InspectionSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionSuggestion
        fields = '__all__'

class InspectionObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionObservation
        fields = '__all__'
