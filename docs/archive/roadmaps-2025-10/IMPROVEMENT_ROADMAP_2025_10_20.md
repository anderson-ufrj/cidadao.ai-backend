# Roadmap de Melhorias - Cidadão.AI Backend
**Data**: 20 de Outubro de 2025, 17:15
**Análise por**: Anderson Henrique da Silva
**Status do Projeto**: Produção (Railway) - 99.9% uptime

---

## 📊 Estado Atual Verificado

### Métricas Reais (Análise Completa 20/10/2025)
| Métrica | Valor Atual | Meta | Gap |
|---------|-------------|------|-----|
| **Agentes Tier 1** | 10/16 (63%) | 16/16 (100%) | -6 agentes |
| **Cobertura de Testes** | ~40% | 80% | **-40pp** 🔴 |
| **Agentes Testados** | 12/16 (75%) | 16/16 (100%) | -4 agentes |
| **Uptime Produção** | 99.9% | 99.9% | ✅ Meta atingida |
| **APIs Funcionando** | 266+ endpoints | - | ✅ Completo |
| **Documentação** | 100% agentes | 100% | ✅ Excelente |

### Descobertas Críticas

#### 🎯 Pontos Fortes
1. **Produção Estável** - Railway com 99.9% uptime desde 07/10/2025
2. **10 Agentes Operacionais** - Tier 1 com implementação sólida
3. **API Robusta** - 266+ endpoints com SSE, autenticação, rate limiting
4. **Infraestrutura Completa** - PostgreSQL, Redis, Celery, Prometheus configurados
5. **Documentação Honesta** - IMPLEMENTATION_REALITY.md reconhece gaps

#### ⚠️ Gaps Críticos Identificados
1. **Oxóssi sem testes** - 1,698 LOC de detecção de fraude, **ZERO arquivos de teste**
2. **Cobertura real 40%** - Documentação afirma 80%, realidade é 40% (gap de 40pp)
3. **5 agentes Tier 2 incompletos** - 50-70% implementados, frameworks prontos
4. **Dados simulados** - Vários agentes usam `asyncio.sleep()` + valores aleatórios
5. **Modelos ML ausentes** - Céuci tem framework detalhado mas sem modelos treinados
6. **Instrumentação pendente** - Prometheus configurado, código Python não instrumentado

---

## 🔥 PRIORIDADE 1: Semana Atual (21-27 Out 2025)

### 1.1 🧪 Criar Suite de Testes para Oxóssi
**Impacto**: CRÍTICO | **Esforço**: 8-12 horas | **Status**: 🔴 Bloqueante

**Problema**: Oxóssi implementa 7 padrões de fraude (licitação direcionada, fornecedores fantasma, cartelização, etc.) mas está completamente sem testes.

**Ação**:
```bash
# Criar arquivo de teste completo
touch tests/unit/agents/test_oxossi.py

# Template mínimo necessário
pytest tests/unit/agents/test_oxossi.py -v --cov=src.agents.oxossi --cov-report=html
```

**Checklist de Testes Essenciais**:
- [ ] `test_detect_bid_rigging()` - Padrão de licitação direcionada
- [ ] `test_identify_phantom_vendors()` - Fornecedores fantasma
- [ ] `test_price_fixing_detection()` - Cartelização de preços
- [ ] `test_invoice_fraud_patterns()` - Fraude em notas fiscais
- [ ] `test_conflict_of_interest()` - Conflito de interesses
- [ ] `test_shell_company_detection()` - Empresas de fachada
- [ ] `test_payment_splitting()` - Fracionamento de pagamentos
- [ ] `test_integration_with_zumbi()` - Integração com anomalias
- [ ] `test_edge_cases()` - Casos extremos e validação

**Resultado Esperado**: Cobertura de Oxóssi de 0% → 75%+

---

### 1.2 📏 Medir Cobertura Real e Documentar Gaps
**Impacto**: ALTO | **Esforço**: 2-4 horas | **Status**: 🟡 Importante

