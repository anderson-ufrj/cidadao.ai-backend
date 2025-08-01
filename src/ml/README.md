# 🧠 Cidadão.AI Machine Learning Pipeline

## 📋 Overview

The **Machine Learning Pipeline** powers the analytical core of Cidadão.AI with **advanced anomaly detection**, **pattern recognition**, and **explainable AI** capabilities. Built with **scikit-learn**, **TensorFlow**, and **statistical analysis** tools to provide transparent, interpretable insights into government data.

## 🏗️ Architecture

```
src/ml/
├── models.py                # Core ML models and algorithms
├── anomaly_detector.py      # Anomaly detection engine
├── pattern_analyzer.py      # Pattern recognition system
├── spectral_analyzer.py     # Frequency domain analysis
├── data_pipeline.py         # Data preprocessing pipeline
├── training_pipeline.py     # Model training orchestration
├── advanced_pipeline.py     # Advanced ML algorithms
├── cidadao_model.py         # Custom Cidadão.AI model
├── hf_cidadao_model.py      # HuggingFace integration
├── model_api.py            # Model serving API
├── hf_integration.py       # HuggingFace deployment
└── transparency_benchmark.py # Model evaluation benchmarks
```

## 🔬 Core ML Capabilities

### 1. **Anomaly Detection Engine** (anomaly_detector.py)

#### Statistical Anomaly Detection
```python
class AnomalyDetector:
    """
    Multi-algorithm anomaly detection for government transparency data
    
    Methods:
    - Statistical outliers (Z-score, IQR, Modified Z-score)
    - Isolation Forest for high-dimensional data
    - One-Class SVM for complex patterns
    - Local Outlier Factor for density-based detection
    - Time series anomalies with seasonal decomposition
    """
    
    # Price anomaly detection
    def detect_price_anomalies(
        self, 
        contracts: List[Contract], 
        threshold: float = 2.5
    ) -> List[PriceAnomaly]:
        """
        Detect price anomalies using statistical methods
        
        Algorithm:
        1. Group contracts by category/type
        2. Calculate mean and standard deviation
        3. Flag contracts beyond threshold * std_dev
        4. Apply contextual filters (contract size, organization type)
        """
        
    # Vendor concentration analysis
    def detect_vendor_concentration(
        self,
        contracts: List[Contract],
        concentration_threshold: float = 0.7
    ) -> List[VendorConcentrationAnomaly]:
        """
        Detect monopolistic vendor patterns
        
        Algorithm:
        1. Calculate vendor market share by organization
        2. Apply Herfindahl-Hirschman Index (HHI)
        3. Flag organizations with high vendor concentration
        4. Analyze temporal patterns for sudden changes
        """
```

#### Advanced Anomaly Types
```python
# Anomaly classification system
class AnomalyType(Enum):
    PRICE_OUTLIER = "price_outlier"               # Statistical price deviation
    VENDOR_CONCENTRATION = "vendor_concentration"  # Market concentration
    TEMPORAL_SUSPICION = "temporal_suspicion"     # Timing irregularities
    DUPLICATE_CONTRACT = "duplicate_contract"      # Contract similarity
    PAYMENT_IRREGULARITY = "payment_irregularity" # Payment pattern anomaly
    SEASONAL_DEVIATION = "seasonal_deviation"     # Seasonal pattern break
    NETWORK_ANOMALY = "network_anomaly"           # Graph-based anomalies

# Severity classification
class AnomalySeverity(Enum):
    LOW = "low"           # Minor deviations, may be normal
    MEDIUM = "medium"     # Noticeable patterns requiring attention
    HIGH = "high"         # Strong indicators of irregularities
    CRITICAL = "critical" # Severe anomalies requiring immediate action
```

### 2. **Pattern Analysis System** (pattern_analyzer.py)

