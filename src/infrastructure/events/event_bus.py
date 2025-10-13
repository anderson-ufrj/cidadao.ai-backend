"""
Event bus implementation using Redis Streams.

This module provides a distributed event bus for decoupling
components and enabling async processing.
"""

import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import redis.asyncio as redis

from src.core import get_logger, settings
from src.core.json_utils import dumps, loads

logger = get_logger(__name__)


class EventType(str, Enum):
    """System event types."""

    # Investigation events
    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_STARTED = "investigation.started"
    INVESTIGATION_COMPLETED = "investigation.completed"
    INVESTIGATION_FAILED = "investigation.failed"

    # Agent events
    AGENT_TASK_STARTED = "agent.task.started"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"

    # Anomaly events
    ANOMALY_DETECTED = "anomaly.detected"
    ANOMALY_CONFIRMED = "anomaly.confirmed"
    ANOMALY_RESOLVED = "anomaly.resolved"

    # Chat events
    CHAT_MESSAGE_RECEIVED = "chat.message.received"
    CHAT_RESPONSE_SENT = "chat.response.sent"

    # System events
    SYSTEM_HEALTH_CHECK = "system.health.check"
    SYSTEM_METRIC_RECORDED = "system.metric.recorded"
    CACHE_INVALIDATED = "cache.invalidated"


@dataclass
class Event:
    """Base event class."""

    id: str
    type: EventType
    timestamp: datetime
    data: dict[str, Any]
    metadata: dict[str, Any]

    @classmethod
    def create(
        cls,
        event_type: EventType,
        data: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Event":
        """Create a new event."""
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
        }


class EventHandler:
    """Base class for event handlers."""

    def __init__(self, event_types: list[EventType]):
        """
        Initialize event handler.

        Args:
            event_types: List of event types to handle
        """
        self.event_types = event_types
        self.logger = get_logger(self.__class__.__name__)

    async def handle(self, event: Event) -> Any:
        """
        Handle an event.

        Args:
            event: Event to handle

        Returns:
            Handler result
        """
        raise NotImplementedError("Subclasses must implement handle()")

    async def on_error(self, event: Event, error: Exception):
        """Called when handler fails."""
        self.logger.error(f"Handler error for event {event.id}: {error}")


