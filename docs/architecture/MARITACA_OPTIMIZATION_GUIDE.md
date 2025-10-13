# 🚀 Guia de Otimização Maritaca AI - Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## Resumo das Melhorias

### 1. Novo Endpoint Otimizado
- **URL**: `/api/v1/chat/optimized`
- **Modelo**: Sabiazinho-3 (mais econômico)
- **Persona**: Carlos Drummond de Andrade
- **Economia**: ~40-50% menor custo por requisição

### 2. Comparação de Modelos

| Modelo | Custo | Qualidade | Tempo Resposta | Uso Recomendado |
|--------|-------|-----------|----------------|-----------------|
| Sabiazinho-3 | 💰 | ⭐⭐⭐⭐ | 1-5s | Conversas gerais, saudações |
| Sabiá-3 | 💰💰💰 | ⭐⭐⭐⭐⭐ | 3-15s | Análises complexas |

### 3. Endpoints Disponíveis

```bash
# 1. Simple (Sabiá-3) - FUNCIONANDO 100%
POST /api/v1/chat/simple

# 2. Stable (Multi-fallback) - NOVO
POST /api/v1/chat/stable

# 3. Optimized (Sabiazinho-3 + Drummond) - NOVO
POST /api/v1/chat/optimized
```

## Integração Frontend - Versão Otimizada

### Serviço de Chat Atualizado

```typescript
// services/chatService.ts
export interface ChatEndpoint {
  url: string;
  name: string;
  priority: number;
  model: string;
}

export class ChatService {
  private readonly API_URL = process.env.NEXT_PUBLIC_API_URL

  private endpoints: ChatEndpoint[] = [
    {
      url: '/api/v1/chat/optimized',
      name: 'Optimized (Sabiazinho)',
      priority: 1,
      model: 'sabiazinho-3'
    },
    {
      url: '/api/v1/chat/simple',
      name: 'Simple (Sabiá-3)',
      priority: 2,
      model: 'sabia-3'
    },
    {
      url: '/api/v1/chat/stable',
      name: 'Stable (Fallback)',
      priority: 3,
      model: 'mixed'
    }
  ]

  async sendMessage(
    message: string,
    options?: {
      preferredModel?: 'economic' | 'quality';
      useDrummond?: boolean;
    }
  ): Promise<ChatResponse> {
    const sessionId = `session_${Date.now()}`

    // Select endpoint based on preference
    let selectedEndpoints = [...this.endpoints]

    if (options?.preferredModel === 'economic') {
      // Prioritize Sabiazinho
      selectedEndpoints.sort((a, b) =>
        a.model === 'sabiazinho-3' ? -1 : 1
      )
    } else if (options?.preferredModel === 'quality') {
      // Prioritize Sabiá-3
      selectedEndpoints.sort((a, b) =>
        a.model === 'sabia-3' ? -1 : 1
      )
    }

    // Try endpoints in order
    for (const endpoint of selectedEndpoints) {
      try {
        const body: any = { message, session_id: sessionId }

        // Add Drummond flag for optimized endpoint
        if (endpoint.url.includes('optimized')) {
          body.use_drummond = options?.useDrummond ?? true
        }

        const response = await fetch(`${this.API_URL}${endpoint.url}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        })

        if (response.ok) {
          const data = await response.json()
          console.log(`✅ Success with ${endpoint.name}`)
          return data
        }
      } catch (error) {
        console.warn(`Failed ${endpoint.name}:`, error)
      }
    }

    // Ultimate fallback
    return {
      message: 'Desculpe, estou temporariamente indisponível.',
      session_id: sessionId,
      agent_name: 'Sistema',
      agent_id: 'system',
      confidence: 0,
      metadata: { fallback: true }
    }
  }

  // Analyze message to decide best model
  analyzeComplexity(message: string): 'simple' | 'complex' {
    const complexKeywords = [
      'analise', 'investigue', 'compare', 'tendência',
      'padrão', 'anomalia', 'detalhe', 'relatório'
    ]

    const hasComplexKeyword = complexKeywords.some(
      keyword => message.toLowerCase().includes(keyword)
    )

    return hasComplexKeyword || message.length > 100
      ? 'complex'
      : 'simple'
  }
}
```

### Componente Inteligente

```tsx
// components/SmartChat.tsx
export function SmartChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [modelPreference, setModelPreference] = useState<'auto' | 'economic' | 'quality'>('auto')
  const chatService = new ChatService()

  const handleSendMessage = async (text: string) => {
    // Add user message
    const userMessage = createUserMessage(text)
    setMessages(prev => [...prev, userMessage])

    // Analyze complexity for auto mode
    let preference: 'economic' | 'quality' | undefined

    if (modelPreference === 'auto') {
      const complexity = chatService.analyzeComplexity(text)
      preference = complexity === 'simple' ? 'economic' : 'quality'
    } else if (modelPreference !== 'auto') {
      preference = modelPreference
    }

    // Send with appropriate model
    const response = await chatService.sendMessage(text, {
      preferredModel: preference,
      useDrummond: true // Enable cultural persona
    })

    // Add response
    const assistantMessage = {
      ...createAssistantMessage(response),
      metadata: {
        ...response.metadata,
        model_preference: preference,
        actual_model: response.model_used
      }
    }

    setMessages(prev => [...prev, assistantMessage])

    // Log for monitoring
    logChatMetrics({
      model_used: response.model_used,
      response_time: response.metadata?.response_time_ms,
      tokens: response.metadata?.tokens_used,
      success: true
    })
  }

  return (
    <div className="smart-chat">
      {/* Model preference selector */}
      <div className="model-selector">
        <label>Modo:</label>
        <select
          value={modelPreference}
          onChange={(e) => setModelPreference(e.target.value as any)}
        >
          <option value="auto">Automático</option>
          <option value="economic">Econômico (Sabiazinho)</option>
          <option value="quality">Qualidade (Sabiá-3)</option>
        </select>
      </div>

      {/* Chat messages */}
      <MessageList messages={messages} />

      {/* Input */}
      <ChatInput onSend={handleSendMessage} />

      {/* Status indicator */}
      <ChatStatus
        lastModel={messages[messages.length - 1]?.metadata?.actual_model}
        preference={modelPreference}
      />
    </div>
  )
}
```

## Otimizações de Custo

### 1. Cache Inteligente
```typescript
class CachedChatService extends ChatService {
  private cache = new Map<string, CachedResponse>()

  async sendMessage(message: string, options?: any) {
    // Check cache for common questions
    const cacheKey = this.normalizeMessage(message)
    const cached = this.cache.get(cacheKey)

    if (cached && !this.isExpired(cached)) {
      return {
        ...cached.response,
        metadata: {
          ...cached.response.metadata,
          from_cache: true
        }
      }
    }

    // Get fresh response
    const response = await super.sendMessage(message, options)

    // Cache if successful
    if (response.confidence > 0.8) {
      this.cache.set(cacheKey, {
        response,
        timestamp: Date.now()
      })
    }

    return response
  }
}
```

### 2. Batching de Requisições
```typescript
class BatchedChatService extends ChatService {
  private queue: QueuedMessage[] = []
  private timer: NodeJS.Timeout | null = null

  async sendMessage(message: string, options?: any) {
    return new Promise((resolve) => {
      this.queue.push({ message, options, resolve })

      if (!this.timer) {
        this.timer = setTimeout(() => this.processBatch(), 100)
      }
    })
  }

  private async processBatch() {
    const batch = this.queue.splice(0, 5) // Max 5 per batch

    // Send all at once (if API supports)
    const responses = await this.sendBatch(batch)

    // Resolve individual promises
    batch.forEach((item, index) => {
      item.resolve(responses[index])
    })

    this.timer = null
  }
}
```

## Métricas e Monitoramento

```typescript
// utils/chatMetrics.ts
export class ChatMetricsCollector {
  private metrics = {
    totalRequests: 0,
    modelUsage: new Map<string, number>(),
    avgResponseTime: 0,
    totalTokens: 0,
    errorRate: 0,
    cacheHitRate: 0
  }

  recordMetric(data: ChatMetric) {
    this.metrics.totalRequests++

    // Track model usage
    const model = data.model_used || 'unknown'
    this.metrics.modelUsage.set(
      model,
      (this.metrics.modelUsage.get(model) || 0) + 1
    )

    // Update averages
    this.updateAverages(data)

    // Send to analytics (optional)
    if (window.gtag) {
      window.gtag('event', 'chat_interaction', {
        model_used: model,
        response_time: data.response_time,
        success: !data.error
      })
    }
  }

  getCostEstimate(): number {
    const sabiazinhoCost = 0.001 // per request
    const sabia3Cost = 0.003 // per request

    const sabiazinhoCount = this.metrics.modelUsage.get('sabiazinho-3') || 0
    const sabia3Count = this.metrics.modelUsage.get('sabia-3') || 0

    return (sabiazinhoCount * sabiazinhoCost) + (sabia3Count * sabia3Cost)
  }

  getReport() {
    return {
      ...this.metrics,
      estimatedCost: this.getCostEstimate(),
      modelDistribution: Object.fromEntries(this.metrics.modelUsage)
    }
  }
}
```

## Recomendações de Uso

### Para o Frontend:
1. **Perguntas Simples/Saudações**: Use Sabiazinho (economic mode)
2. **Análises Complexas**: Use Sabiá-3 (quality mode)
3. **Auto Mode**: Deixa o sistema decidir baseado na complexidade

### Economia Estimada:
- Conversas simples: 40-50% economia usando Sabiazinho
- Mix típico (70% simples, 30% complexo): ~35% economia total
- Com cache: Adicional 10-20% economia

### Próximos Passos:
1. Implementar cache para perguntas frequentes
2. Adicionar análise de sentimento para ajustar tom
3. Criar dashboards de custo em tempo real
4. A/B testing entre modelos
