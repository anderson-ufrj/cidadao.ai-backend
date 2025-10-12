# API Versioning Strategy - Cidadão.AI

## 📋 Versioning Overview

The Cidadão.AI API uses **URL-based versioning** for maximum clarity and backward compatibility.

### Current Version
- **Version**: v1.0.0
- **Base URL**: `/api/v1/`
- **Status**: Production
- **Deprecated**: No
- **Sunset Date**: N/A

---

## 🎯 Versioning Philosophy

### 1. URL-Based Versioning
We use the URL path to specify API versions:
```
/api/v1/investigations  → Version 1
/api/v2/investigations  → Version 2 (future)
```

### 2. Semantic Versioning
We follow semantic versioning for the API:
- **Major** (v1 → v2): Breaking changes, incompatible API changes
- **Minor** (v1.0 → v1.1): Backward-compatible functionality additions
- **Patch** (v1.0.0 → v1.0.1): Backward-compatible bug fixes

### 3. Backward Compatibility
- Old versions remain accessible for minimum 12 months after new version release
- Deprecation notices provided 6 months in advance
- Clear migration guides for major version changes

---

## 📁 Directory Structure for v2

When implementing v2, follow this structure:

```
src/api/
├── v1/                        # Current version
│   ├── routes/
│   │   ├── investigations.py
│   │   ├── analysis.py
│   │   └── ...
│   └── models/
│       └── ...
├── v2/                        # Future version
│   ├── routes/
│   │   ├── investigations.py  # New implementation
│   │   ├── analysis.py
│   │   └── ...
│   └── models/
│       └── ...
└── app.py                     # Main app with both versions
```

---

## 🔄 Migration Strategy (v1 → v2)

### What Stays in v1
- All current endpoints remain functional
- Bug fixes and security patches continue
- No new features added after v2 release

### What Changes in v2
#### Planned Improvements:
1. **Enhanced Agent Response Format**
   - Structured JSON instead of markdown
   - Confidence scores for all analyses
   - Provenance tracking for data sources

2. **GraphQL as Primary Interface**
   - REST endpoints remain for backward compatibility
   - GraphQL provides more flexible querying

3. **Improved Authentication**
   - API key rotation policies
   - Fine-grained permission system
   - OAuth2 scopes for granular access

4. **Real-time Features**
   - WebSocket connections for live updates
   - Server-Sent Events for streaming
   - Webhooks for event notifications

5. **Enhanced Caching**
   - Edge caching support
   - ETag-based conditional requests
   - Stale-while-revalidate patterns

---

## 🚀 Implementation Checklist for v2

### Phase 1: Planning (1 month)
- [ ] Define breaking changes
- [ ] Create migration guide
- [ ] Design new API contracts
- [ ] Update OpenAPI specs

### Phase 2: Development (3 months)
- [ ] Create `/api/v2/` namespace
- [ ] Implement new endpoints
- [ ] Add deprecation warnings to v1
- [ ] Write comprehensive tests

### Phase 3: Beta Testing (1 month)
- [ ] Deploy v2 beta to staging
- [ ] Invite select users to test
- [ ] Collect feedback
- [ ] Fix issues

### Phase 4: Production Release (1 week)
- [ ] Deploy v2 to production
- [ ] Update documentation
- [ ] Announce to all users
- [ ] Monitor adoption

### Phase 5: Sunset v1 (12 months)
- [ ] 6 months: Add deprecation notices
- [ ] 9 months: Email all v1 users
- [ ] 12 months: Disable v1 endpoints

---

## 📊 Version Lifecycle

```
v1.0 ─────────┬─────────────────────────────┬─────────> Sunset
              │                             │
              └──> v2.0 Beta                │
                   │                        │
                   └──> v2.0 Production ────┘
                        │
                        └──> v3.0 (future)
```

### Lifecycle States:
1. **Active Development**: New features added regularly
2. **Maintenance**: Only bug fixes and security patches
3. **Deprecated**: Still functional, but users encouraged to migrate
4. **Sunset**: Endpoints return 410 Gone status

---

## 🔐 Versioning Headers

### Request Headers:
```http
# Specify API version (optional, defaults to v1)
Accept: application/vnd.cidadao.v2+json

# For backward compatibility
X-API-Version: 2
```

### Response Headers:
```http
# Current version used
X-API-Version: 1.0.0

# Deprecation warning (when applicable)
Deprecation: true
Sunset: Fri, 11 Nov 2026 11:11:11 GMT
Link: <https://docs.cidadao.ai/migration/v2>; rel="deprecation"
```

---

## 📚 Documentation Strategy

### Separate Documentation per Version:
- `/docs` → Latest version (v1 currently)
- `/docs/v1` → Version 1 specific
- `/docs/v2` → Version 2 specific (when released)

### Migration Guides:
- `/docs/migration/v1-to-v2` → Step-by-step migration
- `/docs/changelog/v2` → All changes from v1

---

## 🎯 Success Metrics

Track these metrics for successful versioning:

1. **Adoption Rate**: % of requests using new version
2. **Migration Time**: Average time users take to migrate
3. **Error Rate**: Compare error rates between versions
4. **Performance**: Response times for each version
5. **Support Tickets**: Version-specific issues

---

## 🚨 Emergency Rollback Plan

If critical issues found in new version:

1. **Immediate**: Add warning to v2 docs
2. **1 hour**: Investigate root cause
3. **4 hours**: Deploy hotfix or rollback
4. **24 hours**: Communicate to all users
5. **1 week**: Post-mortem and action items

---

## 📝 Notes

- This is a living document - update as strategy evolves
- Review quarterly for alignment with product roadmap
- Gather user feedback before making breaking changes
- Always prioritize backward compatibility when possible

---

*Last Updated: 2025-10-09*
*Next Review: 2026-01-09*
