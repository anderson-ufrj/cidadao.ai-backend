# 🎯 Sprint Roadmap - November 19-25, 2025

**Sprint Goal**: Elevar cobertura de testes de 76.29% para 80%+ e resolver issues técnicos críticos
**Duration**: 5 dias úteis (19-25 Nov)
**Team**: Anderson Henrique + Claude Code
**Previous Sprint**: ROADMAP_TRABALHO_2025_11_18.md (100% completo ✅)

---

## 📊 Estado Atual (Baseline)

### Cobertura de Testes
- **Atual**: 76.29% (1,514 testes, 136 arquivos)
- **Meta**: 80%+ (target: 85%)
- **Gap**: 3.71% → 8.71%

### Agent Tiers
- **Tier 1** (>75%): 10 agentes (62.5%)
- **Tier 2** (50-75%): 5 agentes (31.3%)
- **Tier 3** (<50%): 1 agente (6.2%)

### Issues Conhecidos
1. ⚠️ Drummond import circular (HuggingFace Spaces)
2. ⚠️ Dandara com dados mock (falta integração de APIs)
3. ⚠️ 5 agentes Tier 2 precisam de boost

---

## 🎯 Objetivos da Sprint

### Objetivo Principal
**Alcançar 80%+ de cobertura média de testes** através de:
1. Boost de 3 agentes Tier 2 para Tier 1
2. Resolução de issues técnicos
3. Refatoração de código duplicado

### Objetivos Secundários
- ✅ Resolver import circular do Drummond
- ✅ Iniciar integração de APIs reais no Dandara
- ✅ Adicionar testes de integração faltantes
- ✅ Melhorar documentação de troubleshooting

---

## 📅 Cronograma (5 dias)

### 🗓️ Dia 1 (19 Nov) - Terça - Boost Obaluaiê & Céuci
**Foco**: Agentes com menor cobertura primeiro (maior ROI)

#### Manhã (4h) - Obaluaiê
- [ ] Análise de coverage: identificar branches não cobertas
- [ ] Adicionar 9 testes novos:
  - 3 testes de error handling
  - 3 testes de edge cases
  - 3 testes de reflection pattern
- [ ] Meta: 62.18% → 76%+ (Tier 2 → Tier 1)

#### Tarde (4h) - Céuci
- [ ] Análise de coverage: identificar gaps
- [ ] Adicionar 7 testes novos:
  - 3 testes de validação
  - 2 testes de error recovery
  - 2 testes de integration
- [ ] Meta: 65.31% → 76%+ (Tier 2 → Tier 1)

**Entregável Dia 1**: 2 agentes movidos para Tier 1 (+16 testes)

---

### 🗓️ Dia 2 (20 Nov) - Quarta - Boost Nanã & Issue Drummond
**Foco**: Completar boost Tier 2 + resolver import circular

#### Manhã (3h) - Nanã
- [ ] Análise de coverage detalhada
- [ ] Adicionar 5 testes novos:
  - 2 testes de async operations
  - 2 testes de concurrent processing
  - 1 teste de timeout handling
- [ ] Meta: 68.92% → 76%+ (Tier 2 → Tier 1)

#### Tarde (5h) - Drummond Import Fix
- [ ] Investigar import circular com MaritacaClient
- [ ] Testar 3 soluções:
  1. Lazy import dentro de métodos
  2. Split drummond_full.py vs drummond_simple.py
  3. Mover MaritacaClient para módulo separado
- [ ] Implementar melhor solução
- [ ] Testar em HuggingFace Spaces mock
- [ ] Descomentar em `__init__.py`
- [ ] Validar todos os 117 testes do Drummond

**Entregável Dia 2**: 1 agente Tier 1 + Drummond issue resolvido (+5 testes)

---

### 🗓️ Dia 3 (21 Nov) - Quinta - Abaporu Final Push & Dandara Prep
**Foco**: Finalizar Tier 2 + preparar integração Dandara

#### Manhã (2h) - Abaporu
- [ ] Adicionar 2 testes de reflection
- [ ] Meta: 73.45% → 76%+ (Tier 2 → Tier 1)

