# 🗺️ Agent Implementation Roadmap

**Author**: Anderson Henrique da Silva
**Created**: October 12, 2025
**Status**: Active Development

---

## 📋 Overview

This document outlines the technical implementation plan for completing the 17-agent system of Cidadão.AI. Currently, 8 agents are fully operational (47%), and 9 require implementation or completion.

---

## 🎯 Current Status

### ✅ Fully Operational (8 agents - 47%)

| Agent | Status | Coverage | Performance | Notes |
|-------|--------|----------|-------------|-------|
| Deodoro | ✅ 100% | Base classes | N/A | Foundation for all agents |
| Abaporu | ✅ 100% | Master orchestrator | 12.5s/investigation | ReAct Pattern implemented |
| Senna | ✅ 100% | Intent routing | <100ms | NLP-based routing |
| Zumbi | ✅ 100% | Anomaly detection | 2.1s, 500 contracts/s | FFT analysis working |
| Anita | ✅ 100% | Data analysis | 1.8s, 600 contracts/s | Statistical methods complete |
| Oxossi | ✅ 100% | Fraud detection | 3.5s, 300 contracts/s | 10 fraud types |
| Tiradentes | ✅ 100% | Report generation | <1s | SHA-256 audit trail |
| Bonifacio | ✅ 100% | Legal validation | <500ms | Law 8.666/93 + 14.133/21 |

### 🔧 Partially Implemented (5 agents - 29%)

| Agent | Status | Missing | Priority | Effort |
|-------|--------|---------|----------|--------|
| Lampião | ⚠️ 95% | Test coverage + edge cases | Medium | 1 week |
| Drummond | ⚠️ 95% | Fix HF import issue | High | 2 days |
| Maria Quitéria | ⚠️ 95% | Advanced audit controls | Medium | 1 week |
| Niemeyer | ⚠️ 40% | Visualization engine | Low | 3 weeks |
| Dandara | ⚠️ 30% | Real data integration | Medium | 2 weeks |

### 🚧 Framework Only (4 agents - 24%)

| Agent | Status | Needs | Priority | Effort |
|-------|--------|-------|----------|--------|
| Ceuci | 🚧 10% | ML models training | High | 4 weeks |
| Obaluaie | 🚧 15% | Algorithm implementation | High | 3 weeks |
| Nana | 🚧 60% | Vector store integration | Medium | 2 weeks |
| Machado | 🚧 70% | NLP sentiment models | Low | 2 weeks |

---

## 🚀 Implementation Phases

### Phase 1: Critical Completions (2 weeks)
**Goal**: Bring partially implemented agents to 100%

#### Week 1: High Priority
- [ ] **Drummond** (2 days)
  - [ ] Refactor MaritacaClient dependency to fix circular import
  - [ ] Uncomment in `__init__.py` for HuggingFace deployment
  - [ ] Add integration tests
  - [ ] Update documentation with working examples

- [ ] **Ceuci** (5 days)
  - [ ] Implement ARIMA/SARIMA time series models
  - [ ] Train Prophet model for seasonality detection
  - [ ] Add LSTM neural network for complex patterns
  - [ ] Create evaluation pipeline (MAE, RMSE, MAPE)
  - [ ] Add real-time prediction API endpoint

#### Week 2: Medium Priority
- [ ] **Lampião** (3 days)
  - [ ] Add comprehensive test coverage (>80%)
  - [ ] Implement edge case handling for missing geographic data
  - [ ] Optimize spatial queries performance
  - [ ] Add caching for expensive calculations

- [ ] **Dandara** (4 days)
  - [ ] Integrate IBGE API for real demographic data
  - [ ] Connect DataSUS for health statistics
  - [ ] Implement INEP education data fetching
  - [ ] Replace simulated data with real calculations
  - [ ] Add data validation and error handling

### Phase 2: Algorithm Implementation (3 weeks)
**Goal**: Implement core algorithms for framework-only agents

