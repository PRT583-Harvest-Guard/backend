from rest_framework import viewsets, mixins, status, serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from farm.serializers.admin_serializers import FarmAdminSerializer, BlockAdminSerializer
from farm.models import Farm, Block
from surveillance.models import Pest, SurveillancePlan, SamplingEvent, Observation
from surveillance.serializers.admin_serializers import SurveillancePlanAdminSerializer, SurveillanceCreatePlanAdminSerializer, SamplingEventAdminSerializer, PestAdminSerializer, SamplingEventUpdateAdminSerializer, ObservationAdminSerializer, SurveillancePlanUpdateAdminSerializer
from datetime import datetime

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
        elif self.action == 'update' or self.action == 'partial_update':
            return SurveillancePlanUpdateAdminSerializer
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


    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return SamplingEventUpdateAdminSerializer
        return SamplingEventAdminSerializer
    
    
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

        # Check for existing events
        existing_events = plan.events.all()
        existing_block_ids = set(event.blockDetails.id for event in existing_events)
        
        # Filter out blocks that already have events
        blocks_to_process = blocks.exclude(id__in=existing_block_ids)
        
        if not blocks_to_process.exists():
            return Response(
                SamplingEventAdminSerializer(existing_events, many=True).data,
                status=status.HTTP_200_OK
            )
        
        # Create sampling events for remaining blocks
        created_events = []
        for block in blocks_to_process:
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
        
        serializer.instance = created_events
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class ObservationViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Observation.objects.all()
    serializer_class = ObservationAdminSerializer


    def perform_create(self, serializer):
        event_id = self.request.parser_context['kwargs'].get('event_id')
        event = SamplingEvent.objects.get(id=event_id)
        if not event:
            return Response({"error": "Event with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        sample_size = event.sampleSize
        block_details = event.blockDetails
        for i in range(sample_size):
            observation = Observation(
                event=event,
                blockId=block_details.id,
                plantId="",
                detectionResult=False,
                severity=0,
                notes="",
            )
            observation.save()

        return Response({"Message": f"{sample_size} observation list is created for block id {block_details.id}"},
                        status=status.HTTP_201_CREATED)
