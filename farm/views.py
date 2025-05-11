# api/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Farm, BoundaryPoint, ObservationPoint, InspectionSuggestion, InspectionObservation
from farm.serializers import (
    FarmSerializer, BoundaryPointSerializer, ObservationPointSerializer,
    InspectionSuggestionSerializer, InspectionObservationSerializer, ObservationPointBulkSyncSerializer,
    InspectionSuggestionBulkSyncSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction



@extend_schema(
    parameters=[
        OpenApiParameter("id", int, OpenApiParameter.PATH)
    ]
)
class FarmViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FarmSerializer

    def get_queryset(self):
        return Farm.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=False, methods=['post'])
    @transaction.atomic
    def sync(self, request):
        """
        Sync farms from the mobile app.

        This endpoint handles bulk creation, update, and deletion of farms.
        It expects a list of farms with mobile_id to identify them.
        """
        serializer = FarmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        farms_data = serializer.validated_data['farms']

        # Track results
        created_count = 0
        updated_count = 0
        failed_count = 0
        results = []

        for farm_data in farms_data:
            try:
                # Extract mobile_id
                mobile_id = farm_data.get('id')

                # Check if farm exists
                farm = Farm.objects.filter(mobile_id=mobile_id).first()

                if farm:
                    # Update existing farm
                    for key, value in farm_data.items():
                        setattr(farm, key, value)

                    farm.last_synced = timezone.now()
                    farm.sync_status = 'synced'
                    farm.save()

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': farm.id,
                        'status': 'updated'
                    })
                    updated_count += 1
                else:
                    # Create new farm
                    new_farm_data = {k: v for k, v in farm_data.items() if k != 'id'}
                    new_farm_data['mobile_id'] = mobile_id
                    new_farm_data['user'] = request.user

                    farm = Farm.objects.create(**new_farm_data)

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': farm.id,
                        'status': 'created'
                    })
                    created_count += 1

            except Exception as e:
                results.append({
                    'mobile_id': farm_data.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })
                failed_count += 1

        return Response({
            'status': 'success',
            'created': created_count,
            'updated': updated_count,
            'failed': failed_count,
            'results': results
        })


@extend_schema(
    parameters=[
        OpenApiParameter("id", int, OpenApiParameter.PATH)
    ]
)
class BoundaryPointViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BoundaryPointSerializer

    def get_queryset(self):
        return BoundaryPoint.objects.filter(farm__user=self.request.user)

    def sync(self, request):
        """
        Sync boundary points from the mobile app.

        This endpoint handles bulk creation, update, and deletion of boundary points.
        It expects a list of boundary points with mobile_id to identify them.
        """
        serializer = BoundaryPointSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        boundary_points_data = serializer.validated_data['boundary_points']

        # Track results
        created_count = 0
        updated_count = 0
        failed_count = 0
        results = []

        for point_data in boundary_points_data:
            try:
                # Extract mobile_id and farm_id
                mobile_id = point_data.get('id')
                farm_id = point_data.get('farm_id')

                # Verify farm belongs to user
                farm = Farm.objects.filter(id=farm_id, user=request.user).first()
                if not farm:
                    results.append({
                        'mobile_id': mobile_id,
                        'status': 'failed',
                        'message': f'Farm with ID {farm_id} not found or does not belong to user'
                    })
                    failed_count += 1
                    continue

                # Check if boundary point exists
                point = BoundaryPoint.objects.filter(mobile_id=mobile_id).first()

                if point:
                    # Update existing point
                    for key, value in point_data.items():
                        if key not in ['id', 'mobile_id']:
                            setattr(point, key, value)

                    point.last_synced = timezone.now()
                    point.sync_status = 'synced'
                    point.save()

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': point.id,
                        'status': 'updated'
                    })
                    updated_count += 1
                else:
                    # Create new point
                    new_point_data = {k: v for k, v in point_data.items() if k not in ['id', 'farm_id']}
                    new_point_data['farm'] = farm
                    new_point_data['mobile_id'] = mobile_id

                    point = BoundaryPoint.objects.create(**new_point_data)

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': point.id,
                        'status': 'created'
                    })
                    created_count += 1

            except Exception as e:
                results.append({
                    'mobile_id': point_data.get('id'),
                    'status': 'failed',
                    'message': str(e)})