**Problema**: Documentação afirma 80% de cobertura, realidade é ~40%. Gap de transparência.

**Ação**:
```bash
# Executar relatório completo
JWT_SECRET_KEY=test SECRET_KEY=test pytest --cov=src --cov-report=html --cov-report=term

# Gerar badge de cobertura
pip install coverage-badge
coverage-badge -o docs/badges/coverage.svg
```

**Entregáveis**:
1. **Relatório HTML** em `htmlcov/index.html` com drill-down por módulo
2. **Badge de cobertura** em `docs/badges/coverage.svg`
3. **Documento de gaps** listando:
   - Módulos com <60% cobertura
   - Funções críticas sem testes
   - Priorização por impacto

**Atualizar**:
- `README.md` - Badge real de cobertura
- `CLAUDE.md` - Métricas honestas
- `docs/project/CURRENT_STATUS_2025_10.md` - Números verificados

---

### 1.3 🔍 Instrumentar Métricas Prometheus no Código
**Impacto**: ALTO | **Esforço**: 6-8 horas | **Status**: 🟡 Infraestrutura pronta

**Problema**: Grafana e Prometheus configurados, mas código Python não expõe métricas.

**Ação**:
```bash
# Adicionar prometheus_client
echo "prometheus_client==0.19.0" >> requirements.txt
make install-dev
```

**Implementação**:

1. **Métricas de Agentes** (`src/agents/metrics_wrapper.py`):
```python
from prometheus_client import Counter, Histogram, Gauge

# Contadores
agent_invocations = Counter('agent_invocations_total', 'Total agent calls', ['agent_id'])
agent_errors = Counter('agent_errors_total', 'Agent errors', ['agent_id', 'error_type'])

# Histogramas (latência)
agent_duration = Histogram('agent_duration_seconds', 'Agent processing time', ['agent_id'])

# Gauges (estado atual)
active_investigations = Gauge('active_investigations', 'Current investigations running')
```

2. **Métricas de API** (`src/api/middleware/metrics_middleware.py`):
```python
from prometheus_client import Counter, Histogram

http_requests = Counter('http_requests_total', 'HTTP requests', ['method', 'endpoint', 'status'])
http_duration = Histogram('http_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
```

3. **Endpoint de Métricas** (`src/api/routes/monitoring.py`):
```python
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

**Verificação**:
```bash
# Iniciar aplicação
make run-dev

# Testar endpoint
curl http://localhost:8000/health/metrics

