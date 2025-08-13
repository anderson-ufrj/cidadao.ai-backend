"""Base ML model interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np


class MLModel(ABC):
    """Abstract base class for ML models."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._is_trained = False
    
    @abstractmethod
    async def train(self, data: List[Dict], **kwargs) -> Dict:
        """Train the model."""
        pass
    
    @abstractmethod
    async def predict(self, data: List[Dict]) -> List[Dict]:
        """Make predictions."""
        pass
    
    @abstractmethod
    async def evaluate(self, data: List[Dict]) -> Dict:
        """Evaluate model performance."""
        pass
    
    def is_trained(self) -> bool:
        """Check if model is trained."""
        return self._is_trained