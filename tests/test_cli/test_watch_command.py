"""
Module: tests.test_cli.test_watch_command
Description: Tests for the watch CLI command
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from typer.testing import CliRunner
from pathlib import Path
import signal
import time

from src.cli.commands.watch import app, MonitoringMode, AlertLevel


runner = CliRunner()


class TestWatchCommand:
    """Test suite for watch command."""
    
    def test_watch_help(self):
        """Test help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "watch" in result.stdout
        assert "Monitor government data" in result.stdout
    
    def test_watch_modes(self):
        """Test different monitoring modes."""
        for mode in MonitoringMode:
            result = runner.invoke(app, [mode.value, "--help"])
            assert result.exit_code == 0
    
    @patch('src.cli.commands.watch.call_api')
    def test_test_connection_success(self, mock_api):
        """Test connection test command."""
        mock_api.return_value = asyncio.run(self._mock_health_response())
        
        result = runner.invoke(app, ["test-connection"])
        
        assert result.exit_code == 0
        assert "API connection successful" in result.stdout
    
    @patch('src.cli.commands.watch.call_api')
    def test_test_connection_failure(self, mock_api):
        """Test connection test with failure."""
        mock_api.side_effect = Exception("Connection failed")
        
        result = runner.invoke(app, ["test-connection"])
        
        assert result.exit_code != 0
        assert "Connection failed" in result.stdout
    
    @patch('src.cli.commands.watch.call_api')
    @patch('src.cli.commands.watch.Live')
    def test_watch_contracts_basic(self, mock_live, mock_api):
        """Test basic contract monitoring."""
        # Mock API responses
        mock_api.return_value = asyncio.run(self._mock_contracts_response())
        
        # Mock live display
        mock_live_instance = MagicMock()
        mock_live.return_value.__enter__.return_value = mock_live_instance
        
        # Simulate interrupt after short time
        def side_effect(*args, **kwargs):
            # Set shutdown flag after first call
            import src.cli.commands.watch as watch_module
            watch_module.shutdown_requested = True
            return asyncio.run(self._mock_contracts_response())
        
        mock_api.side_effect = side_effect
        
        result = runner.invoke(app, ["contracts"])
        
        assert result.exit_code == 0
        assert "Monitoring stopped gracefully" in result.stdout
    
    @patch('src.cli.commands.watch.call_api')
    @patch('src.cli.commands.watch.Live')
    def test_watch_with_filters(self, mock_live, mock_api):
        """Test monitoring with filters."""
        mock_api.return_value = asyncio.run(self._mock_anomalies_response())
        
        # Set up shutdown
        def side_effect(*args, **kwargs):
            import src.cli.commands.watch as watch_module
            watch_module.shutdown_requested = True
            return asyncio.run(self._mock_anomalies_response())
        
        mock_api.side_effect = side_effect
        
        result = runner.invoke(app, [
            "anomalies",
            "--org", "MIN_SAUDE",
            "--org", "MIN_EDUCACAO",
            "--threshold", "0.8",
            "--interval", "10"
        ])
        
        assert result.exit_code == 0
        # Verify filters were applied
        call_args = mock_api.call_args_list[0]
        params = call_args[1]['params']
        assert params['threshold'] == 0.8
    
    @patch('src.cli.commands.watch.call_api')
    @patch('src.cli.commands.watch.Live')
    def test_watch_with_export(self, mock_live, mock_api, tmp_path):
        """Test monitoring with alert export."""
        mock_api.return_value = asyncio.run(self._mock_anomalies_response())
        
        export_path = tmp_path / "alerts.log"
        
        # Set up shutdown
        def side_effect(*args, **kwargs):
            import src.cli.commands.watch as watch_module
            watch_module.shutdown_requested = True
            return asyncio.run(self._mock_anomalies_response())
        
        mock_api.side_effect = side_effect
        
        result = runner.invoke(app, [
            "anomalies",
            "--export", str(export_path)
        ])
        
        assert result.exit_code == 0
        assert export_path.exists()
        
        # Check export content
        content = export_path.read_text()
        assert "Cidadão.AI Watch Mode" in content
    
    def test_dashboard_components(self):
        """Test dashboard rendering functions."""
        from src.cli.commands.watch import (
            create_dashboard_layout,
            render_header,
            render_stats,
            render_alerts,
            render_footer,
            MonitoringConfig,
            MonitoringStats
        )
        
        # Create test data
        config = MonitoringConfig(
            mode=MonitoringMode.CONTRACTS,
            anomaly_threshold=0.7,
            alert_level=AlertLevel.MEDIUM,
            check_interval=60
        )
        
        stats = MonitoringStats(
            start_time=asyncio.run(self._get_datetime()),
            checks_performed=10,
            anomalies_detected=3,
            alerts_triggered=1,
            active_alerts=[
                {
                    "timestamp": "2025-01-25T10:00:00",
                    "level": "high",
                    "type": "anomaly",
                    "description": "Test alert"
                }
            ]
        )
        
        # Test rendering (should not raise exceptions)
        layout = create_dashboard_layout()
        header = render_header(config)
        stats_panel = render_stats(stats)
        alerts_panel = render_alerts(stats)
        footer = render_footer()
        
        assert layout is not None
        assert header is not None
        assert stats_panel is not None
        assert alerts_panel is not None
        assert footer is not None
    
    @patch('src.cli.commands.watch.call_api')
    def test_anomaly_detection_logic(self, mock_api):
        """Test anomaly detection and alerting logic."""
        from src.cli.commands.watch import check_for_anomalies, MonitoringConfig, MonitoringStats
        
        mock_api.return_value = asyncio.run(self._mock_anomalies_with_alerts())
        
        config = MonitoringConfig(
            mode=MonitoringMode.ANOMALIES,
            anomaly_threshold=0.7,
            alert_level=AlertLevel.MEDIUM,
            check_interval=60
        )
        
        stats = MonitoringStats(start_time=asyncio.run(self._get_datetime()))
        
        # Run check
        alerts = asyncio.run(check_for_anomalies(config, stats))
        
        assert len(alerts) > 0
        assert stats.anomalies_detected > 0
        assert stats.checks_performed == 1
    
    async def _mock_health_response(self):
        """Mock health check response."""
        return {"status": "healthy", "version": "1.0.0"}
    
    async def _mock_contracts_response(self):
        """Mock contracts response."""
        return [
            {
                "id": "CTR-001",
                "value": 1500000,
                "organization": "MIN_SAUDE",
                "supplier": "Supplier A"
            }
        ]
    
    async def _mock_anomalies_response(self):
        """Mock anomalies response."""
        return [
            {
                "id": "ANOM-001",
                "severity": 0.75,
                "type": "value_anomaly",
                "description": "Unusual contract value"
            }
        ]
    
    async def _mock_anomalies_with_alerts(self):
        """Mock anomalies that should trigger alerts."""
        return [
            {
                "id": "ANOM-001",
                "severity": 0.85,
                "type": "critical_anomaly",
                "description": "Critical anomaly detected"
            },
            {
                "id": "ANOM-002",
                "severity": 0.95,
                "type": "fraud_risk",
                "description": "High fraud risk detected"
            }
        ]
    
    async def _get_datetime(self):
        """Get datetime for async context."""
        from datetime import datetime
        return datetime.now()


class TestMonitoringHelpers:
    """Test monitoring helper functions."""
    
    def test_signal_handler_setup(self):
        """Test signal handler setup."""
        from src.cli.commands.watch import setup_signal_handlers
        
        # Should not raise exception
        setup_signal_handlers()
    
    def test_monitoring_config_validation(self):
        """Test monitoring configuration."""
        from src.cli.commands.watch import MonitoringConfig
        
        config = MonitoringConfig(
            mode=MonitoringMode.CONTRACTS,
            organizations=["ORG1", "ORG2"],
            min_value=1000000,
            anomaly_threshold=0.8
        )
        
        assert config.mode == MonitoringMode.CONTRACTS
        assert len(config.organizations) == 2
        assert config.min_value == 1000000
        assert config.anomaly_threshold == 0.8