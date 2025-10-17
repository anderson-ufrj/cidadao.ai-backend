"""
Module: tests.test_cli.test_investigate_command
Description: Tests for the investigate CLI command
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
import json
from unittest.mock import patch

from typer.testing import CliRunner

from src.cli.commands.investigate import app

runner = CliRunner()


class TestInvestigateCommand:
    """Test suite for investigate command."""

    def test_investigate_help(self):
        """Test help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "investigate" in result.stdout
        assert "Execute an investigation" in result.stdout

    def test_investigate_without_query(self):
        """Test command without required query."""
        result = runner.invoke(app, [])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_basic(self, mock_api):
        """Test basic investigation."""
        # Mock API responses
        mock_api.return_value = asyncio.run(self._mock_investigation_response())

        # Run command
        result = runner.invoke(app, ["Test investigation"])

        # Verify
        assert result.exit_code == 0
        assert "Investigation ID:" in result.stdout
        assert "Completed" in result.stdout
        assert mock_api.called

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_with_data_sources(self, mock_api):
        """Test investigation with specific data sources."""
        mock_api.return_value = asyncio.run(self._mock_investigation_response())

        result = runner.invoke(
            app,
            ["Test investigation", "--source", "contracts", "--source", "suppliers"],
        )

        assert result.exit_code == 0
        # Verify data sources were passed
        call_args = mock_api.call_args_list[0]
        assert call_args[1]["data"]["data_sources"] == ["contracts", "suppliers"]

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_with_filters(self, mock_api):
        """Test investigation with filters."""
        mock_api.return_value = asyncio.run(self._mock_investigation_response())

        result = runner.invoke(
            app,
            [
                "Test investigation",
                "--filter",
                "organization:MIN_SAUDE",
                "--filter",
                "value:>1000000",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_api.call_args_list[0]
        filters = call_args[1]["data"]["filters"]
        assert filters["organization"] == "MIN_SAUDE"
        assert filters["value"] == ">1000000"

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_with_output_format(self, mock_api):
        """Test investigation with different output formats."""
        mock_api.return_value = asyncio.run(self._mock_investigation_response())

        # Test JSON output
        result = runner.invoke(app, ["Test investigation", "--output", "json"])

        assert result.exit_code == 0
        # Output should be valid JSON
        output_data = json.loads(result.stdout)
        assert output_data["investigation_id"] == "INV-123"

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_with_save_path(self, mock_api, tmp_path):
        """Test saving investigation results."""
        mock_api.return_value = asyncio.run(self._mock_investigation_response())

        save_path = tmp_path / "investigation.json"

        result = runner.invoke(app, ["Test investigation", "--save", str(save_path)])

        assert result.exit_code == 0
        assert save_path.exists()

        # Verify saved content
        with open(save_path) as f:
            saved_data = json.load(f)
            assert saved_data["investigation_id"] == "INV-123"

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_timeout_handling(self, mock_api):
        """Test timeout parameter."""
        mock_api.return_value = asyncio.run(self._mock_investigation_response())

        result = runner.invoke(app, ["Test investigation", "--timeout", "60"])

        assert result.exit_code == 0
        # Verify timeout was set
        call_args = mock_api.call_args_list[0]
        assert call_args[1]["data"]["timeout"] == 60

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_error_handling(self, mock_api):
        """Test error handling."""
        mock_api.side_effect = Exception("API Error")

        result = runner.invoke(app, ["Test investigation"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    @patch("src.cli.commands.investigate.call_api")
    def test_investigate_streaming_mode(self, mock_api):
        """Test streaming mode with updates."""

        # Mock multiple status updates
        async def mock_multiple_responses(*args, **kwargs):
            endpoint = args[0]
            if "status" in endpoint:
                # Return different statuses on consecutive calls
                if not hasattr(mock_multiple_responses, "call_count"):
                    mock_multiple_responses.call_count = 0
                mock_multiple_responses.call_count += 1

                if mock_multiple_responses.call_count == 1:
                    return {"status": "running", "progress": 0.5}
                else:
                    return {"status": "completed", "progress": 1.0}
            else:
                return await self._mock_investigation_response()

        mock_api.side_effect = lambda *args, **kwargs: asyncio.run(
            mock_multiple_responses(*args, **kwargs)
        )

        result = runner.invoke(app, ["Test investigation", "--stream"])

        assert result.exit_code == 0
        assert "Investigation ID:" in result.stdout

    async def _mock_investigation_response(self):
        """Create mock investigation response."""
        return {
            "investigation_id": "INV-123",
            "query": "Test investigation",
            "status": "completed",
            "progress": 1.0,
            "started_at": "2025-01-25T10:00:00",
            "completed_at": "2025-01-25T10:05:00",
            "findings": [
                {
                    "type": "anomaly",
                    "severity": "high",
                    "description": "Unusual spending pattern detected",
                    "data": {"contract_id": "CTR-001"},
                }
            ],
            "anomalies": [
                {
                    "score": 0.85,
                    "type": "value_anomaly",
                    "description": "Contract value significantly above average",
                }
            ],
            "recommendations": [
                "Review contract CTR-001 for potential irregularities",
                "Investigate supplier history",
            ],
            "summary": "Investigation found 1 high-severity anomaly",
            "confidence_score": 0.89,
            "agents_used": ["zumbi", "anita", "tiradentes"],
        }


class TestInvestigateHelpers:
    """Test helper functions."""

    def test_filter_parsing(self):
        """Test filter string parsing."""
        from src.cli.commands.investigate import parse_filters

        filters = parse_filters(
            ["key1:value1", "key2:value2", "invalid_filter", "key3:value:with:colons"]
        )

        assert filters["key1"] == "value1"
        assert filters["key2"] == "value2"
        assert "invalid_filter" not in filters
        assert filters["key3"] == "value:with:colons"

    def test_format_display_functions(self):
        """Test display formatting functions."""
        from src.cli.commands.investigate import (
            display_anomalies,
            display_findings,
            display_recommendations,
        )

        # These should not raise errors
        findings = [{"type": "test", "description": "Test finding"}]
        anomalies = [{"score": 0.8, "description": "Test anomaly"}]
        recommendations = ["Test recommendation"]

        # Just verify they don't crash
        display_findings(findings)
        display_anomalies(anomalies)
        display_recommendations(recommendations)
