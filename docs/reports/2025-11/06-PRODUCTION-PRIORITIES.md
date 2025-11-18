# 🚀 Prioridades Críticas para Entrega - Cidadão.AI Backend

**Data**: 2025-11-19
**Status**: Sistema pronto para entrega, ajustes finais necessários
**Contexto**: 15/16 agentes operacionais (93.8%), Céuci funcional com ML real

---

## 🎯 Meta de Entrega

**Sistema funcional em produção** com:
- ✅ Multi-agent system operacional (15/16 agentes)
- ✅ Pipeline ML real conectado (Céuci: mock → ARIMA/LSTM/Prophet)
- ⚠️ Validação de APIs governamentais
- ⚠️ Error handling robusto
- ⚠️ Testes end-to-end com dados reais

---

## 🔥 PRIORITY 1: Validação de APIs Governamentais (CRÍTICO)

### 1.1 Portal da Transparência - 78% de Endpoints Bloqueados

**Problema Atual**:
```
Total de endpoints: ~20
Endpoints funcionais: 4 (22%)
Endpoints bloqueados (403 Forbidden): 16 (78%)
```

**Endpoints Funcionais** ✅:
- `/api/v1/transparency/contracts` (requer `codigoOrgao`)
- `/api/v1/transparency/servants` (busca por CPF)
- `/api/v1/transparency/agencies` (info organizacional)
- `/api/v1/transparency/contracts/{id}` (detalhes de contrato)

**Endpoints Bloqueados** ❌:
- Despesas (`/expenses`)
- Fornecedores (`/suppliers`)
- Emendas parlamentares (`/amendments`)
- Benefícios sociais (`/benefits`)
- Transferências (`/transfers`)
- Licitações (`/bids`)
- E mais 10 endpoints...

### Ação Necessária (2-3 horas):

**Opção A: Documentar e Aceitar Limitação** (RECOMENDADO) ✅
```bash
# 1. Criar documentação clara dos endpoints funcionais
# Arquivo: docs/api/PORTAL_TRANSPARENCIA_LIMITATIONS.md

# 2. Atualizar README com aviso sobre limitação
# "⚠️ Portal da Transparência: Apenas 22% dos endpoints estão acessíveis.
#  Sistema usa 30+ APIs alternativas como fallback."

# 3. Garantir fallback funciona
# Testar que agentes usam APIs alternativas quando Portal falha
```

**Opção B: Investigar Causa dos 403** (NÃO RECOMENDADO - muito tempo)
- Entrar em contato com CGU
- Solicitar chave de API de nível superior
- Aguardar resposta (pode levar semanas)

**Decisão**: **Opção A** - Sistema já tem 30+ APIs alternativas configuradas!

---

## 🔧 PRIORITY 2: Error Handling e Fallbacks (CRÍTICO)

### 2.1 Validar Circuit Breaker com APIs Reais

**Arquivo**: `src/services/orchestration/resilience/circuit_breaker.py`

**Teste Necessário** (1 hora):
```python
# Criar script: scripts/testing/test_circuit_breaker_production.py

import asyncio
from src.services.orchestration.resilience.circuit_breaker import CircuitBreaker

async def test_portal_fallback():
    """Test circuit breaker opens after Portal API failures."""
    circuit = CircuitBreaker(failure_threshold=3, timeout=60.0)

    # Simular 3 falhas consecutivas no Portal
    for i in range(3):
        try:
            await circuit.call(lambda: call_blocked_portal_endpoint())
        except:
            print(f"Failure {i+1}/3")

    # Circuit deve estar OPEN agora
    assert circuit.state == "OPEN"

    # Próximas chamadas devem falhar imediatamente (fast-fail)
    start = time.time()
    try:
        await circuit.call(lambda: call_blocked_portal_endpoint())
    except CircuitBreakerOpenError:
        elapsed = time.time() - start
        assert elapsed < 0.1  # Fast-fail em <100ms
        print("✅ Circuit breaker working!")

if __name__ == "__main__":
    asyncio.run(test_portal_fallback())
```

### 2.2 Validar Fallback para APIs Alternativas

**APIs Alternativas Disponíveis** (já configuradas):
- IBGE API (dados demográficos)
- DataSUS (saúde pública)
- INEP (educação)
- PNCP (licitações)
- SICONFI (finanças municipais/estaduais)
- TCE-CE, TCE-PE, TCE-MG (tribunais estaduais)
- Mais 20+ APIs federais

