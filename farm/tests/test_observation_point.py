import pytest
import json
from rest_framework import status
from farm.models import ObservationPoint
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db]


class TestObservationPointModel:
    """Test the ObservationPoint model."""

    def test_observation_point_creation(self, observation_point):
        """Test creating an observation point."""
        assert observation_point.id is not None
        assert observation_point.farm is not None
        assert observation_point.latitude is not None
        assert observation_point.longitude is not None
        assert observation_point.observation_status is not None
        assert observation_point.segment is not None
        assert observation_point.created_at is not None
        assert observation_point.inspection_suggestion is not None
        assert observation_point.confidence_level is not None
        assert observation_point.target_entity is not None

    def test_observation_point_string_representation(self, observation_point):
        """Test the string representation of an observation point."""
        assert str(observation_point) is not None


class TestObservationPointViewSet:
    """Test the ObservationPoint API endpoints."""

    def test_list_observation_points_authenticated(self, authenticated_client, observation_points_url, observation_point):
        """Test listing observation points when authenticated."""
        client, user = authenticated_client
        
        response = client.get(observation_points_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == observation_point.id
        assert response.data[0]['farm'] == observation_point.farm.id
        assert float(response.data[0]['latitude']) == float(observation_point.latitude)
        assert float(response.data[0]['longitude']) == float(observation_point.longitude)
        assert response.data[0]['observation_status'] == observation_point.observation_status
        assert response.data[0]['segment'] == observation_point.segment
        assert response.data[0]['inspection_suggestion'] == observation_point.inspection_suggestion.id
        assert response.data[0]['confidence_level'] == observation_point.confidence_level
        assert response.data[0]['target_entity'] == observation_point.target_entity
    
    def test_list_observation_points_unauthenticated(self, api_client, observation_points_url):
        """Test listing observation points when unauthenticated."""
        response = api_client.get(observation_points_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_observation_point_authenticated(self, authenticated_client, observation_points_url, farm, inspection_suggestion):
        """Test creating an observation point when authenticated."""
        client, user = authenticated_client
        
        data = {
            'farm': farm.id,
            'latitude': 37.7749,
            'longitude': -122.4194,
            'observation_status': 'Observed',
            'name': 'Test Observation Point',
            'segment': 5,
            'inspection_suggestion': inspection_suggestion.id,
            'confidence_level': 'High',
            'target_entity': 'Test Target'
        }
        
        response = client.post(
            observation_points_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['farm'] == data['farm']
        assert response.data['latitude'] == data['latitude']
        assert response.data['longitude'] == data['longitude']
        assert response.data['observation_status'] == data['observation_status']
        assert response.data['name'] == data['name']
        assert response.data['segment'] == data['segment']
        assert response.data['inspection_suggestion'] == data['inspection_suggestion']
        assert response.data['confidence_level'] == data['confidence_level']
        assert response.data['target_entity'] == data['target_entity']
        
        # Check that the observation point was created in the database
        assert ObservationPoint.objects.filter(name=data['name']).exists()
    
    def test_create_observation_point_unauthenticated(self, api_client, observation_points_url, farm, inspection_suggestion):
        """Test creating an observation point when unauthenticated."""
        data = {
            'farm': farm.id,
            'latitude': 37.7749,
            'longitude': -122.4194,
            'observation_status': 'Observed',
            'name': 'Test Observation Point',
            'segment': 5,
            'inspection_suggestion': inspection_suggestion.id,
            'confidence_level': 'High',
            'target_entity': 'Test Target'
        }
        
        response = api_client.post(
            observation_points_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the observation point was not created in the database
        assert not ObservationPoint.objects.filter(name=data['name']).exists()
    
    def test_retrieve_observation_point_authenticated(self, authenticated_client, observation_point_detail_url, observation_point):
        """Test retrieving an observation point when authenticated."""
        client, user = authenticated_client
        
        response = client.get(observation_point_detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == observation_point.id
        assert response.data['farm'] == observation_point.farm.id
        assert float(response.data['latitude']) == float(observation_point.latitude)
        assert float(response.data['longitude']) == float(observation_point.longitude)
        assert response.data['observation_status'] == observation_point.observation_status
        assert response.data['segment'] == observation_point.segment
        assert response.data['inspection_suggestion'] == observation_point.inspection_suggestion.id
        assert response.data['confidence_level'] == observation_point.confidence_level
        assert response.data['target_entity'] == observation_point.target_entity
    
    def test_retrieve_observation_point_unauthenticated(self, api_client, observation_point_detail_url):
        """Test retrieving an observation point when unauthenticated."""
        response = api_client.get(observation_point_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_observation_point_authenticated(self, authenticated_client, observation_point_detail_url, observation_point):
        """Test updating an observation point when authenticated."""
        client, user = authenticated_client
        
        data = {
            'farm': observation_point.farm.id,
            'latitude': 34.0522,
            'longitude': -118.2437,
            'observation_status': 'Pending',
            'name': 'Updated Observation Point',
            'segment': 3,
            'inspection_suggestion': observation_point.inspection_suggestion.id,
            'confidence_level': 'Medium',
            'target_entity': 'Updated Target'
        }
        
        response = client.put(
            observation_point_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['farm'] == data['farm']
        assert response.data['latitude'] == data['latitude']
        assert response.data['longitude'] == data['longitude']
        assert response.data['observation_status'] == data['observation_status']
        assert response.data['name'] == data['name']
        assert response.data['segment'] == data['segment']
        assert response.data['inspection_suggestion'] == data['inspection_suggestion']
        assert response.data['confidence_level'] == data['confidence_level']
        assert response.data['target_entity'] == data['target_entity']
        
        # Check that the observation point was updated in the database
        observation_point.refresh_from_db()
        assert observation_point.latitude == data['latitude']
        assert observation_point.longitude == data['longitude']
        assert observation_point.observation_status == data['observation_status']
        assert observation_point.name == data['name']
        assert observation_point.segment == data['segment']
        assert observation_point.confidence_level == data['confidence_level']
        assert observation_point.target_entity == data['target_entity']
    
    def test_update_observation_point_unauthenticated(self, api_client, observation_point_detail_url, observation_point):
        """Test updating an observation point when unauthenticated."""
        data = {
            'farm': observation_point.farm.id,
            'latitude': 34.0522,
            'longitude': -118.2437,
            'observation_status': 'Pending',
            'name': 'Updated Observation Point',
            'segment': 3,
            'inspection_suggestion': observation_point.inspection_suggestion.id,
            'confidence_level': 'Medium',
            'target_entity': 'Updated Target'
        }
        
        response = api_client.put(
            observation_point_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the observation point was not updated in the database
        observation_point.refresh_from_db()
        assert observation_point.name != data['name']
    
    def test_delete_observation_point_authenticated(self, authenticated_client, observation_point_detail_url, observation_point):
        """Test deleting an observation point when authenticated."""
        client, user = authenticated_client
        
        response = client.delete(observation_point_detail_url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the observation point was deleted from the database
        assert not ObservationPoint.objects.filter(id=observation_point.id).exists()
    
    def test_delete_observation_point_unauthenticated(self, api_client, observation_point_detail_url, observation_point):
        """Test deleting an observation point when unauthenticated."""
        response = api_client.delete(observation_point_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the observation point was not deleted from the database
        assert ObservationPoint.objects.filter(id=observation_point.id).exists()
