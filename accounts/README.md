# JWT Authentication System

This module implements a robust JWT-based authentication system for a Django REST API, designed to be consumed by a React Native app with offline support.

## Features

- **Custom User model** with phone_number (used for login), email, and password
- **Feature-flagged MFA** (optional for future implementation)
- **JWT authentication** using djangorestframework-simplejwt
- **Refresh tokens** stored in a Django model (database)
- **Password policy** with minimum length of 6 characters
- **Throttling** for login and OTP endpoints to prevent brute-force attacks
- **Offline support** for mobile apps

## Endpoints

All endpoints return JSON responses with appropriate HTTP status codes.

### Registration

- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Auth required**: No
- **Feature flag**: `is_mvp=True`
- **Request body**:
  ```json
  {
    "phone_number": "+1234567890",
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword",
    "password_confirm": "securepassword"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "detail": "User registered successfully."
  }
  ```

### Login

- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Auth required**: No
- **Request body**:
  ```json
  {
    "phone_number": "+1234567890",
    "password": "securepassword",
    "device_info": "iPhone 13, iOS 15.0" // Optional
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "phone_number": "+1234567890",
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
  ```

### Logout

- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Auth required**: Yes (JWT)
- **Request body**:
  ```json
  {
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "detail": "Successfully logged out."
  }
  ```

### Token Refresh

- **URL**: `/api/auth/token/refresh/`
- **Method**: `POST`
- **Auth required**: No
- **Request body**:
  ```json
  {
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." // Only included if token rotation is enabled
  }
  ```

### Forgot Password

- **URL**: `/api/auth/forgot-password/`
- **Method**: `POST`
- **Auth required**: No
- **Request body**:
  ```json
  {
    "phone_number": "+1234567890" // Or "email": "user@example.com"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "detail": "OTP has been sent to your email/phone."
  }
  ```

### Reset Password

- **URL**: `/api/auth/reset-password/`
- **Method**: `POST`
- **Auth required**: No
- **Request body**:
  ```json
  {
    "phone_number": "+1234567890", // Or "email": "user@example.com"
    "otp": "123456",
    "new_password": "newsecurepassword",
    "confirm_password": "newsecurepassword"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "detail": "Password has been reset successfully."
  }
  ```

### Change Password

- **URL**: `/api/auth/change-password/`
- **Method**: `POST`
- **Auth required**: Yes (JWT)
- **Request body**:
  ```json
  {
    "old_password": "securepassword",
    "new_password": "newsecurepassword",
    "confirm_password": "newsecurepassword"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "detail": "Password has been changed successfully."
  }
  ```

### Get User Info

- **URL**: `/api/auth/me/`
- **Method**: `GET`
- **Auth required**: Yes (JWT)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "phone_number": "+1234567890",
    "email": "user@example.com",
    "name": "John Doe"
  }
  ```

## Models

### User

Custom user model with phone_number as the username field.

```python
class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(blank=True, null=True, unique=True)
    name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(unique=True, null=False, blank=False)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='farmer')
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_mvp = models.BooleanField(default=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']
```

### RefreshToken

Model to store refresh tokens in the database.

```python
class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)
    device_info = models.TextField(blank=True, null=True)
```

### PasswordResetToken

Model to store password reset tokens/OTPs.

```python
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=6)  # 6-digit OTP
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
```

## Security Features

1. **Password Validation**: Minimum length of 6 characters, enforced by Django's password validators.
2. **Token Storage**: Refresh tokens are stored in the database, allowing for invalidation and tracking.
3. **Token Rotation**: Refresh tokens can be rotated for enhanced security.
4. **Throttling**: Login and OTP endpoints are throttled to prevent brute-force attacks.
5. **JWT Authentication**: Access tokens are short-lived (30 minutes) and refresh tokens are longer-lived (1 day).

## Offline Support

The mobile app can securely store tokens and refresh them in the background when connectivity returns. See `accounts/utils.py` for detailed documentation and implementation examples.

## Testing

Unit tests are provided for all endpoints in `accounts/tests.py`. Run them with:

```bash
python manage.py test accounts
```
