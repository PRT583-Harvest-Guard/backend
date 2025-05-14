import pytest
from rest_framework import status

pytestmark = [pytest.mark.django_db, pytest.mark.auth]


class TestUserInfoView:
    """Test the user info endpoint."""

    def test_get_user_info_authenticated(self, authenticated_client, user_info_url):
        """Test getting user info when authenticated."""
        client, user = authenticated_client
        
        response = client.get(user_info_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['phone_number'] == str(user.phone_number)
        assert response.data['email'] == user.email
        assert response.data['name'] == user.name
    
    def test_get_user_info_unauthenticated(self, api_client, user_info_url):
        """Test getting user info without authentication."""
        response = api_client.get(user_info_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
