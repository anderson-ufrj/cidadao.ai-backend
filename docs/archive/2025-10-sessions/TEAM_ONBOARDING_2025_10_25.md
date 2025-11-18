# 🎯 Team Onboarding - Cidadão.AI Backend

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data**: Sábado, 25 de outubro de 2025 - 12:27 -03
**Timezone**: America/Sao_Paulo (UTC-3)
**Status**: Novo membro da equipe - Primeira sessão de trabalho

---

## 📅 Contexto Temporal

### Data Atual do Projeto
- **Hoje**: 25 de outubro de 2025 (Sábado)
- **Última análise oficial**: 09 de outubro de 2025 (16 dias atrás)
- **Deploy produção Railway**: 07 de outubro de 2025 (18 dias de uptime)
- **Última atualização docs**: 13 de outubro de 2025 (12 dias atrás)

### Timeline do Projeto (2025)
```
Janeiro 2025
├─ Início do desenvolvimento
├─ Implementação dos primeiros agentes
└─ Fase de prototipação

Julho-Setembro 2025
├─ Desenvolvimento intenso dos 16 agentes
├─ Implementação da API FastAPI
└─ Configuração de infraestrutura

Outubro 2025
├─ 07/10: Deploy produção no Railway ✅
├─ 09/10: Análise completa da codebase (CURRENT_STATUS_2025_10.md)
├─ 13/10: Atualização da documentação (INVENTORY.md)
└─ 25/10: Novo membro da equipe ingressa no projeto 🎯 ← HOJE
```

---

## 🎯 Status Atual (25/10/2025)

### O Que Sabemos
**Baseado na análise completa realizada hoje:**

#### ✅ Agentes Operacionais (7/16 - 44%)
1. ✅ **Zumbi dos Palmares** - Anomaly Detective (1,266 LOC, 2 test files)
2. ✅ **Anita Garibaldi** - Data Analyst (1,405 LOC, 1 test file)
3. ✅ **Tiradentes** - Report Writer (1,066 LOC, 3 test files)
4. ✅ **Ayrton Senna** - Agent Router (625 LOC, 2 test files)
5. ✅ **José Bonifácio** - Legal Expert (657 LOC, 1 test file)
6. ✅ **Machado de Assis** - Textual Analyst (622 LOC, 1 test file)
7. ✅ **Oxóssi** - Fraud Hunter (903 LOC, ❌ NO TESTS!)

#### ⚠️ Agentes com Framework Substancial (5/16 - 31%)
8. ⚠️ **Abaporu** - Master Orchestrator (710 LOC, 70% functional)
9. ⚠️ **Nanã** - Memory Manager (685 LOC, 65% functional)
10. ⚠️ **Lampião** - Regional Analyst (921 LOC, 60% functional)
11. ⚠️ **Maria Quitéria** - Security Guardian (823 LOC, 55% functional)
12. ⚠️ **Oscar Niemeyer** - Visualizer (648 LOC, 50% functional)

#### 🚧 Agentes Framework Only (4/16 - 25%)
13. 🚧 **Dandara** - Social Justice (385 LOC, 30% functional)
14. 🚧 **Drummond** - Communicator (958 LOC, 25% functional)
15. 🚧 **Ceuci** - Predictive AI (595 LOC, 10% functional)
16. 🚧 **Obaluaiê** - Corruption Detector (236 LOC, 15% functional)

### Infraestrutura em Produção (Railway)
```
✅ API FastAPI (2 replicas) - https://cidadao-api-production.up.railway.app
✅ Celery Worker (4 processes) - Background tasks 24/7
✅ Celery Beat (1 replica) - Scheduler
✅ Redis Cache - Persistent cache
✅ PostgreSQL (Supabase) - Database (partially integrated)
✅ Uptime: 99.9% (18 dias estáveis)
✅ Custo: ~$20/mês (sustentável)
```

### Métricas de Código
```
Total Lines of Code: ~66,000
Agents Code: ~14,439 lines (16 agents)
Test Files: 98 files
Test Coverage: ~40% (Target: 80%) 🔴
API Routes: 50 files (37 registered routes)
TODOs in Code: 147 found
```

