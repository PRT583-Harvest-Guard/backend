from rest_framework import viewsets, mixins, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from farm.serializers.client_serializers import FarmClientSerializer, BlockClientSerializer
from farm.models import Farm, Block
from rest_framework.decorators import action





class ClientFarmViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):

    
    serializer_class = FarmClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def blocks(self, request, pk=None):
        farm = self.get_object()
        blocks = Block.objects.filter(farm=farm)
        serializer = BlockClientSerializer(blocks, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['post'])
    def add_block(self, request, pk=None):
        farm = self.get_object()
        serializer = BlockClientSerializer(data=request.data)
        if serializer.is_valid():
            block = serializer.save(farm=farm)
            return Response(BlockClientSerializer(block).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['put'])
    def update_block(self, request, pk=None):
        block = self.get_object()
        serializer = BlockClientSerializer(block, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['delete'])
    def delete_block(self, request, pk=None):
        block = self.get_object()
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



    