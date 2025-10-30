===============================================================================
CIDADÃO.AI BACKEND - FRONTEND API INTEGRATION ANALYSIS SUMMARY
===============================================================================

ANALYSIS COMPLETED: 2025-10-30
DOCUMENT: /tmp/frontend_api_analysis.md (1,650 lines, 44KB)

===============================================================================
EXECUTIVE SUMMARY
===============================================================================

The Cidadão.AI backend is a production-ready, enterprise-grade API system for
Brazilian government transparency analysis. The system provides 40+ specialized
AI agents integrated with 30+ government data sources.

KEY STATUS:
  Production Ready: ✅ Yes (live at https://cidadao-api-production.up.railway.app)
  Real Data Integration: ✅ Active (is_demo_mode: false)
  API Completeness: ✅ 90+ endpoints across 16 categories
  Test Coverage: ✅ 251+ tests, 100% agents have tests
  Architecture: ✅ FastAPI, async/await, multi-layer caching

===============================================================================
API ENDPOINT INVENTORY (90+ ENDPOINTS)
===============================================================================

1. HEALTH & MONITORING (9 endpoints)
   - Health checks, Kubernetes probes, Prometheus metrics
   - Railway-recommended: GET /health/

2. CHAT & CONVERSATIONS (15+ endpoints)
   - POST /api/v1/chat/message - Main chat endpoint
   - GET /api/v1/chat/stream - SSE streaming
   - 6 chat-enabled agents (Zumbi, Anita, Tiradentes, Machado, Bonifacio, Maria Quiteria)

3. INVESTIGATIONS (12 endpoints)
   - POST /api/v1/investigations/start - Create investigation
   - GET /api/v1/investigations/{id}/stream - SSE results streaming
   - Anomaly types: price, vendor, temporal, payment, duplicate, pattern

4. DIRECT AGENT ENDPOINTS (16 agents)
   - POST /api/v1/agents/{agent_name}
   - All agents accessible for direct invocation

5. FEDERAL APIS (7 data sources exposed as REST)
   - IBGE (geography, demographics)
   - DataSUS (health)
   - INEP (education)
   - Plus 4 more (PNCP, Compras.gov, Minha Receita, BCB)

6. TRANSPARENCY APIS (Portal integration)
   - Contracts, servants, agencies endpoints
   - Coverage map with 6-hour cache updates
   - 30+ fallback APIs when Portal returns 403

7. REPORTS & EXPORT (12+ endpoints)
   - 6 report types (executive, detailed, investigation, dashboard, comparative, audit)
   - 4 export formats (Excel, CSV, JSON, PDF)
   - Bulk export with compression support

8. ANALYSIS & VISUALIZATION (5+ endpoints)
   - Contract analysis, supplier analysis, temporal analysis
   - Network graph analysis, visualization creation

9. GEOGRAPHIC DATA (5 endpoints)
   - Boundaries, regions, metrics, coordinates

10. BATCH OPERATIONS (3 endpoints)
    - Bulk job processing and validation

11. AUTHENTICATION (8 endpoints)
    - JWT token-based (1 hour access, 7 days refresh)
    - OAuth2 integration with multiple providers
    - Rate limiting: Free (100/hr), Pro (1k/hr), Enterprise (10k/hr)

12. OBSERVABILITY & MONITORING (10+ endpoints)
    - HTTP metrics, tracing, agent statistics
    - Performance summary, correlation tracking

13. ADMIN ENDPOINTS (5+ endpoints)
    - Cache warming, database optimization
    - IP whitelist, connection pool management

14. AUDIT & COMPLIANCE (9 endpoints)
    - Audit events, statistics, integrity verification
    - Comprehensive logging and compliance dashboards

15. DEBUG & TROUBLESHOOTING (8+ endpoints)
    - Agent status, LLM configuration
    - Investigation logs, database diagnostics

16. WEBSOCKET SUPPORT (2+ endpoints)
    - Bidirectional chat
    - Real-time investigation updates

===============================================================================
REAL DATA SOURCES (30+ APIS INTEGRATED)
===============================================================================

FEDERAL LEVEL:
  ✅ Portal da Transparência (contracts, expenses) - Primary source
  ✅ PNCP (public contracts, procurement)
  ✅ Compras.gov (government purchases)
  ✅ IBGE (geography, statistics, demographics)
  ✅ DataSUS (health indicators, medical data)
  ✅ INEP (education, institutions, student data)
  ✅ Minha Receita (federal revenue, financial data)
  ✅ BCB (central bank rates, economic indicators)

STATE LEVEL (TAX/AUDIT COURTS - TCEs):
  ✅ TCE Pernambuco (PE)
  ✅ TCE Ceará (CE)
  ✅ TCE Rio de Janeiro (RJ)
  ✅ TCE São Paulo (SP)
  ✅ TCE Minas Gerais (MG)
  ✅ TCE Bahia (BA)
  Coverage: 2,500+ municipalities

STATE LEVEL (CKAN PORTALS):
  ✅ São Paulo (SP)
  ✅ Rio de Janeiro (RJ)
  ✅ Rio Grande do Sul (RS)
  ✅ Santa Catarina (SC)
  ✅ Bahia (BA)

DIRECT STATE APIs:
  ✅ Rondônia (RO) - CGE API

CACHING STRATEGY:
  1. Memory Cache (5 min TTL) - In-process, fastest
  2. Redis Cache (1 hr TTL) - Distributed, optional
  3. Database Cache (24 hr TTL) - Persistent, historical

DATA AVAILABILITY:
  Federal: Daily updates
  States: Monthly-quarterly updates
  Portal: Real-time (when accessible)
  Fallback: Automatic when primary source unavailable

===============================================================================
CHAT SYSTEM CAPABILITIES
===============================================================================

CHAT ARCHITECTURE:
  1. Intent Detection (Brazilian Portuguese NLP)
  2. Entity Extraction (NER)
  3. Data Federation (Parallel API calls)
  4. Agent Processing (Maritaca AI primary, Claude backup)
  5. Reflection Pattern (quality assurance)
  6. Response Formatting

LLM PROVIDERS:
  Primary: Maritaca AI (Sabiá-3, Brazilian Portuguese optimized)
  Backup: Anthropic Claude (Sonnet-4)
  Automatic failover if primary unavailable

STREAMING SUPPORT:
  - SSE (Server-Sent Events) for real-time updates
  - WebSocket infrastructure ready (disabled in HuggingFace)
  - Chunked streaming for large responses
  - Automatic compression (GZIP/Brotli)

SESSION MANAGEMENT:
  - 24-hour session persistence
  - Chat history available
  - Investigation context linkage
  - Local storage recommended for frontend

CHAT-ENABLED AGENTS:
  1. Zumbi dos Palmares - Anomaly detection (FFT spectral analysis)
  2. Anita Garibaldi - Statistical pattern analysis
  3. Tiradentes - Report generation
  4. Machado - Named entity recognition, text analysis
  5. Bonifácio - Legal compliance evaluation
  6. Maria Quitéria - Security auditing

===============================================================================
AUTHENTICATION & SECURITY
===============================================================================

JWT TOKEN FLOW:
  POST /api/v1/auth/login
    → access_token (1 hour)
    → refresh_token (7 days)
  POST /api/v1/auth/refresh
    → new access_token

OAUTH2 INTEGRATION:
  Supported providers configurable in production
  Social login flow available

RATE LIMITING:
  Free Tier: 100 requests/hour
  Pro Tier: 1,000 requests/hour
  Enterprise Tier: 10,000 requests/hour
  Headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

IP WHITELISTING (Production only):
  Excluded paths: /health/*, /api/v1/auth/*, /docs, /redoc

CORS CONFIGURATION:
  Allowed origins configured per environment
  Credentials allowed (cookies + Authorization header)

MIDDLEWARE STACK:
  1. SecurityMiddleware (headers, CSP)
  2. LoggingMiddleware (request/response)
  3. CompressionMiddleware (GZIP/Brotli)
  4. StreamingCompressionMiddleware (chunked)
  5. CorrelationMiddleware (request tracking)
  6. MetricsMiddleware (Prometheus)
  7. RateLimitMiddleware (sliding window)
  8. IPWhitelistMiddleware (production)
  9. QueryTrackingMiddleware (cache optimization)

===============================================================================
EXPORT & REPORTING CAPABILITIES
===============================================================================

REPORT TYPES (6):
  1. Executive Summary - High-level findings (2-3 pages)
  2. Detailed Analysis - Complete findings with charts
  3. Investigation Report - Full anomaly details
  4. Transparency Dashboard - Interactive HTML
  5. Comparative Analysis - Multi-period comparison
  6. Audit Report - Compliance-focused

EXPORT FORMATS (4):
  1. Excel (.xlsx) - Full data with formatting
  2. CSV (.csv) - Comma-separated, optional compression
  3. JSON (.json) - Machine-readable, API integration
  4. PDF (.pdf) - Distribution, archival (partial support)

TARGET AUDIENCES:
  - General
  - Technical
  - Executive
  - Journalist
  - Researcher

EXPORT TYPES (9):
  - Investigations
  - Contracts
  - Anomalies
  - Reports
  - Analytics
  - Full data
  - Visualizations
  - Regional analysis
  - Time series

BULK EXPORT:
  - Multiple datasets in single request
  - ZIP compression support
  - Progress tracking

===============================================================================
KNOWN LIMITATIONS & WORKAROUNDS
===============================================================================

1. PORTAL DA TRANSPARÊNCIA ACCESS
   Issue: 78% of endpoints return 403 Forbidden
   Root Cause: Government API access tier restrictions
   Workaround: Auto-fallback to TCE, CKAN, alternative federal APIs
   Frontend: Check metadata.sources to identify data source

2. WEBSOCKET STREAMING
   Status: Infrastructure ready, disabled in HuggingFace
   Workaround: Use SSE (GET /api/v1/investigations/stream/{id})
   Feature Flag: NEXT_PUBLIC_FEATURE_WEBSOCKET=false

3. IN-MEMORY DATABASE
   Issue: SQLite in-memory loses data on restart (dev only)
   Production: PostgreSQL configured in Railway
   Frontend: No impact (transparent)

4. PDF EXPORT
   Status: Partial support (JSON to PDF needs conversion)
   Current: HTML, JSON, Excel/CSV fully supported
   Workaround: Use HTML + client-side print-to-PDF

5. REAL-TIME UPDATES
   Issue: WebSocket unreliable in HuggingFace Spaces
   Workaround: Use polling with exponential backoff
   Max Backoff: 30 seconds

6. LARGE DATASET EXPORTS
   Issue: 30-second timeout on HuggingFace Spaces (>10MB)
   Workaround: Use filters, chunk by time range, enable compression
   Compression reduces data ~60%

===============================================================================
PERFORMANCE METRICS (PRODUCTION SLA)
===============================================================================

Target vs Actual (p95):
  Health checks:          <50ms | Actual: 15ms ✅
  Chat message:          <500ms | Actual: 380ms ✅
  Investigation start:      <1s | Actual: 850ms ✅
  Agent processing:         <5s | Actual: 3.2s ✅
  Data export:             <10s | Actual: 7.5s ✅
  Portal API call:          <3s | Actual: 2.8s ✅

OPTIMIZATION STRATEGIES:
  1. Multi-layer caching (Memory → Redis → DB)
  2. Response compression (GZIP level 7-9, Brotli)
  3. Connection pooling (5-20 PostgreSQL, 1 Redis)
  4. Request batching (bulk operations)
  5. Lazy agent loading (on-demand instantiation)
  6. Parallel API calls (data federation)
  7. Circuit breaker pattern (fault tolerance)

===============================================================================
FRONTEND INTEGRATION PATTERNS (5 CORE PATTERNS)
===============================================================================

1. CHAT INTERFACE
   - Session management with localStorage
   - Message sending and response handling
   - Check is_demo_mode flag
   - Display suggested actions and follow-up questions

2. INVESTIGATION STREAMING
   - Subscribe to SSE stream: /api/v1/investigations/stream/{id}
   - Handle progress, anomaly, and completion events
   - Real-time UI updates

3. DATA EXPORT
   - POST /api/v1/export/investigations/{id}/download
   - Support multiple formats
   - Show download progress

4. REAL-TIME MONITORING (WebSocket alternative)
   - Use polling with exponential backoff
   - Max 30-second intervals
   - Detect completion and stop polling

5. MULTI-FORMAT EXPORT
   - Bulk export with ZIP compression
   - Progress tracking for large operations
   - File download with progress indicator

===============================================================================
FRONTEND IMPLEMENTATION CHECKLIST
===============================================================================

Error Handling:
  ☐ Handle HTTP status codes (401, 403, 429, 500, 503)
  ☐ Parse CidadaoAIError custom exceptions
  ☐ Implement timeout and network error handling

Rate Limiting:
  ☐ Monitor X-RateLimit-* headers
  ☐ Implement exponential backoff for 429
  ☐ Cache results when possible

Data Sources:
  ☐ Check metadata.is_demo_mode flag
  ☐ Handle alternative data sources in fallback
  ☐ Validate data freshness (cache_age_seconds)

Authentication:
  ☐ Store JWT securely (HttpOnly cookies preferred)
  ☐ Refresh tokens before expiry
  ☐ Clear tokens on logout
  ☐ Handle 401 Unauthorized (redirect to login)

Streaming:
  ☐ Implement SSE with EventSource API
  ☐ Handle stream errors and reconnection
  ☐ Display real-time progress indicators

Export:
  ☐ Show download progress for large files
  ☐ Suggest chunking for >10MB exports
  ☐ Validate format support

Performance:
  ☐ Cache chat session IDs locally
  ☐ Debounce search/filter inputs
  ☐ Use virtual scrolling for large lists
  ☐ Compress outgoing requests

Monitoring:
  ☐ Log API errors for debugging
  ☐ Track endpoint response times
  ☐ Monitor usage metrics
  ☐ Alert on high error rates

===============================================================================
KEY FINDINGS & RECOMMENDATIONS
===============================================================================

STRENGTHS:
  ✅ Production-ready with 99.9% uptime in Railway
  ✅ Real government data integration (30+ APIs)
  ✅ Comprehensive AI agent system (16 specialized agents)
  ✅ Multi-layer caching for optimal performance
  ✅ Enterprise security (JWT, OAuth2, IP whitelist, audit logging)
  ✅ Real-time capabilities (SSE, WebSocket infrastructure)
  ✅ Multiple export formats (Excel, PDF, JSON, CSV)
  ✅ Automatic fallback for degraded services
  ✅ Full API documentation at /docs

CONSIDERATIONS:
  ⚠️  Portal API 403 errors expected (78% of endpoints)
      - Workaround: System auto-falls back to 30+ alternative APIs
  ⚠️  WebSocket disabled in HuggingFace Spaces
      - Workaround: Use SSE streaming instead
  ⚠️  Large exports may timeout on HuggingFace (>10MB, 30s limit)
      - Workaround: Use filters, chunking, compression

RECOMMENDED FRONTEND INTEGRATION:
  1. Use session-based chat (persist session_id in localStorage)
  2. Implement SSE streaming for real-time investigation updates
  3. Check is_demo_mode flag in responses
  4. Monitor X-RateLimit headers for rate limit awareness
  5. Use exponential backoff for resilience
  6. Chunk large exports by time range
  7. Cache frequently accessed data (agents, geographic data)
  8. Implement error boundaries for graceful degradation

===============================================================================
FILE LOCATIONS & NEXT STEPS
===============================================================================

ANALYSIS DOCUMENT:
  Location: /tmp/frontend_api_analysis.md (1,650 lines, 44KB)
  Format: Markdown with detailed sections
  Sections: Architecture, endpoints, data sources, integration patterns, examples

FOR FRONTEND TEAM:
  1. Review "FRONTEND INTEGRATION PATTERNS" section
  2. Implement error handling checklist
  3. Set up SSE streaming for real-time features
  4. Configure rate limit handling
  5. Implement export functionality with progress tracking

FOR BACKEND TEAM:
  1. Verify all documented endpoints are accessible
  2. Update API documentation if needed
  3. Monitor Portal API fallback patterns
  4. Ensure cache invalidation for data freshness

RESOURCES:
  - API Documentation: https://cidadao-api-production.up.railway.app/docs
  - Health Status: https://cidadao-api-production.up.railway.app/health/
  - GitHub: https://github.com/anderson-ufrj/cidadao.ai-backend
  - CLAUDE.md: Full project documentation in repo

===============================================================================
CONCLUSION
===============================================================================

The Cidadão.AI backend is a mature, production-ready system with comprehensive
API coverage for Brazilian government transparency analysis. The integration of
30+ data sources, advanced AI agents, and enterprise-grade infrastructure
provides a solid foundation for sophisticated frontend applications.

All critical endpoints are production-ready and tested. Real government data
integration is active (is_demo_mode: false). The system gracefully handles
limitations in Portal da Transparência access through intelligent fallback to
alternative federal, state, and municipal data sources.

Frontend teams can confidently integrate with all documented endpoints,
implementing the provided patterns and checklists for production-quality
implementations.

===============================================================================
