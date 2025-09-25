"""
Module: models.base
Description: Base model for SQLAlchemy ORM
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class BaseModel(Base):
    """
    Base model with common fields for all tables.
    
    Includes:
    - UUID primary key
    - Created/updated timestamps
    - Common methods
    """
    __abstract__ = True
    
    # Use UUID for all primary keys
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case
        name = cls.__name__
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert model to dictionary.
        
        Args:
            include_sensitive: Include sensitive fields
            
        Returns:
            Dictionary representation
        """
        # Default implementation - can be overridden
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "BaseModel":
        """
        Create instance from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Model instance
        """
        return cls(**data)