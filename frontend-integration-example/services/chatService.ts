// services/chatService.ts
/**
 * Serviço de integração com o backend Cidadão.AI
 * Conecta com o Drummond (Carlos Drummond de Andrade) que usa Maritaca AI
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://neural-thinker-cidadao-ai-backend.hf.space';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agentName?: string;
  confidence?: number;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  session_id: string;
  agent_id: string;
  agent_name: string;
  message: string;
  confidence: number;
  suggested_actions?: string[];
  requires_input?: Record<string, string>;
  metadata?: Record<string, any>;
}

class ChatService {
  private sessionId: string | null = null;

  /**
   * Envia mensagem para o Drummond (powered by Maritaca AI)
   */
  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: this.sessionId,
          context: {}
        } as ChatRequest),
      });

      if (!response.ok) {
        // Se o endpoint principal falhar, tenta o simplificado
        if (response.status === 500) {
          return this.sendSimpleMessage(message);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      
      // Salva o session_id para manter contexto
      if (!this.sessionId) {
        this.sessionId = data.session_id;
      }

      return data;
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      // Fallback para o endpoint simples
      return this.sendSimpleMessage(message);
    }
  }

  /**
   * Endpoint alternativo (mais simples e confiável)
   */
  private async sendSimpleMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/chat/simple`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: this.sessionId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Converte para o formato ChatResponse
      return {
        session_id: data.session_id || this.sessionId || 'temp-session',
        agent_id: 'drummond',
        agent_name: 'Carlos Drummond de Andrade',
        message: data.message,
        confidence: 0.9,
        metadata: { model_used: data.model_used }
      };
    } catch (error) {
      // Se tudo falhar, retorna resposta de erro amigável
      return {
        session_id: this.sessionId || 'error-session',
        agent_id: 'system',
        agent_name: 'Sistema',
        message: 'Desculpe, estou com dificuldades para me conectar. Por favor, tente novamente em alguns instantes.',
        confidence: 0,
        metadata: { error: true }
      };
    }
  }

  /**
   * Verifica status do serviço
   */
  async checkStatus(): Promise<{
    online: boolean;
    maritacaAvailable: boolean;
    message: string;
  }> {
    try {
      // Tenta o health check primeiro
      const healthResponse = await fetch(`${BACKEND_URL}/health`);
      const health = await healthResponse.json();

      // Tenta verificar status do chat
      const chatStatusResponse = await fetch(`${BACKEND_URL}/api/v1/chat/simple/status`);
      const chatStatus = chatStatusResponse.ok ? await chatStatusResponse.json() : null;

      return {
        online: healthResponse.ok,
        maritacaAvailable: chatStatus?.maritaca_available || false,
        message: health.status === 'healthy' 
          ? '✅ Todos os sistemas operacionais' 
          : '⚠️ Sistema operacional com limitações'
      };
    } catch (error) {
      return {
        online: false,
        maritacaAvailable: false,
        message: '❌ Sistema offline'
      };
    }
  }

  /**
   * Limpa a sessão atual
   */
  clearSession() {
    this.sessionId = null;
  }
}

// Exporta instância única (singleton)
export const chatService = new ChatService();