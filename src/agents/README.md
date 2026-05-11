# 🤖 Cidadão.AI Multi-Agent System

## 📋 Overview

The **Multi-Agent System** is the cognitive core of Cidadão.AI, featuring **20 specialized AI agents** with Brazilian cultural identities. Each agent embodies specific expertise in transparency analysis, from anomaly detection to policy evaluation, working together through sophisticated **coordination patterns** and **self-reflection mechanisms**.

## 🏗️ Architecture

```
src/agents/
├── deodoro.py           # Base agent framework & communication protocols
├── base_kids_agent.py   # Base framework for Education agents (Monteiro Lobato, Tarsila)
│
├── abaporu.py           # Master orchestrator - coordinates multi-agent workflows
├── ayrton_senna.py      # Semantic router - routes queries to the right specialist
├── nana.py              # Memory agent - multi-layer memory management (Nanã)
│
├── zumbi.py             # Investigator - anomaly detection specialist
├── zumbi_wrapper.py     # Metrics/cache wrapper for Zumbi
├── anita.py             # Analyst - pattern analysis expert
├── tiradentes.py        # Reporter - natural language generation
├── obaluaie.py          # Corruption detector - financial crime signals
├── oxossi.py            # Fraud hunter - precision fraud detection
│
├── machado.py           # Textual analyst - document processing
├── bonifacio.py         # Policy analyst - institutional effectiveness
├── dandara.py           # Social justice - equity and inclusion monitoring
├── maria_quiteria.py    # Security auditor - system protection
├── oscar_niemeyer.py    # Data aggregator - visualization architecture
├── lampiao.py           # Regional analyst - territorial insights
├── ceuci.py             # ETL specialist + ML predictions
├── ceuci_ml_models.py   # ML models used by Ceuci
├── drummond.py          # Communication - conversational interface
├── drummond_simple.py   # Lightweight version of Drummond
│
├── santos_dumont.py     # System educator - onboarding for interns/contributors
├── bo_bardi.py          # Frontend design guide - SSE/component integration
├── monteiro_lobato.py   # Kids programming educator - Sítio do Picapau Amarelo
└── tarsila.py           # Kids design educator - colors, shapes, and aesthetics
```

## 🧠 Agent Coordination Patterns

### Master-Agent Hierarchy
```python
# Central coordination with adaptive strategies
MasterAgent (Abaporu)
├── coordinates → InvestigatorAgent (Zumbi)
├── coordinates → AnalystAgent (Anita)  
├── coordinates → ReporterAgent (Tiradentes)
├── coordinates → SemanticRouter (Ayrton Senna)
└── coordinates → ContextMemoryAgent (Nanã)

# Self-reflection loops with quality thresholds
Reflection Loop:
1. Execute investigation
2. Assess quality (threshold: 0.8)
3. If quality < threshold: reflect & adapt
4. Max 3 reflection iterations
5. Return optimized results
```

### Communication Architecture
```python
# Structured message passing between agents
AgentMessage:
- sender: str               # Agent identifier
- recipient: str            # Target agent
- action: str              # Action to perform
- payload: Dict[str, Any]  # Message data
- context: AgentContext    # Shared investigation context
- requires_response: bool  # Synchronous vs async

AgentResponse:
- agent_name: str          # Responding agent
- status: AgentStatus      # Success/failure/in_progress
- result: Any              # Actual result data
- error: Optional[str]     # Error details if failed
- metadata: Dict           # Processing metrics
```

## 🎭 Agent Profiles

### 1. **Abaporu** - Master Agent (Orchestrator)
**Cultural Reference**: Abaporu painting by Tarsila do Amaral - symbol of Brazilian Modernism

```python
# Core capabilities
MasterAgent:
- Investigation planning with adaptive strategies
- Agent registry and dependency management  
- Self-reflection with configurable thresholds
- Quality assessment and strategy adaptation
- Comprehensive result synthesis

# Advanced features
- Reflection threshold: 0.8 (configurable)
- Max reflection loops: 3 iterations
- Adaptive investigation strategies based on results
- Agent capability matching and load balancing
```

