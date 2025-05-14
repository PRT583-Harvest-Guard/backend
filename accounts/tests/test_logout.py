import pytest
from rest_framework import status
from accounts.models import RefreshToken
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db, pytest.mark.auth]


class TestLogoutView:
    """Test the logout endpoint."""

    def test_logout_success(self, authenticated_client, logout_url, refresh_token):
        """Test successful logout."""
        client, user = authenticated_client
        
        data = {
            'refresh_token': refresh_token.token
        }
        
        response = client.post(
            logout_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the refresh token is now invalid
        refresh_token.refresh_from_db()
        assert not refresh_token.is_valid
    
    def test_logout_invalid_token(self, authenticated_client, logout_url):
        """Test logout with an invalid token."""
        client, user = authenticated_client
        
        data = {
            'refresh_token': 'invalid-token'
        }
        
        response = client.post(
            logout_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_logout_missing_token(self, authenticated_client, logout_url):
        """Test logout with a missing token."""
        client, user = authenticated_client
        
        data = {}
        
        response = client.post(
            logout_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_logout_unauthenticated(self, api_client, logout_url, refresh_token):
        """Test logout without authentication."""
        data = {
            'refresh_token': refresh_token.token
        }
        
        response = api_client.post(
            logout_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Check that the refresh token is still valid
        refresh_token.refresh_from_db()
        assert refresh_token.is_valid
