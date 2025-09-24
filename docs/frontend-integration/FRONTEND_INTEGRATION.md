# Integração Frontend - Cidadão.AI Chat com Maritaca AI

## Status Atual ✅

- **Backend**: Funcionando em https://neural-thinker-cidadao-ai-backend.hf.space
- **Maritaca AI**: Configurada e pronta para uso
- **Endpoints**: Disponíveis para integração

## Endpoints Principais

### 1. Chat Principal (com Drummond/Maritaca)
```
POST https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/message
```

**Request:**
```json
{
  "message": "Olá, como posso investigar contratos públicos?",
  "session_id": "opcional-uuid",
  "context": {}
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "agent_id": "drummond",
  "agent_name": "Carlos Drummond de Andrade",
  "message": "Resposta do agente...",
  "confidence": 0.8,
  "suggested_actions": ["investigar_contratos", "ver_gastos"],
  "metadata": {}
}
```

### 2. Chat Simplificado (Novo - Mais Confiável)
```
POST https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/simple
```

**Request:**
```json
{
  "message": "Sua mensagem aqui",
  "session_id": "opcional"
}
```

**Response:**
```json
{
  "message": "Resposta da Maritaca AI ou fallback",
  "session_id": "uuid",
  "timestamp": "2025-09-20T19:45:00Z",
  "model_used": "sabia-3" // ou "fallback"
}
```

### 3. Status do Chat
```
GET https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/simple/status
```

**Response:**
```json
{
  "maritaca_available": true,
  "api_key_configured": true,
  "timestamp": "2025-09-20T19:45:00Z"
}
```

## Exemplo de Integração no Next.js

```typescript
// services/chatService.ts
const BACKEND_URL = 'https://neural-thinker-cidadao-ai-backend.hf.space';

export interface ChatMessage {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  timestamp: string;
  model_used: string;
}

export async function sendChatMessage(message: string, sessionId?: string): Promise<ChatResponse> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/chat/simple`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Chat error:', error);
    throw error;
  }
}

// Verificar status do serviço
export async function checkChatStatus() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/chat/simple/status`);
    return await response.json();
  } catch (error) {
    console.error('Status check error:', error);
    return { maritaca_available: false, api_key_configured: false };
  }
}
```

## Componente React Exemplo

```tsx
// components/Chat.tsx
import { useState, useEffect } from 'react';
import { sendChatMessage, checkChatStatus } from '../services/chatService';

export function Chat() {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>();
  const [serviceStatus, setServiceStatus] = useState<any>();

  useEffect(() => {
    // Verificar status do serviço ao carregar
    checkChatStatus().then(setServiceStatus);
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Adicionar mensagem do usuário
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(input, sessionId);
      
      // Salvar session ID para próximas mensagens
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Adicionar resposta do bot
      setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Desculpe, ocorreu um erro. Por favor, tente novamente.' 
      }]);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  return (
    <div>
      {serviceStatus && (
        <div className="status">
          Maritaca AI: {serviceStatus.maritaca_available ? '✅' : '❌'}
        </div>
      )}
      
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Digite sua mensagem..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading}>
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
}
```

## Sugestões de Mensagens para Testar

1. **Saudações:**
   - "Olá, como você pode me ajudar?"
   - "Bom dia! O que é o Cidadão.AI?"

2. **Investigações:**
   - "Quero investigar contratos de saúde"
   - "Como posso analisar gastos com educação?"
   - "Mostre contratos do Ministério da Saúde"

3. **Ajuda:**
   - "Me ajude a entender o portal da transparência"
   - "Quais tipos de dados posso consultar?"
   - "Como funciona a detecção de anomalias?"

## Tratamento de Erros

O backend pode retornar diferentes tipos de respostas:

1. **Sucesso com Maritaca AI**: `model_used: "sabia-3"`
2. **Fallback (sem Maritaca)**: `model_used: "fallback"`
3. **Erro 500**: Sistema temporariamente indisponível
4. **Erro 422**: Dados de entrada inválidos

## Notas Importantes

1. **Session ID**: Mantenha o mesmo `session_id` para manter contexto da conversa
2. **Rate Limiting**: O backend tem limite de requisições por minuto
3. **Timeout**: Configure timeout de pelo menos 30 segundos para a Maritaca AI
4. **CORS**: Já configurado para aceitar requisições do Vercel

## Próximos Passos

1. Aguardar alguns minutos para o deploy no HuggingFace Spaces
2. Testar o endpoint `/api/v1/chat/simple` 
3. Integrar no frontend Next.js
4. Adicionar tratamento de erros e loading states
5. Implementar persistência de sessão no localStorage

## Suporte

Em caso de problemas:
1. Verifique o status em: `/api/v1/chat/simple/status`
2. Consulte os logs do HuggingFace Spaces
3. Use o endpoint fallback se a Maritaca estiver indisponível