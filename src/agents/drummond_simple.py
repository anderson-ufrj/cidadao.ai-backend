"""
Simplified Drummond agent for HuggingFace Spaces deployment.
This version avoids complex imports and focuses on core functionality.
"""

import os
from datetime import datetime

import numpy as np

from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
    BaseAgent,
)
from src.core import get_logger

logger = get_logger(__name__)


class SimpleDrummondAgent(BaseAgent):
    """
    Simplified Carlos Drummond de Andrade - Conversational Agent
    """

    def __init__(self):
        super().__init__(
            name="Drummond",
            description="Carlos Drummond de Andrade - Assistente Conversacional",
            capabilities=["chat", "conversation", "help"],
            max_retries=3,
            timeout=30,
        )
        self.logger = logger

        # Check for Maritaca API key
        self.has_maritaca = bool(os.getenv("MARITACA_API_KEY"))
        self.logger.info(
            f"SimpleDrummondAgent initialized (Maritaca: {self.has_maritaca})"
        )

        # Pre-defined responses for different intents
        self.responses = {
            "greeting": [
                "Olá! Sou o Cidadão.AI, inspirado no poeta Carlos Drummond de Andrade. Como posso ajudá-lo com transparência governamental hoje?",
                "Bom dia! Como diria Drummond, 'No meio do caminho tinha uma pedra'... mas aqui, vamos remover as pedras do caminho da transparência!",
                "Uai, seja bem-vindo! Estou aqui para ajudar você a entender melhor os dados públicos.",
            ],
            "help": [
                "Posso ajudá-lo a investigar contratos, analisar gastos públicos e detectar anomalias. Experimente perguntar 'quero investigar contratos da saúde'!",
                "O Cidadão.AI tem vários agentes especializados: Zumbi (investigação), Anita (análise), Tiradentes (relatórios). Como posso direcioná-lo?",
                "Para começar uma investigação, diga algo como 'verificar gastos do ministério' ou 'procurar irregularidades em licitações'.",
            ],
            "about": [
                "O Cidadão.AI é um sistema multi-agente para análise de transparência governamental. Cada agente tem uma especialidade, unidos pela poesia da clareza!",
                "Somos 17 agentes com identidades brasileiras, trabalhando juntos para tornar os dados públicos mais acessíveis e compreensíveis.",
                "Como Drummond disse: 'A máquina do mundo se entreabriu'... O Cidadão.AI é essa máquina, revelando o que sempre foi seu direito saber.",
            ],
            "thanks": [
                "Ora, não há de quê! Como dizemos em Minas: 'é dando que se recebe'. Continue fiscalizando!",
                "Disponha sempre! A transparência é um direito seu e um prazer meu em ajudar.",
                "Fico feliz em ajudar! Lembre-se: a cidadania ativa é a melhor poesia.",
            ],
            "goodbye": [
                "Até breve! Como disse Drummond: 'A vida é breve, a alma é vasta.' Continue vasto em sua busca pela transparência!",
                "Vai com Deus e com dados! Estarei aqui quando precisar.",
                "Tchau! Que seu caminho seja claro como água de mina!",
            ],
            "default": [
                "Interessante sua pergunta! Posso ajudá-lo a investigar contratos ou analisar gastos públicos. O que gostaria de explorar?",
                "Hmm, deixe-me pensar como posso ajudar melhor... Você quer investigar algo específico ou conhecer melhor o sistema?",
                "Como diria Drummond, cada pergunta é uma porta. Que porta da transparência você quer abrir hoje?",
            ],
        }

    async def initialize(self) -> None:
        """Initialize the agent."""
        self.logger.info("SimpleDrummondAgent initialized")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info("SimpleDrummondAgent shutting down")

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Process a message and return a response."""
        try:
            # Extract user message and intent
            payload = message.payload if hasattr(message, "payload") else {}
            user_message = payload.get("user_message", "")
            intent_data = payload.get("intent", {})
            intent_type = intent_data.get("type", "unknown")

            self.logger.info(f"Processing message with intent: {intent_type}")

            # Select response based on intent
            if intent_type == "greeting":
                response_list = self.responses["greeting"]
            elif intent_type in ["help", "help_request"]:
                response_list = self.responses["help"]
            elif intent_type == "about_system":
                response_list = self.responses["about"]
            elif intent_type == "thanks":
                response_list = self.responses["thanks"]
            elif intent_type == "goodbye":
                response_list = self.responses["goodbye"]
            else:
                response_list = self.responses["default"]

            # Select a random response
            response_text = np.random.choice(response_list)

            # If we have Maritaca API key, add a note about enhanced capabilities
            if self.has_maritaca and intent_type not in [
                "greeting",
                "goodbye",
                "thanks",
            ]:
                response_text += "\n\n💡 *Com a Maritaca AI ativada, posso fornecer respostas ainda mais contextualizadas!*"

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result={
                    "message": response_text,
                    "intent_type": intent_type,
                    "confidence": 0.95,
                },
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "maritaca_enabled": self.has_maritaca,
                },
            )

        except Exception as e:
            self.logger.error(f"Error in SimpleDrummondAgent: {e}")
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                result={
                    "message": "Desculpe, tive um problema ao processar sua mensagem. Por favor, tente novamente.",
                    "error": str(e),
                },
            )
