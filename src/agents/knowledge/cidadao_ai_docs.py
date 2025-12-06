"""
Cidadão.AI Technical Knowledge Base
====================================

Base de conhecimento técnico consolidada para o agente Santos-Dumont.
Contém documentação completa do backend e orientações para frontend.

Author: Anderson H. Silva
Date: 2025-12-06
"""

# =============================================================================
# CONHECIMENTO CONSOLIDADO DO CIDADÃO.AI
# =============================================================================

CIDADAO_AI_KNOWLEDGE = {
    # =========================================================================
    # VISÃO GERAL DO PROJETO
    # =========================================================================
    "projeto": {
        "nome": "Cidadão.AI",
        "descricao": "Plataforma multi-agente de IA para análise de transparência governamental brasileira",
        "autor": "Anderson Henrique da Silva",
        "instituicao": "Instituto Federal do Sul de Minas Gerais (IFSULDEMINAS)",
        "orientadora": "Professora Aracele Garcia de Oliveira Fassbinder",
        "tipo": "Trabalho de Conclusão de Curso (TCC)",
        "producao_url": "https://cidadao-api-production.up.railway.app/",
        "repositorio": "github.com/anderson-ufrj/cidadao.ai-backend",
    },
    # =========================================================================
    # ARQUITETURA DO SISTEMA
    # =========================================================================
    "arquitetura": {
        "visao_geral": """
O Cidadão.AI é uma plataforma multi-agente que usa 17 agentes de IA especializados
para analisar dados de transparência governamental brasileira.

FLUXO PRINCIPAL:
User Query → IntentClassifier → EntityExtractor → ExecutionPlanner
                                                        ↓
                                                DataFederationExecutor
                                                        ↓
                                                  EntityGraph (NetworkX)
                                                        ↓
                                            Investigation Agent(s)
                                                        ↓
                                                Consolidated Result
""",
        "stack_tecnologico": {
            "linguagem": "Python 3.11+",
            "framework_web": "FastAPI",
            "banco_dados": "PostgreSQL (SQLAlchemy async)",
            "cache": "Redis",
            "llm_primario": "Maritaca AI (sabia-3)",
            "llm_backup": "Anthropic Claude",
            "orquestracao_llm": "DSPy",
            "task_queue": "Celery",
            "monitoramento": "Prometheus + Grafana",
        },
        "numeros": {
            "agentes_total": 17,
            "agentes_operacionais": 16,
            "endpoints": "323+",
            "rotas": 39,
            "arquivos_teste": 149,
            "cobertura_testes": "76.29%",
            "total_testes": 1514,
        },
    },
    # =========================================================================
    # OS 17 AGENTES
    # =========================================================================
    "agentes": {
        "resumo": """
O sistema possui 17 agentes, sendo:
- 1 framework base (Deodoro) que define BaseAgent e ReflectiveAgent
- 16 agentes operacionais especializados

Todos herdam de src/agents/deodoro.py e seguem o mesmo padrão.
""",
        "lista": {
            "deodoro": {
                "nome_completo": "Marechal Deodoro da Fonseca",
                "tipo": "Base Framework",
                "descricao": "Framework base - define BaseAgent e ReflectiveAgent",
                "arquivo": "src/agents/deodoro.py",
                "classes": ["BaseAgent", "ReflectiveAgent"],
                "especificacoes": {
                    "quality_threshold": 0.8,
                    "max_iterations": 3,
                    "estados": [
                        "IDLE",
                        "THINKING",
                        "ACTING",
                        "WAITING",
                        "ERROR",
                        "COMPLETED",
                    ],
                },
            },
            "zumbi": {
                "nome_completo": "Zumbi dos Palmares",
                "tipo": "Investigator",
                "descricao": "Investigador - detecta anomalias e irregularidades",
                "arquivo": "src/agents/zumbi.py",
                "especialidade": "Detecção de anomalias em dados financeiros",
                "algoritmos": ["Z-Score", "IQR", "Isolation Forest", "LOF"],
                "emoji": "🔍",
            },
            "anita": {
                "nome_completo": "Anita Garibaldi",
                "tipo": "Analyst",
                "descricao": "Analista - analisa padrões e tendências estatísticas",
                "arquivo": "src/agents/anita.py",
                "especialidade": "Análise estatística e identificação de padrões",
                "emoji": "📊",
            },
            "tiradentes": {
                "nome_completo": "Joaquim José da Silva Xavier",
                "tipo": "Reporter",
                "descricao": "Relator - gera relatórios detalhados",
                "arquivo": "src/agents/tiradentes.py",
                "especialidade": "Documentação clara e acessível",
                "emoji": "📝",
            },
            "drummond": {
                "nome_completo": "Carlos Drummond de Andrade",
                "tipo": "Communicator",
                "descricao": "Comunicador - interface conversacional amigável",
                "arquivo": "src/agents/drummond.py",
                "especialidade": "Tradução de dados técnicos para linguagem cidadã",
                "emoji": "💬",
                "estilo": "Poético, reflexivo, com toques de humor mineiro",
            },
            "machado": {
                "nome_completo": "Joaquim Maria Machado de Assis",
                "tipo": "Text Analyst",
                "descricao": "Analista Textual - analisa documentos e contratos",
                "arquivo": "src/agents/machado.py",
                "especialidade": "Análise de documentos oficiais e contratos",
                "emoji": "📚",
            },
            "bonifacio": {
                "nome_completo": "José Bonifácio de Andrada e Silva",
                "tipo": "Legal",
                "descricao": "Especialista Legal - verifica conformidade com leis",
                "arquivo": "src/agents/bonifacio.py",
                "especialidade": "Análise de conformidade legal e normativa",
                "emoji": "⚖️",
            },
            "maria_quiteria": {
                "nome_completo": "Maria Quitéria de Jesus",
                "tipo": "Security",
                "descricao": "Auditora de Segurança - análise de vulnerabilidades",
                "arquivo": "src/agents/maria_quiteria.py",
                "especialidade": "Segurança da informação e proteção de dados",
                "emoji": "🛡️",
            },
            "oxossi": {
                "nome_completo": "Oxóssi",
                "tipo": "Data Hunter",
                "descricao": "Caçador de Dados - busca informações em múltiplas fontes",
                "arquivo": "src/agents/oxossi.py",
                "especialidade": "Busca e recuperação de dados governamentais",
                "emoji": "🏹",
            },
            "oscar_niemeyer": {
                "nome_completo": "Oscar Ribeiro de Almeida Niemeyer Soares Filho",
                "tipo": "Visualizer",
                "descricao": "Visualizador - cria gráficos e dashboards",
                "arquivo": "src/agents/oscar_niemeyer.py",
                "especialidade": "Agregação e visualização de dados",
                "emoji": "📐",
            },
            "dandara": {
                "nome_completo": "Dandara dos Palmares",
                "tipo": "Social Equity",
                "descricao": "Justiça Social - avalia equidade e inclusão",
                "arquivo": "src/agents/dandara.py",
                "especialidade": "Análise de equidade social e acessibilidade",
                "emoji": "✊",
            },
            "lampiao": {
                "nome_completo": "Virgulino Ferreira da Silva",
                "tipo": "Regional",
                "descricao": "Investigador Regional - foco em dados regionais",
                "arquivo": "src/agents/lampiao.py",
                "especialidade": "Análise de dados regionais, especialmente Nordeste",
                "emoji": "🌵",
            },
            "nana": {
                "nome_completo": "Nanã",
                "tipo": "Memory",
                "descricao": "Memória - gerencia contexto e histórico",
                "arquivo": "src/agents/nana.py",
                "especialidade": "Gestão de memória e contexto de investigações",
                "emoji": "🌙",
            },
            "ceuci": {
                "nome_completo": "Ceuci",
                "tipo": "Predictive/ETL",
                "descricao": "Preditivo - análises preditivas e ETL",
                "arquivo": "src/agents/ceuci.py",
                "especialidade": "Predições e processamento de dados",
                "emoji": "🔮",
            },
            "obaluaie": {
                "nome_completo": "Obaluaiê",
                "tipo": "Corruption Detection",
                "descricao": "Detector de Corrupção - identifica padrões suspeitos",
                "arquivo": "src/agents/obaluaie.py",
                "especialidade": "Detecção de padrões de corrupção",
                "emoji": "🔥",
            },
            "senna": {
                "nome_completo": "Ayrton Senna da Silva",
                "tipo": "Semantic Router",
                "descricao": "Roteador Semântico - direciona consultas rapidamente",
                "arquivo": "src/agents/ayrton_senna.py",
                "especialidade": "Roteamento inteligente de queries",
                "emoji": "🏎️",
            },
            "abaporu": {
                "nome_completo": "Abaporu",
                "tipo": "Master Orchestrator",
                "descricao": "Orquestrador Master - coordena investigações complexas",
                "arquivo": "src/agents/abaporu.py",
                "especialidade": "Coordenação multi-agente",
                "emoji": "🎨",
                "is_orchestrator": True,
            },
            "santos_dumont": {
                "nome_completo": "Alberto Santos-Dumont",
                "tipo": "Educator",
                "descricao": "Educador - ensina sobre o sistema Cidadão.AI",
                "arquivo": "src/agents/santos_dumont.py",
                "especialidade": "Onboarding e educação técnica",
                "emoji": "✈️",
            },
        },
    },
    # =========================================================================
    # ESTRUTURA DA API
    # =========================================================================
    "api": {
        "entry_point": "src/api/app.py",
        "nota_importante": "O arquivo app.py na raiz é APENAS para HuggingFace Spaces!",
        "rotas_principais": {
            "/api/v1/chat/": {
                "descricao": "Chat com agentes via SSE streaming",
                "metodos": ["POST /stream", "POST /investigate"],
                "uso": "Principal interface de conversação",
            },
            "/api/v1/agents/": {
                "descricao": "Acionamento direto de agentes",
                "metodos": ["GET /", "POST /{agent_id}/invoke"],
                "uso": "Chamar agentes programaticamente",
            },
            "/api/v1/investigations/": {
                "descricao": "Gestão de investigações",
                "metodos": ["GET /", "POST /", "GET /{id}", "DELETE /{id}"],
                "uso": "CRUD de investigações",
            },
            "/api/v1/federal/": {
                "descricao": "APIs federais integradas",
                "apis": ["IBGE", "DataSUS", "INEP", "PNCP", "TCU"],
                "uso": "Dados federais",
            },
            "/api/v1/transparency/": {
                "descricao": "Portal da Transparência",
                "nota": "78% dos endpoints retornam 403 (limitação conhecida)",
                "uso": "Dados do Portal da Transparência",
            },
            "/health/metrics": {
                "descricao": "Métricas Prometheus",
                "uso": "Monitoramento",
            },
        },
        "middleware_stack": [
            {
                "ordem": 1,
                "nome": "IPWhitelistMiddleware",
                "funcao": "Filtro de IP (produção)",
            },
            {"ordem": 2, "nome": "CORSMiddleware", "funcao": "Cross-origin requests"},
            {"ordem": 3, "nome": "LoggingMiddleware", "funcao": "Log de requisições"},
            {
                "ordem": 4,
                "nome": "SecurityMiddleware",
                "funcao": "CSRF, XSS protection",
            },
            {
                "ordem": 5,
                "nome": "RateLimitMiddleware",
                "funcao": "Limites por usuário/IP",
            },
            {"ordem": 6, "nome": "CompressionMiddleware", "funcao": "Gzip responses"},
            {
                "ordem": 7,
                "nome": "CorrelationMiddleware",
                "funcao": "Request ID tracing",
            },
            {"ordem": 8, "nome": "MetricsMiddleware", "funcao": "Prometheus metrics"},
        ],
        "sse_streaming": """
O chat usa Server-Sent Events para streaming em tempo real:

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

Eventos enviados:
- start: Início do processamento
- detecting: Análise de intent
- intent: Intent detectado
- agent_selected: Agente escolhido
- thinking: Agente processando
- chunk: Pedaço da resposta
- complete: Finalizado
""",
    },
    # =========================================================================
    # GUIA PARA FRONTEND
    # =========================================================================
    "frontend": {
        "integracao_chat": """
## Integração do Chat com SSE

O frontend deve consumir o endpoint de streaming:

```javascript
const eventSource = new EventSource('/api/v1/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: userMessage,
        session_id: sessionId,
        agent_id: 'drummond'  // opcional - se não enviar, auto-seleciona
    })
});

eventSource.addEventListener('chunk', (e) => {
    const data = JSON.parse(e.data);
    appendToChat(data.content);
});

eventSource.addEventListener('complete', (e) => {
    const data = JSON.parse(e.data);
    eventSource.close();
});

eventSource.onerror = (e) => {
    console.error('SSE Error:', e);
    eventSource.close();
};
```
""",
        "eventos_sse": {
            "start": "Início do processamento",
            "detecting": "Analisando mensagem",
            "intent": "Intent detectado (type, confidence)",
            "agent_selected": "Agente escolhido (agent_id, agent_name)",
            "thinking": "Agente está processando",
            "chunk": "Parte da resposta (content)",
            "complete": "Finalizado (agent_id, agent_name, suggested_actions)",
        },
        "selecao_agentes": """
## Seleção de Agentes

O frontend pode deixar o backend escolher automaticamente ou especificar:

1. **Auto-seleção** (recomendado para chat):
   - Não envie agent_id
   - O sistema detecta o intent e escolhe o agente apropriado

2. **Seleção explícita**:
   - Envie agent_id: "zumbi", "drummond", "anita", etc.
   - Útil para funcionalidades específicas

3. **Agentes principais por caso de uso**:
   - Chat geral: drummond
   - Investigação: zumbi
   - Análise: anita
   - Relatório: tiradentes
   - Educação: santos_dumont
""",
        "tratamento_erros": """
## Tratamento de Erros

```javascript
eventSource.onerror = (e) => {
    if (e.readyState === EventSource.CLOSED) {
        // Conexão fechada normalmente
    } else {
        // Erro de conexão - tente reconectar
        setTimeout(() => reconnect(), 3000);
    }
};
```

Códigos HTTP importantes:
- 200: Sucesso
- 400: Parâmetros inválidos
- 401: Não autenticado
- 403: Não autorizado
- 429: Rate limit excedido
- 500: Erro interno
""",
    },
    # =========================================================================
    # GUIA DE DESENVOLVIMENTO
    # =========================================================================
    "desenvolvimento": {
        "setup_ambiente": """
## Setup do Ambiente

```bash
# Clone e entre no projeto
git clone <repo>
cd cidadao.ai-backend

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\\Scripts\\activate  # Windows

# Instale dependências
make install-dev

# Configure variáveis
cp .env.example .env
# Edite .env com suas chaves
```
""",
        "variaveis_ambiente": {
            "obrigatorias": {
                "SECRET_KEY": "Chave secreta da aplicação",
                "JWT_SECRET_KEY": "Chave para tokens JWT",
            },
            "llm": {
                "LLM_PROVIDER": "maritaca ou anthropic",
                "MARITACA_API_KEY": "Chave da Maritaca AI (primário)",
                "MARITACA_MODEL": "sabia-3 ou sabiazinho-3",
                "ANTHROPIC_API_KEY": "Chave da Anthropic (backup)",
            },
            "opcionais": {
                "DATABASE_URL": "postgresql+asyncpg://... (default: SQLite)",
                "REDIS_URL": "redis://... (default: in-memory)",
                "TRANSPARENCY_API_KEY": "Chave do Portal da Transparência",
            },
        },
        "comandos_principais": {
            "make run-dev": "Iniciar servidor com hot reload",
            "make test": "Rodar todos os testes (COM prefixo!)",
            "make test-unit": "Apenas testes unitários",
            "make format": "Formatar código (black + isort)",
            "make check": "Verificar tudo antes do commit",
            "make lint": "Verificar linting (ruff)",
        },
        "testes": {
            "prefixo_obrigatorio": "JWT_SECRET_KEY=test SECRET_KEY=test",
            "exemplo_completo": "JWT_SECRET_KEY=test SECRET_KEY=test make test",
            "cobertura_minima": "80%",
            "estrutura": {
                "tests/unit/": "Testes unitários",
                "tests/integration/": "Testes de integração",
                "tests/multiagent/": "Testes multi-agente",
            },
        },
        "commits": {
            "idioma": "Inglês apenas",
            "formato": "<type>(scope): summary",
            "tipos": ["feat", "fix", "docs", "test", "refactor", "chore"],
            "exemplos": [
                "feat(agents): add fraud detection algorithm",
                "fix(api): resolve SSE streaming timeout",
                "test(zumbi): add integration tests",
            ],
            "proibido": [
                "Menções a IA/AI",
                "Generated by...",
                "Co-Authored-By: Claude",
            ],
        },
    },
    # =========================================================================
    # PADRÕES DE CÓDIGO
    # =========================================================================
    "padroes": {
        "criar_agente": """
## Como Criar um Novo Agente

1. Crie o arquivo: `src/agents/<nome>.py`

```python
from src.agents.deodoro import ReflectiveAgent, AgentMessage, AgentResponse, AgentContext
from src.core import get_logger

class MeuAgente(ReflectiveAgent):
    def __init__(self):
        super().__init__(
            name="meu_agente",
            description="O que este agente faz",
            capabilities=["cap1", "cap2"],
            quality_threshold=0.8,
            max_iterations=3
        )
        self.logger = get_logger(__name__)

    async def process(self, message: AgentMessage, context: AgentContext) -> AgentResponse:
        # Sua lógica aqui
        result = await self._minha_analise(message.content)

        return AgentResponse(
            agent_name=self.name,
            status="success",
            result=result,
            metadata={"confidence": 0.9}
        )
```

2. Registre em `src/agents/__init__.py`:
```python
"MeuAgente": "src.agents.meu_agente:MeuAgente"
```

3. Crie testes em `tests/unit/agents/test_meu_agente.py`

4. Documente em `docs/agents/meu_agente.md`
""",
        "async_await": """
## Async/Await

Todas as operações de I/O devem ser assíncronas:

```python
import httpx

async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```
""",
        "caching": """
## Multi-Layer Caching

```python
from src.services.cache_service import CacheService

cache = CacheService()

result = await cache.get_or_fetch(
    key="unique_key",
    fetch_function=expensive_operation,
    ttl=300  # segundos
)
```
""",
        "circuit_breaker": """
## Circuit Breaker para APIs Externas

```python
from src.services.orchestration.resilience.circuit_breaker import CircuitBreaker

circuit = CircuitBreaker(
    failure_threshold=3,
    timeout=60.0
)

result = await circuit.call(external_api_function)
```
""",
    },
    # =========================================================================
    # TROUBLESHOOTING
    # =========================================================================
    "troubleshooting": {
        "auth_error": {
            "sintoma": "Authorization header is missing",
            "causa": "Testes sem variáveis de ambiente",
            "solucao": "Use: JWT_SECRET_KEY=test SECRET_KEY=test pytest ...",
        },
        "imports_lentos": {
            "sintoma": "Demora para importar agentes",
            "causa": "Importação eager em vez de lazy",
            "solucao": "Use: from src.agents import ZumbiAgent (lazy loading)",
        },
        "porta_ocupada": {
            "sintoma": "Address already in use",
            "causa": "Outro processo na porta 8000",
            "solucao": "lsof -i :8000 ou use --port 8001",
        },
        "module_not_found": {
            "sintoma": "ModuleNotFoundError",
            "causa": "Ambiente virtual não ativado",
            "solucao": "source venv/bin/activate",
        },
        "llm_fallback": {
            "sintoma": "Respostas genéricas/fallback",
            "causa": "API key não configurada",
            "solucao": "Configure MARITACA_API_KEY ou ANTHROPIC_API_KEY no .env",
        },
    },
    # =========================================================================
    # ARQUIVOS IMPORTANTES
    # =========================================================================
    "arquivos_importantes": {
        "nao_modificar_sem_entender": [
            "src/agents/deodoro.py - Base de todos os agentes",
            "src/agents/__init__lazy.py - Lazy loading (367x performance)",
            "src/api/app.py - Aplicação principal com middlewares",
            "src/agents/simple_agent_pool.py - Gestão de ciclo de vida",
            "src/services/orchestration/orchestrator.py - Orquestração multi-agente",
            "pyproject.toml - Dependências e configurações",
        ],
        "documentacao": [
            "CLAUDE.md - Manual completo do projeto",
            "docs/agents/ - Documentação dos 17 agentes",
            "docs/architecture/ - Diagramas e arquitetura",
            "docs/api/ - Documentação da API",
        ],
    },
    # =========================================================================
    # PERFORMANCE
    # =========================================================================
    "performance": {
        "lazy_loading": {
            "antes": "1460.41ms para importar",
            "depois": "3.81ms para importar",
            "melhoria": "367x mais rápido",
            "arquivo": "src/agents/__init__lazy.py",
        },
        "metricas_alvo": {
            "api_response_p95": "<200ms",
            "agent_processing": "<5s",
            "chat_first_token": "<500ms",
            "investigation_6_agents": "<15s",
        },
    },
}


# =============================================================================
# FUNÇÕES DE ACESSO AO CONHECIMENTO
# =============================================================================


def get_agent_info(agent_name: str) -> dict | None:
    """Retorna informações sobre um agente específico."""
    agents = CIDADAO_AI_KNOWLEDGE["agentes"]["lista"]
    return agents.get(agent_name.lower())


def get_all_agents() -> dict:
    """Retorna todos os agentes."""
    return CIDADAO_AI_KNOWLEDGE["agentes"]["lista"]


def get_api_route_info(route: str) -> dict | None:
    """Retorna informações sobre uma rota da API."""
    routes = CIDADAO_AI_KNOWLEDGE["api"]["rotas_principais"]
    return routes.get(route)


def get_troubleshooting(problem: str) -> dict | None:
    """Retorna solução para um problema."""
    problems = CIDADAO_AI_KNOWLEDGE["troubleshooting"]
    return problems.get(problem)


def get_development_command(command: str) -> str | None:
    """Retorna descrição de um comando de desenvolvimento."""
    commands = CIDADAO_AI_KNOWLEDGE["desenvolvimento"]["comandos_principais"]
    return commands.get(command)


def search_knowledge(query: str) -> list[tuple[str, str, str]]:
    """
    Busca no conhecimento por uma query.

    Returns:
        Lista de tuplas (categoria, subcategoria, conteudo)
    """
    results = []
    query_lower = query.lower()

    def search_dict(d: dict, path: str = "") -> None:
        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, dict):
                search_dict(value, current_path)
            elif isinstance(value, str):
                if query_lower in value.lower() or query_lower in key.lower():
                    results.append((path, key, value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and query_lower in item.lower():
                        results.append((path, key, str(value)))
                        break

    search_dict(CIDADAO_AI_KNOWLEDGE)
    return results[:10]  # Limita a 10 resultados
