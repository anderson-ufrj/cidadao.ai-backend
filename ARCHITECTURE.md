# Cidadão.AI Backend Architecture

## 🏗️ Repository Structure

This repository contains **only the backend API** components of the Cidadão.AI system, following a clean separation of concerns.

### 📁 Backend Structure

```
cidadao.ai-backend/
├── src/                           # Core backend source code
│   ├── api/                      # FastAPI application
│   │   ├── app.py               # Main FastAPI app
│   │   ├── routes/              # API endpoints
│   │   ├── middleware/          # Authentication, logging, security
│   │   └── websocket.py         # Real-time communication
│   ├── agents/                   # Multi-agent AI system
│   │   ├── master_agent.py      # Orchestration agent
│   │   ├── investigator_agent.py # Anomaly detection
│   │   ├── analyst_agent.py     # Financial analysis
│   │   ├── reporter_agent.py    # Report generation
│   │   └── semantic_router.py   # Query routing
│   ├── ml/                       # Machine learning pipeline
│   │   ├── models.py            # ML models
│   │   ├── anomaly_detector.py  # Anomaly detection
│   │   └── training_pipeline.py # Training workflows
│   ├── services/                 # Business logic services
│   ├── tools/                    # Transparency API integration
│   ├── memory/                   # Agent memory systems
│   ├── infrastructure/           # System infrastructure
│   └── core/                     # Configuration and utilities
├── deployment/                   # Container orchestration
│   ├── Dockerfile.api           # API container
│   ├── Dockerfile.ml            # ML services container  
│   ├── Dockerfile.worker        # Background workers
│   ├── docker-compose.yml       # Full stack orchestration
│   └── kubernetes/              # K8s deployment configs
├── tests/                        # Comprehensive test suite
├── apps/                         # Backend applications
│   └── api_app.py               # FastAPI application entry point
├── requirements/                 # Dependencies
├── scripts/                      # Deployment and utility scripts
└── Dockerfile                    # Main API container
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /api/v1/status` - System status
- `POST /api/v1/classify` - Text classification
- `POST /api/v1/analyze` - Data analysis
- `GET /api/v1/reports/{id}` - Report retrieval
- `WebSocket /ws` - Real-time updates

### Multi-Agent Endpoints
- `POST /api/v1/agents/investigate` - Investigation analysis
- `POST /api/v1/agents/analyze` - Financial analysis
- `GET /api/v1/agents/memory` - Memory system access

### Administrative
- `GET /api/v1/metrics` - System metrics
- `POST /api/v1/audit` - Audit logging
- `GET /docs` - API documentation (Swagger)

## 🚀 Deployment Options

### Docker Compose (Recommended)
```bash
# Full backend stack
docker-compose up -d

# Development mode
docker-compose -f docker-compose.dev.yml up
```

### Kubernetes
```bash
# Deploy to K8s cluster
kubectl apply -f deployment/kubernetes/
```

### Standalone API
```bash
# Build and run API container
docker build -t cidadao-api .
docker run -p 8000:8000 cidadao-api
```

## 🔗 Frontend Integration

The backend provides REST API endpoints consumed by the separate frontend repository:

- **Frontend Repository**: `https://github.com/anderson-ufrj/cidadao.ai-frontend`
- **API Base URL**: `https://your-backend-api.com/api/v1`
- **WebSocket URL**: `wss://your-backend-api.com/ws`

### Frontend Applications
- **Gradio Interface**: Professional multi-page UI
- **Streamlit Dashboard**: Data visualization and analytics
- **Documentation Site**: Technical documentation and blog

## 🛡️ Security Features

- JWT-based authentication
- Rate limiting per endpoint
- CORS configuration
- Input validation with Pydantic
- Security headers and middleware
- Audit logging and monitoring

## 📊 Infrastructure Services

### Required Services
- **PostgreSQL**: Primary database
- **Redis**: Caching and message queue
- **ChromaDB**: Vector database for embeddings

### Optional Services  
- **Elasticsearch**: Advanced search capabilities
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## 🧠 Multi-Agent System

### Agent Architecture
- **MasterAgent**: Coordinates all other agents
- **InvestigatorAgent**: Detects anomalies in public data
- **AnalystAgent**: Performs financial analysis
- **ReporterAgent**: Generates structured reports
- **MemoryAgent**: Manages episodic and semantic memory

### Communication
- Async message passing via Redis
- Shared memory with ChromaDB
- WebSocket real-time updates to frontend

## 📈 Performance Characteristics

- **API Response Time**: <180ms average
- **Concurrent Users**: 100+ supported
- **Database**: Optimized queries with indexing
- **Caching**: Redis-based response caching
- **Memory Usage**: Efficient connection pooling

## 🔄 Development Workflow

### Local Development
```bash
# Install dependencies
pip install -r requirements/base.txt

# Run API server
python -m uvicorn src.api.app:app --reload

# Run tests
pytest tests/

# Code quality
black src/ tests/
ruff check src/ tests/
```

### Docker Development
```bash
# Build development environment
make docker-dev

# Run with hot reload
make run-dev
```

This architecture enables independent scaling, deployment, and development of backend services while maintaining clean separation from frontend components.