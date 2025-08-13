# 🏢 Cidadão.AI Business Services Layer

## 📋 Overview

The **Business Services Layer** encapsulates the **core business logic** and **domain operations** for transparency analysis. This layer orchestrates complex workflows, coordinates between different system components, and provides high-level services that implement the platform's business requirements.

## 🏗️ Architecture

```
src/services/
├── analysis_service.py      # Core data analysis orchestration
├── data_service.py          # Data management and processing
├── notification_service.py  # Communication and alerting
└── __init__.py             # Service layer initialization
```

## 🎯 Core Services

### 1. **AnalysisService** - Data Analysis Orchestration

#### Comprehensive Analysis Workflows
```python
class AnalysisService:
    """
    Central service for orchestrating government data analysis
    
    Responsibilities:
    - Coordinate multi-agent analysis workflows
    - Implement business logic for transparency analysis
    - Manage analysis caching and optimization
    - Provide high-level analysis APIs
    - Ensure data quality and validation
    """
    
    def __init__(self):
        self._analysis_cache = {}              # Result caching
        self.agent_orchestrator = None         # Multi-agent coordinator
        self.ml_pipeline = None               # ML processing pipeline
        self.data_validator = None            # Data quality validation
```

#### Advanced Analysis Methods
```python
async def analyze_spending_patterns(self, data: List[Dict]) -> Dict:
    """
    Comprehensive spending pattern analysis
    
    Analysis Types:
    - Temporal spending trends
    - Seasonal pattern detection  
    - Organizational behavior analysis
    - Vendor concentration analysis
    - Budget execution efficiency
    - Cross-organizational comparisons
    """
    
    if not data:
        return {"error": "No data provided for analysis"}
    
    # Data preprocessing and validation
    validated_data = await self._validate_and_clean_data(data)
    
    # Multi-dimensional analysis
    analysis_results = {
        # Basic statistics
        "total_items": len(validated_data),
        "total_value": self._calculate_total_value(validated_data),
        "average_value": self._calculate_average_value(validated_data),
        
        # Temporal analysis
        "temporal_patterns": await self._analyze_temporal_patterns(validated_data),
        
        # Statistical analysis
        "statistical_summary": await self._generate_statistical_summary(validated_data),
        
        # Pattern recognition
        "identified_patterns": await self._identify_spending_patterns(validated_data),
        
        # Risk assessment
        "risk_indicators": await self._assess_risk_indicators(validated_data),
        
        # Compliance analysis
        "compliance_status": await self._analyze_compliance(validated_data)
    }
    
    # Cache results for performance
    cache_key = self._generate_cache_key(data)
    self._analysis_cache[cache_key] = analysis_results
    
    return analysis_results

async def detect_anomalies(self, data: List[Dict]) -> List[Dict]:
    """
    Multi-algorithm anomaly detection
    
    Detection Methods:
    - Statistical outliers (Z-score, IQR)
    - Machine learning-based detection
    - Pattern deviation analysis
    - Cross-reference validation
    - Temporal anomaly detection
    """
    
    if not data:
        return []
    
    anomalies = []
    
    # Statistical anomaly detection
    statistical_anomalies = await self._detect_statistical_anomalies(data)
    anomalies.extend(statistical_anomalies)
    
    # ML-based anomaly detection
    if self.ml_pipeline:
        ml_anomalies = await self.ml_pipeline.detect_anomalies(data)
        anomalies.extend(ml_anomalies)
    
    # Pattern-based anomaly detection
    pattern_anomalies = await self._detect_pattern_anomalies(data)
    anomalies.extend(pattern_anomalies)
    
    # Consolidate and rank anomalies
    consolidated_anomalies = await self._consolidate_anomalies(anomalies)
    
    return consolidated_anomalies

async def generate_insights(self, data: List[Dict]) -> List[str]:
    """
    AI-powered insight generation
    
    Insight Categories:
    - Spending efficiency insights
    - Risk and compliance insights  
    - Trend and pattern insights
    - Comparative insights
    - Actionable recommendations
    """
    
    if not data:
        return ["Nenhum dado disponível para análise"]
    
    insights = []
    
    # Data volume insights
    insights.append(f"Analisados {len(data)} registros de dados governamentais")
    
    # Value analysis insights
    total_value = self._calculate_total_value(data)
    if total_value > 0:
        insights.append(f"Valor total analisado: R$ {total_value:,.2f}")
        
        avg_value = total_value / len(data)
        insights.append(f"Valor médio por registro: R$ {avg_value:,.2f}")
    
    # Temporal insights
    temporal_insights = await self._generate_temporal_insights(data)
    insights.extend(temporal_insights)
    
    # Pattern insights
    pattern_insights = await self._generate_pattern_insights(data)
    insights.extend(pattern_insights)
    
    # Risk insights
    risk_insights = await self._generate_risk_insights(data)
    insights.extend(risk_insights)
    
    # Actionable recommendations
    recommendations = await self._generate_recommendations(data)
    insights.extend(recommendations)
    
    return insights
```

