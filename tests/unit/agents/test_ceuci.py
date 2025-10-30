"""
Unit tests for Ceuci Agent - ML/Predictive Analysis specialist.
Tests time series prediction, anomaly forecasting, and trend analysis capabilities.
"""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.agents.ceuci import PredictiveAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus


@pytest.fixture
def agent_context():
    """Create test agent context."""
    return AgentContext(
        investigation_id="pred-test-001",
        user_id="test_user",
        session_id="test_session",
        metadata={"analysis_type": "prediction"},
    )


@pytest.fixture
def ceuci_agent():
    """Create Céuci agent instance for testing."""
    config = {
        "default_model": "random_forest",
        "confidence_threshold": 0.7,
        "min_training_samples": 10,
    }
    return PredictiveAgent(config=config)


@pytest.fixture
def sample_time_series_data():
    """Create sample time series data for testing."""
    dates = pd.date_range(start="2024-01-01", periods=24, freq="M")
    values = [100 + i * 5 + np.random.normal(0, 10) for i in range(24)]  # Trend + noise
    return pd.DataFrame({"date": dates, "value": values})


@pytest.fixture
def sample_contracts_data():
    """Create sample contracts data for trend analysis."""
    return [
        {
            "date": f"2024-{i:02d}-01",
            "value": 100000 + i * 10000,
            "category": "education",
            "region": "southeast",
        }
        for i in range(1, 13)
    ]


# ============================================================================
# INITIALIZATION AND SETUP TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciInitialization:
    """Test Céuci agent initialization and configuration."""

    def test_agent_initialization_default(self):
        """Test agent initialization with default config."""
        agent = PredictiveAgent()
        assert agent.name == "Ceuci"
        assert "time_series_forecasting" in agent.capabilities
        assert "anomaly_prediction" in agent.capabilities
        assert "trend_modeling" in agent.capabilities

    def test_agent_initialization_custom_config(self):
        """Test agent initialization with custom config."""
        config = {
            "default_model": "arima",
            "confidence_threshold": 0.8,
            "min_training_samples": 20,
        }
        agent = PredictiveAgent(config=config)
        assert agent.config["default_model"] == "arima"
        assert agent.config["confidence_threshold"] == 0.8
        assert agent.config["min_training_samples"] == 20

    @pytest.mark.asyncio
    async def test_agent_initialize(self, ceuci_agent):
        """Test agent initialization method."""
        await ceuci_agent.initialize()
        # Should complete without errors
        assert True

    @pytest.mark.asyncio
    async def test_agent_shutdown(self, ceuci_agent):
        """Test agent shutdown method."""
        await ceuci_agent.shutdown()
        # Should complete without errors
        assert True


# ============================================================================
# PROCESS METHOD TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciProcess:
    """Test Céuci agent message processing."""

    @pytest.mark.asyncio
    async def test_process_time_series_prediction(self, ceuci_agent, agent_context):
        """Test processing time series prediction request."""
        message = AgentMessage(
            sender="test_agent",
            recipient="Ceuci",
            action="predict",
            payload={
                "prediction_type": "time_series",
                "horizon": 6,
                "data": [{"month": i, "value": 100 + i * 10} for i in range(12)],
            },
        )

        response = await ceuci_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "prediction_result" in response.result
        assert response.result["prediction_result"]["model_used"] == "ARIMA"
        assert "confidence" in response.metadata

    @pytest.mark.asyncio
    async def test_process_anomaly_forecast(self, ceuci_agent, agent_context):
        """Test processing anomaly forecast request."""
        message = AgentMessage(
            sender="test_agent",
            recipient="Ceuci",
            action="predict",
            payload={
                "prediction_type": "anomaly_forecast",
                "data": [{"value": 100 + i * 5} for i in range(20)],
            },
        )

        response = await ceuci_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "prediction_result" in response.result
        result = response.result["prediction_result"]
        assert "anomaly_probability" in result
        assert "risk_level" in result
        assert result["model_used"] == "Isolation Forest"

    @pytest.mark.asyncio
    async def test_process_trend_analysis(self, ceuci_agent, agent_context):
        """Test processing trend analysis request."""
        message = AgentMessage(
            sender="test_agent",
            recipient="Ceuci",
            action="predict",
            payload={
                "prediction_type": "trend_analysis",
                "data": [{"month": i, "spending": 50000 + i * 5000} for i in range(12)],
            },
        )

        response = await ceuci_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        result = response.result["prediction_result"]
        assert "trend_direction" in result
        assert "trend_strength" in result
        assert result["model_used"] == "Linear Regression"

    @pytest.mark.asyncio
    async def test_process_unknown_prediction_type(self, ceuci_agent, agent_context):
        """Test processing unknown prediction type."""
        message = AgentMessage(
            sender="test_agent",
            recipient="Ceuci",
            action="predict",
            payload={"prediction_type": "unknown_type", "data": []},
        )

        response = await ceuci_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert (
            "not specifically implemented"
            in response.result["prediction_result"]["message"]
        )

    @pytest.mark.asyncio
    async def test_process_with_string_data(self, ceuci_agent, agent_context):
        """Test processing with string data instead of dict."""
        message = AgentMessage(
            sender="test_agent",
            recipient="Ceuci",
            action="predict",
            payload="predict future spending",
        )

        response = await ceuci_agent.process(message, agent_context)

        # Should handle gracefully and return default prediction
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_process_error_handling(self, ceuci_agent, agent_context):
        """Test error handling in process method."""
        # Create a message that will cause an error
        message = AgentMessage(
            sender="test_agent", recipient="Ceuci", action="predict", payload=None
        )

        with patch.object(
            ceuci_agent, "_time_series_prediction", side_effect=Exception("Test error")
        ):
            response = await ceuci_agent.process(message, agent_context)

        assert response.status == AgentStatus.ERROR
        assert response.error == "Test error"