#### Tarde (6h) - Dandara API Integration Prep
- [ ] Mapear APIs de transparência disponíveis:
  - Portal da Transparência endpoints funcionais
  - PNCP (Plataforma Nacional de Contratações Públicas)
  - Compras.gov.br
  - APIs estaduais (TCE-CE, TCE-MG, etc.)
- [ ] Criar camada de abstração para APIs
- [ ] Implementar circuit breakers
- [ ] Adicionar rate limiting
- [ ] Preparar cache layer
- [ ] Documentar estratégia de integração

**Entregável Dia 3**: 1 agente Tier 1 + Arquitetura Dandara definida (+2 testes)

---

### 🗓️ Dia 4 (22 Nov) - Sexta - Dandara Integration Início
**Foco**: Conectar Dandara a APIs reais

#### Manhã (4h) - API Clients
- [ ] Implementar client para Portal da Transparência
- [ ] Implementar client para PNCP
- [ ] Adicionar error handling robusto
- [ ] Implementar retry logic com exponential backoff

#### Tarde (4h) - Dandara Core
- [ ] Substituir mock data por API calls
- [ ] Adicionar data transformation layer
- [ ] Implementar caching (Redis)
- [ ] Adicionar logging detalhado
- [ ] Testar com dados reais (sandbox)

**Entregável Dia 4**: Dandara conectado a 2 APIs reais

---

### 🗓️ Dia 5 (25 Nov) - Segunda - Integration Tests & Review
**Foco**: Testes de integração + review final

#### Manhã (4h) - Integration Tests
- [ ] Criar testes de integração Dandara:
  - Test real API calls (mock responses)
  - Test error scenarios
  - Test rate limiting
  - Test circuit breaker
  - Test cache layer
- [ ] Adicionar 8 integration tests
- [ ] Meta Dandara: 86.32% → 90%+ (Tier 3 → Tier 1)

#### Tarde (4h) - Final Review & Metrics
- [ ] Rodar coverage report completo
- [ ] Validar meta de 80%+ atingida
- [ ] Atualizar AGENT_COVERAGE_MATRIX.md
- [ ] Criar SPRINT_REVIEW_2025_11_25.md
- [ ] Commit & Push all changes

**Entregável Dia 5**: Sprint review completo + 80%+ coverage

---

## 📊 Métricas de Sucesso

### Coverage Goals

| Agente | Atual | Meta | Testes a Adicionar |
|--------|-------|------|--------------------|
| **Obaluaiê** | 62.18% | 76%+ | +9 testes |
| **Céuci** | 65.31% | 76%+ | +7 testes |
| **Nanã** | 68.92% | 76%+ | +5 testes |
| **Abaporu** | 73.45% | 76%+ | +2 testes |
| **Dandara** | 86.32% | 90%+ | +8 integration tests |

**Total Novos Testes**: 31 testes
**Coverage Esperado**: 76.29% → 82-85%

### Tier Distribution Goal

| Tier | Atual | Meta | Mudança |
|------|-------|------|---------|
| **Tier 1** | 10/16 (62.5%) | 15/16 (93.8%) | +5 agentes |
| **Tier 2** | 5/16 (31.3%) | 0/16 (0%) | -5 agentes |
| **Tier 3** | 1/16 (6.2%) | 1/16 (6.2%) | 0 agentes |

### Technical Debt Reduction

- [x] ~~Tiradentes sem testes~~ (resolvido sprint anterior)
- [ ] Drummond import circular → Resolvido
- [ ] Dandara mock data → APIs reais conectadas
- [ ] 5 agentes Tier 2 → Movidos para Tier 1

---

## 🛠️ Abordagem Técnica

### Estratégia de Testes

#### 1. Análise de Coverage (30min por agente)
```bash
# Gerar report detalhado
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_obaluaie.py \
  --cov=src.agents.obaluaie \
  --cov-report=html \
  --cov-report=term-missing

# Abrir no browser
firefox htmlcov/index.html

# Identificar linhas não cobertas
# Focar em: branches, error handling, edge cases
```

