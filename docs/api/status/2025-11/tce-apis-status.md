# 🏛️ TCE APIs Integration Status - 2025-11-14

**Subject**: State Audit Courts (Tribunais de Contas dos Estados)
**Coverage**: 6 TCE APIs tested across Brazilian states
**Status**: 2/6 Operational (33.3%), 4/6 Non-functional (66.7%)

---

## 📊 Executive Summary

Conducted comprehensive testing of all 6 implemented TCE (State Audit Court) APIs to identify which are currently functional. Results show significant API availability issues, with only TCE-SP and TCE-CE operational.

**Working APIs (2/6 - 33.3%)**:
- ✅ TCE-SP: 644 municipalities (São Paulo)
- ✅ TCE-CE: 185 municipalities (Ceará)

**Non-functional APIs (4/6 - 66.7%)**:
- ❌ TCE-BA: No public API (403 Forbidden)
- ❌ TCE-MG: SSL certificate errors
- ❌ TCE-PE: Returns 500 errors
- ❌ TCE-RJ: Connection/redirect issues

**Total Municipality Access**: 829 municipalities across 2 states

---

## ✅ WORKING APIS (2/6)

### 1. **TCE-SP - São Paulo** ✅ 100% Operational

**Base URL**: `https://transparencia.tce.sp.gov.br/api`
**Status**: Fully operational since October 2025
**Coverage**: 644 municipalities (100% of São Paulo state)

**Working Endpoints**:
- `/json/municipios` - Municipality list
- `/json/contratos` - Contracts
- `/json/licitacoes` - Bidding processes
- `/json/despesas` - Expenses
- `/json/receitas` - Revenues

**Test Results**:
```
Connection: ✅ PASSED
Municipalities: ✅ 644 found
Response format: JSON (direct array)
Authentication: None required
```

**Client Location**: `src/services/transparency_apis/tce_apis/tce_sp.py`

**Notable Features**:
- Fast response times (<500ms)
- Reliable endpoint availability
- Comprehensive fiscal data
- Well-documented API structure

**Use Cases**:
- Municipal fiscal analysis for São Paulo state
- Contract tracking and anomaly detection
- Budget execution monitoring
- Supplier concentration analysis

---

### 2. **TCE-CE - Ceará** ✅ 100% Operational

**Base URL**: `https://api-dados-abertos.tce.ce.gov.br`
**Status**: Operational after migration (fixed 2025-11-14)
**Coverage**: 185 municipalities (100% of Ceará state)

**Working Endpoints**:
- `/municipios` - Municipality list
- `/contratos` - Contracts
- `/licitacoes` - Bidding processes
- `/fornecedores` - Suppliers
- `/receitas` - Revenues
- `/despesas` - Expenses

**Test Results**:
```
Connection: ✅ PASSED
Municipalities: ✅ 185 found
Sample: ABAIARA (IBGE: 2300101)
Response format: JSON {"data": [...]}
Authentication: None required
```

**Client Location**: `src/services/transparency_apis/tce_apis/tce_ce.py`

**Recent Changes (2025-11-14)**:
- Migrated from deprecated SIM API (`api.tce.ce.gov.br/sim/1_0`)
- Now using open data portal (`api-dados-abertos.tce.ce.gov.br`)
- Updated response parsing for new `{"data": [...]}` format
- Fixed field mapping (`codigo_municipio` vs `geoibgeId`)
- Reduced timeout from 90s to 30s (new API is faster)

**Commit**: `e29554a` - "fix(apis): update TCE-CE client to use new open data API"

**Notable Features**:
- RESTful design
- Fast response times
- Standard JSON format
- Good data coverage

**Use Cases**:
- Municipal fiscal analysis for Ceará state
- Cross-state comparative analysis (CE vs SP)
- Contract and supplier tracking
- Revenue/expense monitoring

---

## ❌ NON-FUNCTIONAL APIS (4/6)

### 3. **TCE-BA - Bahia** ❌ No Public API

**Attempted URL**: `https://sistemas.tce.ba.gov.br/egestaoapi`
**Status**: Not accessible (403 Forbidden)
**Coverage**: 417 municipalities (cannot access)

**Issue**: Returns HTTP 403 Forbidden on all endpoints