# Verificar Prometheus
curl http://localhost:9090/api/v1/targets
```

**Dashboards Grafana a Atualizar**:
- `agent_performance.json` - Latência e throughput por agente
- `api_metrics.json` - Requisições HTTP, erros, p95/p99
- `investigation_metrics.json` - Investigações ativas, taxa de conclusão

---

## 📈 PRIORIDADE 2: Próximas 2 Semanas (28 Out - 10 Nov 2025)

### 2.1 🧪 Expandir Cobertura de Testes: 40% → 65%
**Impacto**: ALTO | **Esforço**: 20-30 horas | **Status**: 🟡 Planejado

**Estratégia por Prioridade**:

#### Fase 1: Agentes Críticos sem Testes (8 horas)
1. **Lampião** (1,587 LOC) - Análise regional
   - Criar `tests/unit/agents/test_lampiao.py`
   - Testar Gini, Theil, Williamson indices
   - Validar análise de 27 estados brasileiros

2. **Oscar Niemeyer** (1,228 LOC) - Visualização
   - Expandir `tests/unit/agents/test_oscar_niemeyer.py`
   - Testar geração Plotly, NetworkX, mapas geográficos
   - Validar layouts de dashboard

#### Fase 2: Agentes com Testes Insuficientes (12 horas)
3. **Maria Quitéria** (2,589 LOC) - Segurança
   - Expandir teste único para cobertura completa
   - Testar MITRE ATT&CK, UEBA, compliance LGPD
   - Validar relatórios de auditoria

4. **Céuci** (1,697 LOC) - ML/Predictivo
   - Criar testes para framework (mesmo sem modelos)
   - Mockar predições ARIMA, LSTM, Prophet
   - Validar API de inferência

5. **Obaluaiê** (829 LOC) - Corrupção
   - Criar suite completa de testes
   - Implementar Benford's Law tests
   - Validar detecção de padrões suspeitos

#### Fase 3: Serviços Críticos (10 horas)
6. **Orchestration System** (`src/services/orchestration/`)
   - Expandir testes de integração
   - Testar intent classification, entity extraction
   - Validar data federation com circuit breakers

7. **Cache Service** (`src/services/cache_service.py`)
   - Testar estratégia multi-layer (memory → Redis → DB)
   - Validar TTL e invalidação
   - Testar failover automático

**Meta**: 40% → 65% cobertura (+25pp)

---

### 2.2 🔄 Remover Dados Simulados dos Agentes Tier 2
**Impacto**: MÉDIO | **Esforço**: 15-20 horas | **Status**: 🟡 Técnico

**Problema**: Vários agentes usam `asyncio.sleep()` + valores aleatórios em vez de análises reais.

**Agentes a Refatorar**:

#### 1. **Dandara** (788 LOC) - Social Justice
**Localizações**:
- `src/agents/dandara.py:450-470` - Cálculo Gini simulado
- `src/agents/dandara.py:520-540` - Integração IBGE/DataSUS fake

**Refatoração**:
```python
# ANTES (simulado)
async def calculate_gini(self, data):
    await asyncio.sleep(2)  # Fake processing
    return random.uniform(0.4, 0.6)  # Random Gini

# DEPOIS (real)
async def calculate_gini(self, data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    cumsum = np.cumsum(sorted_data)
    return (2 * sum((i+1) * val for i, val in enumerate(sorted_data))) / (n * cumsum[-1]) - (n+1)/n
```

#### 2. **Obaluaiê** (829 LOC) - Corruption Detection
**Localizações**:
- `src/agents/obaluaie.py:350-380` - Benford's Law não implementada
- `src/agents/obaluaie.py:420-450` - Análise de padrões simulada

**Implementar**:
```python
async def benfords_law_analysis(self, amounts: List[float]) -> Dict:
    """Implementar teste real de Benford's Law."""
    first_digits = [int(str(abs(a))[0]) for a in amounts if a > 0]
    observed = Counter(first_digits)

    # Expected distribution (Benford)
    expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}

    # Chi-square test
    chi_square = sum((observed[d] - expected[d] * len(first_digits))**2 /
                     (expected[d] * len(first_digits)) for d in range(1, 10))

    return {
        "chi_square": chi_square,
        "p_value": 1 - stats.chi2.cdf(chi_square, 8),
        "suspicious": chi_square > 15.507  # p=0.05, df=8
    }
```

#### 3. **Nanã** (963 LOC) - Memory System
**Problema**: Usa memória in-memory, ignora PostgreSQL/Redis

**Refatoração**:
- Integrar `SQLAlchemy` para memória episódica persistente
- Usar `Redis` para cache de contexto conversacional
- Implementar pattern learning com histórico real

**Esforço estimado**: 6-8 horas por agente = 18-24 horas total

---

### 2.3 🎓 Treinar e Integrar Modelos ML para Céuci
**Impacto**: MÉDIO | **Esforço**: 30-40 horas | **Status**: 🟠 Projeto maior

**Problema**: Céuci tem documentação excelente (1,697 LOC) mas 0% de implementação real.

**Plano de Implementação**:

#### Fase 1: Datasets e Preparação (8 horas)
1. **Coletar dados históricos**:
   - Portal da Transparência (últimos 5 anos)
   - PNCP (contratos públicos 2020-2025)
   - TCE-MG (licitações estaduais)

2. **Feature engineering**:
   - Séries temporais de valores contratuais
   - Features de sazonalidade (mês, trimestre)
   - Lag features (valores passados)
   - Rolling statistics (médias móveis)

#### Fase 2: Treinamento de Modelos (12 horas)
1. **ARIMA** (Auto-Regressive Integrated Moving Average):
```python
from statsmodels.tsa.arima.model import ARIMA

