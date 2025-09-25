"""
Module: tests.unit.agents.test_tiradentes_pdf
Description: Unit tests for Tiradentes PDF generation functionality
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import pytest
import base64
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.tiradentes import (
    ReporterAgent, ReportRequest, ReportFormat, ReportType,
    ReportSection, AgentContext
)


class TestTiradentePDFGeneration:
    """Test suite for Tiradentes PDF generation."""
    
    @pytest.fixture
    def reporter_agent(self):
        """Create ReporterAgent instance."""
        return ReporterAgent()
    
    @pytest.fixture
    def agent_context(self):
        """Create agent context for testing."""
        return AgentContext(
            conversation_id="test-conv-001",
            user_id="test-user-123",
            investigation_id="INV-001",
            session_data={}
        )
    
    @pytest.fixture
    def sample_sections(self):
        """Create sample report sections."""
        return [
            ReportSection(
                title="Resumo Executivo",
                content="Este relatório apresenta as principais descobertas da investigação.",
                importance=5,
                subsections=None,
                charts=None,
                tables=None
            ),
            ReportSection(
                title="Anomalias Detectadas",
                content="""
## Anomalia 1: Valor Atípico
- **Severidade**: 0.85
- **Descrição**: Contrato com valor 300% acima da média
- **Recomendação**: Investigação detalhada necessária

