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
            "No specific prediction" in response.result["prediction_result"]["message"]
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
# PREPROCESSING TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciPreprocessing:
    """Test data preprocessing methods."""

    @pytest.mark.asyncio
    async def test_preprocess_time_series(self, ceuci_agent, sample_time_series_data):
        """Test time series preprocessing."""
        result = await ceuci_agent._preprocess_time_series(sample_time_series_data)

        assert isinstance(result, pd.DataFrame)
        # Check that data was processed
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_preprocess_with_missing_values(self, ceuci_agent):
        """Test preprocessing with missing values."""
        data_with_nans = pd.DataFrame(
            {
                "date": pd.date_range(start="2024-01-01", periods=10),
                "value": [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
            }
        )

        result = await ceuci_agent._preprocess_time_series(data_with_nans)

        # Should handle missing values
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.asyncio
    async def test_preprocess_empty_data(self, ceuci_agent):
        """Test preprocessing with empty data."""
        empty_data = pd.DataFrame({"date": [], "value": []})

        result = await ceuci_agent._preprocess_time_series(empty_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


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
# MODEL TRAINING AND EVALUATION TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciModelOperations:
    """Test model training and evaluation."""

    @pytest.mark.asyncio
    async def test_train_model_linear_regression(self, ceuci_agent):
        """Test training linear regression model."""
        X = np.array([[i] for i in range(20)])
        y = np.array([2 * i + 1 for i in range(20)])

        model = await ceuci_agent._train_model(X, y, "linear_regression")

        assert model is not None
        # Model should be able to predict
        predictions = model.predict(X)
        assert len(predictions) == len(y)

    @pytest.mark.asyncio
    async def test_train_model_random_forest(self, ceuci_agent):
        """Test training random forest model."""
        X = np.array([[i, i * 2] for i in range(30)])
        y = np.array([i * 3 + 5 for i in range(30)])

        model = await ceuci_agent._train_model(X, y, "random_forest")

        assert model is not None
        predictions = model.predict(X)
        assert len(predictions) == len(y)

    @pytest.mark.asyncio
    async def test_evaluate_model_performance(self, ceuci_agent):
        """Test model performance evaluation."""
        # Create simple predictions
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.0, 2.9, 4.1, 5.0])

        metrics = await ceuci_agent._evaluate_model_performance(y_true, y_pred)

        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert metrics["mae"] < 0.5  # Good predictions
        assert metrics["r2"] > 0.9  # High R²

    @pytest.mark.asyncio
    async def test_generate_predictions(self, ceuci_agent):
        """Test prediction generation."""
        # Create a simple trained model
        X_train = np.array([[i] for i in range(20)])
        y_train = np.array([2 * i for i in range(20)])
        model = await ceuci_agent._train_model(X_train, y_train, "linear_regression")

        # Generate predictions for future
        X_future = np.array([[i] for i in range(20, 26)])
        predictions = await ceuci_agent._generate_predictions(model, X_future)

        assert len(predictions) == 6
        assert all(isinstance(p, (int, float, np.number)) for p in predictions)


# ============================================================================
# CONFIDENCE INTERVAL TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciConfidenceIntervals:
    """Test confidence interval calculations."""

    def test_calculate_confidence_intervals(self, ceuci_agent):
        """Test confidence interval calculation."""
        predictions = np.array([100, 110, 120, 130, 140])
        std_dev = 10

        intervals = ceuci_agent._calculate_confidence_intervals(
            predictions, std_dev, confidence=0.95
        )

        assert "lower_bound" in intervals
        assert "upper_bound" in intervals
        assert len(intervals["lower_bound"]) == len(predictions)
        assert len(intervals["upper_bound"]) == len(predictions)

        # Upper bound should be greater than lower bound
        for i in range(len(predictions)):
            assert intervals["upper_bound"][i] > intervals["lower_bound"][i]

    def test_confidence_intervals_different_levels(self, ceuci_agent):
        """Test different confidence levels."""
        predictions = np.array([100, 100, 100])
        std_dev = 10

        ci_95 = ceuci_agent._calculate_confidence_intervals(
            predictions, std_dev, confidence=0.95
        )
        ci_99 = ceuci_agent._calculate_confidence_intervals(
            predictions, std_dev, confidence=0.99
        )

        # 99% CI should be wider than 95% CI
        width_95 = ci_95["upper_bound"][0] - ci_95["lower_bound"][0]
        width_99 = ci_99["upper_bound"][0] - ci_99["lower_bound"][0]
        assert width_99 > width_95


# ============================================================================
# FEATURE IMPORTANCE TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciFeatureImportance:
    """Test feature importance calculation."""

    @pytest.mark.asyncio
    async def test_calculate_feature_importance(self, ceuci_agent):
        """Test feature importance calculation for random forest."""
        # Train a random forest model
        X = np.array(
            [[i, i * 2, i * 3] for i in range(50)]
        )  # 3 features, varying importance
        y = np.array(
            [i * 2 + i * 3 * 5 for i in range(50)]
        )  # Feature 2 is most important

        model = await ceuci_agent._train_model(X, y, "random_forest")
        feature_names = ["feature_1", "feature_2", "feature_3"]

        importance = await ceuci_agent._calculate_feature_importance(
            model, feature_names
        )

        assert len(importance) == 3
        assert all("name" in f and "importance" in f for f in importance)
        # All importances should sum to ~1.0
        total_importance = sum(f["importance"] for f in importance)
        assert 0.95 <= total_importance <= 1.05


# ============================================================================
# SEASONAL PATTERN TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciSeasonalPatterns:
    """Test seasonal pattern detection."""

    @pytest.mark.asyncio
    async def test_detect_seasonal_patterns(self, ceuci_agent):
        """Test seasonal pattern detection."""
        # Create data with clear seasonal pattern
        dates = pd.date_range(start="2020-01-01", periods=36, freq="M")
        # Create monthly seasonal pattern: higher in summer, lower in winter
        seasonal_component = [10 * np.sin(2 * np.pi * i / 12) for i in range(36)]
        values = [100 + s + np.random.normal(0, 2) for s in seasonal_component]

        data = pd.DataFrame({"date": dates, "value": values})

        result = await ceuci_agent._detect_seasonal_patterns(data)

        assert "seasonality_detected" in result
        assert isinstance(result["seasonality_detected"], bool)


# ============================================================================
# ANOMALY DETECTION TESTS
# ============================================================================


@pytest.mark.unit
class TestCeuciAnomalyDetection:
    """Test future anomaly detection."""

    @pytest.mark.asyncio
    async def test_detect_future_anomalies(self, ceuci_agent):
        """Test future anomaly detection."""
        # Historical data with known anomaly
        data = [100] * 20 + [500] + [100] * 10  # Spike anomaly in middle
        result = await ceuci_agent._detect_future_anomalies(data)

        assert "anomaly_probability" in result
        assert "risk_score" in result
        assert isinstance(result["anomaly_probability"], (int, float))
        assert 0 <= result["anomaly_probability"] <= 1


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