def train_arima(data, order=(5,1,0)):
    model = ARIMA(data, order=order)
    fitted = model.fit()
    return fitted
```

2. **Prophet** (Facebook Time Series):
```python
from prophet import Prophet

def train_prophet(df):
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        changepoint_prior_scale=0.05
    )
    model.fit(df)
    return model
```

3. **LSTM** (Deep Learning):
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def train_lstm(X, y):
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(X.shape[1], X.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=50, batch_size=32)
    return model
```

#### Fase 3: Deploy e Integração (10 horas)
1. **Salvar modelos treinados**:
```bash
models/
├── arima_contracts_v1.pkl
├── prophet_spending_v1.pkl
└── lstm_anomalies_v1.h5
```

2. **API de inferência** (`src/agents/ceuci.py`):
```python
async def predict_next_quarter(self, historical_data):
    """Predição real usando modelos treinados."""
    # Carregar modelo apropriado
    model = self.load_model("arima_contracts_v1.pkl")

    # Fazer predição
    forecast = model.forecast(steps=3)  # 3 meses

    return {
        "predictions": forecast.tolist(),
        "confidence_intervals": model.conf_int().tolist(),
        "model": "ARIMA(5,1,0)",
        "trained_on": "2020-2025 contracts data"
    }
```

#### Fase 4: Validação e Testes (8 horas)
- Backtesting com dados de 2024
- Cross-validation temporal
- Métricas: MAE, RMSE, MAPE
- Testes de drift detection

**Entregáveis**:
- 3 modelos treinados e versionados
- API de predição funcional
- Testes automatizados com >75% cobertura
- Documentação de retreinamento

---

## 🚀 PRIORIDADE 3: Médio Prazo (Nov-Dez 2025)

### 3.1 🎭 Completar Agentes Tier 2 (50-70% → 95%+)
**Impacto**: ALTO | **Esforço**: 60-80 horas | **Status**: 🟠 Estratégico

#### Agente 1: **Abaporu** (Orquestrador Master)
**Status Atual**: 70% - Framework ReAct implementado, coordenação usa placeholders

**Melhorias Necessárias** (15 horas):
1. **Substituir asyncio.sleep()** por coordenação real:
```python
# ANTES
async def coordinate_agents(self, task):
    await asyncio.sleep(2)  # Fake coordination
    return {"status": "delegated"}

# DEPOIS
async def coordinate_agents(self, task):
    # Análise real de requisitos
    required_agents = await self._analyze_task_requirements(task)

    # Execução paralela real
    agent_pool = AgentPool()
    tasks = [agent_pool.get_agent(agent_id).process(task)
             for agent_id in required_agents]
    results = await asyncio.gather(*tasks)

    # Síntese de resultados
    return await self._synthesize_results(results)
```

2. **Implementar detecção de conflitos**:
   - Validar compatibilidade de agentes
   - Resolver dependências de execução
   - Implementar retry logic com backoff

3. **Adicionar telemetria de orquestração**:
   - Tempo de coordenação
   - Taxas de sucesso por combinação de agentes
   - Detecção de gargalos

#### Agente 2: **Nanã** (Sistema de Memória)
**Status Atual**: 65% - Estrutura de memória definida, sem persistência

**Melhorias Necessárias** (12 horas):
1. **Integrar PostgreSQL para memória episódica**:
```python
class EpisodicMemory:
    async def store_episode(self, episode: Dict):
        async with SessionLocal() as db:
            memory = Memory(
                type="episodic",
                content=episode,
                timestamp=datetime.now(),
                importance_score=self._calculate_importance(episode)
            )
            db.add(memory)
            await db.commit()
```