# ============================================================================
# PREDICTION TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciPredictions:
    """Test specific prediction methods."""

    @pytest.mark.asyncio
    async def test_time_series_prediction(self, ceuci_agent, agent_context):
        """Test time series prediction method."""
        data = {
            "horizon": 12,
            "data": [{"month": i, "value": 100 + i * 10} for i in range(24)],
        }

        result = await ceuci_agent._time_series_prediction(data, agent_context)

        assert "prediction" in result
        assert "forecast_values" in result
        assert "confidence" in result
        assert "model_used" in result
        assert result["horizon"] == 12

    @pytest.mark.asyncio
    async def test_anomaly_forecast(self, ceuci_agent, agent_context):
        """Test anomaly forecasting method."""
        data = {"data": [{"value": 100 + i * 5} for i in range(30)]}

        result = await ceuci_agent._anomaly_forecast(data, agent_context)

        assert "anomaly_probability" in result
        assert "risk_level" in result
        assert "confidence" in result
        assert result["model_used"] == "Isolation Forest"

    @pytest.mark.asyncio
    async def test_trend_analysis(self, ceuci_agent, agent_context):
        """Test trend analysis method."""
        data = {"data": [{"month": i, "value": 1000 + i * 100} for i in range(12)]}

        result = await ceuci_agent._trend_analysis(data, agent_context)

        assert "trend_direction" in result
        assert "trend_strength" in result
        assert "confidence" in result
        assert result["model_used"] == "Linear Regression"


# ============================================================================
# PUBLIC METHODS TESTS (High Coverage Priority)
# ============================================================================


@pytest.mark.unit
class TestCeuciPublicMethods:
    """Test public API methods for comprehensive coverage."""

    @pytest.mark.asyncio
    async def test_initialize(self, ceuci_agent):
        """Test agent initialization."""
        await ceuci_agent.initialize()
        # Agent should be ready after initialization
        assert ceuci_agent is not None

    @pytest.mark.asyncio
    async def test_predict_time_series(self, ceuci_agent):
        """Test time series prediction public method."""
        data = {"month": list(range(24)), "value": [100 + i * 10 for i in range(24)]}
        result = await ceuci_agent.predict_time_series(data, horizon=6)

        assert result is not None
        assert "forecast" in result or "prediction" in result or "values" in result

    @pytest.mark.asyncio
    async def test_analyze_trends(self, ceuci_agent):
        """Test trend analysis public method."""
        data = [{"month": i, "value": 1000 + i * 50} for i in range(12)]
        result = await ceuci_agent.analyze_trends(data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_detect_seasonal_patterns(self, ceuci_agent):
        """Test seasonal pattern detection public method."""
        # Create data with monthly pattern
        data = [100 + 20 * (i % 12) for i in range(36)]
        result = await ceuci_agent.detect_seasonal_patterns(data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_forecast_anomalies(self, ceuci_agent):
        """Test anomaly forecasting public method."""
        historical_data = [100] * 20  # Stable historical data
        future_predictions = [100, 101, 99, 300, 98]  # One anomaly

        result = await ceuci_agent.forecast_anomalies(
            historical_data, future_predictions
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_compare_models(self, ceuci_agent):
        """Test model comparison public method."""
        data = {"values": [100 + i * 5 for i in range(50)]}
        models = ["arima", "linear_regression"]

        result = await ceuci_agent.compare_models(data, models)

        assert result is not None

    @pytest.mark.asyncio
    async def test_process_message(self, ceuci_agent, agent_context):
        """Test message processing public method."""
        payload = {
            "action": "predict",
            "data": {"values": [1, 2, 3, 4, 5]},
            "horizon": 3,
        }

        result = await ceuci_agent.process_message(payload, agent_context)

        assert result is not None

    @pytest.mark.asyncio
    async def test_shutdown(self, ceuci_agent):
        """Test agent shutdown."""
        await ceuci_agent.shutdown()
        # Should complete without errors
        assert True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciIntegration:
    """Integration tests for Céuci agent."""

    @pytest.mark.asyncio
    async def test_complete_prediction_workflow(
        self, ceuci_agent, agent_context, sample_contracts_data
    ):
        """Test complete prediction workflow."""
        message = AgentMessage(
            sender="abaporu",
            recipient="Ceuci",
            action="predict",
            payload={
                "prediction_type": "time_series",
                "horizon": 3,
                "data": sample_contracts_data,
            },
        )

        response = await ceuci_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "prediction_result" in response.result
        assert response.metadata["prediction_type"] == "time_series"

    @pytest.mark.asyncio
    async def test_multiple_sequential_predictions(self, ceuci_agent, agent_context):
        """Test multiple sequential prediction requests."""
        prediction_types = ["time_series", "anomaly_forecast", "trend_analysis"]
        responses = []

        for pred_type in prediction_types:
            message = AgentMessage(
                sender="test",
                recipient="Ceuci",
                action="predict",
                payload={
                    "prediction_type": pred_type,
                    "data": [{"value": i * 10} for i in range(20)],
                },
            )
            response = await ceuci_agent.process(message, agent_context)
            responses.append(response)

        # All should succeed
        assert all(r.status == AgentStatus.COMPLETED for r in responses)
        assert len(responses) == 3
