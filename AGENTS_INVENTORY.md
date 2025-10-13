# Cidadão.AI - Agents Inventory & Activation Guide

**Date**: 2025-10-13
**Status**: Agent Activation Project

---

## 🤖 Agents Status Overview

### Active Agents (9/17)

| Agent | Status | Endpoint | Capabilities |
|-------|--------|----------|--------------|
| **Zumbi dos Palmares** | ✅ Active | `/agents/zumbi` | Anomaly Detection, Price Analysis, Vendor Concentration |
| **Anita Garibaldi** | ✅ Active | `/agents/anita` | Pattern Analysis, Trend Detection, Correlation |
| **Tiradentes** | ✅ Active | `/agents/tiradentes` | Report Generation, Natural Language, Documentation |
| **José Bonifácio** | ✅ Active | `/agents/bonifacio` | Legal Analysis, Compliance, Constitutional Review |
| **Maria Quitéria** | ✅ Active | `/agents/maria-quiteria` | Security Auditing, LGPD Compliance, Forensics |
| **Machado de Assis** | ✅ Active | `/agents/machado` | Textual Analysis, NER, Document Processing |
| **Dandara dos Palmares** | ✅ Active | `/agents/dandara` | Social Equity Analysis, IBGE/DataSUS/INEP Integration |
| **Lampião** | ✅ Active | `/agents/lampiao` | Regional Analysis, Spatial Statistics, Inequality Measurement |
| **Oscar Niemeyer** | ✅ Active | `/agents/oscar` | Data Aggregation, Network Graphs, Choropleth Maps |

### Ready to Activate (1/17)

| Agent | Status | Implementation | Activation Priority |
|-------|--------|----------------|---------------------|
| **Drummond** | 🟡 Ready | Needs Review | MEDIUM - Communication |

### Infrastructure Agents (3/17)

| Agent | Status | Purpose | Priority |
|-------|--------|---------|----------|
| **Abaporu** | 🔧 Infrastructure | Master Agent/Orchestrator | CRITICAL |
| **Ayrton Senna** | 🔧 Infrastructure | Semantic Router/Intent Detection | CRITICAL |
| **Nanã** | 🔧 Infrastructure | Memory System (Episodic/Semantic) | HIGH |

### Under Development (4/17)

| Agent | Status | Implementation | Notes |
|-------|--------|----------------|-------|
| **Obaluaiê** | 🚧 Partial | Structure Only | Corruption Detection |
| **Oxossi** | 🚧 Partial | Structure Only | Data Hunting/Investigation |
| **Ceuci** | 🚧 Partial | Structure Only | Unknown Role |
| **Deodoro** | 🔧 Base Classes | Foundation | Base Agent Implementation |

---

## 📋 Detailed Agent Descriptions

### ✅ ACTIVE AGENTS

#### 1. Zumbi dos Palmares - Anomaly Detection Specialist
**File**: `src/agents/zumbi.py`
**Role**: Investigator / Anomaly Detector

**Capabilities**:
- Price anomaly detection (2.5 standard deviations)
- Vendor concentration analysis (>70% threshold)
- Temporal pattern recognition
- Contract duplication detection (>85% similarity)
- Payment irregularity identification
- FFT spectral analysis for patterns

**API Endpoint**:
```
POST /api/v1/agents/zumbi
{
  "query": "Analyze contracts for anomalies",
  "context": {},
  "options": {}
}
```

#### 2. Anita Garibaldi - Pattern Analysis Specialist
**File**: `src/agents/anita.py`
**Role**: Analyst / Pattern Recognizer

**Capabilities**:
- Spending trend analysis
- Organizational behavior mapping
- Vendor relationship analysis
- Seasonal pattern detection
- Efficiency metrics calculation
- Correlation detection

**API Endpoint**:
```
POST /api/v1/agents/anita
{
  "query": "Find spending patterns",
  "context": {},
  "options": {}
}
```

#### 3. Tiradentes - Report Generation Specialist
**File**: `src/agents/tiradentes.py`
**Role**: Reporter / Communicator

**Capabilities**:
- Executive summary generation
- Detailed investigation reports
- Multi-format output (JSON, Markdown, HTML)
- Natural language explanations
- Actionable recommendations
- Brazilian Portuguese fluency

**API Endpoint**:
```
POST /api/v1/agents/tiradentes
{
  "query": "Generate investigation report",
  "context": {},
  "options": {
    "format": "markdown"
  }
}
```

#### 4. José Bonifácio - Legal & Compliance Specialist
**File**: `src/agents/bonifacio.py`
**Role**: Legal Analyst / Compliance Auditor

