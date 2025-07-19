"""
Module: ml.spectral_analyzer
Description: Spectral analysis using Fourier transforms for government transparency data
Author: Anderson H. Silva
Date: 2025-07-19
License: Proprietary - All rights reserved
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from scipy.fft import fft, fftfreq, ifft, rfft, rfftfreq
from scipy.signal import find_peaks, welch, periodogram, spectrogram
from scipy.stats import zscore
import warnings
warnings.filterwarnings('ignore')

from src.core import get_logger

logger = get_logger(__name__)


@dataclass
class SpectralFeatures:
    """Spectral characteristics of a time series."""
    
    dominant_frequencies: List[float]
    dominant_periods: List[float]
    spectral_entropy: float
    power_spectrum: np.ndarray
    frequencies: np.ndarray
    peak_frequencies: List[float]
    seasonal_components: Dict[str, float]
    anomaly_score: float
    trend_component: np.ndarray
    residual_component: np.ndarray


@dataclass
class SpectralAnomaly:
    """Spectral anomaly detection result."""
    
    timestamp: datetime
    anomaly_type: str
    severity: str  # "low", "medium", "high", "critical"
    frequency_band: Tuple[float, float]
    anomaly_score: float
    description: str
    evidence: Dict[str, Any]
    recommendations: List[str]


@dataclass
class PeriodicPattern:
    """Detected periodic pattern in spending data."""
    
    period_days: float
    frequency_hz: float
    amplitude: float
    confidence: float
    pattern_type: str  # "seasonal", "cyclical", "irregular", "suspicious"
    business_interpretation: str
    statistical_significance: float


class SpectralAnalyzer:
    """
    Advanced spectral analysis for government transparency data using Fourier transforms.
    
    Capabilities:
    - Seasonal pattern detection in public spending
    - Cyclical anomaly identification
    - Frequency-domain correlation analysis
    - Spectral anomaly detection
    - Periodic pattern classification
    - Cross-spectral analysis between entities
    """
    
    def __init__(
        self,
        sampling_frequency: float = 1.0,  # Daily sampling by default
        anomaly_threshold: float = 2.5,   # Z-score threshold for anomalies
        min_period_days: int = 7,         # Minimum period for pattern detection
        max_period_days: int = 365,       # Maximum period for pattern detection
    ):
        """
        Initialize the Spectral Analyzer.
        
        Args:
            sampling_frequency: Sampling frequency in Hz (1.0 = daily)
            anomaly_threshold: Z-score threshold for anomaly detection
            min_period_days: Minimum period in days for pattern detection
            max_period_days: Maximum period in days for pattern detection
        """
        self.fs = sampling_frequency
        self.anomaly_threshold = anomaly_threshold
        self.min_period = min_period_days
        self.max_period = max_period_days
        self.logger = logger
        
        # Pre-computed frequency bands for Brazilian government patterns
        self.frequency_bands = {
            "daily": (1/1, 1/3),           # 1-3 day cycles
            "weekly": (1/7, 1/10),         # Weekly patterns
            "biweekly": (1/14, 1/21),      # Bi-weekly patterns
            "monthly": (1/30, 1/45),       # Monthly cycles
            "quarterly": (1/90, 1/120),    # Quarterly patterns
            "semester": (1/180, 1/200),    # Semester patterns
            "annual": (1/365, 1/400),      # Annual cycles
            "suspicious": (1/2, 1/5)       # Very high frequency (potentially manipulated)
        }
    
    def analyze_time_series(
        self,
        data: pd.Series,
        timestamps: Optional[pd.DatetimeIndex] = None
    ) -> SpectralFeatures:
        """
        Perform comprehensive spectral analysis of a time series.
        
        Args:
            data: Time series data (spending amounts, contract counts, etc.)
            timestamps: Optional datetime index
            
        Returns:
            SpectralFeatures object with complete spectral characteristics
        """
        try:
            # Prepare data
            if timestamps is None:
                timestamps = pd.date_range(start='2020-01-01', periods=len(data), freq='D')
            
            # Ensure data is numeric and handle missing values
            data_clean = self._preprocess_data(data)
            
            # Compute FFT
            fft_values = rfft(data_clean)
            frequencies = rfftfreq(len(data_clean), d=1/self.fs)
            
            # Power spectrum
            power_spectrum = np.abs(fft_values) ** 2
            
            # Find dominant frequencies
            dominant_freqs, dominant_periods = self._find_dominant_frequencies(
                frequencies, power_spectrum
            )
            
            # Calculate spectral entropy
            spectral_entropy = self._calculate_spectral_entropy(power_spectrum)
            
            # Find peaks in spectrum
            peak_frequencies = self._find_peak_frequencies(frequencies, power_spectrum)
            
            # Detect seasonal components
            seasonal_components = self._detect_seasonal_components(
                frequencies, power_spectrum
            )
            
            # Decompose signal
            trend, residual = self._decompose_signal(data_clean)
            
            # Calculate anomaly score
            anomaly_score = self._calculate_spectral_anomaly_score(
                power_spectrum, frequencies
            )
            
            return SpectralFeatures(
                dominant_frequencies=dominant_freqs,
                dominant_periods=dominant_periods,
                spectral_entropy=spectral_entropy,
                power_spectrum=power_spectrum,
                frequencies=frequencies,
                peak_frequencies=peak_frequencies,
                seasonal_components=seasonal_components,
                anomaly_score=anomaly_score,
                trend_component=trend,
                residual_component=residual
            )
            
        except Exception as e:
            self.logger.error(f"Error in spectral analysis: {str(e)}")
            raise
    
    def detect_anomalies(
        self,
        data: pd.Series,
        timestamps: pd.DatetimeIndex,
        context: Optional[Dict[str, Any]] = None
    ) -> List[SpectralAnomaly]:
        """
        Detect anomalies using spectral analysis techniques.
        
        Args:
            data: Time series data
            timestamps: Datetime index
            context: Additional context (entity name, spending category, etc.)
            
        Returns:
            List of detected spectral anomalies
        """
        anomalies = []
        
        try:
            # Get spectral features
            features = self.analyze_time_series(data, timestamps)
            
            # Anomaly 1: Unusual frequency peaks
            freq_anomalies = self._detect_frequency_anomalies(features)
            anomalies.extend(freq_anomalies)
            
            # Anomaly 2: Sudden spectral changes
            spectral_change_anomalies = self._detect_spectral_changes(data, timestamps)
            anomalies.extend(spectral_change_anomalies)
            
            # Anomaly 3: Suspicious periodic patterns
            suspicious_patterns = self._detect_suspicious_patterns(features, context)
            anomalies.extend(suspicious_patterns)
            
            # Anomaly 4: High-frequency noise (potential manipulation)
            noise_anomalies = self._detect_high_frequency_noise(features)
            anomalies.extend(noise_anomalies)
            
            # Sort by severity and timestamp
            anomalies.sort(key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.severity],
                x.timestamp
            ), reverse=True)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting spectral anomalies: {str(e)}")
            return []
    
    def find_periodic_patterns(
        self,
        data: pd.Series,
        timestamps: pd.DatetimeIndex,
        entity_name: Optional[str] = None
    ) -> List[PeriodicPattern]:
        """
        Find and classify periodic patterns in spending data.
        
        Args:
            data: Time series data
            timestamps: Datetime index
            entity_name: Name of the entity being analyzed
            
        Returns:
            List of detected periodic patterns
        """
        patterns = []
        
        try:
            features = self.analyze_time_series(data, timestamps)
            
            # Analyze each frequency band
            for band_name, (min_freq, max_freq) in self.frequency_bands.items():
                pattern = self._analyze_frequency_band(
                    features, band_name, min_freq, max_freq, entity_name
                )
                if pattern:
                    patterns.append(pattern)
            
            # Sort by amplitude (strongest patterns first)
            patterns.sort(key=lambda x: x.amplitude, reverse=True)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error finding periodic patterns: {str(e)}")
            return []
    
    def cross_spectral_analysis(
        self,
        data1: pd.Series,
        data2: pd.Series,
        entity1_name: str,
        entity2_name: str,
        timestamps: Optional[pd.DatetimeIndex] = None
    ) -> Dict[str, Any]:
        """
        Perform cross-spectral analysis between two entities.
        
        Args:
            data1: First time series
            data2: Second time series  
            entity1_name: Name of first entity
            entity2_name: Name of second entity
            timestamps: Datetime index
            
        Returns:
            Cross-spectral analysis results
        """
        try:
            # Ensure same length
            min_len = min(len(data1), len(data2))
            data1_clean = self._preprocess_data(data1[:min_len])
            data2_clean = self._preprocess_data(data2[:min_len])
            
            # Cross-power spectrum
            fft1 = rfft(data1_clean)
            fft2 = rfft(data2_clean)
            cross_spectrum = fft1 * np.conj(fft2)
            
            frequencies = rfftfreq(min_len, d=1/self.fs)
            
            # Coherence
            coherence = np.abs(cross_spectrum) ** 2 / (
                (np.abs(fft1) ** 2) * (np.abs(fft2) ** 2)
            )
            
            # Phase difference
            phase_diff = np.angle(cross_spectrum)
            
            # Find highly correlated frequency bands
            high_coherence_indices = np.where(coherence > 0.7)[0]
            correlated_frequencies = frequencies[high_coherence_indices]
            correlated_periods = 1 / correlated_frequencies[correlated_frequencies > 0]
            
            # Statistical significance
            correlation_coeff = np.corrcoef(data1_clean, data2_clean)[0, 1]
            
            return {
                "entities": [entity1_name, entity2_name],
                "correlation_coefficient": correlation_coeff,
                "coherence_spectrum": coherence,
                "phase_spectrum": phase_diff,
                "frequencies": frequencies,
                "correlated_frequencies": correlated_frequencies.tolist(),
                "correlated_periods_days": correlated_periods.tolist(),
                "max_coherence": np.max(coherence),
                "mean_coherence": np.mean(coherence),
                "synchronization_score": self._calculate_synchronization_score(coherence),
                "business_interpretation": self._interpret_cross_spectral_results(
                    correlation_coeff, coherence, correlated_periods, 
                    entity1_name, entity2_name
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error in cross-spectral analysis: {str(e)}")
            return {}
    
    def _preprocess_data(self, data: pd.Series) -> np.ndarray:
        """Preprocess time series data for spectral analysis."""
        # Convert to numeric and handle missing values
        data_numeric = pd.to_numeric(data, errors='coerce')
        
        # Fill missing values with interpolation
        data_filled = data_numeric.interpolate(method='linear')
        
        # Fill remaining NaN values with median
        data_filled = data_filled.fillna(data_filled.median())
        
        # Remove trend (detrending)
        data_detrended = data_filled - data_filled.rolling(window=30, center=True).mean().fillna(data_filled.mean())
        
        # Apply window function to reduce spectral leakage
        window = np.hanning(len(data_detrended))
        data_windowed = data_detrended * window
        
        return data_windowed.values
    
    def _find_dominant_frequencies(
        self, 
        frequencies: np.ndarray, 
        power_spectrum: np.ndarray
    ) -> Tuple[List[float], List[float]]:
        """Find dominant frequencies in the power spectrum."""
        # Find peaks in power spectrum
        peaks, properties = find_peaks(
            power_spectrum, 
            height=np.mean(power_spectrum) + 2*np.std(power_spectrum),
            distance=5
        )
        
        # Get frequencies and periods for peaks
        dominant_freqs = frequencies[peaks].tolist()
        dominant_periods = [1/f if f > 0 else np.inf for f in dominant_freqs]
        
        # Sort by power (strongest first)
        peak_powers = power_spectrum[peaks]
        sorted_indices = np.argsort(peak_powers)[::-1]
        
        dominant_freqs = [dominant_freqs[i] for i in sorted_indices]
        dominant_periods = [dominant_periods[i] for i in sorted_indices]
        
        return dominant_freqs[:10], dominant_periods[:10]  # Top 10
    
    def _calculate_spectral_entropy(self, power_spectrum: np.ndarray) -> float:
        """Calculate spectral entropy as a measure of spectral complexity."""
        # Normalize power spectrum
        normalized_spectrum = power_spectrum / np.sum(power_spectrum)
        
        # Avoid log(0)
        normalized_spectrum = normalized_spectrum[normalized_spectrum > 0]
        
        # Calculate entropy
        entropy = -np.sum(normalized_spectrum * np.log2(normalized_spectrum))
        
        # Normalize by maximum possible entropy
        max_entropy = np.log2(len(normalized_spectrum))
        
        return entropy / max_entropy if max_entropy > 0 else 0
    
    def _find_peak_frequencies(
        self, 
        frequencies: np.ndarray, 
        power_spectrum: np.ndarray
    ) -> List[float]:
        """Find significant peak frequencies."""
        # Use adaptive threshold
        threshold = np.mean(power_spectrum) + np.std(power_spectrum)
        
        peaks, _ = find_peaks(power_spectrum, height=threshold)
        peak_frequencies = frequencies[peaks]
        
        # Filter by relevant frequency range
        relevant_peaks = peak_frequencies[
            (peak_frequencies >= 1/self.max_period) & 
            (peak_frequencies <= 1/self.min_period)
        ]
        
        return relevant_peaks.tolist()
    
    def _detect_seasonal_components(
        self, 
        frequencies: np.ndarray, 
        power_spectrum: np.ndarray
    ) -> Dict[str, float]:
        """Detect seasonal components in the spectrum."""
        seasonal_components = {}
        
        # Define seasonal frequencies (cycles per day)
        seasonal_freqs = {
            "weekly": 1/7,
            "monthly": 1/30,
            "quarterly": 1/91,
            "biannual": 1/182,
            "annual": 1/365
        }
        
        for component, target_freq in seasonal_freqs.items():
            # Find closest frequency in spectrum
            freq_idx = np.argmin(np.abs(frequencies - target_freq))
            
            if freq_idx < len(power_spectrum):
                # Calculate relative power in this component
                window_size = max(1, len(frequencies) // 50)
                start_idx = max(0, freq_idx - window_size//2)
                end_idx = min(len(power_spectrum), freq_idx + window_size//2)
                
                component_power = np.mean(power_spectrum[start_idx:end_idx])
                total_power = np.mean(power_spectrum)
                
                seasonal_components[component] = component_power / total_power if total_power > 0 else 0
        
        return seasonal_components
    
    def _decompose_signal(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Decompose signal into trend and residual components."""
        # Simple trend extraction using moving average
        window_size = min(30, len(data) // 4)
        trend = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        
        # Residual after removing trend
        residual = data - trend
        
        return trend, residual
    
    def _calculate_spectral_anomaly_score(
        self, 
        power_spectrum: np.ndarray, 
        frequencies: np.ndarray
    ) -> float:
        """Calculate overall anomaly score based on spectral characteristics."""
        # Factor 1: Spectral entropy (lower entropy = more anomalous)
        entropy = self._calculate_spectral_entropy(power_spectrum)
        entropy_score = 1 - entropy  # Invert so higher = more anomalous
        
        # Factor 2: High-frequency content
        high_freq_mask = frequencies > 1/self.min_period
        high_freq_power = np.sum(power_spectrum[high_freq_mask])
        total_power = np.sum(power_spectrum)
        high_freq_ratio = high_freq_power / total_power if total_power > 0 else 0
        
        # Factor 3: Peak concentration
        peak_indices, _ = find_peaks(power_spectrum)
        if len(peak_indices) > 0:
            peak_concentration = np.sum(power_spectrum[peak_indices]) / total_power
        else:
            peak_concentration = 0
        
        # Combine factors
        anomaly_score = (
            0.4 * entropy_score +
            0.3 * high_freq_ratio +
            0.3 * peak_concentration
        )
        
        return min(anomaly_score, 1.0)
    
    def _detect_frequency_anomalies(self, features: SpectralFeatures) -> List[SpectralAnomaly]:
        """Detect anomalies in frequency domain."""
        anomalies = []
        
        # Check for unusual dominant frequencies
        for freq in features.dominant_frequencies:
            if freq > 0:
                period_days = 1 / freq
                
                # Very short periods might indicate manipulation
                if period_days < 3:
                    anomalies.append(SpectralAnomaly(
                        timestamp=datetime.now(),
                        anomaly_type="high_frequency_pattern",
                        severity="high",
                        frequency_band=(freq * 0.9, freq * 1.1),
                        anomaly_score=0.8,
                        description=f"Suspicious high-frequency pattern detected (period: {period_days:.1f} days)",
                        evidence={"frequency_hz": freq, "period_days": period_days},
                        recommendations=[
                            "Investigate potential data manipulation",
                            "Check for automated/systematic processes",
                            "Verify data source integrity"
                        ]
                    ))
        
        return anomalies
    
    def _detect_spectral_changes(
        self, 
        data: pd.Series, 
        timestamps: pd.DatetimeIndex
    ) -> List[SpectralAnomaly]:
        """Detect sudden changes in spectral characteristics."""
        anomalies = []
        
        if len(data) < 60:  # Need sufficient data
            return anomalies
        
        # Split data into segments
        segment_size = len(data) // 4
        segments = [data[i:i+segment_size] for i in range(0, len(data)-segment_size, segment_size)]
        
        # Compare spectral entropy between segments
        entropies = []
        for segment in segments:
            if len(segment) > 10:
                features = self.analyze_time_series(segment)
                entropies.append(features.spectral_entropy)
        
        if len(entropies) > 1:
            entropy_changes = np.diff(entropies)
            
            # Detect significant changes
            for i, change in enumerate(entropy_changes):
                if abs(change) > 0.3:  # Significant spectral change
                    timestamp = timestamps[i * segment_size] if i * segment_size < len(timestamps) else datetime.now()
                    
                    anomalies.append(SpectralAnomaly(
                        timestamp=timestamp,
                        anomaly_type="spectral_regime_change",
                        severity="medium",
                        frequency_band=(0, 0.5),
                        anomaly_score=abs(change),
                        description=f"Significant change in spending pattern complexity detected",
                        evidence={"entropy_change": change, "segment": i},
                        recommendations=[
                            "Investigate policy or procedural changes",
                            "Check for organizational restructuring",
                            "Verify data consistency"
                        ]
                    ))
        
        return anomalies
    
    def _detect_suspicious_patterns(
        self, 
        features: SpectralFeatures, 
        context: Optional[Dict[str, Any]]
    ) -> List[SpectralAnomaly]:
        """Detect patterns that might indicate irregular activities."""
        anomalies = []
        
        # Check seasonal components for anomalies
        seasonal = features.seasonal_components
        
        # Excessive quarterly activity might indicate budget manipulation
        if seasonal.get("quarterly", 0) > 0.4:
            anomalies.append(SpectralAnomaly(
                timestamp=datetime.now(),
                anomaly_type="excessive_quarterly_pattern",
                severity="medium",
                frequency_band=(1/120, 1/60),
                anomaly_score=seasonal["quarterly"],
                description="Excessive quarterly spending pattern detected",
                evidence={"quarterly_component": seasonal["quarterly"]},
                recommendations=[
                    "Investigate budget execution practices",
                    "Check for end-of-quarter rushing",
                    "Review budget planning processes"
                ]
            ))
        
        # Very regular weekly patterns in government spending might be suspicious
        if seasonal.get("weekly", 0) > 0.3:
            anomalies.append(SpectralAnomaly(
                timestamp=datetime.now(),
                anomaly_type="unusual_weekly_regularity",
                severity="low",
                frequency_band=(1/10, 1/5),
                anomaly_score=seasonal["weekly"],
                description="Unusually regular weekly spending pattern",
                evidence={"weekly_component": seasonal["weekly"]},
                recommendations=[
                    "Verify if pattern matches business processes",
                    "Check for automated payments",
                    "Review spending authorization patterns"
                ]
            ))
        
        return anomalies
    
    def _detect_high_frequency_noise(self, features: SpectralFeatures) -> List[SpectralAnomaly]:
        """Detect high-frequency noise that might indicate data manipulation."""
        anomalies = []
        
        # Check power in high-frequency band
        high_freq_mask = features.frequencies > 0.2  # > 5 day period
        high_freq_power = np.sum(features.power_spectrum[high_freq_mask])
        total_power = np.sum(features.power_spectrum)
        
        high_freq_ratio = high_freq_power / total_power if total_power > 0 else 0
        
        if high_freq_ratio > 0.3:  # More than 30% power in high frequencies
            anomalies.append(SpectralAnomaly(
                timestamp=datetime.now(),
                anomaly_type="high_frequency_noise",
                severity="medium",
                frequency_band=(0.2, np.max(features.frequencies)),
                anomaly_score=high_freq_ratio,
                description="High-frequency noise detected in spending data",
                evidence={"high_freq_ratio": high_freq_ratio},
                recommendations=[
                    "Check data collection processes",
                    "Investigate potential data manipulation",
                    "Verify data source reliability"
                ]
            ))
        
        return anomalies
    
    def _analyze_frequency_band(
        self, 
        features: SpectralFeatures, 
        band_name: str, 
        min_freq: float, 
        max_freq: float,
        entity_name: Optional[str]
    ) -> Optional[PeriodicPattern]:
        """Analyze specific frequency band for patterns."""
        # Find frequencies in this band
        mask = (features.frequencies >= min_freq) & (features.frequencies <= max_freq)
        
        if not np.any(mask):
            return None
        
        band_power = features.power_spectrum[mask]
        band_frequencies = features.frequencies[mask]
        
        if len(band_power) == 0:
            return None
        
        # Find peak in this band
        max_idx = np.argmax(band_power)
        peak_frequency = band_frequencies[max_idx]
        peak_power = band_power[max_idx]
        
        # Calculate relative amplitude
        total_power = np.sum(features.power_spectrum)
        relative_amplitude = peak_power / total_power if total_power > 0 else 0
        
        # Skip if amplitude is too low
        if relative_amplitude < 0.05:
            return None
        
        # Calculate confidence based on peak prominence
        mean_power = np.mean(band_power)
        confidence = (peak_power - mean_power) / mean_power if mean_power > 0 else 0
        confidence = min(confidence / 3, 1.0)  # Normalize
        
        # Determine pattern type and business interpretation
        period_days = 1 / peak_frequency if peak_frequency > 0 else 0
        pattern_type = self._classify_pattern_type(band_name, period_days, relative_amplitude)
        business_interpretation = self._interpret_pattern(
            band_name, period_days, relative_amplitude, entity_name
        )
        
        return PeriodicPattern(
            period_days=period_days,
            frequency_hz=peak_frequency,
            amplitude=relative_amplitude,
            confidence=confidence,
            pattern_type=pattern_type,
            business_interpretation=business_interpretation,
            statistical_significance=confidence
        )
    
    def _classify_pattern_type(
        self, 
        band_name: str, 
        period_days: float, 
        amplitude: float
    ) -> str:
        """Classify the type of periodic pattern."""
        if band_name in ["weekly", "monthly", "quarterly", "annual"]:
            if amplitude > 0.2:
                return "seasonal"
            else:
                return "cyclical"
        elif band_name == "suspicious" or period_days < 3:
            return "suspicious"
        else:
            return "irregular"
    
    def _interpret_pattern(
        self, 
        band_name: str, 
        period_days: float, 
        amplitude: float,
        entity_name: Optional[str]
    ) -> str:
        """Provide business interpretation of detected pattern."""
        entity_str = f" for {entity_name}" if entity_name else ""
        
        interpretations = {
            "weekly": f"Weekly spending cycle detected{entity_str} (period: {period_days:.1f} days, strength: {amplitude:.1%})",
            "monthly": f"Monthly budget cycle identified{entity_str} (period: {period_days:.1f} days, strength: {amplitude:.1%})",
            "quarterly": f"Quarterly spending pattern found{entity_str} (period: {period_days:.1f} days, strength: {amplitude:.1%})",
            "annual": f"Annual budget cycle detected{entity_str} (period: {period_days:.1f} days, strength: {amplitude:.1%})",
            "suspicious": f"Potentially suspicious high-frequency pattern{entity_str} (period: {period_days:.1f} days)"
        }
        
        return interpretations.get(band_name, f"Periodic pattern detected{entity_str} (period: {period_days:.1f} days)")
    
    def _calculate_synchronization_score(self, coherence: np.ndarray) -> float:
        """Calculate synchronization score between two entities."""
        # Weight higher frequencies less (focus on meaningful business cycles)
        weights = np.exp(-np.linspace(0, 5, len(coherence)))
        weighted_coherence = coherence * weights
        
        return np.mean(weighted_coherence)
    
    def _interpret_cross_spectral_results(
        self,
        correlation: float,
        coherence: np.ndarray,
        correlated_periods: List[float],
        entity1: str,
        entity2: str
    ) -> str:
        """Interpret cross-spectral analysis results."""
        if correlation > 0.7:
            correlation_strength = "strong"
        elif correlation > 0.4:
            correlation_strength = "moderate"
        else:
            correlation_strength = "weak"
        
        interpretation = f"{correlation_strength.capitalize()} correlation detected between {entity1} and {entity2} (r={correlation:.3f}). "
        
        if len(correlated_periods) > 0:
            main_periods = [p for p in correlated_periods if 7 <= p <= 365]  # Focus on business-relevant periods
            if main_periods:
                interpretation += f"Synchronized patterns found at periods: {', '.join([f'{p:.0f} days' for p in main_periods[:3]])}."
        
        max_coherence = np.max(coherence)
        if max_coherence > 0.8:
            interpretation += " High spectral coherence suggests systematic coordination or shared external factors."
        elif max_coherence > 0.6:
            interpretation += " Moderate spectral coherence indicates some shared patterns or influences."
        
        return interpretation