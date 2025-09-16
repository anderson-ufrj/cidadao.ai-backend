"""Unit tests for service layer components."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from src.services.analysis_service import (
    AnalysisService,
    ContractAnalysis,
    SpendingAnalysis,
    VendorAnalysis,
    RiskAssessment
)
from src.services.data_service import (
    DataService,
    DataSource,
    DataFilter,
    DataAggregation,
    DataQuality
)
from src.services.notification_service import (
    NotificationService,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    NotificationTemplate
)
from src.services.investigation_service import (
    InvestigationService,
    InvestigationRequest,
    InvestigationPlan,
    InvestigationResult
)


class TestAnalysisService:
    """Test analysis service functionality."""
    
    @pytest.fixture
    def analysis_service(self):
        """Create analysis service instance."""
        return AnalysisService()
    
    @pytest.fixture
    def sample_contracts(self):
        """Create sample contract data."""
        return pd.DataFrame({
            'contract_id': [f'CTR-{i:03d}' for i in range(100)],
            'value': np.random.lognormal(11, 1.5, 100),  # Log-normal distribution
            'vendor_id': np.random.choice(['V001', 'V002', 'V003', 'V004', 'V005'], 100),
            'date': pd.date_range('2024-01-01', periods=100, freq='D'),
            'category': np.random.choice(['IT', 'Medical', 'Construction'], 100),
            'duration_days': np.random.randint(30, 365, 100)
        })
    
    @pytest.mark.asyncio
    async def test_contract_analysis(self, analysis_service, sample_contracts):
        """Test contract analysis functionality."""
        analysis = ContractAnalysis()
        
        result = await analysis.analyze_contracts(sample_contracts)
        
        assert result is not None
        assert 'summary_stats' in result
        assert 'anomalies' in result
        assert 'risk_score' in result
        
        # Check summary statistics
        stats = result['summary_stats']
        assert stats['total_contracts'] == 100
        assert stats['total_value'] > 0
        assert stats['avg_value'] > 0
        assert stats['median_value'] > 0
    
    @pytest.mark.asyncio
    async def test_anomaly_detection_in_contracts(self, analysis_service, sample_contracts):
        """Test anomaly detection in contract analysis."""
        # Add anomalous contracts
        anomalous = sample_contracts.copy()
        anomalous.loc[0, 'value'] = anomalous['value'].mean() * 10  # 10x average
        anomalous.loc[1, 'duration_days'] = 1  # Very short duration
        
        analysis = ContractAnalysis()
        result = await analysis.analyze_contracts(anomalous)
        
        anomalies = result['anomalies']
        assert len(anomalies) >= 2
        
        # Check anomaly details
        assert any(a['type'] == 'price_anomaly' for a in anomalies)
        assert any(a['type'] == 'duration_anomaly' for a in anomalies)
    
    @pytest.mark.asyncio
    async def test_spending_pattern_analysis(self, analysis_service):
        """Test spending pattern analysis."""
        # Create spending data with patterns
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        spending_data = pd.DataFrame({
            'date': dates,
            'amount': [
                100000 * (1 + 0.5 * np.sin(2 * np.pi * i / 30))  # Monthly pattern
                + 50000 * (1 if d.month == 12 else 0)  # Year-end spike
                + np.random.normal(0, 10000)  # Noise
                for i, d in enumerate(dates)
            ],
            'department': np.random.choice(['Health', 'Education', 'Infrastructure'], len(dates))
        })
        
        analysis = SpendingAnalysis()
        patterns = await analysis.detect_patterns(spending_data)
        
        assert 'seasonal_patterns' in patterns
        assert 'trend' in patterns
        assert 'anomalous_periods' in patterns
        
        # Should detect year-end spike
        anomalous = patterns['anomalous_periods']
        assert any(p['period'].month == 12 for p in anomalous)
    
    @pytest.mark.asyncio
    async def test_vendor_concentration_analysis(self, analysis_service, sample_contracts):
        """Test vendor concentration analysis."""
        # Create concentrated vendor scenario
        concentrated = sample_contracts.copy()
        concentrated.loc[:70, 'vendor_id'] = 'V001'  # 70% to one vendor
        
        analysis = VendorAnalysis()
        result = await analysis.analyze_concentration(concentrated)
        
        assert 'concentration_index' in result
        assert 'top_vendors' in result
        assert 'risk_level' in result
        
        # Should detect high concentration
        assert result['concentration_index'] > 0.7
        assert result['risk_level'] == 'high'
        assert result['top_vendors'][0]['vendor_id'] == 'V001'
        assert result['top_vendors'][0]['percentage'] > 0.7
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, analysis_service, sample_contracts):
        """Test comprehensive risk assessment."""
        assessment = RiskAssessment()
        
        # Add risk factors
        risk_contracts = sample_contracts.copy()
        risk_contracts.loc[0, 'value'] = risk_contracts['value'].mean() * 20
        risk_contracts.loc[:60, 'vendor_id'] = 'V001'  # Vendor concentration
        
        risk_score = await assessment.calculate_risk(
            contracts=risk_contracts,
            historical_data=sample_contracts
        )
        
        assert isinstance(risk_score, dict)
        assert 'overall_risk' in risk_score
        assert 'risk_factors' in risk_score
        assert 'recommendations' in risk_score
        
        assert risk_score['overall_risk'] > 0.7  # High risk
        assert len(risk_score['risk_factors']) >= 2


class TestDataService:
    """Test data service functionality."""
    
    @pytest.fixture
    def data_service(self):
        """Create data service instance."""
        return DataService()
    
    @pytest.mark.asyncio
    async def test_data_source_registration(self, data_service):
        """Test registering data sources."""
        source = DataSource(
            id="transparency_api",
            name="Portal da Transparência",
            type="api",
            config={
                "base_url": "https://api.portaltransparencia.gov.br",
                "auth_required": True
            }
        )
        
        await data_service.register_source(source)
        
        # Verify registration
        registered = await data_service.get_source("transparency_api")
        assert registered is not None
        assert registered.name == "Portal da Transparência"
    
    @pytest.mark.asyncio
    async def test_data_filtering(self, data_service):
        """Test data filtering capabilities."""
        # Sample data
        data = pd.DataFrame({
            'entity': ['MinHealth', 'MinEdu', 'MinHealth', 'MinInfra'],
            'value': [100000, 200000, 150000, 300000],
            'date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01']),
            'status': ['active', 'active', 'cancelled', 'active']
        })
        
        # Apply filters
        filters = DataFilter(
            entity="MinHealth",
            status="active",
            date_range=("2024-01-01", "2024-12-31")
        )
        
        filtered = await data_service.apply_filters(data, filters)
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['entity'] == 'MinHealth'
        assert filtered.iloc[0]['status'] == 'active'
    
    @pytest.mark.asyncio
    async def test_data_aggregation(self, data_service):
        """Test data aggregation functionality."""
        data = pd.DataFrame({
            'department': ['Health', 'Health', 'Education', 'Education'],
            'category': ['IT', 'Medical', 'IT', 'Books'],
            'amount': [100000, 200000, 150000, 50000]
        })
        
        aggregation = DataAggregation(
            group_by=['department'],
            aggregations={
                'amount': ['sum', 'mean', 'count'],
            }
        )
        
        result = await data_service.aggregate_data(data, aggregation)
        
        assert len(result) == 2  # Two departments
        assert 'amount_sum' in result.columns
        assert 'amount_mean' in result.columns
        assert 'amount_count' in result.columns
        
        health_row = result[result['department'] == 'Health'].iloc[0]
        assert health_row['amount_sum'] == 300000
        assert health_row['amount_count'] == 2
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment(self, data_service):
        """Test data quality assessment."""
        # Create data with quality issues
        data = pd.DataFrame({
            'id': [1, 2, 3, None, 5],  # Missing value
            'value': [100, 200, -50, 300, 1e9],  # Negative and outlier
            'date': ['2024-01-01', '2024-02-01', 'invalid', '2024-04-01', '2024-05-01'],
            'duplicate': [1, 1, 2, 3, 4]  # Duplicate values
        })
        
        quality = DataQuality()
        assessment = await quality.assess_quality(data)
        
        assert 'completeness' in assessment
        assert 'validity' in assessment
        assert 'consistency' in assessment
        assert 'issues' in assessment
        
        # Should detect issues
        assert assessment['completeness'] < 1.0  # Missing values
        assert len(assessment['issues']) > 0
        assert any(issue['type'] == 'missing_value' for issue in assessment['issues'])
        assert any(issue['type'] == 'invalid_value' for issue in assessment['issues'])


class TestNotificationService:
    """Test notification service functionality."""
    
    @pytest.fixture
    def notification_service(self):
        """Create notification service instance."""
        return NotificationService()
    
    @pytest.mark.asyncio
    async def test_send_notification(self, notification_service):
        """Test sending notifications."""
        # Mock notification channels
        with patch.object(notification_service, '_send_email') as mock_email:
            mock_email.return_value = True
            
            result = await notification_service.send_notification(
                type=NotificationType.ANOMALY_DETECTED,
                channel=NotificationChannel.EMAIL,
                recipient="admin@cidadao.ai",
                data={
                    "anomaly_count": 5,
                    "severity": "high",
                    "investigation_id": "inv-123"
                }
            )
            
            assert result is True
            mock_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_notification_templates(self, notification_service):
        """Test notification template rendering."""
        template = NotificationTemplate(
            id="anomaly_alert",
            type=NotificationType.ANOMALY_DETECTED,
            subject="🚨 {anomaly_count} Anomalies Detected",
            body="""
            Investigation: {investigation_id}
            Severity: {severity}
            Anomalies Found: {anomaly_count}
            
            Please review the findings immediately.
            """
        )
        
        rendered = await notification_service.render_template(
            template,
            data={
                "anomaly_count": 3,
                "severity": "medium",
                "investigation_id": "inv-456"
            }
        )
        
        assert "3 Anomalies Detected" in rendered['subject']
        assert "inv-456" in rendered['body']
        assert "medium" in rendered['body']
    
    @pytest.mark.asyncio
    async def test_notification_priority_queue(self, notification_service):
        """Test notification priority queuing."""
        # Queue notifications with different priorities
        notifications = [
            {
                "type": NotificationType.SYSTEM_ALERT,
                "priority": NotificationPriority.LOW,
                "data": {"message": "Low priority"}
            },
            {
                "type": NotificationType.ANOMALY_DETECTED,
                "priority": NotificationPriority.CRITICAL,
                "data": {"message": "Critical anomaly"}
            },
            {
                "type": NotificationType.REPORT_READY,
                "priority": NotificationPriority.MEDIUM,
                "data": {"message": "Report ready"}
            }
        ]
        
        for notif in notifications:
            await notification_service.queue_notification(**notif)
        
        # Process queue - critical should be first
        processed = await notification_service.process_queue()
        
        assert processed[0]['priority'] == NotificationPriority.CRITICAL
        assert processed[-1]['priority'] == NotificationPriority.LOW
    
    @pytest.mark.asyncio
    async def test_notification_rate_limiting(self, notification_service):
        """Test notification rate limiting."""
        recipient = "user@example.com"
        
        # Send multiple notifications
        for i in range(10):
            await notification_service.send_notification(
                type=NotificationType.ANOMALY_DETECTED,
                channel=NotificationChannel.EMAIL,
                recipient=recipient,
                data={"count": i}
            )
        
        # Check rate limit
        stats = await notification_service.get_recipient_stats(recipient)
        assert stats['notifications_sent'] <= notification_service.rate_limit_per_hour


class TestInvestigationService:
    """Test investigation service functionality."""
    
    @pytest.fixture
    def investigation_service(self):
        """Create investigation service instance."""
        return InvestigationService()
    
    @pytest.mark.asyncio
    async def test_create_investigation_plan(self, investigation_service):
        """Test creating investigation plan."""
        request = InvestigationRequest(
            id="req-123",
            query="Analyze health ministry contracts for overpricing",
            parameters={
                "entity": "Ministry of Health",
                "period": "2024",
                "focus": "price_anomalies"
            }
        )
        
        plan = await investigation_service.create_plan(request)
        
        assert isinstance(plan, InvestigationPlan)
        assert len(plan.steps) > 0
        assert any(step.agent_type == "investigator" for step in plan.steps)
        assert any(step.agent_type == "analyst" for step in plan.steps)
        assert plan.estimated_duration > 0
    
    @pytest.mark.asyncio
    async def test_execute_investigation(self, investigation_service):
        """Test investigation execution."""
        # Mock agent responses
        with patch('src.agents.abaporu.MasterAgent.execute') as mock_execute:
            mock_execute.return_value = AsyncMock(
                status="completed",
                result={
                    "anomalies": [
                        {"type": "price", "severity": 0.8},
                        {"type": "vendor", "severity": 0.6}
                    ],
                    "summary": "Found 2 significant anomalies"
                }
            )
            
            request = InvestigationRequest(
                id="inv-exec-123",
                query="Test investigation",
                parameters={}
            )
            
            result = await investigation_service.execute_investigation(request)
            
            assert isinstance(result, InvestigationResult)
            assert result.status == "completed"
            assert len(result.findings['anomalies']) == 2
            assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_investigation_progress_tracking(self, investigation_service):
        """Test tracking investigation progress."""
        investigation_id = "track-123"
        
        # Update progress
        await investigation_service.update_progress(
            investigation_id,
            step="data_collection",
            progress=0.5,
            message="Collected 50% of contract data"
        )
        
        await investigation_service.update_progress(
            investigation_id,
            step="analysis",
            progress=0.3,
            message="Analyzing patterns"
        )
        
        # Get overall progress
        progress = await investigation_service.get_progress(investigation_id)
        
        assert progress['overall_progress'] > 0
        assert 'data_collection' in progress['steps']
        assert progress['steps']['data_collection']['progress'] == 0.5
    
    @pytest.mark.asyncio
    async def test_investigation_caching(self, investigation_service):
        """Test investigation result caching."""
        request = InvestigationRequest(
            id="cache-123",
            query="Cached investigation",
            parameters={"entity": "test", "use_cache": True}
        )
        
        # First execution
        with patch('src.agents.abaporu.MasterAgent.execute') as mock_execute:
            mock_execute.return_value = AsyncMock(
                status="completed",
                result={"data": "first_execution"}
            )
            
            result1 = await investigation_service.execute_investigation(request)
            assert mock_execute.call_count == 1
        
        # Second execution should use cache
        result2 = await investigation_service.execute_investigation(request)
        
        assert result1.findings == result2.findings
        assert result2.from_cache is True