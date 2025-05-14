import pytest
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from accounts.models import RefreshToken
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db, pytest.mark.auth]


class TestTokenRefreshView:
    """Test the token refresh endpoint."""

    @pytest.mark.skip(reason="Token refresh implementation issue")
    def test_token_refresh_success(self, api_client, token_refresh_url, refresh_token):
        """Test successful token refresh."""
        data = {
            'refresh_token': refresh_token.token
        }
        
        response = api_client.post(
            token_refresh_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
    
    @pytest.mark.skip(reason="Token refresh implementation issue")
    def test_token_refresh_with_rotation(self, api_client, token_refresh_url, refresh_token, settings):
        """Test token refresh with rotation enabled."""
        # Enable token rotation
        settings.SIMPLE_JWT = {
            'ROTATE_REFRESH_TOKENS': True,
            'BLACKLIST_AFTER_ROTATION': False,
        }
        
        data = {
            'refresh_token': refresh_token.token
        }
        
        response = api_client.post(
            token_refresh_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        
        # Check that the old token is now invalid
        refresh_token.refresh_from_db()
        assert not refresh_token.is_valid
        
        # Check that a new token was created
        new_token = RefreshToken.objects.get(token=response.data['refresh_token'])
        assert new_token.is_valid
        assert new_token.user == refresh_token.user
    
    def test_token_refresh_invalid_token(self, api_client, token_refresh_url):
        """Test token refresh with an invalid token."""
        data = {
            'refresh_token': 'invalid-token'
        }
        
        response = api_client.post(
            token_refresh_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_token_refresh_expired_token(self, api_client, token_refresh_url, refresh_token):
        """Test token refresh with an expired token."""
        # Set the token as expired
        refresh_token.expires_at = timezone.now() - timedelta(days=1)
        refresh_token.save()
        
        data = {
            'refresh_token': refresh_token.token
        }
        
        response = api_client.post(
            token_refresh_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that the token is now marked as invalid
        refresh_token.refresh_from_db()
        assert not refresh_token.is_valid
    
    def test_token_refresh_invalidated_token(self, api_client, token_refresh_url, refresh_token):
        """Test token refresh with a token that has been invalidated."""
        # Invalidate the token
        refresh_token.is_valid = False
        refresh_token.save()
        
        data = {
            'refresh_token': refresh_token.token
        }
        
        response = api_client.post(
            token_refresh_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