2. **Usar Redis para cache de contexto**:
```python
class ConversationalMemory:
    async def get_context(self, user_id: str, window: int = 10):
        cache_key = f"context:{user_id}"
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Buscar do banco
        context = await self._fetch_from_db(user_id, window)
        await redis.setex(cache_key, 300, json.dumps(context))
        return context
```

3. **Implementar pattern learning**:
   - Extrair padrões de investigações anteriores
   - Recomendar estratégias baseadas em histórico
   - Detecção de investigações similares

#### Agente 3: **Drummond** (Comunicação NLG)
**Status Atual**: 25% - Templates prontos, sem integração LLM

**Melhorias Necessárias** (18 horas):
1. **Integrar Maritaca/Claude para geração**:
```python
async def generate_narrative(self, data: Dict, style: str = "formal"):
    prompt = self._build_prompt(data, style)

    # Usar Maritaca (sabiazinho-3) para português natural
    response = await self.llm_client.generate(
        model="sabiazinho-3",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000
    )

    return response
```

2. **Implementar multicanal real**:
   - Email via SendGrid/AWS SES
   - Slack via Webhook
   - Discord via Bot API
   - WhatsApp via Twilio

3. **Sistema de templates dinâmicos**:
   - Templates Jinja2 com dados reais
   - Suporte a markdown, HTML, plain text
   - Personalização por stakeholder

#### Agente 4: **Obaluaiê** (Detecção de Corrupção)
**Status Atual**: 15% - Framework criado, algoritmos não implementados

**Melhorias Necessárias** (10 horas):
1. **Implementar Benford's Law** (já descrito na seção 2.2)
2. **Detecção de padrões de corrupção**:
   - Round-tripping (movimentações circulares)
   - Bid splitting (fracionamento de licitações)
   - Favoritism detection (favoritismo recorrente)
   - Ghost employees (funcionários fantasma)

3. **Integração com Oxóssi e Zumbi**:
   - Pipeline: Zumbi (anomalias) → Obaluaiê (corrupção) → Oxóssi (fraude)
   - Score agregado de suspeição
   - Priorização de investigações

**Total Estimado**: 60-80 horas para 5 agentes Tier 2

---

### 3.2 🔐 Fortalecer Segurança e Compliance
**Impacto**: ALTO | **Esforço**: 25-30 horas | **Status**: 🟠 Regulatório

**Motivação**: Sistema lida com dados públicos sensíveis, precisa compliance LGPD/ISO27001.

#### Melhorias Necessárias:

1. **Auditoria de Segurança Completa** (8 horas):
   - Scan de dependências: `pip-audit`, `safety check`
   - Análise estática: `bandit`, `semgrep`
   - Secrets detection: `truffleHog`, `gitleaks`
   - Container scanning: `trivy` para imagens Docker

2. **LGPD Compliance** (10 horas):
   - Implementar data retention policies (90 dias investigações)
   - Anonimização de CPF/CNPJ em logs
   - Direito ao esquecimento (API de deleção)
   - Consent management para dados pessoais
   - Data breach notification system

3. **Hardening de Infraestrutura** (7 horas):
   - Rate limiting por IP mais agressivo (10 req/min → 5 req/min)
   - Implementar IP reputation check (AbuseIPDB)
   - WAF rules para SQL injection, XSS
   - TLS 1.3 enforcement
   - Security headers (CSP, HSTS, X-Frame-Options)

4. **Logging e Forensics** (5 horas):
   - Structured logging com ELK stack
   - Audit trail completo (quem, quando, o quê)
   - Tamper-proof logs (hash chain)
   - SIEM integration readiness

**Entregáveis**:
- Relatório de auditoria de segurança
- Certificado de compliance LGPD
- Security.md com responsible disclosure
- Runbook de incident response

---

### 3.3 📊 Expandir Integração com APIs Estaduais
**Impacto**: MÉDIO | **Esforço**: 40-50 horas | **Status**: 🟡 Expansão

