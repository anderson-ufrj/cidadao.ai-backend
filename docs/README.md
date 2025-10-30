# 📚 Cidadão.AI Backend - Documentation

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-29 (Professional Documentation Reorganization)

---

> **✅ DOCUMENTATION REORGANIZATION COMPLETE - OCTOBER 2025**
>
> **Professional structure implemented** (2025-10-29):
> - ✅ **53 session reports** moved to `archive/2025-10-sessions/`
> - ✅ **Current status** organized in `project/current/`
> - ✅ **Planning docs** consolidated in `project/planning/`
> - ✅ **Clean navigation** - easy to find relevant documentation
> - **Current metrics**: **16 agents** (10 Tier 1, 5 Tier 2, 1 Tier 3)
> - **Production**: Railway (99.9% uptime since 07/10/2025)

---

> **Comprehensive documentation for the Cidadão.AI multi-agent transparency platform**

---

## 🗂️ Documentation Structure

### 🎨 [Frontend Integration](frontend-integration/) **NEW!** ⭐

**Complete API guide for frontend developers** - Everything you need to integrate with Cidadão.AI backend.

- **[README](frontend-integration/README.md)** - Start here! Navigation guide and quick reference
- **[Comprehensive API Guide](frontend-integration/COMPREHENSIVE_API_GUIDE.md)** ⭐ - 1,650 lines, 90+ endpoints
  - Complete endpoint catalog with schemas
  - 30+ government data sources
  - 5 integration patterns with code examples
  - Working curl/JavaScript examples
- **[Executive Summary](frontend-integration/EXECUTIVE_SUMMARY.md)** - Quick overview for decision makers
  - 45-item implementation checklist
  - Key findings and recommendations
  - Performance metrics and validation

### 🚀 [Deployment](deployment/)

Production deployment guides and configurations.

- **[Railway Guide](deployment/railway/README.md)** ⭐ - Primary production platform
  - Complete setup and troubleshooting
  - Environment variables
  - Database and Redis configuration
  - [Historical docs](deployment/railway/archive/) - Archived deployment fixes
- **[Docker Deployment](deployment/docker.md)** - Container-based deployment
- **[Database Checks](deployment/DATABASE_CHECK.md)** - Health verification
- **[Service Health](deployment/SERVICE_HEALTH_CHECKS.md)** - Monitoring setup

### 🏗️ [Architecture](architecture/)

System design and technical architecture.

- **[Multi-API Integration](architecture/MULTI_API_INTEGRATION.md)** ⭐ - NEW!
  - 15+ government data sources
  - Intelligent routing strategies
  - Complete integration guide
- **[Agent Pool Architecture](architecture/AGENT_POOL_ARCHITECTURE.md)** - Agent management
- **[Orchestration System](architecture/ORCHESTRATION_SYSTEM.md)** - Multi-source coordination
- **[Auto-Investigation System](architecture/auto-investigation-system.md)** - 24/7 monitoring
- **[Multi-Agent Architecture](architecture/multi-agent-architecture.md)** - Agent collaboration
- **[Performance Optimization](architecture/PERFORMANCE_OPTIMIZATION.md)** - Speed improvements
- **[Monitoring & Observability](architecture/MONITORING_OBSERVABILITY.md)** - Metrics and logs
- **[Redis Cache](architecture/REDIS_CACHE_IMPLEMENTATION.md)** - Caching strategy
- **[Connection Pooling](architecture/CONNECTION_POOLING.md)** - Database optimization
- **[Agent Lazy Loading](architecture/AGENT_LAZY_LOADING.md)** - Memory efficiency

### 💻 [Development](development/)

Guides for developers working on the project.

- **[Code Duplication Analysis](development/CODE_DUPLICATION_ANALYSIS.md)** - Code quality
- **[Conversational AI](development/CONVERSATIONAL_AI_IMPLEMENTATION.md)** - Chat system
- **[CORS Configuration](development/CORS_CONFIGURATION.md)** - Cross-origin setup
- **[Cursor Pagination](development/CURSOR_PAGINATION_IMPLEMENTATION.md)** - Efficient pagination
- **[Frontend Integration](development/FRONTEND_INTEGRATION_GUIDE.md)** - Frontend connection

### 📊 [Monitoring](monitoring/)

Production monitoring and observability.

- **[Grafana Dashboards Guide](monitoring/GRAFANA_DASHBOARDS_GUIDE.md)** ⭐ NEW! - Complete monitoring setup
  - 6 production dashboards documented
  - PromQL query examples for all metrics
  - Alert configurations (Critical/Warning)
  - Troubleshooting guide
  - Daily monitoring procedures

### 📊 [Project](project/)

Project management, status tracking, and planning.

