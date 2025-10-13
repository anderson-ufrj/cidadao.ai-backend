"""Event-driven architecture for Cidadão.AI."""

from .event_bus import (
    Event,
    EventBus,
    EventHandler,
    EventType,
    InvestigationEventHandler,
    LoggingEventHandler,
    get_event_bus,
)

__all__ = [
    "EventType",
    "Event",
    "EventHandler",
    "EventBus",
    "LoggingEventHandler",
    "InvestigationEventHandler",
    "get_event_bus",
]