#### Time Series Analysis
```python
class PatternAnalyzer:
    """
    Advanced pattern recognition for government spending patterns
    
    Capabilities:
    - Seasonal decomposition (trend, seasonal, residual)
    - Spectral analysis using FFT
    - Cross-correlation analysis between organizations
    - Regime change detection
    - Forecasting with uncertainty quantification
    """
    
    def analyze_spending_trends(
        self, 
        expenses: List[Expense],
        decomposition_model: str = "additive"
    ) -> TrendAnalysis:
        """
        Decompose spending into trend, seasonal, and irregular components
        
        Algorithm:
        1. Time series preprocessing and gap filling
        2. Seasonal-Trend decomposition using LOESS (STL)
        3. Trend change point detection
        4. Seasonal pattern stability analysis
        5. Residual anomaly identification
        """
        
    def detect_spending_regime_changes(
        self,
        time_series: np.ndarray,
        method: str = "cusum"
    ) -> List[RegimeChange]:
        """
        Detect structural breaks in spending patterns
        
        Methods:
        - CUSUM (Cumulative Sum) control charts
        - Bayesian change point detection
        - Structural break tests (Chow test, Quandt-Andrews)
        """
```

#### Cross-Organizational Analysis
```python
def analyze_cross_organizational_patterns(
    self,
    organizations: List[str],
    time_window: str = "monthly"
) -> CrossOrgAnalysis:
    """
    Identify patterns across government organizations
    
    Features:
    - Spending correlation analysis
    - Synchronized timing detection
    - Resource competition analysis
    - Coordination pattern identification
    """
    
    # Calculate cross-correlation matrix
    correlation_matrix = np.corrcoef([
        org_spending_series for org in organizations
    ])
    
    # Detect synchronized events
    synchronized_events = self._detect_synchronized_spending(
        organizations, threshold=0.8
    )
    
    return CrossOrgAnalysis(
        correlation_matrix=correlation_matrix,
        synchronized_events=synchronized_events,
        coordination_score=self._calculate_coordination_score(correlation_matrix)
    )
```

### 3. **Spectral Analysis Engine** (spectral_analyzer.py)

#### Frequency Domain Analysis
```python
class SpectralAnalyzer:
    """
    Frequency domain analysis for detecting periodic patterns
    
    Applications:
    - End-of-year spending rush detection
    - Electoral cycle influence analysis
    - Budget cycle pattern identification
    - Periodic corruption pattern detection
    """
    
    def analyze_spending_spectrum(
        self,
        spending_series: np.ndarray,
        sampling_rate: str = "monthly"
    ) -> SpectralAnalysis:
        """
        Perform FFT analysis on spending time series
        
        Algorithm:
        1. Preprocessing: detrending, windowing
        2. Fast Fourier Transform (FFT)
        3. Power spectral density estimation
        4. Peak detection in frequency domain
        5. Periodic pattern significance testing
        """
        
        # Remove trend and apply windowing
        detrended = signal.detrend(spending_series)
        windowed = detrended * signal.windows.hann(len(detrended))
        
        # FFT analysis
        frequencies = np.fft.fftfreq(len(windowed))
        fft_result = np.fft.fft(windowed)
        power_spectrum = np.abs(fft_result) ** 2
        
        # Detect significant peaks
        peaks, properties = signal.find_peaks(
            power_spectrum,
            height=np.mean(power_spectrum) + 2 * np.std(power_spectrum),
            distance=10
        )
        
        return SpectralAnalysis(
            frequencies=frequencies[peaks],
            power_spectrum=power_spectrum,
            significant_periods=1 / frequencies[peaks],
            seasonality_strength=self._calculate_seasonality_strength(power_spectrum)
        )
```

### 4. **Data Processing Pipeline** (data_pipeline.py)

