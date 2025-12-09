"""
Module: agents.monteiro_lobato
Codinome: Monteiro Lobato - Educador de Programacao para Criancas
Description: RAG agent specialized in teaching programming concepts to kids using natural language
Author: Anderson H. Silva
Date: 2025-12-09
License: Proprietary - All rights reserved
"""

from typing import Any

from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)
from src.core import get_logger

# Import DSPy service for intelligent responses
try:
    from src.services.dspy_agents import get_dspy_agent_service

    _dspy_service = get_dspy_agent_service()
    _DSPY_AVAILABLE = _dspy_service.is_available() if _dspy_service else False
except ImportError:
    _dspy_service = None
    _DSPY_AVAILABLE = False


# =============================================================================
# BLOCKED TOPICS - EXTREMELY RESTRICTIVE CONTENT FILTER
# =============================================================================
BLOCKED_TOPICS = [
    # Violence
    "violencia",
    "violence",
    "matar",
    "kill",
    "morte",
    "death",
    "arma",
    "weapon",
    "gun",
    "guerra",
    "war",
    "sangue",
    "blood",
    "briga",
    "fight",
    "lutar",
    # Adult content
    "sexo",
    "sex",
    "pornografia",
    "adulto",
    "adult",
    "namorar",
    "beijar",
    # Drugs and substances
    "droga",
    "drug",
    "alcool",
    "alcohol",
    "cerveja",
    "beer",
    "cigarro",
    "cigarette",
    "fumar",
    "smoke",
    # Dangerous activities
    "hackear",
    "hack",
    "invadir",
    "roubar",
    "steal",
    "crime",
    "ilegal",
    "illegal",
    # Scary content
    "terror",
    "horror",
    "medo",
    "fear",
    "assustador",
    "scary",
    "pesadelo",
    "nightmare",
    "monstro",
    "monster",
    # Hate speech
    "odio",
    "hate",
    "racismo",
    "racism",
    "preconceito",
    "bullying",
    # Personal information
    "senha",
    "password",
    "cartao",
    "card",
    "banco",
    "bank",
    "dinheiro",
    "money",
    # Politics and controversy
    "politica",
    "politics",
    "eleicao",
    "election",
    "presidente",
    "presidente",
]

# =============================================================================
# ALLOWED TOPICS - SAFE CONTENT FOR KIDS
# =============================================================================
ALLOWED_TOPICS = [
    # Programming concepts
    "programacao",
    "programming",
    "codigo",
    "code",
    "algoritmo",
    "algorithm",
    "variavel",
    "variable",
    "funcao",
    "function",
    "loop",
    "repeticao",
    "condicao",
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
    "list",
    "numero",
    "number",
    "texto",
    "text",
    "string",
    "jogo",
    "game",
    "robo",
    "robot",
    "computador",
    "computer",
    "internet",
    "site",
    "app",
    "aplicativo",
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
    # Nature and animals
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
    # Greetings and basic conversation
    "ola",
    "oi",
    "hello",
    "hi",
    "tchau",
    "bye",
    "obrigado",
    "thanks",
    "por favor",
    "please",
    "como",
    "how",
    "porque",
    "why",
    "quando",
    "when",
    "onde",
    "where",
    "quem",
    "who",
    "o que",
    "what",
    "ajuda",
    "help",
]


class KidsProgrammingAgent(BaseAgent):
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

    CARACTERISTICAS DO AGENTE:
    - EXTREMAMENTE RESTRITIVO: So fala sobre programacao e temas infantis
    - Usa linguagem simples e acessivel para criancas de 6-12 anos
    - Referencias ao Sitio do Picapau Amarelo para ilustrar conceitos
    - Transforma codigo em historias e aventuras
    - Nunca usa jargao tecnico sem explicar de forma divertida

    EXEMPLOS DE EXPLICACOES:
    - Variavel: "E como uma caixinha onde a Emilia guarda suas ideias!"
    - Loop: "E quando o Pedrinho faz a mesma coisa varias vezes, tipo comer brigadeiro!"
    - Funcao: "E como uma receita da Tia Nastacia - voce segue os passos e sai algo gostoso!"
    - Condicional: "SE chover, ENTAO Narizinho fica em casa, SENAO vai brincar no sitio!"
    """

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
        )
        self.logger = get_logger(__name__)
        self.config = config or {}

        # Personality configuration - DIVERTIDO E EDUCATIVO
        self.personality_prompt = """Voce e Monteiro Lobato, o criador do Sitio do Picapau Amarelo!

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

EXEMPLO DE RESPOSTA:
"Ola, pequeno programador! Que bom te ver no Sitio!

Sabe o que e uma variavel? E como a caixinha onde a Emilia guarda suas ideias malucas!
Imagina que a Emilia tem uma caixa chamada 'idade'. Dentro dela, ela coloca o numero 8.
Quando alguem pergunta 'Emilia, quantos anos voce tem?', ela abre a caixa e mostra: 8!

Em programacao, escrevemos assim:
idade = 8

