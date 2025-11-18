# 🎓 Onboarding Guide - Cidadão.AI Backend

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brazil
**Created**: 2025-11-18
**Last Updated**: 2025-11-18
**Version**: 1.0.0-beta

---

## 🎯 Welcome!

This is your **numbered guide** to getting started with Cidadão.AI Backend. Follow the documents in order for the best learning experience.

**Total Time**: 3-6 hours (depending on your role and depth)

---

## 🚀 Quick Start Path (30-60 min)

**Perfect for**: First-time contributors, evaluators, product managers

### 1️⃣ [README.md](README.md) - Project Overview
**Time**: 10 min | **Why**: Understand what Cidadão.AI is and its core features

**You'll learn**:
- What is Cidadão.AI and its mission
- Production status (99.9% uptime, 16 agents operational)
- Key metrics (76.29% test coverage, 1,084 commits)
- Complete ecosystem (4 repositories)
- Quick start installation

**Next**: If you want to try it immediately → Go to **#2**

---

### 2️⃣ [QUICKSTART.md](QUICKSTART.md) - Get Running in 5 Minutes
**Time**: 5-10 min | **Why**: Get the backend running on your machine

**You'll do**:
- Install dependencies (`pip install -r requirements.txt`)
- Configure environment variables (.env setup)
- Start development server
- Access Swagger UI at http://localhost:8000/docs

**Next**: Want to understand the documentation structure → Go to **#3**

---

### 3️⃣ [docs/INDEX.md](docs/INDEX.md) - Documentation Navigator
**Time**: 10 min | **Why**: Learn where everything is documented

**You'll discover**:
- How documentation is organized (17 categories)
- Quick links by role (Developer, DevOps, PM, QA)
- 100+ documents indexed
- Where to find specific information

**Next**: Ready to understand the system → Go to **Path 2**

---

## 🏗️ Understanding the System (2-3 hours)

**Perfect for**: Developers, architects, technical contributors

### 4️⃣ [docs/architecture/multi-agent-architecture.md](docs/architecture/multi-agent-architecture.md) - System Design
**Time**: 30-45 min | **Why**: Understand how the multi-agent system works

**You'll learn**:
- Orchestration flow (User → Intent → Agents → Results)
- 7 Mermaid architecture diagrams
- Query planning and execution
- Data federation pattern
- Entity graph with NetworkX
- Circuit breakers and resilience

**Key Concepts**:
- **Orchestrator**: Coordinates agent execution
- **Reflection Pattern**: Agents self-improve quality
- **Agent Pool**: Lazy loading for 367x faster startup
- **Data Federation**: Parallel API calls with fallbacks

**Next**: Want to understand agents in depth → Go to **#5**

---

### 5️⃣ [docs/agents/README.md](docs/agents/README.md) - Agent System Overview
**Time**: 20-30 min | **Why**: Learn about all 16 AI agents

**You'll learn**:
- Agent tier classification (Tier 1: Excellent, Tier 2: Near-complete, Tier 3: Framework)
- Each agent's specialization and capabilities
- Test coverage by agent (ranging from 81% to 96%)
- How agents communicate and coordinate

**Agent Tiers**:
- **Tier 1** (10 agents): >75% coverage, production-ready
- **Tier 2** (5 agents): 81-85% coverage, minor work needed
- **Tier 3** (1 agent): Framework complete, API integration pending

**Next**: Want to see a reference implementation → Go to **#6**

---

### 6️⃣ [docs/agents/zumbi.md](docs/agents/zumbi.md) - Best Agent Example
**Time**: 20-30 min | **Why**: Study the most complete agent implementation

**You'll learn**:
- How to implement a ReflectiveAgent
- Anomaly detection algorithms (FFT, Z-score, IQR)
- Quality threshold and reflection pattern
- Test coverage best practices (96.32%)
- Error handling and retry logic

**Why Zumbi?**:
- Highest test coverage (96.32%)
- Most mature implementation
- Complete documentation
- Good example of reflection pattern

**Next**: Want to understand the API → Go to **#7**

---

### 7️⃣ [docs/api/INDEX.md](docs/api/INDEX.md) - API Catalog
**Time**: 20-30 min | **Why**: Explore 266+ endpoints and integrations

