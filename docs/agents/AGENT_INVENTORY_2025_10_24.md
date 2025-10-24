# Agent Inventory - Canonical List

**Last Updated**: 2025-10-24 14:30:00 BRT
**Verification Method**: Automated codebase analysis + production testing
**Next Review**: 2026-01-24 (quarterly review cycle)

---

## Summary Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Specialized Agents** | 16 | 100% |
| **Tier 1 (Operational)** | 10 | 62.5% |
| **Tier 2 (Framework)** | 5 | 31.25% |
| **Tier 3 (Minimal)** | 1 | 6.25% |
| **Agents with Tests** | 16 | 100% |
| **Test Files** | 31 | - |
| **Base Class** | 1 (Deodoro) | - |

---

## Agent Classification

### Tier 1: Fully Operational (10 agents - 90-100% complete)

Agents with complete implementation, comprehensive testing, and production-ready functionality.

#### 1. **Zumbi dos Palmares** (`zumbi.py`) - 1,427 LOC
- **Role**: Anomaly Detection Specialist
- **Capabilities**:
  - FFT spectral analysis for pattern detection
  - Statistical anomaly detection (Z-score, IQR)
  - Price deviation analysis (>2.5 std dev)
  - Supplier concentration detection (>70%)
  - Contract similarity analysis (>85%)
- **Test Coverage**: 58.90%
- **Test File**: `test_zumbi.py`, `test_zumbi_complete.py`
- **Status**: ✅ Production ready, battle-tested
- **Cultural Identity**: Leader of Palmares quilombo, fights against systemic injustice

#### 2. **Anita Garibaldi** (`anita.py`) - 1,560 LOC
- **Role**: Statistical Pattern Analyst
- **Capabilities**:
  - Advanced clustering algorithms (K-means, DBSCAN)
  - Data profiling and quality assessment
  - Time-series pattern detection
  - Correlation analysis
  - Distribution analysis
- **Test Coverage**: 10.59%
- **Test Files**: `test_anita.py`, `test_anita_boost.py`, `test_anita_expanded.py`
- **Status**: ✅ Operational, needs test coverage improvement
- **Cultural Identity**: Brazilian revolutionary, fought in South American wars of independence

#### 3. **Oxóssi** (`oxossi.py`) - 1,698 LOC
- **Role**: Fraud Detection Expert
- **Capabilities**:
  - 7+ fraud pattern detection algorithms
  - Bid rigging detection
  - Phantom vendor identification
  - Price fixing analysis
  - Shell company detection
  - Round-number analysis
  - Temporal pattern anomalies
- **Test Coverage**: 83.80% ✅
- **Test File**: `test_oxossi.py` (comprehensive - 43 tests)
- **Status**: ✅ Production ready, excellent coverage
- **Cultural Identity**: Orixá of the hunt, tracks hidden truths

#### 4. **Lampião** (`lampiao.py`) - 1,587 LOC
- **Role**: Regional Inequality Analyst
- **Capabilities**:
  - Spatial inequality analysis
  - Gini coefficient calculation
  - Per-capita normalization
  - Regional hotspot/cold-spot detection
  - Spatial autocorrelation (Moran's I)
  - Geographic clustering
- **Test Coverage**: 79.10%
- **Test File**: `test_lampiao.py`
- **Status**: ✅ Operational, approaching 80% coverage target
- **Cultural Identity**: Cangaceiro leader, challenged regional power imbalances

#### 5. **Ayrton Senna** (`ayrton_senna.py`) - 646 LOC
- **Role**: Intent Router & Orchestrator
- **Capabilities**:
  - Semantic intent classification
  - Agent routing and selection
  - Load balancing across agents
  - Query understanding (Portuguese)
  - Context extraction
- **Test Coverage**: 46.59%
- **Test Files**: `test_ayrton_senna.py`, `test_ayrton_senna_complete.py`
- **Status**: ✅ Core routing operational
- **Cultural Identity**: Formula 1 champion, precision and speed

#### 6. **Tiradentes** (`tiradentes.py`) - 1,934 LOC
- **Role**: Report Generation Specialist
- **Capabilities**:
  - Multi-format report generation (PDF, HTML, Excel, JSON)
  - Executive summaries
  - Data visualization integration
  - Template-based reporting
  - Markdown rendering
- **Test Coverage**: 52.99%
- **Test File**: `test_tiradentes_reporter.py`
- **Status**: ✅ Production reports generated daily
- **Cultural Identity**: Inconfidência Mineira leader, transparency advocate

#### 7. **Oscar Niemeyer** (`oscar_niemeyer.py`) - 1,228 LOC
- **Role**: Data Visualization Architect
- **Capabilities**:
  - Interactive Plotly visualizations
  - Network graphs (NetworkX)
  - Heatmaps and geospatial viz
  - Chart generation (bar, line, scatter, treemap)
  - Dashboard layouts
- **Test Coverage**: 93.78% ✅
- **Test File**: `test_oscar_niemeyer.py`
- **Status**: ✅ Excellent coverage, production ready
- **Cultural Identity**: Renowned architect, builds clear structures from complex data

#### 8. **Machado de Assis** (`machado.py`) - 678 LOC
- **Role**: NER & Textual Analysis
- **Capabilities**:
  - Named Entity Recognition
  - Sentiment analysis
  - Key phrase extraction
  - Narrative structure analysis
  - Document summarization
- **Test Coverage**: 24.84%
- **Test File**: `test_machado.py`
- **Status**: ✅ Core NER operational
- **Cultural Identity**: Literary master, extracts meaning from text

#### 9. **José Bonifácio** (`bonifacio.py`) - 2,131 LOC
- **Role**: Legal Compliance Analyst
- **Capabilities**:
  - Legal framework validation
  - Policy compliance checking
  - Regulatory requirement analysis
  - Constitutional alignment verification
  - Jurisprudence cross-referencing
- **Test Coverage**: 49.13%
- **Test File**: `test_bonifacio.py`
- **Status**: ✅ Legal validations operational
- **Cultural Identity**: Patriarch of Independence, established legal foundations

#### 10. **Maria Quitéria** (`maria_quiteria.py`) - 2,589 LOC
- **Role**: Security Auditing Specialist
- **Capabilities**:
  - MITRE ATT&CK framework integration
  - User Entity Behavior Analytics (UEBA)
  - Threat pattern detection
  - Access control auditing
  - Security posture assessment
- **Test Coverage**: 23.23%
- **Test Files**: `test_maria_quiteria.py`, `test_maria_quiteria_boost.py`, `test_maria_quiteria_expanded.py`
- **Status**: ✅ Security audits operational
- **Cultural Identity**: First woman in Brazilian army, vigilant defender

---

### Tier 2: Substantial Framework (5 agents - 10-70% complete)

Agents with working framework but requiring completion for full production deployment.

#### 11. **Abaporu** (`abaporu.py`) - 1,089 LOC (70% complete)
- **Role**: Multi-Agent Orchestration Master
- **Capabilities (Partial)**:
  - Agent coordination framework
  - Task distribution logic
  - Result aggregation structure
  - Conflict resolution patterns
- **Missing**: Real-time orchestration, priority queuing, deadlock detection
- **Test Coverage**: 13.37%
- **Test File**: `test_abaporu.py`
- **Status**: ⚠️ Framework complete, needs integration testing
- **Cultural Identity**: Tarsila do Amaral's iconic painting, synthesizes diverse elements

#### 12. **Nanã** (`nana.py`) - 963 LOC (65% complete)
- **Role**: Memory & Context Manager
- **Capabilities (Partial)**:
  - Short-term memory structure
  - Context window management
  - Conversation history tracking
- **Missing**: Long-term memory persistence, semantic search, context summarization
- **Test Coverage**: 11.76%
- **Test File**: `test_nana.py`
- **Status**: ⚠️ Basic memory works, needs persistence layer
- **Cultural Identity**: Orixá of wisdom and ancestral memory

#### 13. **Carlos Drummond de Andrade** (`drummond.py`) - 1,678 LOC (25% complete)
- **Role**: Natural Language Generation
- **Capabilities (Partial)**:
  - Template-based response generation
  - Basic Portuguese language structures
- **Missing**: LLM integration, contextual generation, tone adaptation
- **Test Coverage**: 35.48%
- **Test Files**: `test_drummond.py`, `test_drummond_coverage.py`, `test_drummond_expanded.py`
- **Status**: ⚠️ Framework only, needs LLM integration
- **Cultural Identity**: Poetic master, communicates complex ideas elegantly

#### 14. **Céuci** (`ceuci.py`) - 1,697 LOC (10% complete)
- **Role**: ML/Predictive Analytics
- **Capabilities (Partial)**:
  - ML pipeline structure
  - Feature engineering framework
  - Model training scaffolding
- **Missing**: Trained models, prediction endpoints, model versioning
- **Test Coverage**: 10.49%
- **Test File**: `test_ceuci.py`
- **Status**: ⚠️ Framework only, no trained models
- **Cultural Identity**: Tupinambá leader, strategic foresight

#### 15. **Obaluaiê** (`obaluaie.py`) - 829 LOC (15% complete)
- **Role**: Corruption Detection
- **Capabilities (Partial)**:
  - Benford's Law analysis (partial)
  - Digital forensics structure
  - Corruption indicator framework
- **Missing**: Complete Benford implementation, ML corruption models, pattern libraries
- **Test Coverage**: 13.11%
- **Test File**: `test_obaluaie.py`
- **Status**: ⚠️ Basic structure, needs algorithm completion
- **Cultural Identity**: Orixá of healing, cleanses corruption

---

### Tier 3: Minimal Implementation (1 agent - 30% complete)

Agent with basic structure requiring significant development.

#### 16. **Dandara dos Palmares** (`dandara.py`) - 788 LOC (30% complete)
- **Role**: Social Justice Metrics Analyst
- **Capabilities (Partial)**:
  - Social impact framework
  - Inequality metrics structure
  - Justice indicator definitions
- **Missing**: Data integration, metric calculation, impact assessment algorithms
- **Test Coverage**: 73.79%
- **Test Files**: `test_dandara.py`, `test_dandara_complete.py`, `test_dandara_expanded.py`, `test_dandara_improvements.py`
- **Status**: ⚠️ Framework with excellent test structure, needs implementation
- **Cultural Identity**: Quilombo warrior, fought for equality and justice

---

## Base Class

### Deodoro da Fonseca (`deodoro.py`) - 478 LOC
- **Role**: `ReflectiveAgent` Base Class
- **Provides**:
  - Agent lifecycle management
  - Reflection pattern (quality threshold: 0.8)
  - Message/Response structures
  - Error handling framework
  - Logging and metrics integration
- **Test Coverage**: 96.45% ✅
- **Test File**: `test_deodoro.py`
- **Status**: ✅ Stable base for all agents
- **Cultural Identity**: First president of Brazil, established foundations

---

## Support Modules

### Agent Pool Management
1. **`agent_pool.py`** (Legacy - 243 LOC) - Deprecated
2. **`simple_agent_pool.py`** - Lazy loading, singleton pattern (83.21% coverage)
3. **`agent_pool_interface.py`** - Interface definitions

### Agent Utilities
1. **`parallel_processor.py`** - Concurrent agent execution (90.00% coverage)
2. **`metrics_wrapper.py`** - Performance monitoring
3. **`zumbi_wrapper.py`** - Zumbi-specific utilities

---

## File Structure vs Agent Count

**Clarification**: There are 20 Python files in `src/agents/` directory:

### Core Agents (16 files)
1. abaporu.py
2. anita.py
3. ayrton_senna.py
4. bonifacio.py
5. ceuci.py
6. dandara.py
7. drummond.py
8. lampiao.py
9. machado.py
10. maria_quiteria.py
11. nana.py
12. obaluaie.py
13. oscar_niemeyer.py
14. oxossi.py
15. tiradentes.py
16. zumbi.py

### Support Files (4 files)
17. deodoro.py (base class)
18. agent_pool.py (legacy)
19. simple_agent_pool.py
20. parallel_processor.py

**Additional Support** (not counted in 20):
- `__init__.py`
- `metrics_wrapper.py`
- `zumbi_wrapper.py`
- `agent_pool_interface.py`
- `drummond_simple.py`

---

## Test Coverage Summary

### Excellent Coverage (≥80%)
- Deodoro: 96.45%
- Oscar Niemeyer: 93.78%
- Parallel Processor: 90.00%
- Oxóssi: 83.80% ✅
- Simple Agent Pool: 83.21%

### Good Coverage (50-79%)
- Lampião: 79.10%
- Dandara: 73.79%
- Zumbi: 58.90%
- Tiradentes: 52.99%

### Needs Improvement (<50%)
- Bonifácio: 49.13%
- Ayrton Senna: 46.59%
- Drummond: 35.48%
- Machado: 24.84%
- Maria Quitéria: 23.23%
- Abaporu: 13.37%
- Obaluaiê: 13.11%
- Nanã: 11.76%
- Anita: 10.59%
- Céuci: 10.49%

**Overall Agent Module Coverage**: ~44.59% (Target: 80%)

---

## Production Deployment Status

### Active in Production
All 10 Tier 1 agents are deployed and operational on Railway.

### Integration Points
- **Chat API**: Routes to Senna (router) → specific agents
- **Investigation API**: Multi-agent orchestration via Abaporu
- **Analysis API**: Direct agent invocation
- **Report API**: Tiradentes for all report generation

### Real Data Integration
✅ All agents have access to real government data via:
- Portal da Transparência API (configured)
- IBGE federal APIs
- PNCP public contracts
- DataSUS health data
- State TCE APIs

---

## Development Priorities

### High Priority (Next Sprint)
1. Improve test coverage for Tier 1 agents (target: 80%+)
2. Complete Abaporu orchestration integration
3. Integrate Drummond with LLM for NLG

### Medium Priority (Next Quarter)
4. Complete Céuci ML pipeline with trained models
5. Finish Obaluaiê corruption detection algorithms
6. Enhance Nanã memory persistence

### Low Priority (Backlog)
7. Expand Dandara social justice metrics
8. Add new specialized agents as needed

---

## Verification Commands

```bash
# Count agents
ls src/agents/*.py | grep -v "__\|deodoro\|pool\|processor\|wrapper\|interface\|simple" | wc -l
# Returns: 16

# Count test files
ls tests/unit/agents/test_*.py | wc -l
# Returns: 31

# Run validation
python3 scripts/validate_docs.py
# Should return: PASS
```

---

## Change Log

- **2025-10-24**: Initial canonical inventory created
- **2025-10-24**: Verified all 16 agents have tests (100%)
- **2025-10-24**: Updated Oxóssi coverage to 83.80%
- **2025-10-24**: Confirmed production data integration

---

**Maintained By**: DevOps & Agent Development Team
**Questions**: See individual agent documentation in `docs/agents/<agent_name>.md`
**Automated Validation**: `scripts/validate_docs.py`
