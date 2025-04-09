from rest_framework import serializers
from farm.models import Farm, Block


class BlockClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = [
            'id', 'name', 'area', 'totalTrees', 'description'
        ]
        read_only_fields = ['id']


class FarmClientSerializer(serializers.ModelSerializer):
    blocks = BlockClientSerializer(many=True, read_only=True)

    class Meta:
        model = Farm
        fields = [
            'id', 'name', 'description', 'size', 'blocks'
        ]
        read_only_fields = ['id'] 