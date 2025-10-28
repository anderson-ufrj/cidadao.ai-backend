# 📢 Carlos Drummond de Andrade - Comunicador do Povo

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-27

---

**Status**: ✅ **Tier 1 (91.54% Cobertura)** - Totalmente Operacional
**Arquivo**: `src/agents/drummond.py`
**Tamanho**: 1,707 linhas
**Métodos Implementados**: 32
**Testes**: ✅ 117 testes (`tests/unit/agents/test_drummond*.py`)
**Cobertura**: 91.54% (420 statements, 31 missing)
**Última Atualização**: 2025-10-28

---

## 🎯 Missão

Geração automática de comunicações, alertas e notificações multi-canal, traduzindo insights técnicos complexos em linguagem acessível ao cidadão brasileiro.

**Inspiração Cultural**: Carlos Drummond de Andrade, poeta mineiro conhecido por sua capacidade de comunicar sentimentos e ideias complexas em linguagem direta e acessível.

---

## 🧠 Algoritmos e Técnicas Implementadas

### 1. Geração de Linguagem Natural (NLG)
- ✅ **Template-based Generation** para mensagens estruturadas
- ✅ **Neural Language Models** (integração com Maritaca Sabiazinho-3)
- ✅ **Adaptive Text Generation** baseado no perfil do usuário
- ✅ **Conversational Memory** com context persistence
- ✅ **Style Transfer** para adequação de tom e registro
- ✅ **Personality Prompt** com identidade cultural mineira

### 2. Sistema de Notificações Multi-Canal
- ✅ **Priority Queue Algorithm** para ordenação de mensagens
- ✅ **Circuit Breaker Pattern** para canais instáveis
- ✅ **Exponential Backoff** para retry de falhas
- ✅ **Rate Limiting** por canal e destinatário
- ✅ **Deduplication Algorithm** para evitar spam

### 3. Personalização e Segmentação
- ✅ **Collaborative Filtering** para preferências
- ✅ **Clustering de audiências** por perfil comportamental
- ✅ **A/B Testing** automático para otimização
- ✅ **Sentiment Analysis** para ajuste de tom
- ✅ **Demographic Segmentation** com ML

### 4. Análise de Engajamento
- ✅ **Click-through Rate (CTR)** tracking
- ✅ **Message Effectiveness Scoring**
- ✅ **Response Time Analysis**
- ✅ **Channel Performance Optimization**
- ✅ **Conversion Funnel Analysis**

### 5. Processamento de Linguagem Natural
- ✅ **Named Entity Recognition (NER)** para contextualização
- ✅ **Text Summarization** para relatórios executivos
- ✅ **Keyword Extraction** para tags automáticas
- ✅ **Language Detection** automática
- ✅ **Translation API** integration para multilíngue

---

## 📡 Canais de Comunicação Suportados

```python
class CommunicationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    PUSH_NOTIFICATION = "push_notification"
    SLACK = "slack"
    DISCORD = "discord"
    PORTAL_WEB = "portal_web"
    API_CALLBACK = "api_callback"
```

**Total**: 10 canais suportados

---

## 🔧 Capacidades Principais

### ✅ Implementadas e Testadas

1. **Geração de Mensagens Personalizadas**
   - Adaptação automática de linguagem por perfil
   - Templates dinâmicos com variáveis
   - Formatação específica por canal

2. **Notificações Inteligentes**
   - Priorização automática (LOW → CRITICAL)
   - Deduplicação de mensagens similares
   - Retry automático com exponential backoff

3. **Análise de Engajamento**
   - Tracking de entrega, leitura, cliques
   - Métricas de efetividade por canal
   - Otimização contínua de mensagens

4. **Integração com Maritaca AI**
   - Geração de texto natural em português
   - Suporte a múltiplos modelos (sabia-2, sabia-3)
   - Conversação contextualizada

5. **Memória Conversacional**
   - Histórico de interações por usuário
   - Contexto mantido entre sessões
   - Personalização baseada em histórico

### ⚠️ Limitações Conhecidas

1. **HuggingFace Spaces Deploy**
   - Agente comentado no `__init__.py` por problemas de import
   - **Causa**: Dependência circular com `MaritacaClient`
   - **Workaround**: Usar via import direto `from src.agents.drummond import CommunicationAgent`

2. **Canais Externos**
   - WhatsApp, Telegram: Requerem configuração de API keys
   - SMS: Requer integração com provedor (Twilio/Vonage)

3. **Translation API**
   - Multilíngue funcional mas requer API key externa
   - Suporte nativo apenas para PT-BR

---

## 📋 Estrutura de Dados

### MessageTemplate
```python
@dataclass
class MessageTemplate:
    template_id: str
    message_type: MessageType  # ALERT, REPORT, NOTIFICATION, etc
    language: str
    subject_template: str
    body_template: str
    variables: List[str]
    formatting_rules: Dict[str, Any]
    channel_adaptations: Dict[CommunicationChannel, Dict[str, str]]
```

### CommunicationResult
```python
@dataclass
class CommunicationResult:
    message_id: str
    target_id: str
    channel: CommunicationChannel
    status: str  # "sent", "failed", "pending", "delivered", "read"
    sent_at: datetime
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    metadata: Dict[str, Any]
```

---

## 💻 Exemplo de Uso

### Enviar Alerta de Anomalia

```python
from src.agents.drummond import CommunicationAgent, CommunicationChannel, MessageType

# Inicializar agente
drummond = CommunicationAgent()
await drummond.initialize()

# Criar mensagem
message = AgentMessage(
    content={
        "type": "anomaly_alert",
        "organization": "Ministério da Saúde",
        "anomaly_type": "price_spike",
        "severity": "high",
        "value": 1_500_000.00,
        "expected_value": 500_000.00
    },
    context=AgentContext(
        conversation_id="conv_123",
        user_id="user_456"
    )
)

# Processar e enviar
response = await drummond.process(message)

# Resultado
print(response.data["notification_sent"])
# {
#   "message_id": "msg_789",
#   "channels": ["email", "portal_web"],
#   "status": "sent",
#   "generated_text": "🚨 Alerta: Detectada anomalia de preço..."
# }
```

### Gerar Relatório em Linguagem Natural

```python
# Gerar relatório executivo
message = AgentMessage(
    content={
        "type": "generate_summary",
        "investigation_results": {
            "anomalies_found": 12,
            "total_value": 5_000_000.00,
            "risk_level": "high"
        },
        "audience": "executive",  # executivo, técnico, cidadão
        "language": "pt-br"
    }
)

response = await drummond.process(message)
print(response.data["summary"])
# "Foram identificadas 12 irregularidades em contratos
#  governamentais, totalizando R$ 5 milhões em gastos
#  suspeitos. Recomenda-se investigação aprofundada..."
```

---

## 🧪 Testes (Atualizado 2025-10-28)

### Cobertura de Testes

**Cobertura Global**: 91.54% ⭐ (+3.76pp)

- ✅ **117 testes** passando (100% success rate)
- ✅ **420 statements** testados (389 covered, 31 missing)
- ✅ **112 branches** testadas (102 covered, 10 partial)

### Arquivos de Teste

1. `tests/unit/agents/test_drummond.py` - 76 testes (core functionality)
2. `tests/unit/agents/test_drummond_expanded.py` - 33 testes (advanced features)
3. `tests/unit/agents/test_drummond_coverage.py` - 8 testes (coverage boost)

### Principais Cenários Testados

1. **Geração de mensagens**
   - Template rendering
   - Personalização por perfil
   - Formatação por canal

2. **Notificações multi-canal**
   - Envio paralelo
   - Fallback automático
   - Retry em falhas

3. **Análise de engajamento**
   - Tracking de métricas
   - Cálculo de efetividade
   - Otimização de conteúdo

---

## 🔄 Integração com Outros Agentes

### Consumidores Principais

1. **Tiradentes (Reporter)**
   - Recebe relatórios técnicos
   - Traduz para linguagem cidadã
   - Distribui via canais apropriados

2. **Zumbi (Investigator)**
   - Envia alertas de anomalias detectadas
   - Notifica stakeholders relevantes

3. **Abaporu (Master)**
   - Comunica status de investigações
   - Envia relatórios consolidados

### Dependências

- ✅ `MaritacaClient`: Geração de texto via LLM
- ✅ `ConversationalMemory`: Contexto de conversas
- ✅ `IntentDetection`: Classificação de intenções
- ⚠️ `NotificationService`: Envio real por canais externos (opcional)

---

## 📊 Métricas e Monitoramento

### Métricas Prometheus Exportadas

```python
# Mensagens enviadas
drummond_messages_sent_total{channel="email", status="success"}

# Taxa de entrega
drummond_delivery_rate{channel="whatsapp"}

# Tempo de processamento
drummond_processing_duration_seconds

# Taxa de engajamento
drummond_engagement_rate{channel="portal_web", metric="ctr"}
```

---

## 🚀 Roadmap

### Próximas Melhorias (para 100%)

1. **Resolver Import no HuggingFace** (prioridade alta)
   - Refatorar dependência circular com MaritacaClient
   - Descomentar no `__init__.py`

2. **Canais Adicionais**
   - Microsoft Teams
   - Mattermost
   - Matrix

3. **ML Avançado**
   - Fine-tuning de modelos para tom institucional brasileiro
   - Personalização automática por análise de histórico

4. **Analytics**
   - Dashboard de efetividade de comunicações
   - Predição de melhor horário/canal por usuário

---

## ⚠️ Notas de Deploy

### HuggingFace Spaces

**Status Atual**: ❌ Não disponível (comentado no `__init__.py`)

**Problema**:
```python
# src/agents/__init__.py (linha 46)
# from .drummond import CommunicationAgent  # Comentado
```

**Causa**: Import circular com `MaritacaClient` causa erro no deploy HF

**Solução Temporária**:
```python
# Import direto quando necessário
from src.agents.drummond import CommunicationAgent
agent = CommunicationAgent()
```

### Produção Local/Docker

✅ **Funciona perfeitamente** em ambiente local e Docker

**Requisitos**:
```bash
# .env
MARITACA_API_KEY=your_key  # Para geração de texto
NOTIFICATION_CHANNELS=email,portal_web  # Canais habilitados
```

---

## 📚 Referências

- **Poeta inspirador**: Carlos Drummond de Andrade (1902-1987)
- **NLG Research**: Template-based vs Neural approaches
- **Notification Patterns**: Circuit Breaker, Exponential Backoff
- **Engagement Analytics**: CTR, Conversion funnel

---

## 🤝 Contribuindo

Para melhorar este agente:

1. **Resolver o import circular** (alta prioridade)
2. **Adicionar templates** para novos tipos de comunicação
3. **Integrar novos canais** (Teams, Mattermost)
4. **Expandir testes** para cobrir edge cases

---

**Autor**: Anderson Henrique da Silva
**Manutenção**: Ativa
**Versão**: 0.95 (Beta)
