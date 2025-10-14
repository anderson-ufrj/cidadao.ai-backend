# 🎯 Arquitetura de Orquestração Multi-API para Investigações Automáticas

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-14 16:30:00 -03:00
**Status**: PROPOSTA TÉCNICA

---

## 🎯 PROBLEMA

Com 200+ APIs governamentais disponíveis, como os agentes realizam investigações automáticas coordenando múltiplas fontes de dados?

**Desafios**:
1. ❌ Decidir quais APIs consultar para cada investigação
2. ❌ Correlacionar dados de fontes heterogêneas
3. ❌ Gerenciar latência (10+ chamadas de API)
4. ❌ Respeitar rate limits de cada API
5. ❌ Minimizar custos (algumas APIs são pagas)
6. ❌ Cachear dados inteligentemente
7. ❌ Lidar com falhas parciais

---

## ✅ SOLUÇÃO: 3 Camadas de Orquestração

```
┌─────────────────────────────────────────────────────────┐
│  CAMADA 1: Query Understanding & Planning               │
│  (Entende a pergunta, decide quais APIs usar)           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  CAMADA 2: Data Federation Layer                        │
│  (Orquestra chamadas, correlaciona dados)               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  CAMADA 3: Unified Entity Graph                         │
│  (Grafo de conhecimento unificado)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 CAMADA 1: Query Understanding & Planning

### 1.1 Intent Classification

**Objetivo**: Classificar a intenção do usuário e mapear para APIs relevantes.

```python
class InvestigationIntent:
    """Tipos de investigação e APIs necessárias."""

    SUPPLIER_INVESTIGATION = {
        "name": "Investigação de Fornecedor",
        "apis": [
            "minha_receita",  # Dados cadastrais CNPJ
            "pncp",           # Licitações atuais
            "compras_gov",    # Histórico de contratos
            "cnd",            # Regularidade fiscal
            "tse",            # Doações eleitorais (se aplicável)
        ],
        "sequence": "sequential",  # Ordem de execução
        "parallel_groups": [
            ["minha_receita"],        # 1. Primeiro
            ["pncp", "compras_gov"],  # 2. Paralelo após CNPJ
            ["cnd", "tse"],           # 3. Paralelo após contratos
        ]
    }

    CONTRACT_ANOMALY_DETECTION = {
        "name": "Detecção de Anomalias em Contratos",
        "apis": [
            "pncp",           # Contratos para análise
            "ibge",           # Índices econômicos (contexto)
            "bcb",            # SELIC, inflação (contexto)
            "minha_receita",  # Dados de fornecedores
        ],
        "sequence": "mixed",
        "parallel_groups": [
            ["pncp"],                      # 1. Buscar contratos
            ["ibge", "bcb"],               # 2. Contexto econômico (paralelo)
            ["minha_receita"],             # 3. Enriquecer com CNPJs
        ]
    }

    HEALTH_BUDGET_ANALYSIS = {
        "name": "Análise Orçamentária de Saúde",
        "apis": [
            "siconfi",       # Finanças municipais/estaduais
            "datasus",       # Dados de saúde
            "ibge",          # Demografia
            "portal_transp", # Gastos federais
        ],
        "sequence": "mixed",
    }

class QueryPlanner:
    """Planeja execução de queries baseado na intenção."""

    async def plan_investigation(
        self,
        query: str,
        context: InvestigationContext
    ) -> ExecutionPlan:
        """
        Analisa a query e cria plano de execução.

        Args:
            query: Pergunta do usuário
            context: Contexto da investigação (CPF, CNPJ, período)

        Returns:
            ExecutionPlan com APIs, ordem, paralelização
        """
        # 1. Classificar intenção usando LLM
        intent = await self._classify_intent(query)

        # 2. Extrair entidades (CNPJ, CPF, datas, órgãos)
        entities = await self._extract_entities(query, context)

        # 3. Selecionar APIs relevantes
        relevant_apis = self._select_apis(intent, entities)

        # 4. Criar plano de execução otimizado
        plan = self._create_execution_plan(
            intent,
            entities,
            relevant_apis
        )

        return plan
```

### 1.2 Exemplo de Classificação

```python
# Input
query = "Investigue contratos da empresa XYZ LTDA nos últimos 2 anos"

