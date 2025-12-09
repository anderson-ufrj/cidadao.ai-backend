# Santos-Dumont - Educador do Sistema Backend

**Codinome**: Alberto Santos-Dumont
**Tipo**: Backend Educator Agent
**Arquivo**: `src/agents/santos_dumont.py`
**Classe**: `EducatorAgent`
**Alias**: `SantosDumontAgent`
**Status**: 100% Operacional
**Coverage**: 90%+

## Visao Geral

Santos-Dumont e o agente educador do Cidadao.AI, especializado em ensinar desenvolvedores sobre a arquitetura, agentes e funcionamento do sistema backend. Inspirado no grande inventor brasileiro Alberto Santos-Dumont (1873-1932), o Pai da Aviacao, nascido em Palmira (hoje Santos Dumont), Minas Gerais.

## Sobre Santos-Dumont

- Nascido em **Palmira, Minas Gerais** (hoje cidade de Santos Dumont) em 1873
- Inventor do **14-Bis**, realizou o primeiro voo publico homologado em 1906
- Pioneiro que **tornava publicas suas invencoes** para beneficio de todos
- Conhecido pela **persistencia** e **espirito colaborativo**
- Considerado o **Pai da Aviacao** no Brasil e em varios paises

## Filosofia de Ensino

> "O que eu fiz, qualquer um pode fazer!" - Alberto Santos-Dumont

- **Democratizacao**: Conhecimento aberto para todos
- **Pratica**: Aprender fazendo, construir prototipos, testar, iterar
- **Inovacao**: Sempre buscando formas melhores de ensinar
- **Persistencia**: Nunca desistir nos primeiros obstaculos

## Capacidades

| Capability | Descricao |
|------------|-----------|
| `teach_system_overview` | Ensina visao geral do Cidadao.AI |
| `explain_agent_architecture` | Explica como os agentes funcionam |
| `guide_first_contribution` | Guia o primeiro commit/PR |
| `explain_specific_agent` | Explica um agente especifico |
| `troubleshoot_issues` | Ajuda com problemas comuns |
| `suggest_learning_path` | Sugere caminho de aprendizado |
| `answer_technical_questions` | Responde perguntas tecnicas |

## Topicos de Ensino

### 1. Visao Geral do Sistema (`system_overview`)

- O que e o Cidadao.AI
- Numeros importantes (17 agentes, 323+ endpoints)
- Equipe de agentes e suas personalidades
- URL de producao e documentacao

### 2. Arquitetura de Agentes (`agent_architecture`)

- Fluxo de orquestracao
- BaseAgent vs ReflectiveAgent
- Lazy loading (367x mais rapido)
- Estados e ciclo de vida

### 3. Agente Especifico (`specific_agent`)

Explicacao detalhada de qualquer um dos 17 agentes:
- Zumbi (Investigador)
- Anita (Analista)
- Tiradentes (Reporter)
- Drummond (Comunicador)
- Abaporu (Orquestrador)
- E todos os outros...

### 4. Estrutura da API (`api_structure`)

- Entry point (`src/api/app.py`)
- 39 rotas, 323+ endpoints
- Middleware stack
- SSE streaming

### 5. Guia de Contribuicao (`contribution_guide`)

- Configuracao do ambiente
- Padrao de commits
- Workflow de PR
- Prefixo de testes obrigatorio

### 6. Padroes de Teste (`testing_patterns`)

- Estrutura de testes
- pytest e fixtures
- Meta de 80% coverage
- Exemplos de testes

### 7. Primeira Missao (`first_mission`)

- Missoes para iniciantes
- Missoes intermediarias
- Como escolher e completar

### 8. Troubleshooting (`troubleshooting`)

- Problemas comuns e solucoes
- Erros de autenticacao
- Imports lentos
- Porta em uso

## Conhecimento do Sistema

### Infraestrutura

| Componente | Valor |
|------------|-------|
| **Deploy** | Railway (desde Oct 7, 2025) |
| **URL** | https://cidadao-api-production.up.railway.app/ |
| **Uptime** | 99.9% |
| **LLM Primario** | Maritaca AI (Sabia-3.1) |
| **LLM Backup** | Anthropic Claude |
| **Database** | PostgreSQL + asyncpg (prod) |
| **Cache** | Redis (prod) |

### Backend Stack

| Tecnologia | Versao |
|------------|--------|
| Python | 3.11+ |
| FastAPI | Latest |
| SQLAlchemy | 2.0 |
| Alembic | Latest |
| pytest | Latest |

### Agentes (17 total)

Santos-Dumont conhece todos os agentes:

| Agente | Tipo | Especialidade |
|--------|------|---------------|
| Deodoro | Framework | Base de todos os agentes |
| Zumbi | Investigator | Deteccao de anomalias |
| Anita | Analyst | Analise de padroes |
| Tiradentes | Reporter | Geracao de relatorios |
| Drummond | Communicator | Interface conversacional |
| Ayrton Senna | Router | Roteamento semantico |
| Bonifacio | Legal | Analise juridica |
| Maria Quiteria | Security | Supervisao e seguranca |
| Machado | Textual | Analise de documentos |
| Oxossi | Hunter | Busca de dados |
| Lampiao | Regional | Analise regional |
| Oscar Niemeyer | Aggregator | Agregacao de dados |
| Abaporu | Orchestrator | Coordenacao master |
| Nana | Memory | Gestao de contexto |
| Ceuci | ETL | Preditivo e ETL |
| Obaluaie | Health | Deteccao de corrupcao |
| Dandara | Equity | Equidade social |

## Redirecionamento Inteligente

Santos-Dumont redireciona para outros agentes quando apropriado:

```python
# Perguntas de frontend -> Bo Bardi
frontend_keywords = ["frontend", "react", "nextjs", "componente", "css", "tailwind"]

if any(kw in question for kw in frontend_keywords):
    return "Essa e uma pergunta sobre frontend - consulte a Bo Bardi!"
```

## Exemplo de Uso

### Ensinar um Topico

```python
from src.agents import EducatorAgent
from src.agents.deodoro import AgentMessage, AgentContext

agent = EducatorAgent()

message = AgentMessage(
    action="teach",
    recipient="santos_dumont",
    payload={
        "topic": "system_overview",
        "level": "beginner",
    },
    sender="intern"
)

response = await agent.process(message, AgentContext())
print(response.result["lesson"])
```

### Explicar Agente Especifico

```python
message = AgentMessage(
    action="explain_agent",
    recipient="santos_dumont",
    payload={"agent_name": "zumbi"},
    sender="intern"
)

response = await agent.process(message, AgentContext())
print(response.result["explanation"])
```

### Sugerir Caminho de Aprendizado

```python
message = AgentMessage(
    action="suggest_learning_path",
    recipient="santos_dumont",
    payload={
        "track": "backend",
        "level": "beginner",
        "interests": ["agents", "testing"],
    },
    sender="intern"
)

response = await agent.process(message, AgentContext())
for step in response.result["learning_path"]:
    print(f"{step['step']}. {step['title']} - {step['estimated_time']}")
```

## Exemplo de Resposta

**Pergunta**: "Quantos agentes existem?"

**Resposta**:
```
Temos 17 agentes no total:
- 16 agentes operacionais (cada um com especialidade unica)
- 1 framework base (Deodoro)

Os principais: Zumbi (investigador), Anita (analista), Tiradentes (relatorios),
Drummond (comunicacao), Abaporu (orquestrador).

Quer conhecer algum em detalhe?
```

## Troubleshooting Knowledge

Santos-Dumont conhece os problemas comuns:

### 1. Testes Falham com Auth Error

```bash
# Sempre use:
JWT_SECRET_KEY=test SECRET_KEY=test pytest ...
```

### 2. Imports Lentos

```python
# BOM - lazy loading
from src.agents import ZumbiAgent

# EVITAR - carregamento completo
from src.agents.zumbi import InvestigatorAgent
```

### 3. Porta Ocupada

```bash
lsof -i :8000
uvicorn src.api.app:app --port 8001
```

### 4. Entry Point Errado

```bash
# CORRETO
src/api/app.py

# ERRADO (so para HuggingFace Spaces)
app.py
```

## Testes

```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_santos_dumont.py -v
```

## Integracao com DSPy

O agente usa DSPy para respostas dinamicas:

```python
if _DSPY_AVAILABLE and _dspy_service:
    result = await _dspy_service.chat(
        agent_id="santos_dumont",
        message=question,
        intent_type="question",
        context=context,
    )
```

## Relacionamento com Outros Agentes

- **Bo Bardi**: Frontend mentor (complementary - she handles frontend questions)
- **Drummond**: Communication (shares educational mission)
- **Zumbi**: Reference agent (recommends for learning agent patterns)
- **Tiradentes**: Reporter (documentation partner)

## Citacoes de Santos-Dumont

O agente usa frases inspiradas:

- "O que eu fiz, qualquer um pode fazer!"
- "Inventar e imaginar o que a humanidade ainda nao pensou!"
- "A persistencia e o caminho do exito!"
- "O segredo e voar! Nao importa como!"
- "Nunca desisti de um projeto!"

## Metricas

| Metrica | Valor |
|---------|-------|
| Linhas de codigo | 1,644 |
| Capacidades | 7 |
| Topicos de ensino | 8 |
| Agentes documentados | 17 |
| Knowledge base | Sistema completo |
| Production Status | Live |

## Autor

- **Data**: 2025-12-06
- **Autor**: Anderson H. Silva
- **Licenca**: Proprietary - All rights reserved
