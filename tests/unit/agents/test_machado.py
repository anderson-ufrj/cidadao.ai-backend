"""
Unit tests for Machado Agent - Natural Language Processing specialist.
Tests text analysis, sentiment analysis, and document processing capabilities.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from src.agents.machado import (
    MachadoAgent,
    TextAnalysisRequest,
    LanguageProcessingResult,
    SentimentAnalysis,
    EntityExtraction,
    DocumentSummary,
)
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)
from src.core.exceptions import AgentExecutionError


@pytest.fixture
def mock_nlp_service():
    """Mock NLP service for testing."""
    service = AsyncMock()
    
    service.analyze_sentiment.return_value = {
        "sentiment": "negative",
        "confidence": 0.87,
        "score": -0.65,
        "emotions": {
            "anger": 0.23,
            "fear": 0.15,
            "disgust": 0.31,
            "sadness": 0.18,
            "joy": 0.05,
            "surprise": 0.08
        }
    }
    
    service.extract_entities.return_value = {
        "entities": [
            {
                "text": "Ministério da Educação",
                "label": "ORG",
                "confidence": 0.98,
                "start": 45,
                "end": 67
            },
            {
                "text": "R$ 2.500.000,00",
                "label": "MONEY",
                "confidence": 0.95,
                "start": 85,
                "end": 100
            },
            {
                "text": "João Silva",
                "label": "PERSON",
                "confidence": 0.92,
                "start": 120,
                "end": 130
            }
        ],
        "relationships": [
            {
                "subject": "João Silva",
                "predicate": "trabalha_em",
                "object": "Ministério da Educação",
                "confidence": 0.78
            }
        ]
    }
    
    service.classify_text.return_value = {
        "categories": [
            {"label": "procurement", "confidence": 0.91},
            {"label": "irregularity", "confidence": 0.76},
            {"label": "corruption", "confidence": 0.64}
        ],
        "main_category": "procurement",
        "confidence": 0.91
    }
    
    service.summarize_text.return_value = {
        "summary": "Contrato de fornecimento de equipamentos de informática no valor de R$ 2,5 milhões apresenta irregularidades no processo licitatório.",
        "key_points": [
            "Valor elevado para equipamentos básicos",
            "Processo licitatório questionável", 
            "Fornecedor com histórico de problemas"
        ],
        "compression_ratio": 0.15,
        "reading_time_minutes": 2
    }
    
    service.detect_anomalies_text.return_value = {
        "anomalies": [
            {
                "type": "unusual_terminology",
                "confidence": 0.82,
                "description": "Uso de termos técnicos inconsistentes",
                "locations": [{"start": 234, "end": 267}]
            },
            {
                "type": "sentiment_shift",
                "confidence": 0.74,
                "description": "Mudança abrupta no tom do documento",
                "locations": [{"start": 456, "end": 523}]
            }
        ],
        "overall_anomaly_score": 0.68
    }
    
    return service


@pytest.fixture
def mock_translation_service():
    """Mock translation service."""
    service = AsyncMock()
    service.translate.return_value = {
        "translated_text": "Government procurement contract for IT equipment worth $500,000 shows irregularities.",
        "source_language": "pt",
        "target_language": "en",
        "confidence": 0.94
    }
    return service


@pytest.fixture
def agent_context():
    """Test agent context."""
    return AgentContext(
        investigation_id="nlp-investigation-001",
        user_id="analyst-user",
        session_id="analysis-session",
        metadata={
            "analysis_type": "document_processing",
            "language": "pt-BR",
            "priority": "medium"
        },
        trace_id="trace-machado-456"
    )


@pytest.fixture
def machado_agent(mock_nlp_service, mock_translation_service):
    """Create Machado agent with mocked dependencies."""
    with patch("src.agents.machado.NLPService", return_value=mock_nlp_service), \
         patch("src.agents.machado.TranslationService", return_value=mock_translation_service):
        
        agent = MachadoAgent(
            sentiment_threshold=0.3,
            entity_confidence_threshold=0.7,
            summary_max_length=200,
            supported_languages=["pt", "en", "es"]
        )
        return agent


class TestMachadoAgent:
    """Test suite for Machado (NLP Agent)."""
    
    @pytest.mark.unit
    def test_agent_initialization(self, machado_agent):
        """Test Machado agent initialization."""
        assert machado_agent.name == "Machado"
        assert machado_agent.sentiment_threshold == 0.3
        assert machado_agent.entity_confidence_threshold == 0.7
        assert machado_agent.summary_max_length == 200
        assert "pt" in machado_agent.supported_languages
        
        # Check capabilities
        expected_capabilities = [
            "text_analysis",
            "sentiment_analysis",
            "entity_extraction", 
            "document_summarization",
            "language_detection",
            "translation",
            "text_classification"
        ]
        
        for capability in expected_capabilities:
            assert capability in machado_agent.capabilities
    
    @pytest.mark.unit
    async def test_sentiment_analysis(self, machado_agent, agent_context):
        """Test sentiment analysis functionality."""
        text = "Este contrato apresenta várias irregularidades graves que prejudicam o interesse público."
        
        message = AgentMessage(
            sender="investigator_agent",
            recipient="Machado",
            action="analyze_sentiment",
            payload={
                "text": text,
                "include_emotions": True,
                "language": "pt"
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "sentiment_analysis" in response.result
        
        sentiment = response.result["sentiment_analysis"]
        assert sentiment["sentiment"] == "negative"
        assert sentiment["confidence"] == 0.87
        assert "emotions" in sentiment
        assert sentiment["emotions"]["disgust"] > 0.3
    
    @pytest.mark.unit
    async def test_entity_extraction(self, machado_agent, agent_context):
        """Test named entity recognition."""
        text = "O contrato do Ministério da Educação no valor de R$ 2.500.000,00 foi assinado por João Silva."
        
        message = AgentMessage(
            sender="analyst_agent",
            recipient="Machado",
            action="extract_entities",
            payload={
                "text": text,
                "entity_types": ["ORG", "PERSON", "MONEY"],
                "include_relationships": True
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "entity_extraction" in response.result
        
        entities = response.result["entity_extraction"]
        assert len(entities["entities"]) == 3
        
        # Check specific entities
        org_entity = next(e for e in entities["entities"] if e["label"] == "ORG")
        assert org_entity["text"] == "Ministério da Educação"
        assert org_entity["confidence"] > 0.9
        
        money_entity = next(e for e in entities["entities"] if e["label"] == "MONEY")
        assert "2.500.000" in money_entity["text"]
        
        # Check relationships
        assert len(entities["relationships"]) > 0
    
    @pytest.mark.unit
    async def test_text_classification(self, machado_agent, agent_context):
        """Test text classification."""
        text = "Licitação para fornecimento de equipamentos com evidências de superfaturamento."
        
        message = AgentMessage(
            sender="reporter_agent",
            recipient="Machado",
            action="classify_text",
            payload={
                "text": text,
                "categories": ["procurement", "irregularity", "corruption", "normal"],
                "confidence_threshold": 0.6
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "text_classification" in response.result
        
        classification = response.result["text_classification"]
        assert classification["main_category"] == "procurement"
        assert classification["confidence"] > 0.9
        assert len(classification["categories"]) > 0
    
    @pytest.mark.unit
    async def test_document_summarization(self, machado_agent, agent_context):
        """Test document summarization."""
        long_text = """
        O Ministério da Educação celebrou contrato de fornecimento de equipamentos de informática 
        no valor total de R$ 2.500.000,00 com a empresa Tech Solutions LTDA. O processo licitatório 
        foi conduzido na modalidade pregão eletrônico, porém apresenta diversas irregularidades.
        
        Durante a análise dos documentos, foram identificadas inconsistências nos preços apresentados
        pela vencedora, que estão significativamente acima dos valores de mercado. Além disso,
        verificou-se que a empresa não possui experiência prévia no fornecimento de equipamentos
        similares para órgãos públicos.
        
        A comissão de licitação não realizou adequadamente a verificação dos documentos de 
        habilitação técnica, permitindo a participação de empresa sem qualificação adequada.
        Recomenda-se a revisão do processo e possível anulação do contrato.
        """
        
        message = AgentMessage(
            sender="master_agent",
            recipient="Machado",
            action="summarize_document",
            payload={
                "text": long_text,
                "max_length": 100,
                "include_key_points": True,
                "extract_recommendations": True
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "document_summary" in response.result
        
        summary = response.result["document_summary"]
        assert len(summary["summary"]) <= 150  # Allowing some margin
        assert len(summary["key_points"]) >= 2
        assert summary["compression_ratio"] < 0.3
        assert summary["reading_time_minutes"] > 0
    
    @pytest.mark.unit
    async def test_language_detection(self, machado_agent, agent_context):
        """Test language detection."""
        texts = [
            "Este documento está em português brasileiro.",
            "This document is written in English.",
            "Este documento está escrito en español."
        ]
        
        message = AgentMessage(
            sender="data_processor",
            recipient="Machado",
            action="detect_language",
            payload={
                "texts": texts,
                "confidence_threshold": 0.8
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "language_detection" in response.result
        
        languages = response.result["language_detection"]
        assert len(languages) == 3
        # Note: Mock service doesn't implement language detection, 
        # so we're testing the interface
    
    @pytest.mark.unit
    async def test_text_translation(self, machado_agent, agent_context):
        """Test text translation."""
        text = "Contrato de licitação apresenta irregularidades no valor de R$ 500.000,00."
        
        message = AgentMessage(
            sender="international_analyst",
            recipient="Machado",
            action="translate_text",
            payload={
                "text": text,
                "target_language": "en",
                "source_language": "pt"
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "translation" in response.result
        
        translation = response.result["translation"]
        assert translation["source_language"] == "pt"
        assert translation["target_language"] == "en"
        assert translation["confidence"] > 0.9
        assert "contract" in translation["translated_text"].lower()
    
    @pytest.mark.unit
    async def test_text_anomaly_detection(self, machado_agent, agent_context):
        """Test text anomaly detection."""
        text = """
        O contrato de fornecimento apresenta características normais no início do documento.
        Porém, súbitamente o texto muda de tom e apresenta terminologias técnicas inconsistentes
        que não condizem com o padrão usual de documentos oficiais.
        """
        
        message = AgentMessage(
            sender="quality_analyst",
            recipient="Machado", 
            action="detect_text_anomalies",
            payload={
                "text": text,
                "anomaly_types": ["sentiment_shift", "terminology_inconsistency", "style_change"],
                "sensitivity": 0.7
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "text_anomalies" in response.result
        
        anomalies = response.result["text_anomalies"]
        assert len(anomalies["anomalies"]) >= 1
        assert anomalies["overall_anomaly_score"] > 0.6
        
        # Check specific anomaly types
        sentiment_anomaly = next(
            (a for a in anomalies["anomalies"] if a["type"] == "sentiment_shift"),
            None
        )
        assert sentiment_anomaly is not None
    
    @pytest.mark.unit
    async def test_batch_text_processing(self, machado_agent, agent_context):
        """Test batch processing of multiple texts."""
        texts = [
            "Primeiro documento sobre licitação normal.",
            "Segundo documento com irregularidades graves no processo.",
            "Terceiro documento apresentando superfaturamento evidente."
        ]
        
        message = AgentMessage(
            sender="batch_processor",
            recipient="Machado",
            action="batch_analyze",
            payload={
                "texts": texts,
                "operations": ["sentiment", "entities", "classification"],
                "aggregate_results": True
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "batch_analysis" in response.result
        
        batch_results = response.result["batch_analysis"]
        assert len(batch_results["individual_results"]) == 3
        assert "aggregated_metrics" in batch_results
        assert "processing_statistics" in batch_results
    
    @pytest.mark.unit
    async def test_document_comparison(self, machado_agent, agent_context):
        """Test document similarity and comparison."""
        doc1 = "Contrato de fornecimento de equipamentos de informática."
        doc2 = "Acordo para fornecimento de computadores e periféricos."
        doc3 = "Contrato de prestação de serviços de consultoria."
        
        message = AgentMessage(
            sender="comparative_analyst",
            recipient="Machado",
            action="compare_documents",
            payload={
                "documents": [doc1, doc2, doc3],
                "comparison_methods": ["semantic", "structural", "lexical"],
                "similarity_threshold": 0.5
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "document_comparison" in response.result
        
        comparison = response.result["document_comparison"]
        assert "similarity_matrix" in comparison
        assert "clusters" in comparison
        assert "outliers" in comparison
    
    @pytest.mark.unit
    async def test_error_handling_invalid_text(self, machado_agent, agent_context):
        """Test error handling with invalid text input."""
        message = AgentMessage(
            sender="test_agent",
            recipient="Machado",
            action="analyze_sentiment",
            payload={
                "text": "",  # Empty text
                "language": "pt"
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.ERROR
        assert "empty" in response.error.lower() or "invalid" in response.error.lower()
    
    @pytest.mark.unit
    async def test_unsupported_language_handling(self, machado_agent, agent_context):
        """Test handling of unsupported languages."""
        message = AgentMessage(
            sender="test_agent",
            recipient="Machado",
            action="analyze_sentiment",
            payload={
                "text": "这是中文文本",  # Chinese text
                "language": "zh"  # Unsupported language
            }
        )
        
        response = await machado_agent.process(message, agent_context)
        
        # Should either process with warning or gracefully handle
        assert response.status in [AgentStatus.COMPLETED, AgentStatus.WARNING]
        if response.status == AgentStatus.WARNING:
            assert "language" in response.error.lower()
    
    @pytest.mark.unit
    async def test_performance_optimization(self, machado_agent, agent_context):
        """Test performance optimization features."""
        large_text = "Lorem ipsum " * 1000  # Large text
        
        message = AgentMessage(
            sender="performance_tester",
            recipient="Machado",
            action="analyze_sentiment",
            payload={
                "text": large_text,
                "optimize_for_speed": True,
                "max_processing_time": 5.0
            }
        )
        
        start_time = datetime.utcnow()
        response = await machado_agent.process(message, agent_context)
        end_time = datetime.utcnow()
        
        processing_time = (end_time - start_time).total_seconds()
        
        assert response.status == AgentStatus.COMPLETED
        assert processing_time < 10.0  # Should complete within reasonable time
        assert response.processing_time_ms is not None


class TestTextAnalysisRequest:
    """Test TextAnalysisRequest model."""
    
    @pytest.mark.unit
    def test_request_creation(self):
        """Test creating text analysis request."""
        request = TextAnalysisRequest(
            text="Texto para análise",
            analysis_types=["sentiment", "entities"],
            language="pt",
            options={
                "include_confidence": True,
                "detailed_output": True
            }
        )
        
        assert request.text == "Texto para análise"
        assert len(request.analysis_types) == 2
        assert request.language == "pt"
        assert request.options["include_confidence"] is True
    
    @pytest.mark.unit
    def test_request_validation(self):
        """Test request validation."""
        # Valid request
        valid_request = TextAnalysisRequest(
            text="Valid text",
            analysis_types=["sentiment"]
        )
        assert valid_request.text == "Valid text"
        
        # Test with empty text
        with pytest.raises(ValueError):
            TextAnalysisRequest(
                text="",
                analysis_types=["sentiment"]
            )


class TestLanguageProcessingResult:
    """Test LanguageProcessingResult model."""
    
    @pytest.mark.unit
    def test_result_creation(self):
        """Test creating language processing result."""
        result = LanguageProcessingResult(
            request_id="req-001",
            text_analyzed="Sample text",
            analysis_results={
                "sentiment": {"polarity": "positive", "confidence": 0.85},
                "entities": [{"text": "Entity", "label": "ORG"}]
            },
            processing_metadata={
                "language_detected": "en",
                "processing_time_ms": 150.5,
                "model_versions": {"sentiment": "v2.1", "ner": "v1.8"}
            }
        )
        
        assert result.request_id == "req-001"
        assert result.text_analyzed == "Sample text"
        assert result.analysis_results["sentiment"]["confidence"] == 0.85
        assert result.processing_metadata["processing_time_ms"] == 150.5
    
    @pytest.mark.unit
    def test_result_confidence_calculation(self):
        """Test overall confidence calculation."""
        result = LanguageProcessingResult(
            request_id="test",
            text_analyzed="test",
            analysis_results={
                "sentiment": {"confidence": 0.9},
                "entities": {"confidence": 0.8},
                "classification": {"confidence": 0.7}
            }
        )
        
        overall_confidence = result.calculate_overall_confidence()
        assert 0.75 <= overall_confidence <= 0.85  # Average should be around 0.8


class TestSentimentAnalysis:
    """Test SentimentAnalysis model."""
    
    @pytest.mark.unit
    def test_sentiment_creation(self):
        """Test creating sentiment analysis result."""
        sentiment = SentimentAnalysis(
            polarity="negative",
            confidence=0.92,
            score=-0.75,
            emotions={
                "anger": 0.4,
                "sadness": 0.3,
                "disgust": 0.2,
                "fear": 0.1
            }
        )
        
        assert sentiment.polarity == "negative"
        assert sentiment.confidence == 0.92
        assert sentiment.score == -0.75
        assert sentiment.emotions["anger"] == 0.4
    
    @pytest.mark.unit
    def test_sentiment_validation(self):
        """Test sentiment validation."""
        # Valid sentiment
        valid_sentiment = SentimentAnalysis(
            polarity="positive",
            confidence=0.8,
            score=0.6
        )
        assert valid_sentiment.polarity == "positive"
        
        # Test confidence bounds
        with pytest.raises(ValueError):
            SentimentAnalysis(
                polarity="neutral",
                confidence=1.5,  # Invalid confidence > 1
                score=0.0
            )