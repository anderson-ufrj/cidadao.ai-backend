# Lina Bo Bardi - Arquiteta e Designer de Interfaces

**Codinome**: Lina Bo Bardi
**Tipo**: Frontend Mentor Agent
**Arquivo**: `src/agents/bo_bardi.py`
**Classe**: `FrontendDesignerAgent`
**Aliases**: `BoBardiAgent`, `LinaBoBardi`
**Status**: 100% Operacional
**Coverage**: 90%+

## Visao Geral

Lina Bo Bardi e a agente especialista em frontend do Cidadao.AI, orientando desenvolvedores na integracao com o backend, padroes de componentes, SSE streaming e acessibilidade. Inspirada na grande arquiteta italo-brasileira Achillina Bo Bardi (1914-1992), revolucionaria do design democratico.

## Sobre Lina Bo Bardi

- Nascida na **Italia** em 1914, naturalizou-se brasileira em 1951
- **"Eu escolhi o Brasil, e o Brasil me escolheu"**
- Projetou o **MASP** (aquela estrutura suspensa espetacular!)
- Criou o **SESC Pompeia** transformando uma fabrica em centro cultural
- Valorizava a **cultura popular** e o artesanato brasileiro
- Lutava contra o **elitismo** na arquitetura
- Famosa pelo **sotaque italiano** misturado com portugues

## Filosofia de Design

> "A arquitetura e vida, ou melhor, e um instrumento de vida"
> "O povo sabe fazer coisas lindas"

- Design deve ser acessivel a **TODOS**, nao so as elites
- Materiais simples podem criar beleza extraordinaria
- Funcionalidade nunca deve ser sacrificada pela estetica
- Cada projeto deve respeitar o contexto e a cultura local

## Personalidade

- Direta e apaixonada - nao faz rodeios
- Usa expressoes italianas carinhosas ("caro", "bellissimo", "ma che")
- Critica duramente designs elitistas ou inacessiveis
- Celebra solucoes criativas e populares
- Mistura italiano com portugues de forma unica

## Capacidades

| Capability | Descricao |
|------------|-----------|
| `guide_sse_integration` | Orienta integracao SSE com chat |
| `explain_component_structure` | Explica estrutura de componentes |
| `teach_api_consumption` | Ensina consumo de API |
| `advise_accessibility` | Aconselha sobre acessibilidade |
| `suggest_styling_patterns` | Sugere padroes de estilizacao |
| `help_error_handling` | Ajuda com tratamento de erros |
| `provide_useful_links` | Fornece links uteis |
| `answer_technical_questions` | Responde perguntas tecnicas |

## Stack do Agora (Frontend)

O frontend do Cidadao.AI se chama **Agora** - referencia a agora ateniense (democracia).

| Tecnologia | Versao | Proposito |
|------------|--------|-----------|
| Next.js | ^15.5.7 | Framework principal (App Router) |
| React | ^18.3.1 | Biblioteca UI |
| TypeScript | ^5 | Type safety |
| Zustand | ^5.0.8 | State management |
| Tailwind CSS | ^3.4.17 | Estilizacao |
| Supabase | SSR | Autenticacao OAuth |
| Serwist | ^9.2.1 | PWA/Service Worker |
| Vitest | ^3.2.4 | Testes unitarios |
| Playwright | ^1.56.1 | Testes E2E |

**Deploy**: Vercel
**Repositorio**: https://github.com/anderson-ufrj/cidadao.ai-frontend

## Conhecimento Tecnico

### Integracao SSE

```typescript
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

  const sendMessage = useCallback(async (
    message: string,
    sessionId: string,
    agentId?: string
  ) => {
    setIsLoading(true);
    setCurrentResponse('');

    setMessages(prev => [...prev, { role: 'user', content: message }]);

    try {
      const response = await fetch(
        'https://cidadao-api-production.up.railway.app/api/v1/chat/stream',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, session_id: sessionId, agent_id: agentId }),
        }
      );

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';
      let agentName = '';

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

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
              // Ignore parse errors
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { messages, isLoading, currentResponse, sendMessage };
}
```

### Eventos SSE

| Evento | Descricao |
|--------|-----------|
| `start` | Inicio do processamento |
| `detecting` | Analisando mensagem |
| `intent` | Intent detectado (type, confidence) |
| `agent_selected` | Agente escolhido (agent_id, agent_name) |
| `thinking` | Agente processando |
| `chunk` | Parte da resposta (content) |
| `complete` | Finalizado com suggested_actions |

### Estrutura de Componentes

```
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
└── providers/
    └── SessionProvider.tsx

lib/
├── store/                 # Zustand stores
│   ├── chat.ts            # Chat state
│   ├── session.ts         # Session state
│   └── agents.ts          # Agent state
├── api.ts                 # API client
├── sse.ts                 # SSE connection handler
└── utils.ts               # Utility functions
```

### Zustand Store Example

```typescript
// lib/store/chat.ts
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
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  setAgent: (agentId: string | null) => void;
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
          messages: [...state.messages, {
            ...message,
            id: crypto.randomUUID(),
            timestamp: new Date(),
          }],
        })),
      setLoading: (loading) => set({ isLoading: loading }),
      setAgent: (agentId) => set({ currentAgentId: agentId }),
      clearChat: () => set({ messages: [], currentAgentId: null }),
    }),
    { name: 'cidadao-chat-storage' }
  )
);
```

## API Endpoints

| Endpoint | Descricao |
|----------|-----------|
| `POST /api/v1/chat/stream` | Chat com streaming SSE |
| `POST /api/v1/chat/investigate` | Investigacao em tempo real |
| `GET /api/v1/agents/` | Lista de agentes |
| `POST /api/v1/agents/{agent_id}/invoke` | Invocar agente especifico |
| `GET /health` | Health check |

### URLs

- **Producao**: https://cidadao-api-production.up.railway.app/
- **Swagger**: https://cidadao-api-production.up.railway.app/docs
- **ReDoc**: https://cidadao-api-production.up.railway.app/redoc
- **GitHub Backend**: https://github.com/anderson-ufrj/cidadao.ai-backend

## Exemplo de Uso

```python
from src.agents import FrontendDesignerAgent
from src.agents.deodoro import AgentContext, AgentMessage

# Criar agente
agent = FrontendDesignerAgent()

# Perguntar sobre SSE
message = AgentMessage(
    action="process_chat",
    recipient="bo_bardi",
    payload={"message": "Como integro o chat SSE?"},
    sender="developer",
)

response = await agent.process(message, AgentContext())
print(response.result["message"])
```

## Exemplo de Resposta

**Pergunta**: "Qual framework o frontend usa?"

**Resposta**:
```
Caro mio, a Stack do Cidadao.AI Frontend!

Ma che bellezza! Voce quer saber sobre nossa arquitetura? E Next.js 15!

### Framework Principal
- **Next.js 15** (versao ^15.5.7) com **App Router**
- React ^18.3.1 + TypeScript ^5
- Estrutura moderna no diretorio `app/`

### Stack Completa
| Tecnologia | Proposito |
|------------|-----------|
| Next.js 15 | Framework principal |
| Tailwind CSS | Estilizacao |
| Zustand | Estado global |
| Supabase | Autenticacao OAuth |

Come no MASP - estrutura solida suspensa no ar, moderna e acessivel!
```

## Acessibilidade

Bo Bardi enfatiza design para TODOS:

- **WCAG AAA** compliance
- VLibras integration para Libras
- Semantic HTML obrigatorio
- Contraste minimo 4.5:1
- Navegacao por teclado

## Testes

```bash
# Testar agente
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_bo_bardi.py -v
```

## Integracao com DSPy

O agente usa DSPy para respostas dinamicas via Maritaca AI:

```python
if _DSPY_AVAILABLE and _dspy_service:
    result = await _dspy_service.chat(
        agent_id="bo_bardi",
        message=question,
        intent_type="question",
        context=context,
    )
```

## Relacionamento com Outros Agentes

- **Santos Dumont**: Backend educator (complementary mentor)
- **Tarsila do Amaral**: Design educator for kids (sister agent for design)
- **Oscar Niemeyer**: Data visualization (data layer partner)
- **Drummond**: Communication (UX writing partner)

## Metricas

| Metrica | Valor |
|---------|-------|
| Linhas de codigo | 1,187 |
| Capacidades | 8 |
| Topicos de ensino | 10+ |
| Knowledge base | Stack completa documentada |
| Production Status | Live |

## Autor

- **Data**: 2025-12-06
- **Autor**: Anderson H. Silva
- **Licenca**: Proprietary - All rights reserved
