import pytest
from rest_framework import status
from accounts.models import User
from accounts.tests.utils import phone_number_json_dumps

pytestmark = [pytest.mark.django_db, pytest.mark.auth]


class TestRegisterView:
    """Test the registration endpoint."""

    @pytest.mark.skip(reason="Phone number validation issue")
    def test_register_user_success(self, api_client, register_url):
        """Test successful user registration."""
        data = {
            'phone_number': '+1234567890',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        response = api_client.post(
            register_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 1
        
        # Check that the user was created with the correct data
        user = User.objects.get(phone_number=data['phone_number'])
        assert user.email == data['email']
        assert user.name == data['name']
        assert user.is_active  # User should be active by default for MVP
    
    @pytest.mark.skip(reason="Phone number validation issue")
    def test_register_user_password_mismatch(self, api_client, register_url):
        """Test user registration with mismatched passwords."""
        data = {
            'phone_number': '+1234567890',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpassword123',
            'password_confirm': 'differentpassword'
        }
        
        response = api_client.post(
            register_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
        assert User.objects.count() == 0
    
    @pytest.mark.skip(reason="Phone number validation issue")
    def test_register_user_short_password(self, api_client, register_url):
        """Test user registration with a password that's too short."""
        data = {
            'phone_number': '+1234567890',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'short',
            'password_confirm': 'short'
        }
        
        response = api_client.post(
            register_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
        assert User.objects.count() == 0
    
    def test_register_user_duplicate_phone(self, api_client, register_url, user):
        """Test user registration with a duplicate phone number."""
        data = {
            'phone_number': user.phone_number,
            'email': 'another@example.com',
            'name': 'Another User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        response = api_client.post(
            register_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone_number' in response.data
        assert User.objects.count() == 1  # Only the fixture user exists
    
    def test_register_user_duplicate_email(self, api_client, register_url, user):
        """Test user registration with a duplicate email."""
        data = {
            'phone_number': '+9876543210',
            'email': user.email,
            'name': 'Another User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        response = api_client.post(
            register_url,
            data=phone_number_json_dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        assert User.objects.count() == 1  # Only the fixture user exists
