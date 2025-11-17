# Fixes and Postmortems

This directory contains detailed documentation of critical fixes, bug investigations, and postmortem analyses.

## Purpose

- **Document critical fixes** with technical details
- **Preserve investigation process** for learning
- **Share solutions** with team and community
- **Track system evolution** over time

## Directory Structure

```
fixes/
├── README.md          # This file
└── 2025-11/          # November 2025 fixes
    ├── portal-api-fix.md
    ├── agent-message-fix.md
    ├── investigation-metadata-fix.md
    └── complete-fix-summary.md
```

## November 2025 Fixes

### Portal da Transparência API Fix
**File**: `2025-11/portal-api-fix.md`
**Date**: November 17, 2025
**Issue**: 400 Bad Request errors on all Portal API calls
**Solution**: Added required `codigoOrgao` parameter with default value

**Impact**:
- ✅ Portal API returning real data (15 contracts)
- ✅ Default to Ministério da Saúde (orgao=36000)
- ✅ No more 400 Bad Request errors

### AgentMessage Validation Fix
**File**: `2025-11/agent-message-fix.md`
**Date**: November 17, 2025
**Issue**: Validation errors - missing `sender` and `recipient` fields
**Solution**: Added required fields to AgentMessage creation

**Impact**:
- ✅ AgentMessage validation passing
- ✅ Investigation agent can process requests
- ✅ Anomaly detection working

### InvestigationResult Metadata Fix
**File**: `2025-11/investigation-metadata-fix.md`
**Date**: November 17, 2025
**Issue**: Attribute error - 'InvestigationResult' has no 'metadata'
**Solution**: Use correct attributes (result.anomalies + context.metadata)

**Impact**:
- ✅ Investigations completing successfully
- ✅ Anomalies properly stored in database
- ✅ Users receive 200 OK with real data

### Complete Fix Summary
**File**: `2025-11/complete-fix-summary.md`
**Date**: November 17, 2025
**Overview**: Comprehensive summary of all 3 fixes in the investigation system

**Key Achievement**: Complete end-to-end investigation flow now operational!

## Fix Document Template

When documenting a new fix, include:

### 1. Summary Section
- **Date**: When the fix was implemented
- **Issue**: Brief description of the problem
- **Status**: Current status (Fixed, Deployed, Monitoring, etc.)

### 2. Problem Identification
- Error messages from logs
- Impact on users/system
- How the issue was discovered

### 3. Root Cause Analysis
- Technical explanation of why it happened
- Relevant code sections
- Contributing factors

### 4. Solution Applied
- Code changes made
- Files modified (with line numbers)
- Why this solution works

### 5. Testing & Verification
- How to test the fix
- Expected behavior after fix
- Monitoring recommendations

### 6. Deployment Information
- Commit hash
- Deployment timestamp
- Rollback plan (if applicable)

### 7. Lessons Learned
- What we learned from this issue
- How to prevent similar issues
- Improvements to make

## Monthly Organization

Fixes are organized by year-month for easy navigation:
- `2025-11/` - November 2025
- `2025-12/` - December 2025 (future)
- `2026-01/` - January 2026 (future)

## Related Documentation

- **Architecture**: See `docs/architecture/` for system design
- **Operations**: See `docs/operations/` for runbooks
- **Deployment**: See `docs/deployment/` for deployment guides
- **Testing**: See `docs/testing/` for test strategies

## Contributing

When adding a new fix document:
1. Create file in appropriate month directory
2. Use kebab-case naming: `component-issue-fix.md`
3. Follow the template structure above
4. Add entry to this README
5. Reference in CHANGELOG.md if significant

## Historical Index

### 2025

#### November
- **Portal API Fix** - Resolved 400 Bad Request errors by adding codigoOrgao parameter
- **AgentMessage Fix** - Fixed validation errors by adding sender/recipient fields
- **InvestigationResult Fix** - Resolved attribute error by using correct data model fields

## Quick Links

- [Complete Fix Summary (Nov 2025)](./2025-11/complete-fix-summary.md)
- [Portal API Technical Details](./2025-11/portal-api-fix.md)
- [AgentMessage Validation Details](./2025-11/agent-message-fix.md)
- [InvestigationResult Metadata Details](./2025-11/investigation-metadata-fix.md)

---

**Note**: This directory is valuable for onboarding new team members and understanding system evolution. Keep documentation clear, technical, and actionable.
