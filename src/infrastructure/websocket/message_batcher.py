"""
WebSocket message batching for improved performance.

This module implements message batching to reduce WebSocket overhead
by combining multiple messages before sending.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from src.core import get_logger
from src.core.json_utils import dumps

logger = get_logger(__name__)


@dataclass
class BatchedMessage:
    """A message waiting to be sent."""

    connection_id: str
    message: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: int = 0  # Higher priority = sent sooner


class MessageBatcher:
    """
    WebSocket message batcher for improved performance.

    Features:
    - Batches messages to reduce overhead
    - Priority-based message ordering
    - Automatic flush on size/time thresholds
    - Per-connection batching
    - Compression support
    """

    def __init__(
        self,
        batch_size: int = 10,
        batch_interval_ms: int = 50,
        max_batch_bytes: int = 64 * 1024,  # 64KB
        enable_compression: bool = True,
    ):
        """
        Initialize message batcher.

        Args:
            batch_size: Maximum messages per batch
            batch_interval_ms: Maximum time to wait before sending
            max_batch_bytes: Maximum batch size in bytes
            enable_compression: Enable message compression
        """
        self.batch_size = batch_size
        self.batch_interval_ms = batch_interval_ms
        self.max_batch_bytes = max_batch_bytes
        self.enable_compression = enable_compression

        # Message queues per connection
        self._queues: dict[str, list[BatchedMessage]] = {}

        # Active connections
        self._connections: dict[str, Any] = {}

        # Flush tasks
        self._flush_tasks: dict[str, asyncio.Task] = {}

        # Statistics
        self._stats = {
            "messages_queued": 0,
            "messages_sent": 0,
            "batches_sent": 0,
            "bytes_sent": 0,
            "compression_ratio": 0.0,
        }

        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def register_connection(self, connection_id: str, websocket: Any):
        """
        Register a WebSocket connection.

        Args:
            connection_id: Unique connection ID
            websocket: WebSocket connection object
        """
        async with self._lock:
            self._connections[connection_id] = websocket
            self._queues[connection_id] = []

            logger.info(f"Registered WebSocket connection: {connection_id}")

    async def unregister_connection(self, connection_id: str):
        """
        Unregister a WebSocket connection.

        Args:
            connection_id: Connection ID to remove
        """
        async with self._lock:
            # Cancel flush task if exists
            if connection_id in self._flush_tasks:
                self._flush_tasks[connection_id].cancel()
                del self._flush_tasks[connection_id]

            # Clear queue
            if connection_id in self._queues:
                del self._queues[connection_id]

            # Remove connection
            if connection_id in self._connections:
                del self._connections[connection_id]

            logger.info(f"Unregistered WebSocket connection: {connection_id}")

    async def queue_message(
        self, connection_id: str, message: dict[str, Any], priority: int = 0
    ):
        """
        Queue a message for batched sending.

        Args:
            connection_id: Target connection
            message: Message to send
            priority: Message priority (higher = sent sooner)
        """
        async with self._lock:
            if connection_id not in self._connections:
                logger.warning(f"Connection {connection_id} not registered")
                return

            # Add message to queue
            batched_msg = BatchedMessage(
                connection_id=connection_id, message=message, priority=priority
            )

            self._queues[connection_id].append(batched_msg)
            self._stats["messages_queued"] += 1

            # Check if we should flush immediately
            should_flush = await self._should_flush(connection_id)

            if should_flush:
                await self._flush_connection(connection_id)
            elif connection_id not in self._flush_tasks:
                # Schedule flush task
                self._flush_tasks[connection_id] = asyncio.create_task(
                    self._scheduled_flush(connection_id)
                )

    async def broadcast_message(
        self,
        message: dict[str, Any],
        connection_ids: Optional[set[str]] = None,
        priority: int = 0,
    ):
        """
        Broadcast a message to multiple connections.

        Args:
            message: Message to broadcast
            connection_ids: Target connections (all if None)
            priority: Message priority
        """
        if connection_ids is None:
            connection_ids = set(self._connections.keys())

        # Queue for each connection
        for conn_id in connection_ids:
            await self.queue_message(conn_id, message, priority)

    async def flush_all(self):
        """Force flush all pending messages."""
        async with self._lock:
            for connection_id in list(self._connections.keys()):
                await self._flush_connection(connection_id)

    async def _should_flush(self, connection_id: str) -> bool:
        """Check if we should flush messages for a connection."""
        queue = self._queues.get(connection_id, [])

        if not queue:
            return False

        # Check batch size
        if len(queue) >= self.batch_size:
            return True

        # Check message age
        oldest_msg = queue[0]
        age_ms = (time.time() - oldest_msg.timestamp) * 1000
        if age_ms >= self.batch_interval_ms:
            return True

        # Check batch byte size
        batch_size = sum(len(dumps(msg.message)) for msg in queue)
        if batch_size >= self.max_batch_bytes:
            return True

        # Check for high priority messages
        if any(msg.priority > 5 for msg in queue):
            return True

        return False

    async def _scheduled_flush(self, connection_id: str):
        """Scheduled flush task for a connection."""
        try:
            await asyncio.sleep(self.batch_interval_ms / 1000.0)
            async with self._lock:
                await self._flush_connection(connection_id)
        except asyncio.CancelledError:
            pass
        finally:
            async with self._lock:
                if connection_id in self._flush_tasks:
                    del self._flush_tasks[connection_id]

    async def _flush_connection(self, connection_id: str):
        """
        Flush pending messages for a connection.

        Note: Must be called with lock held.
        """
        queue = self._queues.get(connection_id, [])
        if not queue:
            return

        websocket = self._connections.get(connection_id)
        if not websocket:
            return

        try:
            # Sort by priority (descending) and timestamp (ascending)
            queue.sort(key=lambda m: (-m.priority, m.timestamp))

            # Take batch
            batch = queue[: self.batch_size]
            self._queues[connection_id] = queue[self.batch_size :]

            # Create batch message
            batch_data = {
                "type": "batch",
                "timestamp": datetime.utcnow().isoformat(),
                "messages": [msg.message for msg in batch],
                "count": len(batch),
            }

            # Serialize
            message_str = dumps(batch_data)
            message_bytes = message_str.encode("utf-8")

            # Compress if enabled
            if self.enable_compression and len(message_bytes) > 1024:
                import gzip

                compressed = gzip.compress(message_bytes)

                if len(compressed) < len(message_bytes):
                    # Send compressed
                    await websocket.send_bytes(compressed)

                    # Update stats
                    self._stats["compression_ratio"] = 1.0 - len(compressed) / len(
                        message_bytes
                    )
                else:
                    # Send uncompressed
                    await websocket.send_text(message_str)
            else:
                # Send uncompressed
                await websocket.send_text(message_str)

            # Update statistics
            self._stats["messages_sent"] += len(batch)
            self._stats["batches_sent"] += 1
            self._stats["bytes_sent"] += len(message_bytes)

            logger.debug(f"Sent batch of {len(batch)} messages to {connection_id}")

        except Exception as e:
            logger.error(f"Failed to flush messages for {connection_id}: {e}")

            # Put messages back in queue
            self._queues[connection_id] = batch + self._queues[connection_id]

    def get_stats(self) -> dict[str, Any]:
        """Get batcher statistics."""
        return {
            **self._stats,
            "active_connections": len(self._connections),
            "pending_messages": sum(len(queue) for queue in self._queues.values()),
            "avg_batch_size": (
                self._stats["messages_sent"] / self._stats["batches_sent"]
                if self._stats["batches_sent"] > 0
                else 0
            ),
        }


class WebSocketManager:
    """
    Enhanced WebSocket manager with message batching.

    Manages WebSocket connections and provides batched messaging.
    """

    def __init__(
        self,
        batch_size: int = 10,
        batch_interval_ms: int = 50,
        enable_compression: bool = True,
    ):
        """
        Initialize WebSocket manager.

        Args:
            batch_size: Maximum messages per batch
            batch_interval_ms: Maximum time to wait before sending
            enable_compression: Enable message compression
        """
        self.batcher = MessageBatcher(
            batch_size=batch_size,
            batch_interval_ms=batch_interval_ms,
            enable_compression=enable_compression,
        )

        # Room management
        self._rooms: dict[str, set[str]] = {}
        self._connection_rooms: dict[str, set[str]] = {}

    async def connect(self, connection_id: str, websocket: Any):
        """
        Connect a WebSocket client.

        Args:
            connection_id: Unique connection ID
            websocket: WebSocket connection object
        """
        await self.batcher.register_connection(connection_id, websocket)
        self._connection_rooms[connection_id] = set()

        # Send welcome message
        await self.send_message(
            connection_id,
            {
                "type": "connected",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
            priority=10,  # High priority
        )

    async def disconnect(self, connection_id: str):
        """
        Disconnect a WebSocket client.

        Args:
            connection_id: Connection to disconnect
        """
        # Leave all rooms
        if connection_id in self._connection_rooms:
            for room in list(self._connection_rooms[connection_id]):
                await self.leave_room(connection_id, room)
            del self._connection_rooms[connection_id]

        # Unregister from batcher
        await self.batcher.unregister_connection(connection_id)

    async def join_room(self, connection_id: str, room: str):
        """
        Add connection to a room.

        Args:
            connection_id: Connection ID
            room: Room name
        """
        if room not in self._rooms:
            self._rooms[room] = set()

        self._rooms[room].add(connection_id)

        if connection_id in self._connection_rooms:
            self._connection_rooms[connection_id].add(room)

        logger.info(f"Connection {connection_id} joined room {room}")

    async def leave_room(self, connection_id: str, room: str):
        """
        Remove connection from a room.

        Args:
            connection_id: Connection ID
            room: Room name
        """
        if room in self._rooms:
            self._rooms[room].discard(connection_id)

            if not self._rooms[room]:
                del self._rooms[room]

        if connection_id in self._connection_rooms:
            self._connection_rooms[connection_id].discard(room)

        logger.info(f"Connection {connection_id} left room {room}")

    async def send_message(
        self, connection_id: str, message: dict[str, Any], priority: int = 0
    ):
        """
        Send a message to a specific connection.

        Args:
            connection_id: Target connection
            message: Message to send
            priority: Message priority
        """
        await self.batcher.queue_message(connection_id, message, priority)

    async def send_to_room(
        self,
        room: str,
        message: dict[str, Any],
        exclude: Optional[set[str]] = None,
        priority: int = 0,
    ):
        """
        Send a message to all connections in a room.

        Args:
            room: Target room
            message: Message to send
            exclude: Connections to exclude
            priority: Message priority
        """
        if room not in self._rooms:
            return

        connections = self._rooms[room]
        if exclude:
            connections = connections - exclude

        await self.batcher.broadcast_message(message, connections, priority)

    async def broadcast(self, message: dict[str, Any], priority: int = 0):
        """
        Broadcast a message to all connections.

        Args:
            message: Message to broadcast
            priority: Message priority
        """
        await self.batcher.broadcast_message(message, priority=priority)

    async def flush_all(self):
        """Force flush all pending messages."""
        await self.batcher.flush_all()

    def get_stats(self) -> dict[str, Any]:
        """Get manager statistics."""
        return {
            "batcher": self.batcher.get_stats(),
            "rooms": {
                room: len(connections) for room, connections in self._rooms.items()
            },
            "total_connections": len(self._connection_rooms),
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager(
    batch_size=20, batch_interval_ms=50, enable_compression=True
)
