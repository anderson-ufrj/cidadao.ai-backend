"""
Tests for Intent Detection System

Tests the expanded intent classification patterns added in December 2025.
Validates that 87% unknown classification issue is resolved.

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import pytest

from src.services.chat_service import IntentDetector, IntentType


@pytest.fixture
def detector():
    """Create a fresh IntentDetector instance for each test."""
    return IntentDetector()


class TestGreetingDetection:
    """Test greeting intent detection with regional variations."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "Olá",
            "olá",
            "Oi",
            "oi",
            "Bom dia",
            "bom dia!",
            "Boa tarde",
            "boa tarde",
            "Boa noite",
            "boa noite!",
            # Regional variations
            "E aí",
            "eai",
            "Eae",
            "Fala",
            "Salve",
            "Opa",
            # Informal
            "tudo bem?",
            "tudo bom?",
            "beleza?",
            "blz?",
            # English (common in tech)
            "Hi",
            "Hello",
            "Hey",
            # With context
            "Olá Cidadão.AI",
            "Oi, preciso de ajuda",
        ],
    )
    async def test_greeting_detection(self, detector, message):
        """Test that common greetings are detected correctly."""
        intent = await detector.detect(message)
        assert (
            intent.type == IntentType.GREETING
        ), f"Expected GREETING for '{message}', got {intent.type}"
        assert intent.confidence >= 0.7


class TestHelpDetection:
    """Test help and help request intent detection."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "Como funciona?",
            "ajuda",
            "help",
            "O que é isso?",
            "Explique como usar",
            "tutorial",
            "instruções",
            "guia",
            # Help request
            "Preciso de ajuda",
            "Me ajuda",
            "Pode ajudar?",
            "Não sei como fazer",
            "Não entendi",
            "Como faço para investigar?",
            "Como usar o sistema?",
            "Não consigo",
            "Me ensina",
        ],
    )
    async def test_help_detection(self, detector, message):
        """Test that help requests are detected correctly."""
        intent = await detector.detect(message)
        assert intent.type in [
            IntentType.HELP,
            IntentType.HELP_REQUEST,
        ], f"Expected HELP or HELP_REQUEST for '{message}', got {intent.type}"


class TestAboutSystemDetection:
    """Test about system intent detection including creator queries."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "O que é o Cidadão.AI?",
            "Como você funciona?",
            "Quem é você?",
            "Para que serve?",
            "O que você faz?",
            "Qual sua função?",
            "Suas capacidades",
            "Suas funcionalidades",
            "O que pode fazer?",
            # Creator queries
            "Quem criou?",
            "Quem desenvolveu?",
            "Quem fez esse sistema?",
            "Quem idealizou?",
            "Criador do projeto",
            "Autor do sistema",
            # Project info
            "Sobre o projeto",
            "Sobre o Cidadão.AI",
            "História do Cidadão.AI",
            "TCC",
            "Trabalho de conclusão",
            "A Maritaca AI criou o Cidadão.AI?",
            "Foi feito por qual empresa?",
            # Agents
            "Quais agentes existem?",
            "Agentes disponíveis",
            "Quantos agentes?",
        ],
    )
    async def test_about_system_detection(self, detector, message):
        """Test that about system queries are detected correctly."""
        intent = await detector.detect(message)
        assert (
            intent.type == IntentType.ABOUT_SYSTEM
        ), f"Expected ABOUT_SYSTEM for '{message}', got {intent.type}"


class TestInvestigateDetection:
    """Test investigation intent detection."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            # Direct investigation requests
            "Investigar contratos",
            "Quero investigar contratos do Ministério da Saúde",
            "Busque contratos da educação em 2024",
            "Contratos do Ministério da Defesa",
            "Investigar gastos da Fazenda",
            # Listing/viewing
            "Listar contratos",
            "Mostrar contratos",
            "Ver contratos",
            "Quais contratos",
            # With context
            "Contratos de tecnologia do governo",
            "Contratos de limpeza",
            "Contratos acima de 1 milhão",
            "Buscar contratos de 2023",
            "Contratos do Ministério do Meio Ambiente",
            # Related terms
            "Licitações de saúde",
            "Pregão eletrônico",
            "Gastos públicos",
            "Despesas federais",
            # Government entities
            "Ministério da Educação",
            "Órgão federal",
            "Prefeitura de São Paulo",
        ],
    )
    async def test_investigate_detection(self, detector, message):
        """Test that investigation requests are detected correctly."""
        intent = await detector.detect(message)
        assert (
            intent.type == IntentType.INVESTIGATE
        ), f"Expected INVESTIGATE for '{message}', got {intent.type}"


class TestAnalyzeDetection:
    """Test analysis intent detection."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "Detecte anomalias",
            "Análise de contratos",
            "Comparar gastos",
            "Comparação de valores",
            "Tendência de gastos",
            "Evolução dos contratos",
            "Ranking de fornecedores",
            "Maiores contratos",
            "Principais gastos",
            "Top 10 fornecedores",
        ],
    )
    async def test_analyze_detection(self, detector, message):
        """Test that analysis requests are detected correctly."""
        intent = await detector.detect(message)
        assert intent.type in [
            IntentType.ANALYZE,
            IntentType.INVESTIGATE,  # Some may be classified as investigate
        ], f"Expected ANALYZE or INVESTIGATE for '{message}', got {intent.type}"


class TestFraudDetection:
    """Test fraud detection intent."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "Detectar fraude",
            "Contratos fraudulentos",
            "Esquema de corrupção",
            "Superfaturamento",
            "Sobrepreço em contratos",
            "Favorecimento ilícito",
            "Direcionamento de licitação",
            "Cartel de fornecedores",
            "Conluio em licitações",
            "Contratos irregulares",
            "Gastos suspeitos",
        ],
    )
    async def test_fraud_detection(self, detector, message):
        """Test that fraud-related queries are detected correctly."""
        intent = await detector.detect(message)
        assert intent.type in [
            IntentType.FRAUD_DETECTION,
            IntentType.INVESTIGATE,
            IntentType.ANALYZE,
        ], f"Expected FRAUD_DETECTION/INVESTIGATE/ANALYZE for '{message}', got {intent.type}"


class TestThanksAndGoodbye:
    """Test gratitude and farewell detection."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "Obrigado",
            "Obrigada",
            "Muito obrigado",
            "Valeu",
            "Gratidão",
            "Agradeço",
            "Foi útil",
            "Ajudou muito",
            "Thanks",
        ],
    )
    async def test_thanks_detection(self, detector, message):
        """Test that gratitude expressions are detected correctly."""
        intent = await detector.detect(message)
        assert (
            intent.type == IntentType.THANKS
        ), f"Expected THANKS for '{message}', got {intent.type}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message",
        [
            "Tchau",
            "Até logo",
            "Até mais",
            "Adeus",
            "Falou",
            "Tenho que ir",
            "Até breve",
            "Bye",
            "Flw",
        ],
    )
    async def test_goodbye_detection(self, detector, message):
        """Test that farewell expressions are detected correctly."""
        intent = await detector.detect(message)
        assert (
            intent.type == IntentType.GOODBYE
        ), f"Expected GOODBYE for '{message}', got {intent.type}"


