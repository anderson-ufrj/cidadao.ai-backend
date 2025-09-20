// hooks/useChat.ts
import { useState, useCallback, useEffect } from 'react';
import { chatService, ChatMessage, ChatResponse } from '../services/chatService';

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  isOnline: boolean;
  maritacaAvailable: boolean;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOnline, setIsOnline] = useState(true);
  const [maritacaAvailable, setMaritacaAvailable] = useState(false);

  // Verifica status do serviço ao montar
  useEffect(() => {
    checkServiceStatus();
    
    // Verifica a cada 30 segundos
    const interval = setInterval(checkServiceStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const checkServiceStatus = async () => {
    const status = await chatService.checkStatus();
    setIsOnline(status.online);
    setMaritacaAvailable(status.maritacaAvailable);
  };

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Adiciona mensagem do usuário
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Envia para o backend
      const response: ChatResponse = await chatService.sendMessage(content);

      // Adiciona resposta do Drummond/Maritaca
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        agentName: response.agent_name,
        confidence: response.confidence,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Se há ações sugeridas, podemos processá-las
      if (response.suggested_actions?.length) {
        console.log('Ações sugeridas:', response.suggested_actions);
        // TODO: Implementar quick actions
      }

    } catch (err) {
      console.error('Erro no chat:', err);
      setError('Não foi possível enviar a mensagem. Tente novamente.');
      
      // Adiciona mensagem de erro
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
        timestamp: new Date(),
        agentName: 'Sistema',
        confidence: 0,
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    chatService.clearSession();
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    isOnline,
    maritacaAvailable,
  };
}