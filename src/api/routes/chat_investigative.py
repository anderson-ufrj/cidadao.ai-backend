"""
Chat Investigative Routes
Real-time contract search with streaming during agent conversations.

Author: Anderson H. Silva
Date: 2025-11-25
"""

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.core import get_logger
from src.services.chat_investigative_service import get_investigative_service

logger = get_logger(__name__)

router = APIRouter(prefix="/investigate", tags=["Chat Investigativo"])

# HTTP status codes
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500


class InvestigateRequest(BaseModel):
    """Request for investigative chat."""

    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    orgao_code: str | None = Field(
        None, description="Organization SIAFI code (auto-detected if not provided)"
    )
    max_results: int = Field(10, ge=1, le=50, description="Maximum results to return")
    session_id: str | None = Field(
        None, description="Session ID for conversation continuity"
    )


class ContractDownloadRequest(BaseModel):
    """Request for contract download."""

    contracts: list[dict[str, Any]] = Field(
        ..., description="List of contracts to include in report"
    )
    format: str = Field("json", description="Output format: json, csv, or txt")


@router.post(
    "/search",
    summary="Search contracts with real-time streaming",
    description="""
    Search government contracts with real-time streaming updates.

    This endpoint streams SSE events as the search progresses:
    - `thinking`: Agent is processing your request
    - `searching`: Querying the Portal da Transparência API
    - `found`: Initial results found
    - `contract`: Individual contract data (one per contract)
    - `complete`: Search finished with summary
    - `error`: Error occurred during search

    **Example usage with curl:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/chat/investigate/search" \\
      -H "Content-Type: application/json" \\
      -d '{"message": "contratos do ministério da saúde"}' \\
      --no-buffer
    ```

    **Example usage with JavaScript:**
    ```javascript
    const response = await fetch('/api/v1/chat/investigate/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'contratos da educação' })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\\n').filter(line => line.startsWith('data: '));

      for (const line of lines) {
        const data = JSON.parse(line.slice(6));
        console.log(data.type, data);
      }
    }
    ```

    **Response events include:**
    - Contract details (object, value, supplier, dates)
    - Download availability flag
    - Raw contract data for report generation
    """,
)
async def search_contracts_streaming(request: InvestigateRequest):
    """
    Search contracts with real-time streaming updates.

    Returns Server-Sent Events (SSE) stream with search progress and results.
    """
    service = get_investigative_service()

    async def event_stream() -> AsyncGenerator[str, None]:
        """Generate SSE events from the search."""
        session_id = request.session_id or str(uuid.uuid4())

        # Send session start event
        yield f"data: {json.dumps({'type': 'session_start', 'session_id': session_id, 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

        try:
            async for event in service.search_contracts_streaming(
                message=request.message,
                orgao_code=request.orgao_code,
                max_results=request.max_results,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming search: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e), 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

        # Send stream end
        yield f"data: {json.dumps({'type': 'stream_end', 'session_id': session_id, 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.post(
    "/download",
    summary="Download contract report",
    description="""
    Generate and download a report from contract search results.

    Supported formats:
    - **json**: Full structured data with metadata
    - **csv**: Spreadsheet-compatible format
    - **txt**: Human-readable text report

    **Example usage:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/chat/investigate/download" \\
      -H "Content-Type: application/json" \\
      -d '{"contracts": [...], "format": "csv"}' \\
      --output contratos.csv
    ```
    """,
)
async def download_contracts(request: ContractDownloadRequest):
    """
    Generate and download a contract report.

    Args:
        request: Download request with contracts and format

    Returns:
        Downloadable file with contract report
    """
    service = get_investigative_service()

    try:
        report = await service.generate_contract_report(
            contracts=request.contracts,
            output_format=request.format,
        )

        if "error" in report:
            raise HTTPException(status_code=400, detail=report["error"])

        # Set appropriate content type
        content_type = report.get("content_type", "application/octet-stream")

        return Response(
            content=(
                report["content"].encode("utf-8")
                if isinstance(report["content"], str)
                else report["content"]
            ),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={report['filename']}",
                "Content-Length": str(report["size"]),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.get(
    "/contract/{contract_id}",
    summary="Get contract details",
    description="""
    Get detailed information about a specific contract.

    **Note**: Due to CloudFront restrictions on the Portal da Transparência API,
    this endpoint may not return data for all contracts. Use the search endpoint
    to get contract data instead.
    """,
)
async def get_contract_details(contract_id: int):
    """
    Get detailed contract information.

    Args:
        contract_id: Contract ID from Portal da Transparência

    Returns:
        Full contract details or error message
    """
    service = get_investigative_service()

    result = await service.get_contract_details(contract_id)

    if "error" in result:
        raise HTTPException(
            status_code=(
                HTTP_NOT_FOUND
                if result.get("error_code") == HTTP_FORBIDDEN
                else HTTP_SERVER_ERROR
            ),
            detail=result["error"],
        )

    return result


@router.get(
    "/orgaos",
    summary="List available organizations",
    description="Get list of known organization codes (SIAFI) that can be used for searches.",
)
async def list_orgaos():
    """
    List available organization codes.

    Returns:
        List of organization codes and names
    """
    service = get_investigative_service()

    return {
        "orgaos": [
            {"codigo": code, "nome": name} for code, name in service.ORGAO_NAMES.items()
        ],
        "keywords": dict(service.ORGAOS.items()),
        "note": "You can use either the codigo (SIAFI code) or keywords in your search message",
    }


@router.post(
    "/simulate",
    summary="Simulate a full chat conversation with contract search",
    description="""
    Simulates a complete chat interaction where an agent searches for contracts
    and responds with findings. This is useful for testing the full flow.

    The response includes:
    - Agent introduction
    - Search progress
    - Contract findings
    - Summary and download options
    """,
)
async def simulate_chat_investigation(request: InvestigateRequest):
    """
    Simulate a full chat conversation with contract search.

    This demonstrates how the streaming search integrates with agent responses.
    """
    service = get_investigative_service()
    session_id = request.session_id or str(uuid.uuid4())

    async def chat_stream() -> AsyncGenerator[str, None]:
        """Generate a simulated chat stream."""

        # Agent greeting
        yield f"data: {json.dumps({'type': 'agent_message', 'agent': 'Zumbi dos Palmares', 'avatar': '🔍', 'message': 'Olá! Sou Zumbi dos Palmares, o agente investigador do Cidadão.AI. Vou pesquisar os contratos que você solicitou...', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
        await asyncio.sleep(0.5)

        # Collect contracts for summary
        contracts_found = []
        total_value = 0

        # Stream search events
        async for event in service.search_contracts_streaming(
            message=request.message,
            orgao_code=request.orgao_code,
            max_results=request.max_results,
        ):
            # Add context to events
            event["session_id"] = session_id

            if event["type"] == "contract":
                contracts_found.append(event["data"])
                total_value += event["data"].get("valor", 0)

            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        # Agent summary
        if contracts_found:
            summary_message = (
                f"📊 **Resumo da Investigação**\n\n"
                f"Encontrei {len(contracts_found)} contratos totalizando "
                f"R$ {total_value:,.2f}.\n\n"
                f"🔎 **Principais achados:**\n"
            )

            # Top 3 by value
            top_contracts = sorted(
                contracts_found, key=lambda x: x.get("valor", 0), reverse=True
            )[:3]
            for i, contract in enumerate(top_contracts, 1):
                summary_message += (
                    f"{i}. {contract.get('objeto', 'N/A')[:50]}... "
                    f"({contract.get('valor_formatado', 'N/A')})\n"
                )

            summary_message += (
                "\n💾 **Opções de download disponíveis:**\n"
                "- JSON (dados completos)\n"
                "- CSV (planilha)\n"
                "- TXT (relatório texto)\n\n"
                "Posso ajudar a analisar algum contrato específico?"
            )

            yield f"data: {json.dumps({'type': 'agent_message', 'agent': 'Zumbi dos Palmares', 'avatar': '🔍', 'message': summary_message, 'contracts_for_download': contracts_found, 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

        else:
            yield f"data: {json.dumps({'type': 'agent_message', 'agent': 'Zumbi dos Palmares', 'avatar': '🔍', 'message': '😕 Não encontrei contratos com os critérios especificados. Tente refinar sua busca ou escolher outro órgão.', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

        # End stream
        yield f"data: {json.dumps({'type': 'stream_end', 'session_id': session_id, 'timestamp': datetime.now(UTC).isoformat()})}\n\n"

    return StreamingResponse(
        chat_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get(
    "/health",
    summary="Check investigative service health",
    description="Check if the investigative service is operational and API key is configured.",
)
async def health_check():
    """
    Check investigative service health.

    Returns:
        Service status and configuration
    """
    service = get_investigative_service()

    return {
        "status": "operational",
        "api_key_configured": bool(service.api_key),
        "available_orgaos": len(service.ORGAO_NAMES),
        "features": {
            "streaming_search": True,
            "download_json": True,
            "download_csv": True,
            "download_txt": True,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }
