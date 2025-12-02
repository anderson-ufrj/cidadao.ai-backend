"""
ML Pipeline API Routes

This module provides API endpoints for training, versioning, and
A/B testing ML models.
"""

from typing import Any

import numpy as np
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies import get_current_user
from src.core import get_logger
from src.ml.ab_testing import TrafficAllocationStrategy, get_ab_testing
from src.ml.training_pipeline import get_training_pipeline

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/ml")


class TrainModelRequest(BaseModel):
    """Request model for training ML models."""

    model_type: str = Field(..., description="Type of model (anomaly, fraud, pattern)")
    algorithm: str = Field(..., description="Algorithm to use (isolation_forest, etc)")
    dataset_id: str | None = Field(None, description="Dataset identifier")
    hyperparameters: dict[str, Any] | None = Field(default_factory=dict)
    metadata: dict[str, Any] | None = Field(default_factory=dict)


class PromoteModelRequest(BaseModel):
    """Request model for promoting models."""

    model_id: str = Field(..., description="Model identifier")
    version: int = Field(..., description="Model version")
    status: str = Field("production", description="Target status")


class ABTestRequest(BaseModel):
    """Request model for creating A/B tests."""

    test_name: str = Field(..., description="Unique test name")
    model_a_id: str = Field(..., description="Model A identifier")
    model_a_version: int | None = Field(None, description="Model A version")
    model_b_id: str = Field(..., description="Model B identifier")
    model_b_version: int | None = Field(None, description="Model B version")
    allocation_strategy: str = Field("random", description="Allocation strategy")
    traffic_split: list[float] = Field([0.5, 0.5], description="Traffic split")
    success_metric: str = Field("f1_score", description="Success metric")
    minimum_sample_size: int = Field(1000, description="Minimum samples")
    significance_level: float = Field(0.05, description="Significance level")
    auto_stop: bool = Field(True, description="Auto stop on winner")
    duration_hours: int | None = Field(None, description="Max duration")


class RecordPredictionRequest(BaseModel):
    """Request model for recording predictions in A/B test."""

    model_selection: str = Field(..., description="model_a or model_b")
    success: bool = Field(..., description="Prediction success")
    metadata: dict[str, Any] | None = Field(default_factory=dict)


@router.post("/train", response_model=dict[str, Any])
async def train_model(
    request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """
    Train a new ML model.

    This endpoint initiates model training with the specified algorithm
    and parameters. Training runs asynchronously in the background.
    """
    try:
        pipeline = await get_training_pipeline()

        # For demo purposes, generate synthetic training data
        # In production, this would load from dataset_id
        if request.model_type == "anomaly":
            # Generate anomaly detection data
            n_samples = 1000
            n_features = 10
            X_train = np.random.randn(n_samples, n_features)
            # Add some anomalies
            anomalies = np.random.randn(50, n_features) * 3
            X_train = np.vstack([X_train, anomalies])
            y_train = None  # Unsupervised
        elif request.model_type == "fraud":
            # Generate fraud detection data
            n_samples = 1000
            n_features = 15
            X_train = np.random.randn(n_samples, n_features)
            y_train = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
        else:
            # Pattern recognition data
            n_samples = 800
            n_features = 20
            X_train = np.random.randn(n_samples, n_features)
            y_train = np.random.choice([0, 1, 2], size=n_samples)

        # Start training
        result = await pipeline.train_model(
            model_type=request.model_type,
            algorithm=request.algorithm,
            X_train=X_train,
            y_train=y_train,
            hyperparameters=request.hyperparameters,
            metadata={
                **request.metadata,
                "user_id": current_user["id"],
                "dataset_id": request.dataset_id,
            },
        )

        return result

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=list[dict[str, Any]])
async def list_models(
    model_type: str | None = None, current_user: dict = Depends(get_current_user)
):
    """List all available models with their versions."""
    try:
        pipeline = await get_training_pipeline()

        # Get models from registry
        models = []
        for model_id, registry in pipeline.model_registry.items():
            if model_type and not model_id.startswith(model_type):
                continue

            models.append(
                {
                    "model_id": model_id,
                    "versions": len(registry["versions"]),
                    "latest_version": max(
                        (v["version"] for v in registry["versions"]), default=0
                    ),
                    "created_at": registry["created_at"],
                    "production_version": next(
                        (
                            v["version"]
                            for v in registry["versions"]
                            if v.get("status") == "production"
                        ),
                        None,
                    ),
                }
            )

        return models

    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}/versions", response_model=list[dict[str, Any]])
async def list_model_versions(
    model_id: str, current_user: dict = Depends(get_current_user)
):
    """List all versions of a specific model."""
    try:
        pipeline = await get_training_pipeline()

        if model_id not in pipeline.model_registry:
            raise HTTPException(status_code=404, detail="Model not found")

        versions = []
        for version in pipeline.model_registry[model_id]["versions"]:
            versions.append(
                {
                    "version": version["version"],
                    "status": version["status"],
                    "metrics": version["metrics"],
                    "created_at": version["created_at"],
                    "promoted_at": version.get("promoted_at"),
                }
            )

        return versions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list versions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}/metrics", response_model=dict[str, Any])