## Anomalia 2: Padrão Temporal
- **Severidade**: 0.72
- **Descrição**: Concentração anormal de contratos
""",
                importance=4,
                subsections=None,
                charts=None,
                tables=None
            ),
            ReportSection(
                title="Conclusões",
                content="As anomalias identificadas sugerem possíveis irregularidades.",
                importance=3,
                subsections=None,
                charts=None,
                tables=None
            )
        ]
    
    @pytest.mark.asyncio
    @patch('src.agents.tiradentes.export_service')
    async def test_render_pdf_basic(
        self, mock_export_service, reporter_agent, sample_sections, agent_context
    ):
        """Test basic PDF rendering."""
        # Setup mock
        mock_export_service.generate_pdf.return_value = b'mock-pdf-content'
        
        # Create request
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.PDF,
            target_audience="technical",
            language="pt-BR"
        )
        
        # Render PDF
        result = await reporter_agent._render_pdf(
            sections=sample_sections,
            request=request,
            context=agent_context
        )
        
        # Verify result is base64 encoded
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        assert decoded == b'mock-pdf-content'
        
        # Verify export service was called
        mock_export_service.generate_pdf.assert_called_once()
        call_args = mock_export_service.generate_pdf.call_args
        
        # Check arguments
        assert "Este relatório apresenta" in call_args[1]['content']
        assert call_args[1]['title'] == "Relatório: Investigation Report"
        assert call_args[1]['metadata']['report_type'] == 'investigation_report'
        assert call_args[1]['metadata']['investigation_id'] == 'INV-001'
    
    @pytest.mark.asyncio
    @patch('src.agents.tiradentes.export_service')
    async def test_render_pdf_with_metadata(
        self, mock_export_service, reporter_agent, sample_sections, agent_context
    ):
        """Test PDF rendering with full metadata."""
        # Setup mock
        mock_export_service.generate_pdf.return_value = b'pdf-with-metadata'
        
        # Create request
        request = ReportRequest(
            report_type=ReportType.EXECUTIVE_SUMMARY,
            format=ReportFormat.PDF,
            target_audience="executive",
            language="pt-BR"
        )
        
        # Render PDF
        result = await reporter_agent._render_pdf(
            sections=sample_sections,
            request=request,
            context=agent_context
        )
        
        # Verify metadata passed to export service
        call_metadata = mock_export_service.generate_pdf.call_args[1]['metadata']
        assert call_metadata['target_audience'] == 'executive'
        assert call_metadata['author'] == 'Agente Tiradentes - Cidadão.AI'
        assert 'generated_at' in call_metadata
    
    @pytest.mark.asyncio
    @patch('src.agents.tiradentes.export_service')
    async def test_render_pdf_format_type(
        self, mock_export_service, reporter_agent, sample_sections, agent_context
    ):
        """Test PDF rendering passes correct format type."""
        # Setup mock
        mock_export_service.generate_pdf.return_value = b'typed-pdf'
        
        # Create request
        request = ReportRequest(
            report_type=ReportType.TREND_ANALYSIS,
            format=ReportFormat.PDF,
            target_audience="researcher",
            language="pt-BR"
        )
        
        # Render PDF
        await reporter_agent._render_pdf(
            sections=sample_sections,
            request=request,
            context=agent_context
        )
        
        # Verify format_type parameter
        assert mock_export_service.generate_pdf.call_args[1]['format_type'] == "report"
    
    @pytest.mark.asyncio
    async def test_pdf_format_in_renderers(self, reporter_agent):
        """Test PDF format is registered in format renderers."""
        assert ReportFormat.PDF in reporter_agent.format_renderers
        assert reporter_agent.format_renderers[ReportFormat.PDF] == reporter_agent._render_pdf
    
    @pytest.mark.asyncio
    @patch('src.agents.tiradentes.export_service')
    async def test_render_pdf_markdown_conversion(
        self, mock_export_service, reporter_agent, agent_context
    ):
        """Test PDF rendering converts sections to markdown first."""
        # Setup mock to capture markdown content
        markdown_content = None
        
        async def capture_markdown(*args, **kwargs):
            nonlocal markdown_content
            markdown_content = kwargs['content']
            return b'test-pdf'
        
        mock_export_service.generate_pdf.side_effect = capture_markdown
        
        # Create simple sections
        sections = [
            ReportSection(
                title="Test Section",
                content="Test content",
                importance=5
            )
        ]
        
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.PDF,
            target_audience="general",
            language="pt-BR"
        )
        
        # Render PDF
        await reporter_agent._render_pdf(sections, request, agent_context)
        
        # Verify markdown was generated
        assert markdown_content is not None
        assert "# Relatório: Investigation Report" in markdown_content
        assert "## Test Section" in markdown_content
        assert "Test content" in markdown_content
    
    @pytest.mark.asyncio
    @patch('src.agents.tiradentes.export_service')
    async def test_render_pdf_error_handling(
        self, mock_export_service, reporter_agent, sample_sections, agent_context
    ):
        """Test PDF rendering error handling."""
        # Setup mock to raise exception
        mock_export_service.generate_pdf.side_effect = Exception("PDF generation failed")
        
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.PDF,
            target_audience="technical",
            language="pt-BR"
        )
        
        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await reporter_agent._render_pdf(
                sections=sample_sections,
                request=request,
                context=agent_context
            )
        
        assert "PDF generation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('src.agents.tiradentes.export_service')
    async def test_render_pdf_empty_sections(
        self, mock_export_service, reporter_agent, agent_context
    ):
        """Test PDF rendering with empty sections."""
        # Setup mock
        mock_export_service.generate_pdf.return_value = b'empty-pdf'
        
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.PDF,
            target_audience="general",
            language="pt-BR"
        )
        
        # Render with empty sections
        result = await reporter_agent._render_pdf(
            sections=[],
            request=request,
            context=agent_context
        )
        
        # Should still generate PDF
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        assert decoded == b'empty-pdf'
    
    @pytest.mark.asyncio
    @patch('src.agents.tiradentes.export_service')
    async def test_render_pdf_large_content(
        self, mock_export_service, reporter_agent, agent_context
    ):
        """Test PDF rendering with large content."""
        # Create large sections
        large_sections = []
        for i in range(10):
            large_sections.append(
                ReportSection(
                    title=f"Section {i}",
                    content="Very long content. " * 100,
                    importance=3
                )
            )
        
        # Setup mock
        mock_export_service.generate_pdf.return_value = b'large-pdf'
        
        request = ReportRequest(
            report_type=ReportType.INVESTIGATION_REPORT,
            format=ReportFormat.PDF,
            target_audience="technical",
            language="pt-BR"
        )
        
        # Render PDF
        result = await reporter_agent._render_pdf(
            sections=large_sections,
            request=request,
            context=agent_context
        )
        
        # Verify it handles large content
        assert isinstance(result, str)
        call_content = mock_export_service.generate_pdf.call_args[1]['content']
        assert len(call_content) > 10000  # Should be quite large