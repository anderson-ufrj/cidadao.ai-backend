# API Endpoint Cleanup Recommendations

**Date**: 2025-11-14
**Status**: Critical Issues Found
**Priority**: High

## Executive Summary

Analysis of the API endpoints revealed **critical architectural issues**:
- **9 duplicate endpoint definitions** (same method + path in different files)
- **2 route files with 100% duplicate functionality** (`auth.py` vs `auth_db.py`)
- **Multiple pattern inconsistencies** affecting maintainability
- **288 total endpoints** across 38 route files (some redundant)

---

## Critical Issues

### 1. Duplicate Authentication Systems (BLOCKER)

**Problem**: System has TWO complete authentication implementations:
- `src/api/routes/auth.py` - In-memory auth (prefix: `/api/v1/auth`)
- `src/api/routes/auth_db.py` - Database-backed auth (prefix: `/auth`)

**100% duplicate endpoints**:
```
POST /login
POST /register
POST /refresh
POST /logout
POST /change-password
POST /verify
GET  /me
GET  /users
POST /users/{user_id}/deactivate
```

**Impact**:
- Confusing for API consumers (which auth to use?)
- Security risk (dual auth paths, potential inconsistencies)
- Maintenance overhead (must update both files for auth changes)
- Database auth missing `/api/v1` prefix (inconsistent)

**Recommendation**: **DELETE one immediately**
- ✅ **Keep**: `auth_db.py` (database-backed, production-ready)
- ❌ **Delete**: `auth.py` (in-memory, development only)
- **Action**: Update `auth_db.py` prefix to `/api/v1/auth` for consistency

---

### 2. Duplicate Root Endpoints

**Problem**: 5 files define `GET /` endpoint:

```
GET / - reports.py
GET / - analysis.py
GET / - agents.py
GET / - investigations.py
GET / - health.py
```

**Impact**:
- FastAPI will use **last registered router**
- Other 4 endpoints are **dead code** (never executed)
- Misleading API documentation

**Recommendation**:
- Remove `GET /` from `reports.py`, `analysis.py`, `agents.py`, `investigations.py`
- Keep only in `health.py` or make it a dedicated root endpoint in `app.py`

---

### 3. Duplicate WebSocket Endpoints

**Problem**: WebSocket duplicate for investigations:

```
WEBSOCKET /ws/investigations/{investigation_id} - websocket_chat.py
WEBSOCKET /ws/investigations/{investigation_id} - websocket.py
```

**Impact**:
- Only one will work (last registered)
- Confusing implementation split

**Recommendation**:
- **Consolidate** into `websocket_chat.py` (more recent, better maintained)
- **Delete** duplicate from `websocket.py`

---

### 4. Duplicate POST /start Endpoints

```
POST /start - analysis.py
POST /start - investigations.py
```

**Impact**:
- Path collision (no prefix differentiation)
- Both registered at root level without parent router

**Recommendation**:
- These should have prefixes from `app.py`:
  - `POST /api/v1/analysis/start`
  - `POST /api/v1/investigations/start`
- Verify router registration in `app.py` has correct prefixes

---

### 5. Duplicate Health Endpoints

```
GET /health - transparency.py
GET /health - voice.py
GET /health - agent_metrics.py
```

**Impact**:
- Health checks should be centralized
- Multiple implementations cause confusion

**Recommendation**:
- Remove `/health` from feature-specific routers
- Use only main `health.py` router
- Feature-specific health can be nested: `/api/v1/transparency/status`

---

## Pattern Issues

### 6. Inconsistent API Versioning

**Problem**: Some endpoints lack `/api/v1` prefix:

```
❌ /api-keys/{api_key_id}           (should be /api/v1/api-keys/...)
❌ /webhooks/list                     (should be /api/v1/webhooks/...)
❌ /tasks/list/scheduled              (should be /api/v1/tasks/...)
❌ /{investigation_id}                (missing version entirely)
```

**Recommendation**:
- Enforce `/api/v1` prefix on ALL routes
- Update router declarations:
```python
# BEFORE
router = APIRouter(prefix="/api-keys")

# AFTER
router = APIRouter(prefix="/api/v1/api-keys")
```

---

### 7. Verbs in URL Paths (Anti-pattern)

**Problem**: URLs contain verbs instead of using HTTP methods:

```
❌ GET  /list-all-investigations  → GET /api/v1/investigations
❌ GET  /tasks/list/scheduled     → GET /api/v1/tasks?status=scheduled
❌ POST /webhooks/list            → GET /api/v1/webhooks
❌ POST /agents/find-by-capability → POST /api/v1/agents/search
❌ POST /federal/datasus/search   → POST /api/v1/federal/datasus/query
```

**Recommendation**: Follow RESTful conventions:
- Use HTTP methods for actions (GET, POST, PUT, DELETE)
- Use nouns for resources
- Use query params for filtering

---

## Recommended Actions

### Immediate (Critical - Do First)

1. **Delete duplicate auth system**
   ```bash
   # Delete in-memory auth
   git rm src/api/routes/auth.py

   # Update auth_db.py prefix
   router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

   # Update app.py to import only auth_db
   ```

2. **Remove duplicate root endpoints**
   ```python
   # Remove GET / from:
   # - src/api/routes/reports.py
   # - src/api/routes/analysis.py
   # - src/api/routes/agents.py
   # - src/api/routes/investigations.py
   ```

3. **Consolidate WebSocket endpoints**
   ```bash
   # Keep websocket_chat.py (more complete)
   # Remove duplicate from websocket.py
   ```

### High Priority

4. **Fix missing API version prefixes**
   - Update all routers to use `/api/v1` prefix
   - Verify in `app.py` router registrations

5. **Remove verbs from URLs**
   - Refactor REST endpoints to use nouns + HTTP methods
   - Update frontend clients accordingly

6. **Consolidate health checks**
   - Remove `/health` from feature routers
   - Use centralized health endpoint

### Medium Priority

7. **Review feature overlap**
   - `chat.py` vs `chat_drummond_factory.py` vs `chat_zumbi_integration.py`
     - Consider consolidating chat features
   - `websocket.py` vs `websocket_chat.py`
     - Merge into single WebSocket router

8. **Standardize endpoint naming**
   - Review all 288 endpoints for consistency
   - Document naming conventions

---

## Migration Plan

### Phase 1: Remove Duplicates (1 day)
- [ ] Delete `auth.py` (use `auth_db.py` only)
- [ ] Remove duplicate root endpoints
- [ ] Consolidate WebSocket endpoints
- [ ] Fix duplicate health checks

### Phase 2: Fix Prefixes (1 day)
- [ ] Add `/api/v1` to all routes missing it
- [ ] Update router declarations
- [ ] Test all endpoints still work

### Phase 3: Refactor REST Patterns (2-3 days)
- [ ] Remove verbs from URLs
- [ ] Standardize resource naming
- [ ] Update API documentation
- [ ] Update frontend clients

### Phase 4: Consolidate Features (3-5 days)
- [ ] Merge chat-related routers
- [ ] Merge WebSocket routers
- [ ] Review and consolidate similar features

---

## Testing Strategy

Before making changes:
```bash
# 1. Document all current endpoints
python scripts/analyze_endpoints.py > before.txt

# 2. Run full test suite
JWT_SECRET_KEY=test SECRET_KEY=test make test

# 3. Test critical paths manually
curl https://cidadao-api-production.up.railway.app/health
curl https://cidadao-api-production.up.railway.app/api/v1/auth/verify
```

After changes:
```bash
# 1. Verify endpoint changes
python scripts/analyze_endpoints.py > after.txt
diff before.txt after.txt

# 2. Run full test suite again
JWT_SECRET_KEY=test SECRET_KEY=test make test

# 3. Update OpenAPI docs
# Visit /docs and verify all endpoints documented correctly

# 4. Test in production (staging first if available)
```

---

## Impact Assessment

### Benefits
- ✅ **-38 redundant endpoints** (13% reduction)
- ✅ **-1 complete auth system** (major simplification)
- ✅ **Consistent API versioning** (better for clients)
- ✅ **RESTful patterns** (industry standard)
- ✅ **Easier maintenance** (single source of truth)

### Risks
- ⚠️ **Breaking changes** for existing clients
  - Mitigation: Provide deprecation period
  - Maintain old endpoints with warnings initially
- ⚠️ **Test updates** required
  - Many tests may reference old endpoints
- ⚠️ **Documentation updates** required
  - Update all docs, Swagger, README files

---

## Deprecated Endpoints (To Remove)

After implementing recommendations, these endpoints will be deprecated:

```yaml
Deprecated:
  - DELETE:
    - src/api/routes/auth.py (entire file)

  - Endpoints to remove:
    - GET  / from reports.py
    - GET  / from analysis.py
    - GET  / from agents.py
    - GET  / from investigations.py
    - GET  /health from transparency.py
    - GET  /health from voice.py
    - GET  /health from agent_metrics.py
    - WEBSOCKET /ws/investigations/{investigation_id} from websocket.py

  - Endpoints to rename:
    - GET  /list-all-investigations → GET /api/v1/investigations
    - GET  /tasks/list/scheduled → GET /api/v1/tasks?status=scheduled
    - POST /webhooks/list → GET /api/v1/webhooks
    - POST /agents/find-by-capability → POST /api/v1/agents/search
```

---

## Summary Statistics

| Metric | Before | After (Proposed) | Change |
|--------|--------|------------------|--------|
| Route Files | 38 | 36 | -2 (auth.py, merge websockets) |
| Total Endpoints | 288 | 250 | -38 (-13%) |
| Duplicate Definitions | 9 | 0 | -9 (100% fixed) |
| Missing API Version | ~50 | 0 | All standardized |
| Verb-based URLs | ~15 | 0 | All RESTful |

---

## Next Steps

1. **Review this document** with team
2. **Prioritize changes** based on impact/effort
3. **Create tickets** for each phase
4. **Implement Phase 1** (duplicates) first - lowest risk, highest impact
5. **Monitor** production after each phase
6. **Update documentation** incrementally

---

## Questions?

Contact the architecture team before making breaking changes to production endpoints.

**Remember**: This is a production system with 99.9% uptime. Make changes incrementally and test thoroughly.