**Test Results**:
```
GET /v1/municipios: ❌ 403 Forbidden
GET /v1/contratos: ❌ 403 Forbidden
GET /v1/licitacoes: ❌ 403 Forbidden
Portal page: ✅ 200 OK (but no API access)
```

**Error Message**:
```
Client error '403 Forbidden' for url 'https://sistemas.tce.ba.gov.br/egestaoapi/v1/municipios'
```

**Client Location**: `src/services/transparency_apis/tce_apis/tce_ba.py`

**Analysis**:
- API exists but is not publicly accessible
- Likely requires authentication, IP whitelisting, or registration
- Portal website (`www.tce.ba.gov.br/dados-abertos`) is accessible but returns HTML
- Only provides data downloads (ZIP/CSV files) via web interface

**Possible Solutions**:
1. ❌ Request API access credentials from TCE-BA (bureaucratic process)
2. ❌ Implement IP whitelisting if available (requires TCE-BA cooperation)
3. ⚠️ Web scraping of download page (fragile, maintenance-heavy)
4. ⚠️ Periodic download and parsing of CSV files (batch processing)

**Recommendation**: Mark TCE-BA as unavailable and focus on other states. Alternative data sources exist (SICONFI covers all 417 Bahia municipalities).

**Circuit Breaker**: Client correctly opens circuit breaker after 3 failed attempts to prevent further wasted requests.

---

### 4. **TCE-MG - Minas Gerais** ❌ SSL Certificate Issues

**Attempted URLs**:
- `https://www.tce.mg.gov.br/api`
- `https://dadosabertos.tce.mg.gov.br`
- `https://dadosabertos.tce.mg.gov.br/api/3/action` (CKAN)

**Status**: SSL certificate validation failure
**Coverage**: 853 municipalities (cannot access)

**Issue**: SSL certificate cannot be verified

**Test Results**:
```
All endpoints: ❌ [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
cURL test: ❌ SSL certificate problem: unable to get local issuer certificate
Status: Connection refused
```

**Error Message**:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

**Client Location**: `src/services/transparency_apis/tce_apis/tce_mg.py`

**Current Implementation**:
- Base URL configured for CKAN API: `https://dadosabertos.tce.mg.gov.br/api/3/action`
- Should work if SSL issues resolved
- Connection test attempts `/package_list` endpoint

**Analysis**:
- Server has SSL certificate configuration issues
- Certificate chain incomplete or self-signed
- Common with government servers using internal CAs
- Even with `-k` (insecure), returns HTML instead of JSON

**Possible Solutions**:
1. ⚠️ Disable SSL verification (`verify=False`) - **NOT RECOMMENDED** for production
2. ✅ Install TCE-MG's CA certificate if available
3. ✅ Contact TCE-MG about SSL configuration issues
4. ⚠️ Use HTTP instead of HTTPS if available (security risk)

**Recommendation**: Mark as unavailable until SSL issues resolved. Alternative: SICONFI covers all 853 Minas Gerais municipalities with proper SSL.

**Note**: Project author is from Minas Gerais - would prefer this API working, but security cannot be compromised.

---

### 5. **TCE-PE - Pernambuco** ❌ Returns Errors

**Attempted URL**: `https://sistemas.tce.pe.gov.br/DadosAbertos/api`
**Documentation**: `https://sistemas.tce.pe.gov.br/DadosAbertos/Exemplo!listar`
**Status**: Returns 500 Internal Server Error
**Coverage**: 185 municipalities (cannot access)

**Issue**: All endpoints return "ERRO" or 500 errors

**Test Results**:
```
GET /Municipios: ❌ HTTP 500, Response: "ERRO"
GET /Receitas: ❌ HTTP 500, Response: "ERRO"
GET /Contratos: ❌ HTTP 500, Response: "ERRO"
```

**Error Response**:
```
Status: 500 Internal Server Error
Body: ERRO
```

**Client Location**: `src/services/transparency_apis/tce_apis/tce_pe.py`

**Analysis**:
- API endpoints exist (documentation available)
- Server returns generic "ERRO" message
- May require:
  - Authentication headers
  - API key/token
  - Specific request parameters
  - Request headers (User-Agent, Content-Type, etc.)
- Documentation shows examples but unclear about authentication

**Possible Solutions**:
1. ✅ Review TCE-PE API documentation thoroughly
2. ✅ Contact TCE-PE for API access requirements
3. ⚠️ Add authentication if credentials available
4. ⚠️ Test with different HTTP headers and parameters

