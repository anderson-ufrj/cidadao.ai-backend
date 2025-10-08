# 📚 Cidadão.AI Backend - Documentation

> **Comprehensive documentation for the Cidadão.AI multi-agent transparency platform**

---

## 🗂️ Documentation Structure

### 🚀 [Deployment](deployment/)

Production deployment guides for different platforms.

- **[Railway Deployment](deployment/railway.md)** ⭐ - Primary production platform
- **[HF→Railway Migration](deployment/migration-hf-to-railway.md)** - Why and how we migrated
- **[Docker Deployment](deployment/docker.md)** - Container-based deployment

### ⚙️ [Setup](setup/)

Configuration guides for system components.

- **[Supabase Setup](setup/supabase-setup.md)** - PostgreSQL database configuration
- **[Supabase Integration](setup/supabase-integration.md)** - Complete integration guide
- **[Supabase Quick Start](setup/supabase-quick-start.md)** - Fast setup for development
- **[Supabase Testing](setup/supabase-testing.md)** - Testing database integration
- **[Alerts Setup](setup/alerts.md)** - Webhook notifications (Discord, Slack)
- **[Token Configuration](setup/tokens.md)** - Environment variables guide

### 🏗️ [Architecture](architecture/)

System design and technical architecture.

- **[Auto-Investigation System](architecture/auto-investigation-system.md)** - 24/7 autonomous monitoring
- **[Agent System](architecture/AGENT_SYSTEM.md)** - Multi-agent collaboration
- **[Celery Architecture](architecture/CELERY_ARCHITECTURE.md)** - Task queue system
- **[Database Schema](architecture/DATABASE_SCHEMA.md)** - Data models

### 🤖 [Agents](agents/)

Documentation for each AI agent.

- **[Abaporu](agents/abaporu.md)** - Master Orchestrator
- **[Zumbi](agents/zumbi.md)** - Anomaly Detective
- **[Anita](agents/anita.md)** - Data Analyst
- **[Tiradentes](agents/tiradentes.md)** - Report Writer
- **[Lampião](agents/lampiao.md)** - IBGE Data Integrator
- *[See full list...](agents/)*

### 🌐 [API](api/)

API documentation and integration guides.

- **[REST API Endpoints](api/ENDPOINTS_CONNECTION_STATUS.md)** - Complete endpoint reference
- **[Chat API](api/CHAT_API_DOCUMENTATION.md)** - Conversational interface
- **[WebSocket API](api/WEBSOCKET_API_DOCUMENTATION.md)** - Real-time communication
- **[Backend Chat Implementation](api/BACKEND_CHAT_IMPLEMENTATION.md)** - Implementation details
- **[Supabase REST](api/supabase-rest.md)** - Database REST API
- **[Portal da Transparência](api/PORTAL_TRANSPARENCIA_INTEGRATION.md)** - Government API integration

### 💻 [Development](development/)

Guides for developers working on the project.

- **[Conversational AI](development/CONVERSATIONAL_AI_IMPLEMENTATION.md)** - Chat system
- **[CORS Configuration](development/CORS_CONFIGURATION.md)** - Cross-origin setup
- **[Cursor Pagination](development/CURSOR_PAGINATION_IMPLEMENTATION.md)** - Efficient pagination
- **[Frontend Integration](development/FRONTEND_INTEGRATION_GUIDE.md)** - Frontend connection guide

### 📝 [Examples](examples/)

Code examples and usage demos.

- **[Agent Usage](examples/agent_dados_gov_usage.py)** - Using agents programmatically
- **[Chat Demo](examples/chat_dados_gov_demo.py)** - Chat API example
- **[Frontend Integration](examples/frontend_integration.tsx)** - React/Next.js example
- **[Maritaca Integration](examples/integrations/maritaca_drummond_integration.py)** - LLM integration

### 🛠️ [Project](project/)

Project management and internal documentation.

- **[CHANGELOG](project/CHANGELOG.md)** - Version history
- **[PRIVACY](project/PRIVACY.md)** - Privacy policy
- **[Planning](project/planning/)** - Sprint planning and roadmap
  - [Agent Status 2025](project/planning/AGENT_STATUS_2025.md)
  - [Sprint History](project/planning/SPRINT_HISTORY.md)
  - [API Data Structures](project/planning/API_DATA_STRUCTURES.md)
- **[Reports](project/reports/)** - Technical reports
  - [Test Summary](project/reports/TEST_SUMMARY.md)
  - [Implementation Status](project/reports/REAL_IMPLEMENTATION_STATUS.md)
- **[Reorganization](project/REORGANIZATION_SUMMARY.md)** - Repository cleanup history

### 🐛 [Troubleshooting](troubleshooting/)

Common issues and solutions.

- **[Supabase Errors](troubleshooting/supabase-errors.md)** - Database troubleshooting
- **[Common Issues](troubleshooting/common-issues.md)** - General problems (coming soon)

---

## 🚀 Quick Links

### Getting Started

1. **[Railway Deployment Guide](deployment/railway.md)** - Deploy to production
2. **[Supabase Quick Start](setup/supabase-quick-start.md)** - Setup database
3. **[Token Configuration](setup/tokens.md)** - Configure environment variables
4. **[Chat API](api/CHAT_API_DOCUMENTATION.md)** - Start using the API

### Understanding the System

1. **[Migration Story](deployment/migration-hf-to-railway.md)** - Why Railway?
2. **[Architecture](architecture/auto-investigation-system.md)** - How it works
3. **[Agent System](architecture/AGENT_SYSTEM.md)** - Multi-agent collaboration
4. **[Celery Architecture](architecture/CELERY_ARCHITECTURE.md)** - Task queue

### Development

1. **[Frontend Integration](development/FRONTEND_INTEGRATION_GUIDE.md)** - Connect frontend
2. **[Code Examples](examples/)** - Usage examples
3. **[API Reference](api/)** - Complete API docs

---

## 📖 Documentation Standards

All documentation follows these standards:

- **Markdown format** with GitHub-flavored syntax
- **Clear headings** and table of contents
- **Code examples** with syntax highlighting
- **Step-by-step guides** for complex tasks
- **Links** to related documentation
- **Emoji** for visual organization (sparingly)

---

## 🤝 Contributing to Documentation

Found a typo? Want to improve a guide?

1. Edit the relevant file in `docs/`
2. Follow the existing structure
3. Submit a pull request

---

## 📞 Need Help?

- **Issues**: [GitHub Issues](https://github.com/anderson-ufrj/cidadao.ai-backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/anderson-ufrj/cidadao.ai-backend/discussions)
- **Email**: andersonhs27@gmail.com

---

**Last Updated**: 2025-10-07
**Documentation Version**: 2.0 (Post-Railway Migration)
