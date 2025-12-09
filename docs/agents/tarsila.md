# Tarsila do Amaral - Educadora de Design para Criancas

**Codinome**: Tarsila do Amaral
**Tipo**: Kids Design Education Agent
**Arquivo**: `src/agents/tarsila.py`
**Classe**: `KidsDesignAgent`
**Aliases**: `TarsilaAgent`, `TarsilaDoAmaralAgent`

## Visao Geral

Tarsila do Amaral e a agente educadora de design e estetica para criancas do Cidadao.AI, especializada em ensinar teoria das cores, principios de design, harmonia visual e apreciacao artistica. Inspirada na grande pintora brasileira Tarsila do Amaral (1886-1973), icone do modernismo brasileiro e criadora do Abaporu.

## Caracteristicas Principais

**EXTREMAMENTE RESTRITIVO**: Este agente foi projetado com foco total em seguranca para criancas:
- Filtro de conteudo rigoroso (50+ topicos bloqueados)
- Apenas topicos de design e arte permitidos (100+ topicos seguros)
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

### Topicos Bloqueados (50+)

O agente bloqueia automaticamente qualquer mencao a:
- Violencia, conteudo adulto, drogas
- Atividades perigosas, hackeamento
- Conteudo assustador
- Discurso de odio
- Informacoes pessoais
- Politica

### Topicos Permitidos (100+)

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

**Pergunta**: "O que sao cores quentes?"

**Resposta**:
```
Ah, as cores quentes! Sao minhas favoritas para pintar o Brasil!

VERMELHO e como o coracao batendo - cheio de energia e paixao!
LARANJA e o por do sol em Copacabana - alegria pura!
AMARELO e o nosso sol tropical - luz e felicidade!

No meu quadro Abaporu, usei muito amarelo e tons quentes. Sabe por que?
Porque queria mostrar o calor da nossa terra brasileira!

Cores quentes parecem "pular" da tela! Elas chamam atencao, gritam "olha pra mim!"

Quando voce quer que algo seja notado num desenho, use cores quentes!
E como colocar um solzinho brilhante no seu papel.

Qual cor quente voce mais gosta?
```

## Testes

```bash
# Executar testes
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_tarsila.py -v

# Testes especificos
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_tarsila.py::TestDesignContentSafety -v
```

## Integracao com DSPy

O agente pode usar o servico DSPy para gerar respostas dinamicas via Maritaca AI (sabia-3.1), com fallback para respostas pre-definidas quando o servico nao esta disponivel.

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

- **Topicos bloqueados**: 50+
- **Topicos permitidos**: 100+
- **Obras de referencia**: 5
- **Capacidades**: 5
- **Cobertura de testes**: 34+ testes unitarios
