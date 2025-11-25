# DSPy Implementation - Agent Personalities

**Data**: 2025-11-25
**Versão**: 1.0.0
**Status**: Produção
**Autor**: Anderson H. Silva

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [O que é DSPy](#o-que-é-dspy)
3. [Arquitetura da Implementação](#arquitetura-da-implementação)
4. [Componentes Principais](#componentes-principais)
5. [Fluxo de Execução](#fluxo-de-execução)
6. [Configuração do LLM](#configuração-do-llm)
7. [Personalidades dos Agentes](#personalidades-dos-agentes)
8. [API de Uso](#api-de-uso)
9. [Tratamento de Erros](#tratamento-de-erros)
10. [Integração com Frontend](#integração-com-frontend)
11. [Testes](#testes)
12. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O DSPy foi implementado no Cidadão.AI para fornecer respostas dinâmicas e personalizadas através dos agentes com personalidades culturais brasileiras. Antes do DSPy, os agentes retornavam respostas estáticas. Agora, cada agente responde de forma única, refletindo sua personalidade histórica.

### Problema Resolvido

```
ANTES (resposta estática):
"Olá! Sou Anita e vou ajudá-lo com sua solicitação."

DEPOIS (resposta dinâmica com DSPy):
"Olá! Sou Anita Garibaldi, a Analista do Cidadão.AI. Como uma
estrategista brilhante e apaixonada, estou aqui para ajudar a
decifrar padrões e tendências nos dados públicos, com o objetivo
de libertar você da desinformação..."
```

---

## O que é DSPy

[DSPy](https://dspy.ai/) é um framework de programação declarativa para LLMs desenvolvido pela Stanford NLP. Em vez de escrever prompts manualmente, você define **Signatures** (assinaturas) que descrevem inputs e outputs, e o DSPy otimiza automaticamente as chamadas ao LLM.

### Conceitos Chave

| Conceito | Descrição |
|----------|-----------|
| **Signature** | Define a estrutura de entrada/saída de uma tarefa |
| **Module** | Encapsula lógica de processamento (como `ChainOfThought`) |
| **LM** | Configuração do Language Model a ser usado |
| **Prediction** | Resultado retornado pelo módulo |

### Por que DSPy?

1. **Modularidade**: Separa a lógica de personalidade do código
2. **Otimização**: DSPy pode otimizar prompts automaticamente
3. **Flexibilidade**: Fácil trocar LLM (Maritaca, Anthropic, OpenAI)
4. **Manutenibilidade**: Personalidades definidas declarativamente

---

## Arquitetura da Implementação

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                  │
│                   (SSE Event Stream)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    /api/v1/chat/stream                          │
│                     (src/api/routes/chat.py)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Detecta Intent (investigate, question, analyze...)     │ │
│  │  2. Seleciona Agente (zumbi, anita, drummond...)          │ │
│  │  3. Chama DSPyAgentService                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DSPyAgentService                              │
│               (src/services/dspy_agents.py)                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Singleton Pattern                                       │ │
│  │  • Configura LLM (Maritaca/sabia-3)                       │ │
│  │  • Gerencia DSPyAgentChat Module                          │ │
│  │  • Fallback responses se LLM indisponível                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DSPyAgentChat                                │
│                   (dspy.Module)                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • ChainOfThought para raciocínio                         │ │
│  │  • AgentChat Signature                                     │ │
│  │  • System Prompts por personalidade                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Maritaca AI                                 │
│                  (sabia-3 model)                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • API OpenAI-compatible                                   │ │
│  │  • Otimizado para Português Brasileiro                    │ │
│  │  • Base URL: https://chat.maritaca.ai/api                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Componentes Principais

### 1. AgentPersonality (Enum)

Define os agentes disponíveis no sistema:

```python
class AgentPersonality(Enum):
    ZUMBI = "zumbi"           # Investigador
    ANITA = "anita"           # Analista
    TIRADENTES = "tiradentes" # Relator
    DRUMMOND = "drummond"     # Comunicador
    DANDARA = "dandara"       # Guardiã da Justiça Social
    MACHADO = "machado"       # Analista Textual
    OXOSSI = "oxossi"         # Caçador de Dados
    ABAPORU = "abaporu"       # Orquestrador Master
```

### 2. AGENT_SYSTEM_PROMPTS (Dict)

System prompts que definem a personalidade de cada agente:

```python
AGENT_SYSTEM_PROMPTS = {
    AgentPersonality.ZUMBI: """Você é Zumbi dos Palmares, o Investigador do Cidadão.AI.
Sua personalidade: Corajoso, determinado, incansável na busca pela verdade.
Especialidade: Detecção de anomalias, fraudes e irregularidades em dados governamentais.
Tom: Direto, assertivo, comprometido com a transparência.
História: Assim como liderei o Quilombo dos Palmares contra a opressão,
hoje lidero investigações contra a corrupção.
Sempre responda em português brasileiro, com determinação e foco na justiça.""",

    # ... outros agentes
}
```

### 3. AgentChat (dspy.Signature)

Define a estrutura de entrada/saída para o chat:

```python
class AgentChat(dspy.Signature):
    """Agent responds to user message with their unique personality."""

    system_prompt: str = dspy.InputField(
        desc="The agent's personality and role description"
    )
    user_message: str = dspy.InputField(
        desc="The user's message or question"
    )
    conversation_context: str = dspy.InputField(
        desc="Previous conversation context if any",
        default=""
    )
    intent_type: str = dspy.InputField(
        desc="The detected intent type (investigate, analyze, report, question, etc.)"
    )

    response: str = dspy.OutputField(
        desc="The agent's response in Portuguese, reflecting their personality"
    )
```

### 4. DSPyAgentChat (dspy.Module)

Módulo que processa as mensagens:

```python
class DSPyAgentChat(dspy.Module):
    def __init__(self):
        super().__init__()
        self.chat = dspy.ChainOfThought(AgentChat)

    def forward(
        self,
        agent_personality: AgentPersonality,
        user_message: str,
        intent_type: str = "question",
        conversation_context: str = ""
    ):
        system_prompt = AGENT_SYSTEM_PROMPTS.get(
            agent_personality,
            AGENT_SYSTEM_PROMPTS[AgentPersonality.DRUMMOND]
        )

        return self.chat(
            system_prompt=system_prompt,
            user_message=user_message,
            intent_type=intent_type,
            conversation_context=conversation_context
        )
```

### 5. DSPyAgentService (Singleton)

Serviço principal que gerencia toda a interação:

```python
class DSPyAgentService:
    _instance: Optional["DSPyAgentService"] = None
    _initialized: bool = False
    _dspy_available: bool = False

    def __new__(cls) -> "DSPyAgentService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def is_available(self) -> bool:
        """Check if DSPy is fully available and configured"""
        return (
            self._dspy_available
            and self.lm is not None
            and self.chat_module is not None
        )

    async def chat(self, agent_id, message, intent_type, context) -> dict:
        # Retorna resposta do agente com personalidade
        ...

    async def chat_stream(self, agent_id, message, intent_type, context):
        # Gera chunks para streaming SSE
        ...
```

---

## Fluxo de Execução

```
1. Usuário envia mensagem
   │
   ▼
2. IntentClassifier detecta intenção
   │  (investigate, question, analyze, report, greeting...)
   │
   ▼
3. _get_suggested_agent mapeia intent → agent_id
   │  investigate → zumbi
   │  question   → anita/drummond
   │  analyze    → anita
   │  report     → tiradentes
   │
   ▼
4. Verifica DSPY_AVAILABLE
   │
   ├─── True ──────────────────────────┐
   │                                    │
   ▼                                    │
5. dspy_service.chat_stream()          │
   │                                    │
   ▼                                    │
6. DSPyAgentChat.forward()             │
   │  - Busca system_prompt            │
   │  - Chama ChainOfThought           │
   │  - Envia para Maritaca            │
   │                                    │
   ▼                                    │
7. Recebe response                      │
   │                                    │
   ▼                                    │
8. Chunking para SSE                    │
   │  (cada 3 palavras)                │
   │                                    │
   └─── False ─────────────────────────┤
                                        │
                                        ▼
                              9. Fallback response
                                 (resposta estática)
                                        │
                                        ▼
                              10. Stream para frontend
```

---

## Configuração do LLM

### Maritaca AI (Primário)

```python
def _configure_llm(self) -> None:
    api_key = settings.maritaca_api_key.get_secret_value()

    self.lm = dspy.LM(
        model="openai/sabia-3",      # Prefixo openai/ para LiteLLM
        api_key=api_key,
        api_base="https://chat.maritaca.ai/api",
        temperature=0.7,
        max_tokens=1024,
    )
    dspy.configure(lm=self.lm)
```

### Variáveis de Ambiente

```bash
# .env
MARITACA_API_KEY=sua_chave_aqui
```

### Por que Maritaca?

1. **Otimizado para Português**: Melhor compreensão de contexto brasileiro
2. **API OpenAI-compatible**: Funciona com LiteLLM sem modificações
3. **Latência baixa**: Servidores no Brasil
4. **Contexto cultural**: Entende referências históricas brasileiras

---

## Personalidades dos Agentes

### Zumbi dos Palmares - Investigador

| Atributo | Valor |
|----------|-------|
| **ID** | `zumbi` |
| **Função** | Investigador |
| **Personalidade** | Corajoso, determinado, incansável |
| **Especialidade** | Detecção de anomalias e fraudes |
| **Tom** | Direto, assertivo |
| **Intents** | `investigate` |

**Exemplo de resposta**:
> "Entendi seu pedido. Como Zumbi dos Palmares, meu compromisso é com a verdade e a justiça. Para investigar contratos de forma eficaz, siga estes passos..."

---

### Anita Garibaldi - Analista

| Atributo | Valor |
|----------|-------|
| **ID** | `anita` |
| **Função** | Analista |
| **Personalidade** | Estrategista brilhante, apaixonada |
| **Especialidade** | Análise de padrões e tendências |
| **Tom** | Inteligente, caloroso, didático |
| **Intents** | `question`, `analyze` |

**Exemplo de resposta**:
> "Olá! Sou Anita Garibaldi, a Analista do Cidadão.AI. Como uma estrategista brilhante e apaixonada, estou aqui para ajudar a decifrar padrões e tendências nos dados públicos..."

---

### Carlos Drummond de Andrade - Comunicador

| Atributo | Valor |
|----------|-------|
| **ID** | `drummond` |
| **Função** | Comunicador |
| **Personalidade** | Poético, reflexivo, humano |
| **Especialidade** | Comunicação clara e acessível |
| **Tom** | Poético, humor mineiro |
| **Intents** | `greeting`, `help`, `smalltalk` |

**Frases características**:
- "E agora, José?" (quando há problemas)
- "No meio do caminho tinha uma pedra" (para obstáculos)

**Exemplo de resposta**:
> "Olá, caro interlocutor! Estou como um poema inacabado, sempre pronto para novas linhas e versos. E você, como te encontro nesse palco da vida?"

---

### Tiradentes - Relator

| Atributo | Valor |
|----------|-------|
| **ID** | `tiradentes` |
| **Função** | Relator |
| **Personalidade** | Idealista, eloquente |
| **Especialidade** | Geração de relatórios claros |
| **Tom** | Formal mas acessível, patriótico |
| **Intents** | `report` |

---

### Oxóssi - Caçador de Dados

| Atributo | Valor |
|----------|-------|
| **ID** | `oxossi` |
| **Função** | Caçador de Dados |
| **Personalidade** | Perspicaz, paciente, certeiro |
| **Especialidade** | Busca em múltiplas fontes |
| **Tom** | Calmo, focado, preciso |
| **Intents** | `data`, `search` |

---

### Dandara dos Palmares - Guardiã da Justiça Social

| Atributo | Valor |
|----------|-------|
| **ID** | `dandara` |
| **Função** | Guardiã da Justiça Social |
| **Personalidade** | Guerreira, protetora |
| **Especialidade** | Análise de equidade social |
| **Tom** | Forte, empático |

---

### Machado de Assis - Analista Textual

| Atributo | Valor |
|----------|-------|
| **ID** | `machado` |
| **Função** | Analista Textual |
| **Personalidade** | Perspicaz, irônico, genial |
| **Especialidade** | Análise de documentos oficiais |
| **Tom** | Sofisticado, ironia fina |

---

### Abaporu - Orquestrador Master

| Atributo | Valor |
|----------|-------|
| **ID** | `abaporu` |
| **Função** | Orquestrador Master |
| **Personalidade** | Visionário, integrador |
| **Especialidade** | Coordenação de investigações complexas |
| **Tom** | Reflexivo, artístico |

---

## API de Uso

### Endpoint Principal

```
POST /api/v1/chat/stream
Content-Type: application/json

{
  "message": "Quero investigar contratos do Ministério da Saúde"
}
```

### Formato da Resposta (SSE)

```
data: {"type":"start","timestamp":"2025-11-25T12:00:00+00:00"}

data: {"type":"detecting","message":"Analisando sua mensagem..."}

data: {"type":"intent","intent":"investigate","confidence":0.85}

data: {"type":"agent_selected","agent_id":"zumbi","agent_name":"Zumbi"}

data: {"type":"thinking","message":"Zumbi está pensando..."}

data: {"type":"chunk","content":"Entendi seu","agent_id":"zumbi"}

data: {"type":"chunk","content":"pedido. Como","agent_id":"zumbi"}

... mais chunks ...

data: {"type":"complete","agent_id":"zumbi","agent_name":"Zumbi","suggested_actions":["start_investigation","learn_more"]}
```

### Uso Programático

```python
from src.services.dspy_agents import get_dspy_agent_service

async def example():
    service = get_dspy_agent_service()

    # Verificar disponibilidade
    if not service.is_available():
        print("DSPy não disponível, usando fallback")

    # Chat simples
    result = await service.chat(
        agent_id="drummond",
        message="Olá, como você está?",
        intent_type="greeting",
        context=""
    )
    print(result["response"])

    # Chat com streaming
    async for chunk in service.chat_stream(
        agent_id="zumbi",
        message="Investigar contratos",
        intent_type="investigate"
    ):
        if chunk["type"] == "chunk":
            print(chunk["content"], end=" ")
```

---

## Tratamento de Erros

### Import Condicional

O DSPy é importado condicionalmente para não quebrar a aplicação se não estiver disponível:

```python
DSPY_IMPORT_ERROR = None
try:
    import dspy
    logger.info("DSPy module imported successfully")
except ImportError as e:
    DSPY_IMPORT_ERROR = f"DSPy import failed: {e}"
    logger.error(f"Failed to import dspy: {e}")
    dspy = None
```

### Classes Condicionais

As classes DSPy só são definidas se o módulo estiver disponível:

```python
AgentChat = None
DSPyAgentChat = None

if dspy is not None:
    class AgentChat(dspy.Signature):
        ...

    class DSPyAgentChat(dspy.Module):
        ...
```

### Fallback Responses

Se DSPy ou LLM não estiverem disponíveis, respostas estáticas são retornadas:

```python
def _fallback_response(self, personality, message, intent_type):
    fallbacks = {
        AgentPersonality.ZUMBI: f"Sou Zumbi dos Palmares, investigador do Cidadão.AI...",
        AgentPersonality.ANITA: "Olá! Sou Anita Garibaldi, analista do Cidadão.AI...",
        # ... outros
    }
    return {
        "response": fallbacks.get(personality, "..."),
        "fallback": True,  # Flag indicando fallback
    }
```

---

## Integração com Frontend

### Mapeamento de Agentes para UI

```typescript
const AGENT_CONFIG = {
  zumbi: {
    name: 'Zumbi dos Palmares',
    role: 'Investigador',
    color: '#8B4513',
    icon: '🏹',
  },
  anita: {
    name: 'Anita Garibaldi',
    role: 'Analista',
    color: '#B22222',
    icon: '📊',
  },
  drummond: {
    name: 'Carlos Drummond de Andrade',
    role: 'Comunicador',
    color: '#2F4F4F',
    icon: '✍️',
  },
  // ... outros
};
```

### Consumindo o Stream

```typescript
const response = await fetch('/api/v1/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userMessage })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const lines = decoder.decode(value).split('\n');
  for (const line of lines) {
    if (!line.startsWith('data: ')) continue;
    const data = JSON.parse(line.slice(6));

    switch (data.type) {
      case 'agent_selected':
        setCurrentAgent(data.agent_id);
        break;
      case 'chunk':
        appendToMessage(data.content);
        break;
      case 'complete':
        finalizeMessage();
        break;
    }
  }
}
```

---

## Testes

### Teste Local

```bash
# Testar serviço DSPy
JWT_SECRET_KEY=test SECRET_KEY=test python -c "
import asyncio
from src.services.dspy_agents import get_dspy_agent_service

async def test():
    service = get_dspy_agent_service()
    print('Is available:', service.is_available())

    result = await service.chat('drummond', 'Olá!', 'greeting')
    print('Response:', result['response'][:100])

asyncio.run(test())
"
```

### Teste de Produção

```bash
# Testar endpoint de chat
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "Quero investigar contratos"}'
```

---

## Troubleshooting

### DSPy não carrega em produção

**Sintoma**: Logs mostram "DSPy Agent Service loaded but not fully available"

**Solução**: Verificar se `dspy-ai` e `litellm` estão no `requirements.txt`:
```
dspy-ai>=2.5.0
litellm>=1.30.0
```

### Respostas estáticas em vez de dinâmicas

**Sintoma**: Respostas começam com "Olá! Sou [Agente] e vou ajudá-lo..."

**Solução**: Verificar logs para:
1. "DSPy module imported successfully"
2. "DSPy configured with Maritaca LLM"
3. "DSPy Agent Service initialized successfully"

Se faltar algum, verificar:
- `MARITACA_API_KEY` está configurada
- Conexão com `https://chat.maritaca.ai/api`

### Erro de API Key

**Sintoma**: "MARITACA_API_KEY not found"

**Solução**: Configurar variável no Railway:
```bash
railway variables set MARITACA_API_KEY=sua_chave
```

### Timeout na resposta

**Sintoma**: Resposta demora mais de 30s

**Solução**:
1. Reduzir `max_tokens` (padrão: 1024)
2. Verificar latência da Maritaca
3. Considerar usar modelo mais rápido (`sabiazinho-3`)

---

## Referências

- [DSPy Documentation](https://dspy.ai/)
- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [Maritaca AI](https://maritaca.ai/)
- [LiteLLM Documentation](https://docs.litellm.ai/)

---

## Changelog

### v1.0.0 (2025-11-25)
- Implementação inicial do DSPy
- 8 personalidades de agentes brasileiros
- Integração com Maritaca AI (sabia-3)
- Sistema de fallback para indisponibilidade
- Streaming SSE com chunking