#### Current Status
- **[Current Status 2025-10](project/current/CURRENT_STATUS_2025_10.md)** ⭐ - Latest comprehensive status
- **[Quick Status](project/current/QUICK_STATUS.md)** - Quick reference guide
- **[Implementation Reality](project/current/IMPLEMENTATION_REALITY.md)** - Real vs planned features
- **[Milestone: 16 Agents Complete](project/current/MILESTONE_16_AGENTS_COMPLETE_2025_10_27.md)** - Recent achievement
- **[Transparency Map Status](project/current/TRANSPARENCY_MAP_IMPLEMENTATION_STATUS.md)** - API integration status
- **[CHANGELOG](project/current/CHANGELOG.md)** - Version history

#### Planning & Roadmaps
- **[Planning Documents](project/planning/)** - Sprint plans, roadmaps, and v1.0 checklist
- **[Reports](project/reports/2025-10/)** - Monthly progress reports

#### Privacy & Policies
- **[Privacy Policy](project/PRIVACY.md)** - Data privacy guidelines

### 🤖 [Agents](agents/)

Documentation for each AI agent.

- **[Abaporu](agents/abaporu.md)** - Master Orchestrator
- **[Zumbi](agents/zumbi.md)** - Anomaly Detective
- **[Anita](agents/anita.md)** - Data Analyst
- **[Tiradentes](agents/tiradentes.md)** - Report Writer
- **[Lampião](agents/lampiao.md)** - IBGE Data Integrator
- **[Dandara](agents/dandara.md)** - Search Specialist
- **[Nanã](agents/nana.md)** - Memory Manager
- *[See full list...](agents/)*

### 🌐 [API](api/)

API documentation and integration guides.

- **[REST API Endpoints](api/ENDPOINTS_CONNECTION_STATUS.md)** - Complete endpoint reference
- **[Chat API](api/CHAT_API_DOCUMENTATION.md)** - Conversational interface
- **[WebSocket API](api/WEBSOCKET_API_DOCUMENTATION.md)** - Real-time communication
- **[Backend Chat Implementation](api/BACKEND_CHAT_IMPLEMENTATION.md)** - Implementation details
- **[Supabase REST](api/supabase-rest.md)** - Database REST API
- **[Portal da Transparência](api/PORTAL_TRANSPARENCIA_INTEGRATION.md)** - Government API

### 📝 [Examples](examples/)

Code examples and usage demos.

- **[Agent Usage](examples/agent_dados_gov_usage.py)** - Using agents programmatically
- **[Chat Demo](examples/chat_dados_gov_demo.py)** - Chat API example
- **[Frontend Integration](examples/frontend_integration.tsx)** - React/Next.js example
- **[Maritaca Integration](examples/integrations/maritaca_drummond_integration.py)** - LLM integration

### ⚙️ [Setup](setup/)

Configuration guides for system components.

- **[Supabase Setup](setup/supabase-setup.md)** - PostgreSQL database configuration
- **[Supabase Integration](setup/supabase-integration.md)** - Complete integration guide
- **[Supabase Quick Start](setup/supabase-quick-start.md)** - Fast setup for development
- **[Supabase Testing](setup/supabase-testing.md)** - Testing database integration
- **[Alerts Setup](setup/alerts.md)** - Webhook notifications (Discord, Slack)
- **[Token Configuration](setup/tokens.md)** - Environment variables guide

### 🐛 [Troubleshooting](troubleshooting/)

Common issues and solutions.