**Key Methods:**
- `plan_investigation()` - Creates adaptive investigation strategies
- `coordinate_agents()` - Orchestrates multi-agent workflows
- `reflect_on_results()` - Self-assessment and strategy adaptation
- `synthesize_findings()` - Combines results from multiple agents

### 2. **Zumbi** - Investigator Agent (Anomaly Detective)
**Cultural Reference**: Zumbi dos Palmares - freedom fighter and resistance leader

```python
# Anomaly detection capabilities
InvestigatorAgent:
- Price anomalies: 2.5 standard deviation threshold
- Vendor concentration: 70% concentration trigger
- Temporal patterns: Fourier transform analysis
- Duplicate detection: 85% similarity threshold
- Payment irregularities: Statistical outlier detection

# Advanced analytics
- Spectral analysis using FFT for periodic patterns
- Multi-dimensional anomaly scoring
- Machine learning-based pattern recognition
- Cryptographic evidence verification
```

**Anomaly Types:**
- `PRICE_ANOMALY` - Statistical price outliers
- `VENDOR_CONCENTRATION` - Monopolistic vendor patterns
- `TEMPORAL_SUSPICION` - Suspicious timing patterns  
- `DUPLICATE_CONTRACT` - Contract similarity detection
- `PAYMENT_IRREGULARITY` - Payment pattern analysis

### 3. **Anita Garibaldi** - Analyst Agent (Pattern Expert)
**Cultural Reference**: Anita Garibaldi - revolutionary and feminist pioneer

```python
# Pattern analysis capabilities
AnalystAgent:
- Spending trend analysis with linear regression
- Organizational behavior pattern comparison
- Vendor behavior analysis across organizations
- Seasonal pattern detection (end-of-year analysis)
- Cross-spectral analysis between entities
- Efficiency metrics calculation

# Advanced features
- Time series decomposition (trend, seasonal, residual)
- Cross-correlation analysis between organizations
- Spectral density estimation for periodic spending
- Multi-variate regression for complex patterns
```

**Analysis Types:**
- `SPENDING_TRENDS` - Linear regression trend analysis
- `VENDOR_PATTERNS` - Vendor behavior profiling
- `ORGANIZATIONAL_BEHAVIOR` - Cross-org comparison
- `SEASONAL_ANALYSIS` - Seasonal spending patterns
- `EFFICIENCY_METRICS` - Performance indicators

### 4. **Tiradentes** - Reporter Agent (Communication Expert)
**Cultural Reference**: Tiradentes - independence martyr and symbol of justice

```python
# Report generation capabilities
ReporterAgent:
- Multi-format generation: Markdown, HTML, PDF, JSON
- Audience adaptation: technical, executive, public
- Executive summary creation with key insights
- Risk assessment and prioritization
- Multilingual support: PT-BR, EN-US

# Advanced features
- Template-based report generation
- Natural language explanation of technical findings
- Visualization integration with charts and graphs
- Compliance report formatting for regulatory bodies
```

**Report Formats:**
- `EXECUTIVE_SUMMARY` - High-level findings for executives
- `TECHNICAL_REPORT` - Detailed analysis for specialists
- `PUBLIC_REPORT` - Citizen-friendly transparency reports
- `COMPLIANCE_REPORT` - Regulatory compliance documentation

### 5. **Ayrton Senna** - Semantic Router (Query Intelligence)
**Cultural Reference**: Ayrton Senna - Formula 1 champion symbolizing precision and speed

```python
# Intelligent routing capabilities
SemanticRouter:
- Rule-based routing with regex patterns
- Semantic similarity analysis for complex queries
- Intent detection for conversational flows
- Fallback strategies for ambiguous cases
- Agent capability matching and load balancing

# Routing strategies
1. Rule-based: Fast pattern matching for common queries
2. Semantic: Vector similarity for complex queries  
3. Fallback: Default routing when ambiguous
```

**Query Types:**
- `INVESTIGATION_QUERY` → InvestigatorAgent
- `ANALYSIS_QUERY` → AnalystAgent
- `REPORT_REQUEST` → ReporterAgent
- `MEMORY_QUERY` → ContextMemoryAgent

