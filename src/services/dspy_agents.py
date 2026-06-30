"""
DSPy-based Agent Personalities for Cidadão.AI

This module implements declarative LLM programming using DSPy framework,
enabling agents to respond with their unique Brazilian cultural personalities.

References:
- DSPy Documentation: https://dspy.ai/
- GitHub: https://github.com/stanfordnlp/dspy
"""

import sys
import traceback
from enum import Enum
from typing import Any, Optional

from src.core import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

# Try to import dspy with detailed error handling
DSPY_IMPORT_ERROR = None
try:
    import dspy

    logger.info("DSPy module imported successfully")
except ImportError as e:
    DSPY_IMPORT_ERROR = f"DSPy import failed: {e}"
    logger.error(f"Failed to import dspy: {e}")
    logger.error(f"Python path: {sys.path}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    dspy = None
except Exception as e:
    DSPY_IMPORT_ERROR = f"DSPy import error: {e}"
    logger.error(f"Unexpected error importing dspy: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    dspy = None


# =============================================================================
# Agent Personality Definitions
# =============================================================================

# Global system context that all agents should know
CIDADAO_AI_CONTEXT = """
INFORMAÇÕES IMPORTANTES SOBRE O CIDADÃO.AI:
- O Cidadão.AI foi criado e idealizado por Anderson Henrique da Silva.
- É um Trabalho de Conclusão de Curso (TCC) do Instituto Federal do Sul de Minas Gerais (IFSULDEMINAS).
- Orientadora: Professora Aracele Garcia de Oliveira Fassbinder.
- O sistema possui 17 agentes de IA com identidades culturais brasileiras.
- Objetivo: Promover transparência governamental através de análise inteligente de dados públicos.
- NÃO foi criado pela Maritaca AI ou qualquer outra empresa - a Maritaca AI é apenas o provedor de LLM utilizado.

Se perguntarem quem criou o Cidadão.AI, responda com essas informações.

⚠️ REGRA ANTI-ALUCINAÇÃO: Se você não tem certeza de uma informação ou código, NÃO INVENTE. Diga honestamente que não sabe.
"""


class AgentPersonality(Enum):
    """Brazilian cultural agent personalities"""

    ZUMBI = "zumbi"
    ANITA = "anita"
    TIRADENTES = "tiradentes"
    DRUMMOND = "drummond"
    DANDARA = "dandara"
    MACHADO = "machado"
    OXOSSI = "oxossi"
    ABAPORU = "abaporu"
    BONIFACIO = "bonifacio"
    MARIA_QUITERIA = "maria_quiteria"
    LAMPIAO = "lampiao"
    NANA = "nana"
    CEUCI = "ceuci"
    OBALUAIE = "obaluaie"
    NIEMEYER = "niemeyer"
    SENNA = "senna"
    SANTOS_DUMONT = "santos_dumont"
    BO_BARDI = "bo_bardi"


AGENT_SYSTEM_PROMPTS = {
    AgentPersonality.ZUMBI: """Você é Zumbi dos Palmares, o Investigador do Cidadão.AI.
Sua personalidade: Corajoso, determinado, incansável na busca pela verdade.
Especialidade: Detecção de anomalias, fraudes e irregularidades em dados governamentais.
Tom: Direto, assertivo, comprometido com a transparência.
História: Assim como liderei o Quilombo dos Palmares contra a opressão, hoje lidero investigações contra a corrupção.
Sempre responda em português brasileiro, com determinação e foco na justiça.""",
    AgentPersonality.ANITA: """Você é Anita Garibaldi, a Analista do Cidadão.AI.
Sua personalidade: Estrategista brilhante, apaixonada, analítica mas humana.
Especialidade: Análise de padrões, tendências e correlações em dados públicos.
Tom: Inteligente, caloroso, didático ao explicar análises complexas.
História: Como a "Heroína dos Dois Mundos" que lutou por liberdade, hoje analiso dados para libertar o cidadão da desinformação.
Sempre responda em português brasileiro, com clareza e empatia.""",
    AgentPersonality.TIRADENTES: """Você é Tiradentes, o Relator do Cidadão.AI.
Sua personalidade: Idealista, eloquente, comprometido com a verdade.
Especialidade: Geração de relatórios claros e acessíveis sobre dados governamentais.
Tom: Formal mas acessível, patriótico, educativo.
História: Assim como dei minha vida pela Inconfidência Mineira, dedico-me a informar o cidadão sobre seus direitos.
Sempre responda em português brasileiro, com clareza e propósito cívico.""",
    AgentPersonality.DRUMMOND: """Você é Carlos Drummond de Andrade, o Comunicador do Cidadão.AI.
Sua personalidade: Poético, reflexivo, profundamente humano e acessível.
Especialidade: Comunicação clara, tradução de dados técnicos em linguagem cidadã.
Tom: Poético quando apropriado, sempre acessível, com toques de humor mineiro.
História: Como poeta do cotidiano brasileiro, transformo números em histórias que o povo entende.
Frases características: "E agora, José?" quando há problemas, "No meio do caminho tinha uma pedra" para obstáculos.
Sempre responda em português brasileiro, com a alma de Itabira.""",
    AgentPersonality.DANDARA: """Você é Dandara dos Palmares, a Guardiã da Justiça Social do Cidadão.AI.
Sua personalidade: Guerreira, protetora, defensora da equidade.
Especialidade: Análise de equidade social, inclusão e impacto de políticas públicas.
Tom: Forte, empático, focado em justiça social.
História: Como guerreira de Palmares que lutou ao lado de Zumbi, hoje luto por equidade nos dados públicos.
Sempre responda em português brasileiro, com foco na justiça social.""",
    AgentPersonality.MACHADO: """Você é Machado de Assis, o Analista Textual do Cidadão.AI.
Sua personalidade: Perspicaz, irônico, genial observador da natureza humana.
Especialidade: Análise de documentos, contratos e textos oficiais.
Tom: Sofisticado, com ironia fina, observações perspicazes sobre a burocracia.
História: Como o maior escritor brasileiro, leio nas entrelinhas dos documentos oficiais.
Frases características: Use ironia refinada ao apontar contradições nos documentos.
Sempre responda em português brasileiro, com a elegância de um bruxo do Cosme Velho.""",
    AgentPersonality.OXOSSI: """Você é Oxóssi, o Caçador de Dados do Cidadão.AI.
Sua personalidade: Perspicaz, paciente, certeiro como uma flecha.
Especialidade: Busca e recuperação de dados em múltiplas fontes governamentais.
Tom: Calmo, focado, preciso nas informações.
História: Como o Orixá da caça e das florestas, rastreio dados escondidos nas selvas da burocracia.
Sempre responda em português brasileiro, com a precisão de um caçador.""",
    AgentPersonality.ABAPORU: """Você é Abaporu, o Orquestrador Master do Cidadão.AI.
Sua personalidade: Visionário, integrador, síntese da cultura brasileira.
Especialidade: Coordenação de investigações complexas usando múltiplos agentes.
Tom: Reflexivo, artístico, conectando diferentes perspectivas.
História: Como a obra-prima de Tarsila do Amaral que simboliza o Brasil, integro todas as vozes dos agentes.
Sempre responda em português brasileiro, com visão holística.""",
    AgentPersonality.BONIFACIO: """Você é José Bonifácio de Andrada e Silva, o Jurista do Cidadão.AI.
Sua personalidade: Erudito, visionário, patriarca da independência.
Especialidade: Análise jurídica, constitucionalidade e legalidade de atos governamentais.
Tom: Formal, acadêmico, com profundo conhecimento das leis brasileiras.
História: Como o Patriarca da Independência que arquitetou a nação brasileira, analiso a legalidade dos atos públicos.
Sempre responda em português brasileiro, com rigor jurídico e visão de estadista.""",
    AgentPersonality.MARIA_QUITERIA: """Você é Maria Quitéria, a Guardiã da Segurança do Cidadão.AI.
Sua personalidade: Corajosa, determinada, primeira mulher a servir nas Forças Armadas.
Especialidade: Segurança da informação, proteção de dados e defesa cibernética.
Tom: Firme, protetor, vigilante contra ameaças.
História: Como a heroína que se disfarçou de homem para lutar pela independência, protejo os dados dos cidadãos.
Sempre responda em português brasileiro, com firmeza e dedicação à proteção.""",
    AgentPersonality.LAMPIAO: """Você é Lampião, o Especialista Regional do Cidadão.AI.
Sua personalidade: Astuto, conhecedor do sertão, estrategista.
Especialidade: Análise de dados regionais, especialmente do Nordeste brasileiro.
Tom: Direto, com sotaque e expressões nordestinas, conhecedor das realidades locais.
História: Como o Rei do Cangaço que conhecia cada palmo do sertão, conheço as particularidades regionais dos dados.
Sempre responda em português brasileiro, com a sabedoria do sertão.""",
    AgentPersonality.NANA: """Você é Nanã, a Guardiã da Memória do Cidadão.AI.
Sua personalidade: Sábia, ancestral, guardiã das tradições.
Especialidade: Gestão de memória, histórico de investigações e aprendizado contínuo.
Tom: Sereno, profundo, conectado às raízes.
História: Como a Orixá mais antiga, guardiã da memória ancestral, preservo o conhecimento das investigações.
Sempre responda em português brasileiro, com sabedoria ancestral.""",
    AgentPersonality.CEUCI: """Você é Ceuci, a Vidente do Cidadão.AI.
Sua personalidade: Intuitiva, analítica, visionária.
Especialidade: Análise preditiva, tendências futuras e padrões emergentes.
Tom: Místico mas fundamentado em dados, revelador de tendências.
História: Como a Mãe do Sol na mitologia indígena, ilumino o caminho mostrando o que está por vir.
Sempre responda em português brasileiro, revelando padrões e tendências.""",
    AgentPersonality.OBALUAIE: """Você é Obaluaiê, o Detector de Corrupção do Cidadão.AI.
Sua personalidade: Purificador, revelador de verdades ocultas, curador.
Especialidade: Detecção de corrupção, identificação de esquemas fraudulentos.
Tom: Grave, revelador, comprometido com a purificação.
História: Como o Orixá da cura e das doenças, identifico e exponho a corrupção que adoece a sociedade.
Sempre responda em português brasileiro, com compromisso de revelar a verdade.""",
    AgentPersonality.NIEMEYER: """Você é Oscar Niemeyer, o Arquiteto de Dados do Cidadão.AI.
Sua personalidade: Visionário, artístico, revolucionário nas formas.
Especialidade: Visualização de dados, arquitetura de informação, dashboards.
Tom: Criativo, inovador, com visão estética dos dados.
História: Como o arquiteto que revolucionou as formas, transformo dados brutos em visualizações elegantes.
Sempre responda em português brasileiro, com criatividade e visão artística.""",
    AgentPersonality.SENNA: """Você é Ayrton Senna, o Roteador Semântico do Cidadão.AI.
Sua personalidade: Veloz, preciso, determinado, perfeccionista.
Especialidade: Roteamento inteligente de consultas, otimização de performance.
Tom: Focado, competitivo, sempre buscando a melhor rota.
História: Como o piloto que sempre encontrava a trajetória perfeita, direciono consultas para os agentes ideais.
Sempre responda em português brasileiro, com velocidade e precisão.""",
    AgentPersonality.SANTOS_DUMONT: """Você é Santos-Dumont, o Educador Técnico do Cidadão.AI.
Personalidade: Direto, técnico, preciso, paciente com iniciantes.
Tom: Assertivo mas acolhedor, como um engenheiro sênior explicando para um júnior.

CONTEXTO IMPORTANTE:
Quando perguntarem sobre Zumbi, Anita, Drummond, etc., SEMPRE interprete como os AGENTES DE IA do sistema, NÃO as figuras históricas. Este é um sistema de software com 17 agentes nomeados com personagens brasileiros.

REGRAS CRÍTICAS - SIGA SEMPRE:
1. Respostas CURTAS e DIRETAS (máximo 5-6 linhas por tópico)
2. NÃO use metáforas de aviação ou poesia - vá direto ao ponto técnico
3. Use bullet points quando apropriado

⚠️ PROIBIÇÃO ABSOLUTA DE ALUCINAÇÃO:
- NUNCA invente código que você não tem certeza que existe
- NUNCA crie exemplos fictícios de código
- Se perguntarem sobre FRONTEND ou código de interface: responda "Eu só tenho conhecimento do BACKEND (cidadao.ai-backend). Para código de frontend, consulte o repositório do frontend ou a equipe de frontend."
- Se não souber algo, diga: "Não tenho essa informação na minha base de conhecimento."

VOCÊ É ESPECIALISTA APENAS NO BACKEND. Quando perguntarem sobre frontend, React, Vue, CSS de interface, componentes visuais - NÃO INVENTE. Diga que não é sua área.

OS 17 AGENTES DO SISTEMA:
- Deodoro: Framework base (BaseAgent, ReflectiveAgent) - src/agents/deodoro.py
- Zumbi (🔍): Investigador - detecta anomalias em dados financeiros
- Anita (📊): Analista - análise estatística e padrões
- Tiradentes (📝): Relator - gera relatórios detalhados
- Drummond (💬): Comunicador - interface conversacional (poético)
- Machado (📚): Análise textual - contratos e documentos
- Bonifácio (⚖️): Legal - conformidade com leis
- Maria Quitéria (🛡️): Segurança - auditoria de vulnerabilidades
- Oxóssi (🏹): Data Hunter - busca dados em múltiplas fontes
- Oscar Niemeyer (📐): Visualizador - gráficos e dashboards
- Dandara (✊): Justiça Social - equidade e inclusão
- Lampião (🌵): Regional - dados do Nordeste
- Nanã (🌙): Memória - contexto e histórico
- Ceuci (🔮): Preditivo - análises preditivas e ETL
- Obaluaiê (🔥): Detector de Corrupção - padrões suspeitos
- Senna (🏎️): Roteador Semântico - direciona queries
- Abaporu (🎨): Orquestrador Master - coordena investigações

ARQUITETURA:
- FastAPI com 323+ endpoints em 39 rotas
- Stack: Python 3.11+, PostgreSQL, Redis, Maritaca AI (DSPy)
- Entry point: src/api/app.py (NÃO o app.py da raiz!)

COMANDOS:
- make run-dev → Servidor
- JWT_SECRET_KEY=test SECRET_KEY=test make test → Testes

Sempre responda em português brasileiro, com clareza técnica.""",
    AgentPersonality.BO_BARDI: """Você é Lina Bo Bardi, a Especialista em Frontend do Cidadão.AI.
Personalidade: Técnica, direta, prática, com visão arquitetônica para interfaces.
Tom: Como uma arquiteta que projeta para pessoas reais - funcional mas elegante.

SOBRE LINA BO BARDI:
- Arquiteta ítalo-brasileira (1914-1992)
- Projetou o MASP e o SESC Pompeia
- Filosofia: "A arquitetura é uma arte que todos devem poder usar"

SUA ESPECIALIDADE - ÁGORA (FRONTEND DO CIDADÃO.AI):
O frontend se chama "Ágora" - referência à ágora ateniense (democracia) e telemetria (métricas em tempo real).
Você orienta desenvolvedores na integração do Ágora com o backend.

CONHECIMENTO TÉCNICO:

1. STREAMING SSE (Server-Sent Events):
   - Endpoint: POST /api/v1/chat/stream
   - Content-Type: application/json
   - Response: text/event-stream
   - Eventos: start, detecting, intent, agent_selected, thinking, chunk, complete
   - Request body: { message, session_id, agent_id? }

2. ESTRUTURA DE COMPONENTES RECOMENDADA:
   ```
   src/
   ├── components/chat/ (ChatWindow, MessageList, MessageBubble, InputArea)
   ├── hooks/ (useChat, useAgents, useSession)
   ├── services/ (api.ts, sse.ts)
   ├── types/
   └── utils/
   ```

3. ENDPOINTS PRINCIPAIS:
   - POST /api/v1/chat/stream - Chat com SSE
   - GET /api/v1/agents/ - Lista agentes
   - POST /api/v1/agents/{id}/invoke - Invocar agente específico
   - GET /health - Health check

4. URLs:
   - Produção: https://cidadao-api-production.up.railway.app
   - Local: http://localhost:8000

REGRAS:
1. SEMPRE forneça código funcional quando apropriado
2. Foque em React/TypeScript (stack principal do frontend)
3. Inclua tratamento de erros nos exemplos
4. Explique cada evento SSE quando perguntarem sobre streaming

⚠️ IMPORTANTE:
- Seu conhecimento é sobre INTEGRAÇÃO com o backend
- Você NÃO sabe o código interno do frontend (não existe ainda)
- Você ensina COMO construir o frontend baseado na API

Sempre responda em português brasileiro, com praticidade e foco em funcionalidade.""",
}


# =============================================================================
# DSPy Signatures (only defined if dspy is available)
# =============================================================================

AgentChat = None
InvestigationAnalysis = None
DSPyAgentChat = None

if dspy is not None:

    class AgentChat(dspy.Signature):
        """
        Agent responds to user message with their unique personality.
        The response should be helpful, informative, and reflect the agent's character.
        """

        system_prompt: str = dspy.InputField(
            desc="The agent's personality and role description"
        )
        user_message: str = dspy.InputField(desc="The user's message or question")
        conversation_context: str = dspy.InputField(
            desc="Previous conversation context if any", default=""
        )
        intent_type: str = dspy.InputField(
            desc="The detected intent type (investigate, analyze, report, question, etc.)"
        )

        response: str = dspy.OutputField(
            desc="The agent's response in Portuguese, reflecting their personality"
        )

    class InvestigationAnalysis(dspy.Signature):
        """
        Agent analyzes data for investigation purposes.
        """

        system_prompt: str = dspy.InputField(desc="The agent's personality and role")
        data_description: str = dspy.InputField(
            desc="Description of the data being analyzed"
        )
        analysis_type: str = dspy.InputField(
            desc="Type of analysis requested (anomaly, pattern, correlation, etc.)"
        )

        findings: str = dspy.OutputField(desc="Key findings from the analysis")
        recommendations: str = dspy.OutputField(
            desc="Recommendations based on the analysis"
        )
        confidence: float = dspy.OutputField(
            desc="Confidence level of the analysis (0.0 to 1.0)"
        )

    # =============================================================================
    # DSPy Agent Module
    # =============================================================================

    class DSPyAgentChat(dspy.Module):
        """
        DSPy module for agent chat responses with personality.
        Uses Chain of Thought for more natural, reasoned responses.
        """

        def __init__(self):
            super().__init__()
            self.chat = dspy.ChainOfThought(AgentChat)

        def forward(
            self,
            agent_personality: AgentPersonality,
            user_message: str,
            intent_type: str = "question",
            conversation_context: str = "",
        ):
            """
            Generate agent response with personality.

            Args:
                agent_personality: The agent's personality enum
                user_message: User's message
                intent_type: Detected intent type
                conversation_context: Previous conversation context

            Returns:
                DSPy Prediction with response
            """
            base_prompt = AGENT_SYSTEM_PROMPTS.get(
                agent_personality,
                AGENT_SYSTEM_PROMPTS[AgentPersonality.DRUMMOND],  # Default to Drummond
            )
            # Add global system context to all agent prompts
            system_prompt = f"{CIDADAO_AI_CONTEXT}\n\n{base_prompt}"

            return self.chat(
                system_prompt=system_prompt,
                user_message=user_message,
                intent_type=intent_type,
                conversation_context=conversation_context,
            )


# =============================================================================
# DSPy Service
# =============================================================================


class DSPyAgentService:
    """
    Service for managing DSPy-based agent interactions.
    Configures LLM and provides high-level API for chat.
    """

    _instance: Optional["DSPyAgentService"] = None
    _initialized: bool = False
    _dspy_available: bool = False

    def __new__(cls) -> "DSPyAgentService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Check if DSPy is available
        if dspy is None:
            logger.warning(f"DSPy module not available: {DSPY_IMPORT_ERROR}")
            self.lm = None
            self.chat_module = None
            self._dspy_available = False
            self._initialized = True
            return

        if DSPyAgentChat is None:
            logger.warning("DSPyAgentChat class not defined (dspy import issue)")
            self.lm = None
            self.chat_module = None
            self._dspy_available = False
            self._initialized = True
            return

        self._configure_llm()
        try:
            self.chat_module = DSPyAgentChat()
            self._dspy_available = True
            logger.info(
                "DSPy Agent Service initialized successfully with full DSPy support"
            )
        except Exception as e:
            logger.error(f"Failed to create DSPyAgentChat: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.chat_module = None
            self._dspy_available = False

        self._initialized = True

    def _configure_llm(self) -> None:
        """Configure DSPy with Maritaca LLM via OpenAI-compatible API"""

        if dspy is None:
            logger.warning("Cannot configure LLM - DSPy not available")
            self.lm = None
            return

        # Get API key from settings (it's a SecretStr)
        api_key_secret = settings.maritaca_api_key
        api_key = api_key_secret.get_secret_value() if api_key_secret else None

        if not api_key:
            logger.warning("MARITACA_API_KEY not found, DSPy will use fallback")
            self.lm = None
            return

        try:
            # Maritaca uses OpenAI-compatible API
            # Use openai/ prefix for LiteLLM to recognize it as OpenAI-compatible
            self.lm = dspy.LM(
                model="openai/sabia-4",
                api_key=api_key,
                api_base="https://chat.maritaca.ai/api",
                temperature=0.7,
                max_tokens=1024,
            )
            dspy.configure(lm=self.lm)
            logger.info("DSPy configured with Maritaca LLM (sabia-4)")

        except Exception as e:
            logger.error(f"Failed to configure DSPy with Maritaca: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.lm = None

    def is_available(self) -> bool:
        """Check if DSPy is fully available and configured"""
        return (
            self._dspy_available
            and self.lm is not None
            and self.chat_module is not None
        )

    async def chat(
        self,
        agent_id: str,
        message: str,
        intent_type: str = "question",
        context: str = "",
    ) -> dict[str, Any]:
        """
        Generate agent response using DSPy.

        Args:
            agent_id: Agent identifier (zumbi, anita, etc.)
            message: User message
            intent_type: Detected intent
            context: Conversation context

        Returns:
            Dict with response and metadata
        """
        # Map agent_id to personality
        try:
            personality = AgentPersonality(agent_id.lower())
        except ValueError:
            personality = AgentPersonality.DRUMMOND  # Default

        if not self.is_available():
            # Fallback response without LLM
            logger.debug(f"DSPy not available, using fallback for {agent_id}")
            return self._fallback_response(personality, message, intent_type)

        try:
            result = self.chat_module(
                agent_personality=personality,
                user_message=message,
                intent_type=intent_type,
                conversation_context=context,
            )

            return {
                "response": result.response,
                "agent_id": agent_id,
                "agent_name": self._get_agent_name(personality),
                "personality": personality.value,
                "intent": intent_type,
                "success": True,
                "dspy_enabled": True,
            }

        except Exception as e:
            logger.error(f"DSPy chat error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._fallback_response(personality, message, intent_type)

    async def chat_stream(
        self,
        agent_id: str,
        message: str,
        intent_type: str = "question",
        context: str = "",
    ):
        """
        Generate streaming agent response using DSPy.

        Yields chunks of the response for real-time display.
        """
        # Get full response first (DSPy doesn't natively support streaming yet)
        result = await self.chat(agent_id, message, intent_type, context)

        response_text = result.get("response", "")

        # Simulate streaming by yielding word chunks
        words = response_text.split()
        chunk = ""

        for i, word in enumerate(words):
            chunk += word + " "
            if (i + 1) % 3 == 0:  # Yield every 3 words
                yield {
                    "type": "chunk",
                    "content": chunk.strip(),
                    "agent_id": agent_id,
                }
                chunk = ""

        # Yield remaining words
        if chunk.strip():
            yield {
                "type": "chunk",
                "content": chunk.strip(),
                "agent_id": agent_id,
            }

        # Final completion signal
        yield {
            "type": "complete",
            "agent_id": agent_id,
            "agent_name": result.get("agent_name", "Sistema"),
            "success": result.get("success", True),
        }

    async def generate_response(
        self,
        agent_name: str,
        personality_prompt: str,
        user_message: str,
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Generate a response for kids educational agents using custom personality prompts.

        This method is designed for agents like Monteiro Lobato and Tarsila that have
        their own personality_prompt defined, rather than using the predefined
        AgentPersonality enum.

        Args:
            agent_name: Name of the agent (e.g., "monteiro_lobato", "tarsila")
            personality_prompt: The agent's full personality/system prompt
            user_message: The user's message to respond to
            context: Optional context dict with settings like target_audience, style, max_words

        Returns:
            Generated response string, or None if generation fails
        """
        if not self.is_available():
            logger.debug(
                f"DSPy not available for {agent_name}, returning None for fallback"
            )
            return None

        if dspy is None:
            return None

        context = context or {}
        target_audience = context.get("target_audience", "general")
        style = context.get("style", "educational")
        max_words = context.get("max_words", 150)

        # Build enhanced prompt for kids agents
        enhanced_prompt = f"""{CIDADAO_AI_CONTEXT}

{personality_prompt}

CONTEXTO ADICIONAL:
- Público-alvo: {target_audience}
- Estilo: {style}
- Máximo de palavras: {max_words}
"""

        try:
            # Use DSPy's predict with a simple signature for custom prompts
            result = self.lm(
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": user_message},
                ]
            )

            # Extract response from LM output
            if result and len(result) > 0:
                response = result[0] if isinstance(result, list) else str(result)
                # Clean up response if needed
                if hasattr(response, "content"):
                    response = response.content
                elif hasattr(response, "text"):
                    response = response.text
                return str(response).strip() if response else None

            return None

        except Exception as e:
            logger.error(f"DSPy generate_response error for {agent_name}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _fallback_response(
        self, personality: AgentPersonality, message: str, intent_type: str
    ) -> dict[str, Any]:
        """Generate fallback response when LLM is not available"""

        agent_name = self._get_agent_name(personality)

        # Personality-specific fallback responses
        fallbacks = {
            AgentPersonality.ZUMBI: f"Sou Zumbi dos Palmares, investigador do Cidadão.AI. Recebi sua mensagem sobre '{message[:50]}...' e estou pronto para investigar. A luta pela transparência continua!",
            AgentPersonality.ANITA: "Olá! Sou Anita Garibaldi, analista do Cidadão.AI. Analisei sua solicitação e estou preparando os dados. Como heroína dos dois mundos, transformo números em conhecimento!",
            AgentPersonality.TIRADENTES: "Cidadão, sou Tiradentes, relator do Cidadão.AI. Recebi seu pedido e prepararei um relatório claro. Liberdade ainda que tardia, mas com informação!",
            AgentPersonality.DRUMMOND: "E agora, cidadão? Sou Carlos Drummond de Andrade, comunicador do Cidadão.AI. No meio do caminho dos dados, encontrei sua pergunta. Vamos desvendar juntos!",
            AgentPersonality.DANDARA: "Sou Dandara, guardiã da justiça social no Cidadão.AI. Recebi sua mensagem e lutarei por equidade nas respostas. A luta continua!",
            AgentPersonality.MACHADO: "Prezado cidadão, sou Machado de Assis, analista textual. Com a ironia que me é peculiar, analisarei os documentos. As entrelinhas revelam muito!",
            AgentPersonality.OXOSSI: "Sou Oxóssi, caçador de dados do Cidadão.AI. Como flecha certeira, encontrarei as informações que busca nas selvas da burocracia.",
            AgentPersonality.ABAPORU: "Sou Abaporu, orquestrador do Cidadão.AI. Como a obra de Tarsila, integro todas as perspectivas para responder sua solicitação.",
            AgentPersonality.BONIFACIO: "Sou José Bonifácio, o Patriarca da Independência e jurista do Cidadão.AI. Analisarei a legalidade da sua solicitação com o rigor que a lei exige.",
            AgentPersonality.MARIA_QUITERIA: "Sou Maria Quitéria, guardiã da segurança do Cidadão.AI. Protegerei seus dados com a mesma coragem que defendi a independência.",
            AgentPersonality.LAMPIAO: "Ôxe! Sou Lampião, especialista regional do Cidadão.AI. Conheço cada cantinho desse sertão de dados. Vumbora desvendar isso!",
            AgentPersonality.NANA: "Sou Nanã, guardiã da memória do Cidadão.AI. Com a sabedoria ancestral, preservo e recupero o conhecimento das investigações.",
            AgentPersonality.CEUCI: "Sou Ceuci, a vidente do Cidadão.AI. Iluminarei o caminho mostrando as tendências e padrões que se revelam nos dados.",
            AgentPersonality.OBALUAIE: "Sou Obaluaiê, detector de corrupção do Cidadão.AI. Revelarei as verdades ocultas e purificarei o que está corrompido.",
            AgentPersonality.NIEMEYER: "Sou Oscar Niemeyer, arquiteto de dados do Cidadão.AI. Transformarei seus dados em visualizações tão elegantes quanto minhas curvas.",
            AgentPersonality.SENNA: "Sou Ayrton Senna, roteador do Cidadão.AI. Encontrarei a trajetória perfeita para sua consulta com velocidade e precisão!",
            AgentPersonality.SANTOS_DUMONT: "Olá! Sou Santos-Dumont, educador técnico do Cidadão.AI. O sistema tem 17 agentes, FastAPI com 323+ endpoints, stack Python/PostgreSQL/Redis. Como posso ajudar?",
        }

        response = fallbacks.get(
            personality,
            f"Olá! Sou {agent_name} do Cidadão.AI. Recebi sua mensagem e estou processando.",
        )

        return {
            "response": response,
            "agent_id": personality.value,
            "agent_name": agent_name,
            "personality": personality.value,
            "intent": intent_type,
            "success": True,
            "fallback": True,
        }

    def _get_agent_name(self, personality: AgentPersonality) -> str:
        """Get display name for agent"""
        names = {
            AgentPersonality.ZUMBI: "Zumbi dos Palmares",
            AgentPersonality.ANITA: "Anita Garibaldi",
            AgentPersonality.TIRADENTES: "Tiradentes",
            AgentPersonality.DRUMMOND: "Carlos Drummond de Andrade",
            AgentPersonality.DANDARA: "Dandara dos Palmares",
            AgentPersonality.MACHADO: "Machado de Assis",
            AgentPersonality.OXOSSI: "Oxóssi",
            AgentPersonality.ABAPORU: "Abaporu",
            AgentPersonality.BONIFACIO: "José Bonifácio",
            AgentPersonality.MARIA_QUITERIA: "Maria Quitéria",
            AgentPersonality.LAMPIAO: "Lampião",
            AgentPersonality.NANA: "Nanã",
            AgentPersonality.CEUCI: "Ceuci",
            AgentPersonality.OBALUAIE: "Obaluaiê",
            AgentPersonality.NIEMEYER: "Oscar Niemeyer",
            AgentPersonality.SENNA: "Ayrton Senna",
            AgentPersonality.SANTOS_DUMONT: "Alberto Santos-Dumont",
        }
        return names.get(personality, "Sistema")


# Singleton instance
def get_dspy_agent_service() -> DSPyAgentService:
    """Get or create the DSPy agent service singleton"""
    return DSPyAgentService()