#### Advanced Comparative Analysis
```python
async def compare_periods(
    self, 
    current_data: List[Dict], 
    previous_data: List[Dict]
) -> Dict:
    """
    Comprehensive period-over-period comparison
    
    Comparison Dimensions:
    - Volume changes (number of transactions)
    - Value changes (total and average amounts)
    - Efficiency changes (value per transaction)
    - Pattern changes (temporal, vendor, category)
    - Risk profile changes
    - Compliance trend analysis
    """
    
    current_analysis = await self.analyze_spending_patterns(current_data)
    previous_analysis = await self.analyze_spending_patterns(previous_data)
    
    comparison = {
        # Basic metrics comparison
        "volume_comparison": self._compare_volumes(current_data, previous_data),
        "value_comparison": self._compare_values(current_analysis, previous_analysis),
        "efficiency_comparison": self._compare_efficiency(current_analysis, previous_analysis),
        
        # Advanced comparisons
        "pattern_changes": await self._compare_patterns(current_analysis, previous_analysis),
        "risk_profile_changes": await self._compare_risk_profiles(current_analysis, previous_analysis),
        "compliance_trends": await self._compare_compliance(current_analysis, previous_analysis),
        
        # Statistical significance
        "statistical_significance": await self._test_statistical_significance(current_data, previous_data),
        
        # Executive summary
        "executive_summary": await self._generate_comparison_summary(current_analysis, previous_analysis)
    }
    
    return comparison

async def rank_entities(
    self, 
    data: List[Dict], 
    by: str = "valor",
    criteria: str = "total"
) -> List[Dict]:
    """
    Multi-criteria entity ranking and analysis
    
    Ranking Criteria:
    - Total spending volume
    - Average transaction value
    - Transaction frequency
    - Risk score
    - Compliance score
    - Efficiency metrics
    - Anomaly frequency
    """
    
    if not data:
        return []
    
    # Group data by entity
    entities = self._group_by_entity(data)
    
    ranked_entities = []
    
    for entity_id, entity_data in entities.items():
        entity_metrics = {
            "entity_id": entity_id,
            "entity_name": self._get_entity_name(entity_id),
            
            # Volume metrics
            "total_transactions": len(entity_data),
            "total_value": self._calculate_total_value(entity_data),
            "average_value": self._calculate_average_value(entity_data),
            
            # Performance metrics
            "efficiency_score": await self._calculate_efficiency_score(entity_data),
            "compliance_score": await self._calculate_compliance_score(entity_data),
            "risk_score": await self._calculate_risk_score(entity_data),
            
            # Analysis results
            "anomaly_count": await self._count_anomalies(entity_data),
            "pattern_stability": await self._assess_pattern_stability(entity_data),
            
            # Derived metrics
            "value_per_transaction": self._calculate_value_per_transaction(entity_data),
            "transaction_frequency": self._calculate_transaction_frequency(entity_data)
        }
        
        ranked_entities.append(entity_metrics)
    
    # Sort by specified criteria
    if by == "valor":
        ranked_entities.sort(key=lambda x: x["total_value"], reverse=True)
    elif by == "risk":
        ranked_entities.sort(key=lambda x: x["risk_score"], reverse=True)
    elif by == "efficiency":
        ranked_entities.sort(key=lambda x: x["efficiency_score"], reverse=True)
    elif by == "anomalies":
        ranked_entities.sort(key=lambda x: x["anomaly_count"], reverse=True)
    
    return ranked_entities
```

### 2. **DataService** - Data Management Operations

