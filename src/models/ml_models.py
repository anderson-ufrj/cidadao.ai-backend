"""
Machine Learning models for the Cidadão.AI platform.

This module contains Pydantic models for ML model tracking,
versioning, and metadata management.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ModelType(str, Enum):
    """Supported ML model types."""

    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    RANDOM_FOREST = "random_forest"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    NEURAL_NETWORK = "neural_network"
    GRADIENT_BOOSTING = "gradient_boosting"


class ModelStatus(str, Enum):
    """Model lifecycle status."""

    TRAINING = "training"
    VALIDATING = "validating"
    READY = "ready"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected."""

    VALUE_OUTLIER = "value_outlier"
    PATTERN_DEVIATION = "pattern_deviation"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    RELATIONSHIP_ANOMALY = "relationship_anomaly"
    FREQUENCY_ANOMALY = "frequency_anomaly"
    COMBINED = "combined"


class ModelMetrics(BaseModel):
    """Model performance metrics."""

    accuracy: float | None = Field(None, ge=0, le=1)
    precision: float | None = Field(None, ge=0, le=1)
    recall: float | None = Field(None, ge=0, le=1)
    f1_score: float | None = Field(None, ge=0, le=1)
    roc_auc: float | None = Field(None, ge=0, le=1)
    anomaly_detection_rate: float | None = Field(None, ge=0, le=1)
    false_positive_rate: float | None = Field(None, ge=0, le=1)
    false_negative_rate: float | None = Field(None, ge=0, le=1)
    inference_time_ms: float | None = Field(None, ge=0)
    training_time_seconds: float | None = Field(None, ge=0)


class ModelParameters(BaseModel):
    """Hyperparameters for ML models."""

    # Common parameters
    random_state: int = 42
    n_jobs: int = -1

    # Isolation Forest parameters
    n_estimators: int = 100
    max_samples: str | int = "auto"
    contamination: float = Field(0.1, ge=0, le=0.5)
    max_features: float = 1.0

    # One-Class SVM parameters
    kernel: str = "rbf"
    gamma: str | float = "scale"
    nu: float = Field(0.5, ge=0, le=1)

    # Random Forest parameters
    max_depth: int | None = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1

    class Config:
        extra = "allow"  # Allow additional parameters


class TrainingData(BaseModel):
    """Training data information."""

    dataset_name: str
    dataset_version: str | None = None
    n_samples: int = Field(..., gt=0)
    n_features: int = Field(..., gt=0)
    feature_names: list[str] = []
    target_column: str | None = None
    train_test_split: float = Field(0.8, ge=0.5, le=0.95)
    validation_split: float = Field(0.2, ge=0.05, le=0.4)
    preprocessing_steps: list[str] = []
    data_hash: str | None = None


class AnomalyDetectorModel(BaseModel):
    """Main model for anomaly detection tracking."""

    # Model identification
    model_id: str | None = None
    model_name: str
    model_type: ModelType
    version: str = "1.0.0"

    # Model configuration
    parameters: ModelParameters = Field(default_factory=ModelParameters)
    feature_columns: list[str] = []
    target_types: list[AnomalyType] = [AnomalyType.COMBINED]

    # Training information
    training_data: TrainingData | None = None
    trained_at: datetime | None = None
    trained_by: str | None = None

    # Performance metrics
    metrics: ModelMetrics = Field(default_factory=ModelMetrics)
    cross_validation_scores: dict[str, list[float]] = {}

    # Model status
    status: ModelStatus = ModelStatus.TRAINING
    deployed_at: datetime | None = None
    deployment_endpoint: str | None = None

    # Model artifacts
    model_path: str | None = None
    scaler_path: str | None = None
    encoder_path: str | None = None
    mlflow_run_id: str | None = None
    mlflow_experiment_id: str | None = None

    # Additional metadata
    description: str | None = None
    tags: list[str] = []
    metadata: dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class AnomalyPrediction(BaseModel):
    """Result of an anomaly detection prediction."""

    prediction_id: str
    model_id: str
    model_version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Input data
    input_data: dict[str, Any]
    preprocessed_features: list[float] | None = None

    # Prediction results
    is_anomaly: bool
    anomaly_score: float = Field(..., ge=-1, le=1)
    anomaly_type: AnomalyType
    confidence: float = Field(..., ge=0, le=1)

    # Explanation
    explanation: str | None = None
    feature_contributions: dict[str, float] = {}
    similar_cases: list[str] = []

    # Metadata
    inference_time_ms: float
    model_used: str
    processing_metadata: dict[str, Any] = {}


class ModelComparison(BaseModel):
    """Comparison between multiple models."""

    comparison_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    models: list[AnomalyDetectorModel]

    # Comparison metrics
    best_model_id: str | None = None
    comparison_metrics: dict[str, dict[str, float]] = {}
    statistical_tests: dict[str, Any] = {}

    # Recommendations
    recommendation: str | None = None
    confidence_in_recommendation: float = Field(0.0, ge=0, le=1)


# SQLAlchemy models for database persistence
class AnomalyDetectorModelDB(Base):
    """Database model for anomaly detectors."""

    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(100), unique=True, index=True)
    model_name = Column(String(200))
    model_type = Column(String(50))
    version = Column(String(50))
    status = Column(String(50))

    # JSON columns for complex data
    parameters = Column(JSON)
    metrics = Column(JSON)
    feature_columns = Column(JSON)
    metadata = Column(JSON)

    # Timestamps
    trained_at = Column(DateTime)
    deployed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Paths and references
    model_path = Column(Text)
    mlflow_run_id = Column(String(100))
    mlflow_experiment_id = Column(String(100))


class PredictionHistoryDB(Base):
    """Database model for storing prediction history."""

    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(100), unique=True, index=True)
    model_id = Column(String(100), index=True)
    model_version = Column(String(50))

    # Prediction details
    is_anomaly = Column(Integer)  # Boolean as integer
    anomaly_score = Column(Float)
    confidence = Column(Float)
    anomaly_type = Column(String(50))

    # JSON columns
    input_data = Column(JSON)
    feature_contributions = Column(JSON)
    metadata = Column(JSON)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    inference_time_ms = Column(Float)


# Factory functions
def create_anomaly_detector_model(
    model_type: ModelType,
    model_name: str,
    parameters: dict[str, Any] | None = None,
) -> AnomalyDetectorModel:
    """Factory function to create an anomaly detector model."""
    import uuid

    model = AnomalyDetectorModel(
        model_id=str(uuid.uuid4()),
        model_name=model_name,
        model_type=model_type,
        parameters=ModelParameters(**parameters) if parameters else ModelParameters(),
        status=ModelStatus.TRAINING,
    )

    return model


def load_model_from_db(model_id: str, db_session) -> AnomalyDetectorModel | None:
    """Load a model from the database."""
    db_model = (
        db_session.query(AnomalyDetectorModelDB)
        .filter(AnomalyDetectorModelDB.model_id == model_id)
        .first()
    )

    if not db_model:
        return None

    return AnomalyDetectorModel(
        model_id=db_model.model_id,
        model_name=db_model.model_name,
        model_type=ModelType(db_model.model_type),
        version=db_model.version,
        parameters=ModelParameters(**db_model.parameters),
        metrics=(
            ModelMetrics(**db_model.metrics) if db_model.metrics else ModelMetrics()
        ),
        feature_columns=db_model.feature_columns or [],
        status=ModelStatus(db_model.status),
        trained_at=db_model.trained_at,
        deployed_at=db_model.deployed_at,
        model_path=db_model.model_path,
        mlflow_run_id=db_model.mlflow_run_id,
        mlflow_experiment_id=db_model.mlflow_experiment_id,
        metadata=db_model.metadata or {},
    )