#### Week 3-4: Obaluaie (Corruption Detector)
- [ ] **Benford's Law Implementation** (3 days)
  - [ ] Digit frequency analysis algorithm
  - [ ] Statistical significance testing
  - [ ] Visualization of deviations
  - [ ] Integration with contract data

- [ ] **Cartel Detection** (4 days)
  - [ ] Graph construction from supplier networks
  - [ ] Louvain community detection algorithm
  - [ ] Suspicious cluster identification
  - [ ] Network visualization

- [ ] **Money Laundering Detection** (3 days)
  - [ ] Transaction pattern analysis
  - [ ] Structuring detection (smurfing)
  - [ ] Layering complexity scoring
  - [ ] Integration stage identification

- [ ] **Nepotism Analysis** (4 days)
  - [ ] Relationship graph construction
  - [ ] CPF/CNPJ cross-referencing
  - [ ] Family tree detection
  - [ ] Employment pattern analysis

#### Week 5: Nana & Machado
- [ ] **Nana** (Memory Manager) - 5 days
  - [ ] Integrate ChromaDB or Pinecone vector store
  - [ ] Implement embedding generation (sentence-transformers)
  - [ ] Add semantic search capabilities
  - [ ] Create memory consolidation pipeline
  - [ ] Optimize context window management

- [ ] **Machado** (Narrative Analyst) - 5 days
  - [ ] Train sentiment analysis model (Portuguese corpus)
  - [ ] Implement story arc extraction
  - [ ] Add entity relationship mapping
  - [ ] Create narrative summarization
  - [ ] Integrate with Tiradentes for storytelling

### Phase 3: Advanced Features (3 weeks)
**Goal**: Complete remaining features and optimizations

#### Week 6: Maria Quitéria (Security)
- [ ] Implement remaining ISO27001 controls (10 controls)
- [ ] Train ML models for threat detection
- [ ] Integrate SIEM platforms (Splunk/ELK connectors)
- [ ] Add SOAR capabilities for automated response
- [ ] Create threat intelligence feed integration

#### Week 7: Niemeyer (Visualization)
- [ ] Implement chart generation engine (Plotly/Altair)
- [ ] Add geographic map rendering (Folium)
- [ ] Create network graph visualizations (NetworkX + vis.js)
- [ ] Build interactive dashboard framework
- [ ] Integrate with Tiradentes reports

#### Week 8: Integration & Testing
- [ ] Cross-agent integration tests
- [ ] Performance optimization (profiling + caching)
- [ ] Load testing (concurrent users)
- [ ] Security audit
- [ ] Documentation completion

---

## 📊 Technical Requirements by Agent

### Ceuci (Predictive AI)

**ML Models Required**:
```python
models = {
    "arima": "statsmodels.tsa.arima.model.ARIMA",
    "sarima": "statsmodels.tsa.statespace.sarimax.SARIMAX",
    "prophet": "prophet.Prophet",
    "lstm": "tensorflow.keras.layers.LSTM",
    "random_forest": "sklearn.ensemble.RandomForestRegressor",
    "xgboost": "xgboost.XGBRegressor",
    "svr": "sklearn.svm.SVR"
}
```

**Training Pipeline**:
1. Historical data collection (Portal da Transparência, 2015-2024)
2. Feature engineering (time, seasonal, trend)
3. Train/validation/test split (70/15/15)
4. Hyperparameter tuning (GridSearchCV)
5. Ensemble voting (weighted by historical accuracy)
6. Continuous retraining (monthly)

**Dependencies**:
```bash
pip install statsmodels prophet tensorflow xgboost scikit-learn
```

### Obaluaie (Corruption Detector)

**Core Algorithms**:
```python
algorithms = {
    "benford": "scipy.stats + custom digit analysis",
    "cartel_detection": "networkx.community.louvain_communities",
    "money_laundering": "graph analysis + transaction patterns",
    "nepotism": "graph analysis + CPF matching"
}
```