#### 2. Priorização de Testes
**Alta Prioridade**:
- Error handling paths (try/except não cobertos)
- Edge cases (valores None, listas vazias, etc.)
- Reflection pattern (quality < threshold)
- Async operations (timeouts, concurrent calls)

**Média Prioridade**:
- Integration scenarios
- Complex business logic
- Data transformation

**Baixa Prioridade**:
- Logging statements
- Simple getters/setters
- Already well-covered paths

#### 3. Template de Teste
```python
@pytest.mark.asyncio
async def test_agent_error_handling_scenario(agent, sample_data):
    """Test that agent handles [specific error] gracefully."""
    # Arrange: Setup error condition
    invalid_data = {"field": None}  # Causa erro

    message = AgentMessage(
        sender="test",
        recipient="agent",
        action="process",
        payload=invalid_data
    )

    # Act: Process with error
    response = await agent.process(message, AgentContext())

    # Assert: Verifica error handling
    assert response.status == AgentStatus.ERROR
    assert "error" in response.result
    assert "invalid" in response.result["error"].lower()
```

### Estratégia Drummond Fix

#### Análise do Problema
```python
# Current issue em __init__.py:
# from .drummond import CommunicationAgent  # Comentado

# Causa: import circular
# drummond.py → MaritacaClient → algum módulo → drummond.py
```

#### Solução 1: Lazy Import (Preferida)
```python
# drummond.py
def _get_maritaca_client():
    """Lazy import to avoid circular dependency."""
    from src.services.llm.maritaca import MaritacaClient
    return MaritacaClient()

class CommunicationAgent(ReflectiveAgent):
    def __init__(self):
        super().__init__(...)
        self._llm_client = None  # Lazy

    @property
    def llm_client(self):
        if self._llm_client is None:
            self._llm_client = _get_maritaca_client()
        return self._llm_client
```

#### Solução 2: Split Files (Se lazy não funcionar)
```python
# drummond_core.py - Core logic sem LLM
# drummond_full.py - Full version com LLM
# drummond_simple.py - Simple version (já existe)

# __init__.py
try:
    from .drummond_full import CommunicationAgent
except ImportError:
    from .drummond_simple import SimpleDrummondAgent as CommunicationAgent
```

### Estratégia Dandara APIs

#### APIs Disponíveis (Confirmados Funcionais)
1. **Portal da Transparência** (22% endpoints work)
   - `/api/v1/transparency/contracts` ✅
   - `/api/v1/transparency/servants` ✅
   - `/api/v1/transparency/agencies` ✅

2. **PNCP** (100% functional)
   - Contratos públicos
   - Licitações
   - Fornecedores

3. **Compras.gov.br** (functional)
   - Itens de compra
   - Preços de referência

4. **APIs Estaduais**
   - TCE-CE (funcional)
   - TCE-MG (funcional)
   - TCE-PE (funcional)

#### Arquitetura de Integração
```python
# src/services/transparency_apis/api_registry.py
class TransparencyAPIRegistry:
    """Registry of all transparency APIs."""

    def __init__(self):
        self.apis = {
            "portal_federal": PortalTransparenciaClient(),
            "pncp": PNCPClient(),
            "compras_gov": ComprasGovClient(),
            "tce_ce": TCECearaClient(),
            # ...
        }

    async def fetch_contracts(self, filters: dict) -> list:
        """Fetch contracts from all available APIs."""
        results = []

        for api_name, client in self.apis.items():
            try:
                async with client.circuit_breaker:
                    data = await client.get_contracts(filters)
                    results.extend(data)
            except APIError:
                logger.warning(f"API {api_name} failed, continuing...")

        return results
```

#### Circuit Breaker Pattern
```python
from src.infrastructure.resilience.circuit_breaker import CircuitBreaker

circuit = CircuitBreaker(
    failure_threshold=3,  # Abre após 3 falhas
    timeout=60.0,         # Reset após 60s
    expected_exception=APIError
)

async with circuit:
    response = await api_client.get_data()
```

---

## 📋 Checklist Diário