#### Advanced Data Preprocessing
```python
class DataPipeline:
    """
    Comprehensive data preprocessing for ML algorithms
    
    Features:
    - Missing value imputation with multiple strategies
    - Outlier detection and treatment
    - Feature engineering for government data
    - Text preprocessing for contract descriptions
    - Temporal feature extraction
    """
    
    def preprocess_contracts(
        self, 
        contracts: List[Contract]
    ) -> ProcessedDataset:
        """
        Transform raw contract data into ML-ready features
        
        Pipeline:
        1. Data cleaning and validation
        2. Missing value imputation
        3. Categorical encoding
        4. Numerical scaling and normalization
        5. Feature engineering
        6. Dimensionality reduction if needed
        """
        
        # Extract features
        features = self._extract_contract_features(contracts)
        
        # Handle missing values
        features_imputed = self._impute_missing_values(features)
        
        # Scale numerical features
        features_scaled = self._scale_features(features_imputed)
        
        # Engineer domain-specific features
        features_engineered = self._engineer_transparency_features(features_scaled)
        
        return ProcessedDataset(
            features=features_engineered,
            feature_names=self._get_feature_names(),
            preprocessing_metadata=self._get_preprocessing_metadata()
        )
    
    def _extract_contract_features(self, contracts: List[Contract]) -> np.ndarray:
        """Extract numerical features from contract data"""
        
        features = []
        for contract in contracts:
            contract_features = [
                # Financial features
                float(contract.valor_inicial or 0),
                float(contract.valor_global or 0),
                
                # Temporal features
                self._extract_temporal_features(contract.data_assinatura),
                
                # Categorical features (encoded)
                self._encode_modality(contract.modalidade_contratacao),
                self._encode_organization(contract.orgao.codigo if contract.orgao else None),
                
                # Text features (TF-IDF of contract object)
                *self._extract_text_features(contract.objeto),
                
                # Derived features
                self._calculate_contract_duration(contract),
                self._calculate_value_per_day(contract),
                self._get_vendor_risk_score(contract.fornecedor),
            ]
            features.append(contract_features)
        
        return np.array(features)
```

### 5. **Custom Cidadão.AI Model** (cidadao_model.py)

#### Specialized Transparency Analysis Model
```python
class CidadaoAIModel:
    """
    Custom model specialized for Brazilian government transparency analysis
    
    Architecture:
    - Multi-task learning for various anomaly types
    - Attention mechanisms for important features
    - Interpretability through SHAP values
    - Uncertainty quantification
    - Brazilian government domain knowledge integration
    """
    
    def __init__(self):
        self.anomaly_detector = self._build_anomaly_detector()
        self.pattern_classifier = self._build_pattern_classifier()
        self.risk_scorer = self._build_risk_scorer()
        self.explainer = self._build_explainer()
    
    def _build_anomaly_detector(self) -> tf.keras.Model:
        """Build neural network for anomaly detection"""
        
        inputs = tf.keras.Input(shape=(self.n_features,))
        
        # Encoder
        encoded = tf.keras.layers.Dense(128, activation='relu')(inputs)
        encoded = tf.keras.layers.Dropout(0.2)(encoded)
        encoded = tf.keras.layers.Dense(64, activation='relu')(encoded)
        encoded = tf.keras.layers.Dropout(0.2)(encoded)
        encoded = tf.keras.layers.Dense(32, activation='relu')(encoded)
        
        # Decoder (autoencoder for anomaly detection)
        decoded = tf.keras.layers.Dense(64, activation='relu')(encoded)
        decoded = tf.keras.layers.Dense(128, activation='relu')(decoded)
        decoded = tf.keras.layers.Dense(self.n_features, activation='linear')(decoded)
        
        # Anomaly score output
        anomaly_score = tf.keras.layers.Dense(1, activation='sigmoid', name='anomaly_score')(encoded)
        
        model = tf.keras.Model(inputs=inputs, outputs=[decoded, anomaly_score])
        
        return model
    
    def predict_anomalies(
        self, 
        data: np.ndarray,
        return_explanations: bool = True
    ) -> AnomalyPrediction:
        """
        Predict anomalies with explanations
        
        Returns:
        - Anomaly scores (0-1)
        - Anomaly classifications
        - Feature importance (SHAP values)
        - Confidence intervals
        """
        
        # Get predictions
        reconstructed, anomaly_scores = self.anomaly_detector.predict(data)
        
        # Calculate reconstruction error
        reconstruction_error = np.mean((data - reconstructed) ** 2, axis=1)
        
        # Classify anomalies
        anomaly_labels = (anomaly_scores > self.anomaly_threshold).astype(int)
        
        # Generate explanations if requested
        explanations = None
        if return_explanations:
            explanations = self.explainer.explain_predictions(data, anomaly_scores)
        
        return AnomalyPrediction(
            anomaly_scores=anomaly_scores,
            anomaly_labels=anomaly_labels,
            reconstruction_error=reconstruction_error,
            explanations=explanations,
            confidence=self._calculate_confidence(anomaly_scores)
        )
```

