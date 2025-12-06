"""
Module: agents.santos_dumont
Codinome: Alberto Santos-Dumont - Inventor e Educador do Sistema
Description: Agent specialized in teaching interns about the Cidadao.AI system
Author: Anderson H. Silva
Date: 2025-12-06
License: Proprietary - All rights reserved
"""

from enum import Enum
from typing import Any

from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)
from src.core import get_logger
from src.core.exceptions import AgentExecutionError


class LearningTopic(Enum):
    """Topics that Santos-Dumont can teach."""

    SYSTEM_OVERVIEW = "system_overview"
    AGENT_ARCHITECTURE = "agent_architecture"
    SPECIFIC_AGENT = "specific_agent"
    API_STRUCTURE = "api_structure"
    CONTRIBUTION_GUIDE = "contribution_guide"
    TESTING_PATTERNS = "testing_patterns"
    CODE_PATTERNS = "code_patterns"
    FIRST_MISSION = "first_mission"
    TROUBLESHOOTING = "troubleshooting"


class DifficultyLevel(Enum):
    """Difficulty levels for explanations."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EducatorAgent(BaseAgent):
    """
    Alberto Santos-Dumont - Inventor e Educador do Sistema

    MISSAO:
    Ensinar estagiarios sobre a arquitetura, agentes e funcionamento do
    Cidadao.AI de forma pratica e inovadora, seguindo o espirito pioneiro
    do Pai da Aviacao.

    SOBRE SANTOS-DUMONT:
    - Nascido em Palmira (hoje Santos Dumont), Minas Gerais, em 1873
    - Inventor do 14-Bis, realizou o primeiro voo publico homologado (1906)
    - Pioneiro que tornava publicas suas invencoes para beneficio de todos
    - Conhecido pela persistencia e espirito colaborativo

    FILOSOFIA:
    - "O que eu fiz, qualquer um pode fazer" - democratizacao do conhecimento
    - Inovacao com proposito social
    - Construir, testar, iterar, voar!

    CAPACIDADES EDUCACIONAIS:

    1. VISAO GERAL DO SISTEMA:
       - Explicar a arquitetura multi-agente (17 agentes)
       - Mostrar o fluxo de orquestracao
       - Apresentar as APIs de transparencia

    2. ARQUITETURA DE AGENTES:
       - Como o BaseAgent/ReflectiveAgent funciona
       - Padrao de implementacao de agentes
       - Ciclo de vida e estados
       - Lazy loading e performance

    3. AGENTES ESPECIFICOS:
       - Capacidades de cada um dos 16 agentes operacionais
       - Quando usar cada agente
       - Exemplos praticos de uso

    4. ESTRUTURA DA API:
       - 323+ endpoints organizados em 39 rotas
       - Middleware stack e ordem de execucao
       - Autenticacao e seguranca
       - SSE streaming para chat

    5. GUIA DE CONTRIBUICAO:
       - Como fazer o primeiro commit
       - Padrao de testes (80% coverage)
       - Padrao de commits em ingles
       - Code review e PR workflow

    6. PADROES DE CODIGO:
       - Async/await everywhere
       - Multi-layer caching
       - Circuit breaker pattern
       - Error handling

    7. TROUBLESHOOTING:
       - Problemas comuns e solucoes
       - Debug de agentes
       - Variaveis de ambiente

    INTEGRACAO COM ACADEMY:
    - Sugere missoes baseadas no nivel do estagiario
    - Conecta com agentes especialistas para deep dives
    - Gera XP por aprendizado demonstrado
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(
            name="santos_dumont",
            description="Alberto Santos-Dumont - Inventor e Educador do Sistema Cidadao.AI",
            capabilities=[
                "teach_system_overview",
                "explain_agent_architecture",
                "guide_first_contribution",
                "explain_specific_agent",
                "troubleshoot_issues",
                "suggest_learning_path",
                "answer_technical_questions",
            ],
            max_retries=3,
            timeout=60,
        )
        self.logger = get_logger(__name__)

        # Knowledge base about the system
        self._load_system_knowledge()

        # Personality configuration
        self.personality_prompt = """Voce e Alberto Santos-Dumont, inventor mineiro e Pai da Aviacao.

ESTILO: Entusiasmado, pratico, incentivador (motiva a construir e experimentar).
FALA: "Meu caro amigo...", "Vamos construir juntos!", "Como fiz com o 14-Bis..."
FOCO: Ensinar sobre o sistema Cidadao.AI de forma pratica, como um projeto de engenharia.
METODO: Aprender fazendo, construir prototipos, testar, iterar.
LEMBRE: "O que eu fiz, qualquer um pode fazer" - democratize o conhecimento!

ORIGEM: Nascido em Palmira, Minas Gerais (hoje cidade de Santos Dumont).
VALORES: Inovacao aberta, colaboracao, persistencia, elegancia tecnica.

Voce conhece profundamente:
- Os 17 agentes do sistema (16 operacionais + 1 base framework)
- A arquitetura multi-agente baseada em Deodoro
- As APIs de transparencia governamental
- Os padroes de codigo e contribuicao
"""

    def _load_system_knowledge(self) -> None:
        """Load knowledge base about the Cidadao.AI system."""
        self.system_knowledge = {
            "overview": {
                "name": "Cidadao.AI",
                "description": "Plataforma multi-agente de IA para analise de transparencia governamental brasileira",
                "production_url": "https://cidadao-api-production.up.railway.app/",
                "agents_total": 17,
                "agents_operational": 16,
                "test_coverage": "76.29%",
                "total_tests": 1514,
                "endpoints": "323+",
            },
            "agents": {
                "deodoro": {
                    "type": "Base Framework",
                    "description": "Marechal Deodoro - Base de todos os agentes",
                    "classes": ["BaseAgent", "ReflectiveAgent"],
                    "features": [
                        "Quality threshold 0.8",
                        "Max 3 reflection iterations",
                        "State management",
                    ],
                    "file": "src/agents/deodoro.py",
                },
                "zumbi": {
                    "type": "Investigator",
                    "description": "Zumbi dos Palmares - Investigador de anomalias",
                    "specialty": "Deteccao de anomalias em dados financeiros",
                    "algorithms": ["Z-Score", "IQR", "Isolation Forest", "LOF"],
                    "file": "src/agents/zumbi.py",
                },
                "anita": {
                    "type": "Analyst",
                    "description": "Anita Garibaldi - Analista de padroes",
                    "specialty": "Analise estatistica e identificacao de padroes",
                    "file": "src/agents/anita.py",
                },
                "tiradentes": {
                    "type": "Reporter",
                    "description": "Tiradentes - Gerador de relatorios",
                    "specialty": "Documentacao e comunicacao clara",
                    "file": "src/agents/tiradentes.py",
                },
                "drummond": {
                    "type": "Communicator",
                    "description": "Carlos Drummond de Andrade - Comunicador do povo",
                    "specialty": "Interface conversacional e traducao de dados tecnicos",
                    "file": "src/agents/drummond.py",
                },
                "ayrton_senna": {
                    "type": "Semantic Router",
                    "description": "Ayrton Senna - Roteador semantico",
                    "specialty": "Roteamento inteligente de queries para agentes",
                    "file": "src/agents/ayrton_senna.py",
                },
                "bonifacio": {
                    "type": "Legal Analyst",
                    "description": "Jose Bonifacio - Analista juridico",
                    "specialty": "Analise de conformidade legal e normativa",
                    "file": "src/agents/bonifacio.py",
                },
                "maria_quiteria": {
                    "type": "Security",
                    "description": "Maria Quiteria - Guardia da seguranca",
                    "specialty": "Supervisao e seguranca do sistema",
                    "file": "src/agents/maria_quiteria.py",
                },
                "machado": {
                    "type": "Textual Analysis",
                    "description": "Machado de Assis - Analista textual",
                    "specialty": "Analise de documentos e textos",
                    "file": "src/agents/machado.py",
                },
                "oxossi": {
                    "type": "Data Hunter",
                    "description": "Oxossi - Cacador de dados",
                    "specialty": "Busca e recuperacao de dados",
                    "file": "src/agents/oxossi.py",
                },
                "lampiao": {
                    "type": "Regional",
                    "description": "Lampiao - Especialista regional",
                    "specialty": "Analise de dados regionais e locais",
                    "file": "src/agents/lampiao.py",
                },
                "oscar_niemeyer": {
                    "type": "Aggregator",
                    "description": "Oscar Niemeyer - Agregador de dados",
                    "specialty": "Agregacao e visualizacao de dados",
                    "file": "src/agents/oscar_niemeyer.py",
                },
                "abaporu": {
                    "type": "Master Orchestrator",
                    "description": "Abaporu - Orquestrador mestre",
                    "specialty": "Coordenacao de investigacoes multi-agente",
                    "file": "src/agents/abaporu.py",
                },
                "nana": {
                    "type": "Memory",
                    "description": "Nana - Guardia da memoria",
                    "specialty": "Gestao de contexto e memoria",
                    "file": "src/agents/nana.py",
                },
                "ceuci": {
                    "type": "Predictive/ETL",
                    "description": "Ceuci - Agente preditivo",
                    "specialty": "Predicoes e processamento ETL",
                    "file": "src/agents/ceuci.py",
                },
                "obaluaie": {
                    "type": "Corruption Detection",
                    "description": "Obaluaie - Detector de corrupcao",
                    "specialty": "Deteccao de padroes de corrupcao",
                    "file": "src/agents/obaluaie.py",
                },
                "dandara": {
                    "type": "Social Equity",
                    "description": "Dandara - Analista de equidade",
                    "specialty": "Analise de equidade social e acessibilidade",
                    "file": "src/agents/dandara.py",
                },
            },
            "architecture": {
                "flow": "User Query -> IntentClassifier -> EntityExtractor -> ExecutionPlanner -> DataFederationExecutor -> EntityGraph -> Investigation Agent(s) -> Consolidated Result",
                "base_agent": {
                    "file": "src/agents/deodoro.py",
                    "quality_threshold": 0.8,
                    "max_iterations": 3,
                    "states": [
                        "IDLE",
                        "THINKING",
                        "ACTING",
                        "WAITING",
                        "ERROR",
                        "COMPLETED",
                    ],
                },
                "lazy_loading": {
                    "improvement": "367x faster startup",
                    "before": "1460.41ms",
                    "after": "3.81ms",
                    "file": "src/agents/__init__lazy.py",
                },
            },
            "contribution": {
                "test_prefix": "JWT_SECRET_KEY=test SECRET_KEY=test",
                "coverage_target": "80%",
                "commit_language": "English only",
                "commit_format": "<type>(scope): summary",
                "commit_types": ["feat", "fix", "docs", "test", "refactor", "chore"],
                "important_files": {
                    "entry_point": "src/api/app.py",
                    "agent_base": "src/agents/deodoro.py",
                    "config": "src/core/config.py",
                },
            },
            "commands": {
                "run_dev": "make run-dev",
                "run_tests": "JWT_SECRET_KEY=test SECRET_KEY=test make test",
                "format": "make format",
                "check": "make check",
                "install": "make install-dev",
            },
        }

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Process educational messages and requests."""
        try:
            action = message.action
            payload = message.payload

            if action == "teach":
                topic = payload.get("topic", "system_overview")
                level = payload.get("level", "beginner")
                specific_agent = payload.get("agent_name")
                question = payload.get("question", "")

                response = await self._teach(topic, level, specific_agent, question)

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "lesson": response["content"],
                        "metadata": response.get("metadata", {}),
                        "suggested_next": response.get("suggested_next", []),
                        "related_agents": response.get("related_agents", []),
                    },
                    metadata={"educational": True, "topic": topic},
                )

            elif action == "answer_question":
                question = payload.get("question", "")
                response = await self._answer_question(question)

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "answer": response["content"],
                        "metadata": response.get("metadata", {}),
                    },
                    metadata={"educational": True, "type": "qa"},
                )

            elif action == "suggest_learning_path":
                track = payload.get("track", "backend")
                current_level = payload.get("level", "beginner")
                interests = payload.get("interests", [])

                path = await self._suggest_learning_path(
                    track, current_level, interests
                )

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "learning_path": path,
                        "status": "path_generated",
                    },
                    metadata={"educational": True, "type": "learning_path"},
                )

            elif action == "explain_agent":
                agent_name = payload.get("agent_name", "zumbi")
                response = await self._explain_agent(agent_name)

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "explanation": response["content"],
                        "agent_info": response.get("agent_info", {}),
                    },
                    metadata={"educational": True, "explained_agent": agent_name},
                )

            elif action == "first_steps":
                response = await self._guide_first_steps()

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "guide": response["content"],
                        "checklist": response.get("checklist", []),
                    },
                    metadata={"educational": True, "type": "onboarding"},
                )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={"error": "Unknown educational action"},
                metadata={"confidence": 0.0},
            )

        except Exception as e:
            self.logger.error(f"Error in education: {str(e)}")
            raise AgentExecutionError(f"Education failed: {str(e)}")

    async def _teach(
        self,
        topic: str,
        level: str,
        specific_agent: str | None,
        question: str,
    ) -> dict[str, Any]:
        """Generate educational content based on topic."""

        if topic == "system_overview":
            return await self._teach_system_overview(level)
        elif topic == "agent_architecture":
            return await self._teach_agent_architecture(level)
        elif topic == "specific_agent" and specific_agent:
            return await self._explain_agent(specific_agent)
        elif topic == "contribution_guide":
            return await self._teach_contribution_guide(level)
        elif topic == "testing_patterns":
            return await self._teach_testing_patterns(level)
        elif topic == "api_structure":
            return await self._teach_api_structure(level)
        elif topic == "first_mission":
            return await self._guide_first_mission()
        elif topic == "troubleshooting":
            return await self._teach_troubleshooting()
        else:
            return await self._answer_question(question or topic)

    async def _teach_system_overview(self, level: str) -> dict[str, Any]:
        """Teach about the Cidadao.AI system overview."""
        overview = self.system_knowledge["overview"]

        content = f"""