**Motivação**: Portal da Transparência tem 78% de endpoints bloqueados (403). Ampliar fontes.

#### Expansão de TCEs (Tribunais de Contas Estaduais):

**Atual**: 6 TCEs implementados (SP, RJ, MG, BA, PE, CE)
**Meta**: +8 TCEs (RS, PR, SC, GO, DF, MA, PA, AM)

**Template de Implementação** (5 horas por TCE):
```python
# src/services/transparency_apis/tce_apis/tce_rs_client.py
class TCERSClient:
    """Cliente para TCE-RS (Rio Grande do Sul)."""

    BASE_URL = "https://portaltransparencia.tce.rs.gov.br/api/v1"

    async def get_contracts(self, year: int, entity_id: str):
        """Buscar contratos do TCE-RS."""
        endpoint = f"{self.BASE_URL}/contratos"
        params = {"ano": year, "orgao": entity_id}

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params)
            return response.json()
```

#### Novos Endpoints a Implementar:
1. **SICONV** (Convênios Federais) - 8 horas
2. **e-Sic** (Transparência Ativa) - 6 horas
3. **CEIS** (Empresas Inidôneas) - 4 horas
4. **CNEP** (Entidades Punidas) - 4 horas
5. **CEPIM** (Impedidos de Contratar) - 4 horas

**Total**: 40-50 horas para 8 TCEs + 5 novos endpoints

---

## 💡 PRIORIDADE 4: Longo Prazo (2026 Q1)

### 4.1 🎨 Frontend Web Completo
**Impacto**: MUITO ALTO | **Esforço**: 200+ horas | **Status**: 🟣 Novo Projeto

**Motivação**: Backend robusto, mas sem interface gráfica para usuários finais.

**Proposta**: Desenvolver em `cidadao.ai-frontend/` (Next.js 15)

**Features Essenciais**:
1. **Dashboard Executivo**:
   - Cards de métricas agregadas
   - Gráficos interativos (Plotly.js)
   - Mapa de calor de corrupção por estado
   - Timeline de investigações

2. **Chat Interface**:
   - Chat com agentes em tempo real (SSE)
   - Histórico de conversas
   - Sugestões de perguntas
   - Export de conversas (PDF, JSON)

3. **Sistema de Investigações**:
   - Criar investigação via formulário
   - Monitorar progresso em tempo real
   - Visualizar resultados por agente
   - Download de relatórios completos

4. **Painel de Administração**:
   - Gerenciar usuários e permissões
   - Configurar alertas
   - Visualizar métricas de sistema
   - Logs de auditoria

**Stack Técnico**:
- Next.js 15 (App Router)
- TypeScript
- TailwindCSS + shadcn/ui
- Zustand (state management)
- React Query (data fetching)
- PWA (service worker + offline)

**Referência**: `docs/frontend/` já tem documentação inicial

---

### 4.2 🤖 Sistema de Auto-Investigação Proativa
**Impacto**: ALTO | **Esforço**: 60-80 horas | **Status**: 🟣 Inovador

**Conceito**: Sistema que monitora APIs 24/7 e inicia investigações automaticamente quando detecta anomalias.

**Arquitetura**:
```
Celery Beat (scheduler) → Celery Worker → Fetch APIs → Zumbi (detect) → Auto-Investigation
                                                              ↓
                                                       Alert System → Email/Slack/Discord
```

**Implementação**:

1. **Celery Tasks** (já existe infraestrutura):
```python
# src/infrastructure/queue/tasks/auto_investigation_tasks.py
@celery_app.task(name="monitor_contracts")
def monitor_contracts():
    """Monitorar contratos em tempo real."""
    # Fetch últimos contratos (últimas 24h)
    contracts = fetch_recent_contracts()

    # Detectar anomalias com Zumbi
    anomalies = zumbi.detect_anomalies(contracts)

    if anomalies["high_risk"]:
        # Iniciar investigação automática
        investigation_id = create_investigation(
            target=anomalies["suspect_contracts"],
            triggered_by="auto_monitor",
            priority="high"
        )

        # Alertar stakeholders
        send_alert(investigation_id, anomalies)
```