**Capabilities**:
- Legal framework verification
- Compliance assessment (Lei 8.666, Lei 14.133, LAI, LGPD)
- Regulatory requirement checking
- Constitutional alignment analysis (CF/88)
- Legal risk identification
- Jurisprudence application

**API Endpoint**:
```
POST /api/v1/agents/bonifacio
{
  "query": "Check legal compliance",
  "context": {},
  "options": {}
}
```

#### 5. Maria Quitéria - Security Auditor & System Guardian
**File**: `src/agents/maria_quiteria.py`
**Role**: Security Specialist / Auditor

**Capabilities**:
- Security threat detection
- Vulnerability assessment
- LGPD compliance verification
- ISO 27001 compliance checking
- Intrusion detection
- Digital forensics
- Risk assessment
- Security monitoring

**API Endpoint**:
```
POST /api/v1/agents/maria-quiteria
{
  "query": "Audit security compliance",
  "context": {},
  "options": {}
}
```

---

### 🟡 READY TO ACTIVATE

---

### ✅ ACTIVE AGENTS (continued)

#### 6. Machado de Assis - Textual Analysis Agent
**File**: `src/agents/machado.py`
**Status**: ✅ Active
**Role**: Document Analyst / NLP Specialist

**Capabilities**:
- Document parsing and classification
- Named Entity Recognition (NER)
  - Organizations, People, Locations
  - Monetary values, Dates
  - Legal references
- Semantic analysis
- Legal compliance checking
- Ambiguity detection
- Readability assessment (Flesch adapted for PT-BR)
- Contract analysis
- Tender document review
- Regulatory text processing
- Suspicious clause identification
- Linguistic complexity analysis
- Transparency scoring

**Alert Detection**:
- Urgency abuse patterns
- Vague specifications
- Exclusive criteria (favoritism)
- Price manipulation indicators
- Favoritism patterns

**Metrics**:
- Complexity Score (0-1)
- Transparency Score (0-1)
- Legal Compliance (0-1)
- Readability Grade (6-20)

**API Endpoint**:
```
POST /api/v1/agents/machado
{
  "document_content": "Full text of government document",
  "document_type": "contract",  // optional
  "focus_areas": ["ambiguity", "compliance"],  // optional
  "legal_framework": ["LEI8666", "LEI14133"],  // optional
  "complexity_threshold": 0.7
}
```

#### 7. Dandara dos Palmares - Social Justice Agent
**File**: `src/agents/dandara.py`
**Status**: ✅ Active with Real APIs
**Role**: Social Equity Analyst / Policy Monitor

**Capabilities**:
- Social equity analysis
- Inclusion policy monitoring
- Gini coefficient calculation (from real IBGE data)
- Demographic disparity detection
- Social justice violation identification
- Distributive justice assessment
- Policy effectiveness evaluation
- Intersectional analysis
- Vulnerability mapping
- Equity gap identification

**Real API Integrations**:
- ✅ IBGE (demographic, poverty, housing data)
- ✅ DataSUS (health indicators, facilities, vaccination)
- ✅ INEP (education indicators, IDEB, infrastructure)

**Equity Metrics**:
- Gini Coefficient
- Atkinson Index
- Theil Index
- Palma Ratio
- Quintile Ratio

**API Endpoint**:
```
POST /api/v1/agents/dandara
{
  "query": "Analyze social equity in education",
  "target_groups": ["students", "vulnerable_populations"],
  "policy_areas": ["education", "health"],
  "geographical_scope": "Rio de Janeiro",
  "time_period": ["2020-01-01", "2024-12-31"],
  "metrics_focus": ["gini_coefficient", "palma_ratio"]
}
```

**Output**:
- Equity Score (0-100)
- Gini Coefficient (0-1)
- Violations Detected (with legal references)
- Inclusion Gaps Identified
- Evidence-Based Recommendations
- Population Affected (estimated from IBGE)
- Confidence Level (0.92 with real data)

#### 8. Lampião - Regional Analysis Specialist
**File**: `src/agents/lampiao.py`
**Status**: ✅ Active with Real IBGE Data
**Role**: Regional Analyst / Spatial Statistics Expert

