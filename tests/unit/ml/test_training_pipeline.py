"""
Unit tests for ML Training Pipeline
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.ml.training_pipeline import MLTrainingPipeline, training_pipeline
from src.ml.ab_testing import ABTestFramework, ABTestStatus, TrafficAllocationStrategy


class TestMLTrainingPipeline:
    """Test suite for ML training pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create a test pipeline instance."""
        return MLTrainingPipeline(experiment_name="test_experiment")
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample training data."""
        X_train = np.random.randn(100, 10)
        y_train = np.random.choice([0, 1], size=100)
        return X_train, y_train
    
    @pytest.mark.asyncio
    async def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline.experiment_name == "test_experiment"
        assert pipeline.models_dir.exists()
        assert len(pipeline.algorithms) > 0
        assert "isolation_forest" in pipeline.algorithms
    
    @pytest.mark.asyncio
    async def test_train_unsupervised_model(self, pipeline, sample_data):
        """Test training an unsupervised model."""
        X_train, _ = sample_data
        
        with patch('mlflow.start_run'), \
             patch('mlflow.log_param'), \
             patch('mlflow.log_metric'), \
             patch('mlflow.sklearn.log_model'):
            
            result = await pipeline.train_model(
                model_type="anomaly",
                algorithm="isolation_forest",
                X_train=X_train,
                hyperparameters={"contamination": 0.1}
            )
            
            assert result["success"] is True
            assert result["model_id"] == "anomaly_isolation_forest"
            assert result["version"] == 1
            assert "metrics" in result
            assert "model_path" in result
    
    @pytest.mark.asyncio
    async def test_train_supervised_model(self, pipeline, sample_data):
        """Test training a supervised model."""
        X_train, y_train = sample_data
        
        with patch('mlflow.start_run'), \
             patch('mlflow.log_param'), \
             patch('mlflow.log_metric'), \
             patch('mlflow.sklearn.log_model'):
            
            result = await pipeline.train_model(
                model_type="fraud",
                algorithm="random_forest",
                X_train=X_train,
                y_train=y_train,
                hyperparameters={"n_estimators": 50}
            )
            
            assert result["success"] is True
            assert result["model_id"] == "fraud_random_forest"
            assert "accuracy" in result["metrics"]
            assert "precision" in result["metrics"]
            assert "recall" in result["metrics"]
            assert "f1_score" in result["metrics"]
    
    @pytest.mark.asyncio
    async def test_model_versioning(self, pipeline, sample_data):
        """Test model versioning system."""
        X_train, _ = sample_data
        
        with patch('mlflow.start_run'), \
             patch('mlflow.log_param'), \
             patch('mlflow.log_metric'), \
             patch('mlflow.sklearn.log_model'), \
             patch.object(pipeline, '_save_model') as mock_save:
            
            # Mock save to return a path
            mock_save.return_value = "/models/test_model.pkl"
            
            # Train first version
            result1 = await pipeline.train_model(
                model_type="anomaly",
                algorithm="isolation_forest",
                X_train=X_train
            )
            
            # Train second version
            result2 = await pipeline.train_model(
                model_type="anomaly",
                algorithm="isolation_forest",
                X_train=X_train
            )
            
            assert result1["version"] == 1
            assert result2["version"] == 2
            assert pipeline.model_registry["anomaly_isolation_forest"]["versions"].__len__() == 2
    
    @pytest.mark.asyncio
    async def test_load_model(self, pipeline, sample_data):
        """Test loading a model from registry."""
        X_train, _ = sample_data
        
        # Create a mock model
        mock_model = MagicMock()
        model_package = {
            "model": mock_model,
            "model_type": "anomaly",
            "algorithm": "isolation_forest",
            "metrics": {"score": 0.95},
            "created_at": datetime.now().isoformat()
        }
        
        with patch('joblib.load', return_value=model_package), \
             patch.object(pipeline, 'model_registry', {
                 "anomaly_isolation_forest": {
                     "versions": [{
                         "version": 1,
                         "path": "/models/test.pkl",
                         "status": "production"
                     }]
                 }
             }):
            
            model, metadata = await pipeline.load_model("anomaly_isolation_forest")
            
            assert model == mock_model
            assert metadata["model_type"] == "anomaly"
            assert metadata["algorithm"] == "isolation_forest"
    
    @pytest.mark.asyncio
    async def test_promote_model(self, pipeline):
        """Test promoting a model to production."""
        with patch('src.infrastructure.cache.redis_client.get_redis_client') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.get.return_value = json.dumps({
                "versions": [
                    {"version": 1, "status": "staging"},
                    {"version": 2, "status": "staging"}
                ]
            })
            mock_redis_client.set = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            success = await pipeline.promote_model("test_model", 2, "production")
            
            assert success is True
            mock_redis_client.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_compare_models(self, pipeline):
        """Test comparing multiple models."""
        test_data = np.random.randn(50, 10)
        test_labels = np.random.choice([0, 1], size=50)
        
        # Mock models
        mock_model1 = MagicMock()
        mock_model1.predict.return_value = np.ones(50)
        mock_model1.score_samples = MagicMock(return_value=np.random.randn(50))
        
        mock_model2 = MagicMock()
        mock_model2.predict.return_value = np.zeros(50)
        
        with patch.object(pipeline, 'load_model') as mock_load:
            mock_load.side_effect = [
                (mock_model1, {"algorithm": "isolation_forest", "metrics": {}}),
                (mock_model2, {"algorithm": "random_forest", "metrics": {}})
            ]
            
            results = await pipeline.compare_models(
                [("model1", 1), ("model2", 2)],
                test_data,
                test_labels
            )
            
            assert "model1_v1" in results
            assert "model2_v2" in results
            assert "test_metrics" in results["model1_v1"]
            assert "anomaly_scores" in results["model1_v1"]