2. **Configurar Schedules**:
```python
# config/celery_config.py
CELERYBEAT_SCHEDULE = {
    'monitor-contracts-daily': {
        'task': 'monitor_contracts',
        'schedule': crontab(hour=6, minute=0),  # 6am daily
    },
    'check-pncp-hourly': {
        'task': 'check_pncp_updates',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

3. **Sistema de Alertas**:
   - Email para gestores públicos
   - Slack para equipe técnica
   - Discord para comunidade
   - Telegram para jornalistas cadastrados

**Benefício**: Detecção proativa de fraudes sem intervenção humana.

---

### 4.3 📱 API Pública e SDK para Desenvolvedores
**Impacto**: MÉDIO | **Esforço**: 40-50 horas | **Status**: 🟣 Ecossistema

**Motivação**: Permitir que terceiros (jornalistas, ONGs, pesquisadores) integrem Cidadão.AI.

**Componentes**:

1. **API Key System**:
```python
# src/models/api_key.py
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    key = Column(String, unique=True)
    name = Column(String)  # "Jornal O Globo - Investigação"
    tier = Column(String)  # "free", "basic", "premium"
    rate_limit = Column(Integer)  # requests/hour
    expires_at = Column(DateTime)
```

2. **SDK Python**:
```python
# cidadao-ai-sdk/
from cidadao_ai import CidadaoAI

client = CidadaoAI(api_key="ca_xxxxxxxxxxxx")

# Investigar empresa
investigation = client.investigations.create(
    target_cnpj="00.000.000/0001-00",
    agents=["zumbi", "oxossi", "obaluaie"]
)

# Aguardar resultado
result = investigation.wait()
print(result.summary)
```

3. **SDK JavaScript/TypeScript**:
```typescript
import { CidadaoAI } from '@cidadao-ai/sdk';

const client = new CidadaoAI({ apiKey: process.env.CIDADAO_API_KEY });

const investigation = await client.investigations.create({
  targetCnpj: '00.000.000/0001-00',
  agents: ['zumbi', 'oxossi'],
});

console.log(investigation.summary);
```

4. **Documentação Interativa**:
   - OpenAPI 3.1 spec completo
   - Swagger UI + Redoc
   - Exemplos em 5 linguagens (Python, JS, Ruby, Go, PHP)
   - Rate limits e pricing claramente documentados

**Tiers de Uso**:
| Tier | Requests/Hour | Agents Simultâneos | Preço |
|------|---------------|-------------------|-------|
| Free | 10 | 2 | R$ 0 |
| Basic | 100 | 5 | R$ 99/mês |
| Premium | 1000 | 16 | R$ 499/mês |
| Enterprise | Ilimitado | Ilimitado | Contato |

---

## 📊 Resumo Executivo de Prioridades

### Impacto vs Esforço (Matriz de Decisão)

```
        Alto Impacto
             │
   P2.3 ●    │    ● P3.1     ● P4.1
             │
   P2.2 ●    │    ● P3.2
             │
─────────────┼─────────────── Esforço
             │
   P1.1 ●    │    ● P2.1
   P1.2 ●    │
   P1.3 ●    │    ● P4.2
             │    ● P4.3
      Baixo Esforço