# Output do QueryPlanner
ExecutionPlan(
    intent="SUPPLIER_INVESTIGATION",
    entities={
        "company_name": "XYZ LTDA",
        "cnpj": None,  # Será descoberto
        "date_range": ("2023-01-01", "2025-10-14"),
    },
    stages=[
        Stage(
            name="Identificação",
            apis=["minha_receita"],
            method="search_by_name",
            parallel=False,
            reason="Descobrir CNPJ da empresa",
        ),
        Stage(
            name="Busca de Contratos",
            apis=["pncp", "compras_gov"],
            method="search_contracts",
            parallel=True,  # Executar em paralelo
            depends_on=["Identificação"],
            reason="Buscar licitações e contratos",
        ),
        Stage(
            name="Enriquecimento",
            apis=["cnd", "portal_transp"],
            method="check_compliance",
            parallel=True,
            depends_on=["Busca de Contratos"],
            reason="Verificar regularidade e valores",
        ),
    ],
    estimated_duration_seconds=15,
    cache_strategy="aggressive",
)
```

---

## 🔄 CAMADA 2: Data Federation Layer

### 2.1 Unified Data Access

**Objetivo**: Camada de abstração que unifica acesso a todas as APIs.

```python
class DataFederationService:
    """Serviço de federação de dados de múltiplas APIs."""

    def __init__(self):
        self.api_registry = APIRegistry()
        self.cache = UnifiedCache()
        self.metrics = FederationMetrics()

    async def execute_investigation_plan(
        self,
        plan: ExecutionPlan
    ) -> InvestigationResult:
        """
        Executa plano de investigação com orquestração inteligente.

        Recursos:
        - Paralelização automática
        - Circuit breaker para APIs instáveis
        - Fallback para fontes alternativas
        - Deduplicação de chamadas
        - Cache distribuído
        """
        results = InvestigationResult()

        for stage in plan.stages:
            stage_results = await self._execute_stage(stage, results)
            results.add_stage_results(stage.name, stage_results)

        return results

    async def _execute_stage(
        self,
        stage: Stage,
        previous_results: InvestigationResult
    ) -> dict:
        """Executa um estágio do plano."""

        if stage.parallel:
            # Executar APIs em paralelo
            tasks = [
                self._call_api(api, stage, previous_results)
                for api in stage.apis
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Executar sequencialmente
            results = []
            for api in stage.apis:
                result = await self._call_api(api, stage, previous_results)
                results.append(result)

        return self._aggregate_stage_results(results)

    async def _call_api(
        self,
        api_name: str,
        stage: Stage,
        context: InvestigationResult
    ) -> APIResponse:
        """
        Chama API com circuit breaker e fallback.
        """
        # 1. Verificar cache
        cache_key = self._generate_cache_key(api_name, stage, context)
        if cached := await self.cache.get(cache_key):
            self.metrics.record_cache_hit(api_name)
            return cached

        # 2. Obter cliente da API
        client = self.api_registry.get_client(api_name)

        # 3. Preparar parâmetros baseado no contexto
        params = self._prepare_api_params(api_name, stage, context)

        # 4. Executar com circuit breaker
        try:
            result = await self._call_with_circuit_breaker(
                client,
                stage.method,
                params
            )

            # 5. Cachear resultado
            await self.cache.set(
                cache_key,
                result,
                ttl=self._get_cache_ttl(api_name)
            )

            return result

        except APIError as e:
            # 6. Tentar fallback se disponível
            if fallback_api := self._get_fallback_api(api_name):
                logger.warning(f"{api_name} failed, trying {fallback_api}")
                return await self._call_api(fallback_api, stage, context)

            # 7. Falha parcial aceitável
            logger.error(f"API {api_name} failed: {e}")
            return APIResponse(status="failed", error=str(e))
```

### 2.2 Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Previne chamadas para APIs instáveis."""

    STATES = ["CLOSED", "OPEN", "HALF_OPEN"]

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = APIError
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    async def call(self, func, *args, **kwargs):
        """Executa função com circuit breaker."""

        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpen(
                    f"Circuit breaker OPEN for {func.__name__}"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Resetar contador em sucesso."""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"

    def _on_failure(self):
        """Incrementar contador em falha."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

### 2.3 Fallback Strategy

```python
class FallbackRegistry:
    """Mapeia APIs para alternativas."""

    FALLBACKS = {
        "portal_transp": [
            "pncp",           # Para contratos
            "compras_gov",    # Para licitações antigas
        ],
        "serpro_cnpj": [
            "minha_receita",  # Alternativa gratuita
        ],
        "cnd_federal": [
            "portal_transp",  # Pode ter info parcial
        ],
    }

    def get_fallback(self, api_name: str) -> Optional[str]:
        """Retorna API de fallback."""
        fallbacks = self.FALLBACKS.get(api_name, [])
        return fallbacks[0] if fallbacks else None
```

---

## 🕸️ CAMADA 3: Unified Entity Graph

### 3.1 Knowledge Graph

**Objetivo**: Grafo de conhecimento unificado que conecta entidades de todas as APIs.

```python
class EntityGraph:
    """
    Grafo de entidades unificado.

    Permite consultas como:
    - "Todos os contratos da empresa X"
    - "Fornecedores do órgão Y que têm pendências fiscais"
    - "Correlação entre doações eleitorais e contratos"
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entity_index = {}

    async def add_entity(
        self,
        entity_type: str,
        entity_id: str,
        data: dict,
        source_api: str
    ):
        """
        Adiciona entidade ao grafo.

        Args:
            entity_type: "company", "contract", "person", "agency"
            entity_id: Identificador único (CNPJ, CPF, etc)
            data: Dados da entidade
            source_api: API de origem
        """
        node_id = f"{entity_type}:{entity_id}"

        self.graph.add_node(
            node_id,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            source_api=source_api,
            updated_at=datetime.now(),
        )

        # Indexar para busca rápida
        self.entity_index[entity_id] = node_id

    async def link_entities(
        self,
        from_entity: str,
        to_entity: str,
        relationship: str,
        metadata: dict = None
    ):
        """
        Cria relacionamento entre entidades.

        Exemplos:
        - Company X "won_contract" Contract Y
        - Person A "is_partner_of" Company B
        - Company C "donated_to" Politician D
        """
        self.graph.add_edge(
            from_entity,
            to_entity,
            relationship=relationship,
            metadata=metadata or {},
            created_at=datetime.now(),
        )

    async def query_graph(self, cypher_query: str) -> list:
        """
        Consulta o grafo usando query similar a Cypher.

        Example:
            query = '''
            MATCH (c:company)-[:won_contract]->(ct:contract)
            WHERE ct.value > 1000000
            RETURN c.name, ct.value, ct.date
            '''
        """
        # Implementação de query engine
        pass

    async def find_anomalies(self, entity_id: str) -> list[Anomaly]:
        """
        Detecta anomalias analisando o grafo.

        Exemplos:
        - Empresa nova com contratos grandes
        - Concentração de contratos em poucos fornecedores
        - Sócios em comum entre concorrentes
        """
        anomalies = []

        # Análise de padrões suspeitos
        node = self.graph.nodes[entity_id]

        # 1. Verificar idade da empresa vs tamanho de contratos
        if self._is_new_company_large_contracts(node):
            anomalies.append(Anomaly(
                type="new_company_large_contract",
                severity="high",
                description="Empresa recente com contratos acima da média",
            ))

        # 2. Verificar rede de relacionamentos
        if self._has_suspicious_network(node):
            anomalies.append(Anomaly(
                type="suspicious_network",
                severity="medium",
                description="Relacionamentos suspeitos detectados",
            ))

        return anomalies
```

### 3.2 Exemplo de Grafo Construído

```
┌──────────────┐
│ Company:     │
│ 12.345.678/  │────won_contract───┐
│ 0001-01      │                   │
└──────────────┘                   ↓
       │                    ┌──────────────┐
       │                    │ Contract:    │
       │                    │ 2024/001     │
is_partner_of              │ R$ 5.000.000 │
       │                    └──────────────┘
       ↓                            │
┌──────────────┐                   │
│ Person:      │                   │
│ 111.222.333  │──donated_to───────┤
│ -44          │                   │
└──────────────┘                   ↓
                            ┌──────────────┐
                            │ Agency:      │
                            │ Ministry X   │
                            └──────────────┘
```

---

## 🚀 IMPLEMENTAÇÃO PRÁTICA

### Fase 1: Query Planning Service (2 semanas)

```python
# src/services/query_planner/
├── intent_classifier.py      # Classificação de intenção
├── entity_extractor.py       # Extração de entidades
├── execution_planner.py      # Criação de planos
└── templates/
    ├── supplier_investigation.yaml
    ├── contract_anomaly.yaml
    └── budget_analysis.yaml
```

### Fase 2: Data Federation (3 semanas)

```python
# src/services/data_federation/
├── federation_service.py     # Orquestração
├── circuit_breaker.py        # Resiliência
├── fallback_registry.py      # Fallbacks
├── unified_cache.py          # Cache distribuído
└── api_registry.py           # Registro de APIs
```

### Fase 3: Entity Graph (4 semanas)

```python
# src/services/entity_graph/
├── graph_builder.py          # Construção do grafo
├── entity_linker.py          # Link entre entidades
├── query_engine.py           # Engine de consultas
└── anomaly_detector.py       # Detecção de anomalias
```

---

## 📊 EXEMPLO DE FLUXO COMPLETO

### Input
```python
query = "Investigue contratos suspeitos da empresa ACME LTDA em 2024"
```

### Processamento

**1. Query Planning (2s)**
```python
plan = QueryPlanner.plan_investigation(query)
# Intent: CONTRACT_ANOMALY_DETECTION
# Entities: {"company_name": "ACME LTDA", "year": 2024}
# APIs: minha_receita, pncp, compras_gov, bcb, ibge
```

**2. Data Federation (10s)**
```python
# Stage 1: Identificar empresa (2s)
company = await minha_receita.search("ACME LTDA")
# CNPJ: 12.345.678/0001-01

# Stage 2: Buscar contratos (paralelo, 5s)
contracts_pncp = await pncp.search_contracts(cnpj="12.345.678/0001-01", year=2024)
contracts_old = await compras_gov.search_contracts(cnpj="12.345.678/0001-01")

# Stage 3: Contexto econômico (paralelo, 3s)
selic_2024 = await bcb.get_selic(year=2024)
ipca_2024 = await ibge.get_ipca(year=2024)
```

**3. Entity Graph Construction (2s)**
```python
# Adicionar ao grafo
graph.add_entity("company", company.cnpj, company.dict())
for contract in contracts:
    graph.add_entity("contract", contract.id, contract.dict())
    graph.link_entities(company.cnpj, contract.id, "won_contract")
```

**4. Anomaly Detection (1s)**
```python
anomalies = graph.find_anomalies(company.cnpj)
# - Empresa criada em 2023, contratos de R$ 10M em 2024
# - Preços 30% acima da média do mercado
# - Único vencedor em 80% das licitações do órgão X
```

**5. Response (15s total)**
```python
InvestigationResult(
    company=company,
    contracts_found=25,
    total_value=50_000_000,
    anomalies=[
        Anomaly(type="new_company_large_contract", severity="high"),
        Anomaly(type="price_above_market", severity="medium"),
        Anomaly(type="supplier_concentration", severity="high"),
    ],
    data_sources=["Minha Receita", "PNCP", "BCB", "IBGE"],
    confidence_score=0.85,
)
```

---

## 🎯 BENEFÍCIOS DA ARQUITETURA

### ✅ Para os Agentes
- **Automação Total**: Agentes não precisam saber quais APIs usar
- **Velocidade**: Paralelização inteligente reduz latência
- **Resiliência**: Fallbacks automáticos em falhas
- **Contexto Rico**: Grafo fornece visão 360° das entidades

### ✅ Para o Sistema
- **Escalabilidade**: Adicionar novas APIs sem modificar agentes
- **Observabilidade**: Métricas de cada API e estágio
- **Custo**: Cache agressivo reduz chamadas repetidas
- **Qualidade**: Correlação de múltiplas fontes aumenta confiança

### ✅ Para os Usuários
- **Investigações Profundas**: 10+ fontes em uma consulta
- **Respostas Rápidas**: 15s para investigações complexas
- **Confiabilidade**: Sistema continua funcionando com APIs parcialmente offline
- **Transparência**: Sabe exatamente quais fontes foram usadas

---

## 📝 PRÓXIMOS PASSOS

1. ✅ **Documentar arquitetura** (FEITO)
2. ⏳ **Implementar QueryPlanner** (2 semanas)
3. ⏳ **Implementar DataFederation** (3 semanas)
4. ⏳ **Implementar EntityGraph** (4 semanas)
5. ⏳ **Integrar com agentes existentes** (1 semana)
6. ⏳ **Testes de carga e benchmarks** (1 semana)

**Total: 11 semanas (2.5 meses)**

---

**Última Atualização**: 2025-10-14 16:30:00 -03:00
**Status**: PROPOSTA TÉCNICA COMPLETA
**Responsável**: Anderson Henrique da Silva