### Template Diário
```markdown
## Dia X - [Data]

### Manhã
- [ ] Tarefa 1
- [ ] Tarefa 2
- [ ] Code review

### Tarde
- [ ] Tarefa 3
- [ ] Testes
- [ ] Documentation

### Métricas
- Testes adicionados: X
- Coverage: X% → Y%
- Commits: X

### Bloqueios
- Nenhum / [Descrever]

### Aprendizados
- [Key learning 1]
- [Key learning 2]
```

---

## 🎯 Definition of Done

### Por Agente Movido para Tier 1
- [ ] Coverage ≥ 76%
- [ ] Testes novos passando (100% success rate)
- [ ] Todos os testes antigos ainda passando
- [ ] Coverage report gerado e revisado
- [ ] Commit feito com mensagem descritiva
- [ ] AGENT_COVERAGE_MATRIX.md atualizado

### Drummond Fix
- [ ] Import circular resolvido
- [ ] Descomentado em `__init__.py`
- [ ] Todos os 117 testes passando
- [ ] Testado build em HuggingFace Spaces mock
- [ ] Documentação atualizada

### Dandara Integration
- [ ] 2+ APIs reais conectadas
- [ ] Circuit breakers implementados
- [ ] Rate limiting ativo
- [ ] Cache layer funcionando
- [ ] 8 integration tests passando
- [ ] Coverage ≥ 90%
- [ ] Documentação de APIs atualizada

### Sprint Complete
- [ ] Coverage geral ≥ 80%
- [ ] 15/16 agentes em Tier 1
- [ ] CI passando 100%
- [ ] SPRINT_REVIEW_2025_11_25.md criado
- [ ] Todos os commits pushed
- [ ] Métricas atualizadas no README.md

---

## 🚧 Riscos e Mitigações

### Risco 1: Drummond Fix Mais Complexo que Esperado
**Probabilidade**: Média
**Impacto**: Alto
**Mitigação**:
- Alocar dia inteiro (Dia 2 tarde)
- Ter 3 soluções alternativas preparadas
- Se não resolver em 1 dia, mover para sprint seguinte

### Risco 2: APIs de Transparência Instáveis
**Probabilidade**: Alta
**Impacto**: Médio
**Mitigação**:
- Implementar circuit breakers logo no início
- Ter fallback para múltiplas APIs
- Cache agressivo (24h TTL)
- Testes com mock responses

### Risco 3: Coverage Não Atingir 80%
**Probabilidade**: Baixa
**Impacto**: Médio
**Mitigação**:
- Foco em agentes com menor coverage primeiro (maior ROI)
- 31 testes planejados devem ser suficientes
- Buffer: se necessário, adicionar mais testes Dia 5

### Risco 4: Testes Quebrando Outros Testes
**Probabilidade**: Média
**Impacto**: Baixo
**Mitigação**:
- Rodar suite completa após cada agent
- Usar fixtures isolados
- Pre-commit hooks garantem qualidade

---

## 📊 Métricas de Acompanhamento

### Tracking Diário
| Dia | Agentes Tier 1 | Coverage | Testes Adicionados | Issues Resolvidos |
|-----|----------------|----------|-------------------|-------------------|
| Início | 10/16 (62.5%) | 76.29% | 0 | 0 |
| Dia 1 | 12/16 (75.0%) | ~78% | +16 | 0 |
| Dia 2 | 13/16 (81.3%) | ~79% | +21 | 1 (Drummond) |
| Dia 3 | 14/16 (87.5%) | ~80% | +23 | 1 (Drummond) |
| Dia 4 | 14/16 (87.5%) | ~80% | +23 | 1 (Drummond) |
| Dia 5 | 15/16 (93.8%) | 82-85% | +31 | 2 (Drummond + Dandara) |

### Burndown Esperado
```
Testes Restantes:
Dia 0: 31 testes
Dia 1: 15 testes (16 adicionados)
Dia 2: 10 testes (5 adicionados)
Dia 3: 8 testes (2 adicionados)
Dia 4: 8 testes (0 adicionados - foco em APIs)
Dia 5: 0 testes (8 adicionados)
```