- **[Production Fixes 2025-10-29](troubleshooting/PRODUCTION_FIXES_2025_10_29.md)** ⭐ NEW! - Latest fixes
- **[Supabase Errors](troubleshooting/supabase-errors.md)** - Database troubleshooting
- **[Railway Issues](deployment/railway/README.md#-troubleshooting)** - Deployment problems
- **[Common Issues](troubleshooting/common-issues.md)** - General problems

### 📦 [Archive](archive/)

Historical documentation and development audit trail.

- **[2025-01 Historical](archive/2025-01-historical/)** - January 2025 documentation
- **[2025-10 Deployment](archive/2025-10-deployment/)** - October deployment docs
- **[2025-10 Sessions](archive/2025-10-sessions/)** ⭐ NEW! - 53 session reports, coverage analyses, and fixes
  - Complete development history for October 2025
  - Coverage sprint reports
  - Session summaries
  - Fix documentation

### 🧪 [Testing](testing/)

Test documentation and quality assurance.

- Test strategies and coverage reports
- Quality assurance guidelines

---

## 🚀 Quick Start Guides

### For New Developers

1. **[Current Status](project/current/CURRENT_STATUS_2025_10.md)** - Understand where we are
2. **[Railway Deployment](deployment/railway/README.md)** - Deploy to production
3. **[Setup Guide](setup/supabase-quick-start.md)** - Configure local environment
4. **[Architecture Overview](architecture/MULTI_API_INTEGRATION.md)** - Understand the system
5. **[Chat API](api/CHAT_API_DOCUMENTATION.md)** - Start using the API

### For Integration

1. **[Multi-API Integration](architecture/MULTI_API_INTEGRATION.md)** - 15+ government data sources
2. **[Frontend Integration](development/FRONTEND_INTEGRATION_GUIDE.md)** - Connect your frontend
3. **[Code Examples](examples/)** - Usage examples
4. **[API Reference](api/)** - Complete API documentation

### For Operations

1. **[Railway Guide](deployment/railway/README.md)** - Production deployment
2. **[Monitoring Setup](architecture/MONITORING_OBSERVABILITY.md)** - Observability
3. **[Service Health](deployment/SERVICE_HEALTH_CHECKS.md)** - Health checks
4. **[Troubleshooting](deployment/railway/README.md#-troubleshooting)** - Common issues

---

## 🎯 Recent Updates (2025-10-29)

### ✅ Completed

- **Documentation Reorganization** ⭐ NEW! - Professional structure with 53 archived sessions
- **Investigation Persistence Fix** - Chat investigations now properly saved to PostgreSQL
- **Anita Agent Chat Integration** - Full chat support with payload transformation
- **Debug Endpoint Fix** - Accessible at `/api/v1/debug/database-config`
- **Comprehensive Test Suite** - 7/7 tests passing (100% success rate)
- **Multi-API Integration** - 15+ government data sources with intelligent routing
- **Railway Deployment** - Production-ready with PostgreSQL and Redis
- **Agent Pool Architecture** - Efficient agent management system
- **Performance Optimizations** - Redis caching, connection pooling, lazy loading

### 📊 Current Status

- **APIs Integrated:** 30+ (Federal + State + Municipal)
- **Agents Operational:** 10/16 fully functional (Tier 1), 5/16 substantial framework (Tier 2), 1/16 minimal (Tier 3)
- **Test Coverage:** ~44% backend (Target: 80%)
- **Deployment Platform:** Railway (production since 07/10/2025)
- **Production URL:** https://cidadao-api-production.up.railway.app/
- **Database:** PostgreSQL (Supabase) + Redis (Railway)
- **Cache:** Redis (fully operational)
- **Documentation:** Professionally organized with clear navigation

---

## 📖 Documentation Standards

All documentation follows these standards:

- **Markdown format** with GitHub-flavored syntax
- **Clear headings** and table of contents
- **Code examples** with syntax highlighting
- **Step-by-step guides** for complex tasks
- **Links** to related documentation
- **Author and date** in headers

---

## 🗺️ Navigation Tips

### By Role

**Backend Developer:**
- Start with [Architecture](architecture/)
- Read [Multi-API Integration](architecture/MULTI_API_INTEGRATION.md)
- Check [Development Guides](development/)

**Frontend Developer:**
- Start with [API Documentation](api/)
- Read [Frontend Integration](development/FRONTEND_INTEGRATION_GUIDE.md)
- Check [Examples](examples/)

**DevOps/SRE:**
- Start with [Railway Deployment](deployment/railway/README.md)
- Read [Monitoring Guide](architecture/MONITORING_OBSERVABILITY.md)
- Check [Service Health](deployment/SERVICE_HEALTH_CHECKS.md)

**Product Manager:**
- Start with [Current Status](project/current/CURRENT_STATUS_2025_10.md)
- Read [Quick Status](project/current/QUICK_STATUS.md)
- Check [Planning Docs](project/planning/)

### By Task

**Deploying to Production:**
1. [Railway Guide](deployment/railway/README.md)
2. [Environment Variables](deployment/railway/README.md#-environment-variables)
3. [Troubleshooting](deployment/railway/README.md#-troubleshooting)

**Adding New Data Source:**
1. [Multi-API Integration](architecture/MULTI_API_INTEGRATION.md)
2. [API Planning](planning/apis-governamentais.md)
3. [Code Examples](examples/)

**Understanding the System:**
1. [Current Status](project/current/CURRENT_STATUS_2025_10.md)
2. [Architecture Overview](architecture/MULTI_API_INTEGRATION.md)
3. [Agent System](architecture/AGENT_POOL_ARCHITECTURE.md)

---

## 🤝 Contributing to Documentation

Found a typo? Want to improve a guide?

1. Edit the relevant file in `docs/`
2. Follow the existing structure and standards
3. Add author and date to new files
4. Submit a pull request

---

## 📞 Need Help?

- **Issues**: [GitHub Issues](https://github.com/anderson-ufrj/cidadao.ai-backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/anderson-ufrj/cidadao.ai-backend/discussions)
- **Email**: andersonhs27@gmail.com

---

**Documentation Version**: 4.0 (Professional Organization Complete)
**Last Updated**: 2025-10-29 10:00:00 -03:00
**Author**: Anderson Henrique da Silva

---

## 📊 Organization Statistics

- **Total Documentation Files**: 247 markdown files
- **Archived Session Reports**: 53 documents (October 2025)
- **Active Documentation**: Clean, organized, and navigable
- **Current Status Docs**: 7 key status documents
- **Agent Documentation**: 16 comprehensive agent docs
- **API Documentation**: Complete REST, WebSocket, and Chat API guides
