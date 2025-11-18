# Documentation Cleanup Checklist
**Created**: November 17, 2025
**Based on**: DOCUMENTATION_FORENSIC_ANALYSIS_2025_11_17.md

---

## 🔴 WEEK 1: CRITICAL (Fix Immediately)

### Day 1: Roadmap Consolidation (30 min)
- [ ] Review `ROADMAP_TCC_2025.md` - Is it superseded by official roadmap?
- [ ] Review `ROADMAP_TCC_DEZ_2025.md` - Is it superseded by official roadmap?
- [ ] **Decision**: Archive, reconcile, or delete?
- [ ] If archiving: Move to `docs/archive/2025-11-documentation-cleanup/roadmaps/`
- [ ] Update `ROADMAP_OFFICIAL_2025.md` header to state it supersedes all others

### Day 2: Status Files Cleanup (20 min)
- [ ] Create archive folder: `docs/archive/2025-11-documentation-cleanup/status-reports/`
- [ ] Move `docs/project/current/CURRENT_STATUS_2025_10.md` to archive
- [ ] Move `docs/project/current/CURRENT_STATUS.md` to archive
- [ ] Move `docs/project/current/QUICK_STATUS.md` to archive
- [ ] Move `docs/project/current/IMPLEMENTATION_REALITY.md` to archive (if outdated)
- [ ] Move `docs/project/current/TRANSPARENCY_MAP_IMPLEMENTATION_STATUS.md` to archive (if outdated)
- [ ] Move `docs/project/current/MILESTONE_16_AGENTS_COMPLETE_2025_10_27.md` to archive
- [ ] Review `docs/project/current/CHANGELOG.md` - Keep if active, archive if abandoned
- [ ] Move `docs/project/STATUS_ATUAL_2025_11.md` to archive
- [ ] Update `STATUS_ATUAL_2025_11_14.md` to add note: "This is the current status. All others are archived."

### Day 3: Test Coverage Verification (10 min)
- [ ] Run: `JWT_SECRET_KEY=test SECRET_KEY=test pytest --cov=src --cov-report=term-missing -v`
- [ ] Record actual numbers:
  - Total tests: _____
  - Coverage %: _____
  - Test files: _____
- [ ] Update `STATUS_ATUAL_2025_11_14.md` with verified numbers
- [ ] Update `CLAUDE.md` with verified numbers
- [ ] Add note: "Last verified: YYYY-MM-DD"

### Day 4: Agent Terminology Standardization (10 min)
- [ ] **Decision**: Use "16 functional agents + 1 base framework (Deodoro)" OR "17 agents total"?
- [ ] Update `STATUS_ATUAL_2025_11_14.md` with chosen terminology
- [ ] Update `CLAUDE.md` with chosen terminology
- [ ] Update `docs/agents/INVENTORY.md` with chosen terminology
- [ ] Update `docs/agents/README.md` with chosen terminology
- [ ] Add glossary entry: "Agent count: {your decision} means..."

**Week 1 Total Time**: ~70 minutes

---

## 🟡 WEEK 2: HIGH PRIORITY

### Task 1: Update Agent Inventory (30 min)
- [ ] Open `docs/agents/INVENTORY.md`
- [ ] Add tier classification section:
  - Tier 1 (10 agents): Zumbi, Anita, Oxóssi, Lampião, Senna, Tiradentes, Niemeyer, Machado, Bonifácio, Maria Quitéria
  - Tier 2 (5 agents): Abaporu, Nanã, Drummond, Céuci, Obaluaiê
  - Tier 3 (1 agent): Dandara
  - Base (1): Deodoro
- [ ] Add "Last Updated: 2025-11-{day}" at top
- [ ] Cross-reference with `STATUS_ATUAL_2025_11_14.md` for accuracy
- [ ] Archive `docs/agents/AGENT_INVENTORY_2025_10_24.md` (duplicate)

### Task 2: Fix LLM Provider Documentation (15 min)
- [ ] Check `.env.example` for default model
- [ ] Check production Railway config for actual model
- [ ] Update `CLAUDE.md` LLM Provider section:
  - Default model: _____
  - Production model: _____
  - Clarify any differences
- [ ] Add note: "Verified: 2025-11-{day}"

### Task 3: Create Missing Core Documentation (2 hours)

#### CONTRIBUTING.md (30 min)
- [ ] Create `CONTRIBUTING.md` at root
- [ ] Include:
  - Code of conduct
  - How to set up dev environment
  - Coding standards (Black, Ruff, MyPy)
  - Commit message format (no AI mentions!)
  - PR process
  - Testing requirements (80% coverage)
  - Documentation requirements

#### ARCHITECTURE_OVERVIEW.md (30 min)
- [ ] Create `ARCHITECTURE_OVERVIEW.md` at root
- [ ] Include:
  - High-level system diagram
  - Key components (API, Agents, Database, Cache)
  - Data flow (request → response)
  - Agent orchestration overview
  - Link to detailed docs in `docs/architecture/`

#### TESTING.md (30 min)
- [ ] Create `TESTING.md` at root
- [ ] Include:
  - How to run tests (`make test`)
  - Required environment variables (JWT_SECRET_KEY=test SECRET_KEY=test)
  - Test categories (unit, integration, e2e)
  - Coverage requirements (80%)
  - How to write tests for agents
  - CI/CD testing pipeline

#### API_CHANGELOG.md (15 min)
- [ ] Create `docs/api/API_CHANGELOG.md`
- [ ] Include:
  - Version history
  - Breaking changes log
  - Deprecation notices
  - Migration guides
  - Format: `## [Version] - YYYY-MM-DD`

#### SECURITY.md (15 min)
- [ ] Create `SECURITY.md` at root
- [ ] Include:
  - Supported versions
  - How to report vulnerabilities (email)
  - Security best practices
  - Responsible disclosure policy
  - Security update process

**Week 2 Total Time**: ~2 hours 45 minutes

---

## 🟢 WEEK 3: CLEANUP & ORGANIZATION

### Task 1: Consolidate Duplicates (1 hour)
- [ ] Review all files named `INVENTORY.md` or similar:
  - Keep: `docs/agents/INVENTORY.md` (update date)
  - Archive: `docs/agents/AGENT_INVENTORY_2025_10_24.md`
- [ ] Review all README files (15 instances):
  - Ensure each has a clear purpose
  - Update outdated ones
  - Archive unnecessary ones
- [ ] Review status reports:
  - Only `STATUS_ATUAL_2025_11_14.md` should be active
  - All others should be in archive
- [ ] Review roadmaps:
  - Only `ROADMAP_OFFICIAL_2025.md` should be active
  - All others should be in archive

### Task 2: Add Documentation Dates (30 min)
- [ ] Run: `grep -L "Last Updated\|Date\|data\|Data:" docs/**/*.md > undated_files.txt`
- [ ] For each file in undated_files.txt:
  - Add at top: `# Document Title\n**Last Updated**: YYYY-MM-DD\n`
  - Use file's last git commit date if available
- [ ] Convention going forward:
  - All new docs must have `**Last Updated**: YYYY-MM-DD`
  - Update date whenever making significant changes

### Task 3: Create Documentation Index (1 hour)
- [ ] Create `DOCUMENTATION_INDEX.md` at root
- [ ] Structure:
  ```markdown
  # Cidadão.AI Documentation Index

  ## 🚀 Getting Started
  - [README](README.md) - Project overview
  - [ARCHITECTURE_OVERVIEW](ARCHITECTURE_OVERVIEW.md) - High-level architecture
  - [CONTRIBUTING](CONTRIBUTING.md) - How to contribute
  - [TESTING](TESTING.md) - Testing guide

  ## 📊 Current Status
  - [STATUS_ATUAL_2025_11_14](docs/project/STATUS_ATUAL_2025_11_14.md) - Latest status report
  - [ROADMAP_OFFICIAL_2025](docs/project/ROADMAP_OFFICIAL_2025.md) - Official roadmap

  ## 🤖 Agents
  - [Agent Inventory](docs/agents/INVENTORY.md) - All 16+1 agents
  - [Individual Agent Docs](docs/agents/) - Detailed agent documentation

  ## 🏗️ Architecture
  - [Multi-Agent Architecture](docs/architecture/multi-agent-architecture.md) - System design
  - [Improvement Roadmap](docs/architecture/IMPROVEMENT_ROADMAP_2025.md) - Technical improvements

  ## 🌐 API
  - [API Documentation](docs/api/) - API guides
  - [Streaming Implementation](docs/api/STREAMING_IMPLEMENTATION.md) - SSE/WebSocket
  - [API Changelog](docs/api/API_CHANGELOG.md) - Breaking changes

  ## 🚀 Deployment
  - [Railway Deployment](docs/deployment/railway/) - Production platform

  ## 📚 Archive
  - [Archive Index](docs/archive/README.md) - Historical documentation
  ```
