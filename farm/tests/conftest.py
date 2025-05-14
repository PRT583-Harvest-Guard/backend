import pytest
from django.urls import reverse
from rest_framework.test import APIClient
import factory
import factory.fuzzy
from faker import Faker
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from farm.models import Farm, BoundaryPoint, ObservationPoint, InspectionSuggestion, InspectionObservation

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


class FarmFactory(factory.django.DjangoModelFactory):
    """Factory for creating Farm instances."""
    class Meta:
        model = Farm
    
    name = factory.Faker('company')
    size = factory.Faker('pyfloat', min_value=1, max_value=1000)
    plant_type = factory.Faker('word')
    user = factory.SubFactory(UserFactory)


class BoundaryPointFactory(factory.django.DjangoModelFactory):
    """Factory for creating BoundaryPoint instances."""
    class Meta:
        model = BoundaryPoint
    
    farm = factory.SubFactory(FarmFactory)
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    description = factory.Faker('sentence')


class InspectionSuggestionFactory(factory.django.DjangoModelFactory):
    """Factory for creating InspectionSuggestion instances."""
    class Meta:
        model = InspectionSuggestion
    
    target_entity = factory.Faker('word')
    confidence_level = factory.fuzzy.FuzzyChoice(['Low', 'Medium', 'High'])
    property_location = factory.SubFactory(FarmFactory)
    area_size = factory.Faker('pyfloat', min_value=1, max_value=100)
    density_of_plant = factory.Faker('random_int', min=1, max=100)
    user = factory.SelfAttribute('property_location.user')
    mobile_id = factory.Sequence(lambda n: n)
    last_synced = factory.LazyFunction(timezone.now)
    sync_status = 'synced'


class ObservationPointFactory(factory.django.DjangoModelFactory):
    """Factory for creating ObservationPoint instances."""
    class Meta:
        model = ObservationPoint
    
    farm = factory.SubFactory(FarmFactory)
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    observation_status = factory.fuzzy.FuzzyChoice(['Nil', 'Observed', 'Pending'])
    name = factory.Faker('word')
    segment = factory.Faker('random_int', min=1, max=10)
    inspection_suggestion = factory.SubFactory(InspectionSuggestionFactory)
    confidence_level = factory.fuzzy.FuzzyChoice(['Low', 'Medium', 'High'])
    target_entity = factory.Faker('word')
    mobile_id = factory.Sequence(lambda n: n)
    last_synced = factory.LazyFunction(timezone.now)
    sync_status = 'synced'


class InspectionObservationFactory(factory.django.DjangoModelFactory):
    """Factory for creating InspectionObservation instances."""
    class Meta:
        model = InspectionObservation
    
    date = factory.LazyFunction(timezone.now)
    inspection = factory.SubFactory(InspectionSuggestionFactory)
    confidence = factory.fuzzy.FuzzyChoice(['Low', 'Medium', 'High'])
    section = factory.SubFactory(BoundaryPointFactory)
    farm = factory.SelfAttribute('inspection.property_location')
    plant_per_section = factory.Faker('random_int', min=1, max=100)
    status = factory.fuzzy.FuzzyChoice(['Pending', 'Completed', 'Cancelled'])
    target_entity = factory.Faker('word')
    severity = factory.fuzzy.FuzzyChoice(['Low', 'Medium', 'High'])
    user = factory.SelfAttribute('inspection.user')


@pytest.fixture
def user():
    """Create a test user."""
    return UserFactory()


@pytest.fixture
def authenticated_client(user):
    """Return an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def farm(user):
    """Create a test farm."""
    return FarmFactory(user=user)


@pytest.fixture
def boundary_point(farm):
    """Create a test boundary point."""
    return BoundaryPointFactory(farm=farm)


@pytest.fixture
def inspection_suggestion(farm):
    """Create a test inspection suggestion."""
    return InspectionSuggestionFactory(property_location=farm, user=farm.user)


@pytest.fixture
def observation_point(farm, inspection_suggestion):
    """Create a test observation point."""
    return ObservationPointFactory(farm=farm, inspection_suggestion=inspection_suggestion)


@pytest.fixture
def inspection_observation(farm, inspection_suggestion, boundary_point):
    """Create a test inspection observation."""
    return InspectionObservationFactory(
        inspection=inspection_suggestion,
        farm=farm,
        section=boundary_point,
        user=farm.user
    )


# URL fixtures
@pytest.fixture
def farms_url():
    return reverse('farm-list')


@pytest.fixture
def farm_detail_url(farm):
    return reverse('farm-detail', kwargs={'pk': farm.pk})


@pytest.fixture
def boundary_points_url():
    return reverse('boundary-point-list')


@pytest.fixture
def boundary_point_detail_url(boundary_point):
    return reverse('boundary-point-detail', kwargs={'pk': boundary_point.pk})


@pytest.fixture
def observation_points_url():
    return reverse('observation-point-list')


@pytest.fixture
def observation_point_detail_url(observation_point):
    return reverse('observation-point-detail', kwargs={'pk': observation_point.pk})


@pytest.fixture
def inspection_suggestions_url():
    return reverse('inspection-suggestion-list')


@pytest.fixture
def inspection_suggestion_detail_url(inspection_suggestion):
    return reverse('inspection-suggestion-detail', kwargs={'pk': inspection_suggestion.pk})


@pytest.fixture
def inspection_observations_url():
    return reverse('inspection-observation-list')


@pytest.fixture
def inspection_observation_detail_url(inspection_observation):
    return reverse('inspection-observation-detail', kwargs={'pk': inspection_observation.pk})


@pytest.fixture
def sync_data_url():
    return reverse('sync-data')
