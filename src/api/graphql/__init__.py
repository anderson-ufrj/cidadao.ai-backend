"""GraphQL API module for Cidadão.AI."""

from .schema import Mutation, Query, Subscription, schema

__all__ = ["schema", "Query", "Mutation", "Subscription"]
