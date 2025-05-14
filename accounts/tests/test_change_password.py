import pytest
from rest_framework import status
from accounts.models import RefreshToken
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db, pytest.mark.auth]


class TestChangePasswordView:
    """Test the change password endpoint."""

    def test_change_password_success(self, authenticated_client, change_password_url):
        """Test successful password change."""
        client, user = authenticated_client
        
        # Create a refresh token for the user
        refresh_token = RefreshToken.objects.create(
            user=user,
            token='test-token',
            expires_at=user.date_joined + pytest.importorskip('datetime').timedelta(days=1),
            is_valid=True
        )
        
        data = {
            'old_password': 'testpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = client.post(
            change_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        
        # Check that the password was changed
        user.refresh_from_db()
        assert user.check_password('newpassword123')
        
        # Check that all refresh tokens are now invalid
        refresh_token.refresh_from_db()
        assert not refresh_token.is_valid
    
    def test_change_password_wrong_old_password(self, authenticated_client, change_password_url):
        """Test password change with wrong old password."""
        client, user = authenticated_client
        
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = client.post(
            change_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'old_password' in response.data
        
        # Check that the password wasn't changed
        user.refresh_from_db()
        assert not user.check_password('newpassword123')
    
    def test_change_password_password_mismatch(self, authenticated_client, change_password_url):
        """Test password change with mismatched passwords."""
        client, user = authenticated_client
        
        data = {
            'old_password': 'testpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }
        
        response = client.post(
            change_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'confirm_password' in response.data
        
        # Check that the password wasn't changed
        user.refresh_from_db()
        assert not user.check_password('newpassword123')
    
    def test_change_password_short_password(self, authenticated_client, change_password_url):
        """Test password change with a password that's too short."""
        client, user = authenticated_client
        
        data = {
            'old_password': 'testpassword123',
            'new_password': 'short',
            'confirm_password': 'short'
        }
        
        response = client.post(
            change_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password' in response.data
        
        # Check that the password wasn't changed
        user.refresh_from_db()
        assert not user.check_password('short')
    
    def test_change_password_unauthenticated(self, api_client, change_password_url):
        """Test password change without authentication."""
        data = {
            'old_password': 'testpassword123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = api_client.post(
            change_password_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
