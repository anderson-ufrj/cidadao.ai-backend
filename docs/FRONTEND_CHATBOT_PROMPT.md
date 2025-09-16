# 🤖 Prompt Atualizado para Frontend com Chatbot

## Para Claude Code no cidadao.ai-frontend:

```
Preciso implementar a integração com o backend do Cidadão.AI incluindo um chatbot conversacional que permite aos usuários interagir naturalmente com os agentes de IA.

Contexto:
- O backend está funcionando em http://localhost:8000 (ou https://neural-thinker-cidadao-ai-backend.hf.space)
- Temos 8 agentes de IA funcionais, cada um com personalidade brasileira
- Sistema funciona em modo DEMO ou REAL (com API key do Portal da Transparência)

IMPORTANTE: Preciso implementar um CHATBOT CONVERSACIONAL além das páginas:

1. **Chatbot Interface** (componente global ou página /chat)
   - Interface de chat estilo WhatsApp/Telegram
   - Conversa natural com os agentes (Abaporu, Zumbi, etc)
   - Sugestões de perguntas rápidas
   - Mostra qual agente está respondendo
   - Integração com ações (iniciar investigação, ver relatórios)
   - Pode ser flutuante (canto inferior) ou página dedicada

2. **Fluxo Conversacional**:
   Usuário: "Quero investigar contratos suspeitos"
   Abaporu: "Claro! Vou coordenar a investigação. Qual órgão?"
   Usuário: "Ministério da Saúde"
   Zumbi: "Iniciando análise de anomalias no Min. Saúde..."
   [Mostra progresso e resultados no chat]

3. **Páginas principais** (já mencionadas):
   - Nova Investigação (/investigations/new)
   - Dashboard em Tempo Real (/investigations/[id])
   - Landing Page melhorada

4. **Integração Chat + Páginas**:
   - Chat pode redirecionar para páginas específicas
   - Páginas podem abrir chat para dúvidas
   - Contexto compartilhado entre interfaces

Exemplos completos em:
/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/docs/frontend-examples/
- ChatbotInterface.tsx (NOVO - interface completa do chatbot)
- NewInvestigationPage.tsx
- InvestigationDashboard.tsx

Features do Chatbot:
- Detecta intenção do usuário (investigar, analisar, gerar relatório)
- Mostra avatar e nome do agente respondendo
- Indicador de "digitando..." enquanto processa
- Sugestões de perguntas contextuais
- Botões de ação inline (ex: "Iniciar Investigação")
- Histórico da conversa
- Modo minimizado/expandido

Integração Backend:
- Use o endpoint /api/v1/chat para conversas
- SSE para respostas em streaming
- Contexto de investigação mantido entre mensagens

Por favor implemente primeiro o chatbot, pois é a interface mais intuitiva para os cidadãos interagirem com o sistema.
```

## 🎯 Arquitetura do Chatbot

### Componente Principal
```typescript
// components/chat/ChatbotInterface.tsx
- Interface completa do chat
- Gerenciamento de mensagens
- Detecção de intenção
- Renderização de agentes

// hooks/useChatbot.ts
- Hook para abrir/fechar chat
- Estado global do chat
- Integração com API
```

### Integração com Backend
```typescript
// Endpoint de chat
POST /api/v1/chat
{
  message: string
  context?: {
    investigationId?: string
    previousAgent?: string
  }
}

// Resposta
{
  agent: "zumbi",
  message: "Detectei 15 anomalias...",
  metadata: {
    confidence: 0.92,
    nextActions: ["view_details", "generate_report"]
  }
}
```

### Estados do Chat
1. **Idle**: Aguardando input
2. **Processing**: Agente processando
3. **Streaming**: Recebendo resposta
4. **Action**: Mostrando botões de ação

### Fluxos Conversacionais
1. **Investigação Guiada**
   - Bot pergunta órgão
   - Bot pergunta período
   - Bot confirma e inicia

2. **Consulta de Resultados**
   - Lista investigações
   - Mostra resumos
   - Permite drill-down

3. **Geração de Relatórios**
   - Escolhe formato
   - Preview no chat
   - Download direto

---

Esse chatbot tornará o sistema muito mais acessível para cidadãos comuns! 🤖💬