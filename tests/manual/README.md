# Manual Testing Scripts

This directory contains manual testing scripts for validating specific components and integrations.

## Directory Structure

```
manual/
├── api/          # API integration tests
├── chat/         # Chat endpoint tests
├── portal/       # Portal da Transparência tests
└── *.py          # General flow tests
```

## API Tests (`api/`)

Test scripts for external API integrations:

- **`test_all_apis_comprehensive.py`** - Comprehensive test of all federal/state APIs
- **`test_all_apis_review.py`** - Review and validation of API endpoints
- **`test_ckan_states.py`** - Test state CKAN portals (Ceará, Pernambuco, etc.)
- **`test_siconfi.py`** - SICONFI (Treasury) API integration test
- **`test_siconfi_comprehensive.py`** - Detailed SICONFI endpoint testing
- **`test_tce_apis.py`** - TCE (State Court of Accounts) APIs test

### Running API Tests
```bash
# Test specific API
JWT_SECRET_KEY=test SECRET_KEY=test python tests/manual/api/test_siconfi.py

# Test all APIs
JWT_SECRET_KEY=test SECRET_KEY=test python tests/manual/api/test_all_apis_comprehensive.py
```

## Chat Tests (`chat/`)

Test scripts for chat endpoint functionality:

- **`test_chat_endpoint_local.py`** - Local chat endpoint validation
- **`test_chat_integration.py`** - Integration test for chat flow
- **`test_chat_real_scenarios.py`** - Real-world scenario testing
- **`test_production_chat.py`** - Production chat endpoint test

### Running Chat Tests
```bash
# Local test
JWT_SECRET_KEY=test SECRET_KEY=test python tests/manual/chat/test_chat_endpoint_local.py

# Production test
python tests/manual/chat/test_production_chat.py
```

## Portal Tests (`portal/`)

Test scripts for Portal da Transparência integration:

- **`test_portal_api_fix.py`** - Validate portal API fix (orgao parameter)
- **`test_portal_direct.py`** - Direct portal API calls
- **`test_production_portal_fix.py`** - Production portal fix verification

### Running Portal Tests
```bash
# Local test
JWT_SECRET_KEY=test SECRET_KEY=test python tests/manual/portal/test_portal_api_fix.py

# Production test
python tests/manual/portal/test_production_portal_fix.py
```

## Flow Tests (Root)

End-to-end flow validation scripts:

- **`test_complete_flow.py`** - Complete investigation flow test
- **`test_entity_extraction_integration.py`** - Entity extraction integration
- **`test_intent_classification.py`** - Intent classification validation
- **`test_intent_to_zumbi_flow.py`** - Intent to agent routing flow
- **`test_import_investigator.py`** - Investigator agent import test
- **`test_railway_database.py`** - Railway database connection test

### Running Flow Tests
```bash
# Complete flow
JWT_SECRET_KEY=test SECRET_KEY=test python tests/manual/test_complete_flow.py

# Intent classification
JWT_SECRET_KEY=test SECRET_KEY=test python tests/manual/test_intent_classification.py
```

## Important Notes

### Environment Variables
Most tests require environment variables to avoid auth failures:
```bash
export JWT_SECRET_KEY=test
export SECRET_KEY=test
```

### Production Tests
Tests with `production` in the name call the Railway production API:
- **URL**: `https://cidadao-api-production.up.railway.app`
- **No credentials needed** (uses test session)

### Test Coverage
These manual tests complement the automated test suite in `tests/unit/` and `tests/integration/`. Use them for:
- Validating fixes before deployment
- Testing external API integrations
- Debugging production issues
- Verifying complete flows end-to-end

## Adding New Tests

When adding new manual tests:
1. Choose appropriate subdirectory (`api/`, `chat/`, `portal/`)
2. Use descriptive names: `test_<component>_<scenario>.py`
3. Add docstring explaining what the test does
4. Document required environment variables
5. Update this README with test description

## Related Documentation

- Automated tests: See `tests/unit/README.md` and `tests/integration/README.md`
- API documentation: See `docs/api/`
- Testing guide: See `docs/testing/`
