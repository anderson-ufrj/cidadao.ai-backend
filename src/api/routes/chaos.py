"""
Chaos engineering endpoints for testing system resilience.

This module provides controlled failure injection for testing
the robustness of the Cidadão.AI system.
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.auth import get_current_user
from src.infrastructure.observability import get_structured_logger

logger = get_structured_logger(__name__, component="chaos_engineering")

router = APIRouter(prefix="/api/v1/chaos", tags=["Chaos Engineering"])


# Request models
class ChaosExperimentRequest(BaseModel):
    """Request model for chaos experiments."""

    experiment_type: str
    duration_seconds: int = 30
    intensity: float = 0.5  # 0.0 to 1.0
    target_component: Optional[str] = None
    description: str = ""


class LatencyInjectionRequest(BaseModel):
    """Request model for latency injection."""

    min_delay_ms: int = 100
    max_delay_ms: int = 2000
    probability: float = 0.1  # 0.0 to 1.0
    duration_seconds: int = 60


class ErrorInjectionRequest(BaseModel):
    """Request model for error injection."""

    error_rate: float = 0.05  # 0.0 to 1.0
    error_type: str = "HTTP_500"
    duration_seconds: int = 30


# Global chaos configuration
chaos_config = {
    "latency_injection": {
        "enabled": False,
        "min_delay": 0,
        "max_delay": 0,
        "probability": 0.0,
        "expires_at": None,
    },
    "error_injection": {
        "enabled": False,
        "error_rate": 0.0,
        "error_type": "HTTP_500",
        "expires_at": None,
    },
    "memory_pressure": {"enabled": False, "intensity": 0.0, "expires_at": None},
    "cpu_pressure": {"enabled": False, "intensity": 0.0, "expires_at": None},
}

# Statistics
chaos_stats = {
    "experiments_run": 0,
    "latency_injections": 0,
    "errors_injected": 0,
    "total_chaos_time_seconds": 0,
}


@router.get("/status", response_model=dict[str, Any])
async def get_chaos_status(current_user=Depends(get_current_user)):
    """
    Get current chaos engineering status.

    Returns:
        Current chaos configuration and statistics
    """
    # Clean up expired experiments
    now = datetime.utcnow()
    for experiment_type, config in chaos_config.items():
        if config.get("expires_at") and now > config["expires_at"]:
            config["enabled"] = False
            config["expires_at"] = None

    return {
        "timestamp": now.isoformat(),
        "active_experiments": {
            name: config
            for name, config in chaos_config.items()
            if config.get("enabled", False)
        },
        "configuration": chaos_config,
        "statistics": chaos_stats,
    }


@router.post("/inject/latency", response_model=dict[str, Any])
async def inject_latency(
    request: LatencyInjectionRequest, current_user=Depends(get_current_user)
):
    """
    Inject artificial latency into API responses.

    Args:
        request: Latency injection configuration

    Returns:
        Confirmation of latency injection activation
    """
    try:
        expires_at = datetime.utcnow() + timedelta(seconds=request.duration_seconds)

        chaos_config["latency_injection"].update(
            {
                "enabled": True,
                "min_delay": request.min_delay_ms,
                "max_delay": request.max_delay_ms,
                "probability": request.probability,
                "expires_at": expires_at,
            }
        )

        chaos_stats["experiments_run"] += 1
        chaos_stats["total_chaos_time_seconds"] += request.duration_seconds

        logger.warning(
            "Latency injection experiment started",
            operation="chaos_experiment",
            experiment_type="latency_injection",
            min_delay_ms=request.min_delay_ms,
            max_delay_ms=request.max_delay_ms,
            probability=request.probability,
            duration_seconds=request.duration_seconds,
        )

        return {
            "message": "Latency injection activated",
            "experiment_type": "latency_injection",
            "configuration": {
                "min_delay_ms": request.min_delay_ms,
                "max_delay_ms": request.max_delay_ms,
                "probability": request.probability,
                "duration_seconds": request.duration_seconds,
            },
            "expires_at": expires_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to inject latency: {e}")
        raise HTTPException(status_code=500, detail="Failed to inject latency")


@router.post("/inject/errors", response_model=dict[str, Any])
async def inject_errors(
    request: ErrorInjectionRequest, current_user=Depends(get_current_user)
):
    """
    Inject artificial errors into API responses.

    Args:
        request: Error injection configuration

    Returns:
        Confirmation of error injection activation
    """
    try:
        expires_at = datetime.utcnow() + timedelta(seconds=request.duration_seconds)

        chaos_config["error_injection"].update(
            {
                "enabled": True,
                "error_rate": request.error_rate,
                "error_type": request.error_type,
                "expires_at": expires_at,
            }
        )

        chaos_stats["experiments_run"] += 1
        chaos_stats["total_chaos_time_seconds"] += request.duration_seconds

        logger.warning(
            "Error injection experiment started",
            operation="chaos_experiment",
            experiment_type="error_injection",
            error_rate=request.error_rate,
            error_type=request.error_type,
            duration_seconds=request.duration_seconds,
        )

        return {
            "message": "Error injection activated",
            "experiment_type": "error_injection",
            "configuration": {
                "error_rate": request.error_rate,
                "error_type": request.error_type,
                "duration_seconds": request.duration_seconds,
            },
            "expires_at": expires_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to inject errors: {e}")
        raise HTTPException(status_code=500, detail="Failed to inject errors")


@router.post("/experiments/memory-pressure", response_model=dict[str, Any])
async def create_memory_pressure(
    intensity: float = Query(
        default=0.3, ge=0.1, le=0.8, description="Memory pressure intensity"
    ),
    duration_seconds: int = Query(
        default=60, ge=10, le=300, description="Duration in seconds"
    ),
    current_user=Depends(get_current_user),
):
    """
    Create memory pressure to test system behavior under resource constraints.

    Args:
        intensity: Memory pressure intensity (0.1 to 0.8)
        duration_seconds: Duration of the experiment

    Returns:
        Memory pressure experiment status
    """
    try:
        expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)

        chaos_config["memory_pressure"].update(
            {"enabled": True, "intensity": intensity, "expires_at": expires_at}
        )

        # Start background task to create memory pressure
        asyncio.create_task(_create_memory_pressure(intensity, duration_seconds))

        chaos_stats["experiments_run"] += 1
        chaos_stats["total_chaos_time_seconds"] += duration_seconds

        logger.warning(
            "Memory pressure experiment started",
            operation="chaos_experiment",
            experiment_type="memory_pressure",
            intensity=intensity,
            duration_seconds=duration_seconds,
        )

        return {
            "message": "Memory pressure experiment activated",
            "experiment_type": "memory_pressure",
            "intensity": intensity,
            "duration_seconds": duration_seconds,
            "expires_at": expires_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to create memory pressure: {e}")
        raise HTTPException(status_code=500, detail="Failed to create memory pressure")


@router.post("/experiments/cpu-pressure", response_model=dict[str, Any])
async def create_cpu_pressure(
    intensity: float = Query(
        default=0.3, ge=0.1, le=0.8, description="CPU pressure intensity"
    ),
    duration_seconds: int = Query(
        default=60, ge=10, le=300, description="Duration in seconds"
    ),
    current_user=Depends(get_current_user),
):
    """
    Create CPU pressure to test system behavior under high CPU load.

    Args:
        intensity: CPU pressure intensity (0.1 to 0.8)
        duration_seconds: Duration of the experiment

    Returns:
        CPU pressure experiment status
    """
    try:
        expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)

        chaos_config["cpu_pressure"].update(
            {"enabled": True, "intensity": intensity, "expires_at": expires_at}
        )

        # Start background task to create CPU pressure
        asyncio.create_task(_create_cpu_pressure(intensity, duration_seconds))

        chaos_stats["experiments_run"] += 1
        chaos_stats["total_chaos_time_seconds"] += duration_seconds

        logger.warning(
            "CPU pressure experiment started",
            operation="chaos_experiment",
            experiment_type="cpu_pressure",
            intensity=intensity,
            duration_seconds=duration_seconds,
        )

        return {
            "message": "CPU pressure experiment activated",
            "experiment_type": "cpu_pressure",
            "intensity": intensity,
            "duration_seconds": duration_seconds,
            "expires_at": expires_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to create CPU pressure: {e}")
        raise HTTPException(status_code=500, detail="Failed to create CPU pressure")


@router.post("/stop/{experiment_type}", response_model=dict[str, Any])
async def stop_experiment(experiment_type: str, current_user=Depends(get_current_user)):
    """
    Stop a running chaos experiment.

    Args:
        experiment_type: Type of experiment to stop

    Returns:
        Confirmation of experiment termination
    """
    try:
        if experiment_type not in chaos_config:
            raise HTTPException(
                status_code=404, detail=f"Experiment type '{experiment_type}' not found"
            )

        if not chaos_config[experiment_type].get("enabled", False):
            raise HTTPException(
                status_code=400, detail=f"Experiment '{experiment_type}' is not running"
            )

        chaos_config[experiment_type]["enabled"] = False
        chaos_config[experiment_type]["expires_at"] = None

        logger.info(
            f"Chaos experiment stopped: {experiment_type}",
            operation="chaos_experiment_stopped",
            experiment_type=experiment_type,
        )

        return {
            "message": f"Experiment '{experiment_type}' stopped",
            "experiment_type": experiment_type,
            "stopped_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop experiment {experiment_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop experiment")


@router.post("/stop-all", response_model=dict[str, Any])
async def stop_all_experiments(current_user=Depends(get_current_user)):
    """
    Stop all running chaos experiments.

    Returns:
        Summary of stopped experiments
    """
    try:
        stopped_experiments = []

        for experiment_type, config in chaos_config.items():
            if config.get("enabled", False):
                config["enabled"] = False
                config["expires_at"] = None
                stopped_experiments.append(experiment_type)

        logger.info(
            "All chaos experiments stopped",
            operation="chaos_all_experiments_stopped",
            stopped_count=len(stopped_experiments),
        )

        return {
            "message": f"Stopped {len(stopped_experiments)} experiments",
            "stopped_experiments": stopped_experiments,
            "stopped_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to stop all experiments: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop all experiments")


# Chaos injection helper functions
async def apply_chaos_latency():
    """Apply latency chaos if enabled."""
    config = chaos_config["latency_injection"]

    if not config.get("enabled", False):
        return

    if config.get("expires_at") and datetime.utcnow() > config["expires_at"]:
        config["enabled"] = False
        return

    if random.random() < config.get("probability", 0.0):
        delay_ms = random.randint(
            config.get("min_delay", 0), config.get("max_delay", 0)
        )
        await asyncio.sleep(delay_ms / 1000.0)
        chaos_stats["latency_injections"] += 1


def apply_chaos_errors():
    """Apply error chaos if enabled."""
    config = chaos_config["error_injection"]

    if not config.get("enabled", False):
        return

    if config.get("expires_at") and datetime.utcnow() > config["expires_at"]:
        config["enabled"] = False
        return

    if random.random() < config.get("error_rate", 0.0):
        chaos_stats["errors_injected"] += 1
        error_type = config.get("error_type", "HTTP_500")

        if error_type == "HTTP_500":
            raise HTTPException(status_code=500, detail="Chaos: Internal Server Error")
        elif error_type == "HTTP_503":
            raise HTTPException(status_code=503, detail="Chaos: Service Unavailable")
        elif error_type == "TIMEOUT":
            raise HTTPException(status_code=408, detail="Chaos: Request Timeout")
        else:
            raise HTTPException(status_code=500, detail=f"Chaos: {error_type}")

    return


async def _create_memory_pressure(intensity: float, duration_seconds: int):
    """Create memory pressure for the specified duration."""
    try:
        # Calculate memory allocation based on intensity
        # Allocate memory chunks to create pressure
        memory_chunks = []
        chunk_size = int(1024 * 1024 * intensity * 10)  # MB based on intensity

        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            # Allocate memory
            chunk = bytearray(chunk_size)
            memory_chunks.append(chunk)

            await asyncio.sleep(1)

            # Gradually release some memory to avoid OOM
            if len(memory_chunks) > 20:
                memory_chunks.pop(0)

        # Clean up
        memory_chunks.clear()
        chaos_config["memory_pressure"]["enabled"] = False

    except Exception as e:
        logger.error(f"Memory pressure experiment failed: {e}")
        chaos_config["memory_pressure"]["enabled"] = False


async def _create_cpu_pressure(intensity: float, duration_seconds: int):
    """Create CPU pressure for the specified duration."""
    try:
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            # Create CPU-intensive work based on intensity
            work_duration = intensity * 0.1  # Work for up to 0.1 seconds
            sleep_duration = (1 - intensity) * 0.1  # Sleep for the rest

            # CPU-intensive calculation
            work_start = time.time()
            while time.time() - work_start < work_duration:
                # Simple CPU-intensive calculation
                sum(i * i for i in range(1000))

            await asyncio.sleep(sleep_duration)

        chaos_config["cpu_pressure"]["enabled"] = False

    except Exception as e:
        logger.error(f"CPU pressure experiment failed: {e}")
        chaos_config["cpu_pressure"]["enabled"] = False
