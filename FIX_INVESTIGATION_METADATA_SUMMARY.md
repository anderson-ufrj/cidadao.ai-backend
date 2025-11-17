# InvestigationResult Metadata Fix - Summary

**Date**: November 17, 2025
**Issue**: 500 Internal Server Error - 'InvestigationResult' object has no attribute 'metadata'
**Status**: ✅ **FIXED - READY FOR DEPLOYMENT**

---

## Problem Identified

From Railway production logs (after Portal API and AgentMessage fixes):
```
WARNI "Anomaly detection failed for e04c34ab-3f66-46ef-8f2f-6dfb9a0f4472:
'InvestigationResult' object has no attribute 'metadata'"
```

**Context**: This error occurred AFTER:
- ✅ Portal API successfully fetched 15 contracts
- ✅ AgentMessage validation passed (sender/recipient added)
- ✅ Intent classification working
- ✅ Entity extraction working

**Impact**: Investigation completed processing but failed during anomaly result storage, causing:
- 500 error returned to user
- Investigations not saved to database
- User sees "Erro ao processar mensagem" instead of results

---

## Root Cause Analysis

### The Confusion: Two Different InvestigationResult Classes

**Class 1**: `src/agents/abaporu.py` (lines 70-89)
```python
class InvestigationResult(BaseModel):
    """Result of an investigation."""
    investigation_id: str
    query: str
    findings: list[dict[str, Any]]
    confidence_score: float
    sources: list[str]
    explanation: Optional[str]
    metadata: dict[str, Any] = PydanticField(default_factory=dict)  # ✅ HAS metadata
    timestamp: datetime
    processing_time_ms: Optional[float]
```

**Class 2**: `src/services/orchestration/models/investigation.py` (lines 92-138)
```python
class InvestigationResult(BaseModel):
    """Complete investigation result."""
    investigation_id: str
    intent: InvestigationIntent
    context: InvestigationContext  # context.metadata exists
    plan: ExecutionPlan
    stage_results: list[StageResult]
    entities_found: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    anomalies: list[dict[str, Any]]  # ✅ Anomalies go HERE
    # NO metadata attribute at top level!
```

**The Issue**: `orchestrator.py` uses the orchestration version (Class 2), but the code at line 146 tried to access `result.metadata` which doesn't exist!

---

## Solution Applied

### Surgical Fix: Use Correct Attributes

**File**: `src/services/orchestration/orchestrator.py`
**Lines**: 143-156

**Before (WRONG - tries to use non-existent metadata):**
```python
# Add anomaly results to investigation
if anomaly_results and "result" in anomaly_results:
    anomaly_data = anomaly_results["result"]
    result.metadata["anomaly_detection"] = {  # ❌ metadata doesn't exist!
        "status": anomaly_results.get("status"),
        "anomalies_found": anomaly_data.get("anomalies", []),
        "summary": anomaly_data.get("summary", {}),
    }
    self.logger.info(
        f"Anomaly detection completed: "
        f"{len(anomaly_data.get('anomalies', []))} anomalies found"
    )
```

**After (CORRECT - uses proper attributes):**
```python
# Add anomaly results to investigation
if anomaly_results and "result" in anomaly_results:
    anomaly_data = anomaly_results["result"]
    # Store anomalies directly in the anomalies field (not metadata)
    result.anomalies = anomaly_data.get("anomalies", [])
    # Add summary to context metadata
    result.context.metadata["anomaly_detection"] = {
        "status": anomaly_results.get("status"),
        "summary": anomaly_data.get("summary", {}),
    }
    self.logger.info(
        f"Anomaly detection completed: "
        f"{len(result.anomalies)} anomalies found"
    )
```

**Key Changes**:
1. ✅ Store anomalies in `result.anomalies` (correct field that exists)
2. ✅ Store summary in `result.context.metadata` (context has metadata)
3. ✅ Update log to use `len(result.anomalies)` instead of dict access

---

## Why This Fix Works

The `InvestigationResult` class in orchestration has:
- `anomalies: list[dict[str, Any]]` ← Direct field for anomaly data
- `context: InvestigationContext` ← Context has metadata dict

So we should:
- Put anomaly objects directly in `result.anomalies`
- Put metadata (status, summary) in `result.context.metadata`

This matches the data model design!

---

## Complete Fix Chain (All 3 Fixes)

### Fix 1: Portal API (Deployed ✅)
**Problem**: Missing `codigoOrgao` parameter causing 400 Bad Request
**Solution**: Added default orgao=36000 in `portal_transparencia_service.py`
**Result**: Successfully fetching 15 contracts from Portal da Transparência

### Fix 2: AgentMessage (Deployed ✅)
**Problem**: Missing `sender` and `recipient` in AgentMessage causing validation error
**Solution**: Added sender="orchestrator" and recipient="investigator_agent" in `agent_adapter.py`
**Result**: AgentMessage validation passing

### Fix 3: InvestigationResult Metadata (THIS FIX - Ready for Deploy)
**Problem**: Trying to access non-existent `result.metadata` attribute
**Solution**: Use `result.anomalies` for anomaly data and `result.context.metadata` for summary
**Result**: Investigation can complete successfully and save to database

---

## Expected Behavior After Fix

### Complete Investigation Flow (End-to-End)

```bash
User Query: "Contratos de saúde em MG acima de 1 milhão em 2024"
    ↓
1. Intent Classification ✅
   → CONTRACT_ANOMALY_DETECTION (0.90 confidence)
    ↓
2. Entity Extraction ✅
   → {estado: 'MG', codigo_uf: '31', ano: 2024, valor: 1000000.0, categoria: 'saúde'}
    ↓
3. Query Planning ✅
   → 3-stage execution plan (contract_collection → economic_context → anomaly_analysis)
    ↓
4. Data Federation ✅
   → Portal API: Fetched 15 contracts (orgao=36000) ✅
   → PNCP: Failed (signature mismatch - separate issue)
   → Compras.gov: Failed (signature mismatch - separate issue)
    ↓
5. Entity Graph ✅
   → Extracted entities and relationships
    ↓
6. Anomaly Detection ✅ (NOW FULLY FIXED!)
   → AgentMessage created with sender/recipient ✅
   → InvestigatorAgent analyzes contracts ✅
   → Anomalies stored in result.anomalies ✅
   → Summary stored in result.context.metadata ✅
    ↓
7. Database Save ✅ (NOW WORKS!)
   → Investigation saved to PostgreSQL
   → Status: "completed"
   → Anomalies: [list of detected anomalies]
    ↓
8. Response ✅
   → Investigation completed with full results
   → 200 OK (not 500!)
   → Real contract data returned to user
```

### Before All Fixes
```
Status: 400 Bad Request → Portal API
Error: Missing codigoOrgao parameter
Result: No data fetched
```

### After Portal Fix Only
```
Status: 500 Internal Server Error → AgentMessage validation
Error: sender/recipient fields required
Result: Data fetched but not analyzed
```

### After Portal + AgentMessage Fixes
```
Status: 500 Internal Server Error → InvestigationResult metadata
Error: 'metadata' attribute doesn't exist
Result: Analysis completed but not saved
```

### After All Three Fixes (Expected)
```
Status: 200 OK
Result: Complete investigation with:
  - 15 contracts from Portal da Transparência
  - Anomaly detection results in result.anomalies
  - Summary in result.context.metadata
  - Investigation saved to database
  - User receives real transparency data!
```

---

## Testing Verification

### Production Test Command
```bash
curl -X POST 'https://cidadao-api-production.up.railway.app/api/v1/chat/message' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Contratos de saúde em MG acima de 1 milhão em 2024",
    "session_id": "test-final-verification",
    "user_id": "test"
  }'
```

