"""
Tests for Ceuci ML models implementation.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.agents.ceuci_ml_models import (
    HAS_PROPHET,
    ARIMAModel,
    EnsembleModel,
    LSTMModel,
    ProphetModel,
    SARIMAModel,
    get_model_by_type,
)


@pytest.fixture
def sample_time_series():
    """Generate sample time series data."""
    # Create a simple trend + seasonality + noise
    np.random.seed(42)
    t = np.arange(100)
    trend = 0.5 * t
    seasonal = 10 * np.sin(2 * np.pi * t / 12)
    noise = np.random.normal(0, 2, 100)
    return trend + seasonal + noise + 100


@pytest.fixture
def sample_dates():
    """Generate sample date range."""
    return pd.date_range(start="2023-01-01", periods=100, freq="D")


class TestARIMAModel:
    """Test ARIMA model implementation."""

    def test_arima_init(self):
        """Test ARIMA initialization."""
        model = ARIMAModel(p=2, d=1, q=1)
        assert model.p == 2
        assert model.d == 1
        assert model.q == 1
        assert not model.fitted

    def test_arima_fit(self, sample_time_series):
        """Test ARIMA fitting."""
        model = ARIMAModel(p=2, d=1, q=1)
        model.fit(sample_time_series)
        assert model.fitted
        assert model.coefficients is not None
        assert len(model.coefficients) == model.p

    def test_arima_predict(self, sample_time_series):
        """Test ARIMA prediction."""
        model = ARIMAModel(p=2, d=1, q=1)
        model.fit(sample_time_series)

        predictions = model.predict(10)
        assert len(predictions) == 10
        assert all(isinstance(p, (float, np.floating)) for p in predictions)

    def test_arima_predict_without_fit(self):
        """Test that prediction fails without fitting."""
        model = ARIMAModel()
        with pytest.raises(ValueError, match="Model must be fitted"):
            model.predict(5)


class TestSARIMAModel:
    """Test SARIMA model implementation."""

    def test_sarima_init(self):
        """Test SARIMA initialization."""
        model = SARIMAModel((1, 1, 1), (1, 1, 1, 12))
        assert model.p == 1
        assert model.d == 1
        assert model.q == 1
        assert model.s == 12
        assert not model.fitted

    def test_sarima_fit(self, sample_time_series):
        """Test SARIMA fitting."""
        model = SARIMAModel((1, 1, 1), (1, 1, 1, 12))
        model.fit(sample_time_series)
        assert model.fitted
        assert model.seasonal_pattern is not None
        assert len(model.seasonal_pattern) == model.s

    def test_sarima_predict(self, sample_time_series):
        """Test SARIMA prediction."""
        model = SARIMAModel((1, 1, 1), (1, 1, 1, 12))
        model.fit(sample_time_series)

        predictions = model.predict(24)
        assert len(predictions) == 24
        assert all(isinstance(p, (float, np.floating)) for p in predictions)

    def test_sarima_short_series(self):
        """Test SARIMA with short time series."""
        short_series = np.random.randn(20)
        model = SARIMAModel((1, 1, 1), (1, 1, 1, 12))
        model.fit(short_series)
        predictions = model.predict(5)
        assert len(predictions) == 5


class TestProphetModel:
    """Test Prophet model implementation."""

    def test_prophet_init(self):
        """Test Prophet initialization."""
        model = ProphetModel(yearly_seasonality=True, weekly_seasonality=False)
        if HAS_PROPHET:
            assert model.model is not None
        else:
            # Using fallback
            assert model.fallback_model is not None
        assert not model.fitted

    def test_prophet_fit(self, sample_time_series, sample_dates):
        """Test Prophet fitting."""
        model = ProphetModel()
        model.fit(sample_time_series, sample_dates)
        assert model.fitted
        if HAS_PROPHET:
            assert model.last_date is not None

    def test_prophet_predict(self, sample_time_series, sample_dates):
        """Test Prophet prediction."""
        model = ProphetModel()
        model.fit(sample_time_series, sample_dates)

        predictions, lower, upper = model.predict(10)
        assert len(predictions) == 10
        assert len(lower) == 10
        assert len(upper) == 10
        assert all(lower[i] <= predictions[i] <= upper[i] for i in range(10))

    def test_prophet_without_dates(self, sample_time_series):
        """Test Prophet with auto-generated dates."""
        model = ProphetModel()
        model.fit(sample_time_series)
        predictions, _, _ = model.predict(5)
        assert len(predictions) == 5


class TestLSTMModel:
    """Test LSTM model implementation."""

    def test_lstm_init(self):
        """Test LSTM initialization."""
        model = LSTMModel(hidden_size=50, num_layers=2)
        assert model.hidden_size == 50
        assert model.num_layers == 2
        assert not model.fitted

    def test_lstm_fit(self, sample_time_series):
        """Test LSTM fitting."""
        model = LSTMModel()
        model.fit(sample_time_series)
        assert model.fitted
        assert model.model is not None

    def test_lstm_predict(self, sample_time_series):
        """Test LSTM prediction."""
        model = LSTMModel()
        model.fit(sample_time_series)

        predictions = model.predict(10)
        assert len(predictions) == 10
        assert all(isinstance(p, (float, np.floating)) for p in predictions)

    def test_lstm_short_series(self):
        """Test LSTM with short time series."""
        short_series = np.random.randn(8)
        model = LSTMModel()
        model.fit(short_series)
        predictions = model.predict(3)
        assert len(predictions) == 3


class TestEnsembleModel:
    """Test ensemble model implementation."""

    def test_ensemble_init(self):
        """Test ensemble initialization."""
        model = EnsembleModel()
        assert len(model.models) == 4
        assert len(model.weights) == 4
        assert abs(np.sum(model.weights) - 1.0) < 0.001

    def test_ensemble_custom_weights(self):
        """Test ensemble with custom weights."""
        weights = [0.4, 0.3, 0.2, 0.1]
        model = EnsembleModel(weights=weights)
        assert np.allclose(model.weights, weights)

    def test_ensemble_fit(self, sample_time_series, sample_dates):
        """Test ensemble fitting."""
        model = EnsembleModel()
        model.fit(sample_time_series, sample_dates)
        assert model.fitted

    def test_ensemble_predict(self, sample_time_series, sample_dates):
        """Test ensemble prediction."""
        model = EnsembleModel()
        model.fit(sample_time_series, sample_dates)

        predictions, lower, upper = model.predict(10)
        assert len(predictions) == 10
        assert len(lower) == 10
        assert len(upper) == 10
        # Check that confidence intervals make sense
        assert all(lower[i] <= predictions[i] <= upper[i] for i in range(10))

    def test_ensemble_with_failed_models(self, sample_time_series):
        """Test ensemble handles model failures gracefully."""
        # Create ensemble with intentionally failing model
        from src.agents.ceuci_ml_models import ARIMAModel

        class FailingModel:
            def fit(self, data, dates=None):
                raise ValueError("Intentional failure")

            def predict(self, steps):
                raise ValueError("Intentional failure")

        models = [ARIMAModel(), FailingModel(), LSTMModel()]
        model = EnsembleModel(models=models)
        model.fit(sample_time_series)

        # Should still work with remaining models
        predictions, _, _ = model.predict(5)
        assert len(predictions) == 5


class TestModelFactory:
    """Test model factory function."""

    def test_get_arima_model(self):
        """Test ARIMA model creation."""
        model = get_model_by_type("arima", {"p": 3, "d": 1, "q": 2})
        assert isinstance(model, ARIMAModel)
        assert model.p == 3
        assert model.q == 2

    def test_get_sarima_model(self):
        """Test SARIMA model creation."""
        model = get_model_by_type("sarima")
        assert isinstance(model, SARIMAModel)

    def test_get_prophet_model(self):
        """Test Prophet model creation."""
        model = get_model_by_type("prophet", {"yearly_seasonality": False})
        assert isinstance(model, ProphetModel)

    def test_get_lstm_model(self):
        """Test LSTM model creation."""
        model = get_model_by_type("lstm", {"hidden_size": 100})
        assert isinstance(model, LSTMModel)
        assert model.hidden_size == 100

    def test_get_ensemble_model(self):
        """Test ensemble model creation."""
        model = get_model_by_type("ensemble")
        assert isinstance(model, EnsembleModel)

    def test_unknown_model_type(self):
        """Test fallback for unknown model type."""
        model = get_model_by_type("unknown_model")
        assert isinstance(model, ARIMAModel)  # Falls back to ARIMA


@pytest.mark.asyncio
async def test_model_predictions_reasonable(sample_time_series):
    """Test that model predictions are within reasonable bounds."""
    data_mean = np.mean(sample_time_series)
    data_std = np.std(sample_time_series)

    models = [ARIMAModel(), SARIMAModel(), LSTMModel()]

    for model in models:
        model.fit(sample_time_series)
        predictions = model.predict(10)

        # Check predictions are within reasonable range (5 std deviations)
        assert all(
            data_mean - 5 * data_std <= p <= data_mean + 5 * data_std
            for p in predictions
        ), f"Predictions out of range for {type(model).__name__}"
