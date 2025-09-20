---
title: Cidadão.AI Backend
emoji: 🏛️
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
license: mit
---

# 🏛️ Cidadão.AI - Backend

> **Sistema multi-agente de IA para transparência pública brasileira**  
> **Enterprise-grade multi-agent AI system for Brazilian government transparency analysis**

[![Open Gov](https://img.shields.io/badge/Open-Government-blue.svg)](https://www.opengovpartnership.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Test Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)](./tests)
[![Security](https://img.shields.io/badge/security-A+-brightgreen.svg)](./tests/unit/test_security_middleware.py)

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-20 07:28:07 -03 (São Paulo, Brazil)

## 🚀 Quick Start

### 🎯 **Deployment Options**

**HuggingFace Spaces (Cloud):**
```bash
# Uses simplified app.py for fast cloud deployment
# Automatic deployment via Git push to HuggingFace
# Optimized for minimal dependencies and fast startup
```

**Local Development:**
```bash
# Full-featured version with complete agent system
python -m src.api.app
# OR using uvicorn directly:
uvicorn src.api.app:app --reload --port 8000
```

### 🔑 **Dados Reais vs Demo**

O sistema detecta automaticamente se você tem acesso à API do Portal da Transparência:

- **✅ Com `TRANSPARENCY_API_KEY`**: Análise de **dados reais** de contratos públicos
- **🔄 Sem chave API**: Funciona com **dados demo** para demonstração

📚 **[Documentação completa da integração →](docs/PORTAL_TRANSPARENCIA_INTEGRATION.md)**

## 📊 Test Coverage & Quality

### 🛡️ **Enterprise-Grade Testing**

Our comprehensive test suite ensures reliability and security:

- **Overall Coverage**: ~80% (up from 45%)
- **Security Tests**: 90% coverage
- **1,400+ Test Cases**: Comprehensive scenarios
- **28 Test Modules**: Organized by component

### 📈 **Coverage by Component**

| Component | Coverage | Status |
|-----------|----------|--------|
| 🔐 Security & Auth | ~90% | ✅ Excellent |
| 🤖 Multi-Agent System | ~85% | ✅ Very Good |
| 📊 ML Pipeline | ~85% | ✅ Very Good |
| 🌐 API Endpoints | ~90% | ✅ Excellent |
| 💾 Infrastructure | ~80% | ✅ Good |
| 🧠 Memory Systems | ~90% | ✅ Excellent |

### 🧪 **Test Categories**

- **Unit Tests**: Component isolation testing
- **Integration Tests**: API and service integration
- **E2E Tests**: Complete workflow validation
- **Security Tests**: Vulnerability and attack prevention
- **Performance Tests**: Load and stress testing foundations

## 🏗️ Architecture

### 🤖 **Multi-Agent System**

**Status**: 8 agents fully operational, 7 partially implemented, 16/17 total

#### ✅ **Fully Operational Agents**:
- **🎯 Abaporu** (Master): Investigation orchestrator and coordinator
- **🔍 Zumbi dos Palmares** (Investigator): Advanced anomaly detection with FFT
- **📊 Anita Garibaldi** (Analyst): Pattern analysis and trend detection
- **📝 Tiradentes** (Reporter): Multi-format adaptive report generation
- **🧠 Nanã** (Memory): Episodic, semantic and conversational memory
- **🏎️ Ayrton Senna** (Router): Semantic routing with intent detection
- **📚 Machado de Assis** (Textual): Document analysis with NER and compliance
- **⚖️ Dandara** (Social Justice): Equity analysis with social coefficients

#### ⚠️ **In Development** (7 agents):
- José Bonifácio (Policy Analyst), Carlos Drummond (Communication)
- Maria Quitéria (Security), Oscar Niemeyer (Visualization)
- Ceuci (ETL), Obaluaiê (Health), Lampião (Regional)

### 💬 **Chat & Real-time Features**

- **Conversational Interface**: Natural language chat in Portuguese
- **Intent Detection**: 7 intent types with entity extraction
- **SSE Streaming**: Real-time response streaming
- **WebSocket**: Bidirectional communication
- **Smart Caching**: Redis cache for frequent responses
- **Cursor Pagination**: Efficient message history
- **Gzip Compression**: 70-90% bandwidth reduction

### 🔒 **Security Features**

- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Multi-window protection
- **Attack Prevention**: SQL injection, XSS, CSRF protection
- **Audit Trail**: Complete activity logging
- **Secret Management**: HashiCorp Vault integration

### 📊 **ML Capabilities**

- **Anomaly Detection**: Statistical and ML-based methods
- **Spectral Analysis**: Frequency-domain pattern detection
- **Pattern Recognition**: Temporal and behavioral analysis
- **Ensemble Methods**: Combined detection strategies
- **Explainable AI**: Transparent decision-making

### 💾 **Infrastructure**

- **Multi-Level Cache**: L1 (Memory) → L2 (Redis) → L3 (Disk)
- **Database**: PostgreSQL with async SQLAlchemy
- **Message Queue**: Event-driven architecture
- **Monitoring**: Prometheus + Grafana integration
- **Circuit Breakers**: Fault tolerance patterns

### 🚄 **Performance Optimizations** (NEW!)

- **JSON Serialization**: orjson for 3x faster processing
- **Compression**: Brotli + Gzip with smart content detection
- **Connection Pooling**: HTTP/2 multiplexing for LLM providers
- **Agent Pooling**: Pre-warmed instances with lifecycle management
- **Parallel Processing**: Async agent execution strategies
- **Batch Operations**: Bulk API endpoints for efficiency
- **Query Optimization**: Smart indexes and materialized views
- **GraphQL API**: Flexible data fetching with Strawberry
- **WebSocket Batching**: Message aggregation with compression
- **CQRS Pattern**: Separated read/write models

### 📊 **Observability & Monitoring** (NEW!)

- **Health Checks**: Comprehensive dependency monitoring
- **SLA/SLO Tracking**: Error budgets and compliance alerts
- **Distributed Tracing**: OpenTelemetry integration
- **Structured Logging**: JSON format with correlation IDs
- **Business Metrics**: Custom Prometheus metrics
- **Grafana Dashboards**: System and agent performance views
- **Alert Rules**: 25+ Prometheus rules for proactive monitoring
- **APM Integration**: Hooks for New Relic, Datadog, Elastic
- **Chaos Engineering**: Controlled failure injection endpoints

## 🔧 Development

### Prerequisites

```bash
# Python 3.11+
python --version

# PostgreSQL
psql --version

# Redis (optional, for caching)
redis-server --version
```

### Installation

```bash
# Clone repository
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

### Environment Variables

```bash
# Copy example environment
cp .env.example .env

# Edit with your configurations
# Key variables:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cidadaoai
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
TRANSPARENCY_API_KEY=your-api-key  # Optional
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific categories
make test-unit
make test-integration
make test-security

# Run specific test file
pytest tests/unit/test_auth.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make type-check

# All checks
make check
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

```bash
# Health Check
GET /health
GET /health/metrics

# Authentication
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout

# Chat (NEW!)
POST /api/v1/chat/message              # Send message
POST /api/v1/chat/stream               # Stream response (SSE)
GET  /api/v1/chat/suggestions          # Quick actions
GET  /api/v1/chat/history/{session_id} # Get history
GET  /api/v1/chat/history/{session_id}/paginated # Cursor pagination
DELETE /api/v1/chat/history/{session_id} # Clear history
GET  /api/v1/chat/cache/stats          # Cache statistics
GET  /api/v1/chat/agents               # List agents

# WebSocket (NEW!)
WS   /api/v1/ws/chat/{session_id}     # Real-time chat
WS   /api/v1/ws/investigations/{id}   # Investigation updates

# Investigations
POST /api/v1/investigations
GET  /api/v1/investigations/{id}
GET  /api/v1/investigations

# Analysis
POST /api/v1/analysis/contracts
POST /api/v1/analysis/spending-patterns
POST /api/v1/analysis/vendor-concentration

# Reports
POST /api/v1/reports/investigation/{id}
GET  /api/v1/reports/investigation/{id}/export

# Batch Operations (NEW!)
POST /api/v1/batch/investigations      # Bulk create investigations
POST /api/v1/batch/contracts/analyze  # Bulk contract analysis
POST /api/v1/batch/reports/generate    # Bulk report generation

# GraphQL (NEW!)
POST /graphql                          # GraphQL endpoint
GET  /graphql                          # GraphQL playground

# Monitoring (NEW!)
GET  /api/v1/monitoring/health/detailed
GET  /api/v1/monitoring/slo            # SLO compliance status
POST /api/v1/monitoring/slo/metric     # Record SLO metric
GET  /api/v1/monitoring/alerts/violations
GET  /api/v1/monitoring/dashboard/summary

# Observability (NEW!)
GET  /api/v1/observability/traces      # Distributed traces
GET  /api/v1/observability/metrics/custom
GET  /api/v1/observability/logs/structured
GET  /api/v1/observability/correlation/{id}

# Chaos Engineering (NEW!)
GET  /api/v1/chaos/status              # Chaos experiments status
POST /api/v1/chaos/inject/latency      # Inject latency
POST /api/v1/chaos/inject/errors       # Inject errors
POST /api/v1/chaos/stop/{experiment}   # Stop experiment
```

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t cidadao-ai-backend .

# Run container
docker run -p 8000:8000 --env-file .env cidadao-ai-backend
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# With monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### HuggingFace Spaces

```bash
# Deploy to HuggingFace Spaces
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/cidadao-ai-backend
git push huggingface main
```

## 📊 Monitoring

### Prometheus Metrics

Available at `/health/metrics`:

- Request count and duration
- Agent task execution metrics
- Anomaly detection counts
- Cache hit rates
- System resources

### Grafana Dashboards

Pre-configured dashboards for:
- System Overview
- Agent Performance
- API Metrics
- Security Events

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for new features
4. Ensure tests pass (`make test`)
5. Commit changes (`git commit -m 'feat: add amazing feature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: New feature
- `fix`: Bug fix
- `test`: Test additions or fixes
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Portal da Transparência for public data access
- Brazilian open government initiatives
- Open source community

## 📞 Contact

- **Project Lead**: Anderson Henrique
- **GitHub**: [anderson-ufrj](https://github.com/anderson-ufrj)
- **Issues**: [GitHub Issues](https://github.com/anderson-ufrj/cidadao.ai-backend/issues)

---

<div align="center">
  <strong>🇧🇷 Made with ❤️ for Brazilian transparency and accountability 🇧🇷</strong>
</div>