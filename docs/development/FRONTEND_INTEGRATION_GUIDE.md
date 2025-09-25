# 🚀 Guia Completo de Integração Frontend - Cidadão.AI Backend API

**Versão**: 1.0.0  
**Última Atualização**: Janeiro 2025  
**Backend URL**: https://neural-thinker-cidadao-ai-backend.hf.space/  
**Documentação Interativa**: https://neural-thinker-cidadao-ai-backend.hf.space/docs

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Configuração Inicial](#configuração-inicial)
3. [Autenticação](#autenticação)
4. [Endpoints Principais](#endpoints-principais)
5. [WebSockets e Real-time](#websockets-e-real-time)
6. [Exemplos de Implementação](#exemplos-de-implementação)
7. [TypeScript Interfaces](#typescript-interfaces)
8. [Tratamento de Erros](#tratamento-de-erros)
9. [Rate Limiting](#rate-limiting)
10. [Boas Práticas](#boas-práticas)

---

## 🎯 Visão Geral

O Cidadão.AI é uma plataforma multi-agente de IA para análise de transparência governamental brasileira. O backend fornece APIs RESTful, WebSockets e Server-Sent Events (SSE) para comunicação em tempo real.

### Características Principais
- **Autenticação JWT** com refresh tokens
- **Rate Limiting** por tiers (Free, Basic, Premium, Enterprise)
- **WebSockets** para comunicação bidirecional
- **SSE** para streaming de respostas
- **17 Agentes de IA** especializados com identidades brasileiras
- **Cache otimizado** com hit rate >90%
- **Tempo de resposta** <2s para agentes

### Base URLs
```typescript
// Produção
const API_BASE_URL = 'https://neural-thinker-cidadao-ai-backend.hf.space'

// Development (local)
const API_BASE_URL_DEV = 'http://localhost:8000'

// WebSocket
const WS_BASE_URL = 'wss://neural-thinker-cidadao-ai-backend.hf.space'
const WS_BASE_URL_DEV = 'ws://localhost:8000'
```

---

## 🔧 Configuração Inicial

### 1. Instalação de Dependências

```bash
# Axios para requisições HTTP
npm install axios

# Socket.io para WebSockets (opcional - pode usar native WebSocket)
npm install socket.io-client

# Event Source Polyfill para SSE
npm install eventsource

# TypeScript types
npm install -D @types/eventsource
```

### 2. Configuração do Cliente HTTP

```typescript
// utils/api-client.ts
import axios, { AxiosInstance } from 'axios'

class ApiClient {
  private client: AxiosInstance
  private refreshingToken: Promise<string> | null = null

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://neural-thinker-cidadao-ai-backend.hf.space',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 segundos
    })

    // Request interceptor para adicionar token
    this.client.interceptors.request.use(
      async (config) => {
        const token = this.getAccessToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor para refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          
          try {
            await this.refreshToken()
            const newToken = this.getAccessToken()
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return this.client(originalRequest)
          } catch (refreshError) {
            // Redirecionar para login
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  private getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token')
  }

  private async refreshToken(): Promise<string> {
    if (this.refreshingToken) {
      return this.refreshingToken
    }

    this.refreshingToken = this.client
      .post('/auth/refresh', {
        refresh_token: this.getRefreshToken(),
      })
      .then((response) => {
        const { access_token, refresh_token } = response.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        this.refreshingToken = null
        return access_token
      })
      .catch((error) => {
        this.refreshingToken = null
        throw error
      })

    return this.refreshingToken
  }

  // Métodos públicos
  async get<T>(url: string, config?: any): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: any): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response.data
  }
}

export const apiClient = new ApiClient()
```

---

## 🔐 Autenticação

### Fluxo de Autenticação

1. **Login** → Recebe access_token e refresh_token
2. **Armazenamento** → Salvar tokens no localStorage/cookies seguros
3. **Uso** → Enviar access_token no header Authorization
4. **Refresh** → Quando access_token expira, usar refresh_token
5. **Logout** → Limpar tokens e chamar endpoint de logout

### Endpoints de Autenticação

#### 1. Login
```typescript
// POST /auth/login
interface LoginRequest {
  email: string
  password: string
}

interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    email: string
    name: string
    role: string
    is_active: boolean
  }
}

// Exemplo de uso
async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', {
    email,
    password
  })
  
  // Salvar tokens
  localStorage.setItem('access_token', response.access_token)
  localStorage.setItem('refresh_token', response.refresh_token)
  localStorage.setItem('user', JSON.stringify(response.user))
  
  return response
}
```

#### 2. Refresh Token
```typescript
// POST /auth/refresh
interface RefreshRequest {
  refresh_token: string
}

interface RefreshResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

async function refreshAccessToken(): Promise<RefreshResponse> {
  const refreshToken = localStorage.getItem('refresh_token')
  
  const response = await apiClient.post<RefreshResponse>('/auth/refresh', {
    refresh_token: refreshToken
  })
  
  // Atualizar tokens
  localStorage.setItem('access_token', response.access_token)
  localStorage.setItem('refresh_token', response.refresh_token)
  
  return response
}
```

#### 3. Logout
```typescript
// POST /auth/logout
async function logout(): Promise<void> {
  try {
    await apiClient.post('/auth/logout')
  } finally {
    // Limpar dados locais
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    
    // Redirecionar para login
    window.location.href = '/login'
  }
}
```

#### 4. Get Current User
```typescript
// GET /auth/me
interface UserInfo {
  id: string
  email: string
  name: string
  role: string
  is_active: boolean
  created_at: string
  last_login: string
}

async function getCurrentUser(): Promise<UserInfo> {
  return await apiClient.get<UserInfo>('/auth/me')
}
```

---

## 📡 Endpoints Principais

### 1. Chat API

#### Enviar Mensagem
```typescript
// POST /api/v1/chat/message
interface ChatMessageRequest {
  message: string
  session_id?: string  // Opcional, será criado se não fornecido
  context?: Record<string, any>
}

interface ChatMessageResponse {
  response: string
  session_id: string
  message_id: string
  agent_used: string
  processing_time: number
  suggestions?: string[]
}

async function sendChatMessage(message: string, sessionId?: string): Promise<ChatMessageResponse> {
  return await apiClient.post<ChatMessageResponse>('/api/v1/chat/message', {
    message,
    session_id: sessionId
  })
}
```

#### Stream de Resposta (SSE)
```typescript
// POST /api/v1/chat/stream
interface StreamToken {
  type: 'token' | 'error' | 'complete'
  content?: string
  error?: string
  metadata?: {
    agent: string
    processing_time?: number
  }
}

function streamChatMessage(message: string, sessionId?: string): EventSource {
  const token = localStorage.getItem('access_token')
  const url = `${API_BASE_URL}/api/v1/chat/stream?token=${token}`
  
  const eventSource = new EventSource(url, {
    headers: {
      'Content-Type': 'application/json',
    }
  })
  
  // Enviar mensagem inicial
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      session_id: sessionId
    })
  })
  
  return eventSource
}

// Uso do SSE
const eventSource = streamChatMessage('Analise os contratos de 2024', sessionId)

eventSource.onmessage = (event) => {
  const data: StreamToken = JSON.parse(event.data)
  
  switch (data.type) {
    case 'token':
      // Adicionar token à resposta
      setResponse(prev => prev + data.content)
      break
    case 'complete':
      // Resposta completa
      eventSource.close()
      break
    case 'error':
      console.error('Stream error:', data.error)
      eventSource.close()
      break
  }
}

eventSource.onerror = (error) => {
  console.error('SSE Error:', error)
  eventSource.close()
}
```

#### Histórico de Chat
```typescript
// GET /api/v1/chat/history/{session_id}/paginated
interface PaginatedChatHistory {
  messages: ChatMessage[]
  total: number
  page: number
  page_size: number
  has_next: boolean
  has_previous: boolean
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  agent_used?: string
  metadata?: Record<string, any>
}

async function getChatHistory(
  sessionId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<PaginatedChatHistory> {
  return await apiClient.get<PaginatedChatHistory>(
    `/api/v1/chat/history/${sessionId}/paginated`,
    {
      params: { page, page_size: pageSize }
    }
  )
}
```

#### Sugestões Rápidas
```typescript
// GET /api/v1/chat/suggestions
interface ChatSuggestion {
  id: string
  text: string
  category: 'investigation' | 'analysis' | 'report' | 'general'
  icon?: string
}

async function getChatSuggestions(context?: string): Promise<ChatSuggestion[]> {
  return await apiClient.get<ChatSuggestion[]>('/api/v1/chat/suggestions', {
    params: { context }
  })
}
```

### 2. Agentes de IA

#### Zumbi dos Palmares - Detecção de Anomalias
```typescript
// POST /api/v1/agents/zumbi
interface ZumbiRequest {
  data: {
    contract_id?: string
    vendor_name?: string
    amount?: number
    date?: string
    description?: string
    [key: string]: any
  }
  analysis_type?: 'full' | 'quick' | 'pattern'
}

interface AnomalyResult {
  anomaly_score: number  // 0-1
  anomaly_type: string[]
  confidence: number
  severity: 'low' | 'medium' | 'high' | 'critical'
  details: {
    statistical_analysis: Record<string, any>
    pattern_analysis: Record<string, any>
    spectral_analysis?: Record<string, any>
  }
  recommendations: string[]
  visualizations?: {
    type: string
    data: any
  }[]
}

async function detectAnomalies(data: any): Promise<AnomalyResult> {
  return await apiClient.post<AnomalyResult>('/api/v1/agents/zumbi', {
    data,
    analysis_type: 'full'
  })
}
```

#### Status dos Agentes
```typescript
// GET /api/v1/agents/status
interface AgentStatus {
  agent_id: string
  name: string
  status: 'idle' | 'processing' | 'error' | 'maintenance'
  health: {
    cpu_usage: number
    memory_usage: number
    response_time_ms: number
    success_rate: number
  }
  capabilities: string[]
  last_active: string
}

async function getAgentsStatus(): Promise<AgentStatus[]> {
  return await apiClient.get<AgentStatus[]>('/api/v1/agents/status')
}
```

### 3. Investigações

#### Iniciar Investigação
```typescript
// POST /api/v1/investigations/start
interface StartInvestigationRequest {
  title: string
  description: string
  type: 'contract' | 'vendor' | 'pattern' | 'general'
  parameters: {
    date_range?: {
      start: string
      end: string
    }
    vendor_ids?: string[]
    contract_ids?: string[]
    amount_range?: {
      min: number
      max: number
    }
    keywords?: string[]
    [key: string]: any
  }
  agents?: string[]  // Agentes específicos para usar
  priority?: 'low' | 'medium' | 'high' | 'critical'
}

interface Investigation {
  id: string
  title: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number  // 0-100
  created_at: string
  updated_at: string
  estimated_completion: string
  results?: InvestigationResults
}

async function startInvestigation(
  request: StartInvestigationRequest
): Promise<Investigation> {
  return await apiClient.post<Investigation>('/api/v1/investigations/start', request)
}
```

#### Acompanhar Investigação
```typescript
// GET /api/v1/investigations/{id}
async function getInvestigation(id: string): Promise<Investigation> {
  return await apiClient.get<Investigation>(`/api/v1/investigations/${id}`)
}

// GET /api/v1/investigations/{id}/results
interface InvestigationResults {
  summary: string
  findings: Finding[]
  anomalies: AnomalyResult[]
  patterns: Pattern[]
  recommendations: string[]
  risk_score: number
  confidence: number
  visualizations: Visualization[]
  raw_data?: any
}

interface Finding {
  id: string
  type: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  evidence: any[]
  agent: string
}

async function getInvestigationResults(id: string): Promise<InvestigationResults> {
  return await apiClient.get<InvestigationResults>(`/api/v1/investigations/${id}/results`)
}
```

### 4. Análises

#### Análise de Padrões
```typescript
// POST /api/v1/analysis/patterns
interface PatternAnalysisRequest {
  data: any[]
  analysis_config?: {
    min_support?: number
    min_confidence?: number
    algorithms?: ('apriori' | 'fpgrowth' | 'eclat')[]
  }
  time_range?: {
    start: string
    end: string
  }
}

interface PatternAnalysisResponse {
  patterns: Pattern[]
  statistics: {
    total_patterns: number
    avg_confidence: number
    processing_time: number
  }
  visualizations: Visualization[]
}

interface Pattern {
  id: string
  pattern: string[]
  support: number
  confidence: number
  lift: number
  occurrences: number
  examples: any[]
}
```

#### Análise de Tendências
```typescript
// POST /api/v1/analysis/trends
interface TrendAnalysisRequest {
  metric: string
  data: {
    timestamp: string
    value: number
    metadata?: any
  }[]
  analysis_type: 'linear' | 'seasonal' | 'polynomial' | 'all'
  forecast_periods?: number
}

interface TrendAnalysisResponse {
  current_trend: 'increasing' | 'decreasing' | 'stable'
  trend_strength: number
  forecast: {
    timestamp: string
    value: number
    confidence_interval: {
      lower: number
      upper: number
    }
  }[]
  seasonality?: {
    period: string
    strength: number
  }
  change_points: {
    timestamp: string
    significance: number
  }[]
}
```

### 5. Relatórios

#### Gerar Relatório
```typescript
// POST /api/v1/reports/generate
interface GenerateReportRequest {
  investigation_id?: string
  template: 'executive_summary' | 'detailed' | 'technical' | 'compliance'
  format: 'pdf' | 'html' | 'markdown' | 'docx'
  sections?: string[]
  include_visualizations?: boolean
  language?: 'pt-BR' | 'en-US'
}

interface Report {
  id: string
  title: string
  status: 'generating' | 'ready' | 'failed'
  format: string
  size_bytes: number
  download_url?: string
  preview_url?: string
  created_at: string
  expires_at: string
}

async function generateReport(request: GenerateReportRequest): Promise<Report> {
  return await apiClient.post<Report>('/api/v1/reports/generate', request)
}
```

#### Download Relatório
```typescript
// GET /api/v1/reports/{id}/download
async function downloadReport(reportId: string): Promise<Blob> {
  const response = await apiClient.get(`/api/v1/reports/${reportId}/download`, {
    responseType: 'blob'
  })
  return response
}

// Exemplo de uso
const blob = await downloadReport(reportId)
const url = window.URL.createObjectURL(blob)
const a = document.createElement('a')
a.href = url
a.download = `relatorio-${reportId}.pdf`
document.body.appendChild(a)
a.click()
window.URL.revokeObjectURL(url)
```

---

## 🔄 WebSockets e Real-time

### Configuração do WebSocket Client

```typescript
// utils/websocket-client.ts
export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private heartbeatInterval: NodeJS.Timeout | null = null
  private eventHandlers: Map<string, Set<Function>> = new Map()

  constructor(private baseUrl: string) {}

  connect(endpoint: string, token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = `${this.baseUrl}${endpoint}?token=${token}`
      
      try {
        this.ws = new WebSocket(url)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.handleMessage(data)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.stopHeartbeat()
          this.handleReconnect(endpoint, token)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private handleMessage(data: any) {
    const { type, payload } = data
    
    const handlers = this.eventHandlers.get(type)
    if (handlers) {
      handlers.forEach(handler => handler(payload))
    }
    
    // Handler global
    const globalHandlers = this.eventHandlers.get('*')
    if (globalHandlers) {
      globalHandlers.forEach(handler => handler(data))
    }
  }

  on(event: string, handler: Function) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set())
    }
    this.eventHandlers.get(event)!.add(handler)
  }

  off(event: string, handler: Function) {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  send(type: string, payload: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send('ping', { timestamp: Date.now() })
    }, 30000) // 30 segundos
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private handleReconnect(endpoint: string, token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
      
      console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`)
      
      setTimeout(() => {
        this.connect(endpoint, token)
      }, delay)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.stopHeartbeat()
  }
}
```

### WebSocket para Chat

```typescript
// hooks/useWebSocketChat.ts
import { useEffect, useRef, useState } from 'react'
import { WebSocketClient } from '@/utils/websocket-client'

interface WebSocketMessage {
  type: 'message' | 'typing' | 'user_joined' | 'user_left' | 'error'
  payload: any
}

export function useWebSocketChat(sessionId: string) {
  const [messages, setMessages] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [typingUsers, setTypingUsers] = useState<string[]>([])
  const wsClient = useRef<WebSocketClient>()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token || !sessionId) return

    wsClient.current = new WebSocketClient(
      process.env.NEXT_PUBLIC_WS_URL || 'wss://neural-thinker-cidadao-ai-backend.hf.space'
    )

    // Conectar ao WebSocket
    wsClient.current.connect(`/api/v1/ws/chat/${sessionId}`, token)
      .then(() => {
        setIsConnected(true)
      })
      .catch((error) => {
        console.error('Failed to connect to WebSocket:', error)
      })

    // Configurar event handlers
    wsClient.current.on('message', (payload: any) => {
      setMessages(prev => [...prev, payload])
    })

    wsClient.current.on('typing', (payload: { user_id: string, is_typing: boolean }) => {
      setTypingUsers(prev => {
        if (payload.is_typing) {
          return [...prev, payload.user_id]
        } else {
          return prev.filter(id => id !== payload.user_id)
        }
      })
    })

    wsClient.current.on('error', (payload: any) => {
      console.error('WebSocket error:', payload)
    })

    // Cleanup
    return () => {
      if (wsClient.current) {
        wsClient.current.disconnect()
      }
    }
  }, [sessionId])

  const sendMessage = (message: string) => {
    if (wsClient.current && isConnected) {
      wsClient.current.send('message', {
        content: message,
        timestamp: new Date().toISOString()
      })
    }
  }

  const sendTypingIndicator = (isTyping: boolean) => {
    if (wsClient.current && isConnected) {
      wsClient.current.send('typing', { is_typing: isTyping })
    }
  }

  return {
    messages,
    isConnected,
    typingUsers,
    sendMessage,
    sendTypingIndicator
  }
}
```

### WebSocket para Investigações

```typescript
// hooks/useInvestigationWebSocket.ts
export function useInvestigationWebSocket(investigationId: string) {
  const [status, setStatus] = useState<string>('pending')
  const [progress, setProgress] = useState(0)
  const [findings, setFindings] = useState<any[]>([])
  const [logs, setLogs] = useState<string[]>([])
  
  useEffect(() => {
    if (!investigationId) return
    
    const token = localStorage.getItem('access_token')
    const wsClient = new WebSocketClient(process.env.NEXT_PUBLIC_WS_URL!)
    
    wsClient.connect(`/api/v1/ws/investigations/${investigationId}`, token!)
      .then(() => {
        console.log('Connected to investigation WebSocket')
      })
    
    wsClient.on('status_update', (payload: { status: string, progress: number }) => {
      setStatus(payload.status)
      setProgress(payload.progress)
    })
    
    wsClient.on('finding', (payload: any) => {
      setFindings(prev => [...prev, payload])
    })
    
    wsClient.on('log', (payload: { message: string, level: string }) => {
      setLogs(prev => [...prev, `[${payload.level}] ${payload.message}`])
    })
    
    wsClient.on('complete', (payload: { results: any }) => {
      setStatus('completed')
      setProgress(100)
      // Processar resultados finais
    })
    
    return () => {
      wsClient.disconnect()
    }
  }, [investigationId])
  
  return { status, progress, findings, logs }
}
```

---

## 💻 Exemplos de Implementação

### 1. Componente de Chat Completo

```typescript
// components/Chat/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react'
import { useWebSocketChat } from '@/hooks/useWebSocketChat'
import { apiClient } from '@/utils/api-client'

interface ChatInterfaceProps {
  sessionId?: string
}

export function ChatInterface({ sessionId: initialSessionId }: ChatInterfaceProps) {
  const [sessionId, setSessionId] = useState(initialSessionId || '')
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { 
    messages: wsMessages,
    isConnected,
    sendMessage: wsSendMessage,
    sendTypingIndicator
  } = useWebSocketChat(sessionId)
  
  // Carregar histórico ao montar
  useEffect(() => {
    if (sessionId) {
      loadChatHistory()
    }
  }, [sessionId])
  
  // Scroll automático
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, wsMessages])
  
  const loadChatHistory = async () => {
    try {
      const history = await apiClient.get(
        `/api/v1/chat/history/${sessionId}/paginated`
      )
      setMessages(history.messages)
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }
  
  const sendMessage = async () => {
    if (!input.trim()) return
    
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    
    try {
      // Se WebSocket conectado, usar WebSocket
      if (isConnected) {
        wsSendMessage(input)
      } else {
        // Senão, usar API REST
        const response = await apiClient.post('/api/v1/chat/message', {
          message: input,
          session_id: sessionId
        })
        
        if (!sessionId) {
          setSessionId(response.session_id)
        }
        
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.response,
          agent_used: response.agent_used,
          timestamp: new Date().toISOString()
        }])
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      // Mostrar erro ao usuário
    } finally {
      setIsLoading(false)
    }
  }
  
  const streamMessage = () => {
    if (!input.trim()) return
    
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsStreaming(true)
    
    let assistantMessage = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true
    }
    
    setMessages(prev => [...prev, assistantMessage])
    
    // Usar SSE para streaming
    const eventSource = streamChatMessage(input, sessionId)
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'token') {
        assistantMessage.content += data.content
        setMessages(prev => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1] = { ...assistantMessage }
          return newMessages
        })
      } else if (data.type === 'complete') {
        assistantMessage.isStreaming = false
        assistantMessage.agent_used = data.metadata?.agent
        setMessages(prev => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1] = { ...assistantMessage }
          return newMessages
        })
        setIsStreaming(false)
        eventSource.close()
      }
    }
    
    eventSource.onerror = () => {
      setIsStreaming(false)
      eventSource.close()
    }
  }
  
  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <MessageComponent key={index} message={message} />
        ))}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value)
            sendTypingIndicator(true)
          }}
          onBlur={() => sendTypingIndicator(false)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              sendMessage()
            }
          }}
          placeholder="Digite sua mensagem..."
          disabled={isLoading || isStreaming}
        />
        
        <button 
          onClick={sendMessage}
          disabled={isLoading || isStreaming || !input.trim()}
        >
          Enviar
        </button>
        
        <button 
          onClick={streamMessage}
          disabled={isLoading || isStreaming || !input.trim()}
        >
          Stream
        </button>
      </div>
      
      {isConnected && (
        <div className="connection-status">
          <span className="status-dot online" />
          Conectado
        </div>
      )}
    </div>
  )
}
```

### 2. Dashboard de Investigações

```typescript
// components/Investigations/InvestigationsDashboard.tsx
import React, { useState, useEffect } from 'react'
import { useInvestigationWebSocket } from '@/hooks/useInvestigationWebSocket'
import { apiClient } from '@/utils/api-client'

