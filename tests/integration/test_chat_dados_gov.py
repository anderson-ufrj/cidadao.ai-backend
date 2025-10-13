"""
Integration tests for chat with dados.gov.br.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.api.routes.chat_zumbi_integration import (
    format_investigation_message,
    run_zumbi_investigation,
)


@pytest.fixture
def mock_investigation_result():
    """Mock investigation result with dados.gov.br data"""
    return {
        "status": "completed",
        "anomalies_found": 2,
        "records_analyzed": 50,
        "anomalies": [
            {
                "anomaly_type": "price_anomaly",
                "severity": 0.85,
                "confidence": 0.9,
                "description": "Contrato com preço 150% acima da média",
                "evidence": {
                    "_open_data_available": True,
                    "_related_datasets": [
                        {"title": "Licitações e Contratos - Ministério da Saúde 2024"},
                        {"title": "Preços Referenciais de Medicamentos"},
                    ],
                },
            },
            {
                "anomaly_type": "vendor_concentration",
                "severity": 0.72,
                "confidence": 0.85,
                "description": "Fornecedor recebeu 80% dos contratos",
                "evidence": {"_open_data_available": False, "_related_datasets": []},
            },
        ],
        "summary": {
            "total_value": 1500000.0,
            "organizations_count": 1,
            "suppliers_count": 5,
        },
        "open_data_available": True,
        "related_datasets": [
            "Licitações e Contratos - Ministério da Saúde 2024",
            "Preços Referenciais de Medicamentos",
        ],
    }


class TestChatDadosGovIntegration:
    """Test chat integration with dados.gov.br"""

    def test_format_investigation_message_with_open_data(
        self, mock_investigation_result
    ):
        """Test message formatting with open data references"""
        message = format_investigation_message(mock_investigation_result)

        # Check basic structure
        assert "🏹 **Investigação Concluída**" in message
        assert "Registros analisados: 50" in message
        assert "Anomalias detectadas: 2" in message

        # Check open data information
        assert "📂 Datasets abertos encontrados: 2" in message
        assert "💡 **Dados Abertos Disponíveis:**" in message
        assert "Licitações e Contratos - Ministério da Saúde 2024" in message

        # Check anomaly with open data
        assert "📂 Dados abertos relacionados disponíveis" in message

    def test_format_investigation_message_without_open_data(self):
        """Test message formatting without open data"""
        result = {
            "status": "completed",
            "anomalies_found": 1,
            "records_analyzed": 30,
            "anomalies": [
                {
                    "anomaly_type": "temporal_pattern",
                    "severity": 0.6,
                    "description": "Contratos concentrados no final do ano",
                    "evidence": {},
                }
            ],
            "summary": {},
            "open_data_available": False,
            "related_datasets": [],
        }

        message = format_investigation_message(result)

        # Should not have open data references
        assert "📂 Datasets abertos encontrados" not in message
        assert "💡 **Dados Abertos Disponíveis:**" not in message

    def test_format_investigation_message_with_error(self):
        """Test error message formatting"""
        result = {
            "status": "error",
            "error": "Connection timeout",
            "anomalies_found": 0,
            "records_analyzed": 0,
        }

        message = format_investigation_message(result)

        assert "❌ Erro na investigação" in message
        assert "Connection timeout" in message

    @pytest.mark.asyncio
    async def test_run_zumbi_investigation_success(self, mock_investigation_result):
        """Test successful investigation with dados.gov.br"""
        # Mock the agent
        mock_agent = AsyncMock()
        mock_agent.process.return_value = AsyncMock(
            status="completed",
            result={
                "status": "completed",
                "anomalies": mock_investigation_result["anomalies"],
                "summary": mock_investigation_result["summary"],
                "metadata": {"anomalies_detected": 2, "records_analyzed": 50},
            },
        )

        with patch(
            "src.api.routes.chat_zumbi_integration.get_zumbi_agent",
            return_value=mock_agent,
        ):
            result = await run_zumbi_investigation(
                query="Investigar contratos do Ministério da Saúde",
                enable_open_data=True,
            )

            assert result["status"] == "completed"
            assert result["anomalies_found"] == 2
            assert result["records_analyzed"] == 50

            # Verify agent was called with correct parameters
            mock_agent.process.assert_called_once()
            call_args = mock_agent.process.call_args[0][0]
            assert call_args["action"] == "investigate"
            assert call_args["payload"]["enable_open_data_enrichment"] is True

    @pytest.mark.asyncio
    async def test_run_zumbi_investigation_with_org_codes(self):
        """Test investigation with organization codes"""
        mock_agent = AsyncMock()
        mock_agent.process.return_value = AsyncMock(
            status="completed",
            result={"status": "completed", "anomalies": [], "metadata": {}},
        )

        with patch(
            "src.api.routes.chat_zumbi_integration.get_zumbi_agent",
            return_value=mock_agent,
        ):
            await run_zumbi_investigation(
                query="Test query",
                organization_codes=["26000", "25000"],
                enable_open_data=True,
            )

            # Check organization codes were passed
            call_args = mock_agent.process.call_args[0][0]
            assert call_args["payload"]["organization_codes"] == ["26000", "25000"]

    @pytest.mark.asyncio
    async def test_run_zumbi_investigation_error_handling(self):
        """Test error handling in investigation"""
        mock_agent = AsyncMock()
        mock_agent.process.side_effect = Exception("Agent initialization failed")

        with patch(
            "src.api.routes.chat_zumbi_integration.get_zumbi_agent",
            return_value=mock_agent,
        ):
            result = await run_zumbi_investigation(
                query="Test query", enable_open_data=True
            )

            assert result["status"] == "error"
            assert "Agent initialization failed" in result["error"]
            assert result["anomalies_found"] == 0

    def test_suggested_actions_with_open_data(self, mock_investigation_result):
        """Test that suggested actions include open data exploration"""
        # This would be tested in the chat endpoint
        # but we can check the logic
        suggested_actions = []

        if mock_investigation_result["anomalies_found"] > 0:
            suggested_actions.append("🔍 Ver detalhes das anomalias")
            suggested_actions.append("📊 Gerar relatório completo")
            if mock_investigation_result.get("open_data_available"):
                suggested_actions.append("📂 Explorar dados abertos relacionados")

        assert "📂 Explorar dados abertos relacionados" in suggested_actions