**You'll learn**:
- REST API structure and endpoints
- 30+ government APIs integrated
- Authentication and security
- Real-time features (SSE streaming)
- GraphQL implementation status

**Key Sections**:
- **Core API**: Agents, investigations, chat
- **Federal APIs**: IBGE, DataSUS, PNCP, Portal da Transparência
- **State APIs**: TCE-CE, TCE-PE, TCE-MG
- **Real-time**: SSE + WebSocket

**Next**: Ready to contribute → Go to **Path 3**

---

## 🤝 Contributing Path (1-2 hours)

**Perfect for**: Contributors, developers ready to code

### 8️⃣ [CONTRIBUTING.md](CONTRIBUTING.md) - How to Contribute
**Time**: 15-20 min | **Why**: Learn the contribution process and standards

**You'll learn**:
- Code style and conventions (Black, Ruff, MyPy)
- Commit message format (conventional commits)
- Pull request process
- Testing requirements (80% coverage)
- Pre-commit hooks setup

**Standards**:
- **Formatter**: Black (88 char line)
- **Linter**: Ruff (strict mode)
- **Type Checker**: MyPy (strict, all functions typed)
- **Test Coverage**: Minimum 80%

**Next**: Want to deploy to production → Go to **#9**

---

### 9️⃣ [docs/deployment/railway/README.md](docs/deployment/railway/README.md) - Production Deployment
**Time**: 20-30 min | **Why**: Understand production infrastructure

**You'll learn**:
- Railway deployment setup
- PostgreSQL and Redis configuration
- Environment variables management
- Monitoring with Prometheus + Grafana
- Smoke testing production

**Production Stack**:
- **Platform**: Railway
- **Database**: PostgreSQL (managed)
- **Cache**: Redis (managed)
- **Monitoring**: Prometheus + Grafana
- **Uptime**: 99.9% since October 7, 2025

**Next**: Want to see the roadmap → Go to **#10**

---

### 🔟 [docs/project/ROADMAP_OFFICIAL_2025.md](docs/project/ROADMAP_OFFICIAL_2025.md) - Future Plans
**Time**: 15-20 min | **Why**: Understand where the project is going

**You'll learn**:
- V1.0 launch plan (November 30, 2025)
- V1.1 features (December 2025): OAuth, WebSocket, load testing
- V2.0 vision (Q1 2026): ML models, predictive analytics
- Long-term roadmap through 2026

**Timeline**:
- **V1.0** (Nov 2025): Production beta launch
- **V1.1** (Dec 2025): OAuth, WebSocket, performance optimization
- **V2.0** (Q1 2026): ML models, advanced analytics, multi-tenancy

**You're now ready to contribute!** 🎉

---

## 🎓 Advanced Topics (Optional, 2-4 hours)

**Perfect for**: Deep dives, specialized topics

### 1️⃣1️⃣ [docs/architecture/IMPROVEMENT_ROADMAP_2025.md](docs/architecture/IMPROVEMENT_ROADMAP_2025.md) - Technical Improvements
**Time**: 20-30 min

**Topics**: 15 planned technical features, optimization strategies, scaling approach

---

### 1️⃣2️⃣ [docs/api/STREAMING_IMPLEMENTATION.md](docs/api/STREAMING_IMPLEMENTATION.md) - Real-Time Features
**Time**: 20-30 min

**Topics**: SSE implementation, WebSocket setup, real-time chat, event streaming

---

### 1️⃣3️⃣ [docs/project/STATUS_ATUAL_2025_11_14.md](docs/project/STATUS_ATUAL_2025_11_14.md) - Current Status
**Time**: 15-20 min

**Topics**: Detailed agent status, test coverage analysis, production metrics

---

### 1️⃣4️⃣ [docs/reports/2025-11/PRODUCTION_READY_V1_0_2025_11_18.md](docs/reports/2025-11/PRODUCTION_READY_V1_0_2025_11_18.md) - V1.0 Validation
**Time**: 30-40 min

**Topics**: Production readiness validation, must-have criteria (9/9 met), E2E test results

---