**Data Requirements**:
- Contract values (digit distribution)
- Supplier network (CNPJ relationships)
- Transaction history (money flow)
- Employee/contractor data (CPF, family relationships)

**Dependencies**:
```bash
pip install networkx scipy pandas numpy
```

### Dandara (Social Justice)

**Data Source Integration**:
```python
apis = {
    "ibge": "https://servicodados.ibge.gov.br/api/v3/",
    "datasus": "http://tabnet.datasus.gov.br/cgi/",
    "inep": "http://dados.gov.br/dataset/microdados-do-censo-escolar",
    "mds": "http://aplicacoes.mds.gov.br/",
    "portal_transparencia": "http://api.portaldatransparencia.gov.br/"
}
```

**Metrics Implementation**:
- Gini: Already implemented (numpy-based)
- Atkinson: Already implemented (configurable epsilon)
- Theil: Already implemented (entropy-based)
- Palma: Already implemented (quantile-based)
- Regional Gini: TODO (requires IBGE geographic data)

**Dependencies**:
```bash
pip install requests aiohttp pandas numpy
```

### Nana (Memory Manager)

**Vector Store Options**:
```python
vector_stores = {
    "chromadb": {
        "pros": "Local, fast, simple",
        "cons": "Limited scalability",
        "recommended": True
    },
    "pinecone": {
        "pros": "Cloud, scalable, managed",
        "cons": "Costs, requires API key",
        "recommended": False  # For now
    },
    "weaviate": {
        "pros": "Open-source, GraphQL",
        "cons": "Complex setup",
        "recommended": False
    }
}
```

**Embedding Models**:
```python
embeddings = {
    "sentence_transformers": "all-MiniLM-L6-v2",  # 384 dimensions
    "openai": "text-embedding-ada-002",  # 1536 dimensions (paid)
    "cohere": "embed-multilingual-v3.0"  # Multilingual
}
```

**Dependencies**:
```bash
pip install chromadb sentence-transformers
```

### Machado (Narrative Analyst)

**NLP Models**:
```python
models = {
    "sentiment": "neuralmind/bert-base-portuguese-cased",
    "ner": "pierreguillou/bert-base-cased-pt-lenerbr",
    "summarization": "unicamp-dl/ptt5-base-portuguese-vocab"
}
```

**Narrative Extraction**:
- Story arc detection (setup, conflict, resolution)
- Entity relationship mapping
- Timeline reconstruction
- Sentiment trajectory analysis

**Dependencies**:
```bash
pip install transformers torch spacy
python -m spacy download pt_core_news_lg
```

### Maria Quitéria (Security)

**Advanced Features**:
```python
features = {
    "iso27001_controls": [
        "A.5.1.1", "A.5.1.2",  # ... (10 remaining)
    ],
    "ml_threat_detection": {
        "isolation_forest": "sklearn.ensemble.IsolationForest",
        "one_class_svm": "sklearn.svm.OneClassSVM"
    },
    "siem_integration": {
        "splunk": "splunk-sdk",
        "elk": "elasticsearch"
    }
}
```

**Dependencies**:
```bash
pip install splunk-sdk elasticsearch scikit-learn
```

### Niemeyer (Visualizer)

**Visualization Libraries**:
```python
viz_stack = {
    "charts": "plotly",  # Interactive charts
    "maps": "folium",  # Geographic visualization
    "networks": "pyvis",  # Network graphs
    "dashboards": "streamlit"  # Optional web UI
}
```

**Chart Types**:
- Line charts (time series)
- Bar charts (comparisons)
- Scatter plots (correlations)
- Heatmaps (matrices)
- Choropleth maps (regional data)
- Network graphs (relationships)

**Dependencies**:
```bash
pip install plotly folium pyvis streamlit
```

---

## 🧪 Testing Strategy

