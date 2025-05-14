from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
import json

from accounts.models import User, RefreshToken, PasswordResetToken


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.token_refresh_url = reverse('token_refresh')
        self.forgot_password_url = reverse('forgot_password')
        self.reset_password_url = reverse('reset_password')
        self.change_password_url = reverse('change_password')
        self.user_info_url = reverse('user_info')
        
        # Create a test user
        self.user_data = {
            'phone_number': '+1234567890',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        # Create a user for testing login, logout, etc.
        self.user = User.objects.create_user(
            phone_number='+9876543210',
            email='existing@example.com',
            name='Existing User',
            password='existingpassword123'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_register_user(self):
        """
        Test user registration.
        """
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # Including the one created in setUp
        
        # Check that the user was created with the correct data
        user = User.objects.get(phone_number=self.user_data['phone_number'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertTrue(user.is_active)  # User should be active by default for MVP
    
    def test_register_user_password_mismatch(self):
        """
        Test user registration with mismatched passwords.
        """
        data = self.user_data.copy()
        data['password_confirm'] = 'differentpassword'
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
    
    def test_register_user_short_password(self):
        """
        Test user registration with a password that's too short.
        """
        data = self.user_data.copy()
        data['password'] = 'short'
        data['password_confirm'] = 'short'
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_login_user(self):
        """
        Test user login.
        """
        data = {
            'phone_number': '+9876543210',
            'password': 'existingpassword123'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        
        # Check that a refresh token was created in the database
        self.assertTrue(RefreshToken.objects.filter(user=self.user).exists())
    
    def test_login_user_invalid_credentials(self):
        """
        Test user login with invalid credentials.
        """
        data = {
            'phone_number': '+9876543210',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_user(self):
        """
        Test user logout.
        """
        # First login to get a refresh token
        login_data = {
            'phone_number': '+9876543210',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        refresh_token = login_response.data['refresh_token']
        access_token = login_response.data['access_token']
        
        # Set the authorization header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')
        
        # Logout
        logout_data = {
            'refresh_token': refresh_token
        }
        
        response = self.client.post(
            self.logout_url,
            data=json.dumps(logout_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the refresh token is now invalid
        token = RefreshToken.objects.get(token=refresh_token)
        self.assertFalse(token.is_valid)
    
    def test_token_refresh(self):
        """
        Test token refresh.
        """
        # First login to get a refresh token
        login_data = {
            'phone_number': '+9876543210',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        refresh_token = login_response.data['refresh_token']
        
        # Refresh the token
        refresh_data = {
            'refresh_token': refresh_token
        }
        
        response = self.client.post(
            self.token_refresh_url,
            data=json.dumps(refresh_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
    
    def test_forgot_password(self):
        """
        Test forgot password.
        """
        data = {
            'email': 'existing@example.com'
        }
        
        response = self.client.post(
            self.forgot_password_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('otp', response.data)  # This would be removed in production
        
        # Check that a password reset token was created
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())
    
    def test_reset_password(self):
        """
        Test reset password.
        """
        # First request a password reset
        forgot_data = {
            'email': 'existing@example.com'
        }
        
        forgot_response = self.client.post(
            self.forgot_password_url,
            data=json.dumps(forgot_data),
            content_type='application/json'
        )
        
        otp = forgot_response.data['otp']
        
        # Reset the password
        reset_data = {
            'email': 'existing@example.com',
            'otp': otp,
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post(
            self.reset_password_url,
            data=json.dumps(reset_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the token is now marked as used
        token = PasswordResetToken.objects.get(token=otp)
        self.assertTrue(token.is_used)
        
        # Check that we can login with the new password
        login_data = {
            'phone_number': '+9876543210',
            'password': 'newpassword123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
    def test_change_password(self):
        """
        Test change password.
        """
        # First login to get an access token
        login_data = {
            'phone_number': '+9876543210',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        access_token = login_response.data['access_token']
        
        # Set the authorization header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')
        
        # Change the password
        change_data = {
            'old_password': 'existingpassword123',
            'new_password': 'changedpassword123',
            'confirm_password': 'changedpassword123'
        }
        
        response = self.client.post(
            self.change_password_url,
            data=json.dumps(change_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that all refresh tokens are now invalid
        self.assertFalse(RefreshToken.objects.filter(user=self.user, is_valid=True).exists())
        
        # Check that we can login with the new password
        login_data = {
            'phone_number': '+9876543210',
            'password': 'changedpassword123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
    def test_get_user_info(self):
        """
        Test get user info.
        """
        # First login to get an access token
        login_data = {
            'phone_number': '+9876543210',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        access_token = login_response.data['access_token']
        
        # Set the authorization header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')
        
        # Get user info
        response = self.client.get(self.user_info_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '+9876543210')
        self.assertEqual(response.data['email'], 'existing@example.com')
        self.assertEqual(response.data['name'], 'Existing User')
