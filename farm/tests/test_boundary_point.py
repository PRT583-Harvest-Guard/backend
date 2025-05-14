import pytest
import json
from rest_framework import status
from farm.models import BoundaryPoint
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db]


class TestBoundaryPointModel:
    """Test the BoundaryPoint model."""

    def test_boundary_point_creation(self, boundary_point):
        """Test creating a boundary point."""
        assert boundary_point.id is not None
        assert boundary_point.farm is not None
        assert boundary_point.latitude is not None
        assert boundary_point.longitude is not None
        assert boundary_point.timestamp is not None

    def test_boundary_point_string_representation(self, boundary_point):
        """Test the string representation of a boundary point."""
        assert str(boundary_point) is not None


class TestBoundaryPointViewSet:
    """Test the BoundaryPoint API endpoints."""

    def test_list_boundary_points_authenticated(self, authenticated_client, boundary_points_url, boundary_point):
        """Test listing boundary points when authenticated."""
        client, user = authenticated_client
        
        response = client.get(boundary_points_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == boundary_point.id
        assert response.data[0]['farm'] == boundary_point.farm.id
        assert float(response.data[0]['latitude']) == float(boundary_point.latitude)
        assert float(response.data[0]['longitude']) == float(boundary_point.longitude)
        assert response.data[0]['description'] == boundary_point.description
    
    def test_list_boundary_points_unauthenticated(self, api_client, boundary_points_url):
        """Test listing boundary points when unauthenticated."""
        response = api_client.get(boundary_points_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_boundary_point_authenticated(self, authenticated_client, boundary_points_url, farm):
        """Test creating a boundary point when authenticated."""
        client, user = authenticated_client
        
        data = {
            'farm': farm.id,
            'latitude': 37.7749,
            'longitude': -122.4194,
            'description': 'Test Boundary Point'
        }
        
        response = client.post(
            boundary_points_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['farm'] == data['farm']
        assert response.data['latitude'] == data['latitude']
        assert response.data['longitude'] == data['longitude']
        assert response.data['description'] == data['description']
        
        # Check that the boundary point was created in the database
        assert BoundaryPoint.objects.filter(description=data['description']).exists()
    
    def test_create_boundary_point_unauthenticated(self, api_client, boundary_points_url, farm):
        """Test creating a boundary point when unauthenticated."""
        data = {
            'farm': farm.id,
            'latitude': 37.7749,
            'longitude': -122.4194,
            'description': 'Test Boundary Point'
        }
        
        response = api_client.post(
            boundary_points_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the boundary point was not created in the database
        assert not BoundaryPoint.objects.filter(description=data['description']).exists()
    
    def test_retrieve_boundary_point_authenticated(self, authenticated_client, boundary_point_detail_url, boundary_point):
        """Test retrieving a boundary point when authenticated."""
        client, user = authenticated_client
        
        response = client.get(boundary_point_detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == boundary_point.id
        assert response.data['farm'] == boundary_point.farm.id
        assert float(response.data['latitude']) == float(boundary_point.latitude)
        assert float(response.data['longitude']) == float(boundary_point.longitude)
        assert response.data['description'] == boundary_point.description
    
    def test_retrieve_boundary_point_unauthenticated(self, api_client, boundary_point_detail_url):
        """Test retrieving a boundary point when unauthenticated."""
        response = api_client.get(boundary_point_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_boundary_point_authenticated(self, authenticated_client, boundary_point_detail_url, boundary_point):
        """Test updating a boundary point when authenticated."""
        client, user = authenticated_client
        
        data = {
            'farm': boundary_point.farm.id,
            'latitude': 34.0522,
            'longitude': -118.2437,
            'description': 'Updated Boundary Point'
        }
        
        response = client.put(
            boundary_point_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['farm'] == data['farm']
        assert response.data['latitude'] == data['latitude']
        assert response.data['longitude'] == data['longitude']
        assert response.data['description'] == data['description']
        
        # Check that the boundary point was updated in the database
        boundary_point.refresh_from_db()
        assert boundary_point.latitude == data['latitude']
        assert boundary_point.longitude == data['longitude']
        assert boundary_point.description == data['description']
    
    def test_update_boundary_point_unauthenticated(self, api_client, boundary_point_detail_url, boundary_point):
        """Test updating a boundary point when unauthenticated."""
        data = {
            'farm': boundary_point.farm.id,
            'latitude': 34.0522,
            'longitude': -118.2437,
            'description': 'Updated Boundary Point'
        }
        
        response = api_client.put(
            boundary_point_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the boundary point was not updated in the database
        boundary_point.refresh_from_db()
        assert boundary_point.description != data['description']
    
    def test_delete_boundary_point_authenticated(self, authenticated_client, boundary_point_detail_url, boundary_point):
        """Test deleting a boundary point when authenticated."""
        client, user = authenticated_client
        
        response = client.delete(boundary_point_detail_url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the boundary point was deleted from the database
        assert not BoundaryPoint.objects.filter(id=boundary_point.id).exists()
    
    def test_delete_boundary_point_unauthenticated(self, api_client, boundary_point_detail_url, boundary_point):
        """Test deleting a boundary point when unauthenticated."""
        response = api_client.delete(boundary_point_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the boundary point was not deleted from the database
        assert BoundaryPoint.objects.filter(id=boundary_point.id).exists()