```

### Timeline Sugerido

| Período | Foco Principal | Entregáveis | Horas |
|---------|----------------|-------------|-------|
| **Semana 1** (21-27 Out) | Testes + Métricas | Oxóssi testado, Coverage real, Prometheus | 16-24h |
| **Semanas 2-3** (28 Out-10 Nov) | Qualidade | +25pp coverage, Dados reais, ML básico | 50-70h |
| **Nov-Dez 2025** | Completude | Tier 2 completo, Segurança, APIs | 125-160h |
| **2026 Q1** | Expansão | Frontend, Auto-investigação, SDK | 300+h |

### KPIs para Acompanhar

| Métrica | Atual | Meta Dez/2025 | Meta Mar/2026 |
|---------|-------|---------------|---------------|
| **Cobertura de Testes** | 40% | 75% | 85% |
| **Agentes Tier 1** | 10/16 (63%) | 15/16 (94%) | 16/16 (100%) |
| **APIs Integradas** | 37 | 50 | 70 |
| **Uptime** | 99.9% | 99.95% | 99.99% |
| **Usuários Ativos** | N/A | 100 | 1000 |
| **Investigações/Mês** | ~50 | 500 | 5000 |

---

## 🎯 Recomendação Imediata para Esta Semana

Anderson, baseado na análise completa, recomendo focar em:

### Segunda-feira (21 Out):
- [ ] Criar `tests/unit/agents/test_oxossi.py` completo (8-12h)
- [ ] Atingir 75%+ de cobertura em Oxóssi

### Terça-feira (22 Out):
- [ ] Medir cobertura real com `pytest --cov` (2h)
- [ ] Documentar gaps no relatório HTML (2h)
- [ ] Atualizar badges e documentação (1h)

### Quarta-feira (23 Out):
- [ ] Adicionar `prometheus_client` ao projeto (1h)
- [ ] Instrumentar métricas de agentes (4h)
- [ ] Expor endpoint `/health/metrics` (2h)

### Quinta-feira (24 Out):
- [ ] Instrumentar métricas de API (3h)
- [ ] Configurar dashboards Grafana (3h)
- [ ] Testar stack completo localmente (2h)

### Sexta-feira (25 Out):
- [ ] Deploy das mudanças no Railway (1h)
- [ ] Validar métricas em produção (2h)
- [ ] Documentar próximos passos (2h)

**Total estimado**: 16-24 horas de desenvolvimento focado

---

## 📚 Referências e Recursos

### Documentação Interna
- `docs/project/COMPREHENSIVE_ANALYSIS_2025_10_20.md` - Análise completa verificada
- `docs/project/CURRENT_STATUS_2025_10.md` - Status oficial dos agentes
- `docs/project/IMPLEMENTATION_REALITY.md` - Gaps entre docs e código
- `docs/agents/INVENTORY.md` - Registro completo de agentes

### Ferramentas Recomendadas
- **Testes**: `pytest`, `pytest-cov`, `pytest-asyncio`, `hypothesis`
- **Métricas**: `prometheus_client`, `grafana`, `statsd`
- **Segurança**: `bandit`, `safety`, `pip-audit`, `semgrep`
- **ML**: `scikit-learn`, `statsmodels`, `prophet`, `tensorflow`
- **Qualidade**: `black`, `ruff`, `mypy`, `isort`

### Benchmarks de Referência
- **Test Coverage**: [Google: 80%](https://testing.googleblog.com/), [Mozilla: 70%](https://wiki.mozilla.org/), [Meta: 85%](https://engineering.fb.com/)
- **API Uptime**: [AWS: 99.99%](https://aws.amazon.com/compute/sla/), [GCP: 99.95%](https://cloud.google.com/compute/sla)
- **Response Time**: [p95 <300ms](https://sre.google/), [p99 <1s](https://sre.google/)

---

## ✅ Checklist de Ações Imediatas

### Para começar hoje (20 Out, 17:15):
- [ ] Revisar este documento completo
- [ ] Decidir prioridades para semana 1
- [ ] Criar branch `feature/week-1-improvements`
- [ ] Preparar ambiente de testes

### Segunda-feira (21 Out):
- [ ] Iniciar implementação de testes para Oxóssi
- [ ] Configurar pytest-cov para relatórios HTML
- [ ] Documentar descobertas no Slack/Discord da equipe

---

**Documento criado em**: 20 de Outubro de 2025, 17:30
**Próxima revisão**: 27 de Outubro de 2025
**Responsável**: Anderson Henrique da Silva
**Status**: 🟢 Aprovado para execução
