# Multi-API Integration - Complete Transparency System

**Author:** Anderson Henrique da Silva
**Location:** Minas Gerais, Brasil
**Date:** 2025-10-16
**Version:** 1.0.0

---

## 📋 Overview

Implementation of a complete multi-source transparency data system for Brazilian government data, with intelligent routing, automatic fallback, and data aggregation from 15+ APIs.

## 🎯 What Was Implemented

### Phase 1: TransparencyOrchestrator
**File:** `src/services/transparency_orchestrator.py`
**Commit:** `8ae5c0d`

Central orchestration system managing all Brazilian transparency APIs with:

- **4 Query Strategies:**
  - `FALLBACK`: Try sources in priority order
  - `AGGREGATE`: Combine results from all sources
  - `FASTEST`: Return first successful response
  - `PARALLEL`: Execute all concurrently

- **Smart Routing:**
  - Auto-detects best sources based on query parameters
  - State-aware routing (TCE priority for state queries)
  - Federal fallback for all queries

- **Data Quality:**
  - Automatic deduplication by ID or content hash
  - Success/error tracking per source
  - Performance metrics and statistics

### Phase 2: DataService Integration
**File:** `src/services/data_service.py`
**Commit:** `a8a6c22`

Added convenience methods for multi-source access:

```python
# Method 1: Full control
await data_service.get_contracts_multi_source(
    filters={"ano": 2024, "estado": "MG"},
    strategy=QueryStrategy.AGGREGATE,
    sources=[DataSource.PORTAL_FEDERAL, DataSource.PNCP]
)

# Method 2: State-specific (auto-routing)
await data_service.get_state_contracts("MG", include_federal=True)

# Method 3: Fastest response
await data_service.search_contracts_fastest({"ano": 2024})

# Method 4: Get performance stats
stats = data_service.get_orchestrator_stats()
```

---

## 🗺️ Available Data Sources

### Federal Level (8 APIs)

| API | Status | Data Types | Implementation |
|-----|--------|-----------|----------------|
| **Portal da Transparência** | ✅ Active | Contracts, Expenses, Agreements | `src/tools/transparency_api.py` |
| **PNCP** | ✅ Integrated | Standardized Contracts | `src/services/transparency_apis/federal_apis/pncp_client.py` |
| **Compras.gov** | ✅ Integrated | Federal Bids | `src/services/transparency_apis/federal_apis/compras_gov_client.py` |
| **BCB** | ✅ Integrated | Economic Indicators | `src/services/transparency_apis/federal_apis/bcb_client.py` |
| **DataSUS** | ✅ Ready | Health Data | `src/services/transparency_apis/federal_apis/datasus_client.py` |
| **IBGE** | ✅ Ready | Statistical Data | `src/services/transparency_apis/federal_apis/ibge_client.py` |
| **INEP** | ✅ Ready | Education Data | `src/services/transparency_apis/federal_apis/inep_client.py` |
| **Minha Receita** | ✅ Ready | CNPJ/CPF Lookup | `src/services/transparency_apis/federal_apis/minha_receita_client.py` |

### State Level (11 sources)

**TCEs (Tribunais de Contas):**
- ✅ BA (Bahia) - `src/services/transparency_apis/tce_apis/tce_ba.py`
- ✅ CE (Ceará) - `src/services/transparency_apis/tce_apis/tce_ce.py`
- ✅ MG (Minas Gerais) - `src/services/transparency_apis/tce_apis/tce_mg.py`
- ✅ PE (Pernambuco) - `src/services/transparency_apis/tce_apis/tce_pe.py`
- ✅ RJ (Rio de Janeiro) - `src/services/transparency_apis/tce_apis/tce_rj.py`
- ✅ SP (São Paulo) - `src/services/transparency_apis/tce_apis/tce_sp.py`

**State Portals:**
- ✅ RO (Rondônia) - Custom portal
- ✅ SP, RJ, RS, SC, BA - CKAN-based open data portals

---

## 🚀 Usage Examples

### Example 1: Simple Query with Fallback
```python
from src.services.data_service import data_service

# Get contracts for 2024 - tries Portal Federal first, PNCP as fallback
result = await data_service.get_contracts_multi_source(
    filters={"ano": 2024}
)

print(f"Found {len(result['data'])} contracts")
print(f"Sources used: {result['sources']}")
print(f"Duration: {result['metadata']['duration_seconds']}s")
```

### Example 2: State Query with Aggregation
```python
# Get all MG contracts from TCE-MG + State Portal + Federal
result = await data_service.get_state_contracts(
    state_code="MG",
    filters={"ano": 2024, "valor_inicial": 100000}
)

# Results automatically deduplicated and aggregated
print(f"Total contracts: {len(result['data'])}")
print(f"From sources: {result['sources']}")
print(f"Before dedup: {result['metadata']['records_before_dedup']}")
print(f"After dedup: {result['metadata']['records_after_dedup']}")
```

### Example 3: Fastest Response
```python
# Get first successful response (race condition)
result = await data_service.search_contracts_fastest(
    filters={"numero_contrato": "12345"}
)

print(f"Fastest source: {result['metadata']['fastest_source']}")
```

### Example 4: Performance Monitoring
```python
# Get orchestrator statistics
stats = data_service.get_orchestrator_stats()

print(f"Total queries: {stats['total_queries']}")
print(f"Source usage: {stats['source_usage']}")
print(f"Success rates: {stats['success_rate_by_source']}")
```

---

## 🏗️ Architecture

### Request Flow
```
User Request
    ↓
DataService.get_contracts_multi_source()
    ↓
TransparencyOrchestrator.get_contracts()
    ↓
Source Selection (intelligent routing)
    ↓
Strategy Execution (FALLBACK/AGGREGATE/FASTEST/PARALLEL)
    ↓
[Portal Federal] [PNCP] [TCE-MG] [Compras.gov] ...
    ↓
Data Deduplication
    ↓
Response with Metadata
```

### Source Selection Logic

**For State Queries:**
1. State TCE (if available) → Priority
2. State Portal (if available)
3. Federal Portal with state filter → Fallback

**For Federal Queries:**
1. Portal da Transparência → Primary
2. PNCP → Standardized contracts
3. Compras.gov → Bids/tenders

**Auto-Detection:**
- If `filters["estado"]` or `filters["uf"]` exists → State sources first
- If no state specified → Federal sources only
- Always includes federal as ultimate fallback

---

## 📊 Data Deduplication

Records are deduplicated using this priority:

1. **ID fields:** `id`, `numero_contrato`, `numeroContrato`
2. **Compound keys:** `codigoOrgao-ano-numero`
3. **Content hash:** MD5 of sorted JSON (fallback)

```python
# Example: Same contract from 3 sources
TCE-MG: {"id": "123", "valor": 50000, "fornecedor": "ABC"}
Federal: {"numero_contrato": "123", "valor": 50000, "fornecedor": "ABC LTDA"}
PNCP: {"id": "123", "valorTotal": 50000, "contratado": "ABC"}

# After deduplication: 1 record (ID "123")
```

---

## 🎯 Performance & Monitoring

### Built-in Metrics

```python
stats = data_service.get_orchestrator_stats()

{
    "total_queries": 150,
    "source_usage": {
        "portal_federal": 120,
        "pncp": 45,
        "tce": 30,
        "compras_gov": 15
    },
    "error_count": {
        "portal_federal": 5,
        "tce": 2
    },
    "success_rate_by_source": {
        "portal_federal": 0.96,  # 96% success
        "pncp": 1.0,             # 100% success
        "tce": 0.93              # 93% success
    }
}
```

### Query Metadata

Every response includes:
```python
{
    "data": [...],
    "sources": ["portal_federal", "pncp"],
    "metadata": {
        "query_id": "query_150",
        "timestamp": "2025-10-16T16:30:00",
        "strategy": "FALLBACK",
        "sources_attempted": 2,
        "duration_seconds": 1.234,
        "primary_source": "portal_federal",
        "fallback_used": false
    }
}
```

---

## 🔧 Configuration

### Strategy Selection Guide

| Strategy | Use Case | Latency | Coverage | Cost |
|----------|----------|---------|----------|------|
| **FALLBACK** | Default queries | Low | Medium | Low |
| **AGGREGATE** | Comprehensive search | High | Full | High |
| **FASTEST** | Quick lookups | Minimal | Low | Medium |
| **PARALLEL** | Time-critical + full coverage | Medium | Full | High |

### Recommended Patterns

```python
# Pattern 1: User searches (fallback)
await data_service.get_contracts_multi_source(
    filters=user_filters,
    strategy=QueryStrategy.FALLBACK
)

# Pattern 2: Analytics/reports (aggregate)
await data_service.get_contracts_multi_source(
    filters=report_filters,
    strategy=QueryStrategy.AGGREGATE
)

# Pattern 3: Autocomplete/quick checks (fastest)
await data_service.search_contracts_fastest(
    filters={"numero_contrato": partial_id}
)

# Pattern 4: Dashboard/real-time (parallel)
await data_service.get_contracts_multi_source(
    filters=dashboard_filters,
    strategy=QueryStrategy.PARALLEL
)
```

---

## 🚦 Error Handling

### Graceful Degradation

All strategies handle failures gracefully:

```python
# Scenario: TCE-MG is down
result = await data_service.get_state_contracts("MG")

# Orchestrator automatically:
1. Tries TCE-MG → fails (logged as warning)
2. Falls back to State Portal → success
3. Also queries Federal with MG filter → success
4. Returns aggregated results from 2 sources
5. Logs error for TCE-MG but doesn't fail request
```

### Error Tracking

```python
# Check error rates
stats = data_service.get_orchestrator_stats()

if stats["error_count"]["tce"] > 10:
    logger.warning("TCE experiencing high error rate")
    # Maybe disable TCE temporarily or alert ops
```

---

## 📈 Future Enhancements

### Planned Features

1. **Smart Caching Layer**
   - Cache results per source
   - TTL based on data freshness
   - Warm cache for popular queries

2. **Circuit Breaker Pattern**
   - Temporarily disable failing sources
   - Auto-recovery after cooldown
   - Health checks before queries

3. **Query Cost Optimization**
   - Track API costs per source
   - Select cheapest sources first
   - Budget-aware query planning

4. **ML-based Source Selection**
   - Learn best sources per query type
   - Predict optimal strategy
   - Adaptive routing based on history

---

## 📝 Migration Guide

### For Existing Code

**Before (single source):**
```python
result = await data_service.fetch_contracts({"ano": 2024})
# Only queries Portal Federal
```

**After (multi-source):**
```python
result = await data_service.get_contracts_multi_source({"ano": 2024})
# Tries Portal Federal → PNCP → Compras.gov with fallback
```

### Backward Compatibility

All existing methods still work:
- `fetch_contracts()` → Portal Federal only
- `fetch_expenses()` → Portal Federal only
- `fetch_agreements()` → Portal Federal only

New methods are additive - no breaking changes!

---

## 🎓 Best Practices

### DO ✅

```python
# Use fallback for user requests
await data_service.get_contracts_multi_source(
    filters=filters,
    strategy=QueryStrategy.FALLBACK
)

# Use aggregate for comprehensive reports
await data_service.get_contracts_multi_source(
    filters=filters,
    strategy=QueryStrategy.AGGREGATE
)

# Monitor performance
stats = data_service.get_orchestrator_stats()
logger.info(f"API stats: {stats}")

# Check metadata
result = await data_service.get_contracts_multi_source(filters)
logger.info(f"Used sources: {result['sources']}")
```

### DON'T ❌

```python
# Don't use AGGREGATE for everything (expensive!)
# Only when you need comprehensive coverage

# Don't ignore errors completely
# Always log them for monitoring

# Don't hardcode sources
# Let orchestrator auto-select based on query

# Don't bypass orchestrator
# Use it even for single-source to get metrics
```

---

## 🏆 Benefits

### Before Multi-API Integration
- ❌ Single source (Portal Federal only)
- ❌ No fallback if API is down
- ❌ Limited coverage (federal only)
- ❌ No performance metrics
- ❌ Manual source switching

### After Multi-API Integration
- ✅ 15+ data sources available
- ✅ Automatic fallback on failures
- ✅ Full national coverage (federal + 6 states)
- ✅ Comprehensive metrics and monitoring
- ✅ Intelligent auto-routing
- ✅ 4 query strategies for different use cases
- ✅ Automatic data deduplication
- ✅ Production-ready error handling

---

## 🔗 Related Documentation

- [TransparencyAPI Documentation](../src/tools/transparency_api.py)
- [Federal APIs Guide](../src/services/transparency_apis/federal_apis/)
- [TCE APIs Guide](../src/services/transparency_apis/tce_apis/)
- [State APIs Guide](../src/services/transparency_apis/state_apis/)

---

## 📞 Support

**Author:** Anderson Henrique da Silva
**Email:** andersonhs27@gmail.com
**Location:** Minas Gerais, Brasil

For issues or questions about this integration, please refer to project documentation or contact the author.

---

**Last Updated:** 2025-10-16 16:45:00 -03:00
**Version:** 1.0.0 - Initial Release