Meu caro amigo, seja bem-vindo ao Cidadao.AI!

Como fiz com meus baloes e aeronaves, vamos primeiro entender a maquina que
voce vai pilotar. Assim como o 14-Bis precisava de estrutura, motor e asas,
nosso sistema tem suas partes essenciais.

## O que e o Cidadao.AI?

{overview["description"]}

Em producao: {overview["production_url"]}

## Os Numeros da Nossa Aeronave:
- **{overview["agents_total"]} agentes** ({overview["agents_operational"]} operacionais + 1 framework base)
- **{overview["endpoints"]} endpoints** na API
- **{overview["test_coverage"]}** de cobertura de testes
- **{overview["total_tests"]} testes** automatizados

## A Tripulacao - Nossos Agentes

Cada agente e como uma peca do motor, com personalidade historica brasileira:
- **Zumbi dos Palmares**: Investigador de anomalias (o detetive)
- **Anita Garibaldi**: Analista de padroes (a estrategista)
- **Tiradentes**: Gerador de relatorios (o comunicador)
- **Drummond**: Interface com o cidadao (o poeta)
- **Abaporu**: Orquestrador mestre (o maestro)

E muitos outros! Cada um e essencial, como cada parte de um aviao.

## Proximo Voo

O que voce gostaria de explorar agora?
1. Entender como os agentes funcionam (a engenharia)
2. Aprender a contribuir (construir junto)
3. Conhecer um agente especifico

