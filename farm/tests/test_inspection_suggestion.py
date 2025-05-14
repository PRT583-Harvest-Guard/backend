import pytest
import json
from rest_framework import status
from farm.models import InspectionSuggestion
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db]


class TestInspectionSuggestionModel:
    """Test the InspectionSuggestion model."""

    def test_inspection_suggestion_creation(self, inspection_suggestion):
        """Test creating an inspection suggestion."""
        assert inspection_suggestion.id is not None
        assert inspection_suggestion.target_entity is not None
        assert inspection_suggestion.confidence_level is not None
        assert inspection_suggestion.property_location is not None
        assert inspection_suggestion.area_size is not None
        assert inspection_suggestion.density_of_plant is not None
        assert inspection_suggestion.user is not None
        assert inspection_suggestion.created_at is not None

    def test_inspection_suggestion_string_representation(self, inspection_suggestion):
        """Test the string representation of an inspection suggestion."""
        assert str(inspection_suggestion) is not None


class TestInspectionSuggestionViewSet:
    """Test the InspectionSuggestion API endpoints."""

    def test_list_inspection_suggestions_authenticated(self, authenticated_client, inspection_suggestions_url, inspection_suggestion):
        """Test listing inspection suggestions when authenticated."""
        client, user = authenticated_client
        
        response = client.get(inspection_suggestions_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == inspection_suggestion.id
        assert response.data[0]['target_entity'] == inspection_suggestion.target_entity
        assert response.data[0]['confidence_level'] == inspection_suggestion.confidence_level
        assert response.data[0]['property_location'] == inspection_suggestion.property_location.id
        assert response.data[0]['area_size'] == inspection_suggestion.area_size
        assert response.data[0]['density_of_plant'] == inspection_suggestion.density_of_plant
        assert response.data[0]['user'] == user.id
    
    def test_list_inspection_suggestions_unauthenticated(self, api_client, inspection_suggestions_url):
        """Test listing inspection suggestions when unauthenticated."""
        response = api_client.get(inspection_suggestions_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_inspection_suggestion_authenticated(self, authenticated_client, inspection_suggestions_url, farm):
        """Test creating an inspection suggestion when authenticated."""
        client, user = authenticated_client
        
        data = {
            'target_entity': 'Test Target',
            'confidence_level': 'High',
            'property_location': farm.id,
            'area_size': 50.5,
            'density_of_plant': 75,
            'user': user.id
        }
        
        response = client.post(
            inspection_suggestions_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['target_entity'] == data['target_entity']
        assert response.data['confidence_level'] == data['confidence_level']
        assert response.data['property_location'] == data['property_location']
        assert response.data['area_size'] == data['area_size']
        assert response.data['density_of_plant'] == data['density_of_plant']
        assert response.data['user'] == user.id
        
        # Check that the inspection suggestion was created in the database
        assert InspectionSuggestion.objects.filter(target_entity=data['target_entity']).exists()
    
    def test_create_inspection_suggestion_unauthenticated(self, api_client, inspection_suggestions_url, farm):
        """Test creating an inspection suggestion when unauthenticated."""
        data = {
            'target_entity': 'Test Target',
            'confidence_level': 'High',
            'property_location': farm.id,
            'area_size': 50.5,
            'density_of_plant': 75
        }
        
        response = api_client.post(
            inspection_suggestions_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the inspection suggestion was not created in the database
        assert not InspectionSuggestion.objects.filter(target_entity=data['target_entity']).exists()
    
    def test_retrieve_inspection_suggestion_authenticated(self, authenticated_client, inspection_suggestion_detail_url, inspection_suggestion):
        """Test retrieving an inspection suggestion when authenticated."""
        client, user = authenticated_client
        
        response = client.get(inspection_suggestion_detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == inspection_suggestion.id
        assert response.data['target_entity'] == inspection_suggestion.target_entity
        assert response.data['confidence_level'] == inspection_suggestion.confidence_level
        assert response.data['property_location'] == inspection_suggestion.property_location.id
        assert response.data['area_size'] == inspection_suggestion.area_size
        assert response.data['density_of_plant'] == inspection_suggestion.density_of_plant
        assert response.data['user'] == user.id
    
    def test_retrieve_inspection_suggestion_unauthenticated(self, api_client, inspection_suggestion_detail_url):
        """Test retrieving an inspection suggestion when unauthenticated."""
        response = api_client.get(inspection_suggestion_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_inspection_suggestion_authenticated(self, authenticated_client, inspection_suggestion_detail_url, inspection_suggestion):
        """Test updating an inspection suggestion when authenticated."""
        client, user = authenticated_client
        
        data = {
            'target_entity': 'Updated Target',
            'confidence_level': 'Medium',
            'property_location': inspection_suggestion.property_location.id,
            'area_size': 75.5,
            'density_of_plant': 50,
            'user': user.id
        }
        
        response = client.put(
            inspection_suggestion_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['target_entity'] == data['target_entity']
        assert response.data['confidence_level'] == data['confidence_level']
        assert response.data['property_location'] == data['property_location']
        assert response.data['area_size'] == data['area_size']
        assert response.data['density_of_plant'] == data['density_of_plant']
        assert response.data['user'] == user.id
        
        # Check that the inspection suggestion was updated in the database
        inspection_suggestion.refresh_from_db()
        assert inspection_suggestion.target_entity == data['target_entity']
        assert inspection_suggestion.confidence_level == data['confidence_level']
        assert inspection_suggestion.area_size == data['area_size']
        assert inspection_suggestion.density_of_plant == data['density_of_plant']
    
    def test_update_inspection_suggestion_unauthenticated(self, api_client, inspection_suggestion_detail_url, inspection_suggestion):
        """Test updating an inspection suggestion when unauthenticated."""
        data = {
            'target_entity': 'Updated Target',
            'confidence_level': 'Medium',
            'property_location': inspection_suggestion.property_location.id,
            'area_size': 75.5,
            'density_of_plant': 50
        }
        
        response = api_client.put(
            inspection_suggestion_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the inspection suggestion was not updated in the database
        inspection_suggestion.refresh_from_db()
        assert inspection_suggestion.target_entity != data['target_entity']
    
    def test_delete_inspection_suggestion_authenticated(self, authenticated_client, inspection_suggestion_detail_url, inspection_suggestion):
        """Test deleting an inspection suggestion when authenticated."""
        client, user = authenticated_client
        
        response = client.delete(inspection_suggestion_detail_url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the inspection suggestion was deleted from the database
        assert not InspectionSuggestion.objects.filter(id=inspection_suggestion.id).exists()
    
    def test_delete_inspection_suggestion_unauthenticated(self, api_client, inspection_suggestion_detail_url, inspection_suggestion):
        """Test deleting an inspection suggestion when unauthenticated."""
        response = api_client.delete(inspection_suggestion_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the inspection suggestion was not deleted from the database
        assert InspectionSuggestion.objects.filter(id=inspection_suggestion.id).exists()
