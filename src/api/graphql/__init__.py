"""GraphQL API module for Cidadão.AI."""

from .schema import schema, Query, Mutation, Subscription

__all__ = ["schema", "Query", "Mutation", "Subscription"]