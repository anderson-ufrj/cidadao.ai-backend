# 🎯 Sprint Plan - Q4 2025

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data de Criação**: 25 de outubro de 2025 (Sábado)
**Período**: 25 de outubro - 31 de dezembro de 2025
**Timezone**: America/Sao_Paulo (UTC-3)

---

## 📅 Contexto Temporal

**Hoje**: Sábado, 25 de outubro de 2025
**Dias até fim do ano**: 67 dias
**Semanas de trabalho**: ~9 semanas úteis

---

## 🎯 Objetivos do Q4 2025

### Meta Principal
**Elevar o projeto de 44% → 75% de agentes operacionais**

### Métricas Alvo

| Métrica | Atual | Meta Q4 | Delta |
|---------|-------|---------|-------|
| **Agentes Operacionais** | 7/16 (44%) | 12/16 (75%) | +5 agentes |
| **Test Coverage** | 40% | 70% | +30 pontos |
| **Agentes com Testes** | 6/16 (37.5%) | 14/16 (87.5%) | +8 agentes |
| **TODOs Resolvidos** | 147 | <50 | -97 TODOs |

---

## 📊 Sprint Breakdown (9 Semanas)

### 🔥 Sprint 1: Setup & Oxóssi Tests (25/10 - 01/11)
**Foco**: Infraestrutura + Primeiro grande entregável

#### Objetivos
- [x] ✅ Análise completa da codebase (DONE 25/10)
- [x] ✅ Criação de documentação de onboarding (DONE 25/10)
- [ ] Setup do ambiente local completo
- [ ] **Entregável**: Testes completos para Oxóssi (0% → 80%+)

#### Tarefas Detalhadas
```
Segunda 26/10
├─ [ ] Ativar venv, rodar make install-dev
├─ [ ] Configurar .env com API keys
├─ [ ] Rodar make run-dev, testar localhost:8000
├─ [ ] Estudar src/agents/oxossi.py (903 linhas)
└─ [ ] Mapear os 7+ algoritmos de fraude

Terça 27/10
├─ [ ] Criar tests/unit/agents/test_oxossi.py
├─ [ ] Escrever testes para bid_rigging detection
├─ [ ] Escrever testes para phantom_vendor detection
└─ [ ] Coverage parcial: ~30%

Quarta 28/10
├─ [ ] Testes para price_fixing detection
├─ [ ] Testes para invoice_fraud detection
├─ [ ] Testes para money_laundering detection
└─ [ ] Coverage parcial: ~60%

Quinta 29/10
├─ [ ] Testes para kickback_schemes detection
├─ [ ] Testes para complex_fraud patterns
├─ [ ] Edge cases e error handling
└─ [ ] Coverage alvo: 80%+

Sexta 30/10
├─ [ ] Code review dos testes
├─ [ ] Rodar pytest --cov-report=html
├─ [ ] Ajustes finais
└─ [ ] Commit: "test(agents): add comprehensive tests for Oxossi fraud detection"

Sábado-Domingo 31/10-01/11
├─ [ ] Buffer / refinamento
├─ [ ] Documentação dos testes
└─ [ ] Preparar PR se necessário
```

**Critério de Sucesso**:
- ✅ Oxóssi coverage: 0% → 80%+
- ✅ Todos os 7 algoritmos de fraude testados
- ✅ Edge cases cobertos
- ✅ Documentação atualizada

---

### 📊 Sprint 2: Prometheus Metrics (02/11 - 08/11)
**Foco**: Observabilidade

#### Objetivos
- [ ] Instrumentar código Python com métricas Prometheus
- [ ] **Entregável**: Dashboards Grafana com dados reais

#### Tarefas
```
Segunda 02/11
├─ [ ] Estudar src/agents/metrics_wrapper.py
├─ [ ] Entender padrão de decorators existente
└─ [ ] Mapear agentes Tier 1 que precisam de métricas

Terça 03/11
├─ [ ] Adicionar decorators de métricas em Zumbi
├─ [ ] Adicionar decorators em Anita
└─ [ ] Testar exposição em /health/metrics

Quarta 04/11
├─ [ ] Instrumentar Tiradentes, Senna, Bonifácio
├─ [ ] Instrumentar Machado, Oxóssi
└─ [ ] Verificar métricas no Prometheus local

Quinta 05/11
├─ [ ] Configurar dashboards Grafana
├─ [ ] Testar visualizações
└─ [ ] Ajustar queries PromQL

Sexta 06/11
├─ [ ] Documentar métricas implementadas
├─ [ ] Code review
└─ [ ] Commit: "feat(monitoring): implement Prometheus metrics for Tier 1 agents"
```

