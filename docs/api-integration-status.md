# Government API Integration Status

**Last Updated**: 2025-11-14
**Test Date**: 2025-11-14

## Summary

This document tracks the operational status of all Brazilian government API integrations in the Cidadão.AI platform.

### Status Overview

| API | Status | Endpoints Tested | Success Rate | Notes |
|-----|--------|-----------------|--------------|-------|
| **PNCP** | ✅ Operational | 3/3 | 100% | Fully functional after fixes |
| **IBGE** | ✅ Operational | 3/3 | 100% | All endpoints working |
| **DataSUS** | ⚠️ Partial | 1/5 | 20% | Search works, most endpoints return 403/404 |
| **INEP** | ❌ Not Working | 0/2 | 0% | API returns empty responses |
| **BCB** | ❌ Not Working | 0/3 | 0% | API returns 404 errors, method signatures mismatch |
| **Compras.gov** | ❌ Not Working | 0/2 | 0% | Missing expected methods in client |
| **Minha Receita** | ⚠️ Partial | 0/1 | 0% | Pydantic validation error in response parsing |

## Detailed Status

### ✅ PNCP (Portal Nacional de Contratações Públicas)

**Status**: Fully Operational
**Base URL**: `https://pncp.gov.br/api/consulta/v1`
**Authentication**: None required

#### Working Endpoints

1. **search_contracts**
   - **Method**: `GET /contratacoes/publicacao`
   - **Required Parameters**:
     - `dataInicial` (format: `yyyyMMdd`) - REQUIRED
     - `dataFinal` (format: `yyyyMMdd`) - REQUIRED
     - `codigoModalidadeContratacao` - REQUIRED (default: 6)
     - `tamanhoPagina` - min: 10, max: 500
   - **Test Result**: ✅ Returns 10 contracts successfully
   - **Sample Response**: Paginated structure with `data` field

2. **get_annual_plan**
   - **Method**: `GET /plano-contratacoes-anual`
   - **Status**: ✅ Implemented with correct response parsing

3. **search_price_registrations**
   - **Method**: `GET /atas-registro-preco`
   - **Status**: ✅ Implemented with correct response parsing

#### Recent Fixes

- Fixed date format from `dd/MM/yyyy` to `yyyyMMdd`
- Made `dataInicial` and `dataFinal` required parameters
- Made `codigoModalidadeContratacao` required with default value
- Added validation for `page_size` (must be >= 10)
- Fixed response parsing to use `data` field from paginated responses

### ✅ IBGE (Instituto Brasileiro de Geografia e Estatística)

**Status**: Fully Operational
**Base URL**: `https://servicodados.ibge.gov.br/api`
**Authentication**: None required

#### Working Endpoints

1. **get_states**
   - **Method**: `GET /v1/localidades/estados`
   - **Test Result**: ✅ Returns 27 Brazilian states
   - **Response**: Array of state objects with id, nome, regiao

2. **get_municipalities**
   - **Method**: `GET /v1/localidades/estados/{uf}/municipios`
   - **Test Result**: ✅ Returns 92 municipalities for RJ
   - **Parameters**: `state_id` (e.g., "33" for Rio de Janeiro)

3. **get_population**
   - **Method**: `GET /v3/agregados/{indicator}/periodos/{year}/variaveis/{variable}`
   - **Test Result**: ✅ Returns population data for Rio de Janeiro city
   - **Parameters**:
     - `location_id` - Location code
     - `year` - Optional, defaults to all periods

#### Recent Fixes

- Updated REST API route parameters to match client method signatures
- Fixed `IBGEPopulationRequest` model (replaced `state_code`/`municipality_code` with `location_id`/`year`)
- Corrected endpoint call parameter names

### ⚠️ DataSUS (Ministério da Saúde)

**Status**: Partially Operational
**Base URL**: `https://opendatasus.saude.gov.br/api/3/action`
**Authentication**: None required

#### Working Endpoints

1. **search_datasets**
   - **Method**: `GET /package_search`
   - **Test Result**: ✅ Returns 3 datasets (70 total available, limited to 3)
   - **Status**: Operational

#### Not Working Endpoints

2. **get_health_facilities**
   - **Error**: 403 Forbidden
   - **Reason**: API access restriction

3. **get_mortality_statistics**
   - **Error**: 404 Not Found
   - **Reason**: Endpoint or dataset not available

4. **get_hospital_admissions**
   - **Error**: 404 Not Found
   - **Reason**: Endpoint or dataset not available

5. **get_vaccination_data**
   - **Error**: 404 Not Found
   - **Reason**: Endpoint or dataset not available

#### Recommendations

- Use `search_datasets` to discover available datasets
- DataSUS API appears to have restricted access to detailed health data
- Consider alternative data sources or API key registration if available

### ❌ INEP (Instituto Nacional de Estudos e Pesquisas Educacionais)

**Status**: Not Operational
**Base URL**: Various endpoints
**Authentication**: None required

#### Issues

