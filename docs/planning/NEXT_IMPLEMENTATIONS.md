# 🎯 Próximas Implementações - Cidadão.AI Backend

**Data**: 06/11/2025
**Baseado em**: Roadmap v1.1 + Estado Atual dos Testes

---

## 📊 Estado Atual

### ✅ **Completado Recentemente**
- Performance Optimization (~2s faster startup via lazy loading)
- Agent lazy loading (367x speedup)
- Service lazy loading (500x speedup)
- Test infrastructure fixes
- Deprecation warnings resolved

### 📈 **Métricas Atuais**
- **Testes Passando**: 1160/1233 (94.07%)
- **Testes Falhando**: 73 (5.93%)
- **Testes Skipped**: 49
- **Agent Test Coverage**: 76.29%
- **Target Coverage**: 80%

### 🔴 **Categorias de Testes Falhando**
1. **Circuit Breaker** (12 testes) - Infraestrutura de resiliência
2. **IP Whitelist** (12 testes) - Controle de acesso
3. **Dados.gov Service** (9 testes) - Integração API externa
4. **Compression Middleware** (7 testes) - Middleware HTTP
5. **Export Service** (3 testes) - Geração de exports
6. **Agent Lazy Loader** (3 testes) - Sistema de carregamento
7. **Maritaca Client** (2 testes) - Cliente LLM
8. **Agent Memory** (1 teste) - Sistema de memória

---

## 🎯 Priorização de Próximas Implementações

### 🥇 **PRIORIDADE ALTA** (1-2 semanas)

#### 1. Fix Failing Tests (73 failures → 0)
**Por quê**: Necessário para estabilidade e confiança no sistema
**Impacto**: Critical - afeta release v1.1
**Esforço**: 3-5 dias

**Breakdown**:
- [ ] Circuit Breaker tests (12) - 1 dia
  - Problema: Async timing issues ou mudanças na implementação
  - Solução: Revisar e atualizar assertions, corrigir timeouts

- [ ] IP Whitelist tests (12) - 1 dia
  - Problema: Mudanças no modelo ou service
  - Solução: Atualizar mocks e fixtures

- [ ] Dados.gov Service tests (9) - 1 dia
  - Problema: API externa ou mudanças no client
  - Solução: Melhorar mocking de respostas HTTP

- [ ] Compression Middleware tests (7) - 0.5 dia
  - Problema: Mudanças no middleware ou configuração
  - Solução: Atualizar fixtures de request/response

- [ ] Remaining tests (33) - 1.5 dias
  - Export Service, Agent Lazy Loader, Maritaca Client, Memory

**Resultado Esperado**: 100% test pass rate (1233/1233)

#### 2. Aumentar Coverage para 80%+ (76% → 80%+)
**Por quê**: Garantir qualidade e confiança no código
**Impacto**: High - melhora manutenibilidade
**Esforço**: 2-3 dias

**Agentes que precisam de mais testes**:
- [ ] Drummond (35.48% → 80%) - 3h
- [ ] Céuci (10.49% → 80%) - 4h
- [ ] Obaluaiê (13.11% → 80%) - 4h
- [ ] Anita (10.59% → 80%) - 4h
- [ ] Nanã (11.76% → 80%) - 4h

**Resultado Esperado**: >80% overall coverage

#### 3. Complete Tier 2 Agents (5 agents)
**Por quê**: Expandir capacidades do sistema
**Impacto**: High - features importantes
**Esforço**: 4-6 dias

**Status Atual**:
- Abaporu (89%) - ✅ Praticamente completo
- Nanã (81%) - ✅ Quase completo
- Drummond (95%) - ⚠️ Falta integração LLM
- Céuci (90%) - ⚠️ Falta ML models
- Obaluaiê (85%) - ⚠️ Falta análise avançada

**Tasks**:
- [ ] Drummond: Integrar MaritacaClient completamente (1 dia)
- [ ] Céuci: Implementar modelos ML de predição (2 dias)
- [ ] Obaluaiê: Completar detecção de corrupção avançada (1.5 dias)
- [ ] Nanã: Finalizar sistema de memória vetorial (1 dia)
- [ ] Abaporu: Polimento final e testes (0.5 dia)

**Resultado Esperado**: 15/16 agents completos (94%)

---

### 🥈 **PRIORIDADE MÉDIA** (2-4 semanas)

#### 4. WebSocket Implementation
**Por quê**: Real-time updates melhoram UX
**Impacto**: Medium-High - feature diferenciadora
**Esforço**: 3-4 dias

**Tasks**:
- [ ] Implementar WebSocket server com FastAPI (1 dia)
- [ ] Migrar endpoints SSE para WebSocket (1 dia)
- [ ] Real-time investigation progress (1 dia)
- [ ] WebSocket client library + docs (1 dia)