@extend_schema(
    parameters=[
        OpenApiParameter("id", int, OpenApiParameter.PATH)
    ]
)
class ObservationPointViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ObservationPoint model.
    """
    serializer_class = ObservationPointSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return observation points for the authenticated user.
        """
        return ObservationPoint.objects.filter(farm__user=self.request.user)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def sync(self, request):
        """
        Sync observation points from the mobile app.

        This endpoint handles bulk creation, update, and deletion of observation points.
        It expects a list of observation points with mobile_id to identify them.
        """
        serializer = ObservationPointBulkSyncSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        observation_points_data = serializer.validated_data['observation_points']

        # Track results
        created_count = 0
        updated_count = 0
        failed_count = 0
        results = []

        for point_data in observation_points_data:
            try:
                # Extract mobile_id and farm_id
                mobile_id = point_data.get('id')
                farm_id = point_data.get('farm_id')

                # Verify farm belongs to user
                farm = Farm.objects.filter(id=farm_id, user=request.user).first()
                if not farm:
                    results.append({
                        'mobile_id': mobile_id,
                        'status': 'failed',
                        'message': f'Farm with ID {farm_id} not found or does not belong to user'
                    })
                    failed_count += 1
                    continue

                # Check if observation point exists
                point = ObservationPoint.objects.filter(mobile_id=mobile_id).first()

                if point:
                    # Update existing point
                    for key, value in point_data.items():
                        if key not in ['id', 'mobile_id']:
                            if key == 'farm_id':
                                # Handle foreign key
                                point.farm = farm
                            elif key == 'inspection_suggestion_id':
                                # Handle foreign key
                                suggestion = InspectionSuggestion.objects.filter(
                                    id=value,
                                    property_location__user=request.user
                                ).first()
                                point.inspection_suggestion = suggestion
                            else:
                                setattr(point, key, value)

                    point.last_synced = timezone.now()
                    point.sync_status = 'synced'
                    point.save()

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': point.id,
                        'status': 'updated'
                    })
                    updated_count += 1
                else:
                    # Create new point
                    new_point_data = {k: v for k, v in point_data.items() if
                                      k not in ['id', 'farm_id', 'inspection_suggestion_id']}
                    new_point_data['farm'] = farm
                    new_point_data['mobile_id'] = mobile_id

                    # Handle inspection suggestion if present
                    if 'inspection_suggestion_id' in point_data:
                        suggestion = InspectionSuggestion.objects.filter(
                            id=point_data['inspection_suggestion_id'],
                            property_location__user=request.user
                        ).first()
                        if suggestion:
                            new_point_data['inspection_suggestion'] = suggestion

                    new_point_data['last_synced'] = timezone.now()
                    new_point_data['sync_status'] = 'synced'

                    point = ObservationPoint.objects.create(**new_point_data)

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': point.id,
                        'status': 'created'
                    })
                    created_count += 1

            except Exception as e:
                results.append({
                    'mobile_id': point_data.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })
                failed_count += 1

        return Response({
            'status': 'success',
            'created': created_count,
            'updated': updated_count,
            'failed': failed_count,
            'results': results
        })

    @action(detail=False, methods=['get'])
    def pending_sync(self, request):
        """
        Get observation points that need to be synced to the mobile app.

        This endpoint returns observation points that have been updated on the server
        since the last sync.
        """
        last_sync = request.query_params.get('last_sync')

        if last_sync:
            try:
                last_sync_time = timezone.datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                queryset = self.get_queryset().filter(updated_at__gt=last_sync_time)
            except ValueError:
                return Response(
                    {'error': 'Invalid last_sync format. Use ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # If no last_sync provided, return all observation points
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter("id", int, OpenApiParameter.PATH)
    ]
)
class InspectionSuggestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InspectionSuggestion model.
    """
    serializer_class = InspectionSuggestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return inspection suggestions for the authenticated user.
        """
        return InspectionSuggestion.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the user when creating a new inspection suggestion.
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def sync(self, request):
        """
        Sync inspection suggestions from the mobile app.

        This endpoint handles bulk creation, update, and deletion of inspection suggestions.
        It expects a list of inspection suggestions with mobile_id to identify them.
        """
        serializer = InspectionSuggestionBulkSyncSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        suggestions_data = serializer.validated_data['inspection_suggestions']

        # Track results
        created_count = 0
        updated_count = 0
        failed_count = 0
        results = []

        for suggestion_data in suggestions_data:
            try:
                # Extract mobile_id and farm_id
                mobile_id = suggestion_data.get('id')
                farm_id = suggestion_data.get('property_location')

                # Verify farm belongs to user
                farm = Farm.objects.filter(id=farm_id, user=request.user).first()
                if not farm:
                    results.append({
                        'mobile_id': mobile_id,
                        'status': 'failed',
                        'message': f'Farm with ID {farm_id} not found or does not belong to user'
                    })
                    failed_count += 1
                    continue

                # Check if suggestion exists
                suggestion = InspectionSuggestion.objects.filter(mobile_id=mobile_id).first()

                if suggestion:
                    # Update existing suggestion
                    for key, value in suggestion_data.items():
                        if key not in ['id', 'mobile_id', 'user']:
                            if key == 'property_location':
                                # Handle foreign key
                                suggestion.property_location = farm
                            else:
                                setattr(suggestion, key, value)

                    suggestion.last_synced = timezone.now()
                    suggestion.sync_status = 'synced'
                    suggestion.save()

                    # Update related observation points
                    self._update_observation_points(suggestion)

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': suggestion.id,
                        'status': 'updated'
                    })
                    updated_count += 1
                else:
                    # Create new suggestion
                    new_suggestion_data = {k: v for k, v in suggestion_data.items() if
                                           k not in ['id', 'property_location', 'user']}
                    new_suggestion_data['property_location'] = farm
                    new_suggestion_data['user'] = request.user
                    new_suggestion_data['mobile_id'] = mobile_id
                    new_suggestion_data['last_synced'] = timezone.now()
                    new_suggestion_data['sync_status'] = 'synced'

                    suggestion = InspectionSuggestion.objects.create(**new_suggestion_data)

                    # Update related observation points
                    self._update_observation_points(suggestion)

                    results.append({
                        'mobile_id': mobile_id,
                        'server_id': suggestion.id,
                        'status': 'created'
                    })
                    created_count += 1

            except Exception as e:
                results.append({
                    'mobile_id': suggestion_data.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })
                failed_count += 1

        return Response({
            'status': 'success',
            'created': created_count,
            'updated': updated_count,
            'failed': failed_count,
            'results': results
        })

    def _update_observation_points(self, suggestion):
        """
        Update observation points related to this suggestion.

        When a suggestion is created or updated, we need to update the related
        observation points with the suggestion's target_entity and confidence_level.
        """
        from farm.models import ObservationPoint

        # Get all observation points for this farm
        observation_points = ObservationPoint.objects.filter(
            farm=suggestion.property_location
        )

        # Update them with the suggestion's data
        observation_points.update(
            inspection_suggestion=suggestion,
            target_entity=suggestion.target_entity,
            confidence_level=suggestion.confidence_level,
            last_synced=timezone.now(),
            sync_status='synced'
        )

    @action(detail=False, methods=['get'])
    def pending_sync(self, request):
        """
        Get inspection suggestions that need to be synced to the mobile app.

        This endpoint returns inspection suggestions that have been updated on the server
        since the last sync.
        """
        last_sync = request.query_params.get('last_sync')

        if last_sync:
            try:
                last_sync_time = timezone.datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                queryset = self.get_queryset().filter(updated_at__gt=last_sync_time)
            except ValueError:
                return Response(
                    {'error': 'Invalid last_sync format. Use ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # If no last_sync provided, return all inspection suggestions
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter("id", int, OpenApiParameter.PATH)
    ]
)
class InspectionObservationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InspectionObservationSerializer

    def get_queryset(self):
        return InspectionObservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SyncDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        data = request.data
        results = {
            'farms': [],
            'boundary_points': [],
            'observation_points': [],
            'inspection_suggestions': [],
            'inspection_observations': []
        }

        # 1) Farms
        for farm in data.get('farms', []):
            try:
                obj, created = Farm.objects.update_or_create(
                    id=farm['id'],
                    defaults={
                        'name': farm['name'],
                        'size': farm['size'],
                        'plant_type': farm['plant_type'],
                        'user': request.user,
                    }
                )
                results['farms'].append({
                    'mobile_id': farm['id'],
                    'server_id': obj.id,
                    'status': 'created' if created else 'updated'
                })
            except Exception as e:
                results['farms'].append({
                    'mobile_id': farm.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })

        # 2) Boundary Points
        for bp in data.get('boundary_points', []):
            try:
                farm_obj = Farm.objects.get(id=bp['farm_id'], user=request.user)
            except Farm.DoesNotExist:
                results['boundary_points'].append({
                    'mobile_id': bp.get('id'),
                    'status': 'failed',
                    'message': f"Farm {bp.get('farm_id')} not found"
                })
                continue

            try:
                obj, created = BoundaryPoint.objects.update_or_create(
                    id=bp['id'],
                    defaults={
                        'farm': farm_obj,
                        'latitude': bp['latitude'],
                        'longitude': bp['longitude'],
                        'description': bp.get('description', ''),
                    }
                )
                results['boundary_points'].append({
                    'mobile_id': bp['id'],
                    'server_id': obj.id,
                    'status': 'created' if created else 'updated'
                })
            except Exception as e:
                results['boundary_points'].append({
                    'mobile_id': bp.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })

        # 3) Observation Points
        for op in data.get('observation_points', []):
            try:
                farm_obj = Farm.objects.get(id=op['farm_id'], user=request.user)
            except Farm.DoesNotExist:
                results['observation_points'].append({
                    'mobile_id': op.get('id'),
                    'status': 'failed',
                    'message': f"Farm {op.get('farm_id')} not found"
                })
                continue

            # optional FK
            insp = None
            if op.get('inspection_suggestion_id') is not None:
                insp = InspectionSuggestion.objects.filter(
                    id=op['inspection_suggestion_id'],
                    user=request.user
                ).first()

            try:
                obj, created = ObservationPoint.objects.update_or_create(
                    id=op['id'],
                    defaults={
                        'farm': farm_obj,
                        'latitude': op['latitude'],
                        'longitude': op['longitude'],
                        'observation_status': op.get('observation_status', 'Nil'),
                        'name': op.get('name', ''),
                        'segment': op.get('segment', 0),
                        'inspection_suggestion': insp,
                        'confidence_level': op.get('confidence_level'),
                        'target_entity': op.get('target_entity'),
                    }
                )
                results['observation_points'].append({
                    'mobile_id': op['id'],
                    'server_id': obj.id,
                    'status': 'created' if created else 'updated'
                })
            except Exception as e:
                results['observation_points'].append({
                    'mobile_id': op.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })

        # 4) Inspection Suggestions
        for sug in data.get('inspection_suggestions', []):
            try:
                farm_obj = Farm.objects.get(id=sug['property_location'], user=request.user)
            except Farm.DoesNotExist:
                results['inspection_suggestions'].append({
                    'mobile_id': sug.get('id'),
                    'status': 'failed',
                    'message': f"Farm {sug.get('property_location')} not found"
                })
                continue

            try:
                obj, created = InspectionSuggestion.objects.update_or_create(
                    id=sug['id'], property_location=farm_obj,
                    defaults={
                        'target_entity': sug['target_entity'],
                        'confidence_level': sug['confidence_level'],

                        'area_size': sug.get('area_size', 0),
                        'density_of_plant': sug.get('density_of_plant', 0),
                        'user': request.user,
                    }
                )
                results['inspection_suggestions'].append({
                    'mobile_id': sug['id'],
                    'server_id': obj.id,
                    'status': 'created' if created else 'updated'
                })
            except Exception as e:
                results['inspection_suggestions'].append({
                    'mobile_id': sug.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })

        # 5) Inspection Observations (if you have that array)
        for obs in data.get('inspection_observations', []):
            try:
                farm_obj = Farm.objects.get(id=obs['farm'], user=request.user)
                insp_obj = InspectionSuggestion.objects.get(
                    id=obs['inspection'], user=request.user
                )
            except (Farm.DoesNotExist, InspectionSuggestion.DoesNotExist) as e:
                results['inspection_observations'].append({
                    'mobile_id': obs.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })
                continue

            try:
                obj, created = InspectionObservation.objects.update_or_create(
                    id=obs['id'],
                    defaults={
                        'date': obs['date'],
                        'inspection': insp_obj,
                        'farm': farm_obj,
                        'confidence': obs.get('confidence', ''),
                        'plant_per_section': obs.get('plant_per_section', ''),
                        'status': obs.get('status', ''),
                        'target_entity': obs.get('target_entity'),
                        'severity': obs.get('severity'),
                        # if you have an ImageField you can skip or handle separately
                    }
                )
                results['inspection_observations'].append({
                    'mobile_id': obs['id'],
                    'server_id': obj.id,
                    'status': 'created' if created else 'updated'
                })
            except Exception as e:
                results['inspection_observations'].append({
                    'mobile_id': obs.get('id'),
                    'status': 'failed',
                    'message': str(e)
                })

        # all done
        return Response({
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'results': results
        }, status=status.HTTP_200_OK)