#### Comprehensive Data Management
```python
class DataService:
    """
    Central data management service
    
    Responsibilities:
    - Data ingestion from multiple sources
    - Data quality validation and cleaning
    - Data transformation and normalization
    - Data persistence and caching
    - Data lifecycle management
    """
    
    def __init__(self):
        self.transparency_client = None        # External API client
        self.database_manager = None          # Database operations
        self.cache_manager = None             # Caching layer
        self.data_validator = None            # Data quality validation
        self.transformation_pipeline = None   # Data transformation
    
    async def fetch_government_data(
        self,
        data_type: str,
        filters: Dict[str, Any] = None,
        cache_ttl: int = 3600
    ) -> List[Dict]:
        """
        Fetch data from government transparency APIs
        
        Data Sources:
        - Portal da Transparência
        - IBGE statistical data
        - TCU audit data
        - CGU oversight data
        - State and municipal portals
        """
        
        # Check cache first
        cache_key = self._generate_cache_key(data_type, filters)
        cached_data = await self.cache_manager.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Fetch fresh data
        raw_data = await self.transparency_client.fetch_data(data_type, filters)
        
        # Validate and clean data
        validated_data = await self.data_validator.validate_data(raw_data)
        
        # Transform to standard format
        transformed_data = await self.transformation_pipeline.transform(validated_data)
        
        # Cache results
        await self.cache_manager.set(cache_key, transformed_data, ttl=cache_ttl)
        
        # Persist to database
        await self.database_manager.store_data(data_type, transformed_data)
        
        return transformed_data
    
    async def enrich_data(self, data: List[Dict]) -> List[Dict]:
        """
        Enrich data with additional context and metadata
        
        Enrichment Sources:
        - Organization metadata
        - Vendor company information
        - Geographic information
        - Legal and regulatory context
        - Historical trends and benchmarks
        """
        
        enriched_data = []
        
        for record in data:
            enriched_record = record.copy()
            
            # Add organization context
            if 'orgao' in record:
                org_context = await self._get_organization_context(record['orgao'])
                enriched_record['organization_context'] = org_context
            
            # Add vendor information
            if 'fornecedor' in record:
                vendor_info = await self._get_vendor_information(record['fornecedor'])
                enriched_record['vendor_information'] = vendor_info
            
            # Add geographic context
            if 'municipio' in record or 'uf' in record:
                geo_context = await self._get_geographic_context(record)
                enriched_record['geographic_context'] = geo_context
            
            # Add temporal context
            temporal_context = await self._get_temporal_context(record)
            enriched_record['temporal_context'] = temporal_context
            
            # Add regulatory context
            regulatory_context = await self._get_regulatory_context(record)  
            enriched_record['regulatory_context'] = regulatory_context
            
            enriched_data.append(enriched_record)
        
        return enriched_data
    
    async def validate_data_quality(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive data quality assessment
        
        Quality Dimensions:
        - Completeness (missing values)
        - Accuracy (format validation)
        - Consistency (cross-field validation)
        - Timeliness (data freshness)
        - Validity (business rule compliance)
        """
        
        quality_report = {
            "total_records": len(data),
            "validation_timestamp": datetime.utcnow(),
            "quality_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Completeness check
        completeness_score = await self._assess_completeness(data)
        quality_report["completeness"] = completeness_score
        
        # Accuracy check  
        accuracy_score = await self._assess_accuracy(data)
        quality_report["accuracy"] = accuracy_score
        
        # Consistency check
        consistency_score = await self._assess_consistency(data)
        quality_report["consistency"] = consistency_score
        
        # Timeliness check
        timeliness_score = await self._assess_timeliness(data)
        quality_report["timeliness"] = timeliness_score
        
        # Calculate overall quality score
        quality_report["quality_score"] = (
            completeness_score + accuracy_score + 
            consistency_score + timeliness_score
        ) / 4
        
        # Generate recommendations
        quality_report["recommendations"] = await self._generate_quality_recommendations(
            quality_report
        )
        
        return quality_report
```

### 3. **NotificationService** - Communication & Alerting

