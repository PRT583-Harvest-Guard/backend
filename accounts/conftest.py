import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import factory
import factory.fuzzy
from faker import Faker
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, RefreshToken as RefreshTokenModel, PasswordResetToken

fake = Faker()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""
    class Meta:
        model = User
        django_get_or_create = ('phone_number',)
    
    phone_number = factory.Sequence(lambda n: f'+123456789{n}')
    email = factory.LazyAttribute(lambda o: f'user{o.phone_number.replace("+", "")}@example.com')
    name = factory.Faker('name')
    password = factory.PostGenerationMethodCall('set_password', 'testpassword123')
    is_active = True
    is_mvp = True


class RefreshTokenFactory(factory.django.DjangoModelFactory):
    """Factory for creating RefreshToken instances."""
    class Meta:
        model = RefreshTokenModel
    
    user = factory.SubFactory(UserFactory)
    token = factory.Faker('uuid4')
    created_at = factory.LazyFunction(timezone.now)
    expires_at = factory.LazyAttribute(lambda o: o.created_at + timedelta(days=1))
    is_valid = True
    device_info = factory.Faker('user_agent')


class PasswordResetTokenFactory(factory.django.DjangoModelFactory):
    """Factory for creating PasswordResetToken instances."""
    class Meta:
        model = PasswordResetToken
    
    user = factory.SubFactory(UserFactory)
    token = factory.fuzzy.FuzzyText(length=6, chars='0123456789')
    created_at = factory.LazyFunction(timezone.now)
    expires_at = factory.LazyAttribute(lambda o: o.created_at + timedelta(minutes=10))
    is_used = False


@pytest.fixture
def user():
    """Create a test user."""
    return UserFactory()


@pytest.fixture
def authenticated_client(user):
    """Return an authenticated API client."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    return client, user


@pytest.fixture
def refresh_token(user):
    """Create a refresh token for a user."""
    return RefreshTokenFactory(user=user)


@pytest.fixture
def password_reset_token(user):
    """Create a password reset token for a user."""
    return PasswordResetTokenFactory(user=user)


# URL fixtures
@pytest.fixture
def register_url():
    return reverse('register')


@pytest.fixture
def login_url():
    return reverse('login')


@pytest.fixture
def logout_url():
    return reverse('logout')


@pytest.fixture
def token_refresh_url():
    return reverse('token_refresh')


@pytest.fixture
def forgot_password_url():
    return reverse('forgot_password')


@pytest.fixture
def reset_password_url():
    return reverse('reset_password')


@pytest.fixture
def change_password_url():
    return reverse('change_password')


@pytest.fixture
def user_info_url():
    return reverse('user_info')
