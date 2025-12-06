# Santos-Dumont - Educador do Sistema

**Codinome**: Alberto Santos-Dumont
**Tipo**: Educator Agent
**Arquivo**: `src/agents/santos_dumont.py`
**Classe**: `EducatorAgent`
**Alias**: `SantosDumontAgent`

## Visao Geral

Santos-Dumont e o agente educador do Cidadao.AI, especializado em ensinar estagiarios sobre a arquitetura, agentes e funcionamento do sistema. Inspirado no grande inventor brasileiro Alberto Santos-Dumont (1873-1932), o Pai da Aviacao, nascido em Palmira (hoje Santos Dumont), Minas Gerais.

## Filosofia de Ensino

> "O que eu fiz, qualquer um pode fazer!" - Alberto Santos-Dumont

- **Democratizacao**: Conhecimento aberto para todos
- **Pratica**: Aprender fazendo, construir prototipos, testar, iterar
- **Inovacao**: Sempre buscando formas melhores de ensinar
- **Persistencia**: Nunca desistir nos primeiros obstaculos

## Sobre Santos-Dumont

- Nascido em **Palmira, Minas Gerais** (hoje cidade de Santos Dumont) em 1873
- Inventor do **14-Bis**, realizou o primeiro voo publico homologado em 1906
- Pioneiro que **tornava publicas suas invencoes** para beneficio de todos
- Conhecido pela **persistencia** e **espirito colaborativo**
- Considerado o **Pai da Aviacao** no Brasil e em varios paises

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

## Uso via API

### Ensinar um Topico

```python
from src.agents import get_agent
from src.agents.deodoro import AgentMessage, AgentContext

agent = get_agent("santos_dumont")

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
    payload={
        "agent_name": "zumbi",
    },
    sender="intern"
)

response = await agent.process(message, AgentContext())
print(response.result["explanation"])
print(response.result["agent_info"])
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

### Responder Pergunta

```python
message = AgentMessage(
    action="answer_question",
    recipient="santos_dumont",
    payload={
        "question": "Como funciona o Zumbi?",
    },
    sender="intern"
)

response = await agent.process(message, AgentContext())
print(response.result["answer"])
```

### Primeiros Passos

```python
message = AgentMessage(
    action="first_steps",
    recipient="santos_dumont",
    payload={},
    sender="intern"
)

response = await agent.process(message, AgentContext())
print(response.result["guide"])
for item in response.result["checklist"]:
    print(f"[ ] {item}")
```

## Integracao com Academy

O Santos-Dumont e integrado ao sistema Academy para gamificacao:

- Disponivel em **todas as trilhas** (Backend, Frontend, IA, DevOps)
- Ensina sobre o sistema como um todo
- Sugere missoes baseadas no nivel do estagiario
- Conecta com agentes especialistas para deep dives

### Configuracao no Academy

```python
AGENT_TEACHERS = {
    "santos_dumont": {
        "display_name": "Alberto Santos-Dumont",
        "specialty": "Educacao sobre o sistema Cidadao.AI",
        "tracks": [TrackType.BACKEND, TrackType.FRONTEND, TrackType.IA, TrackType.DEVOPS],
        "personality": "Inventor pioneiro e incentivador",
        "greeting": "Meu caro amigo! Sou Santos-Dumont, o mineiro Pai da Aviacao...",
    },
}
```

## Base de Conhecimento

O agente possui conhecimento interno sobre:

### Sistema
- Nome, descricao, URL de producao
- Metricas (17 agentes, 323+ endpoints, 76% coverage)

### Agentes (todos os 17)
- Tipo, descricao, especialidade
- Arquivo de implementacao
- Algoritmos utilizados (quando aplicavel)

### Arquitetura
- Fluxo de orquestracao
- Lazy loading (benchmark)
- Estados do agente

### Contribuicao
- Comandos make
- Padrao de commits
- Arquivos importantes

## Exemplo de Saida

### Ensino de Visao Geral

```
Meu caro amigo, seja bem-vindo ao Cidadao.AI!

Como fiz com meus baloes e aeronaves, vamos primeiro entender a maquina que
voce vai pilotar.

## O que e o Cidadao.AI?

Plataforma multi-agente de IA para analise de transparencia governamental brasileira

## Os Numeros da Nossa Aeronave:
- **17 agentes** (16 operacionais + 1 framework base)
- **323+ endpoints** na API
- **76.29%** de cobertura de testes
- **1514 testes** automatizados

## A Tripulacao - Nossos Agentes

Cada agente e como uma peca do motor, com personalidade historica brasileira:
- **Zumbi dos Palmares**: Investigador de anomalias
- **Anita Garibaldi**: Analista de padroes
- **Tiradentes**: Gerador de relatorios
...

"O que eu fiz, qualquer um pode fazer!" - Vamos construir juntos!
```

## Testes

Os testes do agente estao em `tests/unit/agents/test_santos_dumont.py`:

```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_santos_dumont.py -v
```

### Cobertura de Testes

- 23 testes unitarios
- Testa todas as capacidades
- Testa lazy loading e aliases
- 100% de cobertura do agente

## Roadmap

### Futuras Melhorias

1. **Integracao com LLM**: Respostas mais naturais via Maritaca AI
2. **Quiz Interativo**: Testar conhecimento do estagiario
3. **Metricas de Aprendizado**: Rastrear progresso real
4. **Conteudo Multimidia**: Links para videos e tutoriais
5. **Mentoria Personalizada**: Adaptar ao estilo de aprendizado

## Citacoes de Santos-Dumont

O agente usa frases inspiradas em Santos-Dumont em suas respostas:

- "O que eu fiz, qualquer um pode fazer!"
- "Inventar e imaginar o que a humanidade ainda nao pensou!"
- "A persistencia e o caminho do exito!"
- "O segredo e voar! Nao importa como!"
- "Nunca desisti de um projeto!"

## Autor

- **Data**: 2025-12-06
- **Autor**: Anderson H. Silva
- **Licenca**: Proprietary - All rights reserved
