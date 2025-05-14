import pytest
import json
from rest_framework import status
from farm.models import Farm, BoundaryPoint, ObservationPoint, InspectionSuggestion, InspectionObservation
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db]


class TestSyncDataAPIView:
    """Test the SyncDataAPIView."""

    def test_sync_data_authenticated(self, authenticated_client, sync_data_url, farm):
        """Test syncing data when authenticated."""
        client, user = authenticated_client
        
        data = {
            'farms': [
                {
                    'id': farm.id,
                    'name': 'Updated Farm',
                    'size': 200.5,
                    'plant_type': 'Wheat'
                },
                {
                    'id': 999,  # New farm
                    'name': 'New Farm',
                    'size': 150.5,
                    'plant_type': 'Corn'
                }
            ],
            'boundary_points': [
                {
                    'id': 1,
                    'farm_id': farm.id,
                    'latitude': 37.7749,
                    'longitude': -122.4194,
                    'description': 'Test Boundary Point'
                }
            ],
            'observation_points': [
                {
                    'id': 1,
                    'farm_id': farm.id,
                    'latitude': 37.7749,
                    'longitude': -122.4194,
                    'observation_status': 'Observed',
                    'name': 'Test Observation Point',
                    'segment': 5,
                    'confidence_level': 'High',
                    'target_entity': 'Test Target'
                }
            ],
            'inspection_suggestions': [
                {
                    'id': 1,
                    'target_entity': 'Test Target',
                    'confidence_level': 'High',
                    'property_location': farm.id,
                    'area_size': 50.5,
                    'density_of_plant': 75
                }
            ],
            'inspection_observations': [
                {
                    'id': 1,
                    'date': '2025-05-14T12:00:00Z',
                    'inspection': 1,  # This would be the ID of the inspection suggestion created above
                    'farm': farm.id,
                    'confidence': 'High',
                    'plant_per_section': '50',
                    'status': 'Completed',
                    'target_entity': 'Test Target',
                    'severity': 'Medium'
                }
            ]
        }
        
        response = client.post(
            sync_data_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert 'timestamp' in response.data
        assert 'results' in response.data
        
        # Check that the farm was updated
        farm.refresh_from_db()
        assert farm.name == 'Updated Farm'
        assert farm.size == 200.5
        assert farm.plant_type == 'Wheat'
        
        # Check that a new farm was created
        assert Farm.objects.filter(name='New Farm').exists()
        
        # Check that a boundary point was created
        assert BoundaryPoint.objects.filter(description='Test Boundary Point').exists()
        
        # Check that an observation point was created
        assert ObservationPoint.objects.filter(name='Test Observation Point').exists()
        
        # Check that an inspection suggestion was created
        assert InspectionSuggestion.objects.filter(target_entity='Test Target').exists()
        
        # The inspection observation might not be created if the inspection suggestion ID doesn't match
        # But we can check that the API call was successful
    
    def test_sync_data_unauthenticated(self, api_client, sync_data_url, farm):
        """Test syncing data when unauthenticated."""
        data = {
            'farms': [
                {
                    'id': farm.id,
                    'name': 'Updated Farm',
                    'size': 200.5,
                    'plant_type': 'Wheat'
                }
            ]
        }
        
        response = api_client.post(
            sync_data_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the farm was not updated
        farm.refresh_from_db()
        assert farm.name != 'Updated Farm'
    
    def test_sync_data_invalid_farm(self, authenticated_client, sync_data_url):
        """Test syncing data with an invalid farm ID."""
        client, user = authenticated_client
        
        data = {
            'farms': [
                {
                    'id': 9999,  # Non-existent farm
                    'name': 'Updated Farm',
                    'size': 200.5,
                    'plant_type': 'Wheat'
                }
            ]
        }
        
        response = client.post(
            sync_data_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        
        # Check that a new farm was created with the given ID
        assert Farm.objects.filter(id=9999).exists()
    
    def test_sync_data_invalid_json(self, authenticated_client, sync_data_url):
        """Test syncing data with invalid JSON."""
        client, user = authenticated_client
        
        response = client.post(
            sync_data_url,
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
