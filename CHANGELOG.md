# Changelog

All notable changes to the Cidadão.AI Backend project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Documentation link validation script (`scripts/validate_doc_links.py`)
- Comprehensive INDEX.md files for agents/, api/, and project/ documentation
- Enhanced README badges with coverage, uptime, and agent statistics

### Changed
- Improved repository organization with clearer directory structure
- Fixed file permissions for better consistency (700 → 755)

---

## [3.2.0] - 2025-11-08

### Added
- **Documentation Organization**
  - Created comprehensive documentation indexes (agents, api, project)
  - Added `docs/agents/INDEX.md` with tier classification and capabilities matrix
  - Added `docs/api/INDEX.md` with endpoint catalog (266+ endpoints)
  - Added `docs/project/INDEX.md` with planning and reports navigation

- **Repository Structure**
  - New directory: `docs/project/sessions/` for development session logs
  - New directory: `docs/archive/roadmaps-2025-10/` for historical roadmaps
  - New directory: `docs/archive/agents-old/` for superseded agent documentation
  - New directory: `tests/performance/` for performance test files
  - New directory: `scripts/performance/` for profiling scripts

### Changed
- **File Organization**
  - Moved session logs to `docs/project/sessions/`
  - Moved planning docs to `docs/planning/` with English naming
  - Moved performance files to dedicated directories
  - Consolidated duplicate Oxóssi documentation (OXOSSI.md → oxossi.md)
  - Organized 6 old roadmaps into archive

- **Documentation Updates**
  - Updated `.gitignore` with patterns for temp files
  - Updated `docs/README.md` with structure diagram
  - Fixed file permissions across documentation directories

### Fixed
- Resolved duplicate documentation files (Oxóssi agent)
- Fixed linting issues in `profile_performance.py`
- Corrected inconsistent file permissions

---

## [3.1.0] - 2025-11-07

### Added
- **Test Coverage Improvements**
  - Afternoon coverage boost session (Nov 7)
  - Improved Anita and Oxóssi test coverage
  - Boosted Ayrton Senna and Abaporu coverage to 90%+
  - Enhanced Nanã and Bonifácio coverage to 80%+
  - Added spectral significance tests for Anita

### Changed
- **Testing Strategy**
  - Focus on high-value test cases
  - Improved edge case coverage
  - Better error handling tests

### Performance
- **Lazy Loading Optimization** (367x faster)
  - Agent imports: 1460ms → 3.81ms
  - Implemented `__getattr__` pattern for deferred imports
  - Maintained full backward compatibility with aliases

---

## [3.0.0] - 2025-11-06

### Added
- **Performance Optimizations**
  - Lazy loading implementation for agents module
  - Performance profiling scripts
  - Automated testing for lazy loading behavior

### Changed
- **Agent System**
  - Refactored agent initialization for performance
  - Improved agent pool architecture
  - Enhanced caching for agent retrieval

### Fixed
- Multiple test suite failures resolved
- Agent initialization performance issues

---

## [2.9.0] - 2025-11-01

### Added
- **GraphQL API** (95% complete)
  - Complete schema with types (User, Investigation, Finding, Anomaly, Contract)
  - Queries for investigations, contracts, and agent stats
  - Mutations for creating investigations and chat messages
  - Real-time subscriptions for updates
  - GraphQL Playground at `/graphql/playground`

### Changed
- **Test Coverage**
  - Achieved 80.42% coverage (exceeded 80% target!)
  - Reduced test failures from 66 to 4 (94% improvement)
  - All 17 agents now have comprehensive tests

---

## [2.8.0] - 2025-10-31

### Added
- **Pydantic V2 Migration**
  - Complete migration to Pydantic V2
  - Eliminated all deprecation warnings
  - Improved type safety and validation performance

- **WebSocket Documentation**
  - Comprehensive WebSocket API documentation
  - Implementation status report (70% complete)
  - 16 WebSocket tests created (14 passing)

### Changed
- **Agent Status Correction**
  - Updated from "10-25% complete" to accurate "85-95% complete"
  - Documented 15 operational agents (93.75% of total)
  - Created comprehensive agent metrics dashboard

---

## [2.7.0] - 2025-10-13 to 2025-10-30

### Added
- **Production Deployment**
  - Deployed to Railway platform (Oct 7, 2025)
  - PostgreSQL database integration
  - Redis caching layer
  - 99.9% uptime achieved

- **16 Operational Agents**
  - Tier 1: 10 fully operational agents
  - Tier 2: 5 near-complete agents (85-95%)
  - Tier 3: 1 framework-only agent (30%)

- **Government API Integration**
  - 30+ Brazilian government APIs integrated
  - Portal da Transparência (22% endpoints working)
  - IBGE, DataSUS, INEP, PNCP integrations
  - 6 State TCE APIs

- **Monitoring & Observability**
  - Prometheus metrics collection
  - Grafana dashboards
  - Agent performance monitoring
  - API health checks

### Changed
- **Architecture**
  - Multi-agent orchestration system
  - Reflection pattern for quality control
  - Agent pool management with lazy loading
  - Circuit breaker pattern for external APIs

### Fixed
- Multiple production issues resolved
- API endpoint stability improvements
- Database connection pooling issues

---

## [2.0.0] - 2025-09 to 2025-10 (Early Development)

### Added
- **Core Multi-Agent System**
  - Base agent framework (Deodoro/ReflectiveAgent)
  - Initial agent implementations
  - Agent communication protocols

- **FastAPI Backend**
  - REST API structure
  - Authentication system (JWT)
  - Rate limiting
  - CORS configuration

- **Investigation System**
  - Investigation CRUD operations
  - Contract analysis
  - Anomaly detection algorithms

### Changed
- **Migration from HuggingFace to Railway**
  - Better infrastructure control
  - PostgreSQL database
  - Redis caching
  - Improved performance

---

## [1.0.0] - 2025-08 (Initial Release)

### Added
- **Project Foundation**
  - Initial repository structure
  - Basic FastAPI setup
  - First agent prototype (Zumbi)
  - Documentation framework

- **Core Features**
  - Contract analysis capability
  - Basic anomaly detection
  - Initial government API connections

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
- **Performance**: Performance improvements

---

**For detailed sprint reports**: See `docs/project/reports/`
**For planning documents**: See `docs/project/planning/`
**For technical architecture**: See `docs/architecture/`