#### Multi-Channel Notification System
```python
class NotificationService:
    """
    Multi-channel notification and alerting service
    
    Channels:
    - Email notifications
    - SMS alerts
    - WebSocket real-time updates
    - Webhook integrations
    - In-app notifications
    - Slack/Teams integration
    """
    
    def __init__(self):
        self.email_client = None              # Email service
        self.sms_client = None               # SMS service  
        self.websocket_manager = None        # Real-time updates
        self.webhook_client = None           # Webhook notifications
        self.notification_templates = {}     # Message templates
        self.subscription_manager = None     # User preferences
    
    async def send_anomaly_alert(
        self,
        anomaly: Dict[str, Any],
        recipients: List[str],
        severity: str = "medium"
    ) -> bool:
        """
        Send anomaly detection alerts across multiple channels
        
        Alert Types:
        - Immediate alerts for critical anomalies
        - Daily digest for medium severity
        - Weekly summary for low severity
        - Real-time dashboard updates
        """
        
        # Generate alert content
        alert_content = await self._generate_anomaly_alert_content(anomaly, severity)
        
        # Determine delivery channels based on severity
        channels = await self._determine_alert_channels(severity)
        
        delivery_results = {}
        
        for channel in channels:
            if channel == "email":
                result = await self._send_email_alert(alert_content, recipients)
                delivery_results["email"] = result
                
            elif channel == "sms" and severity == "critical":
                result = await self._send_sms_alert(alert_content, recipients)
                delivery_results["sms"] = result
                
            elif channel == "websocket":
                result = await self._send_websocket_update(alert_content)
                delivery_results["websocket"] = result
                
            elif channel == "webhook":
                result = await self._send_webhook_notification(alert_content)
                delivery_results["webhook"] = result
        
        # Log notification delivery
        await self._log_notification_delivery(anomaly, delivery_results)
        
        return all(delivery_results.values())
    
    async def send_analysis_report(
        self,
        report: Dict[str, Any],
        recipients: List[str],
        format: str = "html"
    ) -> bool:
        """
        Send formatted analysis reports
        
        Report Formats:
        - HTML email with embedded charts
        - PDF attachment with detailed analysis
        - JSON for API integrations
        - CSV for data analysis tools
        """
        
        # Format report based on requested format
        formatted_report = await self._format_report(report, format)
        
        # Generate report email
        email_content = await self._generate_report_email(formatted_report, format)
        
        # Send email with report
        success = await self._send_email_with_attachment(
            content=email_content,
            recipients=recipients,
            attachment=formatted_report if format == "pdf" else None
        )
        
        return success
    
    async def setup_alert_subscription(
        self,
        user_id: str,
        alert_types: List[str],
        channels: List[str],
        filters: Dict[str, Any] = None
    ) -> bool:
        """
        Configure user alert subscriptions
        
        Subscription Options:
        - Alert types (anomalies, reports, system updates)
        - Delivery channels (email, SMS, webhook)
        - Severity thresholds
        - Content filters
        - Delivery frequency
        """
        
        subscription = {
            "user_id": user_id,
            "alert_types": alert_types,
            "channels": channels,
            "filters": filters or {},
            "created_at": datetime.utcnow(),
            "active": True
        }
        
        # Store subscription preferences
        success = await self.subscription_manager.create_subscription(subscription)
        
        # Send confirmation
        if success:
            await self._send_subscription_confirmation(user_id, subscription)
        
        return success
```

## 🔄 Service Integration Patterns

### Service Orchestration
```python
class ServiceOrchestrator:
    """
    Central orchestrator for coordinating business services
    
    Responsibilities:
    - Service dependency management
    - Workflow orchestration
    - Error handling and recovery
    - Performance monitoring
    - Resource management
    """
    
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.data_service = DataService()
        self.notification_service = NotificationService()
        
    async def execute_comprehensive_analysis(
        self,
        investigation_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute end-to-end transparency analysis workflow
        
        Workflow:
        1. Data acquisition and validation
        2. Data enrichment and preprocessing
        3. Multi-dimensional analysis
        4. Anomaly detection
        5. Insight generation
        6. Report creation
        7. Notification delivery
        """
        
        try:
            # Step 1: Acquire and validate data
            raw_data = await self.data_service.fetch_government_data(
                data_type=investigation_request["data_type"],
                filters=investigation_request.get("filters", {})
            )
            
            # Step 2: Enrich data with context
            enriched_data = await self.data_service.enrich_data(raw_data)
            
            # Step 3: Execute analysis
            analysis_results = await self.analysis_service.analyze_spending_patterns(
                enriched_data
            )
            
            # Step 4: Detect anomalies
            anomalies = await self.analysis_service.detect_anomalies(enriched_data)
            
            # Step 5: Generate insights
            insights = await self.analysis_service.generate_insights(enriched_data)
            
            # Step 6: Create comprehensive report
            report = {
                "investigation_id": investigation_request["id"],
                "data_summary": {
                    "total_records": len(enriched_data),
                    "data_quality": await self.data_service.validate_data_quality(enriched_data)
                },
                "analysis_results": analysis_results,
                "anomalies": anomalies,
                "insights": insights,
                "timestamp": datetime.utcnow()
            }
            
            # Step 7: Send notifications if anomalies found
            if anomalies:
                critical_anomalies = [a for a in anomalies if a.get("severity") == "critical"]
                if critical_anomalies:
                    await self.notification_service.send_anomaly_alert(
                        anomaly=critical_anomalies[0],
                        recipients=investigation_request.get("alert_recipients", []),
                        severity="critical"
                    )
            
            return report
            
        except Exception as e:
            # Error handling and notification
            error_report = {
                "investigation_id": investigation_request["id"],
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.utcnow()
            }
            
            # Send error notification
            await self.notification_service.send_error_notification(
                error_report,
                investigation_request.get("alert_recipients", [])
            )
            
            raise
```

