"""
Module: tests.unit.api.routes.test_export
Description: Unit tests for export routes
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import pandas as pd
import base64
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api.routes.export import (
    export_investigation, export_contracts, export_anomalies,
    bulk_export, _format_investigation_as_markdown
)


class TestExportRoutes:
    """Test suite for export API routes."""
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user."""
        return {
            'user_id': 'test-user-123',
            'email': 'test@example.com',
            'roles': ['user']
        }
    
    @pytest.fixture
    def mock_investigation(self):
        """Mock investigation data."""
        return {
            'id': 'INV-001',
            'type': 'contract_analysis',
            'status': 'completed',
            'created_at': '2024-01-20T10:00:00',
            'completed_at': '2024-01-20T10:30:00',
            'summary': 'Investigation completed successfully',
            'anomalies': [
                {
                    'type': 'value_outlier',
                    'severity': 0.85,
                    'description': 'High value contract',
                    'explanation': 'Contract value exceeds threshold'
                }
            ],
            'contracts': [
                {
                    'id': 'C001',
                    'value': 500000,
                    'supplier': 'Company A',
                    'date': '2024-01-15'
                }
            ],
            'total_value': 500000
        }
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.investigation_service')
    @patch('src.api.routes.export.export_service')
    async def test_export_investigation_excel(
        self, mock_export_service, mock_investigation_service, 
        mock_current_user, mock_investigation
    ):
        """Test export investigation as Excel."""
        # Setup mocks
        mock_investigation_service.get_investigation.return_value = mock_investigation
        mock_export_service.convert_investigation_to_excel.return_value = b'excel-content'
        
        # Call function
        response = await export_investigation(
            investigation_id='INV-001',
            format='excel',
            current_user=mock_current_user
        )
        
        # Verify
        assert response.body == b'excel-content'
        assert response.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert 'attachment' in response.headers['Content-Disposition']
        assert '.xlsx' in response.headers['Content-Disposition']
        
        mock_investigation_service.get_investigation.assert_called_once_with(
            'INV-001', 
            user_id='test-user-123'
        )
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.investigation_service')
    @patch('src.api.routes.export.export_service')
    async def test_export_investigation_csv(
        self, mock_export_service, mock_investigation_service,
        mock_current_user, mock_investigation
    ):
        """Test export investigation as CSV."""
        # Setup mocks
        mock_investigation_service.get_investigation.return_value = mock_investigation
        mock_export_service.generate_csv.return_value = b'csv-content'
        
        # Call function
        response = await export_investigation(
            investigation_id='INV-001',
            format='csv',
            current_user=mock_current_user
        )
        
        # Verify
        assert response.body == b'csv-content'
        assert response.media_type == "text/csv"
        assert '.csv' in response.headers['Content-Disposition']
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.investigation_service')
    @patch('src.api.routes.export.export_service')
    async def test_export_investigation_pdf(
        self, mock_export_service, mock_investigation_service,
        mock_current_user, mock_investigation
    ):
        """Test export investigation as PDF."""
        # Setup mocks
        mock_investigation_service.get_investigation.return_value = mock_investigation
        mock_export_service.generate_pdf.return_value = b'pdf-content'
        
        # Call function
        response = await export_investigation(
            investigation_id='INV-001',
            format='pdf',
            current_user=mock_current_user
        )
        
        # Verify
        assert response.body == b'pdf-content'
        assert response.media_type == "application/pdf"
        assert '.pdf' in response.headers['Content-Disposition']
        
        # Check PDF generation was called with correct params
        mock_export_service.generate_pdf.assert_called_once()
        call_args = mock_export_service.generate_pdf.call_args[1]
        assert 'Investigação INV-001' in call_args['title']
        assert call_args['metadata']['investigation_id'] == 'INV-001'
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.investigation_service')
    async def test_export_investigation_not_found(
        self, mock_investigation_service, mock_current_user
    ):
        """Test export investigation when not found."""
        # Setup mock
        mock_investigation_service.get_investigation.return_value = None
        
        # Call function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await export_investigation(
                investigation_id='INV-999',
                format='excel',
                current_user=mock_current_user
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Investigation not found"
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.data_service')
    @patch('src.api.routes.export.export_service')
    async def test_export_contracts_excel(
        self, mock_export_service, mock_data_service, mock_current_user
    ):
        """Test export contracts as Excel."""
        from src.api.routes.export import ExportRequest
        
        # Setup mocks
        mock_contracts = [
            {'id': 'C001', 'value': 100000, 'supplier': 'Company A'},
            {'id': 'C002', 'value': 200000, 'supplier': 'Company B'}
        ]
        mock_data_service.search_contracts.return_value = mock_contracts
        mock_export_service.generate_excel.return_value = b'excel-content'
        
        # Create request
        request = ExportRequest(
            export_type='contracts',
            format='excel',
            filters={'year': 2024},
            include_metadata=True,
            compress=False
        )
        
        # Call function
        response = await export_contracts(request, mock_current_user)
        
        # Verify
        assert response.body == b'excel-content'
        assert response.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        # Check search was called with filters
        mock_data_service.search_contracts.assert_called_once()
        call_kwargs = mock_data_service.search_contracts.call_args[1]
        assert call_kwargs['year'] == 2024
        assert call_kwargs['limit'] == 10000
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.investigation_service')
    @patch('src.api.routes.export.export_service')
    async def test_export_anomalies_excel(
        self, mock_export_service, mock_investigation_service, mock_current_user
    ):
        """Test export anomalies as Excel."""
        from src.api.routes.export import ExportRequest
        
        # Setup mocks
        mock_investigations = [
            {
                'id': 'INV-001',
                'anomalies': [
                    {'severity': 0.8, 'type': 'high', 'description': 'High risk'},
                    {'severity': 0.5, 'type': 'medium', 'description': 'Medium risk'}
                ]
            },
            {
                'id': 'INV-002',
                'anomalies': [
                    {'severity': 0.3, 'type': 'low', 'description': 'Low risk'}
                ]
            }
        ]
        mock_investigation_service.list_investigations.return_value = mock_investigations
        mock_export_service.generate_excel.return_value = b'excel-content'
        
        # Create request
        request = ExportRequest(
            export_type='anomalies',
            format='excel',
            filters={},
            include_metadata=True,
            compress=False
        )
        
        # Call function
        response = await export_anomalies(request, mock_current_user)
        
        # Verify
        assert response.body == b'excel-content'
        
        # Check Excel generation was called with multiple sheets
        mock_export_service.generate_excel.assert_called_once()
        call_args = mock_export_service.generate_excel.call_args[1]
        data_arg = call_args['data']
        
        # Should have sheets for different severity levels
        assert 'Alta Severidade' in data_arg
        assert 'Média Severidade' in data_arg
        assert 'Baixa Severidade' in data_arg
        assert 'Todas Anomalias' in data_arg
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.investigation_service')
    @patch('src.api.routes.export.export_service')
    @patch('src.api.routes.export.json_utils')
    async def test_bulk_export(
        self, mock_json_utils, mock_export_service, 
        mock_investigation_service, mock_current_user, mock_investigation
    ):
        """Test bulk export functionality."""
        from src.api.routes.export import BulkExportRequest
        
        # Setup mocks
        mock_investigation_service.get_investigation.return_value = mock_investigation
        mock_export_service.generate_bulk_export.return_value = b'zip-content'
        mock_json_utils.dumps.return_value = '{"test": "json"}'
        
        # Create request
        request = BulkExportRequest(
            exports=[
                {'type': 'investigation', 'id': 'INV-001', 'format': 'pdf'},
                {'type': 'investigation', 'id': 'INV-002', 'format': 'json'}
            ],
            compress=True
        )
        
        # Call function
        response = await bulk_export(request, mock_current_user)
        
        # Verify
        assert response.body == b'zip-content'
        assert response.media_type == "application/zip"
        assert '.zip' in response.headers['Content-Disposition']
        
        # Check bulk export was called
        mock_export_service.generate_bulk_export.assert_called_once()
        exports_config = mock_export_service.generate_bulk_export.call_args[0][0]
        assert len(exports_config) == 2
    
    def test_format_investigation_as_markdown(self, mock_investigation):
        """Test investigation markdown formatting."""
        markdown = _format_investigation_as_markdown(mock_investigation)
        
        # Verify content
        assert '# Investigação INV-001' in markdown
        assert '**Tipo**: contract_analysis' in markdown
        assert '**Status**: completed' in markdown
        assert '## Resumo' in markdown
        assert 'Investigation completed successfully' in markdown
        assert '## Anomalias Detectadas' in markdown
        assert 'Total de anomalias: 1' in markdown
        assert '### Anomalia 1' in markdown
        assert '**Severidade**: 0.85' in markdown
    
    def test_format_investigation_as_markdown_no_anomalies(self):
        """Test investigation markdown formatting without anomalies."""
        investigation = {
            'id': 'INV-002',
            'type': 'routine_check',
            'status': 'completed',
            'created_at': '2024-01-21T10:00:00',
            'anomalies': []
        }
        
        markdown = _format_investigation_as_markdown(investigation)
        
        # Should not have anomalies section
        assert '## Anomalias Detectadas' not in markdown
        assert '# Investigação INV-002' in markdown
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.data_service')
    async def test_export_contracts_not_found(
        self, mock_data_service, mock_current_user
    ):
        """Test export contracts when none found."""
        from src.api.routes.export import ExportRequest
        
        # Setup mock
        mock_data_service.search_contracts.return_value = []
        
        # Create request
        request = ExportRequest(
            export_type='contracts',
            format='excel',
            filters={'year': 2025}
        )
        
        # Call function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await export_contracts(request, mock_current_user)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "No contracts found with given filters"
    
    @pytest.mark.asyncio
    @patch('src.api.routes.export.investigation_service')
    async def test_export_anomalies_none_found(
        self, mock_investigation_service, mock_current_user
    ):
        """Test export anomalies when none found."""
        from src.api.routes.export import ExportRequest
        
        # Setup mock - investigations without anomalies
        mock_investigations = [
            {'id': 'INV-001', 'anomalies': []},
            {'id': 'INV-002', 'anomalies': []}
        ]
        mock_investigation_service.list_investigations.return_value = mock_investigations
        
        # Create request
        request = ExportRequest(
            export_type='anomalies',
            format='excel'
        )
        
        # Call function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await export_anomalies(request, mock_current_user)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "No anomalies found"
    
    def test_export_request_validation(self):
        """Test ExportRequest validation."""
        from src.api.routes.export import ExportRequest
        
        # Valid request
        request = ExportRequest(
            export_type='investigations',
            format='excel'
        )
        assert request.export_type == 'investigations'
        assert request.format == 'excel'
        assert request.include_metadata is True
        assert request.compress is False
        
        # Invalid export type
        with pytest.raises(ValueError) as exc_info:
            ExportRequest(
                export_type='invalid_type',
                format='excel'
            )
        assert 'Export type must be one of' in str(exc_info.value)
        
        # Invalid format
        with pytest.raises(ValueError) as exc_info:
            ExportRequest(
                export_type='contracts',
                format='invalid_format'
            )
        assert 'Format must be one of' in str(exc_info.value)
    
    def test_bulk_export_request_validation(self):
        """Test BulkExportRequest validation."""
        from src.api.routes.export import BulkExportRequest
        
        # Valid request
        request = BulkExportRequest(
            exports=[{'type': 'investigation', 'id': '123'}]
        )
        assert len(request.exports) == 1
        assert request.compress is True
        
        # Empty exports
        with pytest.raises(ValueError) as exc_info:
            BulkExportRequest(exports=[])
        assert 'At least one export must be specified' in str(exc_info.value)
        
        # Too many exports
        with pytest.raises(ValueError) as exc_info:
            BulkExportRequest(
                exports=[{'type': 'investigation', 'id': str(i)} for i in range(51)]
            )
        assert 'Maximum 50 exports allowed' in str(exc_info.value)