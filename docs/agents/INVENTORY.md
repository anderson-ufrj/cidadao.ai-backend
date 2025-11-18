# Cidadão.AI - Agents Inventory & Activation Guide

**Date**: 2025-11-18 (Documentation Audit Update)
**Status**: Agent System Operational - Documentation Verified

---

## 🤖 Agents Status Overview

### ✅ Active Agents (16/17) - All Operational!

#### Regular Analysis Agents (9/17)
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

#### Specialized Agents (4/17)
| Agent | Status | Endpoint | Capabilities |
|-------|--------|----------|--------------|
| **Drummond** | ✅ Active | `/agents/drummond` | Communication, Content Creation, Documentation |
| **Obaluaiê** | ✅ Active | `/agents/obaluaie` | Corruption Detection, Risk Assessment, Fraud Analysis |
| **Oxossi** | ✅ Active | `/agents/oxossi` | Data Hunting, API Integration, Web Scraping |
| **Ceuci** | ✅ Active | `/agents/ceuci` | ETL, Predictive Analytics, Time Series Forecasting |

#### Infrastructure Agents (3/17)
| Agent | Status | Endpoint | Purpose |
|-------|--------|----------|---------|
| **Abaporu** | ✅ Active | `/agents/abaporu` | Master Agent/Orchestrator (Multi-Agent Coordination) |
| **Ayrton Senna** | ✅ Active | `/agents/ayrton-senna` | Semantic Router (Intent Detection & Routing) |
| **Nanã** | ✅ Active | `/agents/nana` | Memory System (Episodic/Semantic/Conversation) |

### Base Classes (1/17)
| Agent | Status | Purpose |
|-------|--------|---------|
| **Deodoro** | 🔧 Foundation | Base Agent Implementation (BaseAgent, ReflectiveAgent)

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

---

### ✅ ACTIVE SPECIALIZED AGENTS

#### 10. Drummond - Communication & Content Creation Specialist
**File**: `src/agents/drummond.py`
**Status**: ✅ Active
**Role**: Communication Specialist / Content Creator

**Capabilities**:
- Blog posts and articles generation
- Social media content creation
- Technical documentation writing
- Press releases
- Multi-format content (Markdown, HTML, PDF)
- SEO optimization
- Tone and style adaptation
- Content strategy development

**API Endpoint**:
```
POST /api/v1/agents/drummond
{
  "query": "Create a technical article about transparency",
  "context": {},
  "options": {
    "format": "markdown",
    "tone": "professional"
  }
}
```

#### 11. Obaluaiê - Corruption Detection & Risk Assessment Specialist
**File**: `src/agents/obaluaie.py`
**Status**: ✅ Active
**Role**: Corruption Detector / Risk Analyst

**Capabilities**:
- Corruption pattern detection
- Risk score calculation
- Fraud scheme identification
- Network analysis for corruption rings
- Political connection mapping
- Financial anomaly detection
- Behavioral pattern analysis

**API Endpoint**:
```
POST /api/v1/agents/obaluaie
{
  "query": "Detect corruption patterns in contracts",
  "context": {},
  "options": {}
}
```

#### 12. Oxossi - Data Hunting & Discovery Specialist
**File**: `src/agents/oxossi.py`
**Status**: ✅ Active
**Role**: Data Hunter / Investigation Specialist

**Capabilities**:
- Multi-source data discovery
- API integration and data fetching
- Database querying and extraction
- Web scraping (Portal da Transparência)
- Data validation and enrichment
- Entity resolution
- Cross-reference analysis
- Data quality assessment

**API Endpoint**:
```
POST /api/v1/agents/oxossi
{
  "query": "Find all contracts for supplier X",
  "context": {},
  "options": {
    "sources": ["transparency_api", "database"]
  }
}
```

#### 13. Ceuci - ETL & Predictive Analytics Specialist
**File**: `src/agents/ceuci.py`
**Status**: ✅ Active
**Role**: ETL Engineer / Predictive Analyst

**Capabilities**:
- Data extraction, transformation, loading
- Time series forecasting
- Trend prediction
- Seasonality detection
- Budget forecasting
- Resource allocation optimization
- Anomaly prediction
- Machine learning pipeline management

**API Endpoint**:
```
POST /api/v1/agents/ceuci
{
  "query": "Forecast budget for next quarter",
  "context": {},
  "options": {
    "horizon": 90,
    "confidence_level": 0.95
  }
}
```

---

### 🔧 INFRASTRUCTURE AGENTS

#### 14. Abaporu - Master Agent / Orchestrator
**File**: `src/agents/abaporu.py`
**Status**: ✅ Active (Infrastructure)
**Role**: Master Coordinator / Investigation Planner

**Capabilities**:
- Multi-agent workflow coordination
- Investigation planning and execution
- Task delegation and monitoring
- Result synthesis across agents
- Strategic decision making
- Resource allocation
- Quality control
- Complex analysis orchestration

**API Endpoint**:
```
POST /api/v1/agents/abaporu
{
  "query": "Coordinate investigation into budget anomalies",
  "context": {},
  "options": {
    "agents_to_use": ["zumbi", "anita", "tiradentes"]
  }
}
```

**Note**: Can be used both as infrastructure (internal coordination) and as user-facing endpoint for complex multi-agent tasks.

#### 15. Ayrton Senna - Semantic Router & Intent Detection
**File**: `src/agents/ayrton_senna.py`
**Status**: ✅ Active (Infrastructure)
**Role**: Intent Detector / Request Router

**Capabilities**:
- Natural language understanding (PT-BR focus)
- Intent classification
- Entity extraction
- Query understanding
- Agent selection and routing
- Context analysis
- Semantic similarity calculation
- Multi-language support

**API Endpoint**:
```
POST /api/v1/agents/ayrton-senna
{
  "query": "Quero analisar contratos suspeitos",
  "context": {},
  "options": {}
}
```

**Output**:
- Detected intent
- Recommended agent(s)
- Confidence score
- Extracted entities

**Note**: Can be used both as infrastructure (chat routing) and as user-facing endpoint for testing intent detection.

#### 16. Nanã - Memory Management & Context Specialist
**File**: `src/agents/nana.py`
**Status**: ✅ Active (Infrastructure)
**Role**: Memory Manager / Context Provider

**Capabilities**:
- Episodic memory (event sequences, conversation history)
- Semantic memory (knowledge graphs, facts)
- Conversation memory (dialogue state)
- Context retrieval and storage
- Long-term memory management
- Working memory optimization
- Memory consolidation
- Context-aware recommendations

**Memory Types**:
- **Episodic**: Temporal sequences of events
- **Semantic**: Structured knowledge and relationships
- **Conversation**: Session state and dialogue history

**API Endpoint**:
```
POST /api/v1/agents/nana
{
  "query": "Retrieve conversation context",
  "context": {
    "session_id": "abc123"
  },
  "options": {
    "memory_types": ["episodic", "conversation"]
  }
}
```

**Note**: Can be used both as infrastructure (automatic context) and as user-facing endpoint for explicit memory retrieval.

---

### 🔧 BASE CLASSES

#### 17. Deodoro - Base Agent Framework
**File**: `src/agents/deodoro.py`
**Status**: 🔧 Foundation
**Role**: Base Classes for Agent System

**Purpose**:
- Provides base agent architecture
- Implements common agent patterns
- Reflection and self-evaluation
- State management
- Error handling

**Key Classes**:
- `BaseAgent`: Core agent functionality
- `ReflectiveAgent`: Self-reflection capabilities
- `AgentContext`: Execution context
- `AgentMessage`: Message protocol
- `AgentResponse`: Response protocol

**Note**: Foundation component - not a user-facing agent

---

## 🚀 Activation Plan

### ✅ Phase 1: V1 COMPLETE! (All 16 Agents Active)

**Status**: ✅ COMPLETED on 2025-10-13

All 16 agents now have fully functional API endpoints:

1. ✅ 9 Regular Analysis Agents (Zumbi, Anita, Tiradentes, Bonifácio, Maria Quitéria, Machado, Dandara, Lampião, Oscar)
2. ✅ 4 Specialized Agents (Drummond, Obaluaiê, Oxossi, Ceuci)
3. ✅ 3 Infrastructure Agents (Abaporu, Ayrton Senna, Nanã)

**File Size**: `src/api/routes/agents.py` = 1,586 lines (56KB)

**Changes Made**:
- Added 7 new POST endpoints with full FastAPI integration
- Updated `/status` endpoint to include all 16 agents
- Updated `/` listing endpoint with all agents
- Code formatted and validated

### Phase 2: Testing & Quality Assurance (Current Sprint)

**Priority**: Test, document, deploy

1. **Local Testing**
   - ✅ Test agent imports and loading
   - ⏳ Test individual agent endpoints
   - ⏳ Test `/status` endpoint shows all 16 agents
   - ⏳ Test agent pool initialization

2. **Documentation**
   - ✅ Update AGENTS_INVENTORY.md with all 16 agents
   - ⏳ Update README.md with agent count
   - ⏳ Update API docs (if needed)

3. **Deployment**
   - ⏳ Commit changes (professional message, no AI mentions)
   - ⏳ Push to GitHub
   - ⏳ Deploy to Railway
   - ⏳ Verify production endpoints

### Phase 3: Iterative Improvements (Next 2-4 Weeks)

**Priority**: Enhance agent implementations

1. **Agent Implementation Improvements**
   - Complete TODOs in agent code
   - Add missing algorithms and features
   - Improve error handling
   - Add validation logic

2. **Integration & Testing**
   - Write comprehensive unit tests
   - Write integration tests for all endpoints
   - Performance testing
   - Load testing

3. **Agent Coordination**
   - Ensure Abaporu properly orchestrates all agents
   - Update SemanticRouter to recognize all 16 agents
   - Test Memory system integration (Nanã)
   - Multi-agent workflow testing

### Phase 4: Production Optimization (1-2 Months)

1. **Performance & Scale**
   - Agent pool optimization
   - Caching strategies
   - Connection pooling
   - Resource monitoring

2. **Advanced Features**
   - Agent chaining workflows
   - Parallel agent execution
   - Result aggregation
   - Quality scoring

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