## 🧪 Usage Examples

### Basic Analysis Service Usage
```python
from src.services.analysis_service import AnalysisService

# Initialize service
analysis_service = AnalysisService()

# Analyze government spending data
contracts_data = await fetch_contracts_from_api()
analysis_results = await analysis_service.analyze_spending_patterns(contracts_data)

print(f"Total analyzed: R$ {analysis_results['total_value']:,.2f}")
print(f"Anomalies found: {len(analysis_results.get('anomalies', []))}")

# Generate insights
insights = await analysis_service.generate_insights(contracts_data)
for insight in insights:
    print(f"💡 {insight}")

# Compare with previous period
previous_data = await fetch_previous_period_data()
comparison = await analysis_service.compare_periods(contracts_data, previous_data)
print(f"Change: {comparison['percentage_change']:.1f}%")
```

### Data Service Integration
```python
from src.services.data_service import DataService

# Initialize data service
data_service = DataService()

# Fetch and enrich government data
raw_data = await data_service.fetch_government_data(
    data_type="contracts",
    filters={"year": 2024, "organization": "20000"}
)

enriched_data = await data_service.enrich_data(raw_data)

# Validate data quality
quality_report = await data_service.validate_data_quality(enriched_data)
print(f"Data quality score: {quality_report['quality_score']:.2f}")
```

### Notification Service Setup
```python
from src.services.notification_service import NotificationService

# Initialize notification service
notification_service = NotificationService()

# Setup alert subscription
await notification_service.setup_alert_subscription(
    user_id="user123",
    alert_types=["anomalies", "critical_findings"],
    channels=["email", "webhook"],
    filters={"severity": ["high", "critical"]}
)

# Send anomaly alert
anomaly = {
    "type": "price_outlier",
    "description": "Contract value 300% above expected range",
    "confidence": 0.95,
    "affected_value": 5000000.00
}

await notification_service.send_anomaly_alert(
    anomaly=anomaly,
    recipients=["analyst@government.gov"],
    severity="critical"
)
```

### Service Orchestration
```python
from src.services import ServiceOrchestrator

# Initialize orchestrator
orchestrator = ServiceOrchestrator()

# Execute comprehensive analysis
investigation_request = {
    "id": "inv_001",
    "data_type": "contracts",
    "filters": {"year": 2024, "organization": "20000"},
    "alert_recipients": ["analyst@government.gov"]
}

report = await orchestrator.execute_comprehensive_analysis(investigation_request)

print(f"Analysis completed for investigation {report['investigation_id']}")
print(f"Found {len(report['anomalies'])} anomalies")
print(f"Generated {len(report['insights'])} insights")
```

## 🔧 Configuration & Environment

### Service Configuration
```python
# Environment variables for service configuration
SERVICE_CONFIG = {
    # Analysis Service
    "ANALYSIS_CACHE_TTL": 3600,
    "ENABLE_ML_ANOMALY_DETECTION": True,
    "ANOMALY_THRESHOLD": 0.8,
    
    # Data Service  
    "DATA_FETCH_TIMEOUT": 30,
    "DATA_CACHE_TTL": 1800,
    "ENABLE_DATA_ENRICHMENT": True,
    
    # Notification Service
    "EMAIL_SMTP_SERVER": "smtp.gmail.com",
    "SMS_API_KEY": "your_sms_api_key",
    "WEBHOOK_TIMEOUT": 10,
    "ENABLE_REAL_TIME_ALERTS": True
}
```

---

This business services layer provides **comprehensive orchestration** of transparency analysis operations, implementing **sophisticated business logic** while maintaining **clean separation of concerns** and **high-level abstractions** for complex government data processing workflows.