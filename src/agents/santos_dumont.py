"""
Module: agents.santos_dumont
Codinome: Alberto Santos-Dumont - Inventor e Educador do Sistema
Description: Agent specialized in teaching interns about the Cidadão.AI system
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
from src.agents.knowledge.cidadao_ai_docs import (
    CIDADAO_AI_KNOWLEDGE,
    format_links_for_display,
    get_useful_links,
)
from src.core import get_logger
from src.core.exceptions import AgentExecutionError

# Import DSPy service for intelligent responses
try:
    from src.services.dspy_agents import get_dspy_agent_service

    _dspy_service = get_dspy_agent_service()
    _DSPY_AVAILABLE = _dspy_service.is_available() if _dspy_service else False
except ImportError:
    _dspy_service = None
    _DSPY_AVAILABLE = False


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

    MISSÃO:
    Ensinar estagiários sobre a arquitetura, agentes e funcionamento do
    Cidadão.AI de forma prática e inovadora, seguindo o espírito pioneiro
    do Pai da Aviação.

    SOBRE SANTOS-DUMONT:
    - Nascido em Palmira (hoje Santos Dumont), Minas Gerais, em 1873
    - Inventor do 14-Bis, realizou o primeiro voo público homologado (1906)
    - Pioneiro que tornava públicas suas invenções para benefício de todos
    - Conhecido pela persistência e espírito colaborativo

    FILOSOFIA:
    - "O que eu fiz, qualquer um pode fazer" - democratização do conhecimento
    - Inovação com propósito social
    - Construir, testar, iterar, voar!

    CAPACIDADES EDUCACIONAIS:

    1. VISÃO GERAL DO SISTEMA:
       - Explicar a arquitetura multi-agente (17 agentes)
       - Mostrar o fluxo de orquestração
       - Apresentar as APIs de transparência

    2. ARQUITETURA DE AGENTES:
       - Como o BaseAgent/ReflectiveAgent funciona
       - Padrão de implementação de agentes
       - Ciclo de vida e estados
       - Lazy loading e performance

    3. AGENTES ESPECÍFICOS:
       - Capacidades de cada um dos 16 agentes operacionais
       - Quando usar cada agente
       - Exemplos práticos de uso

    4. ESTRUTURA DA API:
       - 323+ endpoints organizados em 39 rotas
       - Middleware stack e ordem de execução
       - Autenticação e segurança
       - SSE streaming para chat

    5. GUIA DE CONTRIBUIÇÃO:
       - Como fazer o primeiro commit
       - Padrão de testes (80% coverage)
       - Padrão de commits em inglês
       - Code review e PR workflow

    6. PADRÕES DE CÓDIGO:
       - Async/await everywhere
       - Multi-layer caching
       - Circuit breaker pattern
       - Error handling

    7. TROUBLESHOOTING:
       - Problemas comuns e soluções
       - Debug de agentes
       - Variáveis de ambiente

    INTEGRAÇÃO COM ACADEMY:
    - Sugere missões baseadas no nível do estagiário
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

        # Personality configuration - DIRETO E ASSERTIVO
        self.personality_prompt = """Você é Santos-Dumont, educador técnico do Cidadão.AI.

REGRAS:
1. Respostas CURTAS e DIRETAS (máximo 5-6 linhas por tópico)
2. Sem metáforas de aviação - vá direto ao ponto técnico
3. Use bullet points e código quando apropriado
4. Se não souber, diga "não sei" e sugira onde buscar

CONHECIMENTO COMPLETO:
Você tem acesso à base de conhecimento técnico completa do Cidadão.AI em CIDADAO_AI_KNOWLEDGE.
Use search_knowledge() para buscar informações específicas.
Use get_agent_info() para detalhes de agentes.

RESUMO DO SISTEMA (BACKEND):
- 17 agentes (16 operacionais + Deodoro base)
- FastAPI com 323+ endpoints em 39 rotas
- Stack: Python 3.11+, PostgreSQL, Redis
- Testes: JWT_SECRET_KEY=test SECRET_KEY=test pytest
- Entry point: src/api/app.py (NÃO app.py na raiz!)

INFRAESTRUTURA (IMPORTANTE!):
- Deploy: Railway (NÃO HuggingFace Spaces - foi migrado!)
- URL Produção: https://cidadao-api-production.up.railway.app/
- LLM Primário: Maritaca AI (Sabiá-3.1) - otimizado para PT-BR
- LLM Backup: Anthropic Claude (fallback automático)
- LLM Antigo: Groq (REMOVIDO em outubro 2025, não usamos mais!)
- Database: PostgreSQL + asyncpg (prod), SQLite in-memory (dev)
- Cache: Redis (prod), in-memory (dev)

FRONTEND (para referência):
- Framework: Next.js 15 (NÃO só React!)
- Deploy: Vercel
- Repo: https://github.com/anderson-ufrj/cidadao.ai-frontend
- Mentora: Lina Bo Bardi (para questões de frontend, redirecione para ela!)

TOM: Amigável mas técnico. Como um sênior explicando para júnior.
"""

        # Reference to full knowledge base
        self.knowledge_base = CIDADAO_AI_KNOWLEDGE

    def _load_system_knowledge(self) -> None:
        """Load knowledge base about the Cidadão.AI system."""
        self.system_knowledge = {
            "overview": {
                "name": "Cidadão.AI",
                "description": "Plataforma multi-agente de IA para análise de transparência governamental brasileira",
                "production_url": "https://cidadao-api-production.up.railway.app/",
                "agents_total": 17,
                "agents_operational": 16,
                "test_coverage": "76.29%",
                "total_tests": 1514,
                "endpoints": "323+",
            },
            "infrastructure": {
                "deployment": {
                    "platform": "Railway",
                    "url": "https://cidadao-api-production.up.railway.app/",
                    "uptime": "99.9%",
                    "since": "October 7, 2025",
                    "note": "Previously HuggingFace Spaces (deprecated)",
                },
                "llm": {
                    "primary": "Maritaca AI (Sabiá-3.1)",
                    "primary_key": "MARITACA_API_KEY",
                    "backup": "Anthropic Claude (claude-sonnet-4)",
                    "backup_key": "ANTHROPIC_API_KEY",
                    "note": "Maritaca is optimized for Brazilian Portuguese",
                    "deprecated": "Groq (removed October 2025)",
                },
                "database": {
                    "primary": "PostgreSQL + asyncpg",
                    "fallback": "SQLite in-memory (dev)",
                },
                "cache": {
                    "primary": "Redis",
                    "fallback": "In-memory cache",
                },
                "backend_stack": {
                    "framework": "FastAPI",
                    "python": "3.11+",
                    "orm": "SQLAlchemy 2.0",
                    "migrations": "Alembic",
                    "async": "asyncio + httpx",
                    "testing": "pytest + pytest-asyncio",
                },
                "frontend": {
                    "name": "Ágora",
                    "framework": "Next.js 15",
                    "repository": "https://github.com/anderson-ufrj/cidadao.ai-frontend",
                    "deployment": "Vercel",
                    "mentor": "bo_bardi",
                    "note": "Para questões de frontend, consulte a Bo Bardi!",
                },
                "agora": {
                    "name": "Ágora",
                    "description": "Frontend do Cidadão.AI - referência à ágora ateniense (democracia) e telemetria (métricas em tempo real)",
                    "features": [
                        "Chat com agentes",
                        "Métricas em tempo real",
                        "XP e gamificação",
                        "Missões",
                        "Badges",
                    ],
                    "status": "Em produção",
                },
            },
            "agents": {
                "deodoro": {
                    "type": "Base Framework",
                    "description": "Marechal Deodoro - Base de todos os agentes",
                    "classes": ["BaseAgent", "ReflectiveAgent"],
                    "features": [
                        "Quality threshold 0.8",
                        "Max 3 reflection iterations",
                        "Staté management",
                    ],
                    "file": "src/agents/deodoro.py",
                },
                "zumbi": {
                    "type": "Investigator",
                    "description": "Zumbi dos Palmares - Investigador de anomalias",
                    "specialty": "Detecção de anomalias em dados financeiros",
                    "algorithms": ["Z-Score", "IQR", "Isolation Forest", "LOF"],
                    "file": "src/agents/zumbi.py",
                },
                "anita": {
                    "type": "Analyst",
                    "description": "Anita Garibaldi - Analista de padrões",
                    "specialty": "Análise estatística e identificação de padrões",
                    "file": "src/agents/anita.py",
                },
                "tiradentes": {
                    "type": "Reporter",
                    "description": "Tiradentes - Gerador de relatórios",
                    "specialty": "Documentação e comúnicação clara",
                    "file": "src/agents/tiradentes.py",
                },
                "drummond": {
                    "type": "Commúnicator",
                    "description": "Carlos Drummond de Andrade - Comúnicador do povo",
                    "specialty": "Interface conversacional e tradução de dados técnicos",
                    "file": "src/agents/drummond.py",
                },
                "ayrton_senna": {
                    "type": "Semantic Router",
                    "description": "Ayrton Senna - Roteador semântico",
                    "specialty": "Roteamento inteligente de queries para agentes",
                    "file": "src/agents/ayrton_senna.py",
                },
                "bonifacio": {
                    "type": "Legal Analyst",
                    "description": "José Bonifácio - Analista jurídico",
                    "specialty": "Análise de conformidade legal e normativa",
                    "file": "src/agents/bonifacio.py",
                },
                "maria_quiteria": {
                    "type": "Security",
                    "description": "Maria Quitéria - Guardiã da segurança",
                    "specialty": "Supervisão e segurança do sistema",
                    "file": "src/agents/maria_quiteria.py",
                },
                "machado": {
                    "type": "Textual Analysis",
                    "description": "Machado de Assis - Analista textual",
                    "specialty": "Análise de documentos e textos",
                    "file": "src/agents/machado.py",
                },
                "oxossi": {
                    "type": "Data Hunter",
                    "description": "Oxóssi - Caçador de dados",
                    "specialty": "Busca e recuperação de dados",
                    "file": "src/agents/oxossi.py",
                },
                "lampiao": {
                    "type": "Regional",
                    "description": "Lampião - Especialista regional",
                    "specialty": "Análise de dados regionais e locais",
                    "file": "src/agents/lampiao.py",
                },
                "oscar_niemeyer": {
                    "type": "Aggregator",
                    "description": "Oscar Niemeyer - Agregador de dados",
                    "specialty": "Agregação e visualização de dados",
                    "file": "src/agents/oscar_niemeyer.py",
                },
                "abaporu": {
                    "type": "Master Orchestrator",
                    "description": "Abaporu - Orquestrador mestre",
                    "specialty": "Coordenação de investigações multi-agente",
                    "file": "src/agents/abaporu.py",
                },
                "nana": {
                    "type": "Memory",
                    "description": "Nanã - Guardiã da memória",
                    "specialty": "Gestão de contexto e memória",
                    "file": "src/agents/nana.py",
                },
                "ceuci": {
                    "type": "Predictive/ETL",
                    "description": "Ceuci - Agente preditivo",
                    "specialty": "Predições e processamento ETL",
                    "file": "src/agents/ceuci.py",
                },
                "obaluaie": {
                    "type": "Corruption Detection",
                    "description": "Obaluaiê - Detector de corrupção",
                    "specialty": "Detecção de padrões de corrupção",
                    "file": "src/agents/obaluaie.py",
                },
                "dandara": {
                    "type": "Social Equity",
                    "description": "Dandara - Analista de equidade",
                    "specialty": "Análise de equidade social e acessibilidade",
                    "file": "src/agents/dandara.py",
                },
                "santos_dumont": {
                    "type": "Educator (Backend)",
                    "description": "Santos-Dumont - Educador do Sistema Backend",
                    "specialty": "Ensino sobre arquitetura, agentes e backend do Cidadão.AI",
                    "file": "src/agents/santos_dumont.py",
                },
                "bo_bardi": {
                    "type": "Educator (Frontend)",
                    "description": "Lina Bo Bardi - Especialista Frontend",
                    "specialty": "Ensino sobre integração frontend, SSE, componentes React/Next.js",
                    "file": "src/agents/bo_bardi.py",
                    "note": "Para questões de frontend, consulte ela!",
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
                "commit_language": "Inglês apenas",
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

            # Handle chat messages from the main chat endpoint
            if action == "process_chat":
                # Extract the user's message from payload
                user_message = payload.get("message", "")
                if not user_message:
                    user_message = payload.get("query", payload.get("content", ""))

                # Process as a question using our knowledge base
                response = await self._answer_question(user_message)

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "message": response["content"],
                        "metadata": response.get("metadata", {}),
                    },
                    metadata={"educator": True, "type": "chat"},
                )

            elif action == "teach":
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
        """Generaté educational content based on topic."""

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
        """Teach about the Cidadão.AI system overview."""
        overview = self.system_knowledge["overview"]

        content = f"""## Cidadão.AI - Visão Geral

{overview["description"]}

**Produção:** {overview["production_url"]}

### Números do Projeto
- **{overview["agents_total"]} agentes** ({overview["agents_operational"]} operacionais + 1 base)
- **{overview["endpoints"]} endpoints** na API
- **{overview["test_coverage"]}** cobertura de testes
- **{overview["total_tests"]} testes** automatizados

### Principais Agentes
| Agente | Função |
|--------|--------|
| Zumbi | Investigador de anomalias |
| Anita | Analista estatística |
| Tiradentes | Gerador de relatórios |
| Drummond | Interface conversacional |
| Abaporu | Orquestrador master |

### Próximos Passos
1. `agent_architecture` - como os agentes funcionam
2. `contribution_guide` - como contribuir
3. `specific_agent` - conhecer um agente específico

O que você quer saber?"""

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
- **Quality Threshold**: {arch["base_agent"]["quality_threshold"]} (calibragem mínima)
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
        # Sua lógica aqui - como o motor do avião
        result = await self._minha_análise(message.content)

        return AgentResponse(
            agent_name=self.name,
            status="success",
            result=result,
            metadata={{"confidence": 0.9}}
        )
```

## Lazy Loading - Otimizacao de Performance

Como reduzi o peso dos meus balões para voar mais alto:
- **Antes**: {arch["lazy_loading"]["before"]} para importar
- **Depois**: {arch["lazy_loading"]["after"]} (367x mais leve!)

Arquivo: `{arch["lazy_loading"]["file"]}`

## Sistema de Reflexao

Os agentes reflexivos sao como pilotos experientes:
1. Executam a manobra
2. Avaliam o resultado
3. Se < 0.8 de qualidade, ajustam e tentam de novo
4. Maximo de 3 tentativas

"Inventar e imaginar o que a humanidade ainda não pensou!"
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

Assim como eu trabalhava em meu hangar em Neuilly, você precisa
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
- Evita acidentes com produção
- Protege dados sensíveis

## Registro de Voo (Commits)

Commits em inglês, formato padrão:

```
{contrib["commit_format"]}
```

Tipos válidos: {", ".join(contrib["commit_types"])}

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
7. Solicite autorização (PR no GitHub)

## Checagem Pre-Voo

Antes de cada commit:
```bash
{commands["check"]}
```

Isso verifica: formatação, lint, tipos e testes.

"A persistência e o caminho do êxito!" - Não desista nos primeiros testes!
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
Meu caro, não encontrei o agente "{agent_name}" no hangar.

Agentes disponíveis: {available}

Qual deles você gostaria de conhecer?
            """
            return {
                "content": content.strip(),
                "metadata": {"error": "agent_not_found"},
            }

        agent = agents[agent_name]

        content = f"""
## {agent["description"]}

**Função**: {agent["type"]}
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

O arquivo está em `{agent["file"]}`. Recomendo estudar
para entender os padrões de construção.

"Voar e muito mais que um sonho - e uma ciência!"
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

Meu caro amigo, hoje você começa sua jornada como aviador do Cidadao.AI!
Assim como preparei cada detalhe antes do voo do 14-Bis, vamos preparar tudo.

### Checklist Pre-Voo

1. [ ] Clone o repositório (baixe os projetos)
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

### Sua Primeira Missão

Sugiro começar com voos curtos:
- Adicionar um teste para um agente existente
- Melhorar a documentação de uma função
- Corrigir um pequeno bug

### Precisa de Suporte?

Estou aqui no torre de controle! Pergunte sobre:
- Qualquer agente específico
- Como funciona alguma parte do sistema
- Problemas que encontrar

"O segredo e voar! Não importa como!"

Vamos construir o futuro juntos!
        """

        checklist = [
            "Clone o repositório",
            "Configure ambiente virtual",
            "Instale dependências",
            "Configure .env",
            "Rode os testes",
            "Rode o servidor local",
            "Acesse a documentação",
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
## Sua Primeira Missão de Voo

Vamos escolher uma missão adequada ao seu nível de experiência...

### Missoes para Novos Pilotos

1. **Adicionar Teste Unitario** (Easy - 10 XP)
   - Escolha um agente com baixa cobertura
   - Adicione testes para um método específico
   - Arquivo: `tests/unit/agents/test_<agent>.py`

2. **Documentar Função** (Easy - 10 XP)
   - Encontre uma função sem documentação
   - Adicione docstring clara
   - Siga o padrão Google docstrings

3. **Corrigir Typo** (Easy - 5 XP)
   - Encontre erros de digitação
   - Corrijá em código ou documentação

### Missoes para Pilotos Intermediarios

4. **Implementar Método de Agente** (Medium - 25 XP)
   - Adicione nova capacidade a um agente
   - Inclua testes
   - Minimo 80% cobertura

5. **Adicionar Endpoint** (Medium - 25 XP)
   - Crie novo endpoint na API
   - Inclua testes de integração
   - Documente no OpenAPI

### Procedimento de Voo

1. Escolha uma missão
2. Crie uma pista: `git checkout -b feat/minha-missão`
3. Construa com testes
4. Verificacao pre-voo: `make check`
5. Solicite autorização (PR)

### Dica do Inventor

Comece pelo Zumbi (`src/agents/zumbi.py`) - e o agente mais
bem documentado e serve como referência de projeto.

"Nunca desisti de um projeto - a persistência e o motor do sucesso!"

Qual missão você escolhe?
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

Assim como testava meus balões antes de voar, todo código precisa de testes!

### Regra de Ouro

**SEMPRE** use as configurações de teste:
```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest ...
```

### Organização dos Testes

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

# Testes unitários
JWT_SECRET_KEY=test SECRET_KEY=test make test-unit

# Teste específico
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_zumbi.py -v

# Com medição de cobertura
JWT_SECRET_KEY=test SECRET_KEY=test pytest --cov=src --cov-report=html
```

### Meta de Qualidade

**80% de cobertura** mínima para código novo.
Verifique o relatório em `htmlcov/index.html`.

"Um avião sem testes e um pássaro sem asas - pode até pular, mas não voa!"
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

- `/api/v1/chat/` - Comúnicacao com agentes (SSE streaming)
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

### SSE Streaming - Comúnicacao em Tempo Real

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
## Manutenção e Reparos

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

# Reativar se necessário
source venv/bin/activate
```

### 5. Problemas de Banco

**Sintoma**: Erros de conexão

**Reparo**: O sistema usa SQLite in-memory por padrão.
Para PostgreSQL, configure `DATABASE_URL` no `.env`.

### 6. LLM Provider

**Sintoma**: Respostas genéricas/fallback

**Reparo**: Configure `MARITACA_API_KEY` ou `ANTHROPIC_API_KEY` no `.env`.

### Ainda com Problemas?

1. Verifique o `.env`
2. Rode `make clean && make install-dev`
3. Consulte `CLAUDE.md`
4. Pergunte aqui na torre de controle!

"Todo problema tem solução - basta persistir!"
        """

        return {
            "content": content.strip(),
            "metadata": {"topic": "troubleshooting"},
            "suggested_next": ["first_steps", "contribution_guide"],
        }

    async def _provide_links(self, category: str | None = None) -> dict[str, Any]:
        """Provide useful links to the user."""
        links = get_useful_links(category)

        if category == "documentacao" or category == "docs":
            content = """## Documentação do Cidadão.AI

### Documentação da API (Swagger/OpenAPI)
- **Produção**: https://cidadao-api-production.up.railway.app/docs
- **ReDoc**: https://cidadao-api-production.up.railway.app/redoc
- **Local**: http://localhost:8000/docs

### Repositório GitHub
- **Backend**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: https://github.com/anderson-ufrj/cidadao.ai-backend/issues

### Documentação Interna (no repositório)
- **Manual completo**: `CLAUDE.md` (na raiz)
- **Agentes**: `docs/agents/`
- **Arquitetura**: `docs/architecture/`
- **API**: `docs/api/`
"""
        elif category == "api" or category == "producao":
            content = """## API em Produção

- **URL Base**: https://cidadao-api-production.up.railway.app/
- **Swagger UI**: https://cidadao-api-production.up.railway.app/docs
- **ReDoc**: https://cidadao-api-production.up.railway.app/redoc
- **Health Check**: https://cidadao-api-production.up.railway.app/health
- **Métricas**: https://cidadao-api-production.up.railway.app/health/metrics
"""
        elif category == "github" or category == "repositorio":
            content = """## Repositório GitHub

- **Código**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: https://github.com/anderson-ufrj/cidadao.ai-backend/issues
- **Pull Requests**: https://github.com/anderson-ufrj/cidadao.ai-backend/pulls
"""
        else:
            content = format_links_for_display()

        return {
            "content": content.strip(),
            "metadata": {"type": "links", "category": category},
            "links": links,
        }

    async def _answer_question(self, question: str) -> dict[str, Any]:
        """Answer a general question about the system."""
        question_lower = question.lower()

        # Detect link requests
        link_keywords = [
            "link",
            "url",
            "endereço",
            "acesso",
            "acessar",
            "documentação",
            "documentacao",
            "docs",
            "swagger",
            "github",
            "repositório",
            "repositorio",
            "repo",
        ]
        if any(keyword in question_lower for keyword in link_keywords):
            # Determine category
            if "doc" in question_lower or "swagger" in question_lower:
                return await self._provide_links("documentacao")
            elif "github" in question_lower or "repo" in question_lower:
                return await self._provide_links("github")
            elif (
                "api" in question_lower
                or "producao" in question_lower
                or "produção" in question_lower
            ):
                return await self._provide_links("api")
            else:
                return await self._provide_links()

        # Frontend questions - redirect to Bo Bardi
        frontend_keywords = [
            "frontend",
            "front-end",
            "react",
            "nextjs",
            "next.js",
            "next js",
            "componente",
            "css",
            "tailwind",
            "zustand",
            "vercel",
            "interface",
            "ui",
            "ux",
        ]
        if any(kw in question_lower for kw in frontend_keywords):
            bo_bardi = self.system_knowledge["agents"].get("bo_bardi", {})
            return {
                "content": f"""## Questão de Frontend!

Meu caro, essa é uma pergunta sobre **frontend** - a especialidade da **Lina Bo Bardi**!

### Sobre a Bo Bardi
- **{bo_bardi.get("description", "Especialista Frontend")}**
- **Especialidade**: {bo_bardi.get("specialty", "Frontend e integração")}
- **Arquivo**: `{bo_bardi.get("file", "src/agents/bo_bardi.py")}`

### O que ela pode te ensinar:
- Integração SSE com o chat (`/api/v1/chat/stream`)
- Estrutura de componentes Next.js 15 com App Router
- State management com Zustand
- Estilização com Tailwind CSS
- Acessibilidade (WCAG AAA)

### Frontend Stack (para referência):
- **Framework**: Next.js 15 (App Router)
- **State**: Zustand
- **Styling**: Tailwind CSS
- **Deploy**: Vercel
- **Repositório**: https://github.com/anderson-ufrj/cidadao.ai-frontend

**Recomendo**: Fale com a Bo Bardi para detalhes de frontend!
Eu sou especialista em **backend** - arquitetura, agentes, API, infraestrutura.
""".strip(),
                "metadata": {"type": "redirect", "redirect_to": "bo_bardi"},
            }

        if "quantos agentes" in question_lower or "how many agents" in question_lower:
            return {
                "content": """
Temos **17 agentes** no total:
- 16 agentes operacionais (cada um com especialidade única)
- 1 framework base (Deodoro)

Os principais: Zumbi (investigador), Anita (analista), Tiradentes (relatórios),
Drummond (comúnicacao), Abaporu (orquestrador).

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

        elif "primeiro" in question_lower or "começar" in question_lower:
            return await self._guide_first_steps()

        # LLM/AI Model questions
        elif any(
            kw in question_lower
            for kw in ["llm", "maritaca", "groq", "anthropic", "claude", "modelo", "ia"]
        ):
            infra = self.system_knowledge["infrastructure"]
            llm = infra["llm"]
            return {
                "content": f"""## LLM do Cidadão.AI

### Provedor Primário
- **{llm["primary"]}**
- Variável: `{llm["primary_key"]}`
- {llm["note"]}

### Backup (Fallback Automático)
- **{llm["backup"]}**
- Variável: `{llm["backup_key"]}`
- Usado quando Maritaca falha ou não está configurado

### Histórico
- ❌ **{llm["deprecated"]}** - não usamos mais!
- ✅ Maritaca é o atual primário

### Configuração
```bash
# .env
LLM_PROVIDER=maritaca
MARITACA_API_KEY=sua-chave
MARITACA_MODEL=sabia-3.1  # ou sabiazinho-3 (mais rápido)

# Backup (opcional)
ANTHROPIC_API_KEY=sua-chave-backup
```
""".strip(),
                "metadata": {"type": "infrastructure", "topic": "llm"},
            }

        # Deployment/Platform questions
        elif any(
            kw in question_lower
            for kw in [
                "deploy",
                "railway",
                "huggingface",
                "hugging",
                "hospedado",
                "produção",
                "producao",
                "servidor",
                "hosting",
            ]
        ):
            infra = self.system_knowledge["infrastructure"]
            deploy = infra["deployment"]
            return {
                "content": f"""## Deploy do Backend

### Plataforma Atual
- **{deploy["platform"]}** (desde {deploy["since"]})
- URL: {deploy["url"]}
- Uptime: {deploy["uptime"]}

### Histórico
- ⚠️ {deploy["note"]}
- A migração para Railway trouxe melhor performance e confiabilidade

### URLs de Produção
- **API**: {deploy["url"]}
- **Docs**: {deploy["url"]}docs
- **Health**: {deploy["url"]}health
- **Metrics**: {deploy["url"]}health/metrics
""".strip(),
                "metadata": {"type": "infrastructure", "topic": "deployment"},
            }

        # Backend Stack questions
        elif any(
            kw in question_lower
            for kw in ["stack", "fastapi", "framework", "tecnologia", "banco", "redis"]
        ):
            infra = self.system_knowledge["infrastructure"]
            stack = infra["backend_stack"]
            db = infra["database"]
            cache = infra["cache"]
            return {
                "content": f"""## Stack do Backend

### Framework
- **{stack["framework"]}** com Python {stack["python"]}
- ORM: {stack["orm"]}
- Migrations: {stack["migrations"]}
- Async: {stack["async"]}
- Testes: {stack["testing"]}

### Banco de Dados
- **Produção**: {db["primary"]}
- **Desenvolvimento**: {db["fallback"]}

### Cache
- **Produção**: {cache["primary"]}
- **Fallback**: {cache["fallback"]}

### Entry Point
- `src/api/app.py` (NÃO `app.py` na raiz!)
""".strip(),
                "metadata": {"type": "infrastructure", "topic": "stack"},
            }

        else:
            # Use LLM for dynamic response if available
            if _DSPY_AVAILABLE and _dspy_service:
                try:
                    # Build context from knowledge base
                    context = """
Conhecimento técnico disponível:
- 17 agentes de IA com identidades culturais brasileiras
- FastAPI com 323+ endpoints, Python 3.11+, PostgreSQL, Redis
- Testes: JWT_SECRET_KEY=test SECRET_KEY=test pytest
- Entry point: src/api/app.py
- Deploy: Railway (https://cidadao-api-production.up.railway.app/)
- LLM: Maritaca AI (Sabiá-3.1) primário, Anthropic backup
"""
                    result = await _dspy_service.chat(
                        agent_id="santos_dumont",
                        message=question,
                        intent_type="question",
                        context=context,
                    )
                    if result.get("success"):
                        return {
                            "content": result.get("response", ""),
                            "metadata": {"type": "llm_response", "dspy_enabled": True},
                        }
                except Exception as e:
                    self.logger.warning(f"DSPy chat failed, using fallback: {e}")

            # Fallback response
            return {
                "content": f"""
Excelente pergunta, meu caro! "{question}"

Para ajuda-lo melhor, posso falar sobre:

1. **Visão geral do sistema** - O que e o Cidadao.AI
2. **Arquitetura de agentes** - A engenharia dos 17 agentes
3. **Um agente específico** - Zumbi, Drummond, Abaporu...
4. **Como contribuir** - Construir junto conosco
5. **Testes** - Procedimentos de qualidade
6. **Links úteis** - URLs da API, GitHub e documentação
7. **Problemas comuns** - Manutenção e reparos

Qual tema te interessa?

"A curiosidade e o primeiro passo para a invenção!"
                """.strip(),
                "metadata": {"type": "fallback_response"},
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
                "title": "Visão Geral do Sistema",
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
                    "description": "O agente referência - melhor projeto para estudar",
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
                "title": "Guia de Contribuição",
                "topic": "contribution_guide",
                "description": "Como construir junto - primeiro commit e PR",
                "estimated_time": "30 min",
            }
        )

        path.append(
            {
                "step": 5,
                "title": "Primeira Missão",
                "topic": "first_mission",
                "description": "Escolha e complete sua primeira missão de voo",
                "estimated_time": "2-4 horas",
            }
        )

        return path

    async def initialize(self) -> None:
        """Initialize the educator agent."""
        self.logger.info("Initializing Santos-Dumont educator agent...")
        self.logger.info("Santos-Dumont ready to teach! O céu e o limite!")

    async def shutdown(self) -> None:
        """Shutdown the educator agent."""
        self.logger.info("Shutting down Santos-Dumont...")
        self.logger.info("Santos-Dumont shutdown complete. Até o próximo voo!")


# Alias for consistency
SantosDumontAgent = EducatorAgent
