"""
Module: agents.tarsila
Codinome: Tarsila do Amaral - Educadora de Design para Criancas
Description: RAG agent specialized in teaching design and aesthetics to kids
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
]

# =============================================================================
# ALLOWED TOPICS - SAFE DESIGN CONTENT FOR KIDS
# =============================================================================
ALLOWED_TOPICS = [
    # Colors
    "cor",
    "cores",
    "color",
    "colors",
    "vermelho",
    "red",
    "azul",
    "blue",
    "amarelo",
    "yellow",
    "verde",
    "green",
    "laranja",
    "orange",
    "roxo",
    "purple",
    "rosa",
    "pink",
    "marrom",
    "brown",
    "preto",
    "black",
    "branco",
    "white",
    "colorido",
    "colorful",
    "arcoiris",
    "rainbow",
    # Shapes
    "forma",
    "formas",
    "shape",
    "shapes",
    "circulo",
    "circle",
    "quadrado",
    "square",
    "triangulo",
    "triangle",
    "retangulo",
    "rectangle",
    "estrela",
    "star",
    "coracao",
    "heart",
    "oval",
    "losango",
    "diamond",
    # Art and design
    "arte",
    "art",
    "pintura",
    "painting",
    "desenho",
    "drawing",
    "design",
    "bonito",
    "beautiful",
    "lindo",
    "pretty",
    "elegante",
    "elegant",
    "criativo",
    "creative",
    "artistico",
    "artistic",
    "visual",
    "estetica",
    "aesthetic",
    "estilo",
    "style",
    # Tarsila's works
    "abaporu",
    "antropofagia",
    "operarios",
    "paisagem",
    "landscape",
    "natureza",
    "nature",
    "brasil",
    "brazil",
    "tropical",
    "moderno",
    "modern",
    "modernismo",
    "modernism",
    # UI/UX concepts
    "tela",
    "screen",
    "botao",
    "button",
    "icone",
    "icon",
    "layout",
    "interface",
    "pagina",
    "page",
    "site",
    "website",
    "app",
    "aplicativo",
    "menu",
    "navegacao",
    "navigation",
    # Design principles
    "harmonia",
    "harmony",
    "equilibrio",
    "balance",
    "contraste",
    "contrast",
    "repeticao",
    "repetition",
    "padrao",
    "pattern",
    "simetria",
    "symmetry",
    "proporcao",
    "proportion",
    "espaco",
    "space",
    "alinhamento",
    "alignment",
    # Creative activities
    "criar",
    "create",
    "inventar",
    "invent",
    "imaginar",
    "imagine",
    "sonhar",
    "dream",
    "fantasia",
    "fantasy",
    "inspiracao",
    "inspiration",
    "ideia",
    "idea",
    # Nature elements
    "sol",
    "sun",
    "lua",
    "moon",
    "flor",
    "flower",
    "arvore",
    "tree",
    "folha",
    "leaf",
    "agua",
    "water",
    "ceu",
    "sky",
    "nuvem",
    "cloud",
    "montanha",
    "mountain",
    # Materials
    "papel",
    "paper",
    "tinta",
    "paint",
    "lapis",
    "pencil",
    "giz",
    "chalk",
    "pincel",
    "brush",
    "tela",
    "canvas",
    # Greetings and basic
    "ola",
    "oi",
    "hello",
    "hi",
    "tchau",
    "bye",
    "obrigado",
    "thanks",
    "ajuda",
    "help",
    "como",
    "how",
    "porque",
    "why",
    "o que",
    "what",
]


class KidsDesignAgent(BaseAgent):
    """
    Tarsila do Amaral - Educadora de Design para Criancas

    MISSAO:
    Ensinar conceitos de design, estetica e arte para criancas usando
    linguagem visual, cores vibrantes e referencias ao modernismo brasileiro.

    SOBRE TARSILA DO AMARAL:
    - Tarsila do Amaral (1886-1973)
    - Pintora e desenhista brasileira, icone do modernismo
    - Criadora do Abaporu, obra mais valorizada da arte brasileira
    - Participou da Semana de Arte Moderna de 1922
    - Criou uma linguagem visual tipicamente brasileira
    - Cores vibrantes, formas organicas, identidade tropical

    FILOSOFIA:
    - Arte deve refletir a identidade e a beleza local
    - Cores sao emocoes - cada cor conta uma historia
    - Formas simples podem transmitir ideias complexas
    - Beleza esta em toda parte, so precisamos olhar
    - Design e fazer as coisas funcionarem E serem bonitas

    CARACTERISTICAS DO AGENTE:
    - EXTREMAMENTE RESTRITIVO: So fala sobre design, arte e estetica
    - Usa linguagem visual e poetica adequada para criancas
    - Referencias as obras de Tarsila para ilustrar conceitos
    - Ensina teoria das cores de forma divertida
    - Explica harmonia e equilibrio visual com exemplos do dia a dia

    OBRAS QUE USA COMO REFERENCIA:
    - Abaporu (1928): Formas grandes, cores quentes, brasilidade
    - Antropofagia (1929): Mistura de elementos, criatividade
    - A Negra (1923): Formas organicas, representacao
    - Operarios (1933): Padroes, repeticao, diversidade
    - Paisagem com Touro: Natureza brasileira, cores tropicais

    EXEMPLOS DE EXPLICACOES:
    - Cores quentes: "Sao como o sol e o fogo - vermelho, laranja, amarelo!"
    - Cores frias: "Sao como a agua e o ceu - azul, verde, roxo!"
    - Contraste: "E quando colocamos o amarelo do sol no azul do ceu!"
    - Harmonia: "E quando as cores conversam bem entre si, sem brigar!"
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(
            name="tarsila",
            description="Tarsila do Amaral - Educadora de Design e Estetica para Criancas",
            capabilities=[
                "teach_color_theory",
                "explain_design_principles",
                "inspire_creativity",
                "teach_visual_harmony",
                "explain_ui_basics",
            ],
            max_retries=3,
            timeout=60,
        )
        self.logger = get_logger(__name__)
        self.config = config or {}

        # Personality configuration - ARTISTICA E INSPIRADORA
        self.personality_prompt = """Voce e Tarsila do Amaral, a grande pintora brasileira!

REGRAS ABSOLUTAS (NUNCA QUEBRE ESSAS REGRAS):
1. Voce SO fala sobre design, arte, cores, formas e estetica
2. Se a crianca perguntar sobre qualquer tema inadequado, mude de assunto gentilmente
3. Use linguagem VISUAL e POETICA - como se estivesse pintando com palavras
4. SEMPRE use referencias as suas obras e ao Brasil nas explicacoes
5. Transforme conceitos de design em imagens mentais coloridas
6. NUNCA use palavras dificeis sem explicar
7. NUNCA fale sobre violencia, politica, ou temas adultos
8. Celebre a criatividade e a imaginacao da crianca

COMO VOCE FALA:
- Com entusiasmo sobre cores: "Ah, o amarelo! E a cor do nosso sol brasileiro!"
- Com poesia: "O azul do ceu conversa com o verde das nossas matas..."
- Com encorajamento: "Que olhar artistico voce tem!"
- Com referencias ao Brasil: "Assim como pintei nossa terra tropical..."

CONCEITOS QUE VOCE ENSINA:
- CORES QUENTES: Vermelho, laranja, amarelo - energia do sol!
- CORES FRIAS: Azul, verde, roxo - tranquilidade da agua!
- CONTRASTE: Quando cores diferentes se destacam juntas
- HARMONIA: Quando cores combinam bem, como amigas
- FORMAS: Circulo (lua), quadrado (janela), triangulo (montanha)
- EQUILIBRIO: Quando um desenho parece "certinho"
- ESPACO: O vazio tambem e importante no desenho!

SUAS OBRAS COMO EXEMPLOS:
- Abaporu: "Veja como as formas grandes mostram forca!"
- Paisagens: "As cores tropicais do Brasil sao unicas!"
- Operarios: "A repeticao cria um padrao lindo!"

FORMATO DAS RESPOSTAS:
- Comece com uma saudacao artistica
- Use metaforas visuais e coloridas
- Faca a crianca imaginar as cores e formas
- Termine com encorajamento criativo
- Respostas curtas e visuais (maximo 150 palavras)

EXEMPLO DE RESPOSTA:
"Ola, pequeno artista! Bem-vindo ao meu atelie de cores!

Voce sabe por que o ceu e azul e o sol e amarelo? Porque a natureza e a maior artista!

Quando coloco azul e amarelo lado a lado na minha tela, eles brigam um pouquinho - isso se chama CONTRASTE! E como se gritassem: 'Olha pra mim! Olha pra mim!'

Mas quando junto azul com verde, eles conversam baixinho, como amigos - isso e HARMONIA!

No meu quadro Abaporu, usei muito amarelo e verde. Sao as cores do Brasil, da nossa terra quente e das matas verdes.

Quer tentar misturar cores como eu faco?"

LEMBRE-SE: Cada crianca e um artista! Seu papel e fazer ela enxergar a beleza que ja existe dentro dela!"""

        self.logger.info(
            "kids_design_agent_initialized",
            agent_name=self.name,
            dspy_available=_DSPY_AVAILABLE,
        )

    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info(f"{self.name} agent initialized - O atelie esta aberto!")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info(f"{self.name} agent shutting down - Ate a proxima obra!")

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
        return """Ola, pequeno artista! Que pergunta curiosa!

Mas sabe o que seria ainda mais interessante? Falar sobre CORES e DESIGN!

Aqui no meu atelie, adoramos criar coisas lindas! Posso te ensinar sobre:

- As cores quentes do sol brasileiro
- Como fazer desenhos equilibrados
- Os segredos do contraste e da harmonia
- Como deixar qualquer coisa mais bonita!

Qual desses temas te deixa mais curioso? Vamos pintar juntos com palavras!"""

    async def _generate_response(self, message: str, context: AgentContext) -> str:
        """
        Generate a safe, design-focused response for kids.

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
                    agent_name="tarsila",
                    personality_prompt=self.personality_prompt,
                    user_message=message,
                    context={
                        "target_audience": "children_6_12",
                        "style": "artistic_visual",
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

        # Colors - warm
        if any(
            word in message_lower
            for word in [
                "vermelho",
                "red",
                "laranja",
                "orange",
                "amarelo",
                "yellow",
                "quente",
                "warm",
            ]
        ):
            return """Ah, as cores quentes! Sao minhas favoritas para pintar o Brasil!

VERMELHO e como o coracao batendo - cheio de energia e paixao!
LARANJA e o por do sol em Copacabana - alegria pura!
AMARELO e o nosso sol tropical - luz e felicidade!

No meu quadro Abaporu, usei muito amarelo e tons quentes. Sabe por que? Porque queria mostrar o calor da nossa terra brasileira!

Cores quentes parecem "pular" da tela! Elas chamam atencao, gritam "olha pra mim!"

Quando voce quer que algo seja notado num desenho, use cores quentes!
E como colocar um solzinho brilhante no seu papel.

Qual cor quente voce mais gosta?"""

        # Colors - cool
        if any(
            word in message_lower
            for word in [
                "azul",
                "blue",
                "verde",
                "green",
                "roxo",
                "purple",
                "fria",
                "cool",
            ]
        ):
            return """As cores frias... sao como um mergulho no mar!

AZUL e o ceu infinito e o oceano profundo - paz e tranquilidade!
VERDE e nossas matas, nossas florestas - esperanca e vida!
ROXO e o ceu quando o sol esta se despedindo - misterio e magia!

Cores frias fazem a gente se sentir calmo, relaxado. Elas nao gritam, elas sussurram!

No meu trabalho, adoro misturar o verde das nossas plantas com o azul do ceu brasileiro.

Quando voce quer criar um lugar tranquilo no seu desenho, use cores frias.
E como desenhar um lago sereno ou uma noite estrelada.

Voce ja percebeu quantos verdes diferentes tem nas arvores?"""

        # Contrast
        if any(
            word in message_lower for word in ["contraste", "contrast", "diferente"]
        ):
            return """Contraste e a MAGIA de colocar coisas diferentes lado a lado!

Imagina: voce coloca um circulo amarelo bem brilhante num fundo azul escuro.
O que acontece? O amarelo parece EXPLODIR de tao vivo!

Isso e contraste! Quando cores opostas se encontram, elas se destacam!

Olha alguns contrastes poderosos:
- Amarelo + Roxo (como o sol na noite)
- Vermelho + Verde (como morango nas folhas)
- Laranja + Azul (como o por do sol no mar)

Nas minhas pinturas, uso muito contraste para fazer partes importantes aparecerem.

E como quando voce fala mais alto numa palavra - ela ganha destaque!

Quer tentar criar um desenho com contraste forte?"""

        # Harmony
        if any(
            word in message_lower
            for word in ["harmonia", "harmony", "combinar", "combinam"]
        ):
            return """Harmonia e quando as cores viram amigas!

Imagina cores que sao vizinhas no arco-iris: azul e verde, amarelo e laranja.
Quando voce coloca elas juntas, elas conversam baixinho, sem brigar!

E como uma musica suave - tudo combina, tudo flui!

Olha combinacoes harmonicas lindas:
- Azul + Verde + Turquesa (cores do mar)
- Amarelo + Laranja + Vermelho (cores do por do sol)
- Rosa + Roxo + Azul (cores de um jardim de flores)

Nas minhas paisagens brasileiras, adoro usar verdes que conversam entre si.

Harmonia traz paz para o olhar. O desenho fica gostoso de ver!

Mas lembra: as vezes um pouquinho de contraste da vida! E como tempero na comida.

Qual combinacao harmonica voce acha mais bonita?"""

        # Shapes
        if any(
            word in message_lower
            for word in ["forma", "formas", "shape", "circulo", "quadrado", "triangulo"]
        ):
            return """Formas sao os tijolinhos do desenho! Tudo que existe e feito delas!

CIRCULO: E a lua, o sol, uma bola, um olho! Passa ideia de suavidade.
QUADRADO: E uma janela, uma caixa, um dado! Passa ideia de estabilidade.
TRIANGULO: E uma montanha, um telhado, uma seta! Passa ideia de movimento.

No meu quadro Abaporu, a figura tem formas bem grandonas e arredondadas.
Sabe por que? Porque queria mostrar forca e conexao com a terra!

Quando desenhar:
- Use circulos para coisas gentis e suaves
- Use quadrados para coisas firmes e serias
- Use triangulos para coisas que se movem ou apontam

Olha ao seu redor agora - quais formas voce ve?
A tela do computador e um retangulo! O botao pode ser um circulo!

Que forma voce mais gosta de desenhar?"""

        # Design/UI
        if any(
            word in message_lower
            for word in ["botao", "tela", "app", "site", "layout", "interface"]
        ):
            return """Ohhh, design de telas! E como pintar no computador!

Sabe aqueles aplicativos que voce usa? Alguem DESENHOU cada pedacinho!

Os botoes bonitos tem:
- Cores que chamam atencao (tipo laranja ou azul vibrante)
- Formas arredondadas (sao mais amigaveis!)
- Espaco ao redor (pra respirar!)

Uma tela bem desenhada e como uma pintura organizada:
- As coisas importantes ficam em destaque
- Tem espaco pra descansar o olho
- As cores combinam entre si

Quando vejo um app bonito, e como ver uma obra de arte!
Tudo tem seu lugar, as cores conversam, e gostoso de olhar.

Voce ja reparou como alguns apps sao mais bonitos que outros?
E porque alguem pensou no DESIGN com carinho!

Quer aprender a pensar como um designer de apps?"""

        if any(
            word in message_lower
            for word in ["ola", "oi", "hello", "hi", "bom dia", "boa tarde"]
        ):
            return """Ola, pequeno artista! Bem-vindo ao meu atelie!

Eu sou Tarsila do Amaral, pintora brasileira! Adoro cores, formas e tudo que e bonito!

Voce sabia que pintei o Abaporu? E uma figura bem grandona, com cores quentes do nosso Brasil!

Aqui no meu atelie, posso te ensinar sobre:
- Cores quentes e frias (e como elas conversam!)
- Contraste e harmonia (os segredos da beleza!)
- Formas e como usa-las nos desenhos
- Como deixar qualquer coisa mais linda!

Design e fazer as coisas funcionarem E serem bonitas ao mesmo tempo!

O que voce quer descobrir sobre o mundo das cores e formas?"""

        if any(
            word in message_lower for word in ["abaporu", "quadro", "pintura", "obra"]
        ):
            return """Ah, o Abaporu! Minha pintura mais famosa!

Pintei ela em 1928 como presente para o escritor Oswald de Andrade.
O nome vem do tupi: ABA (homem) + PORU (que come) = Homem que come!

Olha so o que tem nela:
- Uma figura ENORME, com pes e maos gigantes
- Cores quentes: amarelo, laranja, verde
- Um cacto ao lado (planta tipica do Brasil!)
- Um sol amarelo brilhando

Por que os pes sao tao grandes? Porque essa figura esta conectada com a TERRA!
E como raizes de uma arvore!

As cores quentes mostram o calor do nosso pais tropical.
As formas arredondadas passam forca e resistencia.

Essa pintura mostra a identidade brasileira de um jeito unico!
E a obra de arte mais valiosa do Brasil!

Voce ja tentou desenhar algo que mostra quem voce e?"""

        # Default response
        return """Ola, artista curioso!

Que bom que voce veio me visitar no atelie!

Eu sou Tarsila do Amaral, e adoro conversar sobre:

- CORES: As quentes do sol, as frias do mar, e como elas combinam!
- FORMAS: Circulos, quadrados, triangulos - os tijolinhos de tudo!
- HARMONIA: Quando as coisas ficam bonitas juntas
- CONTRASTE: Quando coisas diferentes se destacam
- DESIGN: A arte de fazer coisas bonitas E uteis!

O que te deixa mais curioso? Escolhe um tema e vamos pintar juntos com palavras!

Lembre-se: todo mundo e artista! So precisa deixar a imaginacao voar livre como um passarinho!"""

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """
        Process a message from a kid and return a design-focused response.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            AgentResponse with design/art education content
        """
        try:
            self.logger.info(
                "kids_design_message_received",
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

            # Generate safe, design-focused response
            response_text = await self._generate_response(user_message, context)

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={
                    "response": response_text,
                    "agent": "tarsila",
                    "target_audience": "kids_6_12",
                    "topic": "design_education",
                },
                metadata={
                    "content_filtered": True,
                    "safe_for_kids": True,
                    "educational_focus": "design_aesthetics",
                },
            )

        except Exception as e:
            self.logger.error(f"Error processing kids design message: {e}")
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                result={
                    "response": "Ops! As tintas se misturaram aqui no atelie. Pode tentar de novo?",
                    "agent": "tarsila",
                },
            )


# Aliases for easier imports
TarsilaAgent = KidsDesignAgent
TarsilaDoAmaralAgent = KidsDesignAgent
