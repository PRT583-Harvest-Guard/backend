#!/bin/bash

# Run pytest with coverage report for accounts app
# python -m pytest  -v --cov=accounts --cov-report=term-missing --no-cov-on-fail

# Run pytest with coverage report for farm app
# python -m pytest farm/tests/ -v --cov=farm --cov-report=term-missing --no-cov-on-fail

# Run all tests with coverage report for both apps
# python -m pytest accounts/tests/ farm/tests/ -v --cov=accounts --cov=farm --cov-report=term-missing --no-cov-on-fail

# If you want to run specific test files, uncomment and modify the line below
# python -m pytest accounts/tests/test_register.py farm/tests/test_farm.py -v

# If you want to run tests with specific markers, uncomment and modify the line below
# python -m pytest accounts/tests/ farm/tests/ -v -m "auth"

docker exec -it backend-web-1 pytest
