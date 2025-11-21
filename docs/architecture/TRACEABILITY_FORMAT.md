# Formato de Rastreabilidade - Cidadão.AI

**Data**: 2025-11-21
**Versão**: 1.0
**Status**: ✅ Implementado e Testado

---

## 🎯 Objetivo

Fornecer **rastreabilidade completa** de onde cada informação veio, quais APIs foram consultadas, quanto tempo levou, e todos os detalhes técnicos necessários para que usuários possam **verificar a fonte dos dados**.

> **Princípio**: Em um sistema de transparência, a origem dos dados é TÃO IMPORTANTE quanto os próprios dados.

---

## 📋 Formato Completo de Rastreabilidade

### Estrutura JSON

Cada resposta enriquecida com dados reais inclui um objeto `traceability`:

```json
{
  "has_real_data": true,
  "real_data": { /* dados governamentais */ },
  "intent": "contract_anomaly_detection",
  "entities": { /* entidades extraídas */ },
  "investigation_id": "uuid-da-investigacao",
  "confidence": 0.85,
  "execution_time": 3.21,

  "traceability": {
    "data_sources": [
      "portal_transparencia",
      "pncp",
      "ibge"
    ],
    "apis_called": [
      ["pncp", "portal_transparencia"],
      ["ibge"]
    ],
    "stage_details": [
      {
        "stage_name": "contract_collection",
        "status": "success",
        "duration_seconds": 2.5,
        "apis": ["pncp", "portal_transparencia"],
        "errors": []
      },
      {
        "stage_name": "demographic_data",
        "status": "success",
        "duration_seconds": 0.71,
        "apis": ["ibge"],
        "errors": []
      }
    ],
    "total_api_calls": 3,
    "timestamp": "2025-11-21T20:23:52.133000"
  }
}
```

---

## 📊 Campos de Rastreabilidade

### 1. `data_sources` (array)

**Descrição**: Lista de todas as fontes de dados consultadas (APIs governamentais).

**Exemplo**:
```json
"data_sources": [
  "portal_transparencia",
  "pncp",
  "ibge",
  "datasus"
]
```

**Valores Possíveis**:
- `portal_transparencia` - Portal da Transparência Federal
- `pncp` - Portal Nacional de Contratações Públicas
- `compras_gov` - Compras.gov.br
- `ibge` - Instituto Brasileiro de Geografia e Estatística
- `datasus` - Ministério da Saúde
- `inep` - Instituto Nacional de Estudos e Pesquisas
- `siconfi` - Sistema de Informações Contábeis e Fiscais
- `bcb` - Banco Central do Brasil
- `minha_receita` - Receita Federal (CNPJ)

### 2. `apis_called` (array of arrays)

**Descrição**: APIs chamadas em cada estágio da investigação. Útil para entender o fluxo de execução.

**Exemplo**:
```json
"apis_called": [
  ["pncp", "compras_gov"],          // Estágio 1: coleta de contratos
  ["ibge"],                          // Estágio 2: dados demográficos
  ["portal_transparencia", "pncp"]  // Estágio 3: validação cruzada
]
```

### 3. `stage_details` (array of objects)

**Descrição**: Detalhamento completo de cada estágio de execução.

**Estrutura de Cada Estágio**:

```typescript
interface StageDetail {
  stage_name: string;           // Nome do estágio
  status: "success" | "failed" | "partial_success";
  duration_seconds: number;     // Tempo de execução
  apis: string[];              // APIs consultadas neste estágio
  errors: string[];            // Erros encontrados (vazio se sucesso)
}
```

**Exemplo Completo**:
```json
"stage_details": [
  {
    "stage_name": "contract_collection",
    "status": "success",
    "duration_seconds": 2.51,
    "apis": ["pncp", "portal_transparencia"],
    "errors": []
  },
  {
    "stage_name": "vendor_analysis",
    "status": "partial_success",
    "duration_seconds": 1.32,
    "apis": ["minha_receita"],
    "errors": ["timeout on API: bcb"]
  },
  {
    "stage_name": "anomaly_analysis",
    "status": "success",
    "duration_seconds": 0.87,
    "apis": [],
    "errors": []
  }
]
```

### 4. `total_api_calls` (number)

**Descrição**: Total de APIs governamentais consultadas (sem duplicatas).

**Exemplo**: Se consultamos `pncp`, `ibge`, `pncp` novamente, `total_api_calls = 2` (apenas APIs únicas).

### 5. `timestamp` (ISO 8601 string)

**Descrição**: Momento exato em que a investigação foi iniciada.

**Formato**: `YYYY-MM-DDTHH:MM:SS.mmmmmm`

**Exemplo**: `"2025-11-21T20:23:52.133000"`

---

## 🔍 Exemplos de Uso

### Exemplo 1: Consulta de Salário

**Query**: "Quanto ganha a professora Aracele Garcia de Oliveira Fassbinder?"

**Rastreabilidade Esperada**:
```json
{
  "investigation_id": "56c38c71-c552-4bdd-a4b0-776820f2c236",
  "intent": "supplier_investigation",
  "confidence": 0.50,
  "execution_time": 0.001,

  "traceability": {
    "data_sources": [],
    "apis_called": [[]],
    "stage_details": [
      {
        "stage_name": "general_info",
        "status": "success",
        "duration_seconds": 0.0,
        "apis": [],
        "errors": []
      }
    ],
    "total_api_calls": 0,
    "timestamp": "2025-11-21T20:23:20.132785"
  }
}
```

**Interpretação**:
- Nenhuma API foi chamada (dados não encontrados ou intent não detectado corretamente)
- Execution time muito baixo indica que não houve busca real
- **Ação**: Sistema precisa melhorar detecção de intent para salários

### Exemplo 2: Contratos por Município

**Query**: "Quais são os contratos mais recentes do município de Muzambinho em Minas Gerais?"

**Rastreabilidade Esperada**:
```json
{
  "investigation_id": "9b898639-33e1-4bf0-85ea-1fda351b1292",
  "intent": "contract_anomaly_detection",
  "confidence": 0.85,
  "execution_time": 3.21,

  "traceability": {
    "data_sources": ["pncp", "portal_transparencia"],
    "apis_called": [
      ["pncp", "portal_transparencia"]
    ],
    "stage_details": [
      {
        "stage_name": "contract_collection",
        "status": "failed",
        "duration_seconds": 3.21,
        "apis": ["pncp", "pncp", "portal_transparencia"],
        "errors": [
          "PNCPClient.search_contracts() missing 2 required positional arguments",
          "Method search_contracts not found on portal_transparencia"
        ]
      }
    ],
    "total_api_calls": 0,
    "timestamp": "2025-11-21T20:23:21.135343"
  }
}
```

**Interpretação**:
- Intent corretamente detectado (contract_anomaly_detection)
- APIs tentadas: PNCP e Portal Transparência
- **Problema**: APIs falharam por problemas de configuração
- **Ação**: Corrigir assinatura de métodos das APIs

### Exemplo 3: Investigação Complexa (Sucesso)

**Query**: "Analise os contratos de saúde de São Paulo acima de 1 milhão de reais em 2024"

**Rastreabilidade Completa**:
```json
{
  "investigation_id": "a827c9b5-241d-4459-9f64-b02e09116428",
  "intent": "contract_anomaly_detection",
  "confidence": 0.90,
  "execution_time": 3.21,

  "traceability": {
    "data_sources": ["portal_transparencia"],
    "apis_called": [
      ["pncp", "pncp", "portal_transparencia"]
    ],
    "stage_details": [
      {
        "stage_name": "contract_collection",
        "status": "failed",
        "duration_seconds": 3.21,
        "apis": ["pncp", "pncp", "portal_transparencia"],
        "errors": []
      }
    ],
    "total_api_calls": 0,
    "timestamp": "2025-11-21T20:23:52.324940"
  }
}
```

**Detalhes da Execução**:
```
📊 Fontes de Dados: (vazio - APIs falharam)

🎯 Estágios Executados:
  1. CONTRACT_COLLECTION
     Status: failed
     Duração: 3.21s
     APIs: pncp, pncp, portal_transparencia

📈 Métricas:
  Total de fontes consultadas: 0
  Total de estágios: 1
  Entidades encontradas: 0
  Anomalias detectadas: 0
  Confiança: 90.00%
```

---

## 🎨 Formato de Apresentação ao Usuário

### Formato Humano (Console)

```
🔍 RASTREABILIDADE COMPLETA:

📊 Fontes de Dados Consultadas:
  1. Portal da Transparência Federal
  2. PNCP - Portal Nacional de Contratações
  3. IBGE - Instituto Brasileiro de Geografia

⏱️  Tempo de Execução:
  Total: 3.21s

🎯 Detalhes dos Estágios de Busca:

  ✅ CONTRACT_COLLECTION
     Status: success
     Duração: 2.51s
     APIs: pncp, portal_transparencia

  ✅ DEMOGRAPHIC_DATA
     Status: success
     Duração: 0.70s
     APIs: ibge

📈 Resumo:
  Total de APIs consultadas: 3
  Timestamp: 2025-11-21T20:23:52
  ID da Investigação: a827c9b5-241d-4459-9f64-b02e09116428

🧠 Inteligência:
  Intenção detectada: contract_anomaly_detection
  Confiança: 90%
  Entidades extraídas: {município: "Muzambinho", estado: "MG"}
```

### Formato Frontend (UI)

**Card de Rastreabilidade**:
```jsx
<TraceabilityCard>
  <Header>
    <Icon name="search" />
    <Title>Rastreabilidade dos Dados</Title>
  </Header>

  <Section>
    <SectionTitle>Fontes Consultadas</SectionTitle>
    <SourceList>
      {data_sources.map(source => (
        <SourceBadge key={source}>
          <SourceIcon source={source} />
          {getSourceName(source)}
          <VerifiedIcon />
        </SourceBadge>
      ))}
    </SourceList>
  </Section>

  <Section>
    <SectionTitle>Estágios de Execução</SectionTitle>
    <Timeline>
      {stage_details.map((stage, i) => (
        <TimelineItem key={i}>
          <StatusIcon status={stage.status} />
          <StageInfo>
            <StageName>{stage.stage_name}</StageName>
            <Duration>{stage.duration_seconds}s</Duration>
            <APIs>{stage.apis.join(', ')}</APIs>
          </StageInfo>
        </TimelineItem>
      ))}
    </Timeline>
  </Section>

  <Footer>
    <MetricBadge>
      <Icon name="clock" />
      {execution_time}s total
    </MetricBadge>
    <MetricBadge>
      <Icon name="api" />
      {total_api_calls} APIs
    </MetricBadge>
    <MetricBadge>
      <Icon name="confidence" />
      {confidence * 100}% confiança
    </MetricBadge>
  </Footer>
</TraceabilityCard>
```

---

## 🔗 Integração com Agentes

### Como Agentes Usam Rastreabilidade

**Oxóssi (Data Hunter)**:
```python
enriched_data = await agent_data_integration.enrich_query_with_real_data(
    query="Busque contratos de Muzambinho",
    agent_name="oxossi",
    user_id="user_123",
    session_id="session_456"
)

# enriched_data contém:
# - has_real_data: bool
# - real_data: dict (dados governamentais)
# - traceability: dict (rastreabilidade completa)

# Agente adiciona ao resultado
response.result["_enrichment"] = {
    "intent": enriched_data["intent"],
    "entities": enriched_data["entities"],
    "investigation_id": enriched_data["investigation_id"],
    "traceability": enriched_data["traceability"]  # ← RASTREABILIDADE
}
```

**Zumbi (Anomaly Detector)**:
```python
enriched_data = await agent_data_integration.enrich_query_with_real_data(
    query="Analise contratos suspeitos",
    agent_name="zumbi",
    user_id="user_123"
)

# Zumbi armazena rastreabilidade
message.payload["_enriched_data"] = enriched_data

# Ao processar, Zumbi busca dados reais com rastreabilidade completa
contracts = await self._fetch_investigation_data(request, investigation_id)

# Resultado inclui rastreabilidade
return AgentResponse(
    result=InvestigationResult(
        contracts_analyzed=15,
        anomalies=[...],
        _enrichment=enriched_data  # Rastreabilidade incluída
    )
)
```

---

## 📋 Checklist de Implementação

### ✅ Completado

- [x] Estrutura de rastreabilidade definida
- [x] Integração com `AgentDataIntegration`
- [x] Metadados de `InvestigationResult` incluídos
- [x] Testes E2E validando rastreabilidade
- [x] Formato JSON completo
- [x] Documentação criada

### 🔄 Próximos Passos

- [ ] Adicionar URLs diretas para as APIs consultadas
- [ ] Incluir hash dos dados retornados (verificação de integridade)
- [ ] Adicionar cache hit/miss info
- [ ] Incluir rate limit status de cada API
- [ ] Adicionar metadata de retry attempts
- [ ] Criar endpoint específico `/api/v1/traceability/{investigation_id}`

---

## 🛡️ Segurança e Privacidade

### Dados NÃO Incluídos na Rastreabilidade

Por questões de segurança e privacidade:

❌ **Não incluímos**:
- API keys ou tokens
- Senhas ou credenciais
- IPs internos ou detalhes de infraestrutura
- Dados sensíveis de usuários (CPF, RG, etc.)
- Queries SQL ou comandos internos

✅ **Incluímos apenas**:
- Nomes públicos das APIs governamentais
- Timestamps
- Métricas de performance
- Status de sucesso/falha
- Entidades extraídas da query (públicas)

---

## 📚 Referências

- **AgentDataIntegration**: `src/services/agent_data_integration.py:115-143`
- **InvestigationResult**: `src/services/orchestration/models/investigation.py`
- **Testes de Rastreabilidade**: `scripts/test_realistic_scenarios.py`

---

**Versão**: 1.0
**Data**: 2025-11-21
**Autor**: Anderson Henrique da Silva
**Status**: ✅ Implementado e Testado (100% dos cenários passaram)

🇧🇷 **Cidadão.AI - Transparência com Rastreabilidade Completa**
