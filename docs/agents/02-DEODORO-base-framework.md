---
title: "Deodoro da Fonseca - Base Agent Architecture"
sidebar_position: 1
description: "Fundador da arquitetura multi-agente - classe base para todos os agentes"
---

# 🏛️ Deodoro da Fonseca - Base Agent Architecture

**Autor**: Anderson Henrique da Silva
**Data**: 12 de outubro de 2025

:::tip **Status: ✅ 100% Operacional**
Implementado em `src/agents/deodoro.py` (464 linhas) com **arquitetura sólida e production-ready**.
Base para todos os 17 agentes do sistema. Testado e validado em produção.
:::

## 📋 Visão Geral

**Deodoro da Fonseca** é a fundação da arquitetura multi-agente do Cidadão.AI. Como Marechal Deodoro proclamou a República e estabeleceu novas estruturas, esta classe estabelece os padrões arquiteturais que todos os agentes seguem.

### Identidade Cultural
Marechal Deodoro da Fonseca (1827-1892) foi o fundador e primeiro presidente da República Brasileira. Representa perfeitamente a missão desta classe: estabelecer fundações sólidas e estruturas duradouras.

## 🎯 Responsabilidades

### 1. **Classe Base Abstrata (BaseAgent)**
```python
class BaseAgent(ABC):
    """
    Classe abstrata para todos os agentes do sistema.

    Funcionalidades:
    - Gerenciamento de estado (IDLE, THINKING, ACTING, ERROR, COMPLETED)
    - Retry logic com exponential backoff
    - Histórico de mensagens e respostas
    - Integração com Prometheus metrics
    - Logging estruturado
    - Lifecycle management (initialize, shutdown)
    """
```

### 2. **Agente Reflexivo (ReflectiveAgent)**
```python
class ReflectiveAgent(BaseAgent):
    """
    Extensão com capacidade de auto-reflexão.

    Funcionalidades adicionais:
    - Loop de reflexão para melhoria iterativa
    - Quality threshold (padrão: 0.7)
    - Máximo de iterações (padrão: 3)
    - Metadata de reflexão em responses
    """
```

### 3. **Data Classes**
```python
@dataclass
class AgentContext:
    """
    Contexto compartilhado entre agentes.

    Campos:
    - investigation_id: UUID único da investigação
    - user_id: ID do usuário solicitante
    - session_id: ID da sessão
    - timestamp: Quando foi criado
    - metadata: Dados adicionais
    - memory_context: Contexto da memória (Nanã)
    - parent_agent: Agente pai (para coordenação)
    - trace_id: Para distributed tracing
    """

class AgentMessage(BaseModel):
    """
    Mensagem entre agentes (Pydantic).

    Campos:
    - sender: Quem enviou
    - recipient: Quem deve receber
    - action: Ação a executar
    - payload: Dados da mensagem
    - context: Contexto adicional
    - message_id: UUID único
    - requires_response: Se espera resposta
    """

class AgentResponse(BaseModel):
    """
    Resposta de um agente (Pydantic).

    Campos:
    - agent_name: Nome do agente
    - status: Status da execução
    - result: Resultado da ação
    - error: Mensagem de erro (se houver)
    - metadata: Metadados adicionais
    - processing_time_ms: Tempo de processamento
    """
```

## 💻 Como Criar um Novo Agente

### Exemplo 1: Agente Simples (Herdar de BaseAgent)
```python
from src.agents.deodoro import BaseAgent, AgentContext, AgentMessage, AgentResponse
from src.core import AgentStatus

class MeuNovoAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="meu_novo_agent",
            description="Descrição do que ele faz",
            capabilities=[
                "capability_1",
                "capability_2",
                "capability_3"
            ],
            max_retries=3,  # Opcional: tentativas em caso de erro
            timeout=60      # Opcional: timeout em segundos
        )

        # Adicionar atributos específicos
        self.custom_config = {...}

    async def initialize(self) -> None:
        """Inicializar recursos (conexões, modelos, etc)."""
        self.logger.info(f"Initializing {self.name}...")

        # Carregar modelos, conectar banco de dados, etc
        # await self._load_models()

        self.logger.info(f"{self.name} ready!")

    async def shutdown(self) -> None:
        """Limpar recursos."""
        self.logger.info(f"Shutting down {self.name}...")

        # Fechar conexões, liberar memória, etc
        # await self._close_connections()

    async def process(
        self,
        message: AgentMessage,
        context: AgentContext
    ) -> AgentResponse:
        """
        Processar mensagem e retornar resposta.

        Este método é chamado pelo framework.
        """
        try:
            self.logger.info(
                "Processing message",
                action=message.action,
                investigation_id=context.investigation_id
            )

            # Extrair dados da mensagem
            action = message.action
            payload = message.payload

            # Executar lógica específica baseada na action
            if action == "analyze":
                result = await self._analyze(payload, context)
            elif action == "report":
                result = await self._report(payload, context)
            else:
                raise ValueError(f"Unknown action: {action}")

            # Retornar resposta de sucesso
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={
                    "action": action,
                    "records_processed": len(payload.get("data", []))
                }
            )

        except Exception as e:
            self.logger.error(
                "Processing failed",
                error=str(e),
                exc_info=True
            )

            # Retornar resposta de erro
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                metadata={"action": message.action}
            )

    async def _analyze(self, payload: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Lógica específica de análise."""
        # Implementar análise
        return {"analysis_result": "..."}

    async def _report(self, payload: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Lógica específica de relatório."""
        # Implementar relatório
        return {"report": "..."}
```

### Exemplo 2: Agente Reflexivo (Herdar de ReflectiveAgent)
```python
from src.agents.deodoro import ReflectiveAgent, AgentContext, AgentMessage, AgentResponse

class MeuAgenteReflexivo(ReflectiveAgent):
    def __init__(self):
        super().__init__(
            name="meu_agente_reflexivo",
            description="Agente com capacidade de auto-melhoria",
            capabilities=["analyze", "improve"],
            reflection_threshold=0.8,    # Qualidade mínima: 80%
            max_reflection_loops=3,      # Máximo 3 iterações
        )

    async def initialize(self) -> None:
        """Inicializar recursos."""
        self.logger.info(f"Initializing reflective agent {self.name}...")

    async def shutdown(self) -> None:
        """Limpar recursos."""
        self.logger.info(f"Shutting down {self.name}...")

    async def process(
        self,
        message: AgentMessage,
        context: AgentContext
    ) -> AgentResponse:
        """Processar mensagem."""

        # Sua lógica aqui
        result = await self._do_analysis(message.payload)

        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            result=result,
            metadata={"quality_score": result.get("quality", 0.0)}
        )

    async def reflect(
        self,
        result: Any,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Refletir sobre o resultado e avaliar qualidade.

        Retornar:
            {
                "quality_score": 0.0-1.0,
                "improvements": ["sugestão 1", "sugestão 2"],
                "issues": ["problema 1"],
                "should_retry": bool
            }
        """
        # Avaliar qualidade do resultado
        quality_score = self._calculate_quality(result)

        if quality_score < self.reflection_threshold:
            return {
                "quality_score": quality_score,
                "improvements": [
                    "Adicionar mais evidências",
                    "Melhorar análise estatística"
                ],
                "issues": ["Confiança abaixo do threshold"],
                "should_retry": True
            }
        else:
            return {
                "quality_score": quality_score,
                "improvements": [],
                "issues": [],
                "should_retry": False
            }

    def _calculate_quality(self, result: Any) -> float:
        """Calcular score de qualidade (0.0-1.0)."""
        # Implementar lógica de avaliação
        return 0.85

    async def _do_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executar análise."""
        return {"data": "...", "quality": 0.85}
```

## 🔧 Funcionalidades Herdadas

### Retry Logic com Exponential Backoff
```python
# Automático em BaseAgent.execute()
# - max_retries: 3 (padrão)
# - Backoff: 2^retry segundos (2s, 4s, 8s)
# - Logging automático de tentativas
# - Métricas Prometheus integradas

response = await agent.execute(
    action="analyze",
    payload={"data": [...]},
    context=context
)
```

### Gerenciamento de Estado
```python
# Estados disponíveis (enum AgentStatus)
AgentStatus.IDLE        # Aguardando
AgentStatus.THINKING    # Processando
AgentStatus.ACTING      # Executando ação
AgentStatus.WAITING     # Aguardando resposta
AgentStatus.ERROR       # Erro
AgentStatus.COMPLETED   # Concluído

# Verificar estado
status_info = agent.get_status()
# {
#     "name": "meu_agent",
#     "description": "...",
#     "status": "idle",
#     "capabilities": [...],
#     "message_count": 45,
#     "response_count": 45
# }
```

### Histórico de Mensagens
```python
# Obter histórico completo
history = agent.get_history()

# Obter últimas N mensagens
history = agent.get_history(limit=10)

# Limpar histórico
agent.clear_history()
```

### Integração com Métricas (Prometheus)
```python
# Métricas coletadas automaticamente:

# Contadores
cidadao_ai_agent_tasks_total{
    agent_name="zumbi",
    task_type="analyze",
    status="completed|retry|failed"
}

# Tempo de processamento (via BusinessMetrics)
agent_task_duration_seconds{
    agent_name="zumbi",
    task_type="analyze"
}
```

### Logging Estruturado
```python
# Logs automáticos em eventos-chave:
# - agent_initialized
# - agent_executing
# - agent_execution_completed
# - agent_execution_failed
# - agent_reflection
# - max_reflections_reached
# - agent_history_cleared

# Usar self.logger em métodos customizados
self.logger.info(
    "custom_event",
    agent_name=self.name,
    custom_field="value",
    investigation_id=context.investigation_id
)
```

## 📊 Diagrama de Herança

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +name: str
        +description: str
        +capabilities: List[str]
        +status: AgentStatus
        +max_retries: int
        +timeout: int
        +initialize()* async
        +shutdown()* async
        +process(message, context)* async
        +execute(action, payload, context) async
        +can_handle(action) bool
        +get_status() Dict
        +get_history(limit) Dict
        +clear_history() void
    }

    class ReflectiveAgent {
        <<abstract>>
        +reflection_threshold: float
        +max_reflection_loops: int
        +reflect(result, context)* async
        +process_with_reflection(message, context) async
    }

    class Abaporu {
        +orchestrate_agents()
        +delegate_task()
        +aggregate_results()
    }

    class Zumbi {
        +detect_anomalies()
        +spectral_analysis()
    }

    class Anita {
        +analyze_trends()
        +statistical_analysis()
    }

    BaseAgent <|-- ReflectiveAgent
    ReflectiveAgent <|-- Abaporu
    ReflectiveAgent <|-- Zumbi
    BaseAgent <|-- Anita
```

## 🧪 Testes

### Testando Agentes Customizados
```python
import pytest
from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse
from src.core import AgentStatus

@pytest.mark.asyncio
async def test_meu_agente_analyze():
    # Setup
    agent = MeuNovoAgent()
    await agent.initialize()

    context = AgentContext(investigation_id="TEST-001")
    message = AgentMessage(
        sender="test",
        recipient=agent.name,
        action="analyze",
        payload={"data": [1, 2, 3]}
    )

    # Execute
    response = await agent.process(message, context)

    # Assert
    assert response.status == AgentStatus.COMPLETED
    assert response.result is not None
    assert "analysis_result" in response.result

    # Cleanup
    await agent.shutdown()

@pytest.mark.asyncio
async def test_agente_reflexivo_quality():
    # Setup
    agent = MeuAgenteReflexivo()
    await agent.initialize()

    context = AgentContext(investigation_id="TEST-002")
    message = AgentMessage(
        sender="test",
        recipient=agent.name,
        action="analyze",
        payload={"data": [...]}
    )

    # Execute com reflexão
    response = await agent.process_with_reflection(message, context)

    # Assert
    assert response.status == AgentStatus.COMPLETED
    assert "reflection" in response.metadata
    assert response.metadata["reflection"]["quality_score"] >= agent.reflection_threshold

    # Cleanup
    await agent.shutdown()
```

## 🔄 Ciclo de Vida de um Agente

```mermaid
sequenceDiagram
    participant System
    participant Agent
    participant Logger
    participant Metrics

    System->>Agent: __init__()
    Agent->>Logger: Registrar agent_initialized

    System->>Agent: initialize()
    Note over Agent: Carregar recursos

    loop Para cada mensagem
        System->>Agent: execute(action, payload, context)
        Agent->>Metrics: Increment task counter (started)
        Agent->>Agent: process(message, context)

        alt Success
            Agent->>Metrics: Record success metrics
            Agent->>Logger: agent_execution_completed
            Agent-->>System: AgentResponse (COMPLETED)
        else Error (retry)
            Agent->>Logger: agent_execution_failed
            Agent->>Metrics: Increment retry counter
            Agent->>Agent: Exponential backoff
            Agent->>Agent: Retry process()
        else All retries exhausted
            Agent->>Metrics: Record failure metrics
            Agent->>Logger: Final error
            Agent-->>System: AgentResponse (ERROR)
        end
    end

    System->>Agent: shutdown()
    Note over Agent: Liberar recursos
```

## 🐛 Tratamento de Erros

### Retry Automático
```python
# Configurar retries no __init__
class MeuAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="meu_agent",
            description="...",
            capabilities=[...],
            max_retries=5,    # 5 tentativas antes de falhar
            timeout=120       # 120 segundos de timeout
        )
```

### Erros Customizados
```python
from src.core.exceptions import AgentExecutionError, DataAnalysisError

async def process(self, message: AgentMessage, context: AgentContext) -> AgentResponse:
    try:
        result = await self._do_work()
        return AgentResponse(...)

    except DataAnalysisError as e:
        # Erro específico de análise
        self.logger.error("Analysis failed", error=str(e))
        return AgentResponse(
            agent_name=self.name,
            status=AgentStatus.ERROR,
            error=f"Analysis error: {str(e)}"
        )

    except Exception as e:
        # Erro genérico
        self.logger.error("Unexpected error", error=str(e), exc_info=True)
        raise AgentExecutionError(
            f"Agent {self.name} failed unexpectedly",
            details={"error": str(e)}
        )
```

## 📚 Referências

### Cultural
- **Deodoro da Fonseca**: Marechal (1827-1892)
- **Proclamação da República**: 15 de novembro de 1889
- **Fundador**: Estabeleceu estruturas da República

### Técnicas
- **Design Patterns**: Template Method, Strategy
- **SOLID Principles**: Single Responsibility, Open/Closed
- **Clean Architecture**: Separation of Concerns

### Documentação Relacionada
- [Arquitetura Multi-Agente](../architecture/multi-agent.md)
- [Padrão ReAct](../architecture/react-pattern.md)
- [Guia de Logging](../development/logging.md)
- [Métricas Prometheus](../monitoring/prometheus.md)

---

**Anterior:** [← Visão Geral dos Agentes](./README.md)
**Próximo:** [🔍 Zumbi dos Palmares - Investigator Agent →](./zumbi.md)

---

**Última Atualização**: 12/10/2025 16:30
**Status**: ✅ 100% Operacional
**Autor**: Anderson Henrique da Silva

**Nota**: Esta é a classe base mais importante do sistema. Todos os 17 agentes herdam dela. Sólida, testada, e production-ready! 🏛️