**Teste Necessário** (1 hora):
```bash
# Criar script: scripts/testing/test_api_fallback.py

# Verificar que quando Portal falha:
# 1. Sistema tenta APIs alternativas
# 2. Logs mostram tentativa de fallback
# 3. Resultado final é agregado de múltiplas fontes
```

---

## 📊 PRIORITY 3: Testes End-to-End com Dados Reais (IMPORTANTE)

### 3.1 Teste Completo de Investigação

**Arquivo**: `scripts/testing/test_complete_investigation_real.py`

```python
"""
Test complete investigation flow with real government data.

Simulates user query → intent detection → agent coordination → result delivery
"""

async def test_real_investigation():
    # 1. User query
    query = "Investigar contratos de construção civil em São Paulo acima de R$ 1 milhão em 2024"

    # 2. Intent detection
    intent = await classify_intent(query)
    assert intent == "contract_investigation"

    # 3. Entity extraction
    entities = await extract_entities(query)
    assert "São Paulo" in entities["location"]
    assert 1000000 in entities["amount"]

    # 4. Agent coordination (Abaporu orchestrates)
    investigation_id = await create_investigation(query, entities)

    # 5. Agents work (Zumbi, Lampião, Oxóssi)
    results = await wait_for_investigation(investigation_id, timeout=60)

    # 6. Validate results
    assert results["status"] == "completed"
    assert len(results["contracts"]) > 0
    assert "anomalies" in results
    assert "suppliers" in results
    assert "price_analysis" in results

    print(f"✅ Investigation completed: {len(results['contracts'])} contracts analyzed")
    print(f"   Anomalies detected: {len(results['anomalies'])}")
    print(f"   Unique suppliers: {len(results['suppliers'])}")
```

**Tempo Estimado**: 2-3 horas para criar e executar

### 3.2 Teste de ML Pipeline (Céuci)

**Arquivo**: `scripts/testing/test_ceuci_real_predictions.py`

```python
"""
Test Céuci ML pipeline with real government spending data.
"""

async def test_ceuci_real_predictions():
    # 1. Fetch real spending data (últimos 24 meses)
    spending_data = await fetch_government_spending_data(
        agency="MEC",  # Ministério da Educação
        period="2023-01 to 2024-12"
    )

    # 2. Request time series prediction
    message = AgentMessage(
        sender="test",
        recipient="Ceuci",
        action="predict",
        payload={
            "prediction_type": "TIME_SERIES",
            "model_type": "ARIMA",
            "data": spending_data,
            "target_variable": "amount",
            "prediction_horizon": 6  # 6 months ahead
        }
    )

    # 3. Execute prediction
    response = await ceuci_agent.process(message, AgentContext())

    # 4. Validate ML output (not mock!)
    assert response.status == AgentStatus.COMPLETED
    assert "predictions" in response.result
    assert "confidence_intervals" in response.result
    assert "model_performance" in response.result

    # 5. Check that predictions are realistic
    predictions = response.result["predictions"]
    assert len(predictions) == 6
    for pred in predictions:
        assert pred["value"] > 0  # Gastos devem ser positivos
        assert pred["value"] < 1e10  # Sanity check: < 10 bilhões/mês

    print(f"✅ Céuci ML predictions: {predictions}")
    print(f"   Model: {response.result.get('model_type')}")
    print(f"   Performance: {response.result.get('model_performance')}")
```

**Tempo Estimado**: 2 horas

---

## ✅ PRIORITY 4: Validação do Ambiente Railway (CRÍTICO)

### 4.1 Checklist de Produção

**Variáveis de Ambiente** (verificar em Railway):
```bash
# LLM Provider
LLM_PROVIDER=maritaca  # ou anthropic
MARITACA_API_KEY=<key>
MARITACA_MODEL=sabia-3.1
ANTHROPIC_API_KEY=<key>  # Backup

# Security
SECRET_KEY=<generate>
JWT_SECRET_KEY=<generate>

# Database
DATABASE_URL=postgresql+asyncpg://...  # Railway Postgres

# Cache
REDIS_URL=redis://...  # Railway Redis

# APIs Governamentais
TRANSPARENCY_API_KEY=<key>  # Portal da Transparência (22% funcional)

# Monitoring
ENABLE_METRICS=true
```

### 4.2 Smoke Tests em Produção

**Script**: `scripts/deployment/smoke_test_production.sh`

```bash
#!/bin/bash
# Smoke tests against Railway production

PROD_URL="https://cidadao-api-production.up.railway.app"

echo "🧪 Running production smoke tests..."

# 1. Health check
echo "1. Testing /health endpoint..."
curl -f "$PROD_URL/health" || exit 1

# 2. Metrics endpoint
echo "2. Testing /health/metrics endpoint..."
curl -f "$PROD_URL/health/metrics" | grep "cidadao_" || exit 1

# 3. API docs
echo "3. Testing /docs endpoint..."
curl -f "$PROD_URL/docs" || exit 1

# 4. Simple agent query
echo "4. Testing agent endpoint..."
curl -X POST "$PROD_URL/api/v1/agents/zumbi/analyze" \
  -H "Content-Type: application/json" \
  -d '{"contracts": [{"id": 1, "amount": 1000000}]}' || exit 1

# 5. Database connection
echo "5. Testing database connection..."
curl -f "$PROD_URL/api/v1/investigations?limit=1" || exit 1

echo "✅ All smoke tests passed!"
```

**Tempo Estimado**: 30 minutos

---

## 📋 Cronograma de Execução (1 Dia)

### Manhã (4 horas): APIs e Error Handling
- **09:00-10:00**: Criar `PORTAL_TRANSPARENCIA_LIMITATIONS.md` ✅
- **10:00-11:30**: Testar circuit breaker com APIs reais
- **11:30-13:00**: Validar fallback para APIs alternativas

### Tarde (4 horas): Testes E2E e Produção
- **14:00-16:00**: Criar e executar teste de investigação completa
- **16:00-17:00**: Testar Céuci com dados reais de governo
- **17:00-17:30**: Smoke tests em Railway production
- **17:30-18:00**: Documentar resultados e criar checklist final

---

## 🎯 Critérios de Sucesso para Entrega

### Must Have (Bloqueantes) ✅
- [x] 15/16 agentes operacionais (93.8%)
- [x] Céuci com ML pipeline real (78.53% coverage)
- [ ] Documentação de limitações do Portal da Transparência
- [ ] Circuit breaker validado com APIs reais
- [ ] Pelo menos 1 teste E2E completo funcionando
- [ ] Smoke tests passando em Railway production

### Nice to Have (Não-bloqueantes)
- [ ] Céuci em 85%+ coverage
- [ ] Testes com todas as APIs alternativas
- [ ] Grafana dashboards configurados com alertas
- [ ] Load testing com 100+ requests/s

---

## 🚨 Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Portal API continua bloqueado | **Alta** | Médio | ✅ 30+ APIs alternativas já configuradas |
| Falha em produção Railway | Baixa | **Alto** | Smoke tests + monitoring + rollback plan |
| LLM provider (Maritaca) falha | Média | Alto | ✅ Fallback automático para Anthropic |
| Céuci retorna previsões inválidas | Baixa | Médio | Validação de ranges + sanity checks |
| Database migrations falham | Baixa | **Alto** | Backup antes de deploy + rollback plan |

---

## 📚 Documentação a Criar

1. **docs/api/PORTAL_TRANSPARENCIA_LIMITATIONS.md** (30min)
   - Listar endpoints funcionais vs bloqueados
   - Explicar estratégia de fallback
   - Documentar APIs alternativas

2. **docs/deployment/PRODUCTION_CHECKLIST.md** (1h)
   - Environment variables completas
   - Smoke test procedures
   - Rollback procedures
   - Monitoring setup

3. **docs/testing/E2E_TESTING_GUIDE.md** (1h)
   - Como executar testes E2E
   - Datasets de teste
   - Resultados esperados

---

## 🎉 Status Atual vs Meta

**Funcionalidade Core**:
- ✅ Multi-agent orchestration (Abaporu coordena)
- ✅ Anomaly detection (Zumbi) - FFT spectral analysis
- ✅ Supplier analysis (Lampião) - IBGE integration
- ✅ Price analysis (Oxóssi) - statistical methods
- ✅ ML predictions (Céuci) - ARIMA/LSTM/Prophet **REAL**
- ⚠️ Social equity (Dandara) - framework pronto, APIs pendentes

**Qualidade**:
- ✅ 76.29% coverage geral (meta: 80%)
- ✅ 97.4% tests passing (1474/1514)
- ✅ 15/16 agents Tier 1/2

**Infraestrutura**:
- ✅ Railway production (99.9% uptime)
- ✅ PostgreSQL + Redis configurados
- ✅ Prometheus metrics endpoint
- ⚠️ Grafana dashboards (não validados)

---

**Conclusão**: Sistema está **85-90% pronto para entrega**. Com 1 dia focado nas prioridades acima, chegamos a **100% production-ready**! 🚀
