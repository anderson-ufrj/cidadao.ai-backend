"""
Resilience Components

Circuit breakers, retry logic, and fallback strategies.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerRegistry, CircuitState

__all__ = ["CircuitBreaker", "CircuitBreakerRegistry", "CircuitState"]
