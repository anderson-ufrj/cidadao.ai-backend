# Monteiro Lobato - Educador de Programacao para Criancas

**Codinome**: Jose Bento Renato Monteiro Lobato
**Tipo**: Kids Programming Education Agent
**Arquivo**: `src/agents/monteiro_lobato.py`
**Classe**: `KidsProgrammingAgent`
**Aliases**: `MonteiroLobatoAgent`, `LobatoAgent`

## Visao Geral

Monteiro Lobato e o agente educador de programacao para criancas do Cidadao.AI, especializado em ensinar conceitos de codigo e logica usando linguagem natural, historias divertidas e referencias ao Sitio do Picapau Amarelo. Inspirado no grande escritor brasileiro Jose Bento Renato Monteiro Lobato (1882-1948), considerado o pai da literatura infantil brasileira.

## Caracteristicas Principais

**EXTREMAMENTE RESTRITIVO**: Este agente foi projetado com foco total em seguranca para criancas:
- Filtro de conteudo rigoroso (50+ topicos bloqueados)
- Apenas topicos educativos permitidos (100+ topicos seguros)
- Redirecionamento automatico de perguntas inadequadas
- Linguagem simples para criancas de 6-12 anos

## Filosofia de Ensino

> "Um pais se faz com homens e livros" - Monteiro Lobato

- **Democratizacao**: Educacao acessivel para todas as criancas
- **Respeito**: Criancas sao inteligentes e merecem respeito intelectual
- **Diversao**: Aprender deve ser divertido como uma aventura no Sitio
- **Fantasia**: Usar fantasia para explicar conceitos reais

## Sobre Monteiro Lobato

- Nascido em **Taubate, Sao Paulo** em 1882
- Criador do **Sitio do Picapau Amarelo**
- Inventor de personagens iconicos: Emilia, Narizinho, Pedrinho, Visconde
- Revolucionou a forma de falar com criancas sobre temas complexos
- Misturava fantasia com educacao de forma natural

## Capacidades

| Capability | Descricao |
|------------|-----------|
| `teach_programming_basics` | Ensina conceitos basicos de programacao |
| `explain_algorithms` | Explica algoritmos de forma simples |
| `tell_code_stories` | Transforma codigo em historias |
| `answer_kids_questions` | Responde perguntas de criancas |
| `make_learning_fun` | Torna o aprendizado divertido |

## Personagens Usados nas Explicacoes

| Personagem | Conceito de Programacao |
|------------|------------------------|
| **Emilia** | Debug - questiona tudo, encontra erros |
| **Narizinho** | Criatividade - pensa fora da caixa |
| **Pedrinho** | Algoritmos - logico e aventureiro |
| **Visconde** | Funcoes - o sabio que explica |
| **Tia Nastacia** | Funcoes/Receitas - cria coisas seguindo passos |
| **Saci** | Loops - rapido e repetitivo |

## Analogias para Conceitos

| Conceito | Analogia |
|----------|----------|
| Variavel | "Caixinha da Emilia" onde ela guarda coisas |
| Loop | "Quando o Saci pula varias vezes" |
| Funcao | "Receita da Tia Nastacia" |
| Condicional (if/else) | "SE/SENAO do Pedrinho decidindo o que fazer" |
| Lista | "Colecao de tesouros da Narizinho" |
| Bug | "Travessura do Saci que precisa consertar" |

## Seguranca de Conteudo

### Topicos Bloqueados (50+)

O agente bloqueia automaticamente qualquer mencao a:
- Violencia (matar, arma, guerra, sangue)
- Conteudo adulto (sexo, pornografia)
- Drogas e substancias (droga, alcool, cigarro)
- Atividades perigosas (hackear, roubar, crime)
- Conteudo assustador (terror, monstro, pesadelo)
- Discurso de odio (racismo, bullying)
- Informacoes pessoais (senha, cartao, banco)
- Politica (eleicao, presidente)

### Topicos Permitidos (100+)

O agente aceita perguntas sobre:
- **Programacao**: variavel, funcao, loop, algoritmo, jogo, robo
- **Logica e Matematica**: soma, subtracao, igual, maior, menor
- **Criatividade**: desenho, cor, forma, animacao, historia
- **Sitio do Picapau**: Emilia, Narizinho, Pedrinho, Visconde, aventura
- **Educacional**: aprender, escola, estudar, criar, inventar
- **Natureza e Animais**: cachorro, gato, borboleta, arvore

## Exemplo de Uso

```python
from src.agents import KidsProgrammingAgent
from src.agents.deodoro import AgentContext, AgentMessage

# Criar agente
agent = KidsProgrammingAgent()

# Criar contexto
context = AgentContext(
    investigation_id="kids-001",
    user_id="crianca-001",
    session_id="aprendizado-001",
)

# Enviar mensagem
message = AgentMessage(
    action="chat",
    recipient="monteiro_lobato",
    payload={"message": "O que e uma variavel?"},
    sender="crianca",
)

# Processar
response = await agent.process(message, context)
print(response.result["response"])
```

## Exemplo de Resposta

**Pergunta**: "O que e uma variavel?"

**Resposta**:
```
Oba, voce quer saber sobre variaveis! A Emilia vai adorar explicar!

Imagina que a Emilia tem varias caixinhas coloridas. Cada caixinha tem um nome escrito nela.
Numa caixinha chamada "nome", ela guarda "Emilia".
Noutra chamada "idade", ela guarda o numero 8.

Em programacao, e assim:
nome = "Emilia"
idade = 8

E so isso! Uma caixinha com nome que guarda algo dentro.
Quer tentar criar sua propria caixinha?
```

## Testes

```bash
# Executar testes
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_monteiro_lobato.py -v

# Testes especificos
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_monteiro_lobato.py::TestContentSafety -v
```

## Integracao com DSPy

O agente pode usar o servico DSPy para gerar respostas dinamicas via Maritaca AI (sabia-3.1), com fallback para respostas pre-definidas quando o servico nao esta disponivel.

## Metricas

- **Topicos bloqueados**: 50+
- **Topicos permitidos**: 100+
- **Personagens do Sitio**: 6
- **Capacidades**: 5
- **Cobertura de testes**: 25+ testes unitarios
