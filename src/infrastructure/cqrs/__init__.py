"""CQRS implementation for Cidadão.AI."""

from .commands import (
    Command,
    CommandResult,
    CommandHandler,
    CommandBus,
    CreateInvestigationCommand,
    UpdateInvestigationCommand,
    CancelInvestigationCommand,
    ExecuteAgentTaskCommand,
    SendChatMessageCommand
)
from .queries import (
    Query,
    QueryResult, 
    QueryHandler,
    QueryBus,
    GetInvestigationByIdQuery,
    SearchInvestigationsQuery,
    GetInvestigationStatsQuery,
    SearchContractsQuery,
    GetAgentPerformanceQuery
)

__all__ = [
    "Command",
    "CommandResult",
    "CommandHandler", 
    "CommandBus",
    "CreateInvestigationCommand",
    "UpdateInvestigationCommand",
    "CancelInvestigationCommand",
    "ExecuteAgentTaskCommand",
    "SendChatMessageCommand",
    "Query",
    "QueryResult",
    "QueryHandler",
    "QueryBus",
    "GetInvestigationByIdQuery",
    "SearchInvestigationsQuery", 
    "GetInvestigationStatsQuery",
    "SearchContractsQuery",
    "GetAgentPerformanceQuery"
]