**Recommendation**: Mark as unavailable until authentication requirements clarified. SICONFI alternative available for all 185 Pernambuco municipalities.

**Documentation URL**: https://sistemas.tce.pe.gov.br/DadosAbertos/Exemplo!listar

---

### 6. **TCE-RJ - Rio de Janeiro** ❌ Connection Issues

**Attempted URLs**:
- `https://www.tce.rj.gov.br/dados-abertos`
- `https://api.tce.rj.gov.br`

**Status**: Connection errors and redirects
**Coverage**: 92 municipalities (cannot access)

**Issue**: Network connectivity and redirect problems

**Test Results**:
```
GET /dados-abertos: ❌ HTTP 302 (redirect)
Connection attempt: ❌ [Errno -2] Name or service not known
DNS resolution: Failed
```

**Error Message**:
```
[Errno -2] Name or service not known
```

**Client Location**: `src/services/transparency_apis/tce_apis/tce_rj.py`

**Analysis**:
- Portal page redirects (302)
- DNS resolution issues
- API endpoint may not exist or may be internal-only
- No clear API documentation found

**Possible Solutions**:
1. ✅ Research correct TCE-RJ API base URL
2. ✅ Check TCE-RJ open data portal for API info
3. ⚠️ Follow redirects to find actual endpoint
4. ⚠️ Contact TCE-RJ for API access information

**Recommendation**: Mark as unavailable until correct endpoint identified. SICONFI alternative available for all 92 Rio de Janeiro municipalities.

---

## 📈 Impact Analysis

### Current TCE Coverage

| State | TCE Status | Municipalities | Data Access |
|-------|-----------|----------------|-------------|
| São Paulo (SP) | ✅ Working | 644 | Via TCE-SP API |
| Ceará (CE) | ✅ Working | 185 | Via TCE-CE API |
| Bahia (BA) | ❌ 403 Forbidden | 417 | Via SICONFI fallback |
| Minas Gerais (MG) | ❌ SSL Error | 853 | Via SICONFI fallback |
| Pernambuco (PE) | ❌ 500 Error | 185 | Via SICONFI fallback |
| Rio de Janeiro (RJ) | ❌ Connection | 92 | Via SICONFI fallback |
| **TOTAL** | **2/6 Working** | **2,376** | **829 direct + 1,547 fallback** |

### Data Sources Summary

**Direct TCE Access**: 829 municipalities (34.9%)
- TCE-SP: 644 municipalities
- TCE-CE: 185 municipalities

**SICONFI Fallback**: 1,547 municipalities (65.1%)
- Covers all municipalities when TCE unavailable
- Federal data source (Tesouro Nacional)
- 5,570 total municipalities available via SICONFI

**Overall Coverage**: 100% of targeted municipalities have data access
- Either via direct TCE API (preferred)
- Or via SICONFI federal fallback (backup)

---

## 🎯 Recommendations

### Immediate Actions (Done)

1. ✅ **TCE-CE Migration Complete** - Updated to new API, now operational
2. ✅ **Documented Status** - All 6 TCEs tested and documented
3. ✅ **Committed Fix** - TCE-CE update committed (e29554a)

### Short Term (Next Week)

1. **TCE-MG**: Contact about SSL certificate issues
   - Minas Gerais is author's home state - priority for local data
   - 853 municipalities is significant coverage
   - May need CA certificate installation

2. **TCE-PE**: Review documentation for authentication requirements
   - Documentation exists but unclear about access
   - May just need correct headers or parameters

3. **TCE-BA**: Request API access credentials
   - Large state (417 municipalities)
   - May have registration process

### Medium Term (Future)

1. **TCE-RJ**: Research correct API endpoint
   - Smallest municipality count (92) - lower priority
   - DNS issues suggest endpoint moved or internal

2. **Fallback Strategy**: Ensure SICONFI integration robust
   - Already provides backup for all non-working TCEs
   - Test SICONFI data quality vs TCE data

3. **Monitoring**: Add health checks for working TCEs
   - TCE-SP and TCE-CE status monitoring
   - Alert if APIs go down
   - Track response times

### Long Term (Strategic)