**Capabilities**:
- Regional inequality measurement (Gini, Theil, Williamson, Atkinson indices)
- Spatial autocorrelation analysis (Moran's I, LISA)
- Hotspot detection (Getis-Ord G*)
- Geographic boundary analysis with IBGE data
- Regional disparity mapping
- Spatial pattern detection
- Lorenz curve generation
- Coverage of all 27 Brazilian states

**Real Data Integration**:
- ✅ IBGE demographic data (population, GDP per capita, HDI)
- ✅ IBGE geographic boundaries (GeoJSON)
- ✅ State-level economic indicators

**Statistical Indices**:
- Gini Spatial Index (0-1)
- Theil Index (entropy-based)
- Williamson Index (weighted variation)
- Atkinson Index (inequality aversion)
- Coefficient of Variation

**API Endpoint**:
```
POST /api/v1/agents/lampiao
{
  "query": "Analyze regional inequality in Northeast",
  "metric": "gdp_per_capita",
  "region_type": "state",
  "options": {
    "calculate_moran": true,
    "detect_hotspots": true
  }
}
```

**Output**:
- Gini Index (0-1)
- Theil Index (0-∞)
- Moran's I (-1 to 1, spatial autocorrelation)
- Hotspot/Coldspot Locations
- Regional Rankings
- Disparity Visualization Data

#### 9. Oscar Niemeyer - Data Aggregation & Visualization Architect
**File**: `src/agents/oscar_niemeyer.py`
**Status**: ✅ Active with Plotly + NetworkX
**Role**: Data Architect / Visualization Engineer

**Capabilities**:
- Network graph visualization (NetworkX + Plotly)
- Fraud relationship network detection
- Choropleth maps for Brazilian states/municipalities
- Time series generation with trend and seasonality
- Geographic aggregation by region (North, Northeast, South, Southeast, Center-West)
- Multi-dimensional data aggregation
- Data export formats (JSON, CSV)
- Interactive graph layouts (force-directed, circular, hierarchical)
- IBGE GeoJSON integration for accurate boundaries

**Visualization Types**:
- Network graphs (fraud detection, relationship mapping)
- Choropleth maps (geographic heat maps)
- Time series charts (trends, seasonality)
- Bar charts, pie charts, scatter plots
- Heatmaps for multi-dimensional data

**API Endpoint**:
```
POST /api/v1/agents/oscar
{
  "query": "Create network graph of supplier relationships",
  "action": "network_graph",
  "options": {
    "entities": [...],
    "relationships": [...],
    "threshold": 0.7,
    "layout": "force_directed"
  }
}
```

**Actions Supported**:
- `time_series`: Generate time series visualization
- `spatial_aggregation`: Aggregate data by geographic region
- `network_graph`: Create interactive fraud network
- `choropleth_map`: Generate choropleth map for Brazil
- `visualization_metadata`: Generate metadata for frontend charts

**Output**:
- Plotly JSON (interactive visualizations)
- Node/Edge counts for networks
- Geographic aggregations
- Time series with trends
- Exportable formats (JSON, CSV)

---

### 🟡 READY TO ACTIVATE

#### 10. Drummond - Communication Agent
**File**: `src/agents/drummond.py` / `drummond_simple.py`
**Status**: 🟡 Needs Review
**Role**: Communication Specialist / Content Creator

**Note**: Two versions exist - need to consolidate and review implementation.

---

### 🔧 INFRASTRUCTURE AGENTS

#### 9. Abaporu - Master Agent / Orchestrator
**File**: `src/agents/abaporu.py`
**Status**: 🔧 Core Infrastructure
**Role**: Master Coordinator / Investigation Planner

**Purpose**:
- Orchestrates multi-agent investigations
- Creates investigation plans
- Delegates tasks to specialized agents
- Synthesizes results from multiple agents
- Manages agent collaboration
- Ensures quality and consistency

**Key Classes**:
- `MasterAgent`
- `InvestigationPlan`
- `InvestigationResult`

**Note**: Should NOT be exposed as direct endpoint - used internally by chat system

#### 10. Ayrton Senna - Semantic Router
**File**: `src/agents/ayrton_senna.py`
**Status**: 🔧 Core Infrastructure
**Role**: Intent Detection / Request Router

**Purpose**:
- Detects user intent from Portuguese queries
- Routes requests to appropriate agents
- Handles semantic understanding
- Maps queries to agent capabilities
- Provides fast agent selection

**Key Class**: `SemanticRouter`

**Note**: Should NOT be exposed as direct endpoint - used by chat API

#### 11. Nanã - Memory System Agent
**File**: `src/agents/nana.py`
**Status**: 🔧 Core Infrastructure
**Role**: Memory Manager / Context Provider

**Purpose**:
- Episodic memory (conversation history)
- Semantic memory (knowledge base)
- Context memory (session state)
- Memory integration across agents
- Conversation continuity

**Key Classes**:
- `ContextMemoryAgent`
- `EpisodicMemory`
- `SemanticMemory`
- `ConversationMemory`
- `MemoryEntry`

**Note**: Infrastructure component - not a user-facing agent

---

### 🚧 UNDER DEVELOPMENT

#### 12-17. Partial Implementation Agents

These agents have file structures but incomplete implementations:

- **Lampião**: Anti-corruption specialist (structure only)
- **Oscar Niemeyer**: Infrastructure analysis (structure only)
- **Obaluaiê**: Corruption detection (structure only)
- **Oxossi**: Data hunting/investigation (structure only)
- **Ceuci**: Role undefined (structure only)
- **Deodoro**: Base classes for all agents (foundation)

---

## 🚀 Activation Plan

### Phase 1: Immediate (This Sprint)

**Priority**: Activate Machado and Dandara

1. **Add Machado to routes**
   - Create POST endpoint `/api/v1/agents/machado`
   - Add to agent status list
   - Write endpoint tests
   - Update API documentation

2. **Add Dandara to routes**
   - Create POST endpoint `/api/v1/agents/dandara`
   - Add to agent status list
   - Write endpoint tests
   - Update API documentation

3. **Update documentation**
   - Update Swagger/OpenAPI docs
   - Create agent capability matrix
   - Write usage examples
   - Add to README

### Phase 2: Short Term (Next Sprint)

1. **Review and Activate Drummond**
   - Consolidate two versions
   - Complete implementation if needed
   - Add endpoint
   - Test integration

2. **Infrastructure Improvements**
   - Ensure Abaporu properly orchestrates new agents
   - Update SemanticRouter to recognize new agents
   - Integrate Memory system

### Phase 3: Medium Term (1 Month)

1. **Complete Partial Agents**
   - Lampião (Anti-Corruption)
   - Oscar Niemeyer (Infrastructure Analysis)
   - Obaluaiê (Corruption Detection)
   - Oxossi (Data Hunting)

2. **Agent Pool Optimization**
   - Pre-warm frequently used agents
   - Implement lazy loading
   - Monitor agent performance
   - Optimize resource usage

---

## 📊 Agent Capabilities Matrix

| Capability | Zumbi | Anita | Tiradentes | Bonifácio | Maria Q. | Machado | Dandara |
|------------|-------|-------|------------|-----------|----------|---------|---------|
| **Anomaly Detection** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Pattern Analysis** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Report Generation** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Legal Analysis** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Security Audit** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Textual Analysis** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Social Equity** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **NLP/NER** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Real API Integration** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🧪 Testing Strategy

### Unit Tests Required

For each activated agent:

```python
# tests/unit/agents/test_machado.py
async def test_machado_document_analysis():
    """Test Machado textual analysis."""
    agent = MachadoAgent()
    result = await agent.process(
        message=AgentMessage(data={"document_content": "..."}),
        context=AgentContext(...)
    )
    assert result.success
    assert "entities" in result.data
    assert "alerts" in result.data

# tests/unit/agents/test_dandara.py
async def test_dandara_equity_analysis():
    """Test Dandara social justice analysis."""
    agent = DandaraAgent()
    result = await agent.process(
        message=AgentMessage(data={"query": "..."}),
        context=AgentContext(...)
    )
    assert result.success
    assert "equity_score" in result.data
```

### Integration Tests

```python
# tests/integration/test_agent_routes.py
async def test_machado_endpoint(client):
    """Test Machado API endpoint."""
    response = await client.post(
        "/api/v1/agents/machado",
        json={"query": "Analyze this contract", "context": {}}
    )
    assert response.status_code == 200
    assert "result" in response.json()
```

---

## 📖 API Documentation Updates Needed

### Swagger/OpenAPI

Add new endpoints to API documentation:

```yaml
/api/v1/agents/machado:
  post:
    summary: Process document with Machado de Assis agent
    description: Textual analysis of government documents
    tags: [Agents]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AgentRequest'
    responses:
      200:
        description: Analysis completed
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AgentResponse'
```

---

## 🔗 Related Files

### Agent Implementation Files
- `src/agents/machado.py` - Machado de Assis agent
- `src/agents/dandara.py` - Dandara dos Palmares agent
- `src/agents/drummond.py` - Drummond agent (review needed)

### Routes
- `src/api/routes/agents.py` - Agent endpoints (needs update)

### Tests
- `tests/unit/agents/` - Unit tests (create new)
- `tests/integration/` - Integration tests (create new)

### Documentation
- `docs/agents/` - Agent documentation (create)
- `README.md` - Update with new agents

---

## 📝 Next Steps

1. ✅ Create this inventory document
2. ✅ Add Machado endpoint to routes
3. ✅ Add Dandara endpoint to routes
4. ✅ Update agent status endpoint
5. ⏳ Write tests for new agents
6. ⏳ Update API documentation
7. ⏳ Deploy and test on Railway

---

**Prepared by**: Anderson Henrique da Silva
**Date**: 2025-10-13
**Status**: Ready for Activation
**Priority**: HIGH - Complete agent activation
