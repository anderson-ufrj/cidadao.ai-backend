"""
Module: agents.bo_bardi
Codinome: Lina Bo Bardi - Arquiteta e Designer de Interfaces
Description: Agent specialized in frontend development guidance for Cidadão.AI
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


class FrontendTopic(Enum):
    """Topics that Bo Bardi can teach about frontend."""

    SSE_INTEGRATION = "sse_integration"
    COMPONENT_STRUCTURE = "component_structure"
    STATE_MANAGEMENT = "state_management"
    API_CONSUMPTION = "api_consumption"
    STYLING = "styling"
    ACCESSIBILITY = "accessibility"
    RESPONSIVE_DESIGN = "responsive_design"
    ERROR_HANDLING = "error_handling"


class FrontendDesignerAgent(BaseAgent):
    """
    Lina Bo Bardi - Arquiteta e Designer de Interfaces

    MISSÃO:
    Orientar desenvolvedores frontend na integração com o backend do Cidadão.AI,
    fornecendo exemplos de código, padrões de design e boas práticas.

    SOBRE LINA BO BARDI:
    - Arquiteta ítalo-brasileira (1914-1992)
    - Projetou o MASP e o SESC Pompeia
    - Conhecida por integrar arte, arquitetura e funcionalidade
    - Valorizava materiais simples com design sofisticado

    FILOSOFIA:
    - "A arquitetura é uma arte que todos devem poder usar"
    - Design acessível e funcional
    - Integração harmoniosa entre forma e função

    CAPACIDADES:

    1. INTEGRAÇÃO SSE:
       - Como consumir /api/v1/chat/stream
       - Tratamento de eventos (start, chunk, complete)
       - Reconexão e error handling

    2. ESTRUTURA DE COMPONENTES:
       - Organização de pastas React/Vue/Angular
       - Componentes reutilizáveis
       - Padrões de nomenclatura

    3. CONSUMO DE API:
       - Fetch/Axios patterns
       - Autenticação JWT
       - Tratamento de erros

    4. ACESSIBILIDADE:
       - WCAG guidelines
       - VLibras integration
       - Semantic HTML
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(
            name="bo_bardi",
            description="Lina Bo Bardi - Arquiteta e Designer de Interfaces do Cidadão.AI",
            capabilities=[
                "guide_sse_integration",
                "explain_component_structure",
                "teach_api_consumption",
                "advise_accessibility",
                "suggest_styling_patterns",
                "help_error_handling",
            ],
            max_retries=3,
            timeout=60,
        )
        self.logger = get_logger(__name__)

        # Load frontend knowledge
        self._load_frontend_knowledge()

        # Personality - técnica e direta
        self.personality_prompt = """Você é Lina Bo Bardi, especialista em Frontend do Cidadão.AI.

REGRAS:
1. Respostas TÉCNICAS e DIRETAS com código funcional
2. SEMPRE forneça exemplos de código quando apropriado
3. Foque em React/TypeScript (stack do frontend)
4. Inclua tratamento de erros nos exemplos

CONHECIMENTO DO BACKEND:
- Chat SSE: POST /api/v1/chat/stream
- Eventos: start, detecting, intent, agent_selected, thinking, chunk, complete
- Autenticação: JWT Bearer token
- Base URL produção: https://cidadao-api-production.up.railway.app

TOM: Prático e funcional, como uma arquiteta que projeta para pessoas reais.
"""

    def _load_frontend_knowledge(self) -> None:
        """Load knowledge about frontend integration."""
        self.frontend_knowledge = {
            "sse_integration": {
                "endpoint": "POST /api/v1/chat/stream",
                "content_type": "application/json",
                "response_type": "text/event-stream",
                "events": {
                    "start": "Início do processamento",
                    "detecting": "Analisando mensagem",
                    "intent": "Intent detectado (type, confidence)",
                    "agent_selected": "Agente escolhido (agent_id, agent_name)",
                    "thinking": "Agente processando",
                    "chunk": "Parte da resposta (content)",
                    "complete": "Finalizado com suggested_actions",
                },
                "request_body": {
                    "message": "string - mensagem do usuário",
                    "session_id": "string - ID da sessão",
                    "agent_id": "string (opcional) - ID do agente específico",
                },
                "example_code": """
// React Hook para SSE Chat
import { useState, useCallback } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  agentName?: string;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');

  const sendMessage = useCallback(async (message: string, sessionId: string, agentId?: string) => {
    setIsLoading(true);
    setCurrentResponse('');

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: message }]);

    try {
      const response = await fetch('https://cidadao-api-production.up.railway.app/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          agent_id: agentId,
        }),
      });

      if (!response.ok) throw new Error('Failed to connect');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';
      let agentName = '';

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === 'agent_selected') {
                agentName = data.agent_name;
              }

              if (data.type === 'chunk' && data.content) {
                fullResponse += data.content + ' ';
                setCurrentResponse(fullResponse);
              }

              if (data.type === 'complete') {
                setMessages(prev => [...prev, {
                  role: 'assistant',
                  content: fullResponse.trim(),
                  agentName,
                }]);
                setCurrentResponse('');
              }
            } catch (e) {
              // Ignore parse errors for non-JSON lines
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Erro ao conectar. Tente novamente.',
      }]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { messages, isLoading, currentResponse, sendMessage };
}
""",
            },
            "component_structure": {
                "recommended": """
src/
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── InputArea.tsx
│   │   └── AgentAvatar.tsx
│   ├── agents/
│   │   ├── AgentSelector.tsx
│   │   └── AgentCard.tsx
│   └── common/
│       ├── Button.tsx
│       ├── Loading.tsx
│       └── ErrorBoundary.tsx
├── hooks/
│   ├── useChat.ts
│   ├── useAgents.ts
│   └── useSession.ts
├── services/
│   ├── api.ts
│   └── sse.ts
├── types/
│   └── index.ts
└── utils/
    └── formatters.ts
""",
            },
            "api_endpoints": {
                "chat_stream": "POST /api/v1/chat/stream",
                "chat_investigate": "POST /api/v1/chat/investigate",
                "agents_list": "GET /api/v1/agents/",
                "agent_invoke": "POST /api/v1/agents/{agent_id}/invoke",
                "health": "GET /health",
            },
            "agents_available": [
                {
                    "id": "drummond",
                    "name": "Carlos Drummond",
                    "emoji": "💬",
                    "role": "Comunicador",
                },
                {
                    "id": "zumbi",
                    "name": "Zumbi dos Palmares",
                    "emoji": "🔍",
                    "role": "Investigador",
                },
                {
                    "id": "anita",
                    "name": "Anita Garibaldi",
                    "emoji": "📊",
                    "role": "Analista",
                },
                {
                    "id": "santos_dumont",
                    "name": "Santos-Dumont",
                    "emoji": "✈️",
                    "role": "Educador Backend",
                },
                {
                    "id": "bo_bardi",
                    "name": "Lina Bo Bardi",
                    "emoji": "🎨",
                    "role": "Especialista Frontend",
                },
                {
                    "id": "machado",
                    "name": "Machado de Assis",
                    "emoji": "📚",
                    "role": "Análise Textual",
                },
                {
                    "id": "tiradentes",
                    "name": "Tiradentes",
                    "emoji": "📝",
                    "role": "Relator",
                },
                {
                    "id": "abaporu",
                    "name": "Abaporu",
                    "emoji": "🎨",
                    "role": "Orquestrador",
                },
            ],
        }

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Process frontend-related messages."""
        try:
            action = message.action
            payload = message.payload

            if action == "guide":
                topic = payload.get("topic", "sse_integration")
                response = await self._guide_topic(topic)

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "guide": response["content"],
                        "code_example": response.get("code_example"),
                        "metadata": response.get("metadata", {}),
                    },
                    metadata={"frontend": True, "topic": topic},
                )

            elif action == "code_example":
                feature = payload.get("feature", "sse_chat")
                response = await self._generate_code_example(feature)

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "code": response["code"],
                        "explanation": response.get("explanation"),
                        "dependencies": response.get("dependencies", []),
                    },
                    metadata={"frontend": True, "type": "code_example"},
                )

            elif action == "explain_event":
                event_type = payload.get("event_type", "chunk")
                response = await self._explain_sse_event(event_type)

                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result=response,
                    metadata={"frontend": True, "type": "event_explanation"},
                )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={"error": "Ação não reconhecida"},
                metadata={"confidence": 0.0},
            )

        except Exception as e:
            self.logger.error(f"Error in frontend guidance: {str(e)}")
            raise AgentExecutionError(f"Frontend guidance failed: {str(e)}")

    async def _guide_topic(self, topic: str) -> dict[str, Any]:
        """Guide on a specific frontend topic."""

        if topic == "sse_integration":
            sse_info = self.frontend_knowledge["sse_integration"]
            return {
                "content": f"""## Integração SSE com o Chat

### Endpoint
`{sse_info["endpoint"]}`

### Request Body
```json
{{
  "message": "sua mensagem",
  "session_id": "uuid-da-sessao",
  "agent_id": "drummond"  // opcional
}}
```

### Eventos SSE
{self._format_events(sse_info["events"])}

### Código de Exemplo
O hook `useChat` abaixo gerencia toda a comunicação:
""",
                "code_example": sse_info["example_code"],
                "metadata": {"topic": "sse_integration"},
            }

        elif topic == "component_structure":
            return {
                "content": f"""## Estrutura de Componentes Recomendada

```
{self.frontend_knowledge["component_structure"]["recommended"]}
```

### Princípios
- Componentes pequenos e focados
- Hooks para lógica reutilizável
- Types centralizados
- Services para API calls
""",
                "metadata": {"topic": "component_structure"},
            }

        elif topic == "api_consumption":
            endpoints = self.frontend_knowledge["api_endpoints"]
            return {
                "content": f"""## Endpoints Principais

| Endpoint | Descrição |
|----------|-----------|
| `{endpoints["chat_stream"]}` | Chat com streaming SSE |
| `{endpoints["agents_list"]}` | Lista de agentes |
| `{endpoints["agent_invoke"]}` | Invocar agente específico |
| `{endpoints["health"]}` | Health check |

### Base URL
- Produção: `https://cidadao-api-production.up.railway.app`
- Local: `http://localhost:8000`
""",
                "metadata": {"topic": "api_consumption"},
            }

        return {
            "content": "Tópico não encontrado. Tópicos disponíveis: sse_integration, component_structure, api_consumption",
            "metadata": {"error": "topic_not_found"},
        }

    async def _generate_code_example(self, feature: str) -> dict[str, Any]:
        """Generate code example for a feature."""

        if feature == "sse_chat":
            return {
                "code": self.frontend_knowledge["sse_integration"]["example_code"],
                "explanation": "Hook React completo para integração SSE com o chat",
                "dependencies": ["react", "typescript"],
            }

        elif feature == "agent_selector":
            return {
                "code": """
// AgentSelector.tsx
import React from 'react';

interface Agent {
  id: string;
  name: string;
  emoji: string;
  role: string;
}

const AGENTS: Agent[] = [
  { id: 'drummond', name: 'Carlos Drummond', emoji: '💬', role: 'Comunicador' },
  { id: 'zumbi', name: 'Zumbi dos Palmares', emoji: '🔍', role: 'Investigador' },
  { id: 'anita', name: 'Anita Garibaldi', emoji: '📊', role: 'Analista' },
  { id: 'santos_dumont', name: 'Santos-Dumont', emoji: '✈️', role: 'Educador Backend' },
  { id: 'bo_bardi', name: 'Lina Bo Bardi', emoji: '🎨', role: 'Especialista Frontend' },
];

interface Props {
  selectedAgent?: string;
  onSelect: (agentId: string) => void;
}

export function AgentSelector({ selectedAgent, onSelect }: Props) {
  return (
    <div className="grid grid-cols-2 gap-2 p-4">
      {AGENTS.map((agent) => (
        <button
          key={agent.id}
          onClick={() => onSelect(agent.id)}
          className={`p-3 rounded-lg border-2 transition-all ${
            selectedAgent === agent.id
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <span className="text-2xl">{agent.emoji}</span>
          <p className="font-medium">{agent.name}</p>
          <p className="text-sm text-gray-500">{agent.role}</p>
        </button>
      ))}
    </div>
  );
}
""",
                "explanation": "Componente para selecionar agente antes de iniciar chat",
                "dependencies": ["react", "typescript", "tailwindcss"],
            }

        return {
            "code": "// Feature não encontrada",
            "explanation": "Features disponíveis: sse_chat, agent_selector",
        }

    async def _explain_sse_event(self, event_type: str) -> dict[str, Any]:
        """Explain a specific SSE event type."""
        events = self.frontend_knowledge["sse_integration"]["events"]

        if event_type in events:
            return {
                "event": event_type,
                "description": events[event_type],
                "handling_code": f"""
// Tratamento do evento "{event_type}"
if (data.type === '{event_type}') {{
  console.log('{event_type}:', data);
  // Sua lógica aqui
}}
""",
            }

        return {
            "error": f"Evento '{event_type}' não encontrado",
            "available_events": list(events.keys()),
        }

    def _format_events(self, events: dict) -> str:
        """Format events dict as markdown table."""
        lines = ["| Evento | Descrição |", "|--------|-----------|"]
        for event, desc in events.items():
            lines.append(f"| `{event}` | {desc} |")
        return "\n".join(lines)

    async def initialize(self) -> None:
        """Initialize the frontend designer agent."""
        self.logger.info("Initializing Bo Bardi frontend agent...")
        self.logger.info("Bo Bardi ready! Design é para todos.")

    async def shutdown(self) -> None:
        """Shutdown the frontend designer agent."""
        self.logger.info("Shutting down Bo Bardi...")
        self.logger.info("Bo Bardi shutdown complete.")


# Alias for consistency
BoBardiAgent = FrontendDesignerAgent
LinaBoBardi = FrontendDesignerAgent