class EventBus:
    """
    Distributed event bus using Redis Streams.

    Features:
    - Publish/Subscribe with Redis Streams
    - Event persistence and replay
    - Consumer groups for scaling
    - Dead letter queue for failed events
    - Event filtering and routing
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        stream_prefix: str = "events",
        consumer_group: str = "cidadao-ai",
        max_retries: int = 3,
    ):
        """
        Initialize event bus.

        Args:
            redis_client: Redis async client
            stream_prefix: Prefix for stream names
            consumer_group: Consumer group name
            max_retries: Maximum retries for failed events
        """
        self.redis = redis_client
        self.stream_prefix = stream_prefix
        self.consumer_group = consumer_group
        self.max_retries = max_retries

        # Handlers registry
        self._handlers: dict[EventType, list[EventHandler]] = {}

        # Active consumers
        self._consumers: list[asyncio.Task] = []
        self._running = False

        # Statistics
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "events_retried": 0,
        }

    def _get_stream_name(self, event_type: EventType) -> str:
        """Get Redis stream name for event type."""
        # Group events by category
        category = event_type.value.split(".")[0]
        return f"{self.stream_prefix}:{category}"

    async def publish(
        self,
        event_type: EventType,
        data: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Publish an event to the bus.

        Args:
            event_type: Type of event
            data: Event data
            metadata: Optional metadata

        Returns:
            Event ID
        """
        event = Event.create(event_type, data, metadata)
        stream_name = self._get_stream_name(event_type)

        # Add to Redis stream
        event_id = await self.redis.xadd(
            stream_name,
            {
                "event": dumps(event.to_dict()),
                "type": event_type.value,
                "timestamp": event.timestamp.isoformat(),
            },
            maxlen=10000,  # Keep last 10k events per stream
        )

        self._stats["events_published"] += 1

        logger.debug(
            f"Published event {event.id} of type {event_type} to {stream_name}"
        )

        return event.id

    def register_handler(
        self, handler: EventHandler, event_types: Optional[list[EventType]] = None
    ):
        """
        Register an event handler.

        Args:
            handler: Event handler instance
            event_types: Event types to handle (uses handler's types if not provided)
        """
        types_to_register = event_types or handler.event_types

        for event_type in types_to_register:
            if event_type not in self._handlers:
                self._handlers[event_type] = []

            self._handlers[event_type].append(handler)
            logger.info(
                f"Registered handler {handler.__class__.__name__} for {event_type}"
            )

    async def start(self, consumer_name: Optional[str] = None):
        """
        Start consuming events.

        Args:
            consumer_name: Unique consumer name (auto-generated if not provided)
        """
        if self._running:
            logger.warning("Event bus already running")
            return

        self._running = True
        consumer_name = consumer_name or f"consumer-{uuid.uuid4().hex[:8]}"

        # Create consumer groups
        stream_categories = set(
            event_type.value.split(".")[0] for event_type in self._handlers.keys()
        )

        for category in stream_categories:
            stream_name = f"{self.stream_prefix}:{category}"

            try:
                await self.redis.xgroup_create(stream_name, self.consumer_group, id="0")
                logger.info(
                    f"Created consumer group {self.consumer_group} for {stream_name}"
                )
            except redis.ResponseError:
                # Group already exists
                pass

            # Start consumer for this stream
            consumer_task = asyncio.create_task(
                self._consume_stream(stream_name, consumer_name)
            )
            self._consumers.append(consumer_task)

        logger.info(f"Event bus started with {len(self._consumers)} consumers")

    async def stop(self):
        """Stop consuming events."""
        self._running = False

        # Cancel all consumers
        for task in self._consumers:
            task.cancel()

        # Wait for cancellation
        await asyncio.gather(*self._consumers, return_exceptions=True)
        self._consumers.clear()

        logger.info("Event bus stopped")

    async def _consume_stream(self, stream_name: str, consumer_name: str):
        """Consume events from a Redis stream."""
        logger.info(f"Starting consumer for {stream_name}")

        while self._running:
            try:
                # Read messages from stream
                messages = await self.redis.xreadgroup(
                    self.consumer_group,
                    consumer_name,
                    {stream_name: ">"},
                    count=10,
                    block=1000,  # Block for 1 second
                )

                if not messages:
                    continue

                # Process messages
                for stream, stream_messages in messages:
                    for msg_id, data in stream_messages:
                        await self._process_message(
                            stream_name, msg_id, data, consumer_name
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error consuming from {stream_name}: {e}")
                await asyncio.sleep(1)

    async def _process_message(
        self, stream_name: str, msg_id: str, data: dict[str, Any], consumer_name: str
    ):
        """Process a single message from the stream."""
        try:
            # Parse event
            event_data = loads(data[b"event"])
            event_type = EventType(event_data["type"])

            event = Event(
                id=event_data["id"],
                type=event_type,
                timestamp=datetime.fromisoformat(event_data["timestamp"]),
                data=event_data["data"],
                metadata=event_data["metadata"],
            )

            # Get handlers for this event type
            handlers = self._handlers.get(event_type, [])

            if not handlers:
                logger.warning(f"No handlers for event type {event_type}")
                await self.redis.xack(stream_name, self.consumer_group, msg_id)
                return

            # Process with all handlers
            errors = []
            for handler in handlers:
                try:
                    await handler.handle(event)
                except Exception as e:
                    logger.error(f"Handler {handler.__class__.__name__} failed: {e}")
                    errors.append((handler, e))
                    await handler.on_error(event, e)

            if errors:
                # Check retry count
                retry_count = event.metadata.get("retry_count", 0)

                if retry_count < self.max_retries:
                    # Retry the event
                    event.metadata["retry_count"] = retry_count + 1
                    await self.publish(event.type, event.data, event.metadata)
                    self._stats["events_retried"] += 1
                else:
                    # Move to dead letter queue
                    await self._move_to_dlq(event, errors)
                    self._stats["events_failed"] += 1
            else:
                self._stats["events_processed"] += 1

            # Acknowledge message
            await self.redis.xack(stream_name, self.consumer_group, msg_id)

        except Exception as e:
            logger.error(f"Failed to process message {msg_id}: {e}")

    async def _move_to_dlq(self, event: Event, errors: list[tuple]):
        """Move failed event to dead letter queue."""
        dlq_stream = f"{self.stream_prefix}:dlq"

        await self.redis.xadd(
            dlq_stream,
            {
                "event": dumps(event.to_dict()),
                "errors": dumps(
                    [
                        {"handler": handler.__class__.__name__, "error": str(error)}
                        for handler, error in errors
                    ]
                ),
                "failed_at": datetime.utcnow().isoformat(),
            },
            maxlen=1000,  # Keep last 1k failed events
        )

        logger.error(f"Event {event.id} moved to DLQ after {self.max_retries} retries")

    def get_stats(self) -> dict[str, Any]:
        """Get event bus statistics."""
        return {
            **self._stats,
            "handlers_registered": sum(len(h) for h in self._handlers.values()),
            "event_types_handled": list(self._handlers.keys()),
            "consumers_active": len(self._consumers),
        }


# Example event handlers
class LoggingEventHandler(EventHandler):
    """Handler that logs all events."""

    def __init__(self):
        super().__init__([])  # Handle all events

    async def handle(self, event: Event) -> Any:
        """Log the event."""
        logger.info(f"Event received: {event.type} - {event.id}")
        return None


class InvestigationEventHandler(EventHandler):
    """Handler for investigation events."""

    def __init__(self):
        super().__init__(
            [
                EventType.INVESTIGATION_CREATED,
                EventType.INVESTIGATION_COMPLETED,
                EventType.INVESTIGATION_FAILED,
            ]
        )

    async def handle(self, event: Event) -> Any:
        """Handle investigation events."""
        if event.type == EventType.INVESTIGATION_CREATED:
            # Could trigger additional processing
            logger.info(f"New investigation: {event.data.get('query')}")

        elif event.type == EventType.INVESTIGATION_COMPLETED:
            # Could trigger notifications
            logger.info(
                f"Investigation completed: {event.data.get('investigation_id')}"
            )

        elif event.type == EventType.INVESTIGATION_FAILED:
            # Could trigger alerts
            logger.error(f"Investigation failed: {event.data.get('error')}")


# Global event bus instance
_event_bus: Optional[EventBus] = None


async def get_event_bus() -> EventBus:
    """Get or create the global event bus instance."""
    global _event_bus

    if _event_bus is None:
        # Initialize Redis client
        redis_client = redis.from_url(settings.redis_url, decode_responses=False)

        _event_bus = EventBus(redis_client)

        # Register default handlers
        _event_bus.register_handler(LoggingEventHandler())
        _event_bus.register_handler(InvestigationEventHandler())

    return _event_bus
