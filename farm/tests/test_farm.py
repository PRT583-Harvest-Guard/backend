import pytest
import json
from rest_framework import status
from farm.models import Farm
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db]


class TestFarmModel:
    """Test the Farm model."""

    def test_farm_creation(self, farm):
        """Test creating a farm."""
        assert farm.id is not None
        assert farm.name is not None
        assert farm.size is not None
        assert farm.plant_type is not None
        assert farm.user is not None
        assert farm.created_at is not None

    def test_farm_string_representation(self, farm):
        """Test the string representation of a farm."""
        assert str(farm) is not None


class TestFarmViewSet:
    """Test the Farm API endpoints."""

    def test_list_farms_authenticated(self, authenticated_client, farms_url, farm):
        """Test listing farms when authenticated."""
        client, user = authenticated_client
        
        response = client.get(farms_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == farm.id
        assert response.data[0]['name'] == farm.name
        assert response.data[0]['size'] == farm.size
        assert response.data[0]['plant_type'] == farm.plant_type
        assert response.data[0]['user'] == user.id
    
    def test_list_farms_unauthenticated(self, api_client, farms_url):
        """Test listing farms when unauthenticated."""
        response = api_client.get(farms_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_farm_authenticated(self, authenticated_client, farms_url):
        """Test creating a farm when authenticated."""
        client, user = authenticated_client
        
        data = {
            'name': 'Test Farm',
            'size': 100.5,
            'plant_type': 'Corn',
            'user': user.id
        }
        
        response = client.post(
            farms_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['size'] == data['size']
        assert response.data['plant_type'] == data['plant_type']
        assert response.data['user'] == user.id
        
        # Check that the farm was created in the database
        assert Farm.objects.filter(name=data['name']).exists()
    
    def test_create_farm_unauthenticated(self, api_client, farms_url):
        """Test creating a farm when unauthenticated."""
        data = {
            'name': 'Test Farm',
            'size': 100.5,
            'plant_type': 'Corn'
        }
        
        response = api_client.post(
            farms_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the farm was not created in the database
        assert not Farm.objects.filter(name=data['name']).exists()
    
    def test_retrieve_farm_authenticated(self, authenticated_client, farm_detail_url, farm):
        """Test retrieving a farm when authenticated."""
        client, user = authenticated_client
        
        response = client.get(farm_detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == farm.id
        assert response.data['name'] == farm.name
        assert response.data['size'] == farm.size
        assert response.data['plant_type'] == farm.plant_type
        assert response.data['user'] == user.id
    
    def test_retrieve_farm_unauthenticated(self, api_client, farm_detail_url):
        """Test retrieving a farm when unauthenticated."""
        response = api_client.get(farm_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_farm_authenticated(self, authenticated_client, farm_detail_url, farm):
        """Test updating a farm when authenticated."""
        client, user = authenticated_client
        
        data = {
            'name': 'Updated Farm',
            'size': 200.5,
            'plant_type': 'Wheat',
            'user': user.id
        }
        
        response = client.put(
            farm_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == data['name']
        assert response.data['size'] == data['size']
        assert response.data['plant_type'] == data['plant_type']
        assert response.data['user'] == user.id
        
        # Check that the farm was updated in the database
        farm.refresh_from_db()
        assert farm.name == data['name']
        assert farm.size == data['size']
        assert farm.plant_type == data['plant_type']
    
    def test_update_farm_unauthenticated(self, api_client, farm_detail_url, farm):
        """Test updating a farm when unauthenticated."""
        data = {
            'name': 'Updated Farm',
            'size': 200.5,
            'plant_type': 'Wheat'
        }
        
        response = api_client.put(
            farm_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the farm was not updated in the database
        farm.refresh_from_db()
        assert farm.name != data['name']
    
    def test_delete_farm_authenticated(self, authenticated_client, farm_detail_url, farm):
        """Test deleting a farm when authenticated."""
        client, user = authenticated_client
        
        response = client.delete(farm_detail_url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the farm was deleted from the database
        assert not Farm.objects.filter(id=farm.id).exists()
    
    def test_delete_farm_unauthenticated(self, api_client, farm_detail_url, farm):
        """Test deleting a farm when unauthenticated."""
        response = api_client.delete(farm_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the farm was not deleted from the database
        assert Farm.objects.filter(id=farm.id).exists()
