# 🔍 TCE-MG Deep Investigation - 2025-11-14

**Subject**: Comprehensive investigation of TCE Minas Gerais data access
**Status**: ❌ No public API access available
**Coverage Attempted**: 853 municipalities

---

## 📊 Executive Summary

Conducted comprehensive investigation of TCE-MG (Tribunal de Contas do Estado de Minas Gerais) data access options. **Conclusion: No working public API available due to SSL certificate issues and access restrictions.**

**Key Findings**:
1. ❌ TCE-MG dedicated portal (`dadosabertos.tce.mg.gov.br`) - SSL certificate errors
2. ❌ State CKAN portal (`dados.mg.gov.br/api/3`) - Returns 403 Forbidden
3. ❌ All tested endpoints return errors or require authentication
4. ✅ SICONFI fallback available for all 853 MG municipalities

---

## 🌐 Portals Investigated

### 1. TCE-MG Open Data Portal

**URL**: https://dadosabertos.tce.mg.gov.br/
**Type**: Custom Angular application (not CKAN)
**Status**: ❌ SSL Certificate Verification Failed

**Error**:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate
```

**Test Results**:
```
Main page (with SSL bypass):
  ✅ Status 200 - Returns HTML (Angular app)
  ❌ No API endpoints found in HTML
  ❌ No JavaScript bundles with API URLs

Attempted API endpoints:
  /api - 404 Not Found
  /api/3 - 404 Not Found
  /api/3/action - 404 Not Found
  /api/datasets - 404 Not Found
  /api/municipios - 404 Not Found
```

**Portal Structure**:
- Modern Angular single-page application
- Data likely fetched from backend API
- JavaScript files are bundled/minified
- No public API documentation found

**Subdomains Discovered**:
- `grafite.tce.mg.gov.br` - Connection refused
- `arabiasaudita.tce.mg.gov.br:8443` - 404 Not Found
- `argentina.tce.mg.gov.br:8443` - Connection refused
- `bronze.tce.mg.gov.br` - Connection refused

---

### 2. State of Minas Gerais CKAN Portal

**URL**: https://dados.mg.gov.br
**Type**: CKAN-based open data portal (state government, not TCE)
**Status**: ❌ 403 Forbidden

**Test Results**:
```
Main page: 403 Forbidden
API endpoint (/api/3): 403 Forbidden
Package list (/api/3/action/package_list): 403 Forbidden
Organization list: 403 Forbidden
Search: 403 Forbidden
```

**Analysis**:
- State government CKAN portal exists
- All endpoints return 403 Forbidden
- May require:
  - Authentication/API key
  - IP whitelisting
  - User registration
- Not specific to TCE-MG (covers all state government data)

---

### 3. Main TCE-MG Website

**URL**: https://www.tce.mg.gov.br
**Status**: ⚠️ Accessible but no API

**Test Results**:
```
Main website: ✅ 200 OK
News about new portal: ❌ SSL certificate error
Transparency tools: ✅ Accessible via web interface
```

**Available Tools** (web interface only):
- Price comparison tool for public acquisitions
- CAPMG - Payroll consultation for public servants
- IEGM - Municipal Management Effectiveness Index
- Fiscal reports and audits

**Limitations**:
- All tools are web-based interfaces
- No programmatic API access
- Would require web scraping (not recommended)

---

## 🔧 Technical Investigation Details

### SSL Certificate Analysis

**Problem**: TCE-MG uses SSL certificates that cannot be verified

**Tests Performed**:
```bash
# Direct SSL test
curl -v "https://dadosabertos.tce.mg.gov.br"
# Result: SSL certificate problem: unable to get local issuer certificate

# Python with verification
requests.get(url, verify=True)
# Result: [SSL: CERTIFICATE_VERIFY_FAILED]

# Python without verification
requests.get(url, verify=False)
# Result: Works, but NOT SECURE
```

**Root Cause Options**:
1. Self-signed certificate
2. Incomplete certificate chain
3. Certificate issued by internal CA
4. Expired or invalid certificate

**Security Assessment**:
- ❌ Cannot disable SSL verification in production
- ❌ Would expose system to man-in-the-middle attacks
- ❌ Violates security best practices
- ✅ Must wait for TCE-MG to fix SSL configuration

### Portal Architecture Analysis

**Frontend**:
```
Technology: Angular (modern SPA)
Build: Webpack/Angular CLI
Files: Bundled and minified
API calls: Obfuscated in compiled JS
```

**Backend** (inferred):
```
Type: Custom REST API (not CKAN)
Location: Unknown internal endpoint
Authentication: Likely required
Documentation: Not publicly available
```

**No API Discovery**:
- Analyzed HTML source: No API URLs found
- Checked JavaScript bundles: URLs obfuscated
- Tested common patterns: All return 404
- Followed subdomain hints: All inaccessible

---

## 📝 Investigation Methods Used

### 1. Web Search
- Searched for TCE-MG API documentation
- Found portal announcement but no API docs
- Discovered state CKAN portal exists
- No tutorials or usage guides found

### 2. Direct Testing
```python
# Tested endpoints
dadosabertos.tce.mg.gov.br/
  - /api, /api/3, /api/3/action
  - /api/datasets, /api/municipios
  - /api/contratos, /api/licitacoes

dados.mg.gov.br/
  - /api/3/action/package_list
  - /api/3/action/organization_list
  - /api/3/action/package_search

# All returned: 404 or 403
```

### 3. HTML/JS Analysis
- Downloaded main page HTML
- Searched for API endpoints in source
- Analyzed JavaScript file references
- Checked for AJAX calls or fetch URLs
- Result: API endpoints not exposed in frontend

### 4. Subdomain Discovery
- Found subdomain references in HTML
- Tested discovered subdomains
- All returned connection errors or 404

---

## 🚫 Why TCE-MG Cannot Be Used

### Primary Blockers

1. **SSL Certificate Issues** ⛔
   - Cannot verify certificate
   - Disabling verification is security risk
   - Production deployment would be vulnerable
   - No workaround without compromising security

2. **No Public API Endpoints** ⛔
   - Portal is Angular SPA
   - Backend API not documented
   - Common CKAN endpoints return 404
   - Custom API structure unknown

3. **Access Restrictions** ⛔
   - State CKAN portal returns 403
   - May require registration/authentication
   - No public access documentation
   - No clear path to obtain credentials

### Secondary Issues

4. **No Documentation** ⚠️
   - No API usage guides found
   - No developer documentation
   - No examples or tutorials
   - Portal announcement has no technical details

5. **Modern SPA Architecture** ⚠️
   - Angular app makes dynamic API calls
   - Endpoints not visible in static HTML
   - Would require browser automation to discover
   - Frequent changes would break integrations

---

## ✅ Alternative Solutions

### Option 1: SICONFI Federal API (RECOMMENDED)

**Status**: ✅ Already implemented and working
**Coverage**: All 853 Minas Gerais municipalities
**Data Available**:
- RREO - Budget execution reports
- RGF - Fiscal management reports
- DCA - Annual accounts
- Entity information

**Advantages**:
- ✅ No SSL issues (proper certificates)
- ✅ No authentication required
- ✅ Well-documented API
- ✅ Reliable uptime
- ✅ Already integrated in our system

**Client**: `src/services/transparency_apis/federal_apis/siconfi_client.py`

**Example**:
```python
from src.services.transparency_apis.federal_apis import SICONFIClient

async with SICONFIClient() as client:
    # Get all MG municipalities
    entities = await client.get_entities(year=2024, state="MG")
    # Returns: 853 municipalities

    # Get fiscal data for Belo Horizonte
    rreo = await client.get_rreo(
        year=2023,
        period=6,
        entity_code="3106200"  # BH IBGE code
    )