"O que eu fiz, qualquer um pode fazer!" - Vamos construir juntos!
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "system_overview", "level": level},
            "suggested_next": [
                "agent_architecture",
                "contribution_guide",
                "specific_agent",
            ],
            "related_agents": ["abaporu", "zumbi", "drummond"],
        }

    async def _teach_agent_architecture(self, level: str) -> dict[str, Any]:
        """Teach about the agent architecture."""
        arch = self.system_knowledge["architecture"]

        content = f"""
Vamos entender a engenharia dos agentes, meu caro!

Assim como projetei cada detalhe do 14-Bis, cada agente aqui foi
cuidadosamente arquitetado.

## O Fluxo de Voo (Orquestracao)

```
{arch["flow"]}
```

## O Motor Central: Deodoro

Todos os 16 agentes herdam de `BaseAgent` ou `ReflectiveAgent`, definidos em
`{arch["base_agent"]["file"]}`.

### Especificacoes Tecnicas:
- **Quality Threshold**: {arch["base_agent"]["quality_threshold"]} (calibragem minima)
- **Max Iterations**: {arch["base_agent"]["max_iterations"]} tentativas de ajuste
- **Estados**: {" -> ".join(arch["base_agent"]["states"])}

### Projeto de um Agente (Blueprint):

```python
from src.agents.deodoro import ReflectiveAgent, AgentMessage, AgentResponse

class MeuAgente(ReflectiveAgent):
    def __init__(self):
        super().__init__(
            name="meu_agente",
            description="O que este agente faz",
            capabilities=["cap1", "cap2"],
            quality_threshold=0.8
        )

    async def process(self, message: AgentMessage, context) -> AgentResponse:
        # Sua logica aqui - como o motor do aviao
        result = await self._minha_analise(message.content)

        return AgentResponse(
            agent_name=self.name,
            status="success",
            result=result,
            metadata={{"confidence": 0.9}}
        )
```

## Lazy Loading - Otimizacao de Performance

Como reduzi o peso dos meus baloes para voar mais alto:
- **Antes**: {arch["lazy_loading"]["before"]} para importar
- **Depois**: {arch["lazy_loading"]["after"]} (367x mais leve!)

Arquivo: `{arch["lazy_loading"]["file"]}`

## Sistema de Reflexao

Os agentes reflexivos sao como pilotos experientes:
1. Executam a manobra
2. Avaliam o resultado
3. Se < 0.8 de qualidade, ajustam e tentam de novo
4. Maximo de 3 tentativas

"Inventar e imaginar o que a humanidade ainda nao pensou!"
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "agent_architecture", "level": level},
            "suggested_next": [
                "specific_agent",
                "contribution_guide",
                "testing_patterns",
            ],
            "related_agents": ["deodoro"],
        }

    async def _teach_contribution_guide(self, level: str) -> dict[str, Any]:
        """Teach how to contribute to the project."""
        contrib = self.system_knowledge["contribution"]
        commands = self.system_knowledge["commands"]

        content = f"""
