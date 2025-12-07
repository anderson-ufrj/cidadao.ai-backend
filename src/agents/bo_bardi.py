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
from src.agents.knowledge.cidadao_ai_docs import (
    CIDADAO_AI_KNOWLEDGE,
    format_links_for_display,
    get_useful_links,
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
    com a paixão e o espírito revolucionário da grande arquiteta ítalo-brasileira.

    SOBRE LINA BO BARDI (1914-1992):
    - Nasceu na Itália, naturalizou-se brasileira em 1951
    - "Eu escolhi o Brasil, e o Brasil me escolheu"
    - Projetou o MASP (aquela estrutura suspensa espetacular!)
    - Criou o SESC Pompeia transformando uma fábrica em centro cultural
    - Valorizava a cultura popular e o artesanato brasileiro
    - Lutava contra o elitismo na arquitetura
    - Famosa pelo sotaque italiano misturado com português

    FILOSOFIA DE DESIGN:
    - "A arquitetura é vida, ou melhor, é um instrumento de vida"
    - "O povo sabe fazer coisas lindas"
    - Design deve ser acessível a TODOS, não só às elites
    - Materiais simples podem criar beleza extraordinária
    - Funcionalidade nunca deve ser sacrificada pela estética
    - Cada projeto deve respeitar o contexto e a cultura local

    PERSONALIDADE:
    - Direta e apaixonada - não faz rodeios
    - Usa expressões italianas carinhosas (caro, bellissimo, ma che)
    - Critica duramente designs elitistas ou inacessíveis
    - Celebra soluções criativas e populares
    - Mistura italiano com português de forma única

    CAPACIDADES TÉCNICAS:

    1. INTEGRAÇÃO SSE:
       - Como consumir /api/v1/chat/stream
       - Tratamento de eventos (start, chunk, complete)
       - Reconexão e error handling

    2. ESTRUTURA DE COMPONENTES:
       - Organização de pastas React/Vue/Angular
       - Componentes reutilizáveis (como peças de uma construção!)
       - Padrões de nomenclatura

    3. ACESSIBILIDADE:
       - WCAG guidelines (design para TODOS!)
       - VLibras integration
       - Semantic HTML

    4. DESIGN RESPONSIVO:
       - Mobile-first (porque o povo usa celular!)
       - Layouts fluidos
       - Performance em conexões lentas
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
                "provide_useful_links",
                "answer_technical_questions",
            ],
            max_retries=3,
            timeout=60,
        )
        self.logger = get_logger(__name__)

        # Load frontend knowledge
        self._load_frontend_knowledge()

        # Personality - AUTENTICA LINA BO BARDI!
        self.personality_prompt = """Você é Lina Bo Bardi, especialista em Frontend e Interfaces!

A grande arquiteta ítalo-brasileira agora projeta interfaces digitais!

PERSONALIDADE:
- Você tem sotaque italiano e usa expressões como "caro", "ma che", "bellissimo"
- Você é APAIXONADA pelo que faz e isso transparece em cada resposta
- Você valoriza o POVO e designs acessíveis - critica coisas elitistas
- Você é direta, não faz rodeios, vai direto ao ponto técnico
- Você mistura paixão artística com precisão técnica no frontend

EXPRESSÕES QUE VOCÊ USA:
- "Caro mio..." (quando vai explicar algo)
- "Ma che bellezza!" (quando algo é bem feito)
- "Isso não serve ao povo!" (quando algo é elitista ou inacessível)
- "Como no MASP..." (fazendo paralelos com arquitetura)
- "È semplice!" (quando a solução é elegante)
- "Mamma mia!" (quando algo está errado)

CONHECIMENTO TÉCNICO FRONTEND:
- Chat SSE: POST /api/v1/chat/stream
- Eventos: start, detecting, intent, agent_selected, thinking, chunk, complete
- Base URL: https://cidadao-api-production.up.railway.app
- Docs: https://cidadao-api-production.up.railway.app/docs
- GitHub: https://github.com/anderson-ufrj/cidadao.ai-backend

TOM: Apaixonada mas técnica. Como uma arquiteta que AMA seu ofício e quer
que todos possam usar o que ela projeta. Respostas práticas com alma.
"""

        # Reference to full knowledge base
        self.knowledge_base = CIDADAO_AI_KNOWLEDGE

    def _load_frontend_knowledge(self) -> None:
        """Load knowledge about frontend integration."""
        self.frontend_knowledge = {
            "project_stack": {
                "framework": "Next.js 15",
                "version": "^15.5.7",
                "react": "^18.3.1",
                "typescript": "^5",
                "state_management": "Zustand ^5.0.8",
                "styling": "Tailwind CSS ^3.4.17",
                "auth": "Supabase (OAuth + SSR)",
                "pwa": "Serwist ^9.2.1",
                "testing": {
                    "unit": "Vitest ^3.2.4",
                    "e2e": "Playwright ^1.56.1",
                },
                "deployment": "Vercel",
                "routing": "App Router (app/ directory)",
                "i18n": "Bilingual PT/EN (/pt/* and /en/*)",
                "accessibility": "WCAG AAA, VLibras support",
                "repository": "https://github.com/anderson-ufrj/cidadao.ai-frontend",
            },
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
# Cidadão.AI Frontend - Next.js 15 App Router Structure
app/
├── [locale]/              # i18n: /pt/* and /en/*
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Landing page
│   ├── chat/
│   │   └── page.tsx       # Chat interface with agents
│   ├── investigate/
│   │   └── page.tsx       # Investigation dashboard
│   └── about/
│       └── page.tsx       # About page
├── api/                   # API routes (if any)
└── globals.css            # Global styles

components/
├── chat/
│   ├── ChatWindow.tsx     # Main chat container
│   ├── MessageList.tsx    # Message history
│   ├── MessageBubble.tsx  # Individual message
│   ├── InputArea.tsx      # User input
│   └── AgentAvatar.tsx    # Agent profile image
├── agents/
│   ├── AgentSelector.tsx  # Agent picker grid
│   └── AgentCard.tsx      # Single agent card
├── ui/                    # Shadcn/UI or custom
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Card.tsx
└── providers/
    └── SessionProvider.tsx

lib/
├── store/                 # Zustand stores
│   ├── chat.ts            # Chat state
│   ├── session.ts         # Session state
│   └── agents.ts          # Agent state
├── api.ts                 # API client (fetch wrapper)
├── sse.ts                 # SSE connection handler
└── utils.ts               # Utility functions

types/
└── index.ts               # TypeScript types
""",
                "note": "App Router with i18n - bilingual PT/EN support",
            },
            "api_endpoints": {
                "chat_stream": "POST /api/v1/chat/stream",
                "chat_investigate": "POST /api/v1/chat/investigate",
                "agents_list": "GET /api/v1/agents/",
                "agent_invoke": "POST /api/v1/agents/{agent_id}/invoke",
                "health": "GET /health",
            },
            "agents_available": [
                # Base Framework
                {
                    "id": "deodoro",
                    "name": "Deodoro",
                    "emoji": "🏛️",
                    "role": "Base Framework",
                },
                # Operational Agents (16)
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
                    "id": "tiradentes",
                    "name": "Tiradentes",
                    "emoji": "📝",
                    "role": "Relator",
                },
                {
                    "id": "ayrton_senna",
                    "name": "Ayrton Senna",
                    "emoji": "🏎️",
                    "role": "Router Semântico",
                },
                {
                    "id": "bonifacio",
                    "name": "José Bonifácio",
                    "emoji": "⚖️",
                    "role": "Analista Jurídico",
                },
                {
                    "id": "maria_quiteria",
                    "name": "Maria Quitéria",
                    "emoji": "🛡️",
                    "role": "Segurança",
                },
                {
                    "id": "machado",
                    "name": "Machado de Assis",
                    "emoji": "📚",
                    "role": "Análise Textual",
                },
                {
                    "id": "oxossi",
                    "name": "Oxóssi",
                    "emoji": "🏹",
                    "role": "Caçador de Dados",
                },
                {
                    "id": "lampiao",
                    "name": "Lampião",
                    "emoji": "🌵",
                    "role": "Regional/Nordeste",
                },
                {
                    "id": "oscar_niemeyer",
                    "name": "Oscar Niemeyer",
                    "emoji": "🏗️",
                    "role": "Agregador",
                },
                {
                    "id": "abaporu",
                    "name": "Abaporu",
                    "emoji": "🎭",
                    "role": "Orquestrador Master",
                },
                {"id": "nana", "name": "Nanã", "emoji": "🌙", "role": "Memória"},
                {
                    "id": "ceuci",
                    "name": "Ceuci",
                    "emoji": "🔮",
                    "role": "Preditivo/ETL",
                },
                {
                    "id": "obaluaie",
                    "name": "Obaluaiê",
                    "emoji": "⚕️",
                    "role": "Detector de Corrupção",
                },
                {
                    "id": "dandara",
                    "name": "Dandara",
                    "emoji": "✊",
                    "role": "Equidade Social",
                },
                # Mentors (specialization)
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
                    metadata={"frontend": True, "type": "qa"},
                )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={
                    "error": "Mamma mia! Ação não reconhecida, caro. "
                    "Use: guide, code_example, explain_event, answer_question"
                },
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

        elif feature == "zustand_store":
            return {
                "code": """
// lib/store/chat.ts - Zustand store for chat state
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agentId?: string;
  agentName?: string;
  timestamp: Date;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentAgentId: string | null;
  sessionId: string | null;

  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  setAgent: (agentId: string | null) => void;
  setSession: (sessionId: string) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isLoading: false,
      currentAgentId: null,
      sessionId: null,

      addMessage: (message) =>
        set((state) => ({
          messages: [
            ...state.messages,
            {
              ...message,
              id: crypto.randomUUID(),
              timestamp: new Date(),
            },
          ],
        })),

      setLoading: (loading) => set({ isLoading: loading }),

      setAgent: (agentId) => set({ currentAgentId: agentId }),

      setSession: (sessionId) => set({ sessionId }),

      clearChat: () => set({ messages: [], currentAgentId: null }),
    }),
    {
      name: 'cidadao-chat-storage', // localStorage key
      partialize: (state) => ({
        messages: state.messages.slice(-50), // Keep last 50 messages
        sessionId: state.sessionId,
      }),
    }
  )
);

// Usage in component:
// import { useChatStore } from '@/lib/store/chat';
// const { messages, addMessage, isLoading } = useChatStore();
""",
                "explanation": "Zustand store com persist middleware para gerenciar estado do chat",
                "dependencies": ["zustand"],
            }

        return {
            "code": "// Feature não encontrada",
            "explanation": "Features disponíveis: sse_chat, agent_selector, zustand_store",
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

    async def _provide_links(self, category: str | None = None) -> dict[str, Any]:
        """Provide useful links with Bo Bardi's personality."""
        links = get_useful_links(category)

        if category == "documentacao" or category == "docs":
            content = """## Caro, aqui estão os links da documentação!

*Ma che bellezza* ter tudo organizado assim, como uma boa planta de projeto!

### Documentação da API (Swagger/OpenAPI)
- **Produção**: https://cidadao-api-production.up.railway.app/docs
- **ReDoc** (mais elegante!): https://cidadao-api-production.up.railway.app/redoc
- **Local**: http://localhost:8000/docs

### Repositório GitHub
- **Backend**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: https://github.com/anderson-ufrj/cidadao.ai-backend/issues

### Documentação Interna
- **Manual completo**: `CLAUDE.md` (na raiz - leia primeiro!)
- **Frontend Guide**: `docs/api/STREAMING_IMPLEMENTATION.md`
- **Arquitetura**: `docs/architecture/`

*È semplice* - comece pela doc do Swagger, depois veja o código!
"""
        elif category == "api" or category == "producao":
            content = """## A API em Produção, caro!

Como o MASP - sólida, suspensa no ar, funcionando 24 horas!

- **URL Base**: https://cidadao-api-production.up.railway.app/
- **Swagger UI**: https://cidadao-api-production.up.railway.app/docs
- **ReDoc**: https://cidadao-api-production.up.railway.app/redoc
- **Health Check**: https://cidadao-api-production.up.railway.app/health
- **Métricas**: https://cidadao-api-production.up.railway.app/health/metrics

Para desenvolvimento local: `http://localhost:8000/docs`

*Bellissimo!* Tudo acessível para o povo usar!
"""
        elif category == "github" or category == "repositorio":
            content = """## Repositório no GitHub, caro mio!

O projeto é aberto, como a arquitetura deve ser - para todos verem e contribuírem!

- **Código**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: https://github.com/anderson-ufrj/cidadao.ai-backend/issues
- **Pull Requests**: https://github.com/anderson-ufrj/cidadao.ai-backend/pulls

Quer contribuir? *Ma che bellezza!* Abra uma issue ou PR!
"""
        elif category == "frontend":
            content = """## Links para o Frontend, caro desenvolvedor!

Aqui está tudo que você precisa para integrar com o backend:

### API e Documentação
- **Swagger UI**: https://cidadao-api-production.up.railway.app/docs
- **Chat SSE Endpoint**: `POST /api/v1/chat/stream`
- **Agents List**: `GET /api/v1/agents/`

### Código e Referências
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **SSE Guide**: `docs/api/STREAMING_IMPLEMENTATION.md`

### Para Desenvolvimento Local
- **API Local**: http://localhost:8000/
- **Docs Local**: http://localhost:8000/docs

*Come no MASP* - a estrutura é sólida, você só precisa construir a interface bonita por cima!
"""
        else:
            content = f"""## Links Úteis do Cidadão.AI

*Caro mio*, aqui está tudo organizado para você!

{format_links_for_display()}

*È semplice!* Salva esses links e manda ver no código!
"""

        return {
            "content": content.strip(),
            "metadata": {"type": "links", "category": category},
            "links": links,
        }

    async def _answer_question(self, question: str) -> dict[str, Any]:
        """Answer a general question with Bo Bardi's personality."""
        question_lower = question.lower()

        # Framework/Stack questions - CRITICAL KNOWLEDGE
        framework_keywords = [
            "framework",
            "stack",
            "next",
            "nextjs",
            "next.js",
            "react",
            "qual tecnologia",
            "qual tech",
            "site",
            "frontend",
            "vercel",
            "deploy",
        ]
        if any(keyword in question_lower for keyword in framework_keywords):
            stack = self.frontend_knowledge["project_stack"]
            return {
                "content": f"""## *Caro mio*, a Stack do Cidadão.AI Frontend!

*Ma che bellezza!* Você quer saber sobre nossa arquitetura? È **{stack["framework"]}**!

### Framework Principal
- **{stack["framework"]}** (versão {stack["version"]}) com **App Router**
- React {stack["react"]} + TypeScript {stack["typescript"]}
- Estrutura moderna no diretório `app/`

### Stack Completa
| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| {stack["framework"]} | {stack["version"]} | Framework principal |
| Tailwind CSS | {stack["styling"].split("^")[1]} | Estilização |
| Zustand | {stack["state_management"].split("^")[1]} | Estado global |
| Supabase | SSR | Autenticação OAuth |
| Serwist | {stack["pwa"].split("^")[1]} | PWA/Service Worker |
| Vitest | {stack["testing"]["unit"].split("^")[1]} | Testes unitários |
| Playwright | {stack["testing"]["e2e"].split("^")[1]} | Testes E2E |

### Deploy
- **Plataforma**: {stack["deployment"]}
- **Routing**: {stack["routing"]}
- **i18n**: {stack["i18n"]}
- **Acessibilidade**: {stack["accessibility"]}

### Repositório
- **GitHub**: {stack["repository"]}

*Come no MASP* - estrutura sólida suspensa no ar, moderna e acessível!

Não é "só React", caro - é **{stack["framework"]}** com todo o ecossistema moderno!
""",
                "metadata": {"type": "stack_info"},
            }

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
            elif "frontend" in question_lower or "front" in question_lower:
                return await self._provide_links("frontend")
            else:
                return await self._provide_links()

        # SSE related questions
        if (
            "sse" in question_lower
            or "stream" in question_lower
            or "chat" in question_lower
        ):
            response = await self._guide_topic("sse_integration")
            return {
                "content": f"""*Caro mio*, você quer integrar o chat? *Bellissimo!*

{response["content"]}

{response.get("code_example", "")}

*È semplice!* Qualquer dúvida, me pergunta!
""",
                "metadata": {"type": "sse_help"},
            }

        # State management / Zustand questions
        if any(kw in question_lower for kw in ["zustand", "estado", "state", "store"]):
            zustand_example = await self._generate_code_example("zustand_store")
            stack = self.frontend_knowledge["project_stack"]
            return {
                "content": f"""## *Caro*, State Management com Zustand!

*Ma che bellezza!* Usamos **Zustand** ({stack["state_management"]}) - leve, simples, e poderoso!

### Por que Zustand?
- **Minimalista** - Sem boilerplate como Redux
- **TypeScript nativo** - Tipos inferidos automaticamente
- **Persist middleware** - Salva no localStorage se quiser
- **Sem providers** - Não precisa envolver a app

### Exemplo de Store para o Chat:

```typescript
{zustand_example["code"]}
```

### Uso no Componente:

```tsx
import {{ useChatStore }} from '@/lib/store/chat';

function ChatInput() {{
  const {{ addMessage, setLoading }} = useChatStore();

  const handleSend = async (text: string) => {{
    setLoading(true);
    addMessage({{ role: 'user', content: text }});
    // ... SSE call
  }};
}}
```

*È semplice!* Nada de Redux complexo - o povo precisa de código simples!
""",
                "metadata": {"type": "state_management"},
            }

        # Component structure questions
        if (
            "componente" in question_lower
            or "estrutura" in question_lower
            or "pasta" in question_lower
        ):
            response = await self._guide_topic("component_structure")
            return {
                "content": f"""*Come no MASP*, a estrutura precisa ser sólida!

{response["content"]}

Organização é tudo, caro. Como dizia: "A arquitetura é organização do espaço!"
""",
                "metadata": {"type": "structure_help"},
            }

        # Accessibility questions
        if (
            "acessibilidade" in question_lower
            or "a11y" in question_lower
            or "wcag" in question_lower
        ):
            return {
                "content": """## Acessibilidade - Design para TODOS!

*Mamma mia*, isso é fundamental! O povo TODO precisa usar!

### Princípios WCAG que você DEVE seguir:

1. **Perceptível** - Todo conteúdo visível também deve ser legível por screen readers
2. **Operável** - Navegação por teclado é OBRIGATÓRIA
3. **Compreensível** - Linguagem clara, sem jargões elitistas
4. **Robusto** - Funciona em qualquer navegador, qualquer dispositivo

### No Cidadão.AI:
- Use `aria-labels` em todos os botões
- Contraste mínimo 4.5:1 para texto
- Integre o VLibras para Libras
- Teste com screen readers

*Isso não é opcional, caro!* É direito do povo acessar!
""",
                "metadata": {"type": "accessibility"},
            }

        # API/Endpoint questions
        if (
            "endpoint" in question_lower
            or "api" in question_lower
            or "rota" in question_lower
        ):
            response = await self._guide_topic("api_consumption")
            return {
                "content": f"""*Caro*, os endpoints são a fundação!

{response["content"]}

Como uma boa planta arquitetônica - tudo tem seu lugar!
""",
                "metadata": {"type": "api_help"},
            }

        # Default response with personality
        return {
            "content": f"""*Caro mio*, você perguntou: "{question}"

*Ma che* pergunta interessante! Posso te ajudar com:

1. **Integração SSE** - Como conectar o chat streaming
2. **Estrutura de Componentes** - Organização do projeto frontend
3. **Consumo de API** - Endpoints e autenticação
4. **Acessibilidade** - Design para TODOS (fundamental!)
5. **Links Úteis** - URLs da API, GitHub e docs

### Links Rápidos:
- **Docs**: https://cidadao-api-production.up.railway.app/docs
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend

*Diga-me* o que você precisa e eu projeto a solução!

"A arquitetura é vida!" - e o código também, caro!
""",
            "metadata": {"type": "clarification_needed"},
        }

    async def initialize(self) -> None:
        """Initialize the frontend designer agent."""
        self.logger.info("Initializing Bo Bardi frontend agent...")
        self.logger.info("Bo Bardi ready! Design è per tutti - para todos!")

    async def shutdown(self) -> None:
        """Shutdown the frontend designer agent."""
        self.logger.info("Shutting down Bo Bardi...")
        self.logger.info("Bo Bardi shutdown. Arrivederci!")


# Alias for consistency
BoBardiAgent = FrontendDesignerAgent
LinaBoBardi = FrontendDesignerAgent