### 6. **Model Interpretability** (explainer.py)

#### SHAP-based Explanations
```python
class TransparencyExplainer:
    """
    Explainable AI for transparency analysis results
    
    Methods:
    - SHAP (SHapley Additive exPlanations) values
    - LIME (Local Interpretable Model-agnostic Explanations)
    - Feature importance analysis
    - Decision boundary visualization
    """
    
    def explain_anomaly_prediction(
        self,
        model: Any,
        data: np.ndarray,
        prediction_index: int
    ) -> AnomalyExplanation:
        """
        Generate human-readable explanations for anomaly predictions
        
        Returns:
        - Feature contributions to the prediction
        - Natural language explanation
        - Visualization data for charts
        - Confidence intervals
        """
        
        # Calculate SHAP values
        explainer = shap.DeepExplainer(model, data[:100])  # Background data
        shap_values = explainer.shap_values(data[prediction_index:prediction_index+1])
        
        # Get feature names and values
        feature_names = self.get_feature_names()
        feature_values = data[prediction_index]
        
        # Sort by importance
        importance_indices = np.argsort(np.abs(shap_values[0]))[::-1]
        
        # Generate natural language explanation
        explanation_text = self._generate_explanation_text(
            shap_values[0],
            feature_names,
            feature_values,
            importance_indices[:5]  # Top 5 features
        )
        
        return AnomalyExplanation(
            shap_values=shap_values[0],
            feature_names=feature_names,
            feature_values=feature_values,
            explanation_text=explanation_text,
            top_features=importance_indices[:10]
        )
    
    def _generate_explanation_text(
        self,
        shap_values: np.ndarray,
        feature_names: List[str],
        feature_values: np.ndarray,
        top_indices: List[int]
    ) -> str:
        """Generate human-readable explanation"""
        
        explanations = []
        
        for idx in top_indices:
            feature_name = feature_names[idx]
            feature_value = feature_values[idx]
            shap_value = shap_values[idx]
            
            if shap_value > 0:
                direction = "increases"
            else:
                direction = "decreases"
                
            explanation = f"The {feature_name} value of {feature_value:.2f} {direction} the anomaly score by {abs(shap_value):.3f}"
            explanations.append(explanation)
        
        return ". ".join(explanations) + "."
```

## 📊 Model Training & Evaluation

### Training Pipeline (training_pipeline.py)

#### Automated Model Training
```python
class ModelTrainingPipeline:
    """
    Automated training pipeline for transparency analysis models
    
    Features:
    - Cross-validation with time series splits
    - Hyperparameter optimization
    - Model selection and ensemble methods
    - Performance monitoring and logging
    - Automated model deployment
    """
    
    def train_anomaly_detection_model(
        self,
        training_data: ProcessedDataset,
        validation_split: float = 0.2,
        hyperparameter_search: bool = True
    ) -> TrainingResult:
        """
        Train anomaly detection model with optimization
        
        Pipeline:
        1. Data splitting with temporal considerations
        2. Hyperparameter optimization using Optuna
        3. Model training with early stopping
        4. Cross-validation evaluation
        5. Model interpretation and validation
        """
        
        # Split data maintaining temporal order
        train_data, val_data = self._temporal_split(training_data, validation_split)
        
        # Hyperparameter optimization
        if hyperparameter_search:
            best_params = self._optimize_hyperparameters(train_data, val_data)
        else:
            best_params = self.default_params
        
        # Train final model
        model = self._train_model(train_data, best_params)
        
        # Evaluate model
        evaluation_results = self._evaluate_model(model, val_data)
        
        # Generate model interpretation
        interpretation = self._interpret_model(model, val_data)
        
        return TrainingResult(
            model=model,
            parameters=best_params,
            evaluation=evaluation_results,
            interpretation=interpretation,
            training_metadata=self._get_training_metadata()
        )
```

