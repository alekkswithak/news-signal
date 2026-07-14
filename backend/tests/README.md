# Test Suite

This directory contains comprehensive tests for the onion architecture backend.

## Test Structure

- `conftest.py`: Shared fixtures and test configuration
- `test_domain.py`: Domain layer entity tests
- `test_application.py`: Application layer use case tests
- `test_infrastructure.py`: Infrastructure layer repository tests
- `test_external_services.py`: External service client tests
- `test_api.py`: API endpoint integration tests

## Running Tests

### Install test dependencies:
```bash
pip install -r requirements.txt
```

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_domain.py
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run with verbose output:
```bash
pytest -v
```

## Test Coverage

- **Domain Layer**: Entity creation, validation, and business rules
- **Application Layer**: Use case logic, caching, and error handling
- **Infrastructure Layer**: MongoDB repository operations and external service calls
- **API Layer**: Endpoint validation, dependency injection, and integration

## Mocking Strategy

- **MongoDB**: Uses mongomock for in-memory database testing
- **HTTP Requests**: Uses respx for mocking external API calls
- **Dependencies**: Uses pytest fixtures for dependency injection
