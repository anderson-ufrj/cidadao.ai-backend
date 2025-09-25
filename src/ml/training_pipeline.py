"""
ML Training Pipeline for Cidadão.AI

This module provides a comprehensive training pipeline for ML models
used in anomaly detection, fraud detection, and pattern recognition.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import pickle
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from src.core import get_logger, settings
from src.core.exceptions import CidadaoAIError
from src.core.cache import get_redis_client
# from src.models.ml_models import AnomalyDetectorModel  # TODO: Create this model


logger = get_logger(__name__)


class MLTrainingPipeline:
    """
    Comprehensive ML training pipeline with versioning and tracking.
    
    Features:
    - Multiple algorithm support
    - Automatic hyperparameter tuning
    - Model versioning with MLflow
    - Performance tracking
    - A/B testing support
    """
    
    def __init__(self, experiment_name: str = "cidadao_ai_models"):
        """Initialize the training pipeline."""
        self.experiment_name = experiment_name
        self.mlflow_client = None
        self.models_dir = Path(settings.get("ML_MODELS_DIR", "./models"))
        self.models_dir.mkdir(exist_ok=True)
        
        # Supported algorithms
        self.algorithms = {
            "isolation_forest": IsolationForest,
            "one_class_svm": OneClassSVM,
            "random_forest": RandomForestClassifier,
            "local_outlier_factor": LocalOutlierFactor
        }
        
        # Model registry
        self.model_registry = {}
        self._initialize_mlflow()
    
    def _initialize_mlflow(self):
        """Initialize MLflow tracking."""
        try:
            mlflow.set_tracking_uri(settings.get("MLFLOW_TRACKING_URI", "file:./mlruns"))
            mlflow.set_experiment(self.experiment_name)
            self.mlflow_client = MlflowClient()
            logger.info(f"MLflow initialized with experiment: {self.experiment_name}")
        except Exception as e:
            logger.warning(f"MLflow initialization failed: {e}. Using local tracking.")
    
    async def train_model(
        self,
        model_type: str,
        algorithm: str,
        X_train: np.ndarray,
        y_train: Optional[np.ndarray] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Train a model with the specified algorithm.
        
        Args:
            model_type: Type of model (anomaly, fraud, pattern)
            algorithm: Algorithm to use
            X_train: Training features
            y_train: Training labels (optional for unsupervised)
            hyperparameters: Model hyperparameters
            metadata: Additional metadata
            
        Returns:
            Training results with model info
        """
        try:
            logger.info(f"Starting training for {model_type} with {algorithm}")
            
            # Start MLflow run
            with mlflow.start_run(run_name=f"{model_type}_{algorithm}_{datetime.now().isoformat()}"):
                # Log parameters
                mlflow.log_param("model_type", model_type)
                mlflow.log_param("algorithm", algorithm)
                mlflow.log_param("n_samples", X_train.shape[0])
                mlflow.log_param("n_features", X_train.shape[1])
                
                if hyperparameters:
                    for key, value in hyperparameters.items():
                        mlflow.log_param(f"param_{key}", value)
                
                # Create and train model
                model = await self._create_model(algorithm, hyperparameters)
                
                # Train based on supervised/unsupervised
                if y_train is not None:
                    # Supervised training
                    X_tr, X_val, y_tr, y_val = train_test_split(
                        X_train, y_train, test_size=0.2, random_state=42
                    )
                    
                    model.fit(X_tr, y_tr)
                    
                    # Evaluate
                    y_pred = model.predict(X_val)
                    metrics = self._calculate_metrics(y_val, y_pred)
                    
                    # Cross-validation
                    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
                    metrics["cv_score_mean"] = cv_scores.mean()
                    metrics["cv_score_std"] = cv_scores.std()
                    
                else:
                    # Unsupervised training
                    model.fit(X_train)
                    
                    # Evaluate with anomaly scores
                    if hasattr(model, 'score_samples'):
                        anomaly_scores = model.score_samples(X_train)
                        metrics = {
                            "anomaly_score_mean": float(np.mean(anomaly_scores)),
                            "anomaly_score_std": float(np.std(anomaly_scores)),
                            "anomaly_score_min": float(np.min(anomaly_scores)),
                            "anomaly_score_max": float(np.max(anomaly_scores))
                        }
                    else:
                        metrics = {"training_complete": True}
                
                # Log metrics
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                # Save model
                model_path = await self._save_model(
                    model, model_type, algorithm, metrics, metadata
                )
                
                # Log model to MLflow
                mlflow.sklearn.log_model(
                    model,
                    f"{model_type}_{algorithm}",
                    registered_model_name=f"{model_type}_{algorithm}_model"
                )
                
                # Create model version
                version = await self._create_model_version(
                    model_type, algorithm, model_path, metrics
                )
                
                return {
                    "success": True,
                    "model_id": version["model_id"],
                    "version": version["version"],
                    "metrics": metrics,
                    "model_path": model_path,
                    "run_id": mlflow.active_run().info.run_id
                }
                
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model_id": None
            }
    
    async def _create_model(
        self,
        algorithm: str,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Create a model instance with hyperparameters."""
        if algorithm not in self.algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        model_class = self.algorithms[algorithm]
        
        # Default hyperparameters
        default_params = {
            "isolation_forest": {
                "contamination": 0.1,
                "random_state": 42,
                "n_estimators": 100
            },
            "one_class_svm": {
                "gamma": 0.001,
                "nu": 0.05,
                "kernel": "rbf"
            },
            "random_forest": {
                "n_estimators": 100,
                "random_state": 42,
                "max_depth": 10
            },
            "local_outlier_factor": {
                "contamination": 0.1,
                "n_neighbors": 20
            }
        }
        
        # Merge with provided hyperparameters
        params = default_params.get(algorithm, {})
        if hyperparameters:
            params.update(hyperparameters)
        
        return model_class(**params)
    
    def _calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """Calculate comprehensive metrics for model evaluation."""
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average='weighted')),
            "recall": float(recall_score(y_true, y_pred, average='weighted')),
            "f1_score": float(f1_score(y_true, y_pred, average='weighted'))
        }
        
        # Add ROC-AUC if probabilities available
        if y_proba is not None and len(np.unique(y_true)) == 2:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba[:, 1]))
        
        return metrics
    
    async def _save_model(
        self,
        model: Any,
        model_type: str,
        algorithm: str,
        metrics: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save trained model to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_type}_{algorithm}_{timestamp}.pkl"
        model_path = self.models_dir / model_filename
        
        # Create model package
        model_package = {
            "model": model,
            "model_type": model_type,
            "algorithm": algorithm,
            "metrics": metrics,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "version": timestamp
        }
        
        # Save with joblib for better compression
        joblib.dump(model_package, model_path)
        logger.info(f"Model saved to: {model_path}")
        
        return str(model_path)
    
    async def _create_model_version(
        self,
        model_type: str,
        algorithm: str,
        model_path: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a versioned model entry in the registry."""
        model_id = f"{model_type}_{algorithm}"
        
        # Get or create model entry
        if model_id not in self.model_registry:
            self.model_registry[model_id] = {
                "versions": [],
                "current_version": None,
                "created_at": datetime.now().isoformat()
            }
        
        # Add new version
        version = {
            "version": len(self.model_registry[model_id]["versions"]) + 1,
            "path": model_path,
            "metrics": metrics,
            "created_at": datetime.now().isoformat(),
            "status": "staging"  # staging, production, archived
        }
        
        self.model_registry[model_id]["versions"].append(version)
        
        # Save registry to Redis
        redis_client = await get_redis_client()
        await redis_client.set(
            f"ml_model_registry:{model_id}",
            json.dumps(self.model_registry[model_id]),
            ex=86400 * 30  # 30 days
        )
        
        return {
            "model_id": model_id,
            "version": version["version"]
        }
    
    async def load_model(
        self,
        model_id: str,
        version: Optional[int] = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Load a model from the registry.
        
        Args:
            model_id: Model identifier
            version: Specific version (latest if None)
            
        Returns:
            Tuple of (model, metadata)
        """
        # Try to load from Redis first
        redis_client = await get_redis_client()
        registry_data = await redis_client.get(f"ml_model_registry:{model_id}")
        
        if registry_data:
            registry = json.loads(registry_data)
        elif model_id in self.model_registry:
            registry = self.model_registry[model_id]
        else:
            raise ValueError(f"Model {model_id} not found in registry")
        
        # Get version
        if version is None:
            # Get latest production version or latest version
            prod_versions = [
                v for v in registry["versions"]
                if v.get("status") == "production"
            ]
            
            if prod_versions:
                version_data = max(prod_versions, key=lambda v: v["version"])
            else:
                version_data = max(registry["versions"], key=lambda v: v["version"])
        else:
            version_data = next(
                (v for v in registry["versions"] if v["version"] == version),
                None
            )
            
            if not version_data:
                raise ValueError(f"Version {version} not found for model {model_id}")
        
        # Load model
        model_package = joblib.load(version_data["path"])
        
        return model_package["model"], model_package
    
    async def promote_model(
        self,
        model_id: str,
        version: int,
        status: str = "production"
    ) -> bool:
        """
        Promote a model version to production.
        
        Args:
            model_id: Model identifier
            version: Version to promote
            status: New status (production, staging, archived)
        """
        try:
            # Load registry
            redis_client = await get_redis_client()
            registry_data = await redis_client.get(f"ml_model_registry:{model_id}")
            
            if registry_data:
                registry = json.loads(registry_data)
            else:
                registry = self.model_registry.get(model_id)
                
            if not registry:
                raise ValueError(f"Model {model_id} not found")
            
            # Update version status
            for v in registry["versions"]:
                if v["version"] == version:
                    # Archive current production if promoting to production
                    if status == "production":
                        for other_v in registry["versions"]:
                            if other_v.get("status") == "production":
                                other_v["status"] = "archived"
                    
                    v["status"] = status
                    v["promoted_at"] = datetime.now().isoformat()
                    break
            
            # Save updated registry
            self.model_registry[model_id] = registry
            await redis_client.set(
                f"ml_model_registry:{model_id}",
                json.dumps(registry),
                ex=86400 * 30
            )
            
            logger.info(f"Promoted {model_id} v{version} to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to promote model: {e}")
            return False
    
    async def get_model_metrics(
        self,
        model_id: str,
        version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get metrics for a specific model version."""
        _, metadata = await self.load_model(model_id, version)
        return metadata.get("metrics", {})
    
    async def compare_models(
        self,
        model_ids: List[Tuple[str, Optional[int]]],
        test_data: np.ndarray,
        test_labels: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple models on the same test data.
        
        Args:
            model_ids: List of (model_id, version) tuples
            test_data: Test features
            test_labels: Test labels (if available)
            
        Returns:
            Comparison results
        """
        results = {}
        
        for model_id, version in model_ids:
            try:
                model, metadata = await self.load_model(model_id, version)
                
                # Make predictions
                predictions = model.predict(test_data)
                
                result = {
                    "model_id": model_id,
                    "version": version or "latest",
                    "algorithm": metadata.get("algorithm"),
                    "training_metrics": metadata.get("metrics", {})
                }
                
                # Calculate test metrics if labels available
                if test_labels is not None:
                    test_metrics = self._calculate_metrics(test_labels, predictions)
                    result["test_metrics"] = test_metrics
                
                # Add anomaly scores for unsupervised models
                if hasattr(model, 'score_samples'):
                    scores = model.score_samples(test_data)
                    result["anomaly_scores"] = {
                        "mean": float(np.mean(scores)),
                        "std": float(np.std(scores)),
                        "percentiles": {
                            "10": float(np.percentile(scores, 10)),
                            "50": float(np.percentile(scores, 50)),
                            "90": float(np.percentile(scores, 90))
                        }
                    }
                
                results[f"{model_id}_v{version or 'latest'}"] = result
                
            except Exception as e:
                logger.error(f"Failed to evaluate {model_id}: {e}")
                results[f"{model_id}_v{version or 'latest'}"] = {
                    "error": str(e)
                }
        
        return results
    
    async def cleanup_old_models(self, days: int = 30) -> int:
        """Remove models older than specified days."""
        count = 0
        cutoff_date = datetime.now().timestamp() - (days * 86400)
        
        for model_file in self.models_dir.glob("*.pkl"):
            if model_file.stat().st_mtime < cutoff_date:
                model_file.unlink()
                count += 1
                logger.info(f"Removed old model: {model_file}")
        
        return count


# Global training pipeline instance
training_pipeline = MLTrainingPipeline()


async def get_training_pipeline() -> MLTrainingPipeline:
    """Get the global training pipeline instance."""
    return training_pipeline