from rest_framework import viewsets, mixins, status, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from farm.serializers.admin_serializers import FarmAdminSerializer, BlockAdminSerializer
from farm.models import Farm, Block
from surveillance.models import Pest, SurveillancePlan, SamplingEvent, Observation
from rest_framework.decorators import action
from surveillance.serializers.admin_serializers import SurveillancePlanAdminSerializer, SurveillanceCreatePlanAdminSerializer, SamplingEventAdminSerializer, PestAdminSerializer
import json
from datetime import datetime, timedelta
import random
import math
from backend.utils import calculate_sample_size, generate_recommendations


class AdminFarmViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Farm.objects.all()
    serializer_class = FarmAdminSerializer


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




    # @action(detail=True, methods=['get'])
    # def blocks(self, request, pk=None):
    #     farm = self.get_object()
    #     blocks = farm.blocks.all()
    #     serializer = BlockAdminSerializer(blocks, many=True)
    #     return Response(serializer.data)


    # @action(detail=True, methods=['post'], serializer_class=BlockAdminSerializer)
    # def add_block(self, request, pk=None):
    #     farm = self.get_object()
    #     serializer = BlockAdminSerializer(data=request.data)
    #     if serializer.is_valid():
    #         block = serializer.save(farm=farm)
    #         return Response(BlockAdminSerializer(block).data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # @action(detail=True, methods=['put', 'patch'], url_path='blocks/(?P<block_id>[^/.]+)', serializer_class=BlockAdminSerializer, name='update_block')
    # def update_block(self, request, pk=None, block_id=None):
    #     try:
    #         farm = self.get_object()
    #         block = Block.objects.get(id=block_id, farm=farm)
    #         serializer = BlockAdminSerializer(block, data=request.data, partial=request.method == 'PATCH')
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Block.DoesNotExist:
    #         return Response({"detail": f"Block with id {block_id} not found."}, status=status.HTTP_404_NOT_FOUND)

    # @action(detail=True, methods=['delete'], url_path='blocks/(?P<block_id>[^/.]+)', name='delete_block')
    # def delete_block(self, request, pk=None, block_id=None):
    #     try:
    #         farm = self.get_object()
    #         block = Block.objects.get(id=block_id, farm=farm)
    #         block.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     except Block.DoesNotExist:
    #         return Response({"detail": f"Block with id {block_id} not found."}, status=status.HTTP_404_NOT_FOUND)


    # @action(detail=True, methods=['post'])
    # def add_surveillance_plan(self, request, pk=None):
    #     farm = self.get_object()
    #     serializer = SurveillancePlanAdminSerializer(data=request.data)
    #     if serializer.is_valid():
    #         plan = serializer.save(farm=farm)
    #         return Response(SurveillancePlanAdminSerializer(plan).data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # @action(detail=True, methods=['get'])
    # def surveillance_plans(self, request, pk=None):
    #     farm = self.get_object()
    #     plans = SurveillancePlan.objects.filter(farm=farm)
    #     serializer = SurveillancePlanAdminSerializer(plans, many=True)
    #     return Response(serializer.data)

    # @action(detail=True, methods=['put'])
    # def update_surveillance_plan(self, request, pk=None):
    #     plan = self.get_object()
    #     serializer = SurveillancePlanAdminSerializer(plan, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # @action(detail=True, methods=['delete'])
    # def delete_surveillance_plan(self, request, pk=None):
    #     plan = self.get_object()
    #     plan.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)



    # @action(detail=True, methods=['get'], url_path='surveillance_plans/(?P<plan_id>[^/.]+)/sampling_events')
    # def sampling_events(self, request, pk=None):
    #     plans = SurveillancePlan.objects.filter(farm=self.get_object(), id=request.parser_context['kwargs']['plan_id'])
    #     events = SamplingEvent.objects.filter(plan__in=plans)
    #     serializer = SurveillancePlanAdminSerializer(events, many=True)
    #     return Response(serializer.data)


    
    # @action(detail=True, methods=['post'], url_path='surveillance_plans/(?P<plan_id>[^/.]+)/sampling_events', serializer_class=SamplingEventAdminSerializer)
    # def add_sampling_event(self, request, pk=None):
    #     plan = self.get_object()
    #     serializer = SurveillancePlanAdminSerializer(data=request.data)
    #     if serializer.is_valid():
    #         event = serializer.save(plan=plan)
    #         return Response(SurveillancePlanAdminSerializer(event).data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    # @action(detail=True, methods=['get'], url_path='surveillance_plans/(?P<plan_id>[^/.]+)/sampling_events/(?P<event_id>[^/.]+)')
    # def sampling_event(self, request, pk=None):
    #     events = SamplingEvent.objects.filter(id=request.parser_context['kwargs']['event_id'])
    #     serializer = SurveillancePlanAdminSerializer(events, many=True)
    #     return Response(serializer.data)


    # @action(detail=True, methods=['get'], url_path='surveillance_plans/(?P<plan_id>[^/.]+)/sampling_events/(?P<event_id>[^/.]+)/observations')
    # def observations(self, request, pk=None):
    #     events = SamplingEvent.objects.filter(id=request.parser_context['kwargs']['event_id'])
    #     observations = Observation.objects.filter(event__in=events)
    #     serializer = SurveillancePlanAdminSerializer(observations, many=True)
    #     return Response(serializer.data)







class PestViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Pest.objects.all()
    serializer_class = PestAdminSerializer





class BlockViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Block.objects.all()
    serializer_class = BlockAdminSerializer


    def perform_create(self, serializer, *args, **kwargs):
        farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
        if farm:
            try:
                serializer.save(farm=farm, *args, **kwargs)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Farm.DoesNotExist:
                raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})
        else:
            raise serializers.ValidationError({"farm": "Farm ID is required."})



    def perform_update(self, serializer, *args, **kwargs):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            block = Block.objects.get(id=self.request.parser_context['kwargs']['pk'], farm=farm)
            if block:
                serializer = BlockAdminSerializer(block, data=self.request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
            else:
                raise serializers.ValidationError({"block": "Block with this ID does not exist."})
        except Farm.DoesNotExist:
            raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})

    def retrieve(self, request, *args, **kwargs):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            block = Block.objects.get(id=self.request.parser_context['kwargs']['pk'], farm=farm)
            if block:
                serializer = BlockAdminSerializer(block)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                raise serializers.ValidationError({"block": "Block with this ID does not exist."})
        except Farm.DoesNotExist:
            raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})


    def list(self, request, *args, **kwargs):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            blocks = farm.blocks.all()
            serializer = BlockAdminSerializer(blocks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Farm.DoesNotExist:
            raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})        

    def perform_destroy(self, instance):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            block = Block.objects.get(id=self.request.parser_context['kwargs']['pk'], farm=farm)
            if block:
                block.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise serializers.ValidationError({"block": "Block with this ID does not exist."})
        except Farm.DoesNotExist:
            raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})



class SurveillancePlanViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = SurveillancePlan.objects.all()


    def get_serializer_class(self):
        if self.action == 'create':
            return SurveillanceCreatePlanAdminSerializer
        return SurveillancePlanAdminSerializer

    def perform_create(self, serializer):
        farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
        if farm:
            try:
                serializer.save(farm=farm, blocks=farm.blocks.all())
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Farm.DoesNotExist:
                raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})
        else:
            raise serializers.ValidationError({"farm": "Farm ID is required."})


    def retrieve(self, request, *args, **kwargs):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            plan = SurveillancePlan.objects.get(id=self.request.parser_context['kwargs']['pk'], farm=farm)
            if plan:
                serializer = SurveillancePlanAdminSerializer(plan)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                raise serializers.ValidationError({"plan": "Plan with this ID does not exist."})
        except Farm.DoesNotExist:
            raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})


    def perform_update(self, serializer):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            plan = SurveillancePlan.objects.get(id=self.request.parser_context['kwargs']['pk'], farm=farm)
            serializer = SurveillanceCreatePlanAdminSerializer(plan, data=self.request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise serializers.ValidationError({"farm": "{e}"})


    def perform_destroy(self, instance):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            plan = SurveillancePlan.objects.get(id=self.request.parser_context['kwargs']['pk'], farm=farm)
            if plan:
                plan.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise serializers.ValidationError({"plan": "Plan with this ID does not exist."})
        except Farm.DoesNotExist:
            raise serializers.ValidationError({"farm": "Farm with this ID does not exist."})


    def perform_partial_update(self, serializer):
        try:
            farm = Farm.objects.get(id=self.request.parser_context['kwargs']['farm_id'])
            plan = SurveillancePlan.objects.get(id=self.request.parser_context['kwargs']['pk'], farm=farm)
            serializer = SurveillanceCreatePlanAdminSerializer(plan, data=self.request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise serializers.ValidationError({"farm": "{e}"})




class SamplingEventViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = SamplingEvent.objects.all()
    serializer_class = SamplingEventAdminSerializer


    def perform_create(self, serializer):
        plan_id = self.request.parser_context['kwargs'].get('plan_id')
        plan = SurveillancePlan.objects.get(id=plan_id)
        
        if not plan:
            raise serializers.ValidationError({"plan": "Plan with this ID does not exist."})
        
        # Get all blocks associated with this plan
        blocks = plan.blocks.all()
        
        if not blocks.exists():
            raise serializers.ValidationError({"blocks": "No blocks associated with this plan."})
        
        # Get the event date from the request data or use current date
        event_date = self.request.data.get('eventDate')
        if not event_date:
            event_date = datetime.now()
        else:
            try:
                event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            except ValueError:
                event_date = datetime.now()
        
        # Create sampling events for each block
        if len(plan.events) == len(blocks):
            return Response({"detail": "Sampling events already created for all blocks."}, status=status.HTTP_200_OK)
            
        if len(plan.events) > len(blocks):
            plan_blocks = set([block.blockDetails.id for block in plan.events])
            blocks = blocks.exclude(id__in=plan_blocks)
        created_events = []
        for block in blocks:
            # Calculate sample size for this block
            sample_size = calculate_sample_size(block, plan)
            
            # Generate recommendations
            recommendations = generate_recommendations(block, sample_size)
            
            # Create the sampling event
            event_data = {
                'plan': plan,
                'eventDate': event_date,
                'blockDetails': block,
                'recommendations': recommendations,
                'sampleSize': sample_size
            }
            
            event = SamplingEvent.objects.create(**event_data)
            created_events.append(event)
        
        # Return the first created event (or you could return all of them)
        serializer.instance = created_events[0]
        return Response(serializer.data, status=status.HTTP_201_CREATED)