```

### Option 2: Contact TCE-MG for API Access

**Action Required**: Official request to TCE-MG IT department

**Information Needed**:
1. Correct API endpoint URLs
2. Authentication method (API key, OAuth, etc.)
3. SSL certificate fix or CA certificate
4. API documentation and usage limits

**Contact Channels**:
- Website: https://www.tce.mg.gov.br
- Transparência/Dados Abertos department
- IT/Technology department

**Estimated Timeline**: 2-4 weeks (bureaucratic process)

### Option 3: Web Scraping (NOT RECOMMENDED)

**Why Not**:
- ❌ Fragile (breaks on UI changes)
- ❌ Slow (requires browser automation)
- ❌ High maintenance
- ❌ SSL issues still present
- ❌ May violate terms of service
- ❌ Not scalable

**If Necessary**:
- Use Selenium/Playwright for browser automation
- Download CSV/Excel exports from web interface
- Parse downloaded files instead of real-time API
- Schedule periodic batch downloads

---

## 📊 Data Coverage Comparison

### TCE-MG vs SICONFI

| Aspect | TCE-MG Direct | SICONFI Fallback |
|--------|---------------|------------------|
| **Access** | ❌ No API | ✅ Working API |
| **SSL** | ❌ Certificate errors | ✅ Valid certificates |
| **Authentication** | ❌ Unknown | ✅ None required |
| **Documentation** | ❌ None found | ✅ Well documented |
| **Municipalities** | 853 (if working) | ✅ 853 available |
| **Data Types** | Unknown | ✅ RREO, RGF, DCA, MSC |
| **Update Frequency** | Unknown | ✅ Monthly/Quarterly |
| **Reliability** | ❌ Untested | ✅ Proven stable |

**Conclusion**: SICONFI provides equivalent or better coverage without the access issues.

---

## 🎯 Recommendations

### Immediate (Current State)

1. ✅ **Continue using SICONFI** for MG municipality data
   - Already integrated and working
   - Covers all 853 municipalities
   - No changes needed to existing code

2. ✅ **Document TCE-MG as unavailable**
   - Update status documentation
   - Note SSL and access issues
   - Reference SICONFI as fallback

### Short Term (1-2 weeks)

3. **Research TCE-MG contact process**
   - Find correct department for API access
   - Prepare official request letter
   - Gather project credentials and purpose

4. **Monitor TCE-MG portal for changes**
   - Check monthly for SSL certificate fixes
   - Watch for API documentation updates
   - Track any announcements about public access

### Long Term (Future)

5. **Official API Access Request**
   - Only pursue if significant value over SICONFI
   - Prepare justification (author's home state, research project)
   - Be prepared for bureaucratic delay

6. **Alternative: Focus on Other States**
   - 21 other states to potentially integrate
   - Some may have working APIs
   - Better ROI than fighting MG access issues

---

## 💡 Key Insights

### What We Learned

1. **SSL Security Cannot Be Compromised**
   - Production system cannot use `verify=False`
   - No workaround exists without certificate fix
   - This is a TCE-MG infrastructure issue, not ours

2. **Modern SPAs Hide APIs**
   - Angular/React apps don't expose endpoints in HTML
   - API discovery requires different techniques
   - Documentation is critical for integration

3. **Government Portals Are Inconsistent**
   - TCE-SP: Works perfectly
   - TCE-CE: Needed migration but now works
   - TCE-MG: SSL issues and no public API
   - No standard across states

4. **Federal Fallbacks Are Valuable**
   - SICONFI provides universal coverage
   - Compensates for state-level API issues
   - Already integrated = zero additional work

### Author's Note

As a Minas Gerais native, it's disappointing that TCE-MG is the most difficult to integrate despite being the home state. However, **data security and system reliability cannot be compromised** for sentimental reasons. SICONFI provides excellent coverage for all MG municipalities, making TCE-MG integration optional rather than critical.

---

## 📚 Files Created/Updated

1. **`investigate_tce_mg.py`** - Investigation script
2. **`docs/TCE_MG_INVESTIGATION_2025_11_14.md`** - This document

---

## 🏆 Conclusion

**TCE-MG Status**: ❌ Not accessible via public API

**Blockers**:
1. SSL certificate verification failures
2. No discoverable API endpoints
3. State CKAN portal returns 403 Forbidden

**Solution**: ✅ Use SICONFI federal API (already working)

**Coverage**: 100% of 853 MG municipalities via SICONFI

**Recommendation**: Mark TCE-MG as unavailable and rely on SICONFI fallback until TCE-MG resolves infrastructure issues or provides public API access.

---

**Author**: Anderson Henrique da Silva (Minas Gerais native)
**Created**: 2025-11-14
**Status**: Investigation Complete - No Public Access Available
**Fallback**: SICONFI federal API provides full coverage