**Critério de Sucesso**:
- ✅ 7 agentes Tier 1 instrumentados
- ✅ Métricas visíveis em /health/metrics
- ✅ Grafana mostrando dados reais
- ✅ Documentação de métricas criada

---

### 🔧 Sprint 3: Supabase Integration (09/11 - 15/11)
**Foco**: Persistência de dados

#### Objetivos
- [ ] Validar integração Supabase
- [ ] Garantir persistência de investigações
- [ ] **Entregável**: Database 100% funcional

#### Tarefas
```
Segunda 09/11
├─ [ ] Verificar configuração Supabase atual
├─ [ ] Testar conexão local → Supabase
└─ [ ] Mapear models que precisam persistência

Terça 10/11
├─ [ ] Implementar persistência para Investigations
├─ [ ] Testar CRUD operations
└─ [ ] Verificar migrations

Quarta 11/11
├─ [ ] Integrar Nanã com PostgreSQL
├─ [ ] Implementar memory persistence
└─ [ ] Testes de integração

Quinta 12/11
├─ [ ] Validar em produção (Railway)
├─ [ ] Verificar queries performance
└─ [ ] Indexação se necessário

Sexta 13/11
├─ [ ] Documentação da integração
└─ [ ] Commit: "feat(infrastructure): complete Supabase integration for persistence"
```

**Critério de Sucesso**:
- ✅ Investigations persistidas corretamente
- ✅ Nanã usando PostgreSQL
- ✅ Performance adequada
- ✅ Testes de integração passando

---

### 🤖 Sprint 4-5: Completar Abaporu (16/11 - 29/11)
**Foco**: Master Orchestrator (2 semanas)

#### Objetivos
- [ ] Abaporu: 70% → 100% funcional
- [ ] **Entregável**: Coordenação multi-agente real

#### Tarefas (Semana 1: 16/11-22/11)
```
├─ [ ] Estudar src/agents/abaporu.py (710 linhas)
├─ [ ] Identificar TODOs e placeholders
├─ [ ] Implementar coordenação real (remover asyncio.sleep)
├─ [ ] Implementar lógica de reflexão real
└─ [ ] Testes unitários iniciais
```

#### Tarefas (Semana 2: 23/11-29/11)
```
├─ [ ] Implementar workflows complexos
├─ [ ] Testar coordenação entre 3+ agentes
├─ [ ] Testes de integração multi-agente
├─ [ ] Documentação completa
└─ [ ] Commit: "feat(agents): complete Abaporu multi-agent orchestration"
```

**Critério de Sucesso**:
- ✅ Abaporu coordena múltiplos agentes simultaneamente
- ✅ Reflexão implementada (não placeholder)
- ✅ Testes de coordenação com 3+ agentes
- ✅ Coverage: 70%+

---

### 🧠 Sprint 6: Completar Nanã (30/11 - 06/12)
**Foco**: Memory System

#### Objetivos
- [ ] Nanã: 65% → 95% funcional
- [ ] **Entregável**: Sistema de memória completo

#### Tarefas
```
├─ [ ] Implementar persistência real (não in-memory)
├─ [ ] Implementar aprendizado de padrões real
├─ [ ] Integrar com PostgreSQL/Redis
├─ [ ] Base de conhecimento persistente
├─ [ ] Testes de memória episódica
├─ [ ] Testes de memória semântica
└─ [ ] Commit: "feat(agents): complete Nanã memory system with persistence"
```

**Critério de Sucesso**:
- ✅ Memória persiste entre sessões
- ✅ Aprendizado de padrões funcional
- ✅ Integração Redis funcionando
- ✅ Coverage: 70%+

---

### 🗺️ Sprint 7: Completar Lampião (07/12 - 13/12)
**Foco**: Regional Analysis

#### Objetivos
- [ ] Lampião: 60% → 90% funcional
- [ ] **Entregável**: Análises geográficas reais

#### Tarefas
```
├─ [ ] Implementar algoritmos geográficos reais
├─ [ ] Integração real com API IBGE
├─ [ ] Cálculos de Gini/Theil/Williamson reais
├─ [ ] Spatial autocorrelation (Moran's I)
├─ [ ] Hotspot detection real
├─ [ ] Testes com dados IBGE reais
└─ [ ] Commit: "feat(agents): complete Lampião regional analysis with IBGE integration"
```

**Critério de Sucesso**:
- ✅ Análises usam dados IBGE reais
- ✅ Métricas calculadas corretamente
- ✅ Mapas geográficos funcionais
- ✅ Coverage: 70%+

---

### 🛡️ Sprint 8: Completar Maria Quitéria (14/12 - 20/12)
**Foco**: Security & Compliance

#### Objetivos
- [ ] Maria Quitéria: 55% → 90% funcional
- [ ] **Entregável**: Security auditing completo

#### Tarefas
```
├─ [ ] Implementar detecção de intrusão real
├─ [ ] Scan de vulnerabilidades funcional
├─ [ ] LGPD/ISO27001 compliance checks reais
├─ [ ] Integração MITRE ATT&CK
├─ [ ] Testes de security patterns
└─ [ ] Commit: "feat(agents): complete Maria Quitéria security auditing system"
```

**Critério de Sucesso**:
- ✅ Detecção de ameaças funcional
- ✅ Compliance checks operacionais
- ✅ Relatórios de segurança gerados
- ✅ Coverage: 70%+

---

### 🎨 Sprint 9: Completar Niemeyer + Buffer (21/12 - 31/12)
**Foco**: Visualization + Fechamento Q4

#### Objetivos
- [ ] Oscar Niemeyer: 50% → 85% funcional
- [ ] **Entregável**: Visualizações renderizando

#### Tarefas (21/12-27/12)
```
├─ [ ] Integrar Plotly/D3.js
├─ [ ] Implementar rendering real (não placeholder)
├─ [ ] Mapas geográficos do Brasil
├─ [ ] Network graphs de fraude
├─ [ ] Dashboards interativos
└─ [ ] Commit: "feat(agents): complete Oscar Niemeyer visualization system"
```

#### Buffer & Review (28/12-31/12)
```
├─ [ ] Code review geral
├─ [ ] Documentação atualizada
├─ [ ] Relatório Q4 2025
├─ [ ] Planejamento Q1 2026
└─ [ ] Celebração! 🎉
```

---

## 📊 Acompanhamento de Progresso

### Métricas Semanais
Atualizar toda sexta-feira:

| Semana | Período | Agentes Op. | Coverage | TODOs | Status |
|--------|---------|-------------|----------|-------|--------|
| S1 | 25/10-01/11 | 7/16 (44%) | 40% | 147 | 🟡 In Progress |
| S2 | 02/11-08/11 | 7/16 (44%) | TBD | TBD | ⏳ Planned |
| S3 | 09/11-15/11 | 7/16 (44%) | TBD | TBD | ⏳ Planned |
| S4 | 16/11-22/11 | 8/16 (50%) | TBD | TBD | ⏳ Planned |
| S5 | 23/11-29/11 | 8/16 (50%) | TBD | TBD | ⏳ Planned |
| S6 | 30/11-06/12 | 9/16 (56%) | TBD | TBD | ⏳ Planned |
| S7 | 07/12-13/12 | 10/16 (62.5%) | TBD | TBD | ⏳ Planned |
| S8 | 14/12-20/12 | 11/16 (69%) | TBD | TBD | ⏳ Planned |
| S9 | 21/12-31/12 | 12/16 (75%) | 70% | <50 | ⏳ Planned |

### Checkpoint de Meio de Trimestre (25/11)
**1 mês após início**

Verificar:
- [ ] 3 sprints completos
- [ ] Oxóssi com testes ✅
- [ ] Prometheus funcionando ✅
- [ ] Supabase validado ✅
- [ ] Abaporu em progresso (50%+)
- [ ] Coverage: 50%+

**Se não atingir**: Reavaliar scope e ajustar plano

---

## 🎯 Critérios de Sucesso Q4

### Essenciais (Must Have)
- ✅ Oxóssi com testes completos (Sprint 1)
- ✅ Prometheus metrics implementado (Sprint 2)
- ✅ Supabase 100% funcional (Sprint 3)
- ✅ Test coverage ≥ 60%
- ✅ Pelo menos 3 agentes Tier 2 completados

### Desejáveis (Should Have)
- ✅ 5 agentes Tier 2 completados (Abaporu, Nanã, Lampião, Maria Q, Niemeyer)
- ✅ Test coverage ≥ 70%
- ✅ TODOs < 50
- ✅ Documentação 100% atualizada

### Bônus (Nice to Have)
- ✅ Começar agentes Tier 3
- ✅ Coverage ≥ 80%
- ✅ Grafana em produção
- ✅ Multi-agent workflows demo

---

## 🚧 Riscos e Mitigações

### Riscos Identificados

#### 1. Complexidade de Testes para Oxóssi
**Probabilidade**: Média
**Impacto**: Alto
**Mitigação**:
- Estudar exemplos de test_zumbi.py (já tem cobertura boa)
- Dividir em testes menores (por algoritmo)
- Pedir ajuda se travar >1 dia

#### 2. Integração Supabase pode ter issues
**Probabilidade**: Baixa
**Impacto**: Médio
**Mitigação**:
- Já está configurado, só precisa validar
- Fallback para in-memory se necessário
- Railway tem PostgreSQL nativo como alternativa

#### 3. Agentes Tier 2 podem demorar mais que 1 semana
**Probabilidade**: Alta
**Impacto**: Médio
**Mitigação**:
- Buffer de 2 semanas para Abaporu
- Priorizar funcionalidades core
- OK não atingir 100%, meta é 90%+

#### 4. Final de ano com feriados
**Probabilidade**: Alta
**Impacto**: Baixo
**Mitigação**:
- Planejar buffer na última semana
- Férias/descanso é importante
- Ajustar metas se necessário

---

## 📝 Template de Relatório Semanal

### Semana X (DD/MM - DD/MM)
**Sprint**: [Nome do Sprint]
**Foco**: [Objetivo principal]

#### ✅ Completado
- [ ] Task 1
- [ ] Task 2

#### 🚧 Em Progresso
- [ ] Task 3 (50%)

#### ⏳ Bloqueado
- [ ] Task 4 (Motivo: ...)

#### 📊 Métricas
- Agentes operacionais: X/16 (Y%)
- Test coverage: Z%
- TODOs: N

#### 💭 Observações
[Lições aprendidas, insights, problemas encontrados]

#### 🎯 Próxima Semana
[Foco para próxima sprint]

---

## 🎉 Celebrações Planejadas

### Mini-Milestones
- 🎊 Oxóssi 80% coverage (fim Sprint 1)
- 🎊 Prometheus funcionando (fim Sprint 2)
- 🎊 50% coverage total (metade Q4)
- 🎊 Primeiro agente Tier 2 100% (Abaporu)
- 🎊 10 agentes operacionais (62.5%)

### Major Milestone (31/12)
**🎉 Q4 2025 COMPLETE**
- 12/16 agentes operacionais (75%)
- 70% test coverage
- Monitoring em produção
- Base sólida para Q1 2026

---

## 📚 Recursos

### Daily
- `/docs/project/TEAM_ONBOARDING_2025_10_25.md` - Guia de onboarding
- `/docs/project/CURRENT_STATUS_2025_10.md` - Status verificado
- `/CLAUDE.md` - Referência rápida

### Weekly
- Este arquivo - Acompanhamento de sprints
- Coverage reports (htmlcov/index.html)
- Git commits (histórico de progresso)

### Tools
```bash
# Rodar testes
make test

# Ver coverage
pytest --cov=src --cov-report=html

# Ver métricas
curl http://localhost:8000/health/metrics

# Monitorar produção
railway logs --service cidadao-api
```

---

## 🔄 Revisão e Ajustes

### Check-in Semanal (Toda Sexta)
- [ ] Atualizar tabela de métricas semanais
- [ ] Escrever relatório da semana
- [ ] Planejar próxima semana
- [ ] Commit docs atualizados

### Check-in Mensal
- [ ] 25/11: Checkpoint 1 mês
- [ ] 25/12: Review completo Q4
- [ ] Ajustar plano Q1 2026

### Flexibilidade
**Este plano é vivo e pode ser ajustado!**

Se algo levar mais/menos tempo:
- ✅ OK reprirorizar
- ✅ OK pular sprints menos críticos
- ✅ OK adicionar buffer
- ❌ Não comprometer qualidade

**Prioridade #1**: Testes e qualidade
**Prioridade #2**: Funcionalidades core
**Prioridade #3**: Features bônus

---

**Plano criado em**: 25 de outubro de 2025, 12:30 -03
**Primeira revisão planejada**: 01 de novembro de 2025
**Status**: Ready to execute! 🚀

---

**Vamos fazer história! 🎯**