### Model Evaluation Metrics
```python
class TransparencyMetrics:
    """
    Specialized metrics for transparency analysis evaluation
    
    Metrics:
    - Precision/Recall for anomaly detection
    - F1-score with class imbalance handling
    - Area Under ROC Curve (AUC-ROC)
    - Area Under Precision-Recall Curve (AUC-PR)
    - False Positive Rate at operational thresholds
    - Coverage: percentage of true anomalies detected
    """
    
    def calculate_anomaly_detection_metrics(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        threshold: float = 0.5
    ) -> Dict[str, float]:
        """Calculate comprehensive metrics for anomaly detection"""
        
        y_pred = (y_pred_proba > threshold).astype(int)
        
        # Basic classification metrics
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        
        # ROC metrics
        auc_roc = roc_auc_score(y_true, y_pred_proba)
        auc_pr = average_precision_score(y_true, y_pred_proba)
        
        # Cost-sensitive metrics
        false_positive_rate = self._calculate_fpr(y_true, y_pred)
        false_negative_rate = self._calculate_fnr(y_true, y_pred)
        
        # Domain-specific metrics
        coverage = self._calculate_coverage(y_true, y_pred)
        efficiency = self._calculate_efficiency(y_true, y_pred)
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc_roc,
            'auc_pr': auc_pr,
            'false_positive_rate': false_positive_rate,
            'false_negative_rate': false_negative_rate,
            'coverage': coverage,
            'efficiency': efficiency
        }
```

## 🚀 Model Deployment

### HuggingFace Integration (hf_integration.py)

#### Model Publishing to HuggingFace Hub
```python
class HuggingFaceIntegration:
    """
    Integration with HuggingFace Hub for model sharing and deployment
    
    Features:
    - Model uploading with metadata
    - Automatic model card generation
    - Version control and model registry
    - Inference API integration
    - Community model sharing
    """
    
    def upload_model_to_hub(
        self,
        model: tf.keras.Model,
        model_name: str,
        description: str,
        metrics: Dict[str, float]
    ) -> str:
        """
        Upload trained model to HuggingFace Hub
        
        Process:
        1. Convert model to HuggingFace format
        2. Generate model card with metrics and description
        3. Package preprocessing pipelines
        4. Upload to Hub with version tags
        5. Set up inference API
        """
        
        # Convert to HuggingFace format
        hf_model = self._convert_to_hf_format(model)
        
        # Generate model card
        model_card = self._generate_model_card(
            model_name, description, metrics
        )
        
        # Upload to hub
        repo_url = hf_model.push_to_hub(
            model_name,
            commit_message=f"Upload {model_name} v{self.version}",
            model_card=model_card
        )
        
        return repo_url
```

### API Serving (model_api.py)

#### FastAPI Model Serving
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Cidadão.AI ML API")

class PredictionRequest(BaseModel):
    contracts: List[Dict[str, Any]]
    include_explanations: bool = True
    anomaly_threshold: float = 0.5

class PredictionResponse(BaseModel):
    anomalies: List[AnomalyResult]
    model_version: str
    processing_time_ms: float
    confidence_score: float

@app.post("/predict/anomalies", response_model=PredictionResponse)
async def predict_anomalies(request: PredictionRequest):
    """
    Predict anomalies in government contracts
    
    Returns:
    - Anomaly predictions with scores
    - Explanations for each prediction
    - Model metadata and performance metrics
    """
    
    start_time = time.time()
    
    # Load model (cached)
    model = await get_cached_model()
    
    # Preprocess data
    processed_data = preprocess_contracts(request.contracts)
    
    # Make predictions
    predictions = model.predict_anomalies(
        processed_data,
        threshold=request.anomaly_threshold,
        return_explanations=request.include_explanations
    )
    
    processing_time = (time.time() - start_time) * 1000
    
    return PredictionResponse(
        anomalies=predictions.anomalies,
        model_version=model.version,
        processing_time_ms=processing_time,  
        confidence_score=predictions.overall_confidence
    )
