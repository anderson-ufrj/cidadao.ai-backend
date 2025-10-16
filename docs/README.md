# 📚 Cidadão.AI Backend - Documentation

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-16 16:55:00 -03:00

---

> **Comprehensive documentation for the Cidadão.AI multi-agent transparency platform**

---

## 🗂️ Documentation Structure

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

### 📊 [Planning](planning/)

Project planning and roadmaps.

- **[2025 Production Roadmap](planning/ROADMAP_PRODUCAO_2025.md)** - Strategic planning
- **[Government APIs](planning/apis-governamentais.md)** - Available data sources
- **[Agent Status 2025](planning/AGENT_STATUS_2025.md)** - Agent implementation status
- **[Sprint History](planning/SPRINT_HISTORY.md)** - Development history
- **[API Data Structures](planning/API_DATA_STRUCTURES.md)** - Schema definitions

### 📝 [Reports](reports/)

Status reports and milestones.

#### 2025-10 (October)
- **[Current State](reports/2025-10/CURRENT_STATE_2025-10-16.md)** - Latest status
- **[Deployment Success](reports/2025-10/DEPLOYMENT_SUCCESS_2025-10-16.md)** - Railway deployment
- **[Migration Complete](reports/2025-10/MIGRATION_SUPABASE_TO_RAILWAY_COMPLETE.md)** - Migration story
- **[Status October 13](reports/2025-10/STATUS_2025_10_13.md)** - Mid-month status

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

- **[Supabase Errors](troubleshooting/supabase-errors.md)** - Database troubleshooting
- **[Railway Issues](deployment/railway/README.md#-troubleshooting)** - Deployment problems
- **[Common Issues](troubleshooting/common-issues.md)** - General problems

---

## 🚀 Quick Start Guides

### For New Developers

1. **[Railway Deployment](deployment/railway/README.md)** - Deploy to production
2. **[Setup Guide](setup/supabase-quick-start.md)** - Configure local environment
3. **[Architecture Overview](architecture/MULTI_API_INTEGRATION.md)** - Understand the system
4. **[Chat API](api/CHAT_API_DOCUMENTATION.md)** - Start using the API

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

## 🎯 Recent Updates (2025-10-16)

### ✅ Completed

- **Multi-API Integration** - 15+ government data sources with intelligent routing
- **Railway Deployment** - Production-ready with PostgreSQL and Redis
- **Documentation Reorganization** - Cleaner, more organized structure
- **Agent Pool Architecture** - Efficient agent management system
- **Performance Optimizations** - Redis caching, connection pooling, lazy loading

### 📊 Current Status

- **APIs Integrated:** 15+ (Federal + State)
- **Agents Operational:** 8/17 fully functional
- **Test Coverage:** 80% backend
- **Deployment Platform:** Railway (production)
- **Database:** PostgreSQL with migrations
- **Cache:** Redis (fully operational)

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
- Start with [Current State](reports/2025-10/CURRENT_STATE_2025-10-16.md)
- Read [Roadmap](planning/ROADMAP_PRODUCAO_2025.md)
- Check [Agent Status](planning/AGENT_STATUS_2025.md)

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
1. [Architecture Overview](architecture/MULTI_API_INTEGRATION.md)
2. [Agent System](architecture/AGENT_POOL_ARCHITECTURE.md)
3. [Current State Report](reports/2025-10/CURRENT_STATE_2025-10-16.md)

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

**Documentation Version**: 3.0 (Post-Reorganization)
**Last Updated**: 2025-10-16 16:55:00 -03:00
**Author**: Anderson Henrique da Silva
