"""Unit tests for anomaly detection components."""

import numpy as np
import pandas as pd
import pytest

from src.ml.anomaly_detector import (
    AnomalyResult,
    AnomalyType,
    EnsembleAnomalyDetector,
    MLAnomalyDetector,
    StatisticalAnomalyDetector,
)
from src.ml.pattern_analyzer import PatternAnalyzer, PatternType
from src.ml.spectral_analyzer import SpectralAnalyzer, SpectralResult


class TestAnomalyResult:
    """Test AnomalyResult data structure."""

    def test_anomaly_result_creation(self):
        """Test creating anomaly result."""
        result = AnomalyResult(
            is_anomaly=True,
            score=0.85,
            type=AnomalyType.STATISTICAL,
            description="Price significantly above average",
            evidence={"z_score": 3.2, "mean": 100000, "value": 250000},
            severity="high",
        )

        assert result.is_anomaly is True
        assert result.score == 0.85
        assert result.type == AnomalyType.STATISTICAL
        assert result.severity == "high"
        assert "z_score" in result.evidence

    def test_anomaly_result_to_dict(self):
        """Test converting anomaly result to dictionary."""
        result = AnomalyResult(
            is_anomaly=True,
            score=0.75,
            type=AnomalyType.PATTERN,
            description="Unusual temporal pattern detected",
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["is_anomaly"] is True
        assert result_dict["score"] == 0.75
        assert result_dict["type"] == "pattern"


class TestStatisticalAnomalyDetector:
    """Test statistical anomaly detection methods."""

    @pytest.fixture
    def detector(self):
        """Create statistical detector instance."""
        return StatisticalAnomalyDetector(z_score_threshold=2.5)

    def test_z_score_detection_normal(self, detector):
        """Test Z-score detection with normal values."""
        # Generate normal data
        np.random.seed(42)
        values = np.random.normal(100, 20, 100).tolist()

        # Test with a normal value
        result = detector.detect_z_score(values, 105)

        assert result.is_anomaly is False
        assert result.score < 0.5
        assert result.type == AnomalyType.STATISTICAL

    def test_z_score_detection_anomaly(self, detector):
        """Test Z-score detection with anomalous value."""
        # Generate normal data
        np.random.seed(42)
        values = np.random.normal(100, 20, 100).tolist()

        # Test with an extreme value
        result = detector.detect_z_score(values, 200)

        assert result.is_anomaly is True
        assert result.score > 0.7
        assert "z_score" in result.evidence
        assert result.evidence["z_score"] > 2.5

    def test_iqr_detection(self, detector):
        """Test IQR-based outlier detection."""
        # Create data with outliers
        values = list(range(1, 101))  # 1 to 100
        outlier = 200

        result = detector.detect_iqr_outlier(values, outlier)

        assert result.is_anomaly is True
        assert result.score > 0.8
        assert "iqr" in result.evidence
        assert "q1" in result.evidence
        assert "q3" in result.evidence

    def test_modified_z_score_detection(self, detector):
        """Test Modified Z-score (MAD-based) detection."""
        # Generate data with outliers
        values = [10, 12, 13, 11, 14, 12, 11, 13, 200]  # 200 is outlier

        result = detector.detect_modified_z_score(values[:-1], 200)

        assert result.is_anomaly is True
        assert result.score > 0.8
        assert "mad_z_score" in result.evidence

    def test_insufficient_data(self, detector):
        """Test handling of insufficient data."""
        # Too few values
        values = [100, 110]

        result = detector.detect_z_score(values, 120)

        assert result.is_anomaly is False
        assert "Insufficient data" in result.description


class TestMLAnomalyDetector:
    """Test machine learning anomaly detection."""

    @pytest.fixture
    def detector(self):
        """Create ML detector instance."""
        return MLAnomalyDetector()

    @pytest.fixture
    def sample_data(self):
        """Create sample contract data."""
        np.random.seed(42)
        n_samples = 100

        # Normal contracts
        normal_data = pd.DataFrame(
            {
                "value": np.random.normal(100000, 20000, n_samples),
                "duration_days": np.random.normal(180, 30, n_samples),
                "n_items": np.random.poisson(10, n_samples),
                "supplier_history": np.random.randint(1, 20, n_samples),
            }
        )

        # Add some anomalies
        anomalies = pd.DataFrame(
            {
                "value": [500000, 1000, 300000],  # Too high/low
                "duration_days": [10, 500, 365],  # Too short/long
                "n_items": [100, 1, 50],  # Too many/few
                "supplier_history": [0, 0, 1],  # New suppliers
            }
        )

        return pd.concat([normal_data, anomalies], ignore_index=True)

    def test_isolation_forest_detection(self, detector, sample_data):
        """Test Isolation Forest anomaly detection."""
        # Train on normal data
        normal_data = sample_data.iloc[:90]
        detector.fit_isolation_forest(normal_data)

        # Test on anomalies
        anomaly_data = sample_data.iloc[-3:]
        results = detector.detect_isolation_forest(anomaly_data)

        assert len(results) == 3
        assert sum(r.is_anomaly for r in results) >= 2  # At least 2 anomalies
        assert all(r.type == AnomalyType.ML for r in results)

    def test_clustering_anomaly_detection(self, detector, sample_data):
        """Test clustering-based anomaly detection."""
        # Fit clustering model
        detector.fit_clustering(sample_data)

        # Test on extreme outlier
        outlier = pd.DataFrame(
            {
                "value": [10000000],  # 100x normal
                "duration_days": [1],
                "n_items": [1000],
                "supplier_history": [0],
            }
        )

        results = detector.detect_clustering_anomaly(outlier)

        assert len(results) == 1
        assert results[0].is_anomaly is True
        assert results[0].score > 0.8

    def test_autoencoder_detection(self, detector, sample_data):
        """Test autoencoder-based anomaly detection."""
        # Train autoencoder
        normal_data = sample_data.iloc[:80]
        detector.fit_autoencoder(normal_data, epochs=5)  # Few epochs for testing

        # Test on normal and anomalous data
        test_data = sample_data.iloc[80:]
        results = detector.detect_autoencoder_anomaly(test_data)

        assert len(results) == len(test_data)
        # Should detect some anomalies
        anomaly_count = sum(r.is_anomaly for r in results)
        assert anomaly_count > 0


class TestSpectralAnalyzer:
    """Test spectral analysis for anomaly detection."""

    @pytest.fixture
    def analyzer(self):
        """Create spectral analyzer instance."""
        return SpectralAnalyzer()

    @pytest.fixture
    def periodic_signal(self):
        """Create periodic signal with anomalies."""
        # Daily data for 365 days
        days = np.arange(365)

        # Normal pattern: weekly and monthly cycles
        weekly = 10 * np.sin(2 * np.pi * days / 7)
        monthly = 20 * np.sin(2 * np.pi * days / 30)
        noise = np.random.normal(0, 5, 365)

        signal = 100 + weekly + monthly + noise

        # Add anomalies (sudden spikes)
        signal[100] += 50  # Day 100
        signal[200] += 70  # Day 200
        signal[300] -= 60  # Day 300

        return days, signal

    def test_fft_analysis(self, analyzer, periodic_signal):
        """Test FFT-based spectral analysis."""
        days, signal = periodic_signal

        result = analyzer.analyze_spectrum(signal, sampling_rate=1.0)  # 1 sample/day

        assert isinstance(result, SpectralResult)
        assert result.dominant_frequencies is not None
        assert len(result.dominant_frequencies) > 0

        # Should detect weekly frequency (~0.14 Hz = 1/7 days)
        weekly_freq = 1 / 7
        assert any(abs(f - weekly_freq) < 0.01 for f in result.dominant_frequencies)

    def test_spectral_anomaly_detection(self, analyzer, periodic_signal):
        """Test spectral anomaly detection."""
        days, signal = periodic_signal

        # Analyze normal portion
        normal_result = analyzer.analyze_spectrum(signal[:90])

        # Analyze anomalous portion
        anomaly_result = analyzer.analyze_spectrum(signal[95:105])

        # Spectral entropy should be higher in anomalous region
        assert anomaly_result.spectral_entropy > normal_result.spectral_entropy

    def test_periodogram_analysis(self, analyzer):
        """Test periodogram computation."""
        # Create simple sinusoidal signal
        t = np.linspace(0, 10, 1000)
        frequency = 2.5  # Hz
        signal = np.sin(2 * np.pi * frequency * t)

        result = analyzer.compute_periodogram(signal, sampling_rate=100)

        assert "frequencies" in result
        assert "power" in result

        # Peak should be at the signal frequency
        peak_idx = np.argmax(result["power"])
        peak_freq = result["frequencies"][peak_idx]
        assert abs(peak_freq - frequency) < 0.1

    def test_wavelet_analysis(self, analyzer):
        """Test wavelet transform analysis."""
        # Create signal with time-varying frequency
        t = np.linspace(0, 1, 1000)
        chirp = np.sin(2 * np.pi * (10 * t + 5 * t**2))

        result = analyzer.wavelet_analysis(chirp)

        assert "scales" in result
        assert "coefficients" in result
        assert result["coefficients"].shape[0] == len(result["scales"])


class TestPatternAnalyzer:
    """Test pattern analysis for anomaly detection."""

    @pytest.fixture
    def analyzer(self):
        """Create pattern analyzer instance."""
        return PatternAnalyzer()

    @pytest.fixture
    def time_series_data(self):
        """Create time series data with patterns."""
        dates = pd.date_range(start="2023-01-01", periods=365, freq="D")

        # Base trend
        trend = np.linspace(100, 150, 365)

        # Seasonal pattern
        seasonal = 20 * np.sin(2 * np.pi * np.arange(365) / 365)

        # Weekly pattern
        weekly = 10 * np.sin(2 * np.pi * np.arange(365) / 7)

        # Random noise
        noise = np.random.normal(0, 5, 365)

        values = trend + seasonal + weekly + noise

        return pd.DataFrame({"date": dates, "value": values})

    def test_temporal_pattern_detection(self, analyzer, time_series_data):
        """Test temporal pattern detection."""
        patterns = analyzer.detect_temporal_patterns(time_series_data)

        assert len(patterns) > 0

        # Should detect trend
        trend_patterns = [p for p in patterns if p.type == PatternType.TREND]
        assert len(trend_patterns) > 0

        # Should detect seasonality
        seasonal_patterns = [p for p in patterns if p.type == PatternType.SEASONAL]
        assert len(seasonal_patterns) > 0

    def test_clustering_pattern_detection(self, analyzer):
        """Test clustering pattern detection."""
        # Create data with clear clusters
        np.random.seed(42)

        # Three clusters
        cluster1 = np.random.normal([0, 0], 0.5, (50, 2))
        cluster2 = np.random.normal([5, 5], 0.5, (50, 2))
        cluster3 = np.random.normal([10, 0], 0.5, (50, 2))

        data = pd.DataFrame(
            np.vstack([cluster1, cluster2, cluster3]), columns=["feature1", "feature2"]
        )

        patterns = analyzer.detect_clustering_patterns(data)

        assert len(patterns) > 0
        cluster_patterns = [p for p in patterns if p.type == PatternType.CLUSTER]
        assert len(cluster_patterns) == 3  # Three clusters

    def test_correlation_pattern_detection(self, analyzer):
        """Test correlation pattern detection."""
        # Create correlated data
        np.random.seed(42)
        n = 100

        x = np.random.normal(0, 1, n)
        data = pd.DataFrame(
            {
                "feature1": x,
                "feature2": 2 * x + np.random.normal(0, 0.1, n),  # Strong positive
                "feature3": -1.5 * x + np.random.normal(0, 0.1, n),  # Strong negative
                "feature4": np.random.normal(0, 1, n),  # No correlation
            }
        )

        patterns = analyzer.detect_correlation_patterns(data)

        correlation_patterns = [
            p for p in patterns if p.type == PatternType.CORRELATION
        ]
        assert len(correlation_patterns) >= 2  # At least 2 strong correlations

        # Check correlation values
        for pattern in correlation_patterns:
            assert abs(pattern.confidence) > 0.8  # Strong correlation


class TestEnsembleAnomalyDetector:
    """Test ensemble anomaly detection."""

    @pytest.fixture
    def detector(self):
        """Create ensemble detector instance."""
        return EnsembleAnomalyDetector()

    def test_ensemble_voting(self, detector):
        """Test ensemble voting mechanism."""
        # Create mock individual results
        results = [
            AnomalyResult(is_anomaly=True, score=0.8, type=AnomalyType.STATISTICAL),
            AnomalyResult(is_anomaly=True, score=0.9, type=AnomalyType.ML),
            AnomalyResult(is_anomaly=False, score=0.3, type=AnomalyType.PATTERN),
        ]

        # Test majority voting
        ensemble_result = detector.combine_results(results, method="majority")

        assert ensemble_result.is_anomaly is True  # 2 out of 3 say anomaly
        assert ensemble_result.type == AnomalyType.ENSEMBLE

    def test_ensemble_averaging(self, detector):
        """Test ensemble score averaging."""
        results = [
            AnomalyResult(is_anomaly=True, score=0.8, type=AnomalyType.STATISTICAL),
            AnomalyResult(is_anomaly=True, score=0.9, type=AnomalyType.ML),
            AnomalyResult(is_anomaly=False, score=0.3, type=AnomalyType.PATTERN),
        ]

        # Test averaging
        ensemble_result = detector.combine_results(results, method="average")

        expected_score = (0.8 + 0.9 + 0.3) / 3
        assert abs(ensemble_result.score - expected_score) < 0.01

    def test_weighted_ensemble(self, detector):
        """Test weighted ensemble combination."""
        results = [
            AnomalyResult(is_anomaly=True, score=0.8, type=AnomalyType.STATISTICAL),
            AnomalyResult(is_anomaly=True, score=0.6, type=AnomalyType.ML),
        ]

        weights = {AnomalyType.STATISTICAL: 0.7, AnomalyType.ML: 0.3}

        ensemble_result = detector.combine_results(
            results, method="weighted", weights=weights
        )

        expected_score = 0.8 * 0.7 + 0.6 * 0.3
        assert abs(ensemble_result.score - expected_score) < 0.01