### Unit Tests (per agent)
```bash
# Target: >80% coverage per agent
pytest tests/unit/agents/test_{agent_name}.py --cov=src.agents.{agent_name}
```

### Integration Tests
```bash
# Multi-agent workflows
pytest tests/integration/test_agent_collaboration.py
pytest tests/integration/test_investigation_flow.py
```

### Performance Tests
```bash
# Load testing
pytest tests/performance/test_agent_throughput.py
pytest tests/performance/test_concurrent_investigations.py
```

### E2E Tests
```bash
# Full system tests
pytest tests/e2e/test_complete_investigation.py
```

---

## 📦 Deployment Considerations

### Environment Variables Required
```bash
# ML Models
HUGGINGFACE_TOKEN=your_token  # For model downloads

# Data APIs
IBGE_API_KEY=your_key  # If required
DATASUS_API_KEY=your_key  # If required

# Vector Store
CHROMADB_PATH=/data/chromadb  # Persistent storage

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_DASHBOARD_ENABLED=true
```

### Resource Requirements

| Agent | CPU | RAM | Storage | Notes |
|-------|-----|-----|---------|-------|
| Ceuci | 2 cores | 4GB | 500MB | ML models |
| Obaluaie | 1 core | 2GB | 100MB | Graph algorithms |
| Dandara | 1 core | 2GB | 100MB | API calls |
| Nana | 2 cores | 8GB | 10GB | Vector store |
| Machado | 2 cores | 4GB | 500MB | NLP models |
| Maria | 1 core | 2GB | 100MB | Security rules |
| Niemeyer | 1 core | 2GB | 100MB | Visualization |

**Total**: ~10 cores, ~26GB RAM, ~12GB storage

### Scaling Strategy
- Horizontal: Multiple agent instances behind load balancer
- Vertical: Increase resources per agent based on load
- Caching: Redis for expensive computations
- Async: All I/O operations use async/await

---

## 🎯 Success Metrics

### Code Quality
- [ ] Test coverage >80% for all agents
- [ ] Type hints on all public methods
- [ ] Docstrings (Google style) on all classes/methods
- [ ] No critical security vulnerabilities (Bandit scan)
- [ ] Code complexity <10 (Radon)

### Performance
- [ ] Agent response time <5s (p95)
- [ ] API latency <200ms (p95)
- [ ] Investigation completion <15s (complex, 6+ agents)
- [ ] Cache hit rate >80%
- [ ] Concurrent users: 100+ without degradation

### Functionality
- [ ] All 17 agents operational
- [ ] Multi-agent orchestration working
- [ ] Real-time chat streaming
- [ ] Report generation (PDF, HTML, JSON)
- [ ] Integration with Portal da Transparência

---

## 📅 Timeline Summary

| Phase | Duration | Agents | Status |
|-------|----------|--------|--------|
| Phase 1: Critical Completions | 2 weeks | Drummond, Ceuci, Lampião, Dandara | 🔄 In Progress |
| Phase 2: Algorithm Implementation | 3 weeks | Obaluaie, Nana, Machado | ⏳ Pending |
| Phase 3: Advanced Features | 3 weeks | Maria, Niemeyer, Integration | ⏳ Pending |
| **Total** | **8 weeks** | **17 agents** | **47% Complete** |

**Target Completion**: December 8, 2025

---

## 🔗 Related Documentation

- [Multi-Agent Architecture](../architecture/multi-agent-architecture.md) - System design
- [Agent Documentation](../agents/) - Individual agent specs
- [SPRINT_PLAN_REVISED_20251012.md](../../SPRINT_PLAN_REVISED_20251012.md) - Project roadmap
- [ARCHITECTURE_COMPLETE.md](../../../ARCHITECTURE_COMPLETE.md) - Ecosystem architecture

---

**Last Updated**: October 12, 2025
**Status**: Active Development
**Maintained By**: Anderson Henrique da Silva
