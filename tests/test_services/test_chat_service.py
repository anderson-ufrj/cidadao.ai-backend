"""
Tests for chat service and intent detection
"""

import pytest

from src.services.chat_service import IntentDetector, IntentType


class TestIntentDetection:
    """Test intent detection for conversational and task-specific intents"""

    @pytest.fixture
    def detector(self):
        return IntentDetector()

    @pytest.mark.asyncio
    async def test_greeting_intents(self, detector):
        """Test greeting intent detection"""
        greetings = [
            "Olá, bom dia!",
            "Oi, tudo bem?",
            "Boa tarde",
            "E aí, como vai?",
            "Bom dia, preciso de ajuda",
        ]

        for greeting in greetings:
            intent = await detector.detect(greeting)
            assert intent.type == IntentType.GREETING, f"Failed for: {greeting}"
            assert intent.suggested_agent == "drummond"

    @pytest.mark.asyncio
    async def test_conversation_intents(self, detector):
        """Test general conversation intent detection"""
        conversations = [
            "Vamos conversar sobre transparência",
            "Quero falar sobre corrupção no governo",
            "Me conte mais sobre isso",
            "Pode me falar sobre os gastos públicos?",
        ]

        for message in conversations:
            intent = await detector.detect(message)
            assert intent.type == IntentType.CONVERSATION, f"Failed for: {message}"
            assert intent.suggested_agent == "drummond"

    @pytest.mark.asyncio
    async def test_help_request_intents(self, detector):
        """Test help request intent detection"""
        help_requests = [
            "Preciso de ajuda para entender",
            "Me ajuda com isso?",
            "Não sei como fazer",
            "Pode ajudar?",
            "Não entendi direito",
        ]

        for message in help_requests:
            intent = await detector.detect(message)
            assert intent.type == IntentType.HELP_REQUEST, f"Failed for: {message}"
            assert intent.suggested_agent == "drummond"

    @pytest.mark.asyncio
    async def test_about_system_intents(self, detector):
        """Test system information intent detection"""
        about_messages = [
            "O que é o Cidadão.AI?",
            "Como você funciona?",
            "Quem é você?",
            "Para que serve este sistema?",
            "O que você faz?",
            "Qual sua função aqui?",
        ]

        for message in about_messages:
            intent = await detector.detect(message)
            assert intent.type == IntentType.ABOUT_SYSTEM, f"Failed for: {message}"
            assert intent.suggested_agent == "drummond"

    @pytest.mark.asyncio
    async def test_smalltalk_intents(self, detector):
        """Test smalltalk intent detection"""
        smalltalk_messages = [
            "Como está o tempo hoje?",
            "Você gosta de poesia?",
            "Qual sua opinião sobre política?",
            "O que acha do Brasil?",
            "Conte uma história",
            "Você é brasileiro?",
        ]

        for message in smalltalk_messages:
            intent = await detector.detect(message)
            assert intent.type == IntentType.SMALLTALK, f"Failed for: {message}"
            assert intent.suggested_agent == "drummond"

    @pytest.mark.asyncio
    async def test_thanks_intents(self, detector):
        """Test gratitude intent detection"""
        thanks_messages = [
            "Obrigado!",
            "Muito obrigada pela ajuda",
            "Valeu mesmo",
            "Gratidão",
            "Agradeço a atenção",
            "Foi útil, obrigado",
        ]

        for message in thanks_messages:
            intent = await detector.detect(message)
            assert intent.type == IntentType.THANKS, f"Failed for: {message}"
            assert intent.suggested_agent == "drummond"

    @pytest.mark.asyncio
    async def test_goodbye_intents(self, detector):
        """Test farewell intent detection"""
        goodbye_messages = [
            "Tchau!",
            "Até logo",
            "Até mais ver",
            "Adeus",
            "Falou, valeu!",
            "Tenho que ir agora",
            "Até breve",
        ]

        for message in goodbye_messages:
            intent = await detector.detect(message)
            assert intent.type == IntentType.GOODBYE, f"Failed for: {message}"
            assert intent.suggested_agent == "drummond"

    @pytest.mark.asyncio
    async def test_task_specific_intents_remain_unchanged(self, detector):
        """Test that task-specific intents still work correctly"""
        task_messages = [
            ("Investigar contratos da saúde", IntentType.INVESTIGATE, "abaporu"),
            ("Analisar gastos excessivos", IntentType.ANALYZE, "anita"),
            ("Gerar relatório completo", IntentType.REPORT, "tiradentes"),
            ("Qual o status da investigação?", IntentType.STATUS, "abaporu"),
        ]

        for message, expected_type, expected_agent in task_messages:
            intent = await detector.detect(message)
            assert intent.type == expected_type, f"Failed for: {message}"
            assert intent.suggested_agent == expected_agent

    @pytest.mark.asyncio
    async def test_mixed_intents_prioritize_correctly(self, detector):
        """Test that mixed messages are correctly prioritized"""
        mixed_messages = [
            # Greeting + task should prioritize task
            ("Bom dia, quero investigar contratos", IntentType.INVESTIGATE, "abaporu"),
            # Help + specific task should prioritize task
            ("Me ajuda a analisar anomalias", IntentType.ANALYZE, "anita"),
            # Pure conversational should go to Drummond
            ("Olá, como funciona isso aqui?", IntentType.GREETING, "drummond"),
        ]

        for message, expected_type, expected_agent in mixed_messages:
            intent = await detector.detect(message)
            assert intent.type == expected_type, f"Failed for: {message}"
            assert intent.suggested_agent == expected_agent

    @pytest.mark.asyncio
    async def test_unknown_defaults_to_drummond(self, detector):
        """Test that unknown intents go to Drummond for handling"""
        unknown_messages = [
            "xyzabc123",
            "????????",
            "asdfghjkl",
        ]

        for message in unknown_messages:
            intent = await detector.detect(message)
            # Should be QUESTION (default) or UNKNOWN
            assert intent.type in [IntentType.QUESTION, IntentType.UNKNOWN]
            assert intent.suggested_agent == "drummond"
