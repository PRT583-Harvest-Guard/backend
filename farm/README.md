# Farm Management API

This module implements a robust API for managing farms, boundary points, observation points, inspection suggestions, and inspection observations.

## Models

### Farm

The Farm model represents a farm with the following fields:

- `name`: The name of the farm
- `size`: The size of the farm in acres
- `plant_type`: The type of plants grown on the farm
- `created_at`: The date and time when the farm was created
- `user`: The user who owns the farm

### BoundaryPoint

The BoundaryPoint model represents a point on the boundary of a farm with the following fields:

- `farm`: The farm that the boundary point belongs to
- `latitude`: The latitude of the boundary point
- `longitude`: The longitude of the boundary point
- `description`: A description of the boundary point
- `timestamp`: The date and time when the boundary point was created

### ObservationPoint

The ObservationPoint model represents a point on the farm where an observation was made with the following fields:

- `farm`: The farm that the observation point belongs to
- `latitude`: The latitude of the observation point
- `longitude`: The longitude of the observation point
- `observation_status`: The status of the observation (e.g., "Nil", "Observed", "Pending")
- `name`: The name of the observation point
- `segment`: The segment of the farm where the observation point is located
- `created_at`: The date and time when the observation point was created
- `inspection_suggestion`: The inspection suggestion that the observation point is related to
- `confidence_level`: The confidence level of the observation
- `target_entity`: The target entity of the observation
- `mobile_id`: The ID of the observation point on the mobile device
- `last_synced`: The date and time when the observation point was last synced
- `sync_status`: The sync status of the observation point

### InspectionSuggestion

The InspectionSuggestion model represents a suggestion for an inspection with the following fields:

- `target_entity`: The target entity of the inspection suggestion
- `confidence_level`: The confidence level of the inspection suggestion
- `property_location`: The farm where the inspection suggestion is located
- `area_size`: The size of the area to be inspected
- `density_of_plant`: The density of plants in the area to be inspected
- `created_at`: The date and time when the inspection suggestion was created
- `user`: The user who created the inspection suggestion
- `mobile_id`: The ID of the inspection suggestion on the mobile device
- `last_synced`: The date and time when the inspection suggestion was last synced
- `sync_status`: The sync status of the inspection suggestion

### InspectionObservation

The InspectionObservation model represents an observation made during an inspection with the following fields:

- `date`: The date and time when the observation was made
- `inspection`: The inspection suggestion that the observation is related to
- `confidence`: The confidence level of the observation
- `section`: The boundary point where the observation was made
- `farm`: The farm where the observation was made
- `plant_per_section`: The number of plants per section
- `status`: The status of the observation
- `created_at`: The date and time when the observation was created
- `updated_at`: The date and time when the observation was last updated
- `target_entity`: The target entity of the observation
- `severity`: The severity of the observation
- `image`: An image of the observation
- `user`: The user who made the observation

## API Endpoints

### Farms

- `GET /api/farms/`: List all farms
- `POST /api/farms/`: Create a new farm
- `GET /api/farms/{id}/`: Retrieve a farm
- `PUT /api/farms/{id}/`: Update a farm
- `DELETE /api/farms/{id}/`: Delete a farm

### Boundary Points

- `GET /api/boundary-points/`: List all boundary points
- `POST /api/boundary-points/`: Create a new boundary point
- `GET /api/boundary-points/{id}/`: Retrieve a boundary point
- `PUT /api/boundary-points/{id}/`: Update a boundary point
- `DELETE /api/boundary-points/{id}/`: Delete a boundary point

### Observation Points

- `GET /api/observation-points/`: List all observation points
- `POST /api/observation-points/`: Create a new observation point
- `GET /api/observation-points/{id}/`: Retrieve an observation point
- `PUT /api/observation-points/{id}/`: Update an observation point
- `DELETE /api/observation-points/{id}/`: Delete an observation point
- `POST /api/observation-points/sync/`: Sync observation points
- `GET /api/observation-points/pending-sync/`: Get observation points that need to be synced

### Inspection Suggestions

- `GET /api/inspection-suggestions/`: List all inspection suggestions
- `POST /api/inspection-suggestions/`: Create a new inspection suggestion
- `GET /api/inspection-suggestions/{id}/`: Retrieve an inspection suggestion
- `PUT /api/inspection-suggestions/{id}/`: Update an inspection suggestion
- `DELETE /api/inspection-suggestions/{id}/`: Delete an inspection suggestion
- `POST /api/inspection-suggestions/sync/`: Sync inspection suggestions
- `GET /api/inspection-suggestions/pending-sync/`: Get inspection suggestions that need to be synced

### Inspection Observations

- `GET /api/inspection-observations/`: List all inspection observations
- `POST /api/inspection-observations/`: Create a new inspection observation
- `GET /api/inspection-observations/{id}/`: Retrieve an inspection observation
- `PUT /api/inspection-observations/{id}/`: Update an inspection observation
- `DELETE /api/inspection-observations/{id}/`: Delete an inspection observation

### Sync Data

- `POST /api/sync-data/`: Sync all data (farms, boundary points, observation points, inspection suggestions, and inspection observations)

## Testing

The farm app includes a comprehensive test suite that tests all models and API endpoints. The test suite is organized as follows:

```
farm/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Test fixtures and configuration
│   ├── test_farm.py             # Farm model and API endpoint tests
│   ├── test_boundary_point.py   # BoundaryPoint model and API endpoint tests
│   ├── test_observation_point.py # ObservationPoint model and API endpoint tests
│   ├── test_inspection_suggestion.py # InspectionSuggestion model and API endpoint tests
│   ├── test_inspection_observation.py # InspectionObservation model and API endpoint tests
│   └── test_sync_data.py        # SyncDataAPIView tests
```

### Running the Tests

You can run the tests using the provided `run_tests.sh` script:

```bash
# Make sure the script is executable
chmod +x run_tests.sh

# Run the tests
./run_tests.sh
```

Or you can run the tests directly using pytest:

```bash
# Run all tests with coverage report
python -m pytest farm/tests/ -v --cov=farm --cov-report=term-missing

# Run specific test files
python -m pytest farm/tests/test_farm.py -v

# Run tests with specific markers
python -m pytest farm/tests/ -v -m "django_db"
```

### Test Fixtures

The test suite includes several useful fixtures:

- `api_client`: A REST framework API client for making requests
- `user`: A test user with default credentials
- `authenticated_client`: An API client with authentication set up
- `farm`: A test farm
- `boundary_point`: A test boundary point
- `observation_point`: A test observation point
- `inspection_suggestion`: A test inspection suggestion
- `inspection_observation`: A test inspection observation
- URL fixtures for all endpoints

### Benefits of the Test Suite

1. **Comprehensive Coverage**: Tests all aspects of the farm management system
2. **Isolated Tests**: Each test is independent and focused on a specific functionality
3. **Reusable Fixtures**: Test data is created consistently across tests
4. **Coverage Reporting**: Identifies untested code paths
5. **Organized Structure**: Tests are organized by model for easy maintenance

The test suite ensures that all farm management endpoints work correctly and handle edge cases properly, providing confidence in the robustness of the system.