```

## 📊 Performance Benchmarks

### Transparency Benchmark Suite (transparency_benchmark.py)

#### Comprehensive Model Evaluation
```python
class TransparencyBenchmark:
    """
    Benchmark suite for transparency analysis models
    
    Tests:
    - Synthetic anomaly detection
    - Real-world case study validation
    - Cross-organization generalization
    - Temporal stability assessment
    - Interpretability quality metrics
    """
    
    def run_comprehensive_benchmark(
        self,
        model: Any,
        test_datasets: List[str]
    ) -> BenchmarkResults:
        """
        Run complete benchmark suite on model
        
        Benchmarks:
        1. Synthetic data with known anomalies
        2. Historical case studies with verified outcomes
        3. Cross-validation across different organizations
        4. Temporal robustness testing
        5. Adversarial robustness evaluation
        """
        
        results = {}
        
        for dataset_name in test_datasets:
            dataset = self._load_benchmark_dataset(dataset_name)
            
            # Run predictions
            predictions = model.predict(dataset.X)
            
            # Calculate metrics
            metrics = self._calculate_metrics(dataset.y, predictions)
            
            # Test interpretability
            interpretability_score = self._test_interpretability(
                model, dataset.X[:10]
            )
            
            results[dataset_name] = {
                'metrics': metrics,
                'interpretability': interpretability_score,
                'processing_time': self._measure_processing_time(model, dataset.X)
            }
        
        return BenchmarkResults(results)
```

## 🧪 Usage Examples

### Basic Anomaly Detection
```python
from src.ml.anomaly_detector import AnomalyDetector
from src.ml.data_pipeline import DataPipeline

# Initialize components
detector = AnomalyDetector()
pipeline = DataPipeline()

# Process contract data
contracts = fetch_contracts_from_api()
processed_data = pipeline.preprocess_contracts(contracts)

# Detect anomalies
anomalies = detector.detect_price_anomalies(
    contracts,
    threshold=2.5
)

for anomaly in anomalies:
    print(f"Anomaly: {anomaly.description}")
    print(f"Confidence: {anomaly.confidence:.2f}")
    print(f"Affected contracts: {len(anomaly.affected_records)}")
```

### Advanced Pattern Analysis
```python
from src.ml.pattern_analyzer import PatternAnalyzer
from src.ml.spectral_analyzer import SpectralAnalyzer

# Initialize analyzers
pattern_analyzer = PatternAnalyzer()
spectral_analyzer = SpectralAnalyzer()

# Analyze spending trends
expenses = fetch_expenses_from_api(organization="20000", year=2024)
trend_analysis = pattern_analyzer.analyze_spending_trends(expenses)

print(f"Trend direction: {trend_analysis.trend_direction}")
print(f"Seasonality strength: {trend_analysis.seasonality_strength:.2f}")
print(f"Anomalous periods: {len(trend_analysis.anomalous_periods)}")

# Spectral analysis
spending_series = extract_monthly_spending(expenses)
spectral_analysis = spectral_analyzer.analyze_spending_spectrum(spending_series)

print(f"Dominant periods: {spectral_analysis.significant_periods}")
print(f"End-of-year effect: {spectral_analysis.eoy_strength:.2f}")
```

### Custom Model Training
```python
from src.ml.training_pipeline import ModelTrainingPipeline
from src.ml.cidadao_model import CidadaoAIModel

# Prepare training data
training_data = prepare_training_dataset()

# Initialize training pipeline
trainer = ModelTrainingPipeline()

# Train model with hyperparameter optimization
training_result = await trainer.train_anomaly_detection_model(
    training_data,
    hyperparameter_search=True,
    cross_validation_folds=5
)

print(f"Best F1 score: {training_result.evaluation.f1_score:.3f}")
print(f"Model size: {training_result.model.count_params()} parameters")

# Deploy to HuggingFace
hf_integration = HuggingFaceIntegration()
model_url = hf_integration.upload_model_to_hub(
    training_result.model,
    "cidadao-ai/anomaly-detector-v1",
    "Government contract anomaly detection model",
    training_result.evaluation.metrics
)

print(f"Model deployed: {model_url}")
```

---

This ML pipeline provides **state-of-the-art anomaly detection** and **pattern analysis** capabilities specifically designed for Brazilian government transparency data, with **full interpretability** and **production-ready deployment** options.