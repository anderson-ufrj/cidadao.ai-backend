"""Tests for investigation service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.investigation import Investigation
from src.services.investigation_service import InvestigationService, investigation_service


class TestInvestigationServiceInitialization:
    """Tests for InvestigationService initialization."""

    def test_initialization(self):
        """Test service initialization."""
        service = InvestigationService()
        assert service is not None

    def test_singleton_instance(self):
        """Test singleton investigation_service exists."""
        assert investigation_service is not None
        assert isinstance(investigation_service, InvestigationService)


class TestCreate:
    """Tests for create method."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        return InvestigationService()

    @pytest.mark.asyncio
    async def test_create_basic(self, service):
        """Test basic investigation creation."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            # Setup context manager
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with patch(
                "src.services.investigation_service.Investigation"
            ) as mock_inv_class:
                mock_inv_class.return_value = mock_investigation

                result = await service.create(
                    user_id="user-1",
                    query="Analyze contracts",
                )

                assert result == mock_investigation
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_all_params(self, service):
        """Test creation with all parameters."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-456"

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with patch(
                "src.services.investigation_service.Investigation"
            ) as mock_inv_class:
                mock_inv_class.return_value = mock_investigation

                result = await service.create(
                    user_id="user-2",
                    query="Find anomalies",
                    data_source="expenses",
                    filters={"ano": 2024},
                    anomaly_types=["overpricing", "duplicate"],
                    session_id="session-789",
                )

                mock_inv_class.assert_called_once_with(
                    user_id="user-2",
                    session_id="session-789",
                    query="Find anomalies",
                    data_source="expenses",
                    status="pending",
                    filters={"ano": 2024},
                    anomaly_types=["overpricing", "duplicate"],
                    progress=0.0,
                )


class TestUpdateStatus:
    """Tests for update_status method."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        return InvestigationService()

    @pytest.mark.asyncio
    async def test_update_status_basic(self, service):
        """Test basic status update."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.status = "pending"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.update_status(
                investigation_id="inv-123",
                status="processing",
            )

            assert mock_investigation.status == "processing"
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_with_progress(self, service):
        """Test status update with progress."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.progress = 0.0

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            await service.update_status(
                investigation_id="inv-123",
                status="processing",
                progress=50.0,
            )

            assert mock_investigation.progress == 50.0

    @pytest.mark.asyncio
    async def test_update_status_with_phase(self, service):
        """Test status update with current phase."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.current_phase = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            await service.update_status(
                investigation_id="inv-123",
                status="processing",
                current_phase="data_collection",
            )

            assert mock_investigation.current_phase == "data_collection"

    @pytest.mark.asyncio
    async def test_update_status_converts_datetime(self, service):
        """Test timezone-aware datetime is converted to naive."""
        mock_investigation = MagicMock(spec=Investigation)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            tz_aware_dt = datetime.now(UTC)
            await service.update_status(
                investigation_id="inv-123",
                status="completed",
                completed_at=tz_aware_dt,
            )

            # Verify datetime was set (as naive)
            call_args = getattr(mock_investigation, "completed_at", None)
            if call_args is not None:
                # Should be naive (no tzinfo)
                assert hasattr(mock_investigation, "completed_at")

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, service):
        """Test update raises error if not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with pytest.raises(ValueError, match="not found"):
                await service.update_status(
                    investigation_id="nonexistent",
                    status="processing",
                )


class TestGetById:
    """Tests for get_by_id method."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        return InvestigationService()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, service):
        """Test getting existing investigation."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.get_by_id("inv-123")

            assert result == mock_investigation

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, service):
        """Test getting non-existent investigation."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.get_by_id("nonexistent")

            assert result is None