1. **Alternative Sources**: Research other state audit courts
   - Brazil has 27 states - we've tested 6 TCEs
   - Identify which other states have APIs
   - Expand coverage to more states

2. **CKAN States**: Leverage existing CKAN state portals
   - 12 states have working CKAN portals
   - May include TCE data
   - Cross-reference with direct TCE APIs

---

## 🔧 Technical Details

### Client Implementations

All TCE clients inherit from `TransparencyAPIClient` base class:
- Automatic retry logic (3 attempts)
- Circuit breaker pattern (opens after 3 failures)
- Rate limiting (60 req/min default)
- Error logging and metrics
- Async context manager support

**Base Class**: `src/services/transparency_apis/base.py`

### Error Handling

All non-functional TCEs gracefully handle errors:
- Return empty arrays instead of throwing exceptions
- Log errors with structured logging
- Open circuit breaker to prevent retry storms
- Maintain type consistency (always return `list[dict]`)

### Testing Approach

Comprehensive test script: `test_tce_apis.py`
- Tests connection for all 6 TCEs
- Validates response formats
- Measures response times
- Documents real API behavior

---

## 📚 Documentation References

### Working APIs
- **TCE-SP**: https://transparencia.tce.sp.gov.br/api
- **TCE-CE**: https://api-dados-abertos.tce.ce.gov.br

### Portal Pages (No API Access)
- **TCE-BA**: https://www.tce.ba.gov.br/dados-abertos
- **TCE-MG**: https://dadosabertos.tce.mg.gov.br
- **TCE-PE**: https://sistemas.tce.pe.gov.br/DadosAbertos/Exemplo!listar
- **TCE-RJ**: https://www.tce.rj.gov.br/dados-abertos

### Fallback Source
- **SICONFI**: https://apidatalake.tesouro.gov.br/ords/siconfi/tt/

---

## 🏆 Achievements

1. **TCE-CE Restored**: Successfully migrated to new API after discovering endpoint change
2. **Complete Assessment**: Tested all 6 implemented TCE APIs
3. **Documented Reality**: Honest documentation of what works and what doesn't
4. **Fallback Verified**: Confirmed SICONFI provides coverage for non-working TCEs
5. **Zero Downtime**: Non-working TCEs fail gracefully without breaking the system

---

## ⚠️ Known Limitations

1. **Low TCE Success Rate**: Only 33.3% (2/6) TCEs working
2. **Geographic Concentration**: Both working TCEs are in Northeast/Southeast
3. **SSL Security**: Cannot use TCE-MG without compromising security
4. **No Authentication**: Cannot access TCE-BA without credentials
5. **Incomplete Documentation**: Some TCE APIs lack clear usage docs

---

## 💡 Key Insights

### What Works
- **TCE-SP**: Mature, stable API with excellent uptime
- **TCE-CE**: Recently migrated to modern open data platform
- **SICONFI Fallback**: Provides universal coverage when TCEs fail

### What Doesn't Work
- **SSL Issues**: Government servers often have certificate problems
- **Authentication**: Some TCEs require undocumented auth
- **Documentation**: API docs often incomplete or outdated
- **Stability**: TCE endpoints can change without notice (TCE-CE case)

### Lessons Learned
- Always implement graceful fallbacks (SICONFI)
- Test APIs regularly (TCE-CE endpoint changed)
- Document real behavior (not aspirational)
- Circuit breakers prevent cascade failures

---

## 📊 Statistics

**Total Municipalities Targeted**: 2,376
**Direct TCE Access**: 829 (34.9%)
**SICONFI Fallback Access**: 1,547 (65.1%)
**Overall Coverage**: 100%

**API Success Rate**: 33.3% (2/6)
**Data Access Rate**: 100% (with fallback)

**Client Files**: 6 implementations
**Test Coverage**: 100% of TCEs tested
**Documentation**: Comprehensive status report

---

**Author**: Anderson Henrique da Silva
**Created**: 2025-11-14
**Last Updated**: 2025-11-14
**Status**: ✅ Assessment Complete, 2 TCEs Operational

**Related Documents**:
- `docs/SICONFI_INTEGRATION_STATUS_2025_11_14.md` - SICONFI fallback details
- `docs/NEW_APIS_TO_INTEGRATE_2025_11_14.md` - Additional APIs to integrate
- `test_tce_apis.py` - Comprehensive TCE testing script
