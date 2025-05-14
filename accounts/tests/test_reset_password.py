import pytest
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db, pytest.mark.auth]


class TestResetPasswordView:
    """Test the reset password endpoint."""

    def test_reset_password_with_phone(self, api_client, reset_password_url, password_reset_token):
        """Test reset password with phone number."""
        user = password_reset_token.user
        
        data = {
            'phone_number': user.phone_number,
            'otp': password_reset_token.token,
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = api_client.post(
            reset_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        
        # Check that the token is now marked as used
        password_reset_token.refresh_from_db()
        assert password_reset_token.is_used
        
        # Check that we can login with the new password
        user.refresh_from_db()
        assert user.check_password('newpassword123')
    
    def test_reset_password_with_email(self, api_client, reset_password_url, password_reset_token):
        """Test reset password with email."""
        user = password_reset_token.user
        
        data = {
            'email': user.email,
            'otp': password_reset_token.token,
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = api_client.post(
            reset_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        
        # Check that the token is now marked as used
        password_reset_token.refresh_from_db()
        assert password_reset_token.is_used
        
        # Check that we can login with the new password
        user.refresh_from_db()
        assert user.check_password('newpassword123')
    
    def test_reset_password_invalid_otp(self, api_client, reset_password_url, password_reset_token):
        """Test reset password with an invalid OTP."""
        user = password_reset_token.user
        
        data = {
            'phone_number': user.phone_number,
            'otp': 'invalid',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = api_client.post(
            reset_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that the token is still not used
        password_reset_token.refresh_from_db()
        assert not password_reset_token.is_used
        
        # Check that the password hasn't changed
        user.refresh_from_db()
        assert not user.check_password('newpassword123')
    
    def test_reset_password_expired_otp(self, api_client, reset_password_url, password_reset_token):
        """Test reset password with an expired OTP."""
        user = password_reset_token.user
        
        # Set the token as expired
        password_reset_token.expires_at = timezone.now() - timedelta(minutes=1)
        password_reset_token.save()
        
        data = {
            'phone_number': user.phone_number,
            'otp': password_reset_token.token,
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = api_client.post(
            reset_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that the token is still not used
        password_reset_token.refresh_from_db()
        assert not password_reset_token.is_used
        
        # Check that the password hasn't changed
        user.refresh_from_db()
        assert not user.check_password('newpassword123')
    
    def test_reset_password_used_otp(self, api_client, reset_password_url, password_reset_token):
        """Test reset password with an already used OTP."""
        user = password_reset_token.user
        
        # Set the token as used
        password_reset_token.is_used = True
        password_reset_token.save()
        
        data = {
            'phone_number': user.phone_number,
            'otp': password_reset_token.token,
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = api_client.post(
            reset_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that the password hasn't changed
        user.refresh_from_db()
        assert not user.check_password('newpassword123')
    
    def test_reset_password_password_mismatch(self, api_client, reset_password_url, password_reset_token):
        """Test reset password with mismatched passwords."""
        user = password_reset_token.user
        
        data = {
            'phone_number': user.phone_number,
            'otp': password_reset_token.token,
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }
        
        response = api_client.post(
            reset_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'confirm_password' in response.data
        
        # Check that the token is still not used
        password_reset_token.refresh_from_db()
        assert not password_reset_token.is_used
        
        # Check that the password hasn't changed
        user.refresh_from_db()
        assert not user.check_password('newpassword123')
    
    def test_reset_password_short_password(self, api_client, reset_password_url, password_reset_token):
        """Test reset password with a password that's too short."""
        user = password_reset_token.user
        
        data = {
            'phone_number': user.phone_number,
            'otp': password_reset_token.token,
            'new_password': 'short',
            'confirm_password': 'short'
        }
        
        response = api_client.post(
            reset_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password' in response.data
        
        # Check that the token is still not used
        password_reset_token.refresh_from_db()
        assert not password_reset_token.is_used
        
        # Check that the password hasn't changed
        user.refresh_from_db()
        assert not user.check_password('short')