### Expected Response (After Fix)
```json
{
  "status": "success",
  "data": {
    "investigation_id": "...",
    "contracts_found": 15,
    "anomalies": [
      {
        "type": "price_anomaly",
        "severity": "high",
        "details": {...}
      }
    ],
    "summary": {
      "total_value": "R$ X.XXX.XXX,XX",
      "suspicious_patterns": X
    }
  }
}
```

### Logs to Monitor
```
✅ "Using default orgao=36000 (Ministério da Saúde) for Portal API"
✅ "Fetched 15 contracts from Portal da Transparência"
✅ "Running anomaly detection for investigation ..."
✅ "Anomaly detection completed: X anomalies found"  ← NEW LOG!
✅ "Investigation ... completed in X.XXs"
✅ "Investigation saved to database"  ← CRITICAL!
```

### Database Verification
After successful investigation, database should show:
```sql
SELECT investigation_id, status, total_contracts_analyzed, anomalies_detected
FROM investigations
ORDER BY created_at DESC
LIMIT 1;
```

Expected result:
```
investigation_id: e04c34ab-... (or new ID)
status: completed
total_contracts_analyzed: 15
anomalies_detected: X (actual count)
```

---

## Files Changed

**Modified**:
- `src/services/orchestration/orchestrator.py` (Lines 143-156)
  - Changed: `result.metadata["anomaly_detection"]` → `result.anomalies` + `result.context.metadata["anomaly_detection"]`
  - Reason: InvestigationResult doesn't have top-level metadata attribute
  - Impact: Anomalies now stored in correct field, investigation can complete

**No other changes needed** - This was a surgical, targeted fix!

---

## Architecture Notes

### Data Model Structure (Important for Future Reference)

**Abaporu's InvestigationResult** (`src/agents/abaporu.py`):
- Used by: Master agent for multi-agent orchestration
- Has: `metadata` dict at top level
- Purpose: General-purpose investigation results

**Orchestration InvestigationResult** (`src/services/orchestration/models/investigation.py`):
- Used by: Investigation orchestrator for API data federation
- Has: `anomalies` list + `context.metadata` dict
- Purpose: Structured results from multi-API investigations
- **This is what orchestrator.py uses!**

**Lesson**: Always check which InvestigationResult class is imported before accessing attributes!

---

## Commit Message

```
fix(orchestration): store anomalies in correct InvestigationResult field

Critical fix for InvestigationResult attribute error during anomaly storage.
The orchestration InvestigationResult model doesn't have a top-level metadata
attribute, but has dedicated fields for anomalies and context.metadata.

Root cause:
- Code tried to access result.metadata["anomaly_detection"]
- InvestigationResult (orchestration) has no metadata attribute
- It has result.anomalies (list) and result.context.metadata (dict)

Changes:
- Store anomaly data in result.anomalies (correct field)
- Store summary in result.context.metadata["anomaly_detection"]
- Update log to use len(result.anomalies) instead of dict access

Impact:
- Investigations can now complete successfully
- Anomaly data is properly stored in database
- Users receive 200 OK with real transparency analysis
- Fixes "InvestigationResult object has no attribute 'metadata'" error

This completes the investigation flow end-to-end:
1. Portal API fetching contracts (Fix 1 ✅)
2. AgentMessage validation (Fix 2 ✅)
3. Anomaly storage and completion (Fix 3 ✅ - THIS FIX)
```

---

## Summary

**Problema**: Tentativa de acessar atributo `metadata` inexistente em InvestigationResult
**Solução**: Usar `result.anomalies` para dados de anomalia e `result.context.metadata` para resumo
**Resultado**: Sistema de investigação completo funcionando de ponta a ponta com salvamento no banco

**Status**: ✅ Fix implementado e pronto para deploy

**Next Steps**:
1. ✅ Portal API working (15 contracts fetched)
2. ✅ AgentMessage validation fixed
3. ✅ InvestigationResult anomaly storage fixed
4. ⏳ Deploy to Railway and monitor
5. ⏳ Verify investigations being saved to database
6. ⏳ Confirm users receive real contract data
7. 🔜 Optional: Fix PNCP and Compras.gov signatures (low priority)