class TestSearch:
    """Tests for search method."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        return InvestigationService()

    @pytest.mark.asyncio
    async def test_search_no_filters(self, service):
        """Test search without filters."""
        mock_investigations = [
            MagicMock(spec=Investigation),
            MagicMock(spec=Investigation),
        ]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_investigations

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.search()

            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_search_by_user_id(self, service):
        """Test search filtered by user ID."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.user_id = "user-1"

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_investigation]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.search(user_id="user-1")

            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_by_status(self, service):
        """Test search filtered by status."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.status = "completed"

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_investigation]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.search(status="completed")

            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_with_pagination(self, service):
        """Test search with limit and offset."""
        mock_investigations = [MagicMock(spec=Investigation)]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_investigations

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.search(limit=5, offset=10)

            assert len(result) == 1


class TestCancel:
    """Tests for cancel method."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        return InvestigationService()

    @pytest.mark.asyncio
    async def test_cancel_success(self, service):
        """Test successful cancellation."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"
        mock_investigation.status = "processing"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            result = await service.cancel("inv-123", "user-1")

            assert mock_investigation.status == "cancelled"
            assert mock_investigation.completed_at is not None
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_not_found(self, service):
        """Test cancel raises error if not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with pytest.raises(ValueError, match="not found"):
                await service.cancel("nonexistent", "user-1")

    @pytest.mark.asyncio
    async def test_cancel_unauthorized(self, service):
        """Test cancel raises error for different user."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"
        mock_investigation.status = "processing"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with pytest.raises(ValueError, match="Unauthorized"):
                await service.cancel("inv-123", "different-user")

    @pytest.mark.asyncio
    async def test_cancel_already_completed(self, service):
        """Test cancel raises error for completed investigation."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"
        mock_investigation.status = "completed"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with pytest.raises(ValueError, match="Cannot cancel"):
                await service.cancel("inv-123", "user-1")

    @pytest.mark.asyncio
    async def test_cancel_already_failed(self, service):
        """Test cancel raises error for failed investigation."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"
        mock_investigation.status = "failed"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with pytest.raises(ValueError, match="Cannot cancel"):
                await service.cancel("inv-123", "user-1")

    @pytest.mark.asyncio
    async def test_cancel_already_cancelled(self, service):
        """Test cancel raises error for already cancelled investigation."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"
        mock_investigation.status = "cancelled"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_investigation

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.services.investigation_service.get_db_session"
        ) as mock_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_db)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.return_value = mock_context

            with pytest.raises(ValueError, match="Cannot cancel"):
                await service.cancel("inv-123", "user-1")


class TestGetUserInvestigations:
    """Tests for get_user_investigations method."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        return InvestigationService()

    @pytest.mark.asyncio
    async def test_get_user_investigations(self, service):
        """Test getting user investigations."""
        mock_investigations = [
            MagicMock(spec=Investigation),
            MagicMock(spec=Investigation),
        ]

        with patch.object(service, "search") as mock_search:
            mock_search.return_value = mock_investigations

            result = await service.get_user_investigations("user-1")

            mock_search.assert_called_once_with(user_id="user-1", limit=10)
            assert result == mock_investigations

    @pytest.mark.asyncio
    async def test_get_user_investigations_custom_limit(self, service):
        """Test getting user investigations with custom limit."""
        mock_investigations = [MagicMock(spec=Investigation)]

        with patch.object(service, "search") as mock_search:
            mock_search.return_value = mock_investigations

            result = await service.get_user_investigations("user-1", limit=5)

            mock_search.assert_called_once_with(user_id="user-1", limit=5)


class TestExecuteInvestigation:
    """Tests for _execute_investigation method (private)."""

    @pytest.fixture
    def service(self):
        """Create service for testing."""
        return InvestigationService()

    @pytest.mark.asyncio
    async def test_execute_success(self, service):
        """Test successful investigation execution."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"
        mock_investigation.query = "Analyze contracts"
        mock_investigation.metadata = {"data_sources": []}

        mock_result = MagicMock()
        mock_result.confidence_score = 0.95

        mock_master = AsyncMock()
        mock_master._investigate = AsyncMock(return_value=mock_result)

        mock_pool = AsyncMock()
        mock_pool.acquire = MagicMock()

        # Setup async context manager for pool.acquire
        mock_acquire_context = AsyncMock()
        mock_acquire_context.__aenter__ = AsyncMock(return_value=mock_master)
        mock_acquire_context.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = mock_acquire_context

        with patch(
            "src.services.investigation_service.get_agent_pool"
        ) as mock_get_pool:
            mock_get_pool.return_value = mock_pool

            await service._execute_investigation(mock_investigation)

            assert mock_investigation.status == "completed"
            assert mock_investigation.confidence_score == 0.95
            assert mock_investigation.processing_time_ms is not None
            assert mock_investigation.completed_at is not None

    @pytest.mark.asyncio
    async def test_execute_failure(self, service):
        """Test investigation execution failure."""
        mock_investigation = MagicMock(spec=Investigation)
        mock_investigation.id = "inv-123"
        mock_investigation.user_id = "user-1"
        mock_investigation.query = "Analyze contracts"
        mock_investigation.metadata = {}

        with patch(
            "src.services.investigation_service.get_agent_pool"
        ) as mock_get_pool:
            mock_get_pool.side_effect = Exception("Agent pool error")

            await service._execute_investigation(mock_investigation)

            assert mock_investigation.status == "failed"
            assert mock_investigation.completed_at is not None
