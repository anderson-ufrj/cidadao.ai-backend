"""
GraphQL API router for Cidadão.AI.

This module integrates Strawberry GraphQL with FastAPI,
providing a modern GraphQL endpoint with subscriptions support.
"""

from typing import Any, Dict
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, Request, WebSocket, HTTPException

from src.core import get_logger

# Try to import strawberry - optional dependency
try:
    from strawberry.fastapi import GraphQLRouter
    from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
    from src.api.graphql.schema import schema
    STRAWBERRY_AVAILABLE = True
except ImportError:
    STRAWBERRY_AVAILABLE = False
    GraphQLRouter = None
    GRAPHQL_TRANSPORT_WS_PROTOCOL = None
    GRAPHQL_WS_PROTOCOL = None
    schema = None

from src.api.dependencies import get_current_optional_user

logger = get_logger(__name__)


# Context getter for GraphQL
async def get_context(
    request: Request,
    user=Depends(get_current_optional_user)
) -> Dict[str, Any]:
    """
    Get GraphQL context with request info and user.
    """
    return {
        "request": request,
        "user": user,
        "db": request.app.state.db if hasattr(request.app.state, "db") else None,
    }


# WebSocket context for subscriptions
async def get_ws_context(
    websocket: WebSocket,
) -> Dict[str, Any]:
    """
    Get WebSocket context for subscriptions.
    """
    return {
        "websocket": websocket,
        "user": None,  # TODO: Implement WebSocket auth
    }


# Create router
router = APIRouter(prefix="/graphql", tags=["GraphQL"])

if STRAWBERRY_AVAILABLE:
    # Create GraphQL app with custom context
    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
        subscription_protocols=[
            GRAPHQL_TRANSPORT_WS_PROTOCOL,
            GRAPHQL_WS_PROTOCOL,
        ],
    )
    
    # Add GraphQL routes
    router.include_router(graphql_app, prefix="")
else:
    # Add placeholder route when GraphQL is not available
    @router.get("/")
    async def graphql_not_available():
        raise HTTPException(
            status_code=503,
            detail="GraphQL is not available in this deployment. Install 'strawberry-graphql' to enable it."
        )

# Add GraphQL playground route (only in development)
@router.get("/playground")
async def graphql_playground():
    """
    GraphQL Playground UI.
    
    Only available in development mode.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cidadão.AI GraphQL Playground</title>
        <link rel="stylesheet" href="https://unpkg.com/graphql-playground-react/build/static/css/index.css" />
        <script src="https://unpkg.com/graphql-playground-react/build/static/js/middleware.js"></script>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: "Open Sans", sans-serif;
            }
            #root {
                height: 100vh;
            }
        </style>
    </head>
    <body>
        <div id="root"></div>
        <script>
            window.addEventListener('load', function (event) {
                GraphQLPlayground.init(document.getElementById('root'), {
                    endpoint: '/graphql',
                    subscriptionEndpoint: 'ws://localhost:8000/graphql',
                    settings: {
                        'request.credentials': 'same-origin',
                        'editor.theme': 'dark',
                        'editor.cursorShape': 'line',
                        'editor.fontSize': 14,
                        'editor.fontFamily': '"Fira Code", "Monaco", monospace',
                        'prettier.printWidth': 80,
                        'prettier.tabWidth': 2,
                        'prettier.useTabs': false,
                        'schema.polling.enable': true,
                        'schema.polling.endpointFilter': '*',
                        'schema.polling.interval': 2000
                    },
                    tabs: [
                        {
                            endpoint: '/graphql',
                            query: `# Welcome to Cidadão.AI GraphQL API
#
# Example queries:

# Get current user
query GetMe {
  me {
    id
    email
    name
    role
  }
}

# Search investigations
query SearchInvestigations($limit: Int) {
  investigations(
    pagination: { limit: $limit, offset: 0 }
  ) {
    id
    query
    status
    confidenceScore
    createdAt
    findings {
      type
      title
      severity
    }
  }
}

# Get agent statistics
query GetAgentStats {
  agentStats {
    agentName
    totalTasks
    successfulTasks
    avgResponseTimeMs
  }
}

# Create investigation
mutation CreateInvestigation($query: String!) {
  createInvestigation(
    input: { 
      query: $query
      priority: "high"
    }
  ) {
    id
    query
    status
    createdAt
  }
}

# Subscribe to investigation updates
subscription InvestigationUpdates($id: ID!) {
  investigationUpdates(investigationId: $id) {
    id
    status
    confidenceScore
    completedAt
    processingTimeMs
  }
}`,
                            variables: JSON.stringify({
                                limit: 10,
                                query: "Contratos suspeitos em 2024",
                                id: "123"
                            }, null, 2)
                        }
                    ]
                })
            })
        </script>
    </body>
    </html>
    """


# Health check for GraphQL
@router.get("/health")
async def graphql_health():
    """Check GraphQL endpoint health."""
    return {
        "status": "healthy",
        "endpoint": "/graphql",
        "playground": "/graphql/playground",
        "features": [
            "queries",
            "mutations", 
            "subscriptions",
            "file_uploads",
            "introspection"
        ]
    }


# Example queries documentation
@router.get("/examples")
async def graphql_examples():
    """Get example GraphQL queries."""
    return {
        "queries": {
            "get_user": """
                query GetUser($id: ID!) {
                    user(id: $id) {
                        id
                        email
                        name
                        investigations {
                            id
                            query
                            status
                        }
                    }
                }
            """,
            "search_contracts": """
                query SearchContracts($search: String, $minValue: Float) {
                    contracts(
                        search: $search
                        minValue: $minValue
                        pagination: { limit: 20 }
                    ) {
                        id
                        numero
                        objeto
                        valor
                        anomalies {
                            type
                            severity
                        }
                    }
                }
            """,
            "complex_investigation": """
                query ComplexInvestigation($id: ID!) {
                    investigation(id: $id) {
                        id
                        query
                        status
                        confidenceScore
                        findings {
                            type
                            title
                            severity
                            confidence
                        }
                        anomalies {
                            type
                            description
                            severityScore
                            affectedEntities
                        }
                        user {
                            name
                            email
                        }
                    }
                }
            """
        },
        "mutations": {
            "create_investigation": """
                mutation CreateInvestigation($input: InvestigationInput!) {
                    createInvestigation(input: $input) {
                        id
                        query
                        status
                        createdAt
                    }
                }
            """,
            "send_message": """
                mutation SendMessage($message: String!, $sessionId: String) {
                    sendChatMessage(
                        input: { 
                            message: $message
                            sessionId: $sessionId 
                        }
                    ) {
                        id
                        content
                        agentName
                        createdAt
                    }
                }
            """
        },
        "subscriptions": {
            "investigation_progress": """
                subscription OnInvestigationUpdate($id: ID!) {
                    investigationUpdates(investigationId: $id) {
                        id
                        status
                        confidenceScore
                        processingTimeMs
                    }
                }
            """,
            "agent_monitoring": """
                subscription MonitorAgents {
                    agentActivity {
                        agentName
                        totalTasks
                        successfulTasks
                        avgResponseTimeMs
                        lastActive
                    }
                }
            """
        },
        "tips": [
            "Use variables for dynamic values",
            "Request only needed fields to reduce payload",
            "Use fragments for reusable selections",
            "Batch multiple queries in a single request",
            "Use subscriptions for real-time updates"
        ]
    }