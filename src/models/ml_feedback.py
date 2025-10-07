"""
Module: models.ml_feedback
Description: ML Feedback Models - Learning from Investigation Results
Author: Anderson Henrique da Silva
Date: 2025-10-07 18:11:37
License: Proprietary - All rights reserved

These models store feedback data that can be used to train
and improve machine learning models for anomaly detection.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.db.base import Base


class FeedbackType(str, Enum):
    """Type of feedback."""
    USER_CONFIRMED = "user_confirmed"  # User confirmed the anomaly
    USER_REJECTED = "user_rejected"    # User rejected as false positive
    AUTO_VALIDATED = "auto_validated"  # System validated through external data
    EXPERT_REVIEW = "expert_review"    # Expert reviewed and confirmed


class AnomalyLabel(str, Enum):
    """Ground truth labels for ML training."""
    TRUE_POSITIVE = "true_positive"    # Correctly identified anomaly
    FALSE_POSITIVE = "false_positive"  # Incorrectly flagged as anomaly
    FALSE_NEGATIVE = "false_negative"  # Missed anomaly
    UNCERTAIN = "uncertain"            # Unclear/needs more review


class InvestigationFeedback(Base):
    """
    Feedback on investigation results for ML training.

    This table stores ground truth data that can be used to:
    - Train supervised ML models
    - Evaluate model performance
    - Identify model weaknesses
    - Improve anomaly detection thresholds
    """

    __tablename__ = "investigation_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    anomaly_id = Column(String(255), nullable=True, index=True)

    # Feedback details
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    anomaly_label = Column(SQLEnum(AnomalyLabel), nullable=False)

    # Contract and detection details
    contract_id = Column(String(255), nullable=True, index=True)
    anomaly_type = Column(String(100), nullable=False, index=True)
    detected_severity = Column(Float, nullable=False)
    detected_confidence = Column(Float, nullable=False)

    # Ground truth
    actual_severity = Column(Float, nullable=True)  # Corrected severity
    corrected_type = Column(String(100), nullable=True)  # Corrected anomaly type

    # Features used for detection (for retraining)
    features = Column(JSON, nullable=False)  # Feature vector used

    # Additional context
    feedback_notes = Column(String(1000), nullable=True)
    evidence_urls = Column(JSON, nullable=True)  # Supporting evidence

    # Attribution
    feedback_by = Column(String(255), nullable=True)  # User ID or system
    reviewed_by = Column(String(255), nullable=True)  # Expert reviewer

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Model version that made the prediction
    model_version = Column(String(50), nullable=True)
    detection_threshold = Column(Float, nullable=True)

    def __repr__(self):
        return f"<InvestigationFeedback {self.id} - {self.anomaly_label}>"


class MLTrainingDataset(Base):
    """
    Curated datasets for ML model training.

    Aggregates feedback data into training-ready datasets with
    proper train/val/test splits and balanced classes.
    """

    __tablename__ = "ml_training_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # Dataset composition
    anomaly_types = Column(JSON, nullable=False)  # Types included
    total_samples = Column(Integer, nullable=False)
    positive_samples = Column(Integer, nullable=False)
    negative_samples = Column(Integer, nullable=False)

    # Data splits
    train_size = Column(Integer, nullable=False)
    val_size = Column(Integer, nullable=False)
    test_size = Column(Integer, nullable=False)

    # Quality metrics
    label_confidence_avg = Column(Float, nullable=True)
    data_quality_score = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(255), nullable=True)

    # Storage
    storage_path = Column(String(500), nullable=True)  # Path to serialized dataset
    format = Column(String(50), nullable=False, default="pytorch")

    def __repr__(self):
        return f"<MLTrainingDataset {self.name} - {self.total_samples} samples>"


class MLModelVersion(Base):
    """
    Trained ML model versions with performance tracking.

    Tracks different versions of trained models with their
    performance metrics and deployment status.
    """

    __tablename__ = "ml_model_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)

    # Model details
    model_type = Column(String(100), nullable=False)
    architecture = Column(String(255), nullable=True)
    hyperparameters = Column(JSON, nullable=True)

    # Training info
    training_dataset_id = Column(UUID(as_uuid=True), ForeignKey("ml_training_datasets.id"))
    trained_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    training_duration_seconds = Column(Float, nullable=True)

    # Performance metrics
    train_accuracy = Column(Float, nullable=True)
    val_accuracy = Column(Float, nullable=True)
    test_accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    auc_roc = Column(Float, nullable=True)

    # Additional metrics
    false_positive_rate = Column(Float, nullable=True)
    false_negative_rate = Column(Float, nullable=True)
    inference_time_ms = Column(Float, nullable=True)

    # Deployment
    is_deployed = Column(Integer, nullable=False, default=0)  # Boolean
    deployed_at = Column(DateTime, nullable=True)
    deployment_environment = Column(String(50), nullable=True)

    # Storage
    model_path = Column(String(500), nullable=True)
    model_size_mb = Column(Float, nullable=True)

    # Metadata
    created_by = Column(String(255), nullable=True)
    notes = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<MLModelVersion {self.model_name} v{self.version}>"