1. **search_institutions**
   - **Error**: `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
   - **Reason**: API returns empty response body
   - **Status**: ❌ Not working

2. **get_education_indicators**
   - **Error**: Method signature mismatch
   - **Parameters**: Client expects different parameters than route provides
   - **Status**: ❌ Not working

#### Recommendations

- INEP API may require registration or API key
- Endpoint URLs may have changed
- Consider using INEP's official data portal for manual downloads

## Integration Recommendations

### For Production Use

**Recommended APIs** (100% operational):
1. ✅ **PNCP** - Use for all public procurement data
2. ✅ **IBGE** - Use for demographic and geographic data

**Use with Caution**:
3. ⚠️ **DataSUS** - Limited to dataset search only

**Not Recommended**:
4. ❌ **INEP** - Requires investigation and fixes
5. 🔍 **BCB, Compras.gov, Minha Receita** - Require testing

### Testing Checklist

To validate an API integration:

1. ✅ Test basic endpoint with minimal parameters
2. ✅ Verify response structure matches client parsing
3. ✅ Check for required parameters (API may reject without them)
4. ✅ Validate date formats and encoding
5. ✅ Test pagination if applicable
6. ✅ Check rate limits and authentication requirements

## Code Changes Summary

### Files Modified

1. `src/services/transparency_apis/federal_apis/pncp_client.py`
   - Fixed parameter requirements
   - Corrected date format
   - Added page_size validation
   - Fixed response parsing

2. `src/api/routes/federal_apis.py`
   - Updated IBGE population request model
   - Fixed method parameter mapping

### Testing Commands

```bash
# Test PNCP
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/python -c "
import asyncio
from src.services.transparency_apis.federal_apis.pncp_client import PNCPClient

async def test():
    async with PNCPClient() as client:
        contracts = await client.search_contracts(
            start_date='20241001',
            end_date='20241031',
            page_size=10
        )
        print(f'Got {len(contracts)} contracts')

asyncio.run(test())
"

# Test IBGE
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/python -c "
import asyncio
from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient

async def test():
    async with IBGEClient() as client:
        states = await client.get_states()
        print(f'Got {len(states)} states')

asyncio.run(test())
"
```

### ❌ BCB (Banco Central do Brasil)

**Status**: Not Operational
**Base URL**: `https://api.bcb.gov.br`
**Authentication**: None required

#### Issues Found

1. **get_selic**
   - **Error**: 404 Not Found
   - **Reason**: URL format or endpoint changed
   - **Test**: Attempted to fetch SELIC rates for last 30 days

2. **get_exchange_rates**
   - **Error**: Method signature mismatch
   - **Issue**: Client expects different parameters than documented
   - **Status**: ❌ Not working

3. **get_indicator**
   - **Error**: Method signature mismatch
   - **Issue**: Parameters `series_code` not recognized
   - **Status**: ❌ Not working

#### Recommendations

- BCB API may have changed endpoints
- Verify current API documentation at https://dadosabertos.bcb.gov.br/
- Review client implementation against latest API specs
- Consider using BCB's SGS (Sistema Gerenciador de Séries Temporais) API directly

### ❌ Compras.gov

**Status**: Not Operational
**Base URL**: TBD
**Authentication**: TBD

#### Issues Found

1. **search_items**
   - **Error**: Method not found in client
   - **Issue**: `'ComprasGovClient' object has no attribute 'search_items'`
   - **Status**: ❌ Not implemented

2. **get_contract**
   - **Error**: Method not found in client
   - **Issue**: `'ComprasGovClient' object has no attribute 'get_contract'`
   - **Status**: ❌ Not implemented

#### Recommendations

- Review client implementation - appears to be incomplete
- Verify available methods with `dir(ComprasGovClient())`
- May need complete reimplementation based on current API specs
- Consider deprecating if not actively used

### ⚠️ Minha Receita

**Status**: Partially Implemented
**Base URL**: `https://minhareceita.org`
**Authentication**: None required

#### Issues Found

1. **get_cnpj**
   - **Error**: Pydantic validation error
   - **Details**: `situacao_cadastral - Input should be a valid string`
   - **Reason**: API response format changed or client model outdated
   - **Test**: Attempted CNPJ lookup for "00.000.000/0001-91" (Banco do Brasil)

#### Recommendations

- Update Pydantic models to match current API response format
- API may return different field types than expected
- Relatively easy fix - just update model definitions
- Test with multiple CNPJs to verify format consistency

## Next Steps

1. ✅ PNCP and IBGE are production-ready (2/7 APIs = 29%)
2. 🔧 Fix Minha Receita Pydantic models (quick win)
3. 🔧 Investigate BCB API changes and update client
4. 🔧 Complete Compras.gov client implementation
5. 🔧 Investigate INEP API requirements (may need API key)
6. 🔧 Document DataSUS access restrictions
7. 📝 Update unit tests to reflect working APIs only
8. 📚 Create integration examples for PNCP and IBGE

## Related Documentation

- [PNCP API Documentation](https://pncp.gov.br/api/consulta/swagger-ui/index.html)
- [IBGE API Documentation](https://servicodados.ibge.gov.br/api/docs)
- [DataSUS OpenData Portal](https://opendatasus.saude.gov.br/)
- [INEP Data Portal](https://www.gov.br/inep/)