- [ ] Update main README.md to link to DOCUMENTATION_INDEX.md
- [ ] Add "Last Updated" date to index

**Week 3 Total Time**: ~2 hours 30 minutes

---

## 📊 PROGRESS TRACKING

### Week 1 Progress
- [ ] Day 1: Roadmap Consolidation
- [ ] Day 2: Status Files Cleanup
- [ ] Day 3: Test Coverage Verification
- [ ] Day 4: Agent Terminology

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

### Week 2 Progress
- [ ] Task 1: Update Agent Inventory
- [ ] Task 2: Fix LLM Provider Docs
- [ ] Task 3: Create Missing Core Docs

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

### Week 3 Progress
- [ ] Task 1: Consolidate Duplicates
- [ ] Task 2: Add Documentation Dates
- [ ] Task 3: Create Documentation Index

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

---

## 📁 FILES TO CREATE

### Week 2 (5 new files):
1. [ ] `CONTRIBUTING.md` (root)
2. [ ] `ARCHITECTURE_OVERVIEW.md` (root)
3. [ ] `TESTING.md` (root)
4. [ ] `docs/api/API_CHANGELOG.md`
5. [ ] `SECURITY.md` (root)

### Week 3 (1 new file):
6. [ ] `DOCUMENTATION_INDEX.md` (root)

---

## 📁 FOLDERS TO CREATE

1. [ ] `docs/archive/2025-11-documentation-cleanup/`
2. [ ] `docs/archive/2025-11-documentation-cleanup/roadmaps/`
3. [ ] `docs/archive/2025-11-documentation-cleanup/status-reports/`

---

## 🎯 SUCCESS CRITERIA

### Week 1 (Critical):
- ✅ Only 1 active roadmap (ROADMAP_OFFICIAL_2025.md)
- ✅ Only 1 active status file (STATUS_ATUAL_2025_11_14.md)
- ✅ Verified test coverage numbers
- ✅ Consistent agent count terminology

### Week 2 (High Priority):
- ✅ Agent inventory has tier classifications
- ✅ LLM provider docs match reality
- ✅ All 5 core docs created

### Week 3 (Cleanup):
- ✅ No duplicate content in active docs
- ✅ All docs have dates
- ✅ Documentation index exists

---

## 🚀 POST-COMPLETION

After completing all 3 weeks:
- [ ] Update `STATUS_ATUAL_2025_11_14.md` with "Documentation cleanup completed"
- [ ] Run verification commands to confirm accuracy
- [ ] Create new status report: `STATUS_ATUAL_2025_12_XX.md`
- [ ] Mark this checklist as complete
- [ ] Archive this checklist to `docs/archive/2025-11-documentation-cleanup/`

---

## 📞 Questions?

If unclear on any task, refer to:
- `DOCUMENTATION_FORENSIC_ANALYSIS_2025_11_17.md` - Full analysis
- `docs/project/reports/DOCUMENTATION_FORENSICS_2025_11_17.json` - JSON data
- `CLAUDE.md` - Project context

---

**Checklist Created**: November 17, 2025
**Expected Completion**: December 8, 2025 (3 weeks)
**Total Estimated Time**: ~5 hours 45 minutes

---

**Remember**: Be RUTHLESS. If something is outdated, archive it. If it's duplicate, delete it. If it's unclear, clarify it. This is a forensic cleanup, not a gentle update.
