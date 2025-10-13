"""
GraphQL schema definition for Cidadão.AI API.

This module defines the GraphQL schema with types, queries, mutations,
and subscriptions for efficient data fetching.
"""

from datetime import datetime
from typing import Optional

import strawberry
from strawberry import ID
from strawberry.extensions import Extension
from strawberry.types import Info

from src.agents import get_agent_pool
from src.core import get_logger
from src.infrastructure.query_cache import cached_query
from src.services.investigation_service_selector import investigation_service

logger = get_logger(__name__)


# GraphQL Types
@strawberry.type
class User:
    """User type for GraphQL."""

    id: ID
    email: str
    name: str
    role: str
    created_at: datetime
    is_active: bool

    @strawberry.field
    async def investigations(
        self, info: Info, limit: int = 10
    ) -> list["Investigation"]:
        """Get user's investigations."""
        # This would fetch from database
        return []


@strawberry.type
class Investigation:
    """Investigation type for GraphQL."""

    id: ID
    user_id: ID
    query: str
    status: str
    confidence_score: float
    created_at: datetime
    completed_at: Optional[datetime]
    processing_time_ms: Optional[float]

    @strawberry.field
    async def findings(self, info: Info) -> list["Finding"]:
        """Get investigation findings."""
        return []

    @strawberry.field
    async def anomalies(self, info: Info) -> list["Anomaly"]:
        """Get detected anomalies."""
        return []

    @strawberry.field
    async def user(self, info: Info) -> Optional[User]:
        """Get investigation owner."""
        return None


@strawberry.type
class Finding:
    """Finding type for GraphQL."""

    id: ID
    investigation_id: ID
    type: str
    title: str
    description: str
    severity: str
    confidence: float
    evidence: strawberry.scalars.JSON
    created_at: datetime


@strawberry.type
class Anomaly:
    """Anomaly type for GraphQL."""

    id: ID
    investigation_id: ID
    type: str
    description: str
    severity: str
    confidence_score: float
    affected_entities: strawberry.scalars.JSON
    detection_method: str
    created_at: datetime


@strawberry.type
class Contract:
    """Contract type for GraphQL."""

    id: ID
    numero: str
    objeto: str
    valor: float
    fornecedor: strawberry.scalars.JSON
    orgao: str
    data_assinatura: datetime
    vigencia: strawberry.scalars.JSON

    @strawberry.field
    async def anomalies(self, info: Info) -> list[Anomaly]:
        """Get contract anomalies."""
        return []


@strawberry.type
class ChatMessage:
    """Chat message type."""

    id: ID
    session_id: str
    role: str
    content: str
    agent_name: Optional[str]
    created_at: datetime


@strawberry.type
class AgentStats:
    """Agent statistics type."""

    agent_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    avg_response_time_ms: float
    last_active: datetime


# Input Types
@strawberry.input
class InvestigationInput:
    """Input for creating investigations."""

    query: str
    data_sources: Optional[list[str]] = None
    priority: Optional[str] = "medium"
    context: Optional[strawberry.scalars.JSON] = None


@strawberry.input
class ChatInput:
    """Input for chat messages."""

    message: str
    session_id: Optional[str] = None
    context: Optional[strawberry.scalars.JSON] = None


@strawberry.input
class SearchFilter:
    """Generic search filter."""

    field: str
    operator: str  # eq, ne, gt, lt, contains, in
    value: strawberry.scalars.JSON


@strawberry.input
class PaginationInput:
    """Pagination parameters."""

    limit: int = 20
    offset: int = 0
    order_by: Optional[str] = None
    order_dir: Optional[str] = "desc"


