"""
Command handling for CQRS pattern implementation.

This module provides command definitions and handlers for write operations,
separating them from read queries for better scalability.
"""

from typing import Any, Dict, Optional, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from src.core import get_logger
from src.infrastructure.events.event_bus import EventBus, EventType, Event

logger = get_logger(__name__)

T = TypeVar('T')


class Command(BaseModel):
    """Base class for all commands."""
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CommandResult(BaseModel):
    """Result of command execution."""
    success: bool
    command_id: str
    data: Optional[Any] = None
    error: Optional[str] = None
    events_published: int = 0


# Investigation Commands
class CreateInvestigationCommand(Command):
    """Command to create a new investigation."""
    query: str
    data_sources: Optional[list[str]] = None
    priority: str = "medium"


class UpdateInvestigationCommand(Command):
    """Command to update investigation status."""
    investigation_id: str
    status: str
    results: Optional[Dict[str, Any]] = None


class CancelInvestigationCommand(Command):
    """Command to cancel an investigation."""
    investigation_id: str
    reason: Optional[str] = None


# Agent Commands
class ExecuteAgentTaskCommand(Command):
    """Command to execute an agent task."""
    agent_name: str
    task_type: str
    payload: Dict[str, Any]
    timeout: Optional[float] = None


# Chat Commands
class SendChatMessageCommand(Command):
    """Command to send a chat message."""
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class CommandHandler(ABC, Generic[T]):
    """
    Base class for command handlers.
    
    Implements the handler pattern for processing commands.
    """
    
    @abstractmethod
    async def handle(self, command: T) -> CommandResult:
        """
        Handle a command.
        
        Args:
            command: Command to handle
            
        Returns:
            Command execution result
        """
        pass
    
    @abstractmethod
    def can_handle(self, command: Command) -> bool:
        """
        Check if this handler can handle the command.
        
        Args:
            command: Command to check
            
        Returns:
            True if handler can process this command
        """
        pass


class CreateInvestigationHandler(CommandHandler[CreateInvestigationCommand]):
    """Handler for creating investigations."""
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize handler.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self.event_bus = event_bus
        self.logger = get_logger(__name__)
    
    async def handle(self, command: CreateInvestigationCommand) -> CommandResult:
        """Create a new investigation."""
        try:
            investigation_id = str(uuid.uuid4())
            
            # In a real implementation, this would:
            # 1. Validate the command
            # 2. Create the investigation in the write model
            # 3. Publish events
            
            # Publish investigation created event
            await self.event_bus.publish(
                EventType.INVESTIGATION_CREATED,
                {
                    "investigation_id": investigation_id,
                    "query": command.query,
                    "user_id": command.user_id,
                    "data_sources": command.data_sources,
                    "priority": command.priority
                },
                {"command_id": command.command_id}
            )
            
            self.logger.info(f"Investigation {investigation_id} created")
            
            return CommandResult(
                success=True,
                command_id=command.command_id,
                data={"investigation_id": investigation_id},
                events_published=1
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create investigation: {e}")
            return CommandResult(
                success=False,
                command_id=command.command_id,
                error=str(e)
            )
    
    def can_handle(self, command: Command) -> bool:
        """Check if this handler can handle the command."""
        return isinstance(command, CreateInvestigationCommand)


class CommandBus:
    """
    Command bus for routing commands to appropriate handlers.
    
    Implements the mediator pattern for command processing.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize command bus.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self.event_bus = event_bus
        self._handlers: list[CommandHandler] = []
        self._middleware: list[CommandMiddleware] = []
        
        # Statistics
        self._stats = {
            "commands_processed": 0,
            "commands_succeeded": 0,
            "commands_failed": 0
        }
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default command handlers."""
        self.register_handler(CreateInvestigationHandler(self.event_bus))
    
    def register_handler(self, handler: CommandHandler):
        """
        Register a command handler.
        
        Args:
            handler: Handler to register
        """
        self._handlers.append(handler)
        logger.info(f"Registered command handler: {handler.__class__.__name__}")
    
    def register_middleware(self, middleware: 'CommandMiddleware'):
        """
        Register command middleware.
        
        Args:
            middleware: Middleware to register
        """
        self._middleware.append(middleware)
        logger.info(f"Registered command middleware: {middleware.__class__.__name__}")
    
    async def execute(self, command: Command) -> CommandResult:
        """
        Execute a command.
        
        Args:
            command: Command to execute
            
        Returns:
            Command execution result
        """
        self._stats["commands_processed"] += 1
        
        try:
            # Apply middleware
            for middleware in self._middleware:
                command = await middleware.before_execute(command)
            
            # Find handler
            handler = None
            for h in self._handlers:
                if h.can_handle(command):
                    handler = h
                    break
            
            if not handler:
                raise ValueError(f"No handler found for command: {type(command).__name__}")
            
            # Execute command
            result = await handler.handle(command)
            
            # Apply middleware to result
            for middleware in reversed(self._middleware):
                result = await middleware.after_execute(command, result)
            
            if result.success:
                self._stats["commands_succeeded"] += 1
            else:
                self._stats["commands_failed"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            self._stats["commands_failed"] += 1
            
            return CommandResult(
                success=False,
                command_id=command.command_id,
                error=str(e)
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get command bus statistics."""
        return {
            **self._stats,
            "handlers_registered": len(self._handlers),
            "middleware_registered": len(self._middleware),
            "success_rate": (
                self._stats["commands_succeeded"] / self._stats["commands_processed"]
                if self._stats["commands_processed"] > 0 else 0
            )
        }


class CommandMiddleware(ABC):
    """Base class for command middleware."""
    
    @abstractmethod
    async def before_execute(self, command: Command) -> Command:
        """
        Process command before execution.
        
        Args:
            command: Command to process
            
        Returns:
            Processed command
        """
        pass
    
    @abstractmethod
    async def after_execute(
        self,
        command: Command,
        result: CommandResult
    ) -> CommandResult:
        """
        Process result after execution.
        
        Args:
            command: Executed command
            result: Execution result
            
        Returns:
            Processed result
        """
        pass


class LoggingMiddleware(CommandMiddleware):
    """Middleware for logging commands."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def before_execute(self, command: Command) -> Command:
        """Log command execution."""
        self.logger.info(
            f"Executing command {command.__class__.__name__} "
            f"(id: {command.command_id})"
        )
        return command
    
    async def after_execute(
        self,
        command: Command,
        result: CommandResult
    ) -> CommandResult:
        """Log command result."""
        if result.success:
            self.logger.info(
                f"Command {command.command_id} succeeded "
                f"(events: {result.events_published})"
            )
        else:
            self.logger.error(
                f"Command {command.command_id} failed: {result.error}"
            )
        return result


class ValidationMiddleware(CommandMiddleware):
    """Middleware for validating commands."""
    
    async def before_execute(self, command: Command) -> Command:
        """Validate command."""
        # Perform validation
        if hasattr(command, 'validate'):
            command.validate()
        return command
    
    async def after_execute(
        self,
        command: Command,
        result: CommandResult
    ) -> CommandResult:
        """No post-processing needed."""
        return result