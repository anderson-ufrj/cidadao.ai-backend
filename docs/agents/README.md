# 🤖 Agentes - Cidadão.AI

**Autor**: Anderson Henrique da Silva  
**Última Atualização**: 2025-09-25 18:25:00 -03:00 (São Paulo, Brasil)

[English version below](#-agents---cidadãoai-english)

## 📊 Status Geral

**8 de 17 agentes totalmente operacionais** | **9 em desenvolvimento**

## ✅ Agentes Operacionais

### 🎯 Abaporu (Master Agent)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/abaporu.py`  
**Papel**: Mestre orquestrador de investigações

**Capacidades**:
- Coordenação de múltiplos agentes
- Planejamento de investigações adaptativo
- Auto-reflexão com qualidade mínima de 0.8
- Síntese de resultados multi-agente

**Exemplo de uso**:
```python
master = MasterAgent()
result = await master.process(
    "Investigar contratos suspeitos do órgão 26000"
)
```

### 🔍 Zumbi dos Palmares (Investigator)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/zumbi.py`  
**Papel**: Especialista em detecção de anomalias

**Capacidades**:
- Detecção de anomalias de preço (2.5 desvios padrão)
- Análise de concentração de fornecedores (>70%)
- Detecção de contratos duplicados (>85% similaridade)
- Análise espectral FFT para padrões periódicos
- Identificação de irregularidades em pagamentos

**Thresholds configuráveis**:
```python
PRICE_ANOMALY_THRESHOLD = 2.5  # desvios padrão
VENDOR_CONCENTRATION_THRESHOLD = 0.7  # 70%
DUPLICATE_THRESHOLD = 0.85  # 85% similaridade
```

### 📊 Anita Garibaldi (Analyst)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/anita.py`  
**Papel**: Análise de padrões e tendências

**Capacidades**:
- Análise de tendências com regressão linear
- Comparação entre organizações similares
- Detecção de padrões sazonais
- Análise cross-espectral
- Cálculo de métricas de eficiência

**Métodos principais**:
```python
analyze_spending_trends()
analyze_organizational_patterns()
detect_seasonal_patterns()
calculate_efficiency_metrics()
```

### 📝 Tiradentes (Reporter)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/tiradentes.py`  
**Papel**: Geração de relatórios em linguagem natural

**Capacidades**:
- Relatórios multi-formato (MD, HTML, PDF, JSON)
- Adaptação por audiência (técnica, executiva, pública)
- Suporte multi-idioma (PT, EN, ES)
- Priorização de riscos
- Visualizações de dados

**Formatos suportados**:
```python
ReportFormat.MARKDOWN
ReportFormat.HTML
ReportFormat.PDF
ReportFormat.JSON
```

### 🏎️ Ayrton Senna (Router)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/ayrton_senna.py`  
**Papel**: Roteamento semântico inteligente

**Capacidades**:
- Roteamento baseado em regras com regex
- Análise de similaridade semântica
- Detecção de intenções
- Estratégias de fallback
- Matching de capacidades dos agentes

**Intenções detectadas**:
- `investigate`: Investigações complexas
- `analyze`: Análises específicas
- `report`: Geração de relatórios
- `greeting`: Saudações
- `help`: Ajuda e informações

### 🧠 Nanã (Memory)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/nana.py`  
**Papel**: Gestão de memória multi-camadas

**Capacidades**:
- Memória episódica (investigações)
- Memória semântica (conhecimento)
- Memória conversacional (contexto)
- Recuperação vetorial com ChromaDB
- Scoring de importância

**Tipos de memória**:
```python
MemoryType.EPISODIC    # Eventos específicos
MemoryType.SEMANTIC    # Conhecimento geral
MemoryType.PROCEDURAL  # Processos
```

### ⚖️ José Bonifácio (Policy)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/bonifacio.py`  
**Papel**: Avaliação de eficácia de políticas

**Capacidades**:
- Avaliação de eficácia
- Análise de eficiência
- Cálculo de ROI social
- Scoring de sustentabilidade
- Análise de impacto em beneficiários

### 📚 Machado de Assis (Text)
**Status**: ✅ Totalmente implementado  
**Arquivo**: `src/agents/machado.py`  
**Papel**: Análise textual avançada

**Capacidades**:
- Classificação de documentos
- Reconhecimento de Entidades (NER)
- Detecção de cláusulas suspeitas
- Verificação de compliance legal
- Avaliação de legibilidade

## 🚧 Agentes em Desenvolvimento

### 🛡️ Dandara (Social Justice)
**Status**: 🚧 Parcialmente implementado  
**Arquivo**: `src/agents/dandara.py`  
**Papel**: Monitoramento de justiça social e equidade

**Planejado**:
- Análise de distribuição de recursos
- Detecção de discriminação
- Coeficiente de Gini
- Análise interseccional

### 🌍 Lampião (Regional)
**Status**: 🚧 Parcialmente implementado  
**Arquivo**: `src/agents/lampiao.py`  
**Papel**: Análise de dados regionais

**Planejado**:
- Comparações regionais
- Detecção de disparidades
- Análise geoespacial
- Padrões migratórios de recursos

### 🔒 Maria Quitéria (Security)
**Status**: 🚧 Parcialmente implementado  
**Arquivo**: `src/agents/maria_quiteria.py`  
**Papel**: Auditoria de segurança

**Planejado**:
- Auditoria de controles
- Detecção de vulnerabilidades
- Análise de compliance
- Monitoramento de acessos

### 🏗️ Oscar Niemeyer (Visualization)
**Status**: 🚧 Estrutura básica  
**Arquivo**: `src/agents/oscar_niemeyer.py`  
**Papel**: Arquiteto de visualização de dados

### 💬 Drummond (Communication)
**Status**: 🚧 Desabilitado (problemas no HF Spaces)  
**Arquivo**: `src/agents/drummond.py`  
**Papel**: Comunicação multi-canal

### 💬 Drummond Simple
**Status**: ✅ Implementação simplificada  
**Arquivo**: `src/agents/drummond_simple.py`  
**Papel**: Chat básico para HuggingFace

### 🔄 Ceúci (ETL)
**Status**: 🚧 Parcialmente implementado  
**Arquivo**: `src/agents/ceuci.py`  
**Papel**: Especialista em ETL

### 🏥 Obaluaié (Health)
**Status**: 🚧 Estrutura básica  
**Arquivo**: `src/agents/obaluaie.py`  
**Papel**: Monitor de saúde do sistema

### 🎯 Oxossi (Hunter)
**Status**: 🚧 Estrutura básica  
**Arquivo**: `src/agents/oxossi.py`  
**Papel**: Caçador de dados

---

# 🤖 Agents - Cidadão.AI (English)

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-25 18:25:00 -03:00 (São Paulo, Brazil)

## 📊 Overall Status

**8 of 17 agents fully operational** | **9 in development**

## ✅ Operational Agents

### 🎯 Abaporu (Master Agent)
**Status**: ✅ Fully implemented  
**File**: `src/agents/abaporu.py`  
**Role**: Master investigation orchestrator

**Capabilities**:
- Multi-agent coordination
- Adaptive investigation planning
- Self-reflection with 0.8 quality threshold
- Multi-agent result synthesis

### 🔍 Zumbi dos Palmares (Investigator)
**Status**: ✅ Fully implemented  
**File**: `src/agents/zumbi.py`  
**Role**: Anomaly detection specialist

**Capabilities**:
- Price anomaly detection (2.5 std dev)
- Supplier concentration analysis (>70%)
- Duplicate contract detection (>85% similarity)
- FFT spectral analysis for periodic patterns
- Payment irregularity identification

### 📊 Anita Garibaldi (Analyst)
**Status**: ✅ Fully implemented  
**File**: `src/agents/anita.py`  
**Role**: Pattern and trend analysis

**Capabilities**:
- Trend analysis with linear regression
- Cross-organizational comparison
- Seasonal pattern detection
- Cross-spectral analysis
- Efficiency metrics calculation

### 📝 Tiradentes (Reporter)
**Status**: ✅ Fully implemented  
**File**: `src/agents/tiradentes.py`  
**Role**: Natural language report generation

**Capabilities**:
- Multi-format reports (MD, HTML, PDF, JSON)
- Audience adaptation (technical, executive, public)
- Multi-language support (PT, EN, ES)
- Risk prioritization
- Data visualizations

### 🏎️ Ayrton Senna (Router)
**Status**: ✅ Fully implemented  
**File**: `src/agents/ayrton_senna.py`  
**Role**: Intelligent semantic routing

**Capabilities**:
- Rule-based routing with regex
- Semantic similarity analysis
- Intent detection
- Fallback strategies
- Agent capability matching

### 🧠 Nanã (Memory)
**Status**: ✅ Fully implemented  
**File**: `src/agents/nana.py`  
**Role**: Multi-layer memory management

**Capabilities**:
- Episodic memory (investigations)
- Semantic memory (knowledge)
- Conversational memory (context)
- Vector retrieval with ChromaDB
- Importance scoring

### ⚖️ José Bonifácio (Policy)
**Status**: ✅ Fully implemented  
**File**: `src/agents/bonifacio.py`  
**Role**: Policy effectiveness evaluation

**Capabilities**:
- Effectiveness assessment
- Efficiency analysis
- Social ROI calculation
- Sustainability scoring
- Beneficiary impact analysis

### 📚 Machado de Assis (Text)
**Status**: ✅ Fully implemented  
**File**: `src/agents/machado.py`  
**Role**: Advanced text analysis

**Capabilities**:
- Document classification
- Named Entity Recognition (NER)
- Suspicious clause detection
- Legal compliance checking
- Readability assessment

## 🚧 Agents in Development

[Same agents as Portuguese section with English descriptions]