Quer construir junto? Magnifico! Vamos montar sua oficina!

Assim como eu trabalhava em meu hangar em Neuilly, voce precisa
de um ambiente bem preparado.

## Montando sua Oficina (Ambiente)

```bash
# Clonar e entrar no projeto
git clone <repo>
cd cidadao.ai-backend

# Criar ambiente isolado (seu hangar)
python3 -m venv venv
source venv/bin/activate

# Instalar ferramentas
{commands["install"]}

# Configurar variaveis
cp .env.example .env
# Editar .env com suas chaves
```

## Testes - Verificacao de Voo

**IMPORTANTE**: Sempre teste antes de voar!

```bash
{commands["run_tests"]}
```

Por que o prefixo `{contrib["test_prefix"]}`?
- Isola os testes (como testar em tunel de vento)
- Evita acidentes com producao
- Protege dados sensiveis

## Registro de Voo (Commits)

Commits em ingles, formato padrao:

```
{contrib["commit_format"]}
```

Tipos validos: {", ".join(contrib["commit_types"])}

**Exemplos de bons registros:**
- `feat(agents): add fraud detection algorithm`
- `fix(api): resolve SSE streaming timeout`
- `test(zumbi): add integration tests for anomaly detection`

**NUNCA incluir:**
- Mencoes a IA/AI
- "Generated by..."
- Emojis de robos

## Plantas Importantes

- **Cabine de comando**: `{contrib["important_files"]["entry_point"]}`
- **Motor principal**: `{contrib["important_files"]["agent_base"]}`
- **Painel de controle**: `{contrib["important_files"]["config"]}`

## Seu Primeiro Voo (PR)

1. Crie uma pista: `git checkout -b feat/minha-feature`
2. Construa sua melhoria
3. Teste: `{commands["run_tests"]}`
4. Calibre: `{commands["format"]}`
5. Registre: `git commit -m "feat(scope): description"`
6. Decole: `git push -u origin feat/minha-feature`
7. Solicite autorizacao (PR no GitHub)

## Checagem Pre-Voo

Antes de cada commit:
```bash
{commands["check"]}
```

Isso verifica: formatacao, lint, tipos e testes.

"A persistencia e o caminho do exito!" - Nao desista nos primeiros testes!
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "contribution_guide", "level": level},
            "suggested_next": ["testing_patterns", "first_mission"],
            "related_agents": ["tiradentes"],
        }

    async def _explain_agent(self, agent_name: str) -> dict[str, Any]:
        """Explain a specific agent in detail."""
        agent_name = agent_name.lower().strip()
        agents = self.system_knowledge["agents"]

        if agent_name not in agents:
            available = ", ".join(agents.keys())
            content = f"""
Meu caro, nao encontrei o agente "{agent_name}" no hangar.

Agentes disponiveis: {available}

Qual deles voce gostaria de conhecer?
            """
            return {
                "content": content.strip(),
                "metadata": {"error": "agent_not_found"},
            }

        agent = agents[agent_name]

        content = f"""
## {agent["description"]}

**Funcao**: {agent["type"]}
**Projeto**: `{agent["file"]}`

### Especialidade
{agent.get("specialty", "Componente base do sistema")}
"""

        if "algorithms" in agent:
            content += f"""
### Mecanismos Utilizados
{", ".join(agent["algorithms"])}
"""

        if "classes" in agent:
            content += f"""
### Pecas Exportadas
{", ".join(agent["classes"])}
"""

        if "features" in agent:
            content += f"""
### Caracteristicas Tecnicas
- {chr(10).join("- " + f for f in agent["features"])}
"""

        content += f"""

### Como Acionar

```python
from src.agents import {agent_name.title().replace("_", "")}Agent

# Ou via lazy loading (mais eficiente)
from src.agents import get_agent
agent = get_agent("{agent_name}")
```

### Quer Estudar o Projeto?

O arquivo esta em `{agent["file"]}`. Recomendo estudar
para entender os padroes de construcao.

"Voar e muito mais que um sonho - e uma ciencia!"
        """

        return {
            "content": content.strip(),
            "agent_info": agent,
            "metadata": {"topic": "specific_agent", "agent": agent_name},
            "suggested_next": ["agent_architecture", "testing_patterns"],
        }

    async def _guide_first_steps(self) -> dict[str, Any]:
        """Guide interns through their first steps."""

        content = """
## Bem-vindo ao Seu Primeiro Dia de Voo!

Meu caro amigo, hoje voce comeca sua jornada como aviador do Cidadao.AI!
Assim como preparei cada detalhe antes do voo do 14-Bis, vamos preparar tudo.

### Checklist Pre-Voo

1. [ ] Clone o repositorio (baixe os projetos)
2. [ ] Configure o hangar (`python3 -m venv venv`)
3. [ ] Instale as ferramentas (`make install-dev`)
4. [ ] Configure o painel (`.env` de `.env.example`)
5. [ ] Teste os motores (rode os testes)
6. [ ] Ligue os sistemas (`make run-dev`)
7. [ ] Verifique instrumentos: http://localhost:8000/docs

### Reconhecimento do Terreno

Depois de configurar, explore:

1. **Leia o CLAUDE.md** - O manual completo da aeronave
2. **Mapeie a estrutura**:
   - `src/agents/` - Os 17 motores (agentes)
   - `src/api/routes/` - As 39 rotas de voo
   - `src/services/` - Sistemas auxiliares
   - `tests/` - 149 procedimentos de teste

3. **Acione um agente**:
```python
from src.agents import get_agent
zumbi = get_agent("zumbi")
print(zumbi.capabilities)
```

### Sua Primeira Missao

Sugiro comecar com voos curtos:
- Adicionar um teste para um agente existente
- Melhorar a documentacao de uma funcao
- Corrigir um pequeno bug

### Precisa de Suporte?

Estou aqui no torre de controle! Pergunte sobre:
- Qualquer agente especifico
- Como funciona alguma parte do sistema
- Problemas que encontrar

"O segredo e voar! Nao importa como!"

Vamos construir o futuro juntos!
        """

        checklist = [
            "Clone o repositorio",
            "Configure ambiente virtual",
            "Instale dependencias",
            "Configure .env",
            "Rode os testes",
            "Rode o servidor local",
            "Acesse a documentacao",
        ]

        return {
            "content": content.strip(),
            "checklist": checklist,
            "metadata": {"topic": "first_steps", "type": "onboarding"},
            "suggested_next": ["system_overview", "contribution_guide"],
        }

    async def _guide_first_mission(self) -> dict[str, Any]:
        """Guide through the first mission."""
        content = """
## Sua Primeira Missao de Voo

Vamos escolher uma missao adequada ao seu nivel de experiencia...

### Missoes para Novos Pilotos

1. **Adicionar Teste Unitario** (Easy - 10 XP)
   - Escolha um agente com baixa cobertura
   - Adicione testes para um metodo especifico
   - Arquivo: `tests/unit/agents/test_<agent>.py`

2. **Documentar Funcao** (Easy - 10 XP)
   - Encontre uma funcao sem documentacao
   - Adicione docstring clara
   - Siga o padrao Google docstrings

3. **Corrigir Typo** (Easy - 5 XP)
   - Encontre erros de digitacao
   - Corrija em codigo ou documentacao

### Missoes para Pilotos Intermediarios

4. **Implementar Metodo de Agente** (Medium - 25 XP)
   - Adicione nova capacidade a um agente
   - Inclua testes
   - Minimo 80% cobertura

5. **Adicionar Endpoint** (Medium - 25 XP)
   - Crie novo endpoint na API
   - Inclua testes de integracao
   - Documente no OpenAPI

### Procedimento de Voo

1. Escolha uma missao
2. Crie uma pista: `git checkout -b feat/minha-missao`
3. Construa com testes
4. Verificacao pre-voo: `make check`
5. Solicite autorizacao (PR)

### Dica do Inventor

Comece pelo Zumbi (`src/agents/zumbi.py`) - e o agente mais
bem documentado e serve como referencia de projeto.

"Nunca desisti de um projeto - a persistencia e o motor do sucesso!"

Qual missao voce escolhe?
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "first_mission"},
            "suggested_next": ["testing_patterns", "specific_agent"],
        }

    async def _teach_testing_patterns(self, level: str) -> dict[str, Any]:
        """Teach about testing patterns in the project."""
        content = """
## Procedimentos de Teste - Tunel de Vento

Assim como testava meus baloes antes de voar, todo codigo precisa de testes!

### Regra de Ouro

**SEMPRE** use as configuracoes de teste:
```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest ...
```

### Organizacao dos Testes

```
tests/
|-- unit/           # Testes de componentes isolados
|   |-- agents/     # Testes de agentes
|   |-- api/        # Testes de rotas
|   +-- services/   # Testes de servicos
|-- integration/    # Testes de sistemas integrados
+-- multiagent/     # Testes de voo em formacao
```

### Projeto de Teste para Agente

```python
import pytest
from src.agents.zumbi import InvestigatorAgent
from src.agents.deodoro import AgentMessage, AgentContext

@pytest.fixture
def agent():
    return InvestigatorAgent()

@pytest.fixture
def sample_message():
    return AgentMessage(
        sender="test",
        recipient="zumbi",
        action="detect_anomalies",
        payload={"data": [100, 200, 150, 10000]}
    )

@pytest.mark.asyncio
async def test_detect_anomalies(agent, sample_message):
    response = await agent.process(sample_message, AgentContext())

    assert response.status == "success"
    assert "anomalies" in response.result
    assert response.result["anomalies_count"] >= 1
```

### Comandos de Teste

```bash
# Teste completo
JWT_SECRET_KEY=test SECRET_KEY=test make test

# Testes unitarios
JWT_SECRET_KEY=test SECRET_KEY=test make test-unit

# Teste especifico
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_zumbi.py -v

# Com medicao de cobertura
JWT_SECRET_KEY=test SECRET_KEY=test pytest --cov=src --cov-report=html
```

### Meta de Qualidade

**80% de cobertura** minima para codigo novo.
Verifique o relatorio em `htmlcov/index.html`.

"Um aviao sem testes e um passaro sem asas - pode ate pular, mas nao voa!"
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "testing_patterns", "level": level},
            "suggested_next": ["contribution_guide", "first_mission"],
        }

    async def _teach_api_structure(self, level: str) -> dict[str, Any]:
        """Teach about the API structure."""
        content = """
## Painel de Controle - Estrutura da API

### Cabine Principal

O arquivo de comando e `src/api/app.py` (NAO o `app.py` da raiz!).

### Rotas de Voo (7 principais de 39)

- `/api/v1/chat/` - Comunicacao com agentes (SSE streaming)
- `/api/v1/agents/` - Acionamento direto de agentes
- `/api/v1/investigations/` - Gestao de investigacoes
- `/api/v1/federal/` - APIs federais (IBGE, DataSUS, INEP)
- `/api/v1/orchestration/` - Coordenacao multi-agente
- `/api/v1/transparency/` - Portal da Transparencia
- `/health/metrics` - Metricas de voo (Prometheus)

### Sistemas de Seguranca (Middleware Stack)

1. IPWhitelistMiddleware (filtro de origem)
2. CORSMiddleware (controle de acesso)
3. LoggingMiddleware (caixa preta)
4. SecurityMiddleware (escudo)
5. RateLimitMiddleware (controle de velocidade)
6. CompressionMiddleware (economia de combustivel)
7. CorrelationMiddleware (rastreamento)
8. MetricsMiddleware (instrumentos)

### SSE Streaming - Comunicacao em Tempo Real

O chat usa Server-Sent Events (como radio de bordo):

```python
from sse_starlette.sse import EventSourceResponse

async def stream_chat():
    async def event_generator():
        yield {"event": "thinking", "data": "..."}
        async for chunk in agent.process_stream(message):
            yield {"event": "chunk", "data": chunk}
        yield {"event": "complete", "data": result}

    return EventSourceResponse(event_generator())
```

### Manual de Voo

Acesse `/docs` para Swagger UI ou `/redoc` para ReDoc.

"A simplicidade e a maior das sofisticacoes!" - Leonardo da Vinci
(Meu inspirador!)
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "api_structure", "level": level},
            "suggested_next": ["agent_architecture", "contribution_guide"],
        }

    async def _teach_troubleshooting(self) -> dict[str, Any]:
        """Teach common troubleshooting."""
        content = """
## Manutencao e Reparos

### 1. Testes Falham com Auth Error

**Sintoma**: "Authorization header is missing"

**Reparo**:
```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest ...
```

### 2. Imports Lentos

**Sintoma**: Demora para importar agentes

**Reparo**: Use lazy loading:
```python
# BOM - carregamento sob demanda
from src.agents import ZumbiAgent

# EVITAR - carregamento completo
from src.agents.zumbi import InvestigatorAgent
```

### 3. Porta Ocupada

**Sintoma**: "Address already in use"

**Reparo**:
```bash
# Identificar processo
lsof -i :8000

# Usar pista alternativa
uvicorn src.api.app:app --port 8001
```

### 4. Ambiente Virtual

**Sintoma**: ModuleNotFoundError

**Reparo**:
```bash
# Verificar hangar ativo
which python  # Deve mostrar venv/bin/python

# Reativar se necessario
source venv/bin/activate
```

### 5. Problemas de Banco

**Sintoma**: Erros de conexao

**Reparo**: O sistema usa SQLite in-memory por padrao.
Para PostgreSQL, configure `DATABASE_URL` no `.env`.

### 6. LLM Provider

**Sintoma**: Respostas genericas/fallback

**Reparo**: Configure `MARITACA_API_KEY` ou `ANTHROPIC_API_KEY` no `.env`.

### Ainda com Problemas?

1. Verifique o `.env`
2. Rode `make clean && make install-dev`
3. Consulte `CLAUDE.md`
4. Pergunte aqui na torre de controle!

"Todo problema tem solucao - basta persistir!"
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "troubleshooting"},
            "suggested_next": ["first_steps", "contribution_guide"],
        }

    async def _answer_question(self, question: str) -> dict[str, Any]:
        """Answer a general question about the system."""
        question_lower = question.lower()

        if "quantos agentes" in question_lower or "how many agents" in question_lower:
            return {
                "content": """
Temos **17 agentes** no total:
- 16 agentes operacionais (cada um com especialidade unica)
- 1 framework base (Deodoro)

Os principais: Zumbi (investigador), Anita (analista), Tiradentes (relatorios),
Drummond (comunicacao), Abaporu (orquestrador).

Quer conhecer algum em detalhe?
                """.strip(),
                "metadata": {"type": "factual"},
            }

        elif "zumbi" in question_lower:
            return await self._explain_agent("zumbi")

        elif "como contribuir" in question_lower or "contribuir" in question_lower:
            return await self._teach_contribution_guide("beginner")

        elif "teste" in question_lower:
            return await self._teach_testing_patterns("beginner")

        elif "primeiro" in question_lower or "comecar" in question_lower:
            return await self._guide_first_steps()

        else:
            return {
                "content": f"""
Excelente pergunta, meu caro! "{question}"

Para ajuda-lo melhor, posso falar sobre:

1. **Visao geral do sistema** - O que e o Cidadao.AI
2. **Arquitetura de agentes** - A engenharia dos 17 agentes
3. **Um agente especifico** - Zumbi, Drummond, Abaporu...
4. **Como contribuir** - Construir junto conosco
5. **Testes** - Procedimentos de qualidade
6. **Problemas comuns** - Manutencao e reparos

Qual tema te interessa?

"A curiosidade e o primeiro passo para a invencao!"
                """.strip(),
                "metadata": {"type": "clarification_needed"},
            }

    async def _suggest_learning_path(
        self, track: str, current_level: str, interests: list[str]
    ) -> list[dict[str, Any]]:
        """Suggest a personalized learning path."""
        path = []

        # Always start with basics
        path.append(
            {
                "step": 1,
                "title": "Visao Geral do Sistema",
                "topic": "system_overview",
                "description": "Conheca o Cidadao.AI e seus 17 agentes",
                "estimated_time": "30 min",
            }
        )

        path.append(
            {
                "step": 2,
                "title": "Arquitetura de Agentes",
                "topic": "agent_architecture",
                "description": "Entenda a engenharia (BaseAgent, ReflectiveAgent)",
                "estimated_time": "45 min",
            }
        )

        # Track-specific recommendations
        if track == "backend":
            path.append(
                {
                    "step": 3,
                    "title": "Conheca o Zumbi",
                    "topic": "specific_agent",
                    "agent": "zumbi",
                    "description": "O agente referencia - melhor projeto para estudar",
                    "estimated_time": "60 min",
                }
            )
        elif track == "ia":
            path.append(
                {
                    "step": 3,
                    "title": "Conheca o Abaporu",
                    "topic": "specific_agent",
                    "agent": "abaporu",
                    "description": "Orquestrador - coordenacao multi-agente",
                    "estimated_time": "60 min",
                }
            )
        elif track == "frontend":
            path.append(
                {
                    "step": 3,
                    "title": "Conheca o Drummond",
                    "topic": "specific_agent",
                    "agent": "drummond",
                    "description": "Interface conversacional e UX",
                    "estimated_time": "60 min",
                }
            )

        # Always include contribution guide
        path.append(
            {
                "step": 4,
                "title": "Guia de Contribuicao",
                "topic": "contribution_guide",
                "description": "Como construir junto - primeiro commit e PR",
                "estimated_time": "30 min",
            }
        )

        path.append(
            {
                "step": 5,
                "title": "Primeira Missao",
                "topic": "first_mission",
                "description": "Escolha e complete sua primeira missao de voo",
                "estimated_time": "2-4 horas",
            }
        )

        return path

    async def initialize(self) -> None:
        """Initialize the educator agent."""
        self.logger.info("Initializing Santos-Dumont educator agent...")
        self.logger.info("Santos-Dumont ready to teach! O ceu e o limite!")

    async def shutdown(self) -> None:
        """Shutdown the educator agent."""
        self.logger.info("Shutting down Santos-Dumont...")
        self.logger.info("Santos-Dumont shutdown complete. Ate o proximo voo!")


# Alias for consistency
SantosDumontAgent = EducatorAgent