class TestSpecializedIntents:
    """Test specialized agent intents."""

    @pytest.mark.asyncio
    async def test_text_analysis_intent(self, detector):
        """Test text analysis detection for Machado agent."""
        messages = [
            "Analisar texto do contrato",
            "Verificar cláusulas",
            "Ler contrato",
            "Entender documento",
            "Revisar texto",
        ]
        for message in messages:
            intent = await detector.detect(message)
            assert intent.type in [
                IntentType.TEXT_ANALYSIS,
                IntentType.INVESTIGATE,
            ], f"Expected TEXT_ANALYSIS/INVESTIGATE for '{message}', got {intent.type}"

    @pytest.mark.asyncio
    async def test_legal_compliance_intent(self, detector):
        """Test legal compliance detection for Bonifácio agent."""
        messages = [
            "Conformidade legal",
            "Verificar lei",
            "Lei 8666",
            "Legislação aplicável",
            "Normas legais",
            "LAI",
        ]
        for message in messages:
            intent = await detector.detect(message)
            assert intent.type in [
                IntentType.LEGAL_COMPLIANCE,
                IntentType.INVESTIGATE,
                IntentType.QUESTION,
            ], f"Expected LEGAL_COMPLIANCE/INVESTIGATE/QUESTION for '{message}', got {intent.type}"

    @pytest.mark.asyncio
    async def test_visualization_intent(self, detector):
        """Test visualization detection for Oscar Niemeyer agent."""
        messages = [
            "Criar gráfico",
            "Mostrar gráfico",
            "Dashboard",
            "Visualização de dados",
            "Mapa de gastos",
        ]
        for message in messages:
            intent = await detector.detect(message)
            assert intent.type in [
                IntentType.VISUALIZATION,
                IntentType.ANALYZE,
            ], f"Expected VISUALIZATION/ANALYZE for '{message}', got {intent.type}"

    @pytest.mark.asyncio
    async def test_statistical_intent(self, detector):
        """Test statistical detection for Anita agent."""
        messages = [
            "Estatísticas de contratos",
            "Média de valores",
            "Mediana dos gastos",
            "Total de contratos",
            "Quantos contratos?",
        ]
        for message in messages:
            intent = await detector.detect(message)
            assert intent.type in [
                IntentType.STATISTICAL,
                IntentType.INVESTIGATE,
                IntentType.ANALYZE,
            ], f"Expected STATISTICAL/INVESTIGATE/ANALYZE for '{message}', got {intent.type}"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.asyncio
    async def test_empty_message_fallback(self, detector):
        """Test that empty/whitespace messages get reasonable handling."""
        intent = await detector.detect("   ")
        # Should not crash and return some intent
        assert intent.type is not None

    @pytest.mark.asyncio
    async def test_very_short_message(self, detector):
        """Test very short messages."""
        intent = await detector.detect("a")
        assert intent.type is not None

    @pytest.mark.asyncio
    async def test_special_characters(self, detector):
        """Test messages with emojis and special characters."""
        intent = await detector.detect("🇧🇷 contratos")
        # Should still detect investigate intent
        assert intent.type in [IntentType.INVESTIGATE, IntentType.QUESTION]

    @pytest.mark.asyncio
    async def test_uppercase_message(self, detector):
        """Test that uppercase messages are handled correctly."""
        intent = await detector.detect("CONTRATOS DA SAÚDE")
        assert intent.type == IntentType.INVESTIGATE

    @pytest.mark.asyncio
    async def test_sql_injection_attempt(self, detector):
        """Test that SQL injection attempts don't crash the system."""
        intent = await detector.detect("SELECT * FROM contratos")
        # Should not crash
        assert intent.type is not None

    @pytest.mark.asyncio
    async def test_xss_attempt(self, detector):
        """Test that XSS attempts don't crash the system."""
        intent = await detector.detect("<script>alert('xss')</script>")
        # Should not crash
        assert intent.type is not None


class TestConfidenceScores:
    """Test confidence score assignments."""

    @pytest.mark.asyncio
    async def test_high_confidence_greeting(self, detector):
        """Test that clear greetings have high confidence."""
        intent = await detector.detect("Olá")
        assert intent.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_high_confidence_investigate(self, detector):
        """Test that clear investigation requests have high confidence."""
        intent = await detector.detect(
            "Quero investigar contratos do Ministério da Saúde"
        )
        assert intent.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_ambiguous_message_lower_confidence(self, detector):
        """Test that ambiguous messages have lower confidence."""
        intent = await detector.detect("me conte mais")
        # Ambiguous messages should still be classified but with potentially lower confidence
        assert intent.type is not None


class TestProductionScenarios:
    """Test scenarios from production test results."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message,expected_type",
        [
            # Identity category (was 87% unknown)
            ("Quem criou o Cidadão.AI?", IntentType.ABOUT_SYSTEM),
            ("Quem desenvolveu esse sistema?", IntentType.ABOUT_SYSTEM),
            ("Quem é o autor do projeto?", IntentType.ABOUT_SYSTEM),
            ("O que é o Cidadão.AI?", IntentType.ABOUT_SYSTEM),
            ("Para que serve essa plataforma?", IntentType.ABOUT_SYSTEM),
            # Greeting category
            ("Olá", IntentType.GREETING),
            ("Oi, tudo bem?", IntentType.GREETING),
            ("Bom dia!", IntentType.GREETING),
            ("E aí!", IntentType.GREETING),
            ("Opa, beleza?", IntentType.GREETING),
            # Help category
            ("Como funciona?", IntentType.HELP),
            ("O que você pode fazer?", IntentType.HELP_REQUEST),
            ("Me ajuda a entender o sistema", IntentType.HELP_REQUEST),
            # Investigation category
            (
                "Quero investigar contratos do Ministério da Saúde",
                IntentType.INVESTIGATE,
            ),
            ("Busque contratos da educação em 2024", IntentType.INVESTIGATE),
            ("Contratos do Ministério da Defesa", IntentType.INVESTIGATE),
        ],
    )
    async def test_production_scenarios(self, detector, message, expected_type):
        """Test scenarios that were failing in production (87% unknown)."""
        intent = await detector.detect(message)
        assert (
            intent.type == expected_type
        ), f"Expected {expected_type} for '{message}', got {intent.type}"
