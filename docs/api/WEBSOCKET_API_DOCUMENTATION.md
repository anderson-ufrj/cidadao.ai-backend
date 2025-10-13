# 🔌 WebSocket API Documentation

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Status**: ✅ Implementado
**Versão**: 1.0.0
**Data**: Setembro 2025

## 📋 Visão Geral

A API WebSocket do Cidadão.AI permite comunicação bidirecional em tempo real para chat, notificações e atualizações de investigações.

## 🚀 Endpoints WebSocket

### 1. Chat em Tempo Real
```
ws://localhost:8000/api/v1/ws/chat/{session_id}?token={jwt_token}
```

Comunicação bidirecional com agentes de IA em tempo real.

**Parâmetros de Conexão:**
- `session_id`: ID da sessão de chat
- `token` (opcional): JWT token para autenticação

**Tipos de Mensagem:**

#### Chat Message
```json
{
  "type": "chat",
  "data": {
    "message": "Investigar contratos do ministério"
  }
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "data": {
    "agent": "processing"
  }
}
```

#### Subscribe to Investigation
```json
{
  "type": "subscribe",
  "data": {
    "investigation_id": "INV-2025-001"
  }
}
```

#### Keep-Alive
```json
{
  "type": "ping",
  "data": {}
}
```

### 2. Atualizações de Investigação
```
ws://localhost:8000/api/v1/ws/investigations/{investigation_id}?token={jwt_token}
```

Recebe atualizações em tempo real de uma investigação específica.

**Mensagens Recebidas:**
- `investigation_progress`: Progresso da investigação
- `anomaly_detected`: Nova anomalia detectada
- `agent_finding`: Descoberta de agente
- `report_ready`: Relatório pronto

## 📨 Formato de Mensagens

### Estrutura Base
```typescript
interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  id: string;
}
```

### Tipos de Resposta

#### Connection Success
```json
{
  "type": "connection",
  "data": {
    "status": "connected",
    "session_id": "abc-123",
    "message": "Conectado ao Cidadão.AI em tempo real"
  },
  "timestamp": "2025-09-16T10:30:00Z",
  "id": "msg-001"
}
```

#### Chat Response (Streaming)
```json
{
  "type": "chat",
  "data": {
    "role": "assistant",
    "content": "Vou analisar os contratos",
    "agent_id": "zumbi",
    "agent_name": "Zumbi dos Palmares",
    "chunk": true
  },
  "timestamp": "2025-09-16T10:30:05Z",
  "id": "msg-002"
}
```

#### Investigation Update
```json
{
  "type": "investigation_progress",
  "data": {
    "investigation_id": "INV-2025-001",
    "update_type": "progress",
    "progress": 45,
    "status": "analyzing_contracts",
    "message": "Analisando 1.234 contratos..."
  }
}
```

#### Anomaly Detection
```json
{
  "type": "anomaly_detected",
  "data": {
    "investigation_id": "INV-2025-001",
    "severity": "high",
    "description": "Preço 300% acima da média",
    "details": {
      "contract_id": "CNT-12345",
      "expected_value": 100000,
      "actual_value": 400000
    }
  }
}
```

## 💡 Exemplos de Uso

### JavaScript/TypeScript
```typescript
class CidadaoAIWebSocket {
  private ws: WebSocket;
  private sessionId: string;

  constructor(sessionId: string, token?: string) {
    this.sessionId = sessionId;
    const url = `ws://localhost:8000/api/v1/ws/chat/${sessionId}`;
    this.ws = new WebSocket(token ? `${url}?token=${token}` : url);

    this.ws.onopen = () => {
      console.log('Conectado ao Cidadão.AI');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  sendMessage(text: string) {
    this.ws.send(JSON.stringify({
      type: 'chat',
      data: { message: text }
    }));
  }

  subscribeToInvestigation(investigationId: string) {
    this.ws.send(JSON.stringify({
      type: 'subscribe',
      data: { investigation_id: investigationId }
    }));
  }

  private handleMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'chat':
        // Handle chat message
        break;
      case 'typing':
        // Show typing indicator
        break;
      case 'anomaly_detected':
        // Show anomaly notification
        break;
    }
  }
}
```

### React Hook
```typescript
import { useEffect, useState } from 'react';

export function useCidadaoAIWebSocket(sessionId: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket(
      `ws://localhost:8000/api/v1/ws/chat/${sessionId}`
    );

    websocket.onopen = () => {
      setIsConnected(true);
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };

    websocket.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      websocket.close();
    };
  }, [sessionId]);

  const sendMessage = (text: string) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify({
        type: 'chat',
        data: { message: text }
      }));
    }
  };

  return { sendMessage, messages, isConnected };
}
```

## 🔄 Fluxo de Reconexão

```typescript
class ReconnectingWebSocket {
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.reconnectDelay *= 2; // Exponential backoff
          this.connect();
        }, this.reconnectDelay);
      }
    };

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
    };
  }
}
```

## 🔒 Segurança

### Autenticação
- JWT token opcional via query parameter
- Validação de sessão
- Rate limiting por conexão

### Boas Práticas
1. **Sempre validar mensagens** recebidas
2. **Implementar heartbeat** para detectar desconexões
3. **Limitar tamanho** de mensagens (max 64KB)
4. **Usar HTTPS/WSS** em produção

## ⚡ Performance

### Limites
- Máximo 1000 conexões simultâneas por servidor
- Mensagens limitadas a 64KB
- Heartbeat a cada 30 segundos
- Timeout de inatividade: 5 minutos

### Otimizações
- Compressão de mensagens grandes
- Batching de notificações
- Debounce de typing indicators

## 🚨 Tratamento de Erros

### Códigos de Close
- `1000`: Fechamento normal
- `1008`: Política violada (ex: auth inválida)
- `1011`: Erro interno do servidor
- `1013`: Servidor sobrecarregado

### Mensagens de Erro
```json
{
  "type": "error",
  "data": {
    "code": "RATE_LIMIT",
    "message": "Muitas mensagens. Aguarde 60 segundos."
  }
}
```

## 📱 Mobile/PWA Considerations

### Gestão de Bateria
- Implementar backoff em reconexões
- Pausar heartbeat em background
- Usar visibility API para gerenciar conexão

### Offline Support
- Queue de mensagens local
- Sincronização ao reconectar
- Indicador de status de conexão

---

**Próximo**: [Implementação de Cache Redis](./REDIS_CACHE_IMPLEMENTATION.md)
