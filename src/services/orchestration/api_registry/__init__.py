"""
API Registry

Central registry of all available government APIs.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from .registry import APICapability, APIRegistration, APIRegistry

__all__ = ["APIRegistry", "APICapability", "APIRegistration"]
