"""Event-driven architecture for Cidadão.AI."""

from .event_bus import (
    EventType,
    Event,
    EventHandler,
    EventBus,
    LoggingEventHandler,
    InvestigationEventHandler,
    get_event_bus
)

__all__ = [
    "EventType",
    "Event",
    "EventHandler",
    "EventBus",
    "LoggingEventHandler",
    "InvestigationEventHandler",
    "get_event_bus"
]