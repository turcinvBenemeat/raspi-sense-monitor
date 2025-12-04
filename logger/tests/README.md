# Test Suite

This directory contains tests for the Raspberry Pi Sense HAT Monitor logger.

## Running Tests

Install test dependencies:
```bash
pip install -r requirements.txt
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_models.py
```

Run with verbose output:
```bash
pytest -v
```

## Test Structure

- `test_models.py` - Tests for data models (SenseHatData, RaspberryPiData)
- `test_config.py` - Tests for configuration management
- `test_sensors.py` - Tests for sensor readers (SenseHatReader, SystemReader)
- `test_database.py` - Tests for database operations
- `conftest.py` - Pytest fixtures and configuration

## Test Coverage

The test suite covers:
- ✅ Data model creation and validation
- ✅ Configuration loading from environment variables
- ✅ Sense HAT reader (with and without hardware)
- ✅ System metrics reader
- ✅ Database connection and operations
- ✅ Error handling and rollback

## Mocking

Tests use mocks for:
- Sense HAT hardware (not available in test environment)
- psutil system calls
- PostgreSQL database connections

This allows tests to run without requiring actual hardware or database connections.

