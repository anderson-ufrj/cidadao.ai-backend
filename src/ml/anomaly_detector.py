"""Anomaly detection for government spending data."""

from .models import MLModel


class AnomalyDetector(MLModel):
    """Detects anomalies in government spending patterns."""

    def __init__(self):
        super().__init__("anomaly_detector")
        self._thresholds = {
            "value_threshold": 1000000,  # 1M BRL
            "frequency_threshold": 10,
            "pattern_threshold": 0.8,
        }

    async def train(self, data: list[dict], **kwargs) -> dict:
        """Train anomaly detection model using Isolation Forest."""
        import numpy as np
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler

        # Extract features from data
        features = []
        for item in data:
            # Extract numerical features for anomaly detection
            feature_vector = [
                float(item.get("value", 0)),
                float(item.get("frequency", 0)),
                float(item.get("pattern_score", 0)),
                len(item.get("connections", [])),
                float(item.get("temporal_score", 0)),
            ]
            features.append(feature_vector)

        if not features:
            return {"status": "failed", "error": "No data to train"}

        # Convert to numpy array and scale
        X = np.array(features)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest model
        self.model = IsolationForest(
            n_estimators=100,
            contamination=kwargs.get("contamination", 0.1),  # 10% expected anomalies
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X_scaled)

        self._is_trained = True
        return {
            "status": "trained",
            "samples": len(data),
            "model": "IsolationForest",
            "contamination": kwargs.get("contamination", 0.1),
            "n_estimators": 100,
        }

    async def predict(self, data: list[dict]) -> list[dict]:
        """Detect anomalies in spending data."""
        anomalies = []

        for item in data:
            anomaly_score, reasons = await self._calculate_anomaly_score(item)

            if anomaly_score > 0.5:  # Threshold for anomaly
                anomalies.append(
                    {
                        "item": item,
                        "anomaly_score": anomaly_score,
                        "reasons": reasons,
                        "severity": self._get_severity(anomaly_score),
                    }
                )

        return anomalies

    async def evaluate(self, data: list[dict]) -> dict:
        """Evaluate anomaly detection performance."""
        predictions = await self.predict(data)
        return {
            "total_items": len(data),
            "anomalies_detected": len(predictions),
            "anomaly_rate": len(predictions) / len(data) if data else 0,
        }

    async def _calculate_anomaly_score(self, item: dict) -> tuple[float, list[str]]:
        """Calculate anomaly score for an item."""
        score = 0.0
        reasons = []

        # Check value anomalies
        value = item.get("valor", 0)
        if (
            isinstance(value, (int, float))
            and value > self._thresholds["value_threshold"]
        ):
            score += 0.3
            reasons.append(f"Alto valor: R$ {value:,.2f}")

        # Check frequency anomalies (simplified)
        supplier = item.get("fornecedor", {}).get("nome", "")
        if supplier and len(supplier) < 10:  # Very short supplier names
            score += 0.2
            reasons.append("Nome de fornecedor suspeito")

        # Check pattern anomalies (simplified)
        description = item.get("objeto", "").lower()
        suspicious_keywords = ["urgente", "emergencial", "dispensada"]
        if any(keyword in description for keyword in suspicious_keywords):
            score += 0.4
            reasons.append("Contratação com características suspeitas")

        return min(score, 1.0), reasons

    def _get_severity(self, score: float) -> str:
        """Get severity level based on anomaly score."""
        if score >= 0.8:
            return "high"
        if score >= 0.6:
            return "medium"
        return "low"

    def set_thresholds(self, **thresholds):
        """Update detection thresholds."""
        self._thresholds.update(thresholds)
