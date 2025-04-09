from rest_framework import serializers
from farm.models import Farm, Block


class BlockAdminSerializer(serializers.ModelSerializer):
    farm = serializers.ReadOnlyField(source='farm.id')
    class Meta:
        model = Block
        fields = [
            'id', 'farm', 'name', 'area', 'location_point_1', 'location_point_2',
            'location_point_3', 'location_point_4', 'totalTrees', 'description',
            'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class FarmAdminSerializer(serializers.ModelSerializer):
    blocks = BlockAdminSerializer(many=True, read_only=True)

    class Meta:
        model = Farm
        fields = [
            'id', 'name', 'location_point_1', 'location_point_2',
            'location_point_3', 'location_point_4', 'description',
            'size', 'createdAt', 'updatedAt', 'blocks'
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt'] 