---

## 💡 Tips & Best Practices

### Writing Effective Tests

1. **Test Names Should Tell a Story**
   ```python
   # ❌ Bad
   async def test_agent_1():

   # ✅ Good
   async def test_agent_handles_invalid_input_gracefully():
   ```

2. **Arrange-Act-Assert Pattern**
   ```python
   async def test_reflection_improves_result_quality():
       # Arrange: Setup low-quality result
       low_quality_data = {"confidence": 0.6}

       # Act: Trigger reflection
       response = await agent.reflect_and_retry(message, low_quality_data)

       # Assert: Quality improved
       assert response.result["confidence"] > 0.8
   ```

3. **Use Descriptive Assertions**
   ```python
   # ❌ Bad
   assert x == y

   # ✅ Good
   assert response.status == AgentStatus.COMPLETED, \
       f"Expected COMPLETED but got {response.status}, error: {response.error}"
   ```

### Debugging Coverage Gaps

```bash
# 1. Generate detailed report
pytest tests/unit/agents/test_agent.py --cov=src.agents.agent --cov-report=term-missing

# 2. Look for:
#    - Lines with "!" (not executed)
#    - "->exit" (branch not taken)
#    - "partials" (partial branch coverage)

# 3. Add tests targeting those lines specifically
```

### Dandara API Integration

```python
# Best Practice: Defensive programming
async def fetch_contracts(self, cpf: str) -> list:
    """Fetch contracts with robust error handling."""
    try:
        # Try primary API
        async with self.circuit_breaker:
            return await self.primary_api.get_contracts(cpf)

    except (APIError, TimeoutError) as e:
        self.logger.warning(f"Primary API failed: {e}, trying fallback")

        try:
            # Fallback to secondary API
            return await self.secondary_api.get_contracts(cpf)

        except Exception as e:
            self.logger.error(f"All APIs failed: {e}")

            # Return cached data if available
            cached = await self.cache.get(f"contracts:{cpf}")
            if cached:
                return cached

            # Last resort: empty list with warning
            return []
```

---

## 🎓 Learning Objectives

### Technical Skills
- [ ] Master pytest coverage analysis
- [ ] Learn circuit breaker pattern
- [ ] Practice rate limiting implementation
- [ ] Understand async API integration
- [ ] Improve error handling patterns

### Process Skills
- [ ] Daily standup discipline
- [ ] Effective time boxing
- [ ] Risk mitigation strategies
- [ ] Metrics-driven development

---

## 📚 Resources

### Documentation
- [Pytest Coverage Docs](https://pytest-cov.readthedocs.io/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Portal da Transparência API](https://api.portaldatransparencia.gov.br/swagger-ui.html)
- [PNCP Documentation](https://pncp.gov.br/api/docs)

### Internal Docs
- `docs/architecture/multi-agent-architecture.md`
- `docs/agents/` (agent-specific docs)
- `docs/project/AGENT_COVERAGE_MATRIX.md`
- `WORK_SUMMARY_2025_11_18.md` (previous sprint)

---

## 🎯 Success Criteria

Sprint será considerado **sucesso** se:

✅ **Coverage ≥ 80%** (target: 82-85%)
✅ **≥14 agentes em Tier 1** (target: 15)
✅ **Drummond issue resolvido**
✅ **Dandara conectado a ≥2 APIs reais**
✅ **31+ testes adicionados**
✅ **0 regressions** (todos os testes antigos passando)

Sprint será **excepcional** se:

🏆 **Coverage ≥ 85%**
🏆 **15 agentes em Tier 1** (93.8%)
🏆 **Dandara 100% funcional** (Tier 3 → Tier 1)
🏆 **40+ testes adicionados**
🏆 **Documentation completa** para todas as mudanças

---

**Criado em**: 2025-11-18
**Sprint Start**: 2025-11-19
**Sprint End**: 2025-11-25
**Team**: Anderson Henrique da Silva + Claude Code
**Status**: 🚀 Ready to Start!

---

**Let's ship it! 🚢**
