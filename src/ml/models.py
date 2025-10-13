"""Base ML model interfaces."""

from abc import ABC, abstractmethod


class MLModel(ABC):
    """Abstract base class for ML models."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._is_trained = False

    @abstractmethod
    async def train(self, data: list[dict], **kwargs) -> dict:
        """Train the model."""
        pass

    @abstractmethod
    async def predict(self, data: list[dict]) -> list[dict]:
        """Make predictions."""
        pass

    @abstractmethod
    async def evaluate(self, data: list[dict]) -> dict:
        """Evaluate model performance."""
        pass

    def is_trained(self) -> bool:
        """Check if model is trained."""
        return self._is_trained