async def get_model_metrics(
    model_id: str,
    version: int | None = None,
    current_user: dict = Depends(get_current_user),
):
    """Get metrics for a specific model version."""
    try:
        pipeline = await get_training_pipeline()
        metrics = await pipeline.get_model_metrics(model_id, version)

        return {
            "model_id": model_id,
            "version": version or "latest",
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/promote", response_model=dict[str, Any])
async def promote_model(
    request: PromoteModelRequest, current_user: dict = Depends(get_current_user)
):
    """Promote a model version to production."""
    try:
        pipeline = await get_training_pipeline()
        success = await pipeline.promote_model(
            request.model_id, request.version, request.status
        )

        if not success:
            raise HTTPException(status_code=500, detail="Promotion failed")

        return {
            "success": True,
            "model_id": request.model_id,
            "version": request.version,
            "status": request.status,
            "message": f"Model promoted to {request.status}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to promote model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/create", response_model=dict[str, Any])
async def create_ab_test(
    request: ABTestRequest, current_user: dict = Depends(get_current_user)
):
    """Create a new A/B test."""
    try:
        ab_framework = await get_ab_testing()

        # Validate allocation strategy
        try:
            strategy = TrafficAllocationStrategy(request.allocation_strategy)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid allocation strategy: {request.allocation_strategy}",
            )

        test_config = await ab_framework.create_test(
            test_name=request.test_name,
            model_a=(request.model_a_id, request.model_a_version),
            model_b=(request.model_b_id, request.model_b_version),
            allocation_strategy=strategy,
            traffic_split=tuple(request.traffic_split),
            success_metric=request.success_metric,
            minimum_sample_size=request.minimum_sample_size,
            significance_level=request.significance_level,
            auto_stop=request.auto_stop,
            duration_hours=request.duration_hours,
        )

        return test_config

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create A/B test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/{test_name}/start", response_model=dict[str, Any])
async def start_ab_test(test_name: str, current_user: dict = Depends(get_current_user)):
    """Start an A/B test."""
    try:
        ab_framework = await get_ab_testing()
        success = await ab_framework.start_test(test_name)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to start test")

        return {"success": True, "test_name": test_name, "message": "A/B test started"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start A/B test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/{test_name}/allocate", response_model=dict[str, Any])
async def allocate_model_for_test(test_name: str, user_id: str | None = None):
    """Get model allocation for a user in an A/B test."""
    try:
        ab_framework = await get_ab_testing()
        model_id, version = await ab_framework.allocate_model(test_name, user_id)

        return {
            "model_id": model_id,
            "version": version,
            "test_name": test_name,
            "user_id": user_id,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to allocate model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/{test_name}/record", response_model=dict[str, Any])
async def record_prediction(test_name: str, request: RecordPredictionRequest):
    """Record a prediction result for an A/B test."""
    try:
        ab_framework = await get_ab_testing()
        await ab_framework.record_prediction(
            test_name, request.model_selection, request.success, request.metadata
        )

        return {
            "success": True,
            "test_name": test_name,
            "model_selection": request.model_selection,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to record prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/{test_name}/status", response_model=dict[str, Any])
async def get_ab_test_status(
    test_name: str, current_user: dict = Depends(get_current_user)
):
    """Get current status and results of an A/B test."""
    try:
        ab_framework = await get_ab_testing()
        status = await ab_framework.get_test_status(test_name)

        # Include latest analysis if available
        if "latest_analysis" in status:
            status["analysis"] = status["latest_analysis"]

        return status

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get test status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/{test_name}/stop", response_model=dict[str, Any])
async def stop_ab_test(
    test_name: str,
    reason: str = "Manual stop",
    current_user: dict = Depends(get_current_user),
):
    """Stop an A/B test."""
    try:
        ab_framework = await get_ab_testing()
        success = await ab_framework.stop_test(test_name, reason)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to stop test")

        return {
            "success": True,
            "test_name": test_name,
            "message": f"A/B test stopped: {reason}",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to stop A/B test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/{test_name}/promote-winner", response_model=dict[str, Any])
async def promote_ab_test_winner(
    test_name: str, current_user: dict = Depends(get_current_user)
):
    """Promote the winning model from an A/B test to production."""
    try:
        ab_framework = await get_ab_testing()
        success = await ab_framework.promote_winner(test_name)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to promote winner")

        return {
            "success": True,
            "test_name": test_name,
            "message": "Winner promoted to production",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to promote winner: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/active", response_model=list[dict[str, Any]])
async def list_active_ab_tests(current_user: dict = Depends(get_current_user)):
    """List all active A/B tests."""
    try:
        ab_framework = await get_ab_testing()
        active_tests = await ab_framework.list_active_tests()

        return active_tests

    except Exception as e:
        logger.error(f"Failed to list active tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
