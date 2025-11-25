# Chat Stream - Guia de Integração Frontend

**Data**: 2025-11-25
**Versão**: 1.0.0
**Endpoint**: `/api/v1/chat/stream`

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [Formato dos Eventos SSE](#formato-dos-eventos-sse)
3. [Tipos de Eventos](#tipos-de-eventos)
4. [Configuração Visual dos Agentes](#configuração-visual-dos-agentes)
5. [Implementação React](#implementação-react)
6. [Implementação Vue](#implementação-vue)
7. [Tratamento de Erros](#tratamento-de-erros)
8. [Boas Práticas de UX](#boas-práticas-de-ux)

---

## Visão Geral

O endpoint `/api/v1/chat/stream` usa Server-Sent Events (SSE) para streaming de respostas em tempo real. Cada agente tem uma personalidade única baseada em figuras históricas brasileiras.

### Request

```http
POST /api/v1/chat/stream
Content-Type: application/json

{
  "message": "Quero investigar contratos do Ministério da Saúde"
}
```

### Response

Stream de eventos SSE com diferentes tipos de dados.

---

## Formato dos Eventos SSE

Cada linha do stream segue o formato:
```
data: {"type": "...", ...}\n\n
```

### TypeScript Interfaces

```typescript
// União de todos os tipos de eventos
type StreamEvent =
  | StartEvent
  | DetectingEvent
  | IntentEvent
  | AgentSelectedEvent
  | ThinkingEvent
  | ChunkEvent
  | CompleteEvent
  | ErrorEvent;

interface StartEvent {
  type: 'start';
  timestamp: string; // ISO 8601
}

interface DetectingEvent {
  type: 'detecting';
  message: string; // "Analisando sua mensagem..."
}

interface IntentEvent {
  type: 'intent';
  intent: IntentType;
  confidence: number; // 0.0 - 1.0
}

type IntentType =
  | 'investigate'  // Investigação de dados
  | 'question'     // Pergunta geral
  | 'analyze'      // Análise de dados
  | 'report'       // Geração de relatório
  | 'greeting'     // Saudação
  | 'help'         // Pedido de ajuda
  | 'data'         // Busca de dados
  | 'search';      // Pesquisa

interface AgentSelectedEvent {
  type: 'agent_selected';
  agent_id: AgentId;
  agent_name: string;
}

type AgentId =
  | 'zumbi'      // Investigador
  | 'anita'      // Analista
  | 'drummond'   // Comunicador
  | 'tiradentes' // Relator
  | 'oxossi'     // Caçador de Dados
  | 'dandara'    // Guardiã da Justiça Social
  | 'machado'    // Analista Textual
  | 'abaporu';   // Orquestrador

interface ThinkingEvent {
  type: 'thinking';
  message: string; // "[Agente] está pensando..."
}

interface ChunkEvent {
  type: 'chunk';
  content: string;  // Pedaço do texto (2-3 palavras)
  agent_id: AgentId;
}

interface CompleteEvent {
  type: 'complete';
  agent_id: AgentId;
  agent_name: string;
  suggested_actions: string[]; // ['start_investigation', 'learn_more']
}

interface ErrorEvent {
  type: 'error';
  message: string;
  fallback_endpoint?: string;
}
```

---

## Tipos de Eventos

### Sequência Típica

```
1. start              → Início da conexão
2. detecting          → Analisando mensagem
3. intent             → Intent detectado
4. agent_selected     → Agente escolhido
5. thinking           → Agente processando
6. chunk (N vezes)    → Pedaços da resposta
7. complete           → Resposta finalizada
```

### Exemplo Real

```
data: {"type":"start","timestamp":"2025-11-25T12:00:00+00:00"}

data: {"type":"detecting","message":"Analisando sua mensagem..."}

data: {"type":"intent","intent":"investigate","confidence":0.85}

data: {"type":"agent_selected","agent_id":"zumbi","agent_name":"Zumbi"}

data: {"type":"thinking","message":"Zumbi está pensando..."}

data: {"type":"chunk","content":"Entendi seu","agent_id":"zumbi"}

data: {"type":"chunk","content":"pedido. Como","agent_id":"zumbi"}

data: {"type":"chunk","content":"Zumbi dos","agent_id":"zumbi"}

data: {"type":"chunk","content":"Palmares, meu","agent_id":"zumbi"}

... mais chunks ...

data: {"type":"complete","agent_id":"zumbi","agent_name":"Zumbi","suggested_actions":["start_investigation","learn_more"]}
```

---

## Configuração Visual dos Agentes

### Mapeamento Completo

```typescript
interface AgentConfig {
  name: string;
  role: string;
  avatar: string;
  color: string;
  accentColor: string;
  icon: string;
  specialty: string;
  greeting: string;
}

const AGENT_CONFIG: Record<AgentId, AgentConfig> = {
  zumbi: {
    name: 'Zumbi dos Palmares',
    role: 'Investigador',
    avatar: '/avatars/zumbi.png',
    color: '#8B4513',        // Marrom terra
    accentColor: '#CD853F',
    icon: '🏹',
    specialty: 'Detecção de fraudes e irregularidades',
    greeting: 'A luta pela transparência continua!'
  },

  anita: {
    name: 'Anita Garibaldi',
    role: 'Analista',
    avatar: '/avatars/anita.png',
    color: '#B22222',        // Vermelho
    accentColor: '#DC143C',
    icon: '📊',
    specialty: 'Análise de padrões e tendências',
    greeting: 'Heroína dos dois mundos, a seu serviço!'
  },

  drummond: {
    name: 'Carlos Drummond de Andrade',
    role: 'Comunicador',
    avatar: '/avatars/drummond.png',
    color: '#2F4F4F',        // Cinza escuro
    accentColor: '#708090',
    icon: '✍️',
    specialty: 'Comunicação clara e acessível',
    greeting: 'E agora, cidadão?'
  },

  tiradentes: {
    name: 'Tiradentes',
    role: 'Relator',
    avatar: '/avatars/tiradentes.png',
    color: '#006400',        // Verde
    accentColor: '#228B22',
    icon: '📜',
    specialty: 'Relatórios e documentação',
    greeting: 'Liberdade ainda que tardia!'
  },

  oxossi: {
    name: 'Oxóssi',
    role: 'Caçador de Dados',
    avatar: '/avatars/oxossi.png',
    color: '#228B22',        // Verde floresta
    accentColor: '#32CD32',
    icon: '🎯',
    specialty: 'Busca em múltiplas fontes',
    greeting: 'Minhas flechas encontram qualquer dado.'
  },

  dandara: {
    name: 'Dandara dos Palmares',
    role: 'Guardiã da Justiça Social',
    avatar: '/avatars/dandara.png',
    color: '#800080',        // Roxo
    accentColor: '#9932CC',
    icon: '⚖️',
    specialty: 'Equidade e inclusão social',
    greeting: 'Lutando por justiça nos dados!'
  },

  machado: {
    name: 'Machado de Assis',
    role: 'Analista Textual',
    avatar: '/avatars/machado.png',
    color: '#4B0082',        // Índigo
    accentColor: '#6A5ACD',
    icon: '📖',
    specialty: 'Análise de documentos oficiais',
    greeting: 'As entrelinhas revelam muito...'
  },

  abaporu: {
    name: 'Abaporu',
    role: 'Orquestrador Master',
    avatar: '/avatars/abaporu.png',
    color: '#FF8C00',        // Laranja
    accentColor: '#FFA500',
    icon: '🎭',
    specialty: 'Coordenação de investigações complexas',
    greeting: 'Integrando todas as perspectivas.'
  }
};
```

### CSS Variables

```css
:root {
  /* Zumbi */
  --agent-zumbi-primary: #8B4513;
  --agent-zumbi-accent: #CD853F;

  /* Anita */
  --agent-anita-primary: #B22222;
  --agent-anita-accent: #DC143C;

  /* Drummond */
  --agent-drummond-primary: #2F4F4F;
  --agent-drummond-accent: #708090;

  /* Tiradentes */
  --agent-tiradentes-primary: #006400;
  --agent-tiradentes-accent: #228B22;

  /* Oxóssi */
  --agent-oxossi-primary: #228B22;
  --agent-oxossi-accent: #32CD32;

  /* Dandara */
  --agent-dandara-primary: #800080;
  --agent-dandara-accent: #9932CC;

  /* Machado */
  --agent-machado-primary: #4B0082;
  --agent-machado-accent: #6A5ACD;

  /* Abaporu */
  --agent-abaporu-primary: #FF8C00;
  --agent-abaporu-accent: #FFA500;
}
```

---

## Implementação React

### Hook Customizado

```tsx
import { useCallback, useState, useRef } from 'react';

interface Message {
  id: string;
  content: string;
  agent_id: string;
  agent_name: string;
  timestamp: Date;
  isUser: boolean;
}

interface ChatState {
  messages: Message[];
  currentAgent: string | null;
  isThinking: boolean;
  streamingContent: string;
  error: string | null;
}

export function useChatStream() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    currentAgent: null,
    isThinking: false,
    streamingContent: '',
    error: null
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (userMessage: string) => {
    // Cancelar request anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    // Adicionar mensagem do usuário
    const userMsg: Message = {
      id: crypto.randomUUID(),
      content: userMessage,
      agent_id: 'user',
      agent_name: 'Você',
      timestamp: new Date(),
      isUser: true
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMsg],
      error: null
    }));

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      const decoder = new TextDecoder();
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;

          try {
            const data = JSON.parse(line.slice(6));
            handleStreamEvent(data, accumulatedContent, (newContent) => {
              accumulatedContent = newContent;
            });
          } catch (e) {
            console.warn('Failed to parse SSE data:', line);
          }
        }
      }
    } catch (error) {
      if ((error as Error).name === 'AbortError') return;

      setState(prev => ({
        ...prev,
        error: (error as Error).message,
        isThinking: false
      }));
    }
  }, []);

  const handleStreamEvent = useCallback((
    data: any,
    accumulatedContent: string,
    setAccumulated: (content: string) => void
  ) => {
    switch (data.type) {
      case 'agent_selected':
        setState(prev => ({
          ...prev,
          currentAgent: data.agent_id,
          isThinking: true
        }));
        break;

      case 'thinking':
        setState(prev => ({ ...prev, isThinking: true }));
        break;

      case 'chunk':
        const newContent = accumulatedContent + data.content + ' ';
        setAccumulated(newContent);
        setState(prev => ({
          ...prev,
          isThinking: false,
          streamingContent: newContent
        }));
        break;

      case 'complete':
        const agentMsg: Message = {
          id: crypto.randomUUID(),
          content: accumulatedContent.trim(),
          agent_id: data.agent_id,
          agent_name: data.agent_name,
          timestamp: new Date(),
          isUser: false
        };

        setState(prev => ({
          ...prev,
          messages: [...prev.messages, agentMsg],
          streamingContent: '',
          isThinking: false
        }));
        break;

      case 'error':
        setState(prev => ({
          ...prev,
          error: data.message,
          isThinking: false
        }));
        break;
    }
  }, []);

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  return {
    ...state,
    sendMessage,
    cancelStream
  };
}
```

### Componentes

```tsx
// AgentAvatar.tsx
import { AGENT_CONFIG } from './agentConfig';

interface AgentAvatarProps {
  agentId: string;
  size?: 'sm' | 'md' | 'lg';
}

export function AgentAvatar({ agentId, size = 'md' }: AgentAvatarProps) {
  const config = AGENT_CONFIG[agentId] || AGENT_CONFIG.drummond;

  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-12 h-12 text-lg',
    lg: 'w-16 h-16 text-2xl'
  };

  return (
    <div
      className={`rounded-full flex items-center justify-center ${sizeClasses[size]}`}
      style={{ backgroundColor: config.color }}
      title={`${config.name} - ${config.role}`}
    >
      <span>{config.icon}</span>
    </div>
  );
}

// ThinkingIndicator.tsx
export function ThinkingIndicator({ agentId }: { agentId: string }) {
  const config = AGENT_CONFIG[agentId];

  return (
    <div className="flex items-center gap-3 p-4">
      <AgentAvatar agentId={agentId} />
      <div className="flex items-center gap-1">
        <span className="text-sm text-gray-500">
          {config.name} está pensando
        </span>
        <div className="flex gap-1">
          {[0, 1, 2].map(i => (
            <span
              key={i}
              className="w-2 h-2 rounded-full animate-bounce"
              style={{
                backgroundColor: config.color,
                animationDelay: `${i * 0.15}s`
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// MessageBubble.tsx
interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const config = message.isUser ? null : AGENT_CONFIG[message.agent_id];

  return (
    <div className={`flex gap-3 ${message.isUser ? 'flex-row-reverse' : ''}`}>
      {!message.isUser && <AgentAvatar agentId={message.agent_id} />}

      <div
        className={`max-w-[70%] rounded-lg p-4 ${
          message.isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100'
        }`}
        style={!message.isUser ? { borderLeft: `4px solid ${config?.color}` } : {}}
      >
        {!message.isUser && (
          <div className="text-xs font-semibold mb-1" style={{ color: config?.color }}>
            {config?.name} • {config?.role}
          </div>
        )}

        <div className="whitespace-pre-wrap">
          {message.content}
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1" />
          )}
        </div>
      </div>
    </div>
  );
}

// ChatContainer.tsx
export function ChatContainer() {
  const {
    messages,
    currentAgent,
    isThinking,
    streamingContent,
    error,
    sendMessage
  } = useChatStream();

  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    sendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Streaming message */}
        {streamingContent && currentAgent && (
          <MessageBubble
            message={{
              id: 'streaming',
              content: streamingContent,
              agent_id: currentAgent,
              agent_name: AGENT_CONFIG[currentAgent]?.name || 'Agente',
              timestamp: new Date(),
              isUser: false
            }}
            isStreaming
          />
        )}

        {/* Thinking indicator */}
        {isThinking && currentAgent && !streamingContent && (
          <ThinkingIndicator agentId={currentAgent} />
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-100 text-red-700 p-4 rounded-lg">
            Erro: {error}
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Digite sua mensagem..."
            className="flex-1 px-4 py-2 border rounded-lg"
            disabled={isThinking}
          />
          <button
            type="submit"
            disabled={isThinking || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
          >
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}
```

---

## Implementação Vue

### Composable

```vue
<script setup lang="ts">
// useChatStream.ts
import { ref, reactive } from 'vue';

interface Message {
  id: string;
  content: string;
  agent_id: string;
  agent_name: string;
  timestamp: Date;
  isUser: boolean;
}

export function useChatStream() {
  const messages = ref<Message[]>([]);
  const currentAgent = ref<string | null>(null);
  const isThinking = ref(false);
  const streamingContent = ref('');
  const error = ref<string | null>(null);

  let abortController: AbortController | null = null;

  async function sendMessage(userMessage: string) {
    if (abortController) {
      abortController.abort();
    }
    abortController = new AbortController();

    // Add user message
    messages.value.push({
      id: crypto.randomUUID(),
      content: userMessage,
      agent_id: 'user',
      agent_name: 'Você',
      timestamp: new Date(),
      isUser: true
    });

    error.value = null;

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
        signal: abortController.signal
      });

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader');

      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const lines = decoder.decode(value).split('\n');

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;

          const data = JSON.parse(line.slice(6));

          switch (data.type) {
            case 'agent_selected':
              currentAgent.value = data.agent_id;
              isThinking.value = true;
              break;

            case 'chunk':
              isThinking.value = false;
              accumulated += data.content + ' ';
              streamingContent.value = accumulated;
              break;

            case 'complete':
              messages.value.push({
                id: crypto.randomUUID(),
                content: accumulated.trim(),
                agent_id: data.agent_id,
                agent_name: data.agent_name,
                timestamp: new Date(),
                isUser: false
              });
              streamingContent.value = '';
              accumulated = '';
              break;

            case 'error':
              error.value = data.message;
              isThinking.value = false;
              break;
          }
        }
      }
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        error.value = (e as Error).message;
      }
    }
  }

  return {
    messages,
    currentAgent,
    isThinking,
    streamingContent,
    error,
    sendMessage
  };
}
</script>
```

---

## Tratamento de Erros

### Tipos de Erro

```typescript
// Erro de conexão
{
  "type": "error",
  "message": "Connection failed",
  "fallback_endpoint": "/api/v1/chat/message"
}

// Erro de processamento
{
  "type": "error",
  "message": "Failed to process message"
}

// Timeout
{
  "type": "error",
  "message": "Request timeout"
}
```

### Estratégias de Retry

```typescript
async function sendWithRetry(message: string, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await sendMessage(message);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * (i + 1))); // Backoff
    }
  }
}
```

### Fallback para Endpoint Síncrono

```typescript
async function sendMessage(message: string) {
  try {
    // Tentar stream primeiro
    return await sendStreamMessage(message);
  } catch (error) {
    // Fallback para endpoint síncrono
    const response = await fetch('/api/v1/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  }
}
```

---

## Boas Práticas de UX

### 1. Transição de Agente

Quando o agente muda, mostrar animação suave:

```css
.agent-transition {
  animation: fadeSlideIn 0.3s ease-out;
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 2. Indicador de Personalidade

Mostrar badge com especialidade do agente:

```tsx
<div className="agent-badge">
  <span className="icon">{config.icon}</span>
  <span className="specialty">{config.specialty}</span>
</div>
```

### 3. Cores Temáticas

Usar cores do agente atual em elementos de UI:

```tsx
<div
  className="message-bubble"
  style={{
    borderLeftColor: AGENT_CONFIG[agentId].color,
    backgroundColor: `${AGENT_CONFIG[agentId].color}10`
  }}
>
```

### 4. Loading State Personalizado

Animação única por agente:

```tsx
const thinkingMessages = {
  zumbi: 'Investigando os dados...',
  anita: 'Analisando padrões...',
  drummond: 'Compondo a resposta...',
  tiradentes: 'Preparando relatório...'
};
```

### 5. Suggested Actions

Usar `suggested_actions` do evento `complete`:

```tsx
{data.suggested_actions.map(action => (
  <button key={action} onClick={() => handleAction(action)}>
    {ACTION_LABELS[action]}
  </button>
))}

const ACTION_LABELS = {
  start_investigation: 'Iniciar Investigação',
  learn_more: 'Saber Mais',
  generate_report: 'Gerar Relatório',
  analyze_data: 'Analisar Dados'
};
```

### 6. Acessibilidade

```tsx
<div
  role="log"
  aria-live="polite"
  aria-label="Histórico de mensagens"
>
  {messages.map(msg => (
    <article
      key={msg.id}
      aria-label={`Mensagem de ${msg.agent_name}`}
    >
      {msg.content}
    </article>
  ))}
</div>
```

---

## Changelog

### v1.0.0 (2025-11-25)
- Documentação inicial
- 8 agentes com configuração visual
- Exemplos React e Vue
- Tratamento de erros
- Boas práticas de UX