---

## 🎯 Prioridades Identificadas

### 🔥 URGENTE (Próximos 7 dias)
**Prioridade**: ALTA
**Responsável**: Anderson Henrique da Silva (novo membro)
**Status**: Ready to start

1. **Criar testes para Oxóssi** 🎯
   - **Por quê**: Agente bem implementado (903 LOC, 7+ algoritmos de fraude) mas SEM testes
   - **Impacto**: Detecção de fraude é funcionalidade crítica
   - **Estimativa**: 2-3 dias de trabalho
   - **Arquivos envolvidos**:
     - `src/agents/oxossi.py` (ler e entender)
     - `tests/unit/agents/test_oxossi.py` (criar)
   - **Coverage esperada**: Levar de 0% → 80%+

2. **Implementar métricas Prometheus no código Python**
   - **Por quê**: Infraestrutura configurada, mas falta instrumentação
   - **Impacto**: Dashboards Grafana esperando dados
   - **Estimativa**: 1-2 dias
   - **Arquivos envolvidos**:
     - `src/agents/*.py` (adicionar decorators de métricas)
     - Verificar `src/agents/metrics_wrapper.py`

3. **Validar integração Supabase**
   - **Por quê**: Configurado mas parcialmente integrado
   - **Impacto**: Persistência de investigações
   - **Estimativa**: 1 dia
   - **Status**: Verificar se está realmente funcionando

### 📈 CURTO PRAZO (Próximas 2-4 semanas)

4. **Completar agentes Tier 2 (5 agentes)**
   - Abaporu: Coordenação real multi-agente
   - Nanã: Persistência PostgreSQL/Redis
   - Lampião: Algoritmos geográficos IBGE
   - Maria Quitéria: Detecção de segurança real
   - Niemeyer: Integrar Plotly/D3.js

5. **Expandir cobertura de testes: 40% → 60%**
   - Criar testes para agentes sem cobertura
   - Priorizar agentes Tier 2

### 🚀 MÉDIO PRAZO (Próximos 1-3 meses)

6. **Implementar agentes Tier 3 (4 agentes)**
   - Dandara: Análises de equidade reais
   - Drummond: Integrações de canais (Discord, Slack, Email)
   - Ceuci: Treinar modelos ML (ARIMA, Prophet, LSTM)
   - Obaluaiê: Lei de Benford + detecção de corrupção

7. **Observabilidade em produção**
   - Grafana dashboards ativos
   - Tracing distribuído (Jaeger)
   - Alerting configurado

---

## 📚 Documentação de Referência

### Documentos Principais (Leitura Obrigatória)
1. ✅ **CURRENT_STATUS_2025_10.md** - Status real verificado (09/10/2025)
2. ✅ **INVENTORY.md** - Status dos 16 agentes (13/10/2025)
3. ✅ **CLAUDE.md** (raiz) - Guia completo do projeto
4. ✅ **multi-agent-architecture.md** - 7 diagramas Mermaid

### Por Agente (docs/agents/)
- `zumbi.md` - Exemplo de agente 100% funcional
- `oxossi.md` - Algoritmos de fraude (PRIORIDADE LER!)
- `deodoro.md` - Base architecture (ReflectiveAgent)

### Deployment
- `docs/deployment/railway/` - Guias Railway
- `RAILWAY_24_7_COMPLETE_SYSTEM.md`

---

## 🛠️ Ambiente de Desenvolvimento

### Setup Inicial (Já realizado)
```bash
✅ Diretório: /home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend
✅ Git status: Clean working directory
✅ Branch: main
✅ Python: 3.13 (venv configurado)
✅ Estrutura: Analisada e compreendida
```

### Próximos Passos de Setup
```bash
# 1. Verificar ambiente virtual
source venv/bin/activate

# 2. Instalar dependências (se necessário)
make install-dev

# 3. Configurar .env
cp .env.example .env
# Adicionar: GROQ_API_KEY, JWT_SECRET_KEY, SECRET_KEY

# 4. Rodar servidor local
make run-dev
# Acessar: http://localhost:8000/docs

# 5. Rodar testes
JWT_SECRET_KEY=test SECRET_KEY=test make test
```

---

## 🎓 Plano de Aprendizado

### Dia 1 (Hoje - 25/10/2025 Sábado)
- [x] ✅ Análise completa da codebase
- [x] ✅ Compreensão da arquitetura multi-agente
- [x] ✅ Identificação de prioridades
- [ ] ⏳ Setup do ambiente local
- [ ] ⏳ Explorar API no Swagger UI

### Semana 1 (26/10 - 01/11)
**Foco**: Testes para Oxóssi

- [ ] Segunda: Ler e entender `src/agents/oxossi.py` completamente
- [ ] Terça: Escrever primeiros testes unitários (bid rigging, phantom vendors)
- [ ] Quarta: Completar testes (price fixing, invoice fraud)
- [ ] Quinta: Testes de integração + edge cases
- [ ] Sexta: Code review, coverage report (meta: 80%+)
- [ ] Sábado/Domingo: Buffer / documentação

**Entregável**: `tests/unit/agents/test_oxossi.py` com 80%+ coverage

### Semana 2 (02/11 - 08/11)
**Foco**: Métricas Prometheus

- [ ] Entender `src/agents/metrics_wrapper.py`
- [ ] Instrumentar agentes com decorators
- [ ] Verificar exposição em `/health/metrics`
- [ ] Testar integração com Grafana local
- [ ] Documentar métricas implementadas

**Entregável**: Métricas Prometheus funcionando + Grafana mostrando dados

### Semana 3-4 (09/11 - 22/11)
**Foco**: Agentes Tier 2

- [ ] Escolher 1-2 agentes Tier 2 para completar
- [ ] Implementar funcionalidades faltantes
- [ ] Criar/expandir testes
- [ ] Documentar melhorias

---

## 📊 Métricas de Sucesso

### Objetivos para o Primeiro Mês (25/10 - 25/11)

#### Testes
- [x] Coverage atual: 40%
- [ ] **Meta**: 60% coverage (ganho de 20 pontos percentuais)
- [ ] Oxóssi: 0% → 80%+ ✅
- [ ] Criar testes para pelo menos 2 agentes Tier 2

#### Agentes
- [x] Tier 1 operacional: 7/16 (44%)
- [ ] **Meta**: Ter 10/16 operacionais (62.5%)
- [ ] Completar 2-3 agentes Tier 2

#### Infraestrutura
- [x] Monitoring configurado: Sim (não ativo)
- [ ] **Meta**: Prometheus + Grafana com dados reais
- [ ] Métricas instrumentadas em todos os agentes Tier 1

#### Documentação
- [x] Docs existentes: Excelentes mas alguns outdated
- [ ] **Meta**: Docs 100% atualizados com mudanças
- [ ] Criar docs de troubleshooting

---

## 🤝 Workflow de Trabalho

### Git Commit Guidelines (CRÍTICO)
```bash
# ❌ NUNCA mencionar:

# - AI assistance
# - LLM tools
# - Generative AI

# ✅ Commits profissionais em inglês:
git commit -m "test(agents): add comprehensive unit tests for Oxossi fraud detection"
git commit -m "feat(monitoring): implement Prometheus metrics for all Tier 1 agents"
git commit -m "fix(api): resolve integration issue with Supabase persistence"
git commit -m "docs(agents): update Oxossi documentation with test examples"

# Padrão:
# <type>(scope): <subject>
#
# Types: feat, fix, docs, test, refactor, chore, perf
```

### Development Cycle
```
1. Branch strategy
   ├─ main: Production-ready code
   ├─ feature/oxossi-tests: Working branch
   └─ feature/prometheus-metrics: Working branch

2. Before commit
   ├─ make check (lint + type-check + test)
   ├─ JWT_SECRET_KEY=test SECRET_KEY=test pytest
   └─ Review changes

3. Commit
   ├─ Professional English message
   ├─ No AI mentions
   └─ Focus on what was implemented/fixed

4. Deploy
   ├─ Push to GitHub
   ├─ Railway auto-deploys from main
   └─ Verify production endpoints
```

---

## 📞 Comunicação

### Desenvolvedor Principal
**Nome**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Timezone**: America/Sao_Paulo (UTC-3)
**Email**: andersonhs27@gmail.com
**Horário de Trabalho**: Flexível (considerando finais de semana)

### Canais
- **GitHub Issues**: Para bugs e feature requests
- **Git Commits**: Documentação das mudanças
- **docs/**: Documentação técnica

---

## 🎯 Ação Imediata (Próximas 2 horas)

### Setup do Ambiente
```bash
# 1. Ativar venv
cd /home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend
source venv/bin/activate

# 2. Verificar instalação
make check

# 3. Rodar servidor
make run-dev

# 4. Testar API (novo terminal)
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/agents/ | jq

# 5. Acessar Swagger
# Navegador: http://localhost:8000/docs
```

### Primeiros Estudos
```bash
# 1. Ler o agente Oxóssi
cat src/agents/oxossi.py | less

# 2. Ver exemplo de testes
cat tests/unit/agents/test_zumbi.py | less

# 3. Verificar estrutura de testes
ls -la tests/unit/agents/

# 4. Ver coverage atual
JWT_SECRET_KEY=test SECRET_KEY=test pytest --cov=src.agents.oxossi --cov-report=term
```

---

## 📝 Notas da Sessão

### Sessão 1 - 25/10/2025 (Sábado) 12:27
**Participante**: Anderson Henrique da Silva (novo membro)
**Duração**: ~1 hora
**Atividades**:
- ✅ Análise completa da codebase (24 agents files, 98 test files, 50 API routes)
- ✅ Identificação de 16 agentes (7 operacionais, 5 framework, 4 minimal)
- ✅ Mapeamento de prioridades (Oxóssi tests = URGENTE)
- ✅ Análise de infraestrutura (Railway production, 99.9% uptime)
- ✅ Criação deste documento de onboarding

**Principais Descobertas**:
1. Oxóssi tem 903 LOC com 7+ algoritmos de fraude mas ZERO testes
2. Test coverage está em 40% (meta: 80%)
3. Infraestrutura de monitoring configurada mas não instrumentada
4. 9 agentes (Tier 2 + Tier 3) precisam de implementação

**Próximas Ações**:
1. Setup ambiente local
2. Rodar API e explorar Swagger UI
3. Estudar `src/agents/oxossi.py` em detalhe
4. Começar escrita de testes na segunda-feira

**Observações**:
- Documentação está excelente e bem organizada
- Código tem boa qualidade (passa linting, type hints 85%)
- Projeto tem potencial enorme, precisa foco em testes
- Arquitetura multi-agente é bem pensada

---

## 🏆 Objetivos de Longo Prazo

### Q4 2025 (Out-Dez)
- [ ] Test coverage: 40% → 80%
- [ ] Agentes operacionais: 7 → 12 (75%)
- [ ] Monitoring em produção (Prometheus + Grafana)
- [ ] Documentação 100% atualizada

### Q1 2026 (Jan-Mar)
- [ ] Todos os 16 agentes 100% operacionais
- [ ] Test coverage: 90%+
- [ ] Performance optimization
- [ ] Multi-agent coordination completa (Abaporu)

### Q2 2026 (Abr-Jun)
- [ ] ML models treinados (Ceuci)
- [ ] Integrações de canais (Drummond)
- [ ] Advanced fraud detection (Obaluaiê com Lei de Benford)
- [ ] Social justice analytics (Dandara com dados reais)

---

**Status**: Pronto para começar! 🚀
**Primeira tarefa**: Setup do ambiente + Estudo do Oxóssi
**Meta da semana 1**: Testes completos para Oxóssi (0% → 80%+)

---

**Documento criado em**: 25 de outubro de 2025, 12:27 -03
**Última atualização**: 25 de outubro de 2025, 12:27 -03
**Versão**: 1.0.0
