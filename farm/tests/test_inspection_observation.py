import pytest
import json
from rest_framework import status
from farm.models import InspectionObservation
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db]


class TestInspectionObservationModel:
    """Test the InspectionObservation model."""

    def test_inspection_observation_creation(self, inspection_observation):
        """Test creating an inspection observation."""
        assert inspection_observation.id is not None
        assert inspection_observation.date is not None
        assert inspection_observation.inspection is not None
        assert inspection_observation.confidence is not None
        assert inspection_observation.section is not None
        assert inspection_observation.farm is not None
        assert inspection_observation.plant_per_section is not None
        assert inspection_observation.status is not None
        assert inspection_observation.created_at is not None
        assert inspection_observation.updated_at is not None
        assert inspection_observation.user is not None

    def test_inspection_observation_string_representation(self, inspection_observation):
        """Test the string representation of an inspection observation."""
        assert str(inspection_observation) is not None


class TestInspectionObservationViewSet:
    """Test the InspectionObservation API endpoints."""

    def test_list_inspection_observations_authenticated(self, authenticated_client, inspection_observations_url, inspection_observation):
        """Test listing inspection observations when authenticated."""
        client, user = authenticated_client
        
        response = client.get(inspection_observations_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == inspection_observation.id
        assert response.data[0]['date'] is not None
        assert response.data[0]['inspection'] == inspection_observation.inspection.id
        assert response.data[0]['confidence'] == inspection_observation.confidence
        assert response.data[0]['section'] == inspection_observation.section.id
        assert response.data[0]['farm'] == inspection_observation.farm.id
        assert str(response.data[0]['plant_per_section']) == str(inspection_observation.plant_per_section)
        assert response.data[0]['status'] == inspection_observation.status
        assert response.data[0]['target_entity'] == inspection_observation.target_entity
        assert response.data[0]['severity'] == inspection_observation.severity
        assert response.data[0]['user'] == user.id
    
    def test_list_inspection_observations_unauthenticated(self, api_client, inspection_observations_url):
        """Test listing inspection observations when unauthenticated."""
        response = api_client.get(inspection_observations_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_inspection_observation_authenticated(self, authenticated_client, inspection_observations_url, farm, inspection_suggestion, boundary_point):
        """Test creating an inspection observation when authenticated."""
        client, user = authenticated_client
        
        data = {
            'date': '2025-05-14T12:00:00Z',
            'inspection': inspection_suggestion.id,
            'confidence': 'High',
            'section': boundary_point.id,
            'farm': farm.id,
            'plant_per_section': '50',
            'status': 'Completed',
            'target_entity': 'Test Target',
            'severity': 'Medium',
            'user': user.id
        }
        
        response = client.post(
            inspection_observations_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == data['date']
        assert response.data['inspection'] == data['inspection']
        assert response.data['confidence'] == data['confidence']
        assert response.data['section'] == data['section']
        assert response.data['farm'] == data['farm']
        assert response.data['plant_per_section'] == data['plant_per_section']
        assert response.data['status'] == data['status']
        assert response.data['target_entity'] == data['target_entity']
        assert response.data['severity'] == data['severity']
        assert response.data['user'] == user.id
        
        # Check that the inspection observation was created in the database
        assert InspectionObservation.objects.filter(target_entity=data['target_entity']).exists()
    
    def test_create_inspection_observation_unauthenticated(self, api_client, inspection_observations_url, farm, inspection_suggestion, boundary_point):
        """Test creating an inspection observation when unauthenticated."""
        data = {
            'date': '2025-05-14T12:00:00Z',
            'inspection': inspection_suggestion.id,
            'confidence': 'High',
            'section': boundary_point.id,
            'farm': farm.id,
            'plant_per_section': '50',
            'status': 'Completed',
            'target_entity': 'Test Target',
            'severity': 'Medium'
        }
        
        response = api_client.post(
            inspection_observations_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the inspection observation was not created in the database
        assert not InspectionObservation.objects.filter(target_entity=data['target_entity']).exists()
    
    def test_retrieve_inspection_observation_authenticated(self, authenticated_client, inspection_observation_detail_url, inspection_observation):
        """Test retrieving an inspection observation when authenticated."""
        client, user = authenticated_client
        
        response = client.get(inspection_observation_detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == inspection_observation.id
        assert response.data['date'] is not None
        assert response.data['inspection'] == inspection_observation.inspection.id
        assert response.data['confidence'] == inspection_observation.confidence
        assert response.data['section'] == inspection_observation.section.id
        assert response.data['farm'] == inspection_observation.farm.id
        assert str(response.data['plant_per_section']) == str(inspection_observation.plant_per_section)
        assert response.data['status'] == inspection_observation.status
        assert response.data['target_entity'] == inspection_observation.target_entity
        assert response.data['severity'] == inspection_observation.severity
        assert response.data['user'] == user.id
    
    def test_retrieve_inspection_observation_unauthenticated(self, api_client, inspection_observation_detail_url):
        """Test retrieving an inspection observation when unauthenticated."""
        response = api_client.get(inspection_observation_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_inspection_observation_authenticated(self, authenticated_client, inspection_observation_detail_url, inspection_observation):
        """Test updating an inspection observation when authenticated."""
        client, user = authenticated_client
        
        data = {
            'date': '2025-05-15T12:00:00Z',
            'inspection': inspection_observation.inspection.id,
            'confidence': 'Medium',
            'section': inspection_observation.section.id,
            'farm': inspection_observation.farm.id,
            'plant_per_section': '75',
            'status': 'Pending',
            'target_entity': 'Updated Target',
            'severity': 'Low',
            'user': user.id
        }
        
        response = client.put(
            inspection_observation_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == data['date']
        assert response.data['inspection'] == data['inspection']
        assert response.data['confidence'] == data['confidence']
        assert response.data['section'] == data['section']
        assert response.data['farm'] == data['farm']
        assert response.data['plant_per_section'] == data['plant_per_section']
        assert response.data['status'] == data['status']
        assert response.data['target_entity'] == data['target_entity']
        assert response.data['severity'] == data['severity']
        assert response.data['user'] == user.id
        
        # Check that the inspection observation was updated in the database
        inspection_observation.refresh_from_db()
        assert inspection_observation.confidence == data['confidence']
        assert inspection_observation.plant_per_section == data['plant_per_section']
        assert inspection_observation.status == data['status']
        assert inspection_observation.target_entity == data['target_entity']
        assert inspection_observation.severity == data['severity']
    
    def test_update_inspection_observation_unauthenticated(self, api_client, inspection_observation_detail_url, inspection_observation):
        """Test updating an inspection observation when unauthenticated."""
        data = {
            'date': '2025-05-15T12:00:00Z',
            'inspection': inspection_observation.inspection.id,
            'confidence': 'Medium',
            'section': inspection_observation.section.id,
            'farm': inspection_observation.farm.id,
            'plant_per_section': '75',
            'status': 'Pending',
            'target_entity': 'Updated Target',
            'severity': 'Low'
        }
        
        response = api_client.put(
            inspection_observation_detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the inspection observation was not updated in the database
        inspection_observation.refresh_from_db()
        assert inspection_observation.target_entity != data['target_entity']
    
    def test_delete_inspection_observation_authenticated(self, authenticated_client, inspection_observation_detail_url, inspection_observation):
        """Test deleting an inspection observation when authenticated."""
        client, user = authenticated_client
        
        response = client.delete(inspection_observation_detail_url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the inspection observation was deleted from the database
        assert not InspectionObservation.objects.filter(id=inspection_observation.id).exists()
    
    def test_delete_inspection_observation_unauthenticated(self, api_client, inspection_observation_detail_url, inspection_observation):
        """Test deleting an inspection observation when unauthenticated."""
        response = api_client.delete(inspection_observation_detail_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the inspection observation was not deleted from the database
        assert InspectionObservation.objects.filter(id=inspection_observation.id).exists()
