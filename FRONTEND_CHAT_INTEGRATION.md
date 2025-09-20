# 🤖 Guia de Integração: Chat Drummond/Maritaca AI no Frontend Next.js

## 🏗️ Arquitetura da Integração

```
Frontend Next.js → Backend API → Agente Drummond → Maritaca AI
   (Interface)     (FastAPI)    (Poeta Mineiro)   (LLM Brasileiro)
```

## 📡 Endpoints Disponíveis

### 1. Endpoint Principal (Recomendado)
```
POST https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/message
```

**Request:**
```json
{
  "message": "Olá, como posso investigar contratos públicos?",
  "session_id": "uuid-opcional",  // Mantém contexto da conversa
  "context": {}                    // Contexto adicional (opcional)
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "drummond",
  "agent_name": "Carlos Drummond de Andrade",
  "message": "Uai! Que bom falar com você...",
  "confidence": 0.95,
  "suggested_actions": ["investigar_contratos", "ver_gastos"],
  "requires_input": null,
  "metadata": {
    "intent_type": "greeting",
    "agent_version": "1.0"
  }
}
```

### 2. Endpoint Alternativo (Fallback)
```
POST https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/simple
```

**Request:**
```json
{
  "message": "Sua mensagem aqui",
  "session_id": "uuid-opcional"
}
```

**Response:**
```json
{
  "message": "Resposta do Drummond via Maritaca AI",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-09-20T20:00:00Z",
  "model_used": "sabia-3"  // ou "fallback" se Maritaca estiver offline
}
```

## 🛠️ Implementação Passo a Passo

### Passo 1: Criar o Serviço de API

```typescript
// services/cidadaoChat.service.ts

const API_URL = process.env.NEXT_PUBLIC_CIDADAO_API_URL || 
                'https://neural-thinker-cidadao-ai-backend.hf.space';

export class CidadaoChatService {
  private sessionId: string | null = null;

  async sendMessage(message: string) {
    try {
      const response = await fetch(`${API_URL}/api/v1/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: this.sessionId,
          context: {}
        }),
      });

      const data = await response.json();
      
      // Guarda o session_id para manter contexto
      if (!this.sessionId && data.session_id) {
        this.sessionId = data.session_id;
      }

      return data;
    } catch (error) {
      console.error('Erro na comunicação:', error);
      throw error;
    }
  }
}
```

### Passo 2: Hook React para Gerenciar o Chat

```typescript
// hooks/useCidadaoChat.ts

import { useState, useCallback } from 'react';
import { CidadaoChatService } from '../services/cidadaoChat.service';

const chatService = new CidadaoChatService();

export function useCidadaoChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (text: string) => {
    // Adiciona mensagem do usuário
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date()
    }]);

    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(text);
      
      // Adiciona resposta do Drummond
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        agentName: response.agent_name,
        confidence: response.confidence,
        timestamp: new Date()
      }]);

      return response;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    messages,
    sendMessage,
    isLoading
  };
}
```

### Passo 3: Componente de Chat

```tsx
// components/CidadaoChat.tsx

export function CidadaoChat() {
  const { messages, sendMessage, isLoading } = useCidadaoChat();
  const [input, setInput] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      await sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            {msg.agentName && (
              <span className="agent-name">{msg.agentName}</span>
            )}
            <p>{msg.content}</p>
          </div>
        ))}
        {isLoading && <div className="loading">Drummond está pensando...</div>}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Pergunte sobre transparência pública..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Enviar
        </button>
      </form>
    </div>
  );
}
```

## 🎯 Casos de Uso e Intents

O Drummond responde melhor a estes tipos de mensagem:

### 1. **Saudações** (IntentType.GREETING)
- "Olá", "Oi", "Bom dia", "Boa tarde"
- **Resposta**: Saudação mineira calorosa com explicação do Cidadão.AI

### 2. **Investigações** (IntentType.INVESTIGATE)
- "Quero investigar contratos de saúde"
- "Mostre gastos com educação em SP"
- **Resposta**: Direcionamento para investigação ou relatório

### 3. **Ajuda** (IntentType.HELP_REQUEST)
- "Como funciona?", "Me ajuda", "O que você faz?"
- **Resposta**: Explicação das capacidades do sistema

### 4. **Sobre o Sistema** (IntentType.ABOUT_SYSTEM)
- "O que é o Cidadão.AI?"
- "Como funciona o portal da transparência?"
- **Resposta**: Informações educativas sobre transparência

## 🔧 Configurações Importantes

### Variáveis de Ambiente (.env.local)
```bash
NEXT_PUBLIC_CIDADAO_API_URL=https://neural-thinker-cidadao-ai-backend.hf.space
```

### Headers CORS
O backend já está configurado para aceitar requisições de:
- http://localhost:3000
- https://*.vercel.app
- Seu domínio customizado

### Timeout Recomendado
```javascript
// Configure timeout de 30 segundos para a Maritaca AI
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

fetch(url, {
  signal: controller.signal,
  // ... outras configs
});
```

## 🚨 Tratamento de Erros

```typescript
async function sendMessageWithErrorHandling(message: string) {
  try {
    const response = await chatService.sendMessage(message);
    return response;
  } catch (error) {
    if (error.name === 'AbortError') {
      // Timeout - Maritaca demorou muito
      return {
        message: 'A resposta está demorando. Por favor, tente novamente.',
        agent_name: 'Sistema',
        confidence: 0
      };
    }
    
    // Outros erros
    return {
      message: 'Desculpe, estou com dificuldades técnicas no momento.',
      agent_name: 'Sistema',
      confidence: 0
    };
  }
}
```

## 📊 Monitoramento e Status

### Verificar Status do Serviço
```typescript
async function checkServiceHealth() {
  try {
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    
    console.log('Status:', data.status); // 'healthy' ou 'degraded'
    console.log('Serviços:', data.services);
    
    return data.status === 'healthy';
  } catch (error) {
    return false;
  }
}
```

### Indicador de Status no UI
```tsx
function ServiceStatus() {
  const [status, setStatus] = useState('checking');
  
  useEffect(() => {
    checkServiceHealth().then(isHealthy => {
      setStatus(isHealthy ? 'online' : 'limited');
    });
  }, []);
  
  return (
    <div className={`status-badge ${status}`}>
      {status === 'online' ? '🟢 Maritaca AI Online' : '🟡 Modo Limitado'}
    </div>
  );
}
```

## 🎨 Personalização da Interface

### Identificando o Agente
Quando a resposta vem do Drummond com Maritaca AI:
```javascript
if (response.agent_name === 'Carlos Drummond de Andrade') {
  // Mostra avatar do Drummond
  // Adiciona estilo "poético mineiro"
  // Confidence > 0.8 = Maritaca está respondendo
}
```

### Sugestões de Ações
Se `suggested_actions` estiver presente:
```tsx
{response.suggested_actions?.map(action => (
  <button 
    key={action} 
    onClick={() => handleQuickAction(action)}
    className="quick-action"
  >
    {getActionLabel(action)}
  </button>
))}
```

## 🚀 Próximos Passos

1. **Implementar o serviço** seguindo os exemplos
2. **Testar a conexão** com o endpoint de health
3. **Adicionar o componente** de chat na interface
4. **Personalizar** visual e comportamento
5. **Monitorar** logs e métricas de uso

## 📞 Suporte

- **Documentação da API**: https://neural-thinker-cidadao-ai-backend.hf.space/docs
- **Status do Serviço**: https://neural-thinker-cidadao-ai-backend.hf.space/health
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend

---

*Drummond está ansioso para conversar com os cidadãos brasileiros sobre transparência pública! 🇧🇷*