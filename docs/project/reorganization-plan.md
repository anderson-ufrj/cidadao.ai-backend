# Repository Reorganization Plan

**Date**: November 17, 2025
**Status**: Planning Phase

---

## Current Problems

### Root Directory Issues
- ❌ 30+ test scripts scattered in root (test_*.py)
- ❌ 3 fix summary files in root (FIX_*.md)
- ❌ 2 investigation scripts in root (investigate_*.py)
- ❌ Multiple loose documentation files

### Docs Directory Issues
- ❌ API status reports scattered (8+ files with different naming)
- ❌ No clear categorization
- ❌ Duplicate/overlapping content
- ❌ Inconsistent naming conventions

---

## Proposed Structure

```
cidadao.ai-backend/
├── .github/              # GitHub workflows, templates
├── .claude/              # Claude Code configuration
├── alembic/              # Database migrations
├── config/               # Configuration files
├── data/                 # Sample data, fixtures
├── logs/                 # Application logs (gitignored)
├── monitoring/           # Grafana, Prometheus configs
├── scripts/              # Utility scripts
│   ├── debug/           # Investigation/debug scripts
│   │   ├── investigate_data_flow.py
│   │   └── investigate_tce_mg.py
│   ├── deployment/      # Deployment scripts
│   └── testing/         # Testing utilities
├── src/                  # Main application code
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── e2e/             # End-to-end tests
│   └── manual/          # Manual test scripts
│       ├── api/         # API testing scripts
│       ├── chat/        # Chat endpoint testing
│       └── portal/      # Portal API testing
├── docs/                 # Documentation
│   ├── README.md        # Documentation index
│   ├── agents/          # Agent documentation
│   ├── api/             # API documentation
│   ├── api-status/      # API integration status reports
│   │   ├── 2025-11/    # Monthly reports
│   │   │   ├── all-apis-status.md
│   │   │   ├── siconfi-status.md
│   │   │   └── tce-apis-status.md
│   │   └── README.md   # Status reports index
│   ├── architecture/    # System architecture
│   ├── deployment/      # Deployment guides
│   ├── development/     # Development guides
│   ├── examples/        # Usage examples
│   ├── fixes/           # Fix summaries and postmortems
│   │   ├── 2025-11/    # Monthly fixes
│   │   │   ├── portal-api-fix.md
│   │   │   ├── agent-message-fix.md
│   │   │   ├── investigation-metadata-fix.md
│   │   │   └── complete-fix-summary.md
│   │   └── README.md   # Fixes index
│   ├── operations/      # Operational guides
│   ├── project/         # Project management
│   ├── release/         # Release notes
│   ├── technical/       # Technical deep-dives
│   └── testing/         # Testing documentation
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── CHANGELOG.md         # Project changelog
├── CITATION.cff         # Citation metadata
├── CLAUDE.md            # Claude Code instructions
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # License file
├── Makefile             # Development commands
├── pyproject.toml       # Python project config
├── pytest.ini           # Pytest configuration
├── QUICKSTART.md        # Quick start guide
├── README.md            # Main project README
└── SECURITY.md          # Security policy
```

---

## Reorganization Steps

### Step 1: Create New Directory Structure
```bash
mkdir -p scripts/debug
mkdir -p scripts/deployment
mkdir -p scripts/testing
mkdir -p tests/manual/api
mkdir -p tests/manual/chat
mkdir -p tests/manual/portal
mkdir -p docs/api-status/2025-11
mkdir -p docs/fixes/2025-11
```

### Step 2: Move Test Scripts
```bash
# Move API test scripts
mv test_all_apis_*.py tests/manual/api/
mv test_ckan_states.py tests/manual/api/
mv test_siconfi*.py tests/manual/api/
mv test_tce_apis.py tests/manual/api/

# Move chat test scripts
mv test_chat_*.py tests/manual/chat/
mv test_production_chat.py tests/manual/chat/

# Move portal test scripts
mv test_portal_*.py tests/manual/portal/
mv test_production_portal_fix.py tests/manual/portal/

# Move flow test scripts
mv test_complete_flow.py tests/manual/
mv test_entity_extraction_integration.py tests/manual/
mv test_intent_*.py tests/manual/
mv test_import_investigator.py tests/manual/
mv test_railway_database.py tests/manual/
```

### Step 3: Move Investigation Scripts
```bash
mv investigate_*.py scripts/debug/
```

### Step 4: Move Fix Summaries
```bash
mv FIX_*.md docs/fixes/2025-11/
mv COMPLETE_FIX_SUMMARY.md docs/fixes/2025-11/
```

### Step 5: Reorganize API Status Reports
```bash
# Move to api-status/2025-11/
mv docs/ALL_APIS_STATUS_2025_11_14.md docs/api-status/2025-11/all-apis-status.md
mv docs/COMPLETE_API_STATUS_2025_11_14.md docs/api-status/2025-11/complete-api-status.md
mv docs/FINAL_API_STATUS_2025_11_14.md docs/api-status/2025-11/final-api-status.md
mv docs/SICONFI_INTEGRATION_STATUS_2025_11_14.md docs/api-status/2025-11/siconfi-status.md
mv docs/TCE_APIS_STATUS_2025_11_14.md docs/api-status/2025-11/tce-apis-status.md
mv docs/TCE_MG_*.md docs/api-status/2025-11/
mv docs/NEW_APIS_TO_INTEGRATE_2025_11_14.md docs/api-status/2025-11/new-apis-to-integrate.md
mv docs/api-integration-status.md docs/api-status/
```

### Step 6: Clean Up Chat Problem Docs
```bash
# Move chat-related docs to examples
mv docs/PROBLEMA_CHAT_APIS.md docs/examples/
mv docs/RESPOSTA_CHAT_APIS.md docs/examples/
mv docs/EXEMPLOS_PRATICOS_CHAT.md docs/examples/
mv docs/INDICE_CHAT_APIS.md docs/examples/
```

### Step 7: Create Index Files
- `docs/README.md` - Main documentation index
- `docs/api-status/README.md` - API status reports index
- `docs/fixes/README.md` - Fixes and postmortems index
- `tests/manual/README.md` - Manual testing guide

---

## Benefits

### Cleaner Root Directory
- ✅ Only essential config files in root
- ✅ All scripts organized by purpose
- ✅ Easy to find what you need
- ✅ Professional appearance

### Better Documentation Organization
- ✅ Clear categorization (api-status, fixes, etc.)
- ✅ Monthly organization for time-based docs
- ✅ Index files for easy navigation
- ✅ Consistent naming conventions

### Improved Developer Experience
- ✅ Easier onboarding for new contributors
- ✅ Clear separation of concerns
- ✅ Better searchability
- ✅ Reduced cognitive load

---

## Backward Compatibility

### Preserve Git History
Use `git mv` instead of `mv` to preserve file history.

### Update References
After moving files, update:
- README.md links
- CLAUDE.md file paths
- GitHub Actions paths (if any)
- Import statements (for Python scripts)

---

## Timeline

- **Step 1-3**: Move scripts (5 min)
- **Step 4-6**: Reorganize docs (10 min)
- **Step 7**: Create indexes (10 min)
- **Testing**: Verify structure (5 min)
- **Commit**: Clean, organized commit (5 min)

**Total**: ~35 minutes

---

## Success Criteria

- ✅ Root directory has < 15 files (only essentials)
- ✅ All test scripts in tests/manual/
- ✅ All docs properly categorized
- ✅ Index files created
- ✅ Git history preserved
- ✅ No broken links
- ✅ Professional repository structure
