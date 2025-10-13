"""
Cursor-based pagination models for efficient data retrieval.

This module implements cursor pagination which is more efficient
than offset pagination for large datasets and real-time data.
"""

import base64
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from src.core import get_logger, json_utils

logger = get_logger(__name__)

T = TypeVar("T")


class CursorInfo(BaseModel):
    """Information encoded in a cursor."""

    timestamp: datetime
    id: str
    direction: str = "next"

    def encode(self) -> str:
        """Encode cursor info to base64 string."""
        data = {"t": self.timestamp.isoformat(), "i": self.id, "d": self.direction}
        json_str = json_utils.dumps(data, separators=(",", ":"))
        return base64.urlsafe_b64encode(json_str.encode()).decode()

    @classmethod
    def decode(cls, cursor: str) -> "CursorInfo":
        """Decode cursor from base64 string."""
        try:
            json_str = base64.urlsafe_b64decode(cursor).decode()
            data = json_utils.loads(json_str)
            return cls(
                timestamp=datetime.fromisoformat(data["t"]),
                id=data["i"],
                direction=data.get("d", "next"),
            )
        except Exception as e:
            logger.error(f"Invalid cursor: {e}")
            raise ValueError("Invalid cursor format")


class CursorPaginationRequest(BaseModel):
    """Request parameters for cursor pagination."""

    cursor: Optional[str] = Field(None, description="Cursor for next/previous page")
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")
    direction: str = Field(
        "next", pattern="^(next|prev)$", description="Pagination direction"
    )


class CursorPaginationResponse(BaseModel, Generic[T]):
    """Response with cursor pagination metadata."""

    items: list[T]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_more: bool = False
    total_items: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PaginationHelper:
    """Helper class for cursor-based pagination."""

    @staticmethod
    def create_cursor(item: dict[str, Any], direction: str = "next") -> str:
        """Create cursor from an item."""
        cursor_info = CursorInfo(
            timestamp=item.get("timestamp", datetime.utcnow()),
            id=str(item.get("id", "")),
            direction=direction,
        )
        return cursor_info.encode()

    @staticmethod
    def parse_cursor(cursor: Optional[str]) -> Optional[CursorInfo]:
        """Parse cursor string to CursorInfo."""
        if not cursor:
            return None
        return CursorInfo.decode(cursor)

    @staticmethod
    def paginate_list(
        items: list[dict[str, Any]],
        request: CursorPaginationRequest,
        key_field: str = "timestamp",
        id_field: str = "id",
    ) -> CursorPaginationResponse[dict[str, Any]]:
        """
        Paginate a list of items using cursor pagination.

        Args:
            items: List of items to paginate (should be sorted)
            request: Pagination request parameters
            key_field: Field to use for cursor comparison
            id_field: Unique identifier field

        Returns:
            Paginated response with cursors
        """
        # Parse cursor if provided
        cursor_info = PaginationHelper.parse_cursor(request.cursor)

        # Filter items based on cursor
        if cursor_info:
            if request.direction == "next":
                # Get items after cursor
                filtered_items = [
                    item
                    for item in items
                    if item.get(key_field) > cursor_info.timestamp
                    or (
                        item.get(key_field) == cursor_info.timestamp
                        and str(item.get(id_field)) > cursor_info.id
                    )
                ]
            else:  # prev
                # Get items before cursor (reverse order)
                filtered_items = [
                    item
                    for item in reversed(items)
                    if item.get(key_field) < cursor_info.timestamp
                    or (
                        item.get(key_field) == cursor_info.timestamp
                        and str(item.get(id_field)) < cursor_info.id
                    )
                ]
                filtered_items = list(reversed(filtered_items))
        else:
            filtered_items = items

        # Apply limit
        page_items = filtered_items[: request.limit]
        has_more = len(filtered_items) > request.limit

        # Generate cursors
        next_cursor = None
        prev_cursor = None

        if page_items:
            # Next cursor from last item
            if has_more or cursor_info:
                next_cursor = PaginationHelper.create_cursor(page_items[-1], "next")

            # Previous cursor from first item
            if cursor_info or (not cursor_info and request.direction == "prev"):
                prev_cursor = PaginationHelper.create_cursor(page_items[0], "prev")

        return CursorPaginationResponse(
            items=page_items,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            has_more=has_more,
            total_items=len(items),
            metadata={"page_size": len(page_items), "direction": request.direction},
        )


class ChatMessagePagination:
    """Specialized pagination for chat messages."""

    @staticmethod
    def paginate_messages(
        messages: list[dict[str, Any]],
        cursor: Optional[str] = None,
        limit: int = 50,
        direction: str = "prev",  # Default to loading older messages
    ) -> CursorPaginationResponse[dict[str, Any]]:
        """
        Paginate chat messages with cursor.

        Chat typically loads older messages, so default direction is "prev".
        """
        request = CursorPaginationRequest(
            cursor=cursor, limit=limit, direction=direction
        )

        # Sort messages by timestamp
        sorted_messages = sorted(
            messages, key=lambda m: m.get("timestamp", datetime.min)
        )

        response = PaginationHelper.paginate_list(
            sorted_messages, request, key_field="timestamp", id_field="id"
        )

        # Add chat-specific metadata
        response.metadata.update(
            {
                "oldest_message": (
                    sorted_messages[0].get("timestamp") if sorted_messages else None
                ),
                "newest_message": (
                    sorted_messages[-1].get("timestamp") if sorted_messages else None
                ),
                "unread_count": sum(1 for m in messages if not m.get("read", True)),
            }
        )

        return response