Facil, ne? E so uma caixinha com nome!
Quer tentar criar sua propria caixinha agora?"

LEMBRE-SE: Voce e um educador GENTIL e PACIENTE. Criancas podem errar e perguntar varias vezes - e assim que se aprende!"""

        self.logger.info(
            "kids_programming_agent_initialized",
            agent_name=self.name,
            dspy_available=_DSPY_AVAILABLE,
        )

    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info(f"{self.name} agent initialized - Bem-vindo ao Sitio!")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info(f"{self.name} agent shutting down - Ate a proxima aventura!")

    def _is_content_safe(self, text: str) -> tuple[bool, str]:
        """
        Check if content is safe for kids.

        Args:
            text: Text to check

        Returns:
            Tuple of (is_safe, reason)
        """
        text_lower = text.lower()

        # Check for blocked topics
        for blocked in BLOCKED_TOPICS:
            if blocked in text_lower:
                return False, f"Conteudo nao apropriado detectado: {blocked}"

        return True, "Conteudo seguro"

    def _is_topic_allowed(self, text: str) -> bool:
        """
        Check if topic is within allowed scope.

        Args:
            text: Text to check

        Returns:
            True if topic is allowed
        """
        text_lower = text.lower()

        # Check if any allowed topic is mentioned
        for allowed in ALLOWED_TOPICS:
            if allowed in text_lower:
                return True

        # If no specific topic detected, allow general questions
        general_patterns = ["o que", "como", "porque", "quando", "onde", "quem", "?"]
        for pattern in general_patterns:
            if pattern in text_lower:
                return True

        return False

    def _get_safe_redirect_response(self) -> str:
        """Get a safe redirect response when content is not appropriate."""
        return """Opa, amiguinho! Essa pergunta e bem interessante, mas sabe o que seria mais legal?

Vamos falar sobre programacao! Aqui no Sitio do Picapau Amarelo, a Emilia e eu adoramos criar coisas incriveis com codigo!

Quer que eu te ensine:
- Como fazer um joguinho simples?
- O que sao variaveis (as caixinhas magicas)?
- Como o computador pensa com "SE" e "SENAO"?

Escolhe um e vamos nessa aventura juntos!"""

    async def _generate_response(self, message: str, context: AgentContext) -> str:
        """
        Generate a safe, educational response for kids.

        Args:
            message: User message
            context: Agent context

        Returns:
            Safe response string
        """
        # Check content safety
        is_safe, reason = self._is_content_safe(message)
        if not is_safe:
            self.logger.warning(
                "unsafe_content_detected",
                reason=reason,
                investigation_id=context.investigation_id,
            )
            return self._get_safe_redirect_response()

        # Check if topic is allowed
        if not self._is_topic_allowed(message):
            self.logger.info(
                "topic_redirect",
                message=message[:50],
                investigation_id=context.investigation_id,
            )
            return self._get_safe_redirect_response()

        # Try DSPy service if available
        if _DSPY_AVAILABLE and _dspy_service:
            try:
                response = await _dspy_service.generate_response(
                    agent_name="monteiro_lobato",
                    personality_prompt=self.personality_prompt,
                    user_message=message,
                    context={
                        "target_audience": "children_6_12",
                        "style": "fun_educational",
                        "max_words": 150,
                    },
                )
                if response:
                    # Double-check the generated response is safe
                    is_safe, _ = self._is_content_safe(response)
                    if is_safe:
                        return response
            except Exception as e:
                self.logger.warning(f"DSPy generation failed: {e}")

        # Fallback to predefined responses
        return self._get_fallback_response(message)

    def _get_fallback_response(self, message: str) -> str:
        """
        Get a predefined fallback response based on message content.

        Args:
            message: User message

        Returns:
            Appropriate fallback response
        """
        message_lower = message.lower()

        # Programming concepts
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

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """
        Process a message from a kid and return an educational response.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            AgentResponse with educational content
        """
        try:
            self.logger.info(
                "kids_message_received",
                investigation_id=context.investigation_id,
                agent_name=self.name,
                action=message.action,
            )

            # Extract user message
            user_message = ""
            if isinstance(message.payload, dict):
                user_message = message.payload.get(
                    "message", message.payload.get("query", "")
                )
            elif isinstance(message.payload, str):
                user_message = message.payload

            if not user_message:
                user_message = "ola"

            # Generate safe, educational response
            response_text = await self._generate_response(user_message, context)

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={
                    "response": response_text,
                    "agent": "monteiro_lobato",
                    "target_audience": "kids_6_12",
                    "topic": "programming_education",
                },
                metadata={
                    "content_filtered": True,
                    "safe_for_kids": True,
                    "educational_focus": "programming",
                },
            )

        except Exception as e:
            self.logger.error(f"Error processing kids message: {e}")
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                result={
                    "response": "Ops! Algo deu errado aqui no Sitio. Pode tentar de novo?",
                    "agent": "monteiro_lobato",
                },
            )


# Aliases for easier imports
MonteiroLobatoAgent = KidsProgrammingAgent
LobatoAgent = KidsProgrammingAgent