# Query Root
@strawberry.type
class Query:
    """Root query type."""

    @strawberry.field
    async def me(self, info: Info) -> Optional[User]:
        """Get current user."""
        # Get from context
        user = info.context.get("user")
        if user:
            return User(
                id=str(user.id),
                email=user.email,
                name=user.name,
                role=user.role,
                created_at=user.created_at,
                is_active=user.is_active,
            )
        return None

    @strawberry.field
    @cached_query(ttl=300)
    async def investigation(self, info: Info, id: ID) -> Optional[Investigation]:
        """Get investigation by ID."""
        # Fetch from service
        investigation = await investigation_service.get_by_id(id)
        if investigation:
            return Investigation(
                id=str(investigation.id),
                user_id=str(investigation.user_id),
                query=investigation.query,
                status=investigation.status,
                confidence_score=investigation.confidence_score,
                created_at=investigation.created_at,
                completed_at=investigation.completed_at,
                processing_time_ms=investigation.processing_time_ms,
            )
        return None

    @strawberry.field
    async def investigations(
        self,
        info: Info,
        filters: Optional[list[SearchFilter]] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> list[Investigation]:
        """Search investigations with filters."""
        # Default pagination
        if not pagination:
            pagination = PaginationInput()

        # Apply filters and fetch
        results = await investigation_service.search(
            filters=filters,
            limit=pagination.limit,
            offset=pagination.offset,
            order_by=pagination.order_by,
            order_dir=pagination.order_dir,
        )

        return [
            Investigation(
                id=str(r.id),
                user_id=str(r.user_id),
                query=r.query,
                status=r.status,
                confidence_score=r.confidence_score,
                created_at=r.created_at,
                completed_at=r.completed_at,
                processing_time_ms=r.processing_time_ms,
            )
            for r in results
        ]

    @strawberry.field
    async def contracts(
        self,
        info: Info,
        search: Optional[str] = None,
        orgao: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> list[Contract]:
        """Search contracts."""
        # Implementation would fetch from database
        return []

    @strawberry.field
    async def agent_stats(self, info: Info) -> list[AgentStats]:
        """Get agent performance statistics."""
        pool = await get_agent_pool()
        stats = pool.get_stats()

        agent_stats = []
        for agent_name, agent_data in stats["pools"].items():
            agent_stats.append(
                AgentStats(
                    agent_name=agent_name,
                    total_tasks=agent_data["avg_usage"] * agent_data["total"],
                    successful_tasks=int(
                        agent_data["avg_usage"] * agent_data["total"] * 0.95
                    ),
                    failed_tasks=int(
                        agent_data["avg_usage"] * agent_data["total"] * 0.05
                    ),
                    avg_response_time_ms=500.0,  # Placeholder
                    last_active=datetime.utcnow(),
                )
            )

        return agent_stats


# Mutation Root
@strawberry.type
class Mutation:
    """Root mutation type."""

    @strawberry.mutation
    async def create_investigation(
        self, info: Info, input: InvestigationInput
    ) -> Investigation:
        """Create a new investigation."""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        # Create investigation
        investigation = await investigation_service.create(
            user_id=user.id,
            query=input.query,
            data_sources=input.data_sources,
            priority=input.priority,
            context=input.context,
        )

        return Investigation(
            id=str(investigation.id),
            user_id=str(investigation.user_id),
            query=investigation.query,
            status=investigation.status,
            confidence_score=0.0,
            created_at=investigation.created_at,
            completed_at=None,
            processing_time_ms=None,
        )

    @strawberry.mutation
    async def send_chat_message(self, info: Info, input: ChatInput) -> ChatMessage:
        """Send a chat message."""
        user = info.context.get("user")

        # Process through chat service
        from src.services.chat_service_with_cache import chat_service

        session = await chat_service.get_or_create_session(
            session_id=input.session_id, user_id=user.id if user else None
        )

        response = await chat_service.process_message(
            session_id=session.id,
            message=input.message,
            user_id=user.id if user else None,
        )

        return ChatMessage(
            id=str(response.id),
            session_id=session.id,
            role="assistant",
            content=response.message,
            agent_name=response.agent_name,
            created_at=datetime.utcnow(),
        )

    @strawberry.mutation
    async def cancel_investigation(self, info: Info, id: ID) -> Investigation:
        """Cancel an ongoing investigation."""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        # Cancel investigation
        investigation = await investigation_service.cancel(id, user.id)

        return Investigation(
            id=str(investigation.id),
            user_id=str(investigation.user_id),
            query=investigation.query,
            status="cancelled",
            confidence_score=investigation.confidence_score,
            created_at=investigation.created_at,
            completed_at=datetime.utcnow(),
            processing_time_ms=investigation.processing_time_ms,
        )


# Subscription Root
@strawberry.type
class Subscription:
    """Root subscription type."""

    @strawberry.subscription
    async def investigation_updates(
        self, info: Info, investigation_id: ID
    ) -> Investigation:
        """Subscribe to investigation updates."""
        # This would use websockets or SSE
        # Simplified implementation
        import asyncio

        while True:
            await asyncio.sleep(2)

            # Fetch current state
            investigation = await investigation_service.get_by_id(investigation_id)
            if investigation:
                yield Investigation(
                    id=str(investigation.id),
                    user_id=str(investigation.user_id),
                    query=investigation.query,
                    status=investigation.status,
                    confidence_score=investigation.confidence_score,
                    created_at=investigation.created_at,
                    completed_at=investigation.completed_at,
                    processing_time_ms=investigation.processing_time_ms,
                )

                if investigation.status in ["completed", "failed", "cancelled"]:
                    break

    @strawberry.subscription
    async def agent_activity(self, info: Info) -> AgentStats:
        """Subscribe to real-time agent activity."""
        import asyncio

        while True:
            await asyncio.sleep(5)

            pool = await get_agent_pool()
            stats = pool.get_stats()

            # Yield stats for each agent
            for agent_name, agent_data in stats["pools"].items():
                yield AgentStats(
                    agent_name=agent_name,
                    total_tasks=agent_data["avg_usage"] * agent_data["total"],
                    successful_tasks=int(
                        agent_data["avg_usage"] * agent_data["total"] * 0.95
                    ),
                    failed_tasks=int(
                        agent_data["avg_usage"] * agent_data["total"] * 0.05
                    ),
                    avg_response_time_ms=500.0,
                    last_active=datetime.utcnow(),
                )


# Performance monitoring extension
class PerformanceExtension(Extension):
    """Track GraphQL query performance."""

    async def on_request_start(self):
        self.start_time = datetime.utcnow()

    async def on_request_end(self):
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        logger.info(f"GraphQL request completed in {duration:.2f}ms")


# Create schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[PerformanceExtension],
)
