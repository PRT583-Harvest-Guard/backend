#!/bin/bash

# Run pytest with coverage report
docker exec -it backend-web-1 python -m pytest accounts/tests/ -v --cov=accounts --cov-report=term-missing --no-cov-on-fail

# If you want to run specific test files, uncomment and modify the line below
# python -m pytest accounts/tests/test_register.py accounts/tests/test_login.py -v

# If you want to run tests with specific markers, uncomment and modify the line below
# python -m pytest accounts/tests/ -v -m "auth"