### 1️⃣5️⃣ [docs/reports/2025-11/PERFORMANCE_REVIEW_2025_11_18.md](docs/reports/2025-11/PERFORMANCE_REVIEW_2025_11_18.md) - Performance Analysis
**Time**: 20-30 min

**Topics**: Response time benchmarks, lazy loading (367x improvement), caching strategy

---

## 🎯 Learning Paths by Role

### 👨‍💻 Developer
**Recommended order**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

**Focus**: Understand architecture, agents, and contribution process

**Time**: 3-4 hours

---

### 🔧 DevOps Engineer
**Recommended order**: 1 → 2 → 3 → 9 → 14 → 15

**Focus**: Deployment, monitoring, performance

**Time**: 2-3 hours

---

### 📊 Product Manager
**Recommended order**: 1 → 3 → 5 → 10 → 13 → 14

**Focus**: Features, roadmap, current status

**Time**: 2-3 hours

---

### 🧪 QA / Tester
**Recommended order**: 1 → 2 → 3 → 8 → 14

**Focus**: Testing strategy, E2E validation, quality standards

**Time**: 2-3 hours

---

### 🎨 UI/UX Designer
**Recommended order**: 1 → 3 → 5 → 7

**Focus**: Agent capabilities, API features, user experience

**Time**: 1-2 hours

---

## 💡 Pro Tips

### For Developers

1. **Start with Zumbi** (#6) - Best reference implementation
2. **Run tests often** - `JWT_SECRET_KEY=test SECRET_KEY=test make test`
3. **Use make commands** - `make check` before every commit
4. **Follow the reflection pattern** - Agents self-improve quality

### For DevOps

1. **Check health regularly** - `/health/metrics` for Prometheus
2. **Monitor Railway dashboard** - PostgreSQL and Redis metrics
3. **Review Grafana** - Local dashboards for development
4. **Run smoke tests** - `scripts/deployment/quick_smoke_test.sh`

### For Product Managers

1. **Check roadmap weekly** - Plans evolve based on feedback
2. **Review test results** - E2E validation shows feature readiness
3. **Monitor production metrics** - 99.9% uptime, 0.6s avg response
4. **User feedback loop** - Inform agent improvements

---

## 📚 Additional Resources

### Documentation
- **Main Index**: [docs/INDEX.md](docs/INDEX.md)
- **Agent Docs**: [docs/agents/](docs/agents/)
- **API Docs**: [docs/api/](docs/api/)
- **Architecture**: [docs/architecture/](docs/architecture/)

### Production
- **API**: https://cidadao-api-production.up.railway.app
- **Swagger**: https://cidadao-api-production.up.railway.app/docs
- **Health**: https://cidadao-api-production.up.railway.app/health

### Community
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: https://github.com/anderson-ufrj/cidadao.ai-backend/issues
- **Discussions**: https://github.com/anderson-ufrj/cidadao.ai-backend/discussions

---

## ❓ Need Help?

### Can't find what you need?

1. **Search**: Use GitHub search or `grep -r "keyword" docs/`
2. **Index**: Check [docs/INDEX.md](docs/INDEX.md) for comprehensive navigation
3. **README**: [README.md](README.md) for quick reference
4. **Issues**: Open an issue if documentation is unclear

### Found a problem?

- **Documentation issue**: Open PR to fix it
- **Code issue**: Create GitHub issue with details
- **Question**: Use GitHub Discussions

---

## 🎉 You're Ready!

After completing the appropriate path for your role, you should be able to:

✅ Understand the multi-agent architecture
✅ Run the backend locally
✅ Navigate the codebase confidently
✅ Contribute code following standards
✅ Deploy to production (DevOps)
✅ Understand the roadmap (PM)

**Welcome to Cidadão.AI!** 🇧🇷

We're democratizing government transparency through AI, one agent at a time.

---

**Questions?** Open an issue or discussion on GitHub!

**Ready to contribute?** Check [CONTRIBUTING.md](CONTRIBUTING.md) and pick an issue!

---

🇧🇷 **Made with ❤️ in Minas Gerais, Brazil**

🚀 **Democratizing Government Transparency Through AI**