export function InvestigationsDashboard() {
  const [investigations, setInvestigations] = useState<any[]>([])
  const [selectedInvestigation, setSelectedInvestigation] = useState<string>('')
  const [isCreating, setIsCreating] = useState(false)
  
  // Carregar investigações
  useEffect(() => {
    loadInvestigations()
  }, [])
  
  const loadInvestigations = async () => {
    try {
      const data = await apiClient.get('/api/v1/investigations/history')
      setInvestigations(data)
    } catch (error) {
      console.error('Failed to load investigations:', error)
    }
  }
  
  const createInvestigation = async (data: any) => {
    setIsCreating(true)
    try {
      const investigation = await apiClient.post('/api/v1/investigations/start', {
        title: data.title,
        description: data.description,
        type: data.type,
        parameters: data.parameters,
        priority: 'high'
      })
      
      setInvestigations(prev => [investigation, ...prev])
      setSelectedInvestigation(investigation.id)
    } catch (error) {
      console.error('Failed to create investigation:', error)
    } finally {
      setIsCreating(false)
    }
  }
  
  return (
    <div className="investigations-dashboard">
      <div className="investigations-list">
        <h2>Investigações</h2>
        <button onClick={() => setIsCreating(true)}>
          Nova Investigação
        </button>
        
        {investigations.map(inv => (
          <InvestigationCard
            key={inv.id}
            investigation={inv}
            isSelected={inv.id === selectedInvestigation}
            onClick={() => setSelectedInvestigation(inv.id)}
          />
        ))}
      </div>
      
      <div className="investigation-detail">
        {selectedInvestigation && (
          <InvestigationDetail investigationId={selectedInvestigation} />
        )}
      </div>
      
      {isCreating && (
        <CreateInvestigationModal
          onClose={() => setIsCreating(false)}
          onCreate={createInvestigation}
        />
      )}
    </div>
  )
}

// Componente de detalhe com WebSocket
function InvestigationDetail({ investigationId }: { investigationId: string }) {
  const { status, progress, findings, logs } = useInvestigationWebSocket(investigationId)
  const [results, setResults] = useState<any>(null)
  
  useEffect(() => {
    if (status === 'completed') {
      loadResults()
    }
  }, [status])
  
  const loadResults = async () => {
    try {
      const data = await apiClient.get(
        `/api/v1/investigations/${investigationId}/results`
      )
      setResults(data)
    } catch (error) {
      console.error('Failed to load results:', error)
    }
  }
  
  return (
    <div className="investigation-detail-container">
      <div className="status-header">
        <h3>Status: {status}</h3>
        <ProgressBar value={progress} />
      </div>
      
      {status === 'running' && (
        <>
          <div className="findings-section">
            <h4>Descobertas ({findings.length})</h4>
            {findings.map((finding, i) => (
              <FindingCard key={i} finding={finding} />
            ))}
          </div>
          
          <div className="logs-section">
            <h4>Logs</h4>
            <div className="logs-container">
              {logs.map((log, i) => (
                <div key={i} className="log-entry">{log}</div>
              ))}
            </div>
          </div>
        </>
      )}
      
      {status === 'completed' && results && (
        <InvestigationResults results={results} />
      )}
    </div>
  )
}
```

### 3. Hook para Análise de Dados

```typescript
// hooks/useDataAnalysis.ts
import { useState } from 'react'
import { apiClient } from '@/utils/api-client'

export function useDataAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  const analyzePatterns = async (data: any[], config?: any) => {
    setIsAnalyzing(true)
    setError(null)
    
    try {
      const response = await apiClient.post('/api/v1/analysis/patterns', {
        data,
        analysis_config: config
      })
      
      setResults(response)
      return response
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setIsAnalyzing(false)
    }
  }
  
  const analyzeTrends = async (metric: string, data: any[], options?: any) => {
    setIsAnalyzing(true)
    setError(null)
    
    try {
      const response = await apiClient.post('/api/v1/analysis/trends', {
        metric,
        data,
        ...options
      })
      
      setResults(response)
      return response
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setIsAnalyzing(false)
    }
  }
  
  const detectAnomalies = async (data: any) => {
    setIsAnalyzing(true)
    setError(null)
    
    try {
      const response = await apiClient.post('/api/v1/agents/zumbi', {
        data,
        analysis_type: 'full'
      })
      
      setResults(response)
      return response
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setIsAnalyzing(false)
    }
  }
  
  return {
    isAnalyzing,
    results,
    error,
    analyzePatterns,
    analyzeTrends,
    detectAnomalies
  }
}
```

---

## 📝 TypeScript Interfaces

### Interfaces Principais

```typescript
// types/api.ts

// Base Types
export interface ApiResponse<T> {
  data: T
  status: number
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
  has_previous: boolean
}

// User & Auth
export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'user' | 'viewer'
  is_active: boolean
  created_at: string
  last_login?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// Chat Types
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  session_id: string
  agent_used?: string
  metadata?: Record<string, any>
  attachments?: Attachment[]
}

export interface ChatSession {
  id: string
  user_id: string
  created_at: string
  updated_at: string
  message_count: number
  is_active: boolean
  context?: Record<string, any>
}

// Agent Types
export interface Agent {
  id: string
  name: string
  type: string
  description: string
  capabilities: string[]
  status: AgentStatus
  performance_metrics: AgentMetrics
}

export type AgentStatus = 'idle' | 'processing' | 'error' | 'maintenance'

export interface AgentMetrics {
  avg_response_time: number
  success_rate: number
  total_requests: number
  last_24h_requests: number
}

// Investigation Types
export interface Investigation {
  id: string
  title: string
  description: string
  type: InvestigationType
  status: InvestigationStatus
  priority: Priority
  progress: number
  user_id: string
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
  estimated_completion?: string
  results?: InvestigationResults
  error?: string
}

export type InvestigationType = 'contract' | 'vendor' | 'pattern' | 'general'
export type InvestigationStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
export type Priority = 'low' | 'medium' | 'high' | 'critical'

export interface InvestigationResults {
  summary: string
  findings: Finding[]
  anomalies: Anomaly[]
  patterns: Pattern[]
  recommendations: string[]
  risk_score: number
  confidence: number
  processing_time: number
  agents_used: string[]
  visualizations?: Visualization[]
}

export interface Finding {
  id: string
  type: string
  title: string
  description: string
  severity: Severity
  confidence: number
  evidence: Evidence[]
  detected_by: string
  detected_at: string
}

export type Severity = 'low' | 'medium' | 'high' | 'critical'

export interface Evidence {
  type: string
  source: string
  data: any
  relevance: number
}

// Analysis Types
export interface Anomaly {
  id: string
  type: string
  description: string
  anomaly_score: number
  severity: Severity
  affected_items: any[]
  detection_method: string
  statistical_significance: number
  context: Record<string, any>
}

export interface Pattern {
  id: string
  pattern: string[]
  type: string
  support: number
  confidence: number
  lift: number
  occurrences: number
  first_seen: string
  last_seen: string
  examples: any[]
}

export interface Trend {
  metric: string
  direction: 'increasing' | 'decreasing' | 'stable'
  strength: number
  change_rate: number
  forecast: ForecastPoint[]
  seasonality?: Seasonality
  change_points: ChangePoint[]
}

export interface ForecastPoint {
  timestamp: string
  value: number
  lower_bound: number
  upper_bound: number
  confidence: number
}

export interface Seasonality {
  period: string
  strength: number
  pattern: number[]
}

export interface ChangePoint {
  timestamp: string
  significance: number
  direction: 'up' | 'down'
}

// Report Types
export interface Report {
  id: string
  title: string
  type: ReportType
  format: ReportFormat
  status: ReportStatus
  size_bytes: number
  pages?: number
  download_url?: string
  preview_url?: string
  created_at: string
  expires_at: string
  metadata: Record<string, any>
}

export type ReportType = 'executive_summary' | 'detailed' | 'technical' | 'compliance'
export type ReportFormat = 'pdf' | 'html' | 'markdown' | 'docx'
export type ReportStatus = 'generating' | 'ready' | 'failed' | 'expired'

// Visualization Types
export interface Visualization {
  id: string
  type: VisualizationType
  title: string
  description?: string
  data: any
  config: VisualizationConfig
  interactive: boolean
}

export type VisualizationType = 
  | 'line_chart' 
  | 'bar_chart' 
  | 'pie_chart' 
  | 'scatter_plot'
  | 'heatmap'
  | 'network_graph'
  | 'timeline'
  | 'geographic_map'

export interface VisualizationConfig {
  width?: number
  height?: number
  colors?: string[]
  theme?: 'light' | 'dark'
  [key: string]: any
}

// Notification Types
export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  severity: Severity
  read: boolean
  created_at: string
  data?: any
  action_url?: string
}

export type NotificationType = 
  | 'anomaly_detected'
  | 'investigation_complete'
  | 'report_ready'
  | 'system_alert'
  | 'agent_update'

// WebSocket Event Types
export interface WebSocketEvent<T = any> {
  type: string
  payload: T
  timestamp: string
  correlation_id?: string
}

export interface ChatWebSocketEvent extends WebSocketEvent {
  type: 'message' | 'typing' | 'user_joined' | 'user_left' | 'error'
}

export interface InvestigationWebSocketEvent extends WebSocketEvent {
  type: 'status_update' | 'progress' | 'finding' | 'log' | 'complete' | 'error'
}

// Error Types
export interface ApiError {
  error: string
  message: string
  status_code: number
  details?: any
  timestamp: string
  request_id?: string
}

export interface ValidationError extends ApiError {
  validation_errors: {
    field: string
    message: string
    code: string
  }[]
}

// Rate Limit Types
export interface RateLimitInfo {
  limit: number
  remaining: number
  reset: number
  tier: 'free' | 'basic' | 'premium' | 'enterprise'
}

// File Types
export interface Attachment {
  id: string
  filename: string
  content_type: string
  size_bytes: number
  url: string
  thumbnail_url?: string
  uploaded_at: string
}
```

---

## 🚨 Tratamento de Erros

### Padrões de Erro da API

```typescript
// utils/error-handler.ts
export class ApiErrorHandler {
  static handle(error: any): never {
    if (error.response) {
      // Erro da API
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          throw new BadRequestError(data.message || 'Requisição inválida', data)
        
        case 401:
          throw new UnauthorizedError(data.message || 'Não autorizado', data)
        
        case 403:
          throw new ForbiddenError(data.message || 'Acesso negado', data)
        
        case 404:
          throw new NotFoundError(data.message || 'Recurso não encontrado', data)
        
        case 422:
          throw new ValidationError(data.message || 'Erro de validação', data.validation_errors)
        
        case 429:
          throw new RateLimitError(
            data.message || 'Limite de requisições excedido',
            data.retry_after
          )
        
        case 500:
          throw new ServerError(data.message || 'Erro interno do servidor', data)
        
        default:
          throw new ApiError(data.message || 'Erro desconhecido', status, data)
      }
    } else if (error.request) {
      // Erro de rede
      throw new NetworkError('Erro de conexão com o servidor')
    } else {
      // Erro desconhecido
      throw new UnknownError(error.message || 'Erro desconhecido')
    }
  }
}

// Classes de erro customizadas
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export class BadRequestError extends ApiError {
  constructor(message: string, details?: any) {
    super(message, 400, details)
    this.name = 'BadRequestError'
  }
}

export class UnauthorizedError extends ApiError {
  constructor(message: string, details?: any) {
    super(message, 401, details)
    this.name = 'UnauthorizedError'
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, public validationErrors: any[]) {
    super(message, 422, validationErrors)
    this.name = 'ValidationError'
  }
}

export class RateLimitError extends ApiError {
  constructor(message: string, public retryAfter: number) {
    super(message, 429, { retry_after: retryAfter })
    this.name = 'RateLimitError'
  }
}
```

### Hook para Tratamento de Erros

```typescript
// hooks/useApiError.ts
import { useState, useCallback } from 'react'
import { ApiError, ValidationError, RateLimitError } from '@/utils/error-handler'

export function useApiError() {
  const [error, setError] = useState<ApiError | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  const execute = useCallback(async <T>(
    apiCall: () => Promise<T>,
    options?: {
      onSuccess?: (data: T) => void
      onError?: (error: ApiError) => void
      showToast?: boolean
    }
  ): Promise<T | null> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const result = await apiCall()
      options?.onSuccess?.(result)
      return result
    } catch (err: any) {
      const apiError = err instanceof ApiError ? err : new ApiError(
        err.message || 'Erro desconhecido',
        500
      )
      
      setError(apiError)
      options?.onError?.(apiError)
      
      if (options?.showToast) {
        showErrorToast(apiError)
      }
      
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])
  
  const clearError = useCallback(() => {
    setError(null)
  }, [])
  
  return {
    error,
    isLoading,
    execute,
    clearError
  }
}

// Função auxiliar para mostrar toast
function showErrorToast(error: ApiError) {
  let message = error.message
  
  if (error instanceof ValidationError) {
    message = error.validationErrors
      .map(err => `${err.field}: ${err.message}`)
      .join('\n')
  } else if (error instanceof RateLimitError) {
    message = `${error.message}. Tente novamente em ${error.retryAfter}s`
  }
  
  // Implementar toast notification
  console.error('Toast:', message)
}
```

---

## ⚡ Rate Limiting

### Headers de Rate Limit

```typescript
interface RateLimitHeaders {
  'X-RateLimit-Limit': string      // Limite total
  'X-RateLimit-Remaining': string  // Requisições restantes
  'X-RateLimit-Reset': string       // Timestamp do reset
  'X-RateLimit-Tier': string        // Tier atual
}
```

### Implementação de Rate Limit Handler

```typescript
// utils/rate-limit-handler.ts
export class RateLimitHandler {
  private static instance: RateLimitHandler
  private limitInfo: Map<string, RateLimitInfo> = new Map()
  
  static getInstance(): RateLimitHandler {
    if (!RateLimitHandler.instance) {
      RateLimitHandler.instance = new RateLimitHandler()
    }
    return RateLimitHandler.instance
  }
  
  updateFromHeaders(endpoint: string, headers: any) {
    const limit = parseInt(headers['x-ratelimit-limit'] || '0')
    const remaining = parseInt(headers['x-ratelimit-remaining'] || '0')
    const reset = parseInt(headers['x-ratelimit-reset'] || '0')
    const tier = headers['x-ratelimit-tier'] || 'free'
    
    this.limitInfo.set(endpoint, {
      limit,
      remaining,
      reset,
      tier
    })
  }
  
  getRemainingRequests(endpoint: string): number {
    const info = this.limitInfo.get(endpoint)
    return info?.remaining ?? -1
  }
  
  getResetTime(endpoint: string): Date | null {
    const info = this.limitInfo.get(endpoint)
    return info ? new Date(info.reset * 1000) : null
  }
  
  shouldThrottle(endpoint: string, threshold: number = 10): boolean {
    const remaining = this.getRemainingRequests(endpoint)
    return remaining !== -1 && remaining < threshold
  }
  
  getWaitTime(endpoint: string): number {
    const resetTime = this.getResetTime(endpoint)
    if (!resetTime) return 0
    
    const now = new Date()
    const waitMs = resetTime.getTime() - now.getTime()
    return Math.max(0, Math.ceil(waitMs / 1000))
  }
}

// Hook para monitorar rate limit
export function useRateLimit(endpoint: string) {
  const [limitInfo, setLimitInfo] = useState<RateLimitInfo | null>(null)
  const handler = RateLimitHandler.getInstance()
  
  useEffect(() => {
    // Atualizar a cada segundo
    const interval = setInterval(() => {
      const info = handler.limitInfo.get(endpoint)
      if (info) {
        setLimitInfo({ ...info })
      }
    }, 1000)
    
    return () => clearInterval(interval)
  }, [endpoint])
  
  return {
    limit: limitInfo?.limit ?? 0,
    remaining: limitInfo?.remaining ?? 0,
    reset: limitInfo ? new Date(limitInfo.reset * 1000) : null,
    tier: limitInfo?.tier ?? 'free',
    shouldThrottle: handler.shouldThrottle(endpoint),
    waitTime: handler.getWaitTime(endpoint)
  }
}
```

---

## 🎯 Boas Práticas

### 1. Gerenciamento de Estado

```typescript
// store/chat-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ChatStore {
  sessions: Map<string, ChatSession>
  activeSessionId: string | null
  messages: Map<string, ChatMessage[]>
  
  // Actions
  setActiveSession: (sessionId: string) => void
  addMessage: (sessionId: string, message: ChatMessage) => void
  loadSession: (session: ChatSession) => void
  clearSession: (sessionId: string) => void
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      sessions: new Map(),
      activeSessionId: null,
      messages: new Map(),
      
      setActiveSession: (sessionId) => set({ activeSessionId: sessionId }),
      
      addMessage: (sessionId, message) => set((state) => {
        const messages = state.messages.get(sessionId) || []
        state.messages.set(sessionId, [...messages, message])
        return { messages: new Map(state.messages) }
      }),
      
      loadSession: (session) => set((state) => {
        state.sessions.set(session.id, session)
        return { sessions: new Map(state.sessions) }
      }),
      
      clearSession: (sessionId) => set((state) => {
        state.sessions.delete(sessionId)
        state.messages.delete(sessionId)
        return {
          sessions: new Map(state.sessions),
          messages: new Map(state.messages)
        }
      })
    }),
    {
      name: 'cidadao-ai-chat',
      partialize: (state) => ({
        activeSessionId: state.activeSessionId
      })
    }
  )
)
```

### 2. Otimização de Performance

```typescript
// components/OptimizedChat.tsx
import React, { memo, useMemo, useCallback } from 'react'
import { FixedSizeList as List } from 'react-window'
import AutoSizer from 'react-virtualized-auto-sizer'

// Memoizar componentes de mensagem
const MessageItem = memo(({ message }: { message: ChatMessage }) => {
  return (
    <div className={`message ${message.role}`}>
      <div className="content">{message.content}</div>
      <div className="metadata">
        {message.timestamp} • {message.agent_used}
      </div>
    </div>
  )
})

// Lista virtualizada para muitas mensagens
export function OptimizedMessageList({ messages }: { messages: ChatMessage[] }) {
  const Row = useCallback(({ index, style }: any) => (
    <div style={style}>
      <MessageItem message={messages[index]} />
    </div>
  ), [messages])
  
  return (
    <AutoSizer>
      {({ height, width }) => (
        <List
          height={height}
          itemCount={messages.length}
          itemSize={100} // Altura estimada de cada mensagem
          width={width}
        >
          {Row}
        </List>
      )}
    </AutoSizer>
  )
}
```

### 3. Cache e Persistência

```typescript
// utils/cache-manager.ts
export class CacheManager {
  private static instance: CacheManager
  private cache: Map<string, { data: any, expires: number }> = new Map()
  
  static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager()
    }
    return CacheManager.instance
  }
  
  set(key: string, data: any, ttl: number = 300000) { // 5 minutos padrão
    const expires = Date.now() + ttl
    this.cache.set(key, { data, expires })
  }
  
  get<T>(key: string): T | null {
    const item = this.cache.get(key)
    if (!item) return null
    
    if (Date.now() > item.expires) {
      this.cache.delete(key)
      return null
    }
    
    return item.data as T
  }
  
  invalidate(pattern: string) {
    const keys = Array.from(this.cache.keys())
    keys.forEach(key => {
      if (key.includes(pattern)) {
        this.cache.delete(key)
      }
    })
  }
  
  clear() {
    this.cache.clear()
  }
}

// Hook com cache
export function useCachedApi<T>(
  key: string,
  fetcher: () => Promise<T>,
  options?: {
    ttl?: number
    refetchOnMount?: boolean
    refetchInterval?: number
  }
) {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const cache = CacheManager.getInstance()
  
  const fetchData = useCallback(async () => {
    // Verificar cache primeiro
    const cached = cache.get<T>(key)
    if (cached) {
      setData(cached)
      setIsLoading(false)
      return cached
    }
    
    try {
      setIsLoading(true)
      const result = await fetcher()
      cache.set(key, result, options?.ttl)
      setData(result)
      return result
    } catch (err: any) {
      setError(err)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [key, fetcher, options?.ttl])
  
  useEffect(() => {
    if (options?.refetchOnMount !== false) {
      fetchData()
    }
    
    if (options?.refetchInterval) {
      const interval = setInterval(fetchData, options.refetchInterval)
      return () => clearInterval(interval)
    }
  }, [])
  
  return { data, isLoading, error, refetch: fetchData }
}
```

### 4. Monitoramento e Analytics

```typescript
// utils/analytics.ts
export class Analytics {
  static trackEvent(event: string, properties?: any) {
    // Implementar tracking
    console.log('Track event:', event, properties)
  }
  
  static trackApiCall(endpoint: string, duration: number, status: number) {
    this.trackEvent('api_call', {
      endpoint,
      duration,
      status,
      timestamp: new Date().toISOString()
    })
  }
  
  static trackError(error: Error, context?: any) {
    this.trackEvent('error', {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString()
    })
  }
  
  static trackPerformance(metric: string, value: number) {
    this.trackEvent('performance', {
      metric,
      value,
      timestamp: new Date().toISOString()
    })
  }
}

// Interceptor para analytics
axios.interceptors.request.use((config) => {
  config.metadata = { startTime: Date.now() }
  return config
})

axios.interceptors.response.use(
  (response) => {
    const duration = Date.now() - response.config.metadata.startTime
    Analytics.trackApiCall(
      response.config.url!,
      duration,
      response.status
    )
    return response
  },
  (error) => {
    if (error.response) {
      const duration = Date.now() - error.config.metadata.startTime
      Analytics.trackApiCall(
        error.config.url,
        duration,
        error.response.status
      )
    }
    Analytics.trackError(error)
    return Promise.reject(error)
  }
)
```

### 5. Segurança

```typescript
// utils/security.ts
export class Security {
  // Sanitizar input do usuário
  static sanitizeInput(input: string): string {
    return input
      .replace(/[<>]/g, '') // Remover tags HTML básicas
      .trim()
      .slice(0, 5000) // Limitar tamanho
  }
  
  // Validar URLs
  static isValidUrl(url: string): boolean {
    try {
      const parsed = new URL(url)
      return ['http:', 'https:'].includes(parsed.protocol)
    } catch {
      return false
    }
  }
  
  // Storage seguro
  static secureStorage = {
    setItem(key: string, value: any) {
      try {
        const encrypted = btoa(JSON.stringify(value))
        localStorage.setItem(key, encrypted)
      } catch (error) {
        console.error('Failed to save to storage:', error)
      }
    },
    
    getItem<T>(key: string): T | null {
      try {
        const encrypted = localStorage.getItem(key)
        if (!encrypted) return null
        return JSON.parse(atob(encrypted)) as T
      } catch {
        return null
      }
    },
    
    removeItem(key: string) {
      localStorage.removeItem(key)
    }
  }
}
```

---

## 📚 Recursos Adicionais

### Links Úteis
- **API Documentation**: https://neural-thinker-cidadao-ai-backend.hf.space/docs
- **Redoc**: https://neural-thinker-cidadao-ai-backend.hf.space/redoc
- **Health Check**: https://neural-thinker-cidadao-ai-backend.hf.space/health

### Variáveis de Ambiente Recomendadas

```env
# .env.local
NEXT_PUBLIC_API_URL=https://neural-thinker-cidadao-ai-backend.hf.space
NEXT_PUBLIC_WS_URL=wss://neural-thinker-cidadao-ai-backend.hf.space
NEXT_PUBLIC_APP_NAME=Cidadão.AI
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

### Scripts Úteis para package.json

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "analyze": "ANALYZE=true next build",
    "generate-types": "openapi-typescript https://neural-thinker-cidadao-ai-backend.hf.space/openapi.json --output ./src/types/api-generated.ts"
  }
}
```

---

## 🤝 Suporte e Contato

Para dúvidas sobre a integração:
1. Consulte a documentação interativa em `/docs`
2. Verifique os logs de erro retornados pela API
3. Use o endpoint `/health` para verificar status dos serviços
4. Monitore rate limits através dos headers de resposta

Este guia será atualizado conforme novas funcionalidades forem adicionadas ao backend. Mantenha-se atualizado com as versões da API através do endpoint `/api/v1/info`.