### 6. **Nanã** - Context Memory Agent (Wisdom Keeper)
**Cultural Reference**: Nanã - Yoruba deity of wisdom and ancestral memory

```python
# Multi-layer memory architecture
ContextMemoryAgent:
- Episodic memory: Investigation results and events
- Semantic memory: General knowledge and patterns
- Conversational memory: Dialog context preservation
- Memory importance scoring and decay management
- Vector-based semantic search with ChromaDB

# Memory layers
Episodic: Specific investigation events and results
Semantic: General patterns and knowledge base  
Conversational: Dialog context and user preferences
```

**Memory Operations:**
- `store_episodic()` - Store investigation results
- `retrieve_semantic()` - Query knowledge patterns
- `maintain_conversation()` - Preserve dialog context
- `consolidate_memory()` - Long-term memory formation

### 7. **Monteiro Lobato** - Kids Programming Educator

**Cultural Reference**: José Bento Renato Monteiro Lobato (1882–1948) — father of Brazilian children's literature and creator of the Sítio do Picapau Amarelo universe.

```python
# Teaching capabilities
KidsProgrammingAgent:
- Explains programming concepts through Sítio do Picapau Amarelo storytelling
- Variables as "Emília's magic boxes", loops as "Saci jumping repeatedly"
- Functions as "Tia Nastacia's recipes", conditionals as "Pedrinho's decisions"
- Safe content filtering via BaseKidsAgent (BLOCKED_TOPICS, topic allowlist)
- Fallback responses for offline/error scenarios

# Routing
- Invoked by Ayrton Senna for children's education queries
- Responses capped at 150 words, always in simple language
```

**Key Methods:**
- `_get_fallback_response()` - Returns pre-written explanations for common concepts
- `_get_safe_redirect_response()` - Redirects off-topic or unsafe content

### 8. **Machado de Assis** - Textual Analyst (Document Master)
**Cultural Reference**: Machado de Assis - greatest Brazilian writer and literary genius

```python
# Document processing capabilities
TextualAnalyst:
- Document classification: contracts, laws, decrees
- Named Entity Recognition: organizations, values, dates
- Suspicious clause identification using regex patterns
- Legal compliance checking against frameworks
- Readability assessment (Portuguese-adapted Flesch)
- Transparency scoring based on document clarity

# NLP pipeline
1. Document classification and structure analysis
2. Named entity extraction and relationship mapping
3. Suspicious pattern detection in legal text
4. Compliance validation against regulatory frameworks
5. Readability and transparency scoring
```

### 9. **José Bonifácio** - Policy Analyst (Institutional Architect)
**Cultural Reference**: José Bonifácio - Patriarch of Independence and institutional architect

```python
# Policy effectiveness evaluation
PolicyAnalyst:
- Efficacy assessment: Did the policy achieve its goals?
- Efficiency evaluation: Resource utilization analysis
- Effectiveness measurement: Impact vs. cost analysis
- Social Return on Investment (SROI) calculation
- Beneficiary impact analysis and coverage assessment
- Sustainability scoring (0-100 scale)

# Evaluation frameworks
- Logic Model: Inputs → Activities → Outputs → Outcomes
- Theory of Change: Causal pathway analysis
- Cost-Benefit Analysis: Economic impact assessment
- Social Impact Measurement: Beneficiary outcome tracking
```

### 10. **Dandara** - Social Justice Agent (Equity Guardian)
**Cultural Reference**: Dandara dos Palmares - warrior for social justice and equality

```python
# Equity monitoring capabilities
SocialJusticeAgent:
- Gini coefficient calculation for inequality measurement
- Equity violation detection using statistical methods
- Inclusion gap identification across demographics
- Distributive justice assessment
- Intersectional analysis capabilities
- Social vulnerability mapping

# Inequality indices
- Gini Coefficient: Income/resource distribution
- Atkinson Index: Inequality aversion measurement
- Theil Index: Decomposable inequality measure
- Palma Ratio: Top 10% vs. bottom 40% comparison
```

### 11. **Obaluaiê** - Corruption Detector (Systemic Pattern Analyst)
**Cultural Reference**: Obaluaiê — Yoruba deity of disease and healing, associated with uncovering hidden afflictions

```python
# Corruption detection capabilities
CorruptionDetectorAgent:
- Cartel detection via Social Network Analysis (Louvain algorithm)
- Benford's Law analysis: P(d) = log₁₀(1 + 1/d) for bid manipulation
- Money laundering detection via Graph Neural Networks
- Nepotism detection through relationship graph analysis
- Transparency scoring (Transparency Corruption Index — TCI)
- Deep Neural Network (LSTM) + Isolation Forest for anomaly detection

# Performance metrics
- Precision: >92% on known corruption schemes
- Recall:    >88% on suspicious patterns
- F1-Score:  >0.90 on alert classification
- False positives: <5% for CRITICAL alerts
```

**Data Sources:**
- Portal da Transparência — contracts, bids, expenditures
- CNJ — related judicial proceedings
- TCU — audit reports and irregularities
- COAF — suspicious financial transaction reports

**Severity Levels:** `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`

### 12. **Oxóssi** - Fraud Hunter (Precision Detector)

**Cultural Reference**: Oxóssi — Yoruba deity of the hunt, known for precision and focus

```python
# Fraud detection capabilities
OxossiAgent:
- Bid rigging detection via contract similarity (threshold: 0.85)
- Price fixing via standard deviation analysis (threshold: 2.5σ)
- Phantom vendor detection using activity thresholds
- Invoice fraud detection with confidence scoring
- Kickback scheme identification through financial forensics
- Conflict of interest and money laundering pattern analysis

# Fraud severity levels
- LOW / MEDIUM / HIGH / CRITICAL
```

**Fraud Types Detected:**
- `BID_RIGGING` - Coordinated bidding between supposed competitors
- `PRICE_FIXING` - Statistical price outliers across vendors
- `PHANTOM_VENDOR` - Shell companies with no real activity
- `INVOICE_FRAUD` - Anomalous invoice patterns
- `KICKBACK_SCHEME` - Circular payment detection

### 13. **Drummond** - Communication Agent (Conversational Interface)
**Cultural Reference**: Carlos Drummond de Andrade — greatest Brazilian poet, known for clarity and wit

```python
# Communication capabilities
DrummondAgent:
- Multi-channel messaging (chat, email, notifications)
- Conversational interface for citizen queries
- Natural language response generation
- Context-aware dialog management

# Variants
- drummond.py        — Full agent with LLM-backed responses
- drummond_simple.py — Lightweight rule-based version for low-latency paths
```

### 14. **Maria Quitéria** - Security Auditor (System Protector)
**Cultural Reference**: Maria Quitéria de Jesus — first Brazilian woman to serve in the military, symbol of courage

```python
# Security capabilities
MariaQuiteria:
- Input validation and sanitization across all endpoints
- Permission and role validation
- Rate limiting enforcement per agent
- Audit logging of all sensitive agent actions
- Compliance checking against security frameworks
```

### 15. **Oscar Niemeyer** - Data Aggregator (Visualization Architect)
**Cultural Reference**: Oscar Niemeyer (1907–2012) — architect of Brasília, master of bold structural design

```python
# Data aggregation capabilities
OscarNiemeyerAgent:
- Aggregates results from multiple agents into unified structures
- Builds visualization-ready data schemas
- Coordinates data architecture for dashboard consumption
```

### 16. **Lampião** - Regional Analyst (Territorial Specialist)
**Cultural Reference**: Virgulino Ferreira da Silva (Lampião) — legendary cangaceiro, deep roots in the Brazilian Northeast

```python
# Regional analysis capabilities
LampiaoAgent:
- State and municipal-level spending analysis
- Regional inequality detection across Brazilian territories
- Cross-region pattern comparison
- Focus on underserved and remote municipalities
```

### 17. **Ceuci** - ETL Specialist (Data Engineer + ML)
**Cultural Reference**: Ceuci — indigenous deity of fertility and abundance in Tupi mythology

```python
# ETL and ML capabilities
CeuciAgent:
- Data extraction, transformation, and loading pipelines
- ML-based predictions (via ceuci_ml_models.py)
- Data quality validation and anomaly pre-processing
- Feeds cleaned datasets to investigator and analyst agents
```

### 18. **Santos-Dumont** - System Educator (Onboarding Guide)
**Cultural Reference**: Alberto Santos-Dumont (1873–1932) — inventor of the 14-Bis, pioneer who shared his inventions freely

```python
# Educational capabilities
EducatorAgent:
- System architecture walkthrough for interns and new contributors
- Agent-by-agent capability explanations
- API structure overview (323+ endpoints, 39 routes)
- Contribution guide: commits, tests, PR workflow
- Troubleshooting common development issues

# Teaching philosophy
"O que eu fiz, qualquer um pode fazer" — democratising knowledge
```

**Learning Topics:**
- `SYSTEM_OVERVIEW` - Multi-agent architecture and flows
- `AGENT_ARCHITECTURE` - BaseAgent patterns and lifecycle
- `API_STRUCTURE` - Endpoints, middleware, auth, SSE
- `CONTRIBUTION_GUIDE` - First commit to merged PR
- `FIRST_MISSION` - Guided first task for new interns

### 19. **Lina Bo Bardi** - Frontend Design Guide (Integration Architect)
**Cultural Reference**: Lina Bo Bardi (1914–1992) — Italian-Brazilian architect of MASP and SESC Pompeia, champion of accessible design

```python
# Frontend guidance capabilities
FrontendDesignerAgent:
- SSE integration guide for /api/v1/chat/stream
- React/Vue/Angular component structure patterns
- Accessibility (WCAG, VLibras, semantic HTML)
- Responsive design and mobile-first patterns
- Error handling and reconnection strategies

# Design philosophy
"Design deve ser acessível a TODOS" — functionality over elitism
```

**Frontend Topics:**
- `SSE_INTEGRATION` - Consuming streaming chat events
- `COMPONENT_STRUCTURE` - Reusable component patterns
- `ACCESSIBILITY` - WCAG compliance and VLibras
- `RESPONSIVE_DESIGN` - Mobile-first layouts

### 20. **Tarsila do Amaral** - Kids Design Educator
**Cultural Reference**: Tarsila do Amaral (1886–1973) — painter of Abaporu and icon of Brazilian Modernism

```python
# Kids design teaching capabilities
KidsDesignAgent (BaseKidsAgent):
- Teaches colors, shapes, contrast, harmony, and balance to children
- Uses her own paintings as visual metaphors (Abaporu, Operários)
- Tropical color palette references from Brazilian nature
- Safe content filtering inherited from BaseKidsAgent

# Teaching metaphors
- Warm colors → "energia do sol brasileiro"
- Cool colors → "tranquilidade da água"
- Abaporu → oversized shapes conveying strength
```

## 🔄 Agent Lifecycle & State Management

### Agent States
```python
class AgentStatus(Enum):
    IDLE = "idle"                    # Ready for new tasks
    PROCESSING = "processing"        # Currently executing
    REFLECTING = "reflecting"        # Self-assessment phase
    WAITING = "waiting"             # Waiting for dependencies
    COMPLETED = "completed"         # Task finished successfully
    ERROR = "error"                 # Execution failed
    TIMEOUT = "timeout"             # Execution exceeded time limit
```

### State Transitions
```python
# Normal execution flow
IDLE → PROCESSING → COMPLETED
     ↓           ↓
   ERROR    REFLECTING → PROCESSING (adaptive retry)
             ↓
           COMPLETED (after improvement)

# Timeout handling
PROCESSING → TIMEOUT → ERROR (cleanup)
```

## 🧪 Self-Reflection Mechanisms

### Quality Assessment Framework
```python
class ReflectionMetrics:
    confidence_score: float     # Result confidence (0-1)
    completeness: float        # Investigation thoroughness (0-1)  
    consistency: float         # Internal consistency (0-1)
    novelty: float            # New insights discovered (0-1)
    actionability: float      # Practical usefulness (0-1)

# Reflection triggers
if overall_quality < reflection_threshold:
    reflect_and_improve()
```

### Adaptive Strategies
```python
# Strategy adaptation based on reflection
ReflectionResult:
- quality_issues: List[str]    # Identified problems
- improvement_plan: str        # How to improve
- strategy_adjustments: Dict   # Parameter changes
- confidence_boost: float     # Expected improvement

# Example adaptations
Low confidence → Increase data sampling
Missing patterns → Add analysis techniques  
Incomplete coverage → Expand search criteria
```

## 💾 Memory Architecture

### Multi-Layer Memory System
```python
# Episodic Memory - Specific events and investigations
EpisodicMemory:
- investigation_results: Dict[str, InvestigationResult]
- agent_interactions: List[AgentMessage]  
- user_queries: List[QueryContext]
- temporal_indexing: Dict[datetime, List[str]]

# Semantic Memory - General knowledge and patterns
SemanticMemory:
- anomaly_patterns: Dict[str, PatternTemplate]
- organization_profiles: Dict[str, OrgProfile]
- vendor_behaviors: Dict[str, VendorProfile]  
- legal_knowledge: Dict[str, LegalConcept]

# Conversational Memory - Dialog context
ConversationalMemory:
- user_preferences: Dict[str, Any]
- conversation_history: List[Message]
- context_stack: List[Context]
- session_metadata: Dict[str, Any]
```

### Memory Operations
```python
# Memory storage with importance weighting
await memory_agent.store_episodic(
    event="investigation_completed",  
    data=investigation_result,
    importance=0.9,  # High importance
    decay_rate=0.1   # Slow decay
)

# Semantic retrieval with vector search
similar_patterns = await memory_agent.retrieve_semantic(
    query_vector=embedding,
    similarity_threshold=0.8,
    max_results=10
)

# Conversational context maintenance
context = await memory_agent.get_conversation_context(
    user_id="user123",
    lookback_messages=20
)
```

## 🛡️ Security & Ethics

### Agent Security Framework
```python
# Input validation and sanitization
@security_guard
async def process_investigation(query: str) -> InvestigationResult:
    # 1. Input sanitization
    sanitized_query = sanitize_input(query)
    
    # 2. Permission validation  
    validate_permissions(user_context)
    
    # 3. Rate limiting per agent
    await rate_limiter.check_agent_limits(agent_name)
    
    # 4. Audit logging
    await audit_logger.log_agent_action(...)

# Ethics guard - prevents harmful analyses
EthicsGuard:
- prevent_privacy_violations()
- ensure_transparency_goals()  
- validate_public_interest()
- block_discriminatory_analysis()
```

### Audit Trail
```python
# Complete agent action logging
AgentAuditEvent:
- agent_name: str                # Which agent
- action: str                   # What action
- input_data: Dict             # Input parameters (sanitized)
- output_summary: str          # Output summary (no sensitive data)
- success: bool                # Success/failure
- processing_time: float       # Performance metrics
- timestamp: datetime          # When it occurred
- user_context: UserContext    # Who requested it
```

## 🧪 Testing Strategy

### Agent Testing Framework
```python
# Unit tests for individual agent logic
@pytest.mark.unit
async def test_investigator_price_anomaly_detection():
    agent = InvestigatorAgent()
    data = create_test_contracts_with_price_anomaly()
    
    result = await agent.detect_price_anomalies(data)
    
    assert len(result.anomalies) == 1
    assert result.anomalies[0].type == "PRICE_ANOMALY"
    assert result.anomalies[0].confidence > 0.8

# Integration tests for agent communication
@pytest.mark.integration  
async def test_master_agent_investigation_workflow():
    master = MasterAgent()
    investigator = InvestigatorAgent()
    reporter = ReporterAgent()
    
    # Register agents
    master.register_agent("investigator", investigator)
    master.register_agent("reporter", reporter)
    
    # Execute full workflow
    result = await master.conduct_investigation(
        query="Analyze suspicious contracts",
        agents=["investigator", "reporter"]
    )
    
    assert result.status == "completed"
    assert len(result.findings) > 0
    assert result.report is not None
```

### Mock Agent System
```python
# Mock agents for testing without external dependencies
class MockInvestigatorAgent(InvestigatorAgent):
    async def detect_anomalies(self, data):
        # Return predictable test results
        return create_mock_anomaly_results()

# Test fixtures with realistic data
@pytest.fixture
def sample_investigation_data():
    return {
        "contracts": create_test_contracts(count=1000),
        "vendors": create_test_vendors(count=100),
        "organizations": create_test_organizations(count=50)
    }
```

## 📊 Performance Metrics

### Agent Performance Monitoring
```python
# Performance metrics per agent
AgentMetrics:
- average_processing_time: float    # Mean execution time
- success_rate: float              # Success percentage
- reflection_frequency: float      # How often reflection occurs
- quality_scores: List[float]      # Historical quality metrics
- memory_usage: float             # Memory consumption
- cache_hit_rate: float           # Cache efficiency

# System-wide metrics
SystemMetrics:
- total_investigations: int        # Total investigations completed
- average_coordination_time: float # Master agent coordination time
- agent_utilization: Dict[str, float] # Per-agent usage
- error_rates: Dict[str, float]   # Per-agent error rates
```

### Scaling Patterns
```python
# Horizontal scaling with agent pools
AgentPool:
- pool_size: int = 5              # Number of agent instances
- load_balancing: str = "round_robin"  # Distribution strategy
- health_checks: bool = True      # Monitor agent health
- auto_scaling: bool = True       # Dynamic scaling based on load

# Vertical scaling with resource limits
ResourceLimits:
- max_memory_mb: int = 1024       # Memory limit per agent
- max_processing_time: int = 300  # Timeout in seconds
- max_concurrent_tasks: int = 10  # Concurrent task limit
```

## 🚀 Development & Deployment

### Local Development
```bash
# Run individual agent tests
pytest tests/unit/agents/test_investigator.py -v

# Run multi-agent integration tests  
pytest tests/integration/agents/ -v

# Performance testing with realistic data
pytest tests/performance/agents/ --benchmark-only

# Memory profiling
pytest tests/agents/ --memray
```

### Agent Configuration
```python
# Environment-specific agent configuration
AgentConfig:
    reflection_threshold: float = 0.8    # Quality threshold
    max_reflection_loops: int = 3        # Max improvement iterations
    memory_retention_days: int = 90      # Memory retention period
    enable_learning: bool = False        # Online learning (experimental)
    parallel_processing: bool = True     # Concurrent agent execution
    
# Per-agent configuration
INVESTIGATOR_CONFIG = {
    "anomaly_threshold": 2.5,           # Standard deviations for anomalies
    "similarity_threshold": 0.85,       # Duplicate detection threshold
    "max_records_per_batch": 10000     # Batch processing size
}
```

### Docker Deployment
```dockerfile
# Multi-agent container with resource limits
FROM python:3.11-slim

# Install agent dependencies
COPY requirements/agents.txt .
RUN pip install -r agents.txt

# Copy agent source code
COPY src/agents/ /app/agents/

# Resource limits for agent container
ENV MEMORY_LIMIT=2048MB
ENV CPU_LIMIT=2.0
ENV MAX_AGENTS=10

# Health check for agent system
HEALTHCHECK --interval=30s --timeout=10s \
  CMD python -c "from src.agents import health_check; health_check()"

CMD ["python", "-m", "src.agents.orchestrator"]
```

## 🔮 Future Enhancements

### Planned Features
- **Federated Learning**: Agents learn from distributed investigations
- **Dynamic Agent Creation**: Generate specialized agents for new domains
- **Cross-Language Support**: Multi-language document analysis
- **Real-time Collaboration**: Simultaneous multi-agent processing
- **Explainable AI**: Enhanced transparency in agent decision-making

### Research Areas
- **Agent Personality Development**: More sophisticated cultural personas
- **Emotional Intelligence**: Agents that understand social context
- **Creative Problem Solving**: Novel approach generation for complex problems
- **Meta-Learning**: Agents that improve their learning strategies

---

This multi-agent system represents a unique approach to transparency analysis, combining cutting-edge AI with Brazilian cultural identity to create agents that are both technically sophisticated and culturally meaningful. Each agent contributes specialized expertise while working together through advanced coordination patterns to democratize access to government transparency analysis.