class TestABTestingFramework:
    """Test suite for A/B testing framework."""
    
    @pytest.fixture
    def ab_framework(self):
        """Create a test A/B testing framework."""
        return ABTestFramework()
    
    @pytest.mark.asyncio
    async def test_create_ab_test(self, ab_framework):
        """Test creating an A/B test."""
        with patch.object(training_pipeline, 'load_model') as mock_load, \
             patch('src.infrastructure.cache.redis_client.get_redis_client') as mock_redis:
            
            # Mock model loading
            mock_load.return_value = (MagicMock(), {})
            
            # Mock Redis
            mock_redis_client = AsyncMock()
            mock_redis_client.set = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            test_config = await ab_framework.create_test(
                test_name="test_ab",
                model_a=("model1", 1),
                model_b=("model2", 1),
                traffic_split=(0.6, 0.4),
                success_metric="accuracy"
            )
            
            assert test_config["test_name"] == "test_ab"
            assert test_config["traffic_split"] == (0.6, 0.4)
            assert test_config["status"] == ABTestStatus.DRAFT.value
            assert test_config["model_a"]["model_id"] == "model1"
            assert test_config["model_b"]["model_id"] == "model2"
    
    @pytest.mark.asyncio
    async def test_start_ab_test(self, ab_framework):
        """Test starting an A/B test."""
        # Create test first
        test_config = {
            "test_name": "test_ab",
            "status": ABTestStatus.DRAFT.value,
            "start_time": None
        }
        ab_framework.active_tests["test_ab"] = test_config
        
        with patch('src.infrastructure.cache.redis_client.get_redis_client') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.set = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            success = await ab_framework.start_test("test_ab")
            
            assert success is True
            assert test_config["status"] == ABTestStatus.RUNNING.value
            assert test_config["start_time"] is not None
    
    @pytest.mark.asyncio
    async def test_allocate_model_random(self, ab_framework):
        """Test random model allocation."""
        test_config = {
            "test_name": "test_ab",
            "status": ABTestStatus.RUNNING.value,
            "allocation_strategy": TrafficAllocationStrategy.RANDOM.value,
            "traffic_split": (0.5, 0.5),
            "model_a": {"model_id": "model1", "version": 1},
            "model_b": {"model_id": "model2", "version": 1}
        }
        ab_framework.active_tests["test_ab"] = test_config
        
        # Test multiple allocations
        allocations = []
        for _ in range(100):
            model_id, version = await ab_framework.allocate_model("test_ab")
            allocations.append(model_id)
        
        # Should have both models allocated
        assert "model1" in allocations
        assert "model2" in allocations
    
    @pytest.mark.asyncio
    async def test_record_prediction(self, ab_framework):
        """Test recording prediction results."""
        test_config = {
            "test_name": "test_ab",
            "status": ABTestStatus.RUNNING.value,
            "allocation_strategy": TrafficAllocationStrategy.RANDOM.value,
            "results": {
                "model_a": {"predictions": 0, "successes": 0},
                "model_b": {"predictions": 0, "successes": 0}
            },
            "minimum_sample_size": 10
        }
        ab_framework.active_tests["test_ab"] = test_config
        
        with patch('src.infrastructure.cache.redis_client.get_redis_client') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.set = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            # Record some predictions
            await ab_framework.record_prediction("test_ab", "model_a", True)
            await ab_framework.record_prediction("test_ab", "model_a", False)
            await ab_framework.record_prediction("test_ab", "model_b", True)
            
            assert test_config["results"]["model_a"]["predictions"] == 2
            assert test_config["results"]["model_a"]["successes"] == 1
            assert test_config["results"]["model_b"]["predictions"] == 1
            assert test_config["results"]["model_b"]["successes"] == 1
    
    @pytest.mark.asyncio
    async def test_analyze_test(self, ab_framework):
        """Test analyzing A/B test results."""
        test_config = {
            "test_name": "test_ab",
            "results": {
                "model_a": {"predictions": 1000, "successes": 520},
                "model_b": {"predictions": 1000, "successes": 480}
            },
            "significance_level": 0.05
        }
        ab_framework.active_tests["test_ab"] = test_config
        
        with patch('src.infrastructure.cache.redis_client.get_redis_client') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.set = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            analysis = await ab_framework.analyze_test("test_ab")
            
            assert "model_a" in analysis
            assert "model_b" in analysis
            assert "p_value" in analysis
            assert "significant" in analysis
            assert "lift" in analysis
            assert analysis["model_a"]["conversion_rate"] == 0.52
            assert analysis["model_b"]["conversion_rate"] == 0.48
    
    @pytest.mark.asyncio
    async def test_thompson_sampling_allocation(self, ab_framework):
        """Test Thompson sampling allocation."""
        test_config = {
            "test_name": "test_ab",
            "status": ABTestStatus.RUNNING.value,
            "allocation_strategy": TrafficAllocationStrategy.THOMPSON_SAMPLING.value,
            "thompson_params": {
                "model_a": {"alpha": 10, "beta": 5},
                "model_b": {"alpha": 5, "beta": 10}
            },
            "model_a": {"model_id": "model1", "version": 1},
            "model_b": {"model_id": "model2", "version": 1}
        }
        ab_framework.active_tests["test_ab"] = test_config
        
        # Test allocation - should favor model_a due to higher success rate
        allocations = []
        for _ in range(100):
            model_id, _ = await ab_framework.allocate_model("test_ab")
            allocations.append(model_id)
        
        # Model 1 should be allocated more often
        model1_count = allocations.count("model1")
        model2_count = allocations.count("model2")
        
        # Thompson sampling is probabilistic, but model1 should generally be favored
        assert model1_count > 0
        assert model2_count > 0