"""CQRS implementation for Cidadão.AI."""

from .commands import (
    CancelInvestigationCommand,
    Command,
    CommandBus,
    CommandHandler,
    CommandResult,
    CreateInvestigationCommand,
    ExecuteAgentTaskCommand,
    SendChatMessageCommand,
    UpdateInvestigationCommand,
)
from .queries import (
    GetAgentPerformanceQuery,
    GetInvestigationByIdQuery,
    GetInvestigationStatsQuery,
    Query,
    QueryBus,
    QueryHandler,
    QueryResult,
    SearchContractsQuery,
    SearchInvestigationsQuery,
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
    "GetAgentPerformanceQuery",
]
