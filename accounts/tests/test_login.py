import pytest
from rest_framework import status
from accounts.models import RefreshToken
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db, pytest.mark.auth]


class TestLoginView:
    """Test the login endpoint."""

    def test_login_user_success(self, api_client, login_url, user):
        """Test successful user login."""
        data = {
            'phone_number': user.phone_number,
            'password': 'testpassword123'
        }
        
        response = api_client.post(
            login_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        assert 'user' in response.data
        
        # Check that a refresh token was created in the database
        assert RefreshToken.objects.filter(user=user).exists()
    
    def test_login_user_with_device_info(self, api_client, login_url, user):
        """Test user login with device info."""
        data = {
            'phone_number': user.phone_number,
            'password': 'testpassword123',
            'device_info': 'iPhone 13, iOS 15.0, App v1.2.3'
        }
        
        response = api_client.post(
            login_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the device info was stored with the refresh token
        refresh_token = RefreshToken.objects.get(user=user)
        assert refresh_token.device_info == data['device_info']
    
    def test_login_user_invalid_credentials(self, api_client, login_url, user):
        """Test user login with invalid credentials."""
        data = {
            'phone_number': user.phone_number,
            'password': 'wrongpassword'
        }
        
        response = api_client.post(
            login_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not RefreshToken.objects.filter(user=user).exists()
    
    def test_login_user_inactive(self, api_client, login_url, user):
        """Test login with an inactive user."""
        # Set the user as inactive
        user.is_active = False
        user.save()
        
        data = {
            'phone_number': user.phone_number,
            'password': 'testpassword123'
        }
        
        response = api_client.post(
            login_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not RefreshToken.objects.filter(user=user).exists()
    
    @pytest.mark.skip(reason="Throttling interferes with this test")
    def test_login_missing_fields(self, api_client, login_url):
        """Test login with missing fields."""
        # Missing password
        data = {
            'phone_number': '+1234567890'
        }
        
        response = api_client.post(
            login_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Missing phone_number
        data = {
            'password': 'testpassword123'
        }
        
        response = api_client.post(
            login_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
