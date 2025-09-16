// Exemplo de Interface de Chatbot Conversacional
// /app/chat/page.tsx ou como componente flutuante

"use client"

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Sparkles,
  Search,
  FileText,
  AlertCircle,
  TrendingUp,
  Brain,
  HelpCircle,
  X,
  Maximize2,
  Minimize2
} from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

// Tipos de mensagem
interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agent?: string
  metadata?: {
    type?: 'investigation' | 'analysis' | 'report' | 'help'
    investigationId?: string
    confidence?: number
    sources?: string[]
  }
}

// Agentes disponíveis para conversa
const AGENTS = {
  abaporu: { name: 'Abaporu', avatar: '🎨', role: 'Orquestrador' },
  zumbi: { name: 'Zumbi', avatar: '🔍', role: 'Investigador' },
  anita: { name: 'Anita', avatar: '📊', role: 'Analista' },
  tiradentes: { name: 'Tiradentes', avatar: '📝', role: 'Relator' },
  machado: { name: 'Machado', avatar: '📚', role: 'Textual' },
  dandara: { name: 'Dandara', avatar: '⚖️', role: 'Justiça Social' }
}

// Sugestões de perguntas
const QUICK_PROMPTS = [
  { icon: <Search className="h-4 w-4" />, text: "Investigar contratos do Ministério da Saúde" },
  { icon: <AlertCircle className="h-4 w-4" />, text: "Quais são as principais anomalias encontradas?" },
  { icon: <TrendingUp className="h-4 w-4" />, text: "Mostre análise de gastos dos últimos 6 meses" },
  { icon: <FileText className="h-4 w-4" />, text: "Gere um relatório das investigações recentes" }
]

interface ChatbotProps {
  embedded?: boolean
  defaultOpen?: boolean
}

export default function ChatbotInterface({ embedded = false, defaultOpen = true }: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Olá! Sou o assistente do Cidadão.AI. Posso ajudá-lo a investigar contratos públicos, detectar anomalias e gerar relatórios. Como posso ajudar hoje?',
      timestamp: new Date(),
      agent: 'abaporu'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isMinimized, setIsMinimized] = useState(!defaultOpen)
  const [isTyping, setIsTyping] = useState<string | null>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll para última mensagem
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  // Simular resposta do agente
  const simulateAgentResponse = async (userMessage: string) => {
    setIsLoading(true)
    
    // Detectar intenção básica
    const intent = detectIntent(userMessage)
    
    // Mostrar agente "pensando"
    setIsTyping(intent.agent)
    
    // Simular delay de processamento
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Resposta baseada na intenção
    let response: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      agent: intent.agent,
      metadata: { type: intent.type }
    }

    switch (intent.type) {
      case 'investigation':
        response.content = `Entendi que você quer investigar contratos. Vou acionar o Zumbi dos Palmares para analisar anomalias. 

Para uma investigação completa, preciso saber:
- Qual órgão você quer investigar?
- Qual período deseja analisar?

Você pode clicar em "Iniciar Nova Investigação" ou me fornecer esses dados aqui.`
        response.metadata!.confidence = 0.92
        break

      case 'analysis':
        response.content = `A Anita Garibaldi analisou os padrões recentes e encontrou:

📊 **Resumo das Anomalias:**
• 15 contratos com sobrepreço (média 180% acima)
• 3 fornecedores concentram 67% dos contratos
• Pico de gastos em dezembro (3x a média)

🚨 **Risco**: Alto

Gostaria de ver os detalhes de alguma anomalia específica?`
        response.metadata!.confidence = 0.88
        break

      case 'report':
        response.content = `O Tiradentes pode gerar diferentes tipos de relatórios:

📝 **Formatos Disponíveis:**
• Resumo Executivo (1 página)
• Relatório Detalhado (completo)
• Apresentação Visual (gráficos)
• Dados Brutos (CSV/JSON)

Qual formato você prefere? Ou posso gerar um relatório padrão das últimas investigações.`
        break

      default:
        response.content = `Posso ajudar você com:

🔍 **Investigações**: Analisar contratos de qualquer órgão público
📊 **Análises**: Detectar anomalias, padrões suspeitos e irregularidades
📝 **Relatórios**: Gerar documentos detalhados dos achados
❓ **Consultas**: Responder dúvidas sobre transparência pública

O que você gostaria de fazer?`
    }

    setIsTyping(null)
    setMessages(prev => [...prev, response])
    setIsLoading(false)

    // Se foi solicitada investigação, mostrar botão de ação
    if (intent.type === 'investigation') {
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'system',
          content: 'action:start_investigation',
          timestamp: new Date()
        }])
      }, 500)
    }
  }

  // Detectar intenção simples
  const detectIntent = (message: string) => {
    const lower = message.toLowerCase()
    
    if (lower.includes('investigar') || lower.includes('analisar contratos')) {
      return { type: 'investigation' as const, agent: 'zumbi' }
    }
    if (lower.includes('anomalia') || lower.includes('irregular')) {
      return { type: 'analysis' as const, agent: 'anita' }
    }
    if (lower.includes('relatório') || lower.includes('documento')) {
      return { type: 'report' as const, agent: 'tiradentes' }
    }
    
    return { type: 'help' as const, agent: 'abaporu' }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    
    await simulateAgentResponse(input)
  }

  const handleQuickPrompt = (prompt: string) => {
    setInput(prompt)
    inputRef.current?.focus()
  }

  // Componente de mensagem
  const MessageBubble = ({ message }: { message: Message }) => {
    const isUser = message.role === 'user'
    const agent = message.agent ? AGENTS[message.agent as keyof typeof AGENTS] : null

    // Renderizar ações do sistema
    if (message.role === 'system' && message.content.startsWith('action:')) {
      const action = message.content.split(':')[1]
      if (action === 'start_investigation') {
        return (
          <div className="flex justify-center my-4">
            <Button 
              onClick={() => window.location.href = '/investigations/new'}
              className="gap-2"
            >
              <Sparkles className="h-4 w-4" />
              Iniciar Nova Investigação
            </Button>
          </div>
        )
      }
    }

    return (
      <div className={cn(
        "flex gap-3 mb-4",
        isUser ? "flex-row-reverse" : "flex-row"
      )}>
        <Avatar className="h-8 w-8 flex-shrink-0">
          {isUser ? (
            <AvatarFallback>
              <User className="h-4 w-4" />
            </AvatarFallback>
          ) : (
            <AvatarFallback>
              {agent ? agent.avatar : <Bot className="h-4 w-4" />}
            </AvatarFallback>
          )}
        </Avatar>

        <div className={cn(
          "flex flex-col gap-1 max-w-[80%]",
          isUser ? "items-end" : "items-start"
        )}>
          {!isUser && agent && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="font-medium">{agent.name}</span>
              <Badge variant="outline" className="text-xs py-0">
                {agent.role}
              </Badge>
              {message.metadata?.confidence && (
                <span className="text-xs">
                  {Math.round(message.metadata.confidence * 100)}% confiança
                </span>
              )}
            </div>
          )}

          <div className={cn(
            "rounded-lg px-4 py-2",
            isUser 
              ? "bg-primary text-primary-foreground" 
              : "bg-muted"
          )}>
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>

          <span className="text-xs text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
        </div>
      </div>
    )
  }

  // Interface flutuante ou incorporada
  const chatContent = (
    <>
      <CardHeader className="border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <CardTitle className="text-base">Assistente Cidadão.AI</CardTitle>
            {isTyping && (
              <Badge variant="secondary" className="text-xs">
                {AGENTS[isTyping as keyof typeof AGENTS]?.name} está digitando...
              </Badge>
            )}
          </div>
          {!embedded && (
            <div className="flex items-center gap-1">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => toast.info("Ajuda: Digite sua pergunta ou use as sugestões rápidas")}
                    >
                      <HelpCircle className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Ajuda</TooltipContent>
                </Tooltip>
              </TooltipProvider>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => setIsMinimized(!isMinimized)}
              >
                {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
              </Button>
            </div>
          )}
        </div>
      </CardHeader>

      {!isMinimized && (
        <>
          <CardContent className="p-0">
            <ScrollArea className="h-[400px] p-4" ref={scrollAreaRef}>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-muted-foreground mb-4">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Processando...</span>
                </div>
              )}
            </ScrollArea>

            {/* Sugestões rápidas */}
            {messages.length === 1 && (
              <div className="px-4 pb-2">
                <p className="text-xs text-muted-foreground mb-2">Sugestões rápidas:</p>
                <div className="flex flex-wrap gap-2">
                  {QUICK_PROMPTS.map((prompt, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => handleQuickPrompt(prompt.text)}
                    >
                      {prompt.icon}
                      <span className="ml-1">{prompt.text}</span>
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </CardContent>

          <div className="border-t p-4">
            <form 
              onSubmit={(e) => {
                e.preventDefault()
                handleSend()
              }}
              className="flex gap-2"
            >
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Digite sua pergunta..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button type="submit" disabled={!input.trim() || isLoading}>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </form>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              Modo: {process.env.NEXT_PUBLIC_DEMO_MODE === 'true' ? '[DEMO]' : 'Produção'} • 
              Powered by Cidadão.AI
            </p>
          </div>
        </>
      )}
    </>
  )

  // Renderizar como card flutuante ou incorporado
  if (embedded) {
    return <Card className="w-full">{chatContent}</Card>
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-[400px]">
      <Card className="shadow-xl">
        {chatContent}
      </Card>
    </div>
  )
}

// Hook para usar o chatbot em qualquer página
export function useChatbot() {
  const [isOpen, setIsOpen] = useState(false)
  
  const Chatbot = () => (
    isOpen ? <ChatbotInterface embedded={false} defaultOpen={true} /> : null
  )
  
  const toggleChatbot = () => setIsOpen(!isOpen)
  
  return { Chatbot, toggleChatbot, isOpen }
}