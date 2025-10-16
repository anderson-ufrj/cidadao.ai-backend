"""
Tests for Machado de Assis Agent (Text Analysis Specialist)
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.machado import MachadoAgent, DocumentType, TextAnalysisResult
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.core.exceptions import AgentExecutionError


@pytest.fixture
def agent_context():
    """Create test agent context."""
    return AgentContext(
        investigation_id="test-123",
        user_id="user-123",
        session_id="session-123",
        metadata={}
    )


@pytest.fixture
def agent():
    """Create Machado agent instance."""
    return MachadoAgent()


class TestMachadoAgent:
    """Test suite for Machado de Assis Agent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_id == "machado"
        assert agent.name == "Machado de Assis"
        assert agent.description == "Government document analysis and text processing specialist"
        assert agent.status == AgentStatus.IDLE
        assert agent.capabilities == [
            "text_analysis",
            "document_extraction", 
            "contract_parsing",
            "clause_identification",
            "legal_compliance_check",
            "semantic_similarity"
        ]
    
    @pytest.mark.asyncio
    async def test_initialize(self, agent):
        """Test agent initialization process."""
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE
    
    @pytest.mark.asyncio
    async def test_analyze_contract_document(self, agent, agent_context):
        """Test contract document analysis."""
        # Create test document
        document = {
            "type": "contract",
            "title": "Contrato de Prestação de Serviços",
            "content": """
            CONTRATO Nº 001/2025
            CONTRATANTE: Prefeitura Municipal
            CONTRATADO: Empresa XYZ LTDA
            VALOR: R$ 500.000,00
            PRAZO: 12 meses
            OBJETO: Prestação de serviços de consultoria
            """
        }
        
        # Create message
        message = AgentMessage(
            role="user",
            content="Analyze government contract",
            data=document
        )
        
        # Process message
        response = await agent.process(message, agent_context)
        
        # Verify response
        assert response.success
        assert "analysis" in response.data
        analysis = response.data["analysis"]
        assert "entities" in analysis
        assert "key_terms" in analysis
        assert "contract_value" in analysis
        assert analysis["contract_value"] == 500000.0
    
    @pytest.mark.asyncio
    async def test_extract_key_clauses(self, agent, agent_context):
        """Test key clause extraction from documents."""
        document = {
            "type": "public_tender",
            "content": """
            EDITAL DE LICITAÇÃO Nº 002/2025
            1. DO OBJETO: Aquisição de equipamentos de informática
            2. DO VALOR: R$ 1.200.000,00
            3. DOS PRAZOS: Entrega em 60 dias
            4. DAS PENALIDADES: Multa de 10% por atraso
            5. DA GARANTIA: 12 meses
            """
        }
        
        message = AgentMessage(
            role="user",
            content="Extract key clauses",
            data=document
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        assert "clauses" in response.data
        clauses = response.data["clauses"]
        assert len(clauses) > 0
        assert any("objeto" in c["type"].lower() for c in clauses)
        assert any("valor" in c["type"].lower() for c in clauses)
    
    @pytest.mark.asyncio
    async def test_semantic_similarity_analysis(self, agent, agent_context):
        """Test semantic similarity between documents."""
        data = {
            "documents": [
                {
                    "id": "doc1",
                    "content": "Contrato de prestação de serviços de consultoria técnica"
                },
                {
                    "id": "doc2",
                    "content": "Acordo para fornecimento de assessoria técnica especializada"
                }
            ]
        }
        
        message = AgentMessage(
            role="user",
            content="Analyze semantic similarity",
            data=data
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        assert "similarity_matrix" in response.data
        assert response.data["similarity_matrix"]["doc1"]["doc2"] > 0.5  # High similarity expected
    
    @pytest.mark.asyncio
    async def test_compliance_check(self, agent, agent_context):
        """Test legal compliance checking."""
        document = {
            "type": "contract",
            "content": """
            CONTRATO EMERGENCIAL
            Dispensa de licitação conforme Art. 24, IV da Lei 8.666/93
            Valor: R$ 50.000,00
            Prazo: 180 dias
            """
        }
        
        message = AgentMessage(
            role="user",
            content="Check legal compliance",
            data=document
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        assert "compliance" in response.data
        compliance = response.data["compliance"]
        assert "issues" in compliance
        assert "recommendations" in compliance
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent, agent_context):
        """Test error handling for invalid documents."""
        # Invalid document
        message = AgentMessage(
            role="user",
            content="Analyze document",
            data={"type": "unknown"}  # Missing content
        )
        
        response = await agent.process(message, agent_context)
        
        assert not response.success
        assert "error" in response.data
    
    @pytest.mark.asyncio
    async def test_batch_document_processing(self, agent, agent_context):
        """Test batch processing of multiple documents."""
        documents = {
            "documents": [
                {"id": "1", "type": "contract", "content": "Contrato 1"},
                {"id": "2", "type": "public_tender", "content": "Edital 2"},
                {"id": "3", "type": "law", "content": "Lei 3"}
            ]
        }
        
        message = AgentMessage(
            role="user",
            content="Batch analyze documents",
            data=documents
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        assert "batch_results" in response.data
        assert len(response.data["batch_results"]) == 3