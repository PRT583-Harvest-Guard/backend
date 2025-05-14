"""
Utility functions for the accounts app.
"""
import logging
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken

from accounts.models import RefreshToken

logger = logging.getLogger(__name__)


def create_tokens_for_user(user, device_info=None):
    """
    Create JWT tokens for a user and store the refresh token in the database.
    
    Args:
        user: The user to create tokens for
        device_info: Optional device information for the mobile app
        
    Returns:
        dict: A dictionary containing the access and refresh tokens
    """
    refresh = JWTRefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    # Store refresh token in database
    expires_at = timezone.now() + timedelta(days=1)  # Match SIMPLE_JWT settings
    RefreshToken.objects.create(
        user=user,
        token=refresh_token,
        expires_at=expires_at,
        device_info=device_info
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def refresh_token(refresh_token_str):
    """
    Refresh an access token using a refresh token.
    
    Args:
        refresh_token_str: The refresh token string
        
    Returns:
        dict: A dictionary containing the new access token and optionally a new refresh token
    """
    try:
        # Check if token exists and is valid
        token_obj = RefreshToken.objects.get(token=refresh_token_str, is_valid=True)
        
        # Check if token is expired
        if token_obj.expires_at < timezone.now():
            token_obj.is_valid = False
            token_obj.save()
            return None
        
        # Create new tokens
        refresh = JWTRefreshToken(refresh_token_str)
        access_token = str(refresh.access_token)
        
        response = {
            'access_token': access_token
        }
        
        # If ROTATE_REFRESH_TOKENS is True, create new refresh token
        if getattr(settings, 'SIMPLE_JWT', {}).get('ROTATE_REFRESH_TOKENS', False):
            # Invalidate old token
            token_obj.is_valid = False
            token_obj.save()
            
            # Create new refresh token
            new_refresh = JWTRefreshToken.for_user(token_obj.user)
            new_refresh_token = str(new_refresh)
            
            # Store new refresh token
            expires_at = timezone.now() + timedelta(days=1)
            RefreshToken.objects.create(
                user=token_obj.user,
                token=new_refresh_token,
                expires_at=expires_at,
                device_info=token_obj.device_info
            )
            
            response['refresh_token'] = new_refresh_token
        
        return response
        
    except RefreshToken.DoesNotExist:
        logger.warning(f"Invalid refresh token: {refresh_token_str[:10]}...")
        return None
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return None


def invalidate_refresh_token(refresh_token_str):
    """
    Invalidate a refresh token.
    
    Args:
        refresh_token_str: The refresh token string
        
    Returns:
        bool: True if the token was invalidated, False otherwise
    """
    try:
        token = RefreshToken.objects.get(token=refresh_token_str, is_valid=True)
        token.is_valid = False
        token.save()
        return True
    except RefreshToken.DoesNotExist:
        logger.warning(f"Invalid refresh token: {refresh_token_str[:10]}...")
        return False
    except Exception as e:
        logger.error(f"Error invalidating token: {str(e)}")
        return False


def invalidate_all_refresh_tokens(user):
    """
    Invalidate all refresh tokens for a user.
    
    Args:
        user: The user to invalidate tokens for
        
    Returns:
        int: The number of tokens invalidated
    """
    try:
        count, _ = RefreshToken.objects.filter(user=user, is_valid=True).update(is_valid=False)
        return count
    except Exception as e:
        logger.error(f"Error invalidating tokens: {str(e)}")
        return 0


"""
Mobile App Offline Flow Documentation

This document describes how the mobile app securely stores tokens and refreshes them in the background when connectivity returns.

## Token Storage

1. **Secure Storage**: The mobile app should store tokens in secure storage:
   - iOS: Keychain
   - Android: EncryptedSharedPreferences or Android Keystore

2. **Token Information**: Store the following information:
   - Access token
   - Refresh token
   - Access token expiry time
   - User information (id, phone_number, email, etc.)
   - Last sync timestamp

## Offline Authentication Flow

1. **Initial Authentication**:
   - User logs in with phone_number and password
   - Server returns access token, refresh token, and user information
   - App stores tokens and user information in secure storage
   - App sets up background refresh task

2. **Using the App While Online**:
   - App includes access token in Authorization header for all API requests
   - If a request returns 401 Unauthorized, app attempts to refresh the token
   - If refresh succeeds, app retries the original request with the new token
   - If refresh fails, app logs out the user and redirects to login screen

3. **Using the App While Offline**:
   - App checks if access token is expired
   - If expired, app marks that token refresh is needed when connectivity returns
   - App allows user to continue using cached data
   - App queues API requests for later execution

4. **When Connectivity Returns**:
   - App detects network connectivity
   - If token refresh is needed, app refreshes token in background
   - App processes queued API requests with the new token
   - App syncs local changes with the server

5. **Background Token Refresh**:
   - App sets up a background task to refresh token before it expires
   - Recommended to refresh when 75% of token lifetime has passed
   - For a 30-minute token, refresh after 22.5 minutes
   - This ensures the app always has a valid token when connectivity is available

6. **Security Considerations**:
   - Never store tokens in plain text or unencrypted storage
   - Implement token rotation (server already supports this)
   - Clear tokens on logout
   - Implement biometric authentication for accessing the app after background/inactivity

## Implementation Example (React Native)

```javascript
// Token storage utility
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import * as Keychain from 'react-native-keychain';

// Choose appropriate storage based on platform
const tokenStorage = {
  async saveTokens(tokens) {
    if (Platform.OS === 'ios') {
      await Keychain.setGenericPassword(
        'auth_tokens',
        JSON.stringify(tokens),
        { service: 'auth' }
      );
    } else {
      await SecureStore.setItemAsync('auth_tokens', JSON.stringify(tokens));
    }
  },
  
  async getTokens() {
    if (Platform.OS === 'ios') {
      const result = await Keychain.getGenericPassword({ service: 'auth' });
      return result ? JSON.parse(result.password) : null;
    } else {
      const tokens = await SecureStore.getItemAsync('auth_tokens');
      return tokens ? JSON.parse(tokens) : null;
    }
  },
  
  async clearTokens() {
    if (Platform.OS === 'ios') {
      await Keychain.resetGenericPassword({ service: 'auth' });
    } else {
      await SecureStore.deleteItemAsync('auth_tokens');
    }
  }
};

// API client with token refresh
import axios from 'axios';
import NetInfo from '@react-native-community/netinfo';

const api = axios.create({
  baseURL: 'https://api.example.com',
});

// Queue for offline requests
const requestQueue = [];

// Add interceptor to handle token refresh
api.interceptors.request.use(async (config) => {
  const tokens = await tokenStorage.getTokens();
  
  if (tokens && tokens.access_token) {
    config.headers.Authorization = `JWT ${tokens.access_token}`;
  }
  
  // Check if we're offline
  const netInfo = await NetInfo.fetch();
  if (!netInfo.isConnected) {
    // Queue request for later if it's not a token refresh request
    if (!config.url.includes('token/refresh')) {
      return new Promise((resolve, reject) => {
        requestQueue.push({
          config,
          resolve,
          reject,
        });
      });
    }
  }
  
  return config;
});

// Handle 401 errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't tried to refresh the token yet
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const tokens = await tokenStorage.getTokens();
        
        if (!tokens || !tokens.refresh_token) {
          // No refresh token, redirect to login
          await tokenStorage.clearTokens();
          // Navigate to login screen
          return Promise.reject(error);
        }
        
        // Try to refresh the token
        const response = await axios.post(
          'https://api.example.com/api/auth/token/refresh/',
          { refresh_token: tokens.refresh_token }
        );
        
        const newTokens = {
          ...tokens,
          access_token: response.data.access_token,
        };
        
        // If we got a new refresh token, update it
        if (response.data.refresh_token) {
          newTokens.refresh_token = response.data.refresh_token;
        }
        
        // Save the new tokens
        await tokenStorage.saveTokens(newTokens);
        
        // Retry the original request with the new token
        originalRequest.headers.Authorization = `JWT ${newTokens.access_token}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Token refresh failed, redirect to login
        await tokenStorage.clearTokens();
        // Navigate to login screen
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Function to process queued requests when connectivity returns
async function processQueue() {
  const queue = [...requestQueue];
  requestQueue.length = 0;
  
  for (const request of queue) {
    try {
      const response = await axios(request.config);
      request.resolve(response);
    } catch (error) {
      request.reject(error);
    }
  }
}

// Listen for network changes
NetInfo.addEventListener((state) => {
  if (state.isConnected) {
    // We're back online, process queued requests
    processQueue();
  }
});

// Background token refresh
import BackgroundFetch from 'react-native-background-fetch';

function setupBackgroundTokenRefresh() {
  BackgroundFetch.configure(
    {
      minimumFetchInterval: 15, // minutes
      stopOnTerminate: false,
      startOnBoot: true,
      enableHeadless: true,
    },
    async (taskId) => {
      try {
        const tokens = await tokenStorage.getTokens();
        
        if (tokens && tokens.refresh_token) {
          // Refresh the token
          const response = await axios.post(
            'https://api.example.com/api/auth/token/refresh/',
            { refresh_token: tokens.refresh_token }
          );
          
          const newTokens = {
            ...tokens,
            access_token: response.data.access_token,
          };
          
          if (response.data.refresh_token) {
            newTokens.refresh_token = response.data.refresh_token;
          }
          
          await tokenStorage.saveTokens(newTokens);
        }
        
        BackgroundFetch.finish(taskId);
      } catch (error) {
        BackgroundFetch.finish(taskId);
      }
    },
    (error) => {
      console.log('Background fetch failed to start:', error);
    }
  );
}
```

This implementation provides a robust solution for handling authentication in a React Native app with offline support. It securely stores tokens, refreshes them when needed, and queues API requests when offline.
"""