**Benefícios**:
- Real-time progress updates
- Bi-directional communication
- Reduced polling overhead
- Better UX for long-running operations

#### 5. Agent Learning System
**Por quê**: Melhorar accuracy ao longo do tempo
**Impacto**: Medium - diferenciação competitiva
**Esforço**: 5-6 dias

**Components**:
- [ ] Agent memory persistence (2 dias)
- [ ] Pattern learning for Zumbi (2 dias)
- [ ] Feedback loop system (1 dia)
- [ ] Adaptive thresholds (1 dia)

**Resultado Esperado**: +10% accuracy improvement

#### 6. Database Query Optimization
**Por quê**: Melhorar performance em produção
**Impacto**: Medium - user experience
**Esforço**: 2-3 dias

**Tasks**:
- [ ] Profile slow queries (0.5 dia)
- [ ] Add database indexes (1 dia)
- [ ] Implement query result caching (1 dia)
- [ ] Connection pooling optimization (0.5 dia)

**Target**: <140ms P95 response time (from <200ms)

---

### 🥉 **PRIORIDADE BAIXA** (4+ semanas)

#### 7. Complete Dandara Agent (30% → 100%)
**Por quê**: Completude do sistema
**Impacto**: Low - feature nice-to-have
**Esforço**: 3-4 dias

**Missing Features**:
- Social justice metrics implementation
- Inequality analysis algorithms
- Demographic analysis
- Integration tests

#### 8. Advanced Monitoring & Alerting
**Por quê**: Observabilidade em produção
**Impacto**: Medium - operational excellence
**Esforço**: 3-4 dias

**Tasks**:
- [ ] Expand Prometheus metrics (1 dia)
- [ ] Create custom Grafana dashboards (1 dia)
- [ ] Implement alerting rules (1 dia)
- [ ] Add distributed tracing (1 dia)

#### 9. API Documentation Enhancement
**Por quê**: Developer experience
**Impacto**: Low-Medium - external developers
**Esforço**: 2 dias

**Tasks**:
- [ ] Add more examples to OpenAPI docs
- [ ] Create API tutorials
- [ ] Add Postman collection
- [ ] Video documentation

---

## 📅 Cronograma Sugerido (Próximas 2 Semanas)

### **Semana 1 (Nov 7-13)**
```
Seg-Ter: Fix failing tests (Circuit Breaker + IP Whitelist + Dados.gov)
Qua-Qui: Fix remaining tests + aumentar coverage
Sex:     Complete Tier 2 agents (Drummond + Obaluaiê)
```

### **Semana 2 (Nov 14-20)**
```
Seg-Ter: Complete Tier 2 agents (Céuci + Nanã + Abaporu)
Qua-Qui: WebSocket implementation
Sex:     Testing + documentation + release prep
```

---

## 🎯 Metas de Release v1.1

### **Must Have** (Bloqueadores de Release)
- ✅ Performance optimization (DONE - 2s faster)
- [ ] All tests passing (73 failures → 0)
- [ ] 80%+ test coverage (76% → 80%+)
- [ ] Tier 2 agents complete (5/5)

### **Should Have** (Importantes mas não bloqueadores)
- [ ] WebSocket implementation
- [ ] Agent learning system (basic)
- [ ] Database optimization

### **Nice to Have** (Future versions)
- [ ] Dandara agent completion
- [ ] Advanced monitoring
- [ ] Enhanced API docs

---

## 💡 Recomendação Imediata

**Começar por**: Fix Failing Tests (73 → 0)

**Justificativa**:
1. Bloqueia release v1.1
2. Afeta confiança no sistema
3. Pode indicar bugs críticos
4. Precisa ser feito de qualquer forma
5. ~5 dias de esforço (viável em 1 semana)

**Próximo Passo**:
```bash
# Analisar primeiro grupo de falhas
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/infrastructure/test_circuit_breaker.py -v --tb=short
```

---

## 📊 Métricas de Sucesso

| Métrica | Atual | Meta v1.1 | Status |
|---------|-------|-----------|--------|
| Test Pass Rate | 94.07% | 100% | 🔴 Missing 5.93% |
| Test Coverage | 76.29% | 80%+ | 🟡 Missing 3.71% |
| Agent Completion | 62.5% | 94% | 🟡 Need 5 agents |
| Startup Time | ~2s | <2s | ✅ Achieved |
| API Response (P95) | <200ms | <140ms | 🔴 Need optimization |

---

**Próxima Ação Recomendada**:
Começar com fix dos testes falhando, priorizando Circuit Breaker e IP Whitelist (24 testes = 33% das falhas).
