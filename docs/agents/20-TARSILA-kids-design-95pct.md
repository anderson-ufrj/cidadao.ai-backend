# Tarsila do Amaral - Educadora de Design para Criancas

**Codinome**: Tarsila do Amaral
**Tipo**: Kids Design Education Agent
**Arquivo**: `src/agents/tarsila.py`
**Classe**: `KidsDesignAgent`
**Aliases**: `TarsilaAgent`, `TarsilaDoAmaralAgent`
**Base Class**: `BaseKidsAgent` (shared safety features)
**Status**: 100% Operacional
**Coverage**: 95%+ (20/20 E2E tests passing)

## Visao Geral

Tarsila do Amaral e a agente educadora de design e estetica para criancas do Cidadao.AI, especializada em ensinar teoria das cores, principios de design, harmonia visual e apreciacao artistica. Inspirada na grande pintora brasileira Tarsila do Amaral (1886-1973), icone do modernismo brasileiro e criadora do Abaporu.

## Arquitetura

```
BaseKidsAgent (base_kids_agent.py)
├── BLOCKED_TOPICS (70 items - single source of truth)
├── is_content_safe() (shared)
├── is_topic_allowed() (shared)
├── _generate_response() with DSPy (shared)
└── process() (shared)
    │
    └── KidsDesignAgent (tarsila.py)
        ├── ALLOWED_TOPICS_DESIGN (162 items)
        ├── PERSONALITY_PROMPT (Brazilian Modernism)
        ├── _get_safe_redirect_response()
        └── _get_fallback_response()
```

## Caracteristicas Principais

**EXTREMAMENTE RESTRITIVO**: Este agente foi projetado com foco total em seguranca para criancas:
- Herda de `BaseKidsAgent` para filtro de conteudo centralizado
- 70 topicos bloqueados (BLOCKED_TOPICS compartilhado)
- 162 topicos de design e arte permitidos (ALLOWED_TOPICS_DESIGN)
- Redirecionamento automatico de perguntas inadequadas
- Linguagem visual e poetica para criancas de 6-12 anos

## Filosofia de Ensino

> "A arte deve refletir a identidade e a beleza local"

- **Identidade**: Arte como expressao da cultura brasileira
- **Emocao**: Cores sao emocoes - cada cor conta uma historia
- **Simplicidade**: Formas simples podem transmitir ideias complexas
- **Beleza Universal**: Beleza esta em toda parte, so precisamos olhar
- **Funcionalidade**: Design e fazer as coisas funcionarem E serem bonitas

## Sobre Tarsila do Amaral

- Nascida em **Capivari, Sao Paulo** em 1886
- Pintora e desenhista brasileira, icone do **modernismo**
- Criadora do **Abaporu** (1928), obra mais valorizada da arte brasileira
- Participou da **Semana de Arte Moderna de 1922**
- Criou uma linguagem visual tipicamente brasileira
- Conhecida pelas **cores vibrantes** e **formas organicas**

## Capacidades

| Capability | Descricao |
|------------|-----------|
| `teach_color_theory` | Ensina teoria das cores |
| `explain_design_principles` | Explica principios de design |
| `inspire_creativity` | Inspira criatividade artistica |
| `teach_visual_harmony` | Ensina harmonia visual |
| `explain_ui_basics` | Explica conceitos basicos de UI/UX |

## Obras Usadas como Referencia

| Obra | Conceito de Design |
|------|-------------------|
| **Abaporu** (1928) | Formas grandes, cores quentes, brasilidade |
| **Antropofagia** (1929) | Mistura de elementos, criatividade |
| **A Negra** (1923) | Formas organicas, representacao |
| **Operarios** (1933) | Padroes, repeticao, diversidade |
| **Paisagem com Touro** | Natureza brasileira, cores tropicais |

## Conceitos de Design Ensinados

### Teoria das Cores

| Conceito | Explicacao Infantil |
|----------|-------------------|
| **Cores Quentes** | "Como o sol e o fogo - vermelho, laranja, amarelo!" |
| **Cores Frias** | "Como a agua e o ceu - azul, verde, roxo!" |
| **Contraste** | "Quando colocamos amarelo no azul - eles brigam!" |
| **Harmonia** | "Quando as cores conversam bem, sem brigar!" |

### Formas Basicas

| Forma | Analogia |
|-------|----------|
| **Circulo** | Lua, sol, bola, olho - suavidade |
| **Quadrado** | Janela, caixa, dado - estabilidade |
| **Triangulo** | Montanha, telhado, seta - movimento |

### Principios de Design

| Principio | Explicacao |
|-----------|------------|
| **Equilibrio** | Quando um desenho parece "certinho" |
| **Espaco** | O vazio tambem e importante no desenho |
| **Repeticao** | Padroes que se repetem criam ritmo |
| **Alinhamento** | Quando as coisas ficam organizadas |

## Seguranca de Conteudo

### BaseKidsAgent - Single Source of Truth

O agente herda de `BaseKidsAgent` que centraliza as safety features:

```python
from src.agents.base_kids_agent import BaseKidsAgent, BLOCKED_TOPICS

# BLOCKED_TOPICS (70 items) - shared across all kids agents
# Prevents drift between Monteiro Lobato, Tarsila, and future kids agents
```

### Topicos Bloqueados (70 - via BaseKidsAgent)

O agente bloqueia automaticamente qualquer mencao a:
- Violencia, conteudo adulto, drogas
- Atividades perigosas, hackeamento
- Conteudo assustador
- Discurso de odio
- Informacoes pessoais
- Politica

### Topicos Permitidos (162 - ALLOWED_TOPICS_DESIGN)

O agente aceita perguntas sobre:
- **Cores**: vermelho, azul, amarelo, verde, quente, fria, arcoiris
- **Formas**: circulo, quadrado, triangulo, estrela, coracao
- **Arte e Design**: pintura, desenho, bonito, elegante, criativo
- **Obras de Tarsila**: Abaporu, antropofagia, paisagem, modernismo
- **UI/UX**: botao, tela, app, layout, interface
- **Principios**: harmonia, contraste, equilibrio, padrao

## Exemplo de Uso

```python
from src.agents import KidsDesignAgent
from src.agents.deodoro import AgentContext, AgentMessage

# Criar agente
agent = KidsDesignAgent()

# Criar contexto
context = AgentContext(
    investigation_id="design-001",
    user_id="crianca-002",
    session_id="arte-001",
)

# Enviar mensagem
message = AgentMessage(
    action="chat",
    recipient="tarsila",
    payload={"message": "O que sao cores quentes?"},
    sender="crianca",
)

# Processar
response = await agent.process(message, context)
print(response.result["response"])
```

## Exemplo de Resposta

**Pergunta**: "O que e contraste?"

**Resposta**:
```
Contraste e a magia de colocar coisas diferentes lado a lado!

Imagina: voce coloca um circulo amarelo bem brilhante num fundo azul escuro.
O que acontece? O amarelo parece explodir de tao vivo! Isso e contraste!

E como quando voce usa uma roupa escura e um tenis colorido -
o tenis chama toda a atencao!

No design, usamos contraste para:
- Destacar coisas importantes
- Criar interesse visual
- Guiar os olhos de quem ve

Quer experimentar criar um desenho usando contraste?
```

## API Usage

### Chat Endpoint

```bash
POST /api/v1/chat/stream
Content-Type: application/json

{
  "message": "Me ensina sobre cores!",
  "session_id": "unique-session-id",
  "agent_id": "tarsila"
}
```

### Agent Aliases

| Alias | Routes To |
|-------|-----------|
| `amaral` | `tarsila` |
| `tarsila_do_amaral` | `tarsila` |
| `tarsila-do-amaral` | `tarsila` |

## Testes

### E2E Production Tests

```bash
# Run all E2E tests
python tests/e2e/test_kids_agents_production.py

# Run with pytest
pytest tests/e2e/test_kids_agents_production.py -v -k "tarsila"
```

### Test Scenarios (10/10 Passing)

| Scenario | Description | Status |
|----------|-------------|--------|
| `greeting` | Welcome and introduce art concepts | PASSED |
| `colors_concept` | Explain color theory in simple terms | PASSED |
| `character_design` | Help with character design concepts | PASSED |
| `composition` | Teach basic composition principles | PASSED |
| `contrast` | Explain contrast in simple terms | PASSED |
| `brazilian_art` | Share knowledge about Brazilian art | PASSED |
| `ui_design_for_kids` | Simple UI design concepts for children | PASSED |
| `encouragement` | Encourage when child is frustrated | PASSED |
| `off_topic_redirect` | Redirect off-topic questions | PASSED |
| `alias_amaral` | Test 'amaral' alias routes correctly | PASSED |

### Unit Tests

```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_tarsila.py -v
```

## Integracao com DSPy

O agente usa o servico DSPy para gerar respostas dinamicas via Maritaca AI (sabia-3.1):

```python
# In BaseKidsAgent._generate_response()
if _DSPY_AVAILABLE and _dspy_service and self.personality_prompt:
    response = await _dspy_service.generate_response(
        agent_name=self.name,
        personality_prompt=self.personality_prompt,
        user_message=message,
        context={
            "target_audience": "children_6_12",
            "style": "fun_educational",
            "max_words": 150,
        },
    )
```

Fallback para respostas pre-definidas quando o servico nao esta disponivel.

## Aplicacoes

### Educacao de UI/UX para Criancas

O agente pode ensinar conceitos basicos de design de interface:
- Como escolher cores para botoes
- Por que alguns apps sao mais bonitos
- O que torna uma tela "organizada"
- Como usar espaco vazio

### Desenvolvimento de Sensibilidade Estetica

- Apreciacao da arte brasileira
- Entendimento de combinacoes de cores
- Percepcao de formas e padroes
- Desenvolvimento do "olhar artistico"

## Metricas

| Metrica | Valor |
|---------|-------|
| Topicos bloqueados | 70 (via BaseKidsAgent) |
| Topicos permitidos | 162 |
| Obras de referencia | 5 |
| Capacidades | 5 |
| E2E Tests | 10/10 passing |
| Production Status | Live |

## Relacionamento com Outros Agentes

- **Monteiro Lobato**: Brother agent for programming education (same BaseKidsAgent)
- **Bo Bardi**: Frontend mentor (can collaborate on design topics)
- **Oscar Niemeyer**: Data visualization (for older learners)

## Autor

- **Data**: 2025-12-09
- **Autor**: Anderson H. Silva
- **Licenca**: Proprietary - All rights reserved
