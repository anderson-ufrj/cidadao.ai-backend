# API Integration Tests

This directory contains integration tests for the Portal da Transparência API.

## Test Files

- **simple_api_test.py**: Basic API connectivity test
- **test_correct_endpoints.py**: Tests for correct endpoint configuration
- **test_final_fix.py**: Final API fixes validation
- **test_transparency_api.py**: Core transparency API functionality tests
- **test_with_required_params.py**: Tests with required parameters
- **test_working_api.py**: Working API validation tests

## Running Tests

```bash
# Run all API integration tests
pytest tests/integration/api/

# Run specific test file
pytest tests/integration/api/test_transparency_api.py
```

## Note

These tests were moved from the `scripts/` directory to follow proper project organization standards.