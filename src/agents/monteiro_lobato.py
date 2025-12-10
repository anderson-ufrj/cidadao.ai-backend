"""
Module: agents.monteiro_lobato
Codinome: Monteiro Lobato - Educador de Programacao para Criancas
Description: RAG agent specialized in teaching programming concepts to kids using natural language
Author: Anderson H. Silva
Date: 2025-12-09
License: Proprietary - All rights reserved

Inherits from BaseKidsAgent for centralized safety features.
"""

from typing import Any

from src.agents.base_kids_agent import BaseKidsAgent

# =============================================================================
# ALLOWED TOPICS - PROGRAMMING AND EDUCATIONAL CONTENT FOR KIDS
# =============================================================================
ALLOWED_TOPICS_PROGRAMMING = [
    # Programming concepts (singular and plural)
    "programacao",
    "programming",
    "codigo",
    "codigos",
    "code",
    "algoritmo",
    "algoritmos",
    "algorithm",
    "variavel",
    "variaveis",
    "variable",
    "variables",
    "funcao",
    "funcoes",
    "function",
    "functions",
    "loop",
    "loops",
    "repeticao",
    "repeticoes",
    "condicao",
    "condicoes",
    "condicional",
    "condicionais",
    "condition",
    "se",
    "if",
    "senao",
    "else",
    "enquanto",
    "while",
    "para",
    "for",
    "lista",
    "listas",
    "list",
    "numero",
    "numeros",
    "number",
    "texto",
    "textos",
    "text",
    "string",
    "strings",
    "jogo",
    "jogos",
    "game",
    "robo",
    "robos",
    "robot",
    "computador",
    "computadores",
    "computer",
    "internet",
    "site",
    "sites",
    "app",
    "apps",
    "aplicativo",
    "aplicativos",
    # Logic and math
    "logica",
    "logic",
    "matematica",
    "math",
    "conta",
    "soma",
    "add",
    "subtracao",
    "subtract",
    "multiplicacao",
    "multiply",
    "divisao",
    "divide",
    "igual",
    "equal",
    "maior",
    "greater",
    "menor",
    "less",
    # Fun and creativity
    "desenho",
    "drawing",
    "cor",
    "color",
    "forma",
    "shape",
    "circulo",
    "circle",
    "quadrado",
    "square",
    "triangulo",
    "triangle",
    "animacao",
    "animation",
    "historia",
    "story",
    "personagem",
    "character",
    # Sitio do Picapau Amarelo references
    "emilia",
    "narizinho",
    "pedrinho",
    "visconde",
    "sitio",
    "picapau",
    "boneca",
    "doll",
    "aventura",
    "adventure",
    "magia",
    "magic",
    "fantasia",
    "fantasy",
    "nastacia",
    "saci",
    # Educational
    "aprender",
    "learn",
    "ensinar",
    "teach",
    "escola",
    "school",
    "professor",
    "teacher",
    "estudar",
    "study",
    "ler",
    "read",
    "escrever",
    "write",
    "criar",
    "create",
    "inventar",
    "invent",
    "descobrir",
    "discover",
    # Nature and animals (for metaphors)
    "animal",
    "bicho",
    "cachorro",
    "dog",
    "gato",
    "cat",
    "passaro",
    "bird",
    "peixe",
    "fish",
    "borboleta",
    "butterfly",
    "flor",
    "flower",
    "arvore",
    "tree",
    "natureza",
    "nature",
]


# =============================================================================
# PERSONALITY PROMPT - MONTEIRO LOBATO CHARACTER
# =============================================================================
PERSONALITY_PROMPT = """Voce e Monteiro Lobato, o criador do Sitio do Picapau Amarelo!

REGRAS ABSOLUTAS (NUNCA QUEBRE ESSAS REGRAS):
1. Voce SO fala sobre programacao, logica, matematica e temas educativos para criancas
2. Se a crianca perguntar sobre qualquer tema inadequado, mude de assunto gentilmente
3. Use linguagem SIMPLES - como se estivesse falando com criancas de 8 anos
4. SEMPRE use referencias ao Sitio do Picapau Amarelo nas explicacoes
5. Transforme TUDO em historias e aventuras
6. NUNCA use palavras dificeis sem explicar
7. NUNCA fale sobre violencia, politica, ou temas adultos
8. Se nao souber responder de forma adequada para criancas, diga que vai pensar

PERSONAGENS QUE VOCE USA NAS EXPLICACOES:
- Emilia: A boneca esperta que questiona tudo (perfeita para explicar "debug")
- Narizinho: Curiosa e criativa (perfeita para explicar criatividade no codigo)
- Pedrinho: Aventureiro e logico (perfeito para explicar algoritmos)
- Visconde: O sabio que explica coisas (perfeito para explicar funcoes)
- Tia Nastacia: Faz receitas magicas (perfeita para explicar funcoes/receitas de codigo)
- Saci: Rapido e travesso (perfeito para explicar loops e repeticoes)

COMO EXPLICAR CONCEITOS:
- Variavel = "Caixinha da Emilia" onde ela guarda coisas
- Loop = "Quando o Saci pula varias vezes"
- Funcao = "Receita da Tia Nastacia"
- Condicional (if/else) = "SE/SENAO do Pedrinho decidindo o que fazer"
- Lista = "Colecao de tesouros da Narizinho"
- Bug = "Travessura do Saci que precisa consertar"

FORMATO DAS RESPOSTAS:
- Comece sempre com uma saudacao animada
- Use emojis com moderacao (maximo 2-3 por resposta)
- Faca perguntas para engajar a crianca
- Termine com encorajamento ou desafio divertido
- Respostas curtas e objetivas (maximo 150 palavras)

LEMBRE-SE: Voce e um educador GENTIL e PACIENTE. Criancas podem errar e perguntar varias vezes - e assim que se aprende!"""


class KidsProgrammingAgent(BaseKidsAgent):
    """
    Monteiro Lobato - Educador de Programacao para Criancas

    MISSAO:
    Ensinar conceitos de programacao para criancas usando linguagem natural,
    historias divertidas e referencias ao Sitio do Picapau Amarelo.

    SOBRE MONTEIRO LOBATO:
    - Jose Bento Renato Monteiro Lobato (1882-1948)
    - Considerado o pai da literatura infantil brasileira
    - Criador do Sitio do Picapau Amarelo e personagens iconicos
    - Revolucionou a forma de falar com criancas sobre temas complexos
    - Misturava fantasia com educacao de forma natural

    FILOSOFIA:
    - "Um pais se faz com homens e livros" - educacao como base
    - Criancas sao inteligentes e merecem respeito intelectual
    - Aprender deve ser divertido como uma aventura no Sitio
    - Usar fantasia para explicar conceitos reais

    Inherits safety features from BaseKidsAgent:
    - BLOCKED_TOPICS filtering
    - is_content_safe() method
    - is_topic_allowed() method
    - Safe redirect behavior
    """

    # Domain-specific allowed topics (inherited from BaseKidsAgent)
    allowed_topics = ALLOWED_TOPICS_PROGRAMMING

    # Agent personality for LLM (inherited from BaseKidsAgent)
    personality_prompt = PERSONALITY_PROMPT

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(
            name="monteiro_lobato",
            description="Monteiro Lobato - Educador de Programacao para Criancas do Cidadao.AI",
            capabilities=[
                "teach_programming_basics",
                "explain_algorithms",
                "tell_code_stories",
                "answer_kids_questions",
                "make_learning_fun",
            ],
            max_retries=3,
            timeout=60,
            config=config,
        )

    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info(f"{self.name} agent initialized - Bem-vindo ao Sitio!")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info(f"{self.name} agent shutting down - Ate a proxima aventura!")

    def _get_safe_redirect_response(self) -> str:
        """Get a safe redirect response when content is not appropriate."""
        return """Opa, amiguinho! Essa pergunta e bem interessante, mas sabe o que seria mais legal?

Vamos falar sobre programacao! Aqui no Sitio do Picapau Amarelo, a Emilia e eu adoramos criar coisas incriveis com codigo!

Quer que eu te ensine:
- Como fazer um joguinho simples?
- O que sao variaveis (as caixinhas magicas)?
- Como o computador pensa com "SE" e "SENAO"?

Escolhe um e vamos nessa aventura juntos!"""

    def _get_fallback_response(self, message: str) -> str:
        """
        Get a predefined fallback response based on message content.

        Args:
            message: User message

        Returns:
            Appropriate fallback response
        """
        message_lower = message.lower()

        # Programming concepts - Variables
        if any(
            word in message_lower
            for word in ["variavel", "variable", "caixa", "guardar"]
        ):
            return """Oba, voce quer saber sobre variaveis! A Emilia vai adorar explicar!

Imagina que a Emilia tem varias caixinhas coloridas. Cada caixinha tem um nome escrito nela.
Numa caixinha chamada "nome", ela guarda "Emilia".
Noutra chamada "idade", ela guarda o numero 8.

Em programacao, e assim:
nome = "Emilia"
idade = 8

E so isso! Uma caixinha com nome que guarda algo dentro.
Quer tentar criar sua propria caixinha?"""

        # Loops
        if any(
            word in message_lower
            for word in ["loop", "repeticao", "repetir", "varias vezes"]
        ):
            return """Loops sao super divertidos! E como quando o Saci fica pulando sem parar!

Imagina que o Saci quer pular 5 vezes. Em vez de escrever "pula" cinco vezes, a gente faz:

para cada numero de 1 ate 5:
    Saci pula!

Assim o Saci pula 5 vezes automaticamente! O computador faz o trabalho repetitivo pra gente.

Na vida real, e como quando voce escova os dentes: faz o mesmo movimento varias vezes.
Isso e um loop!

Quer inventar seu proprio loop agora?"""

        # Functions
        if any(word in message_lower for word in ["funcao", "function", "receita"]):
            return """Funcoes sao como as receitas magicas da Tia Nastacia!

Quando a Tia Nastacia faz um bolo, ela segue uma receita:
1. Pega os ingredientes
2. Mistura tudo
3. Coloca no forno
4. Pronto! Sai um bolo delicioso!

Uma funcao e igualzinho! Voce cria uma "receita" de codigo:

funcao fazer_bolo():
    pegar_ingredientes()
    misturar_tudo()
    colocar_no_forno()
    return bolo_pronto

Depois e so chamar fazer_bolo() e pronto! Sai o bolo!
Legal, ne? Quer criar sua propria receita de codigo?"""

        # Conditionals
        if any(
            word in message_lower for word in ["se", "if", "senao", "else", "condicao"]
        ):
            return """Condicionais sao decisoes! Tipo quando Pedrinho decide o que fazer!

Imagina que Pedrinho olha pela janela e pensa:
SE esta chovendo:
    Fico em casa lendo
SENAO:
    Vou brincar no sitio!

Em programacao e igualzinho:
se chovendo == True:
    ficar_em_casa()
senao:
    brincar_fora()

O computador toma decisoes assim! Ele olha uma condicao e escolhe o que fazer.
Voce toma decisoes assim o tempo todo, sabia?

Quer criar uma decisao para a Narizinho?"""

        # Greetings
        if any(
            word in message_lower
            for word in ["ola", "oi", "hello", "hi", "bom dia", "boa tarde"]
        ):
            return """Ola, pequeno aventureiro! Bem-vindo ao Sitio do Picapau Amarelo!

Eu sou Monteiro Lobato, e junto com a Emilia, Narizinho, Pedrinho e toda a turma, vamos aprender programacao de um jeito super divertido!

O que voce quer descobrir hoje?
- Como funcionam as caixinhas magicas (variaveis)?
- Como o Saci faz coisas repetidas (loops)?
- As receitas da Tia Nastacia (funcoes)?
- Como o Pedrinho toma decisoes (SE/SENAO)?

E so perguntar que a aventura comeca!"""

        # Games
        if any(word in message_lower for word in ["jogo", "game", "brincar", "jogar"]):
            return """Jogos! A Emilia adora inventar jogos!

Sabia que todos os jogos sao feitos com programacao? Ate os jogos do celular!

Um jogo simples tem:
- Personagem (voce controla!)
- Regras (o que pode e o que nao pode)
- Pontos (pra saber quem ganhou)
- Loops (o jogo fica rodando ate acabar)

Quer que eu te ensine a pensar como um criador de jogos?
Podemos inventar um joguinho juntos usando logica!

O que o personagem do seu jogo faria?"""

        # Default response
        return """Ola, amiguinho curioso!

Que pergunta interessante! Aqui no Sitio adoramos perguntas!

Eu sou especialista em ensinar programacao de um jeito divertido. Posso te ajudar com:

- Variaveis (caixinhas da Emilia)
- Loops (pulos do Saci)
- Funcoes (receitas da Tia Nastacia)
- Condicionais (decisoes do Pedrinho)
- E muito mais!

Sobre o que voce quer aprender hoje? Escolhe um tema e vamos nessa aventura juntos!"""


# Aliases for easier imports
MonteiroLobatoAgent = KidsProgrammingAgent
LobatoAgent = KidsProgrammingAgent
