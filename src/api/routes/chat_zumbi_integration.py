"""
Integration module for Zumbi agent in chat flow.

This module provides a clean interface to use Zumbi agent from chat
without causing circular imports.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.agents.zumbi import InvestigatorAgent, InvestigationRequest
from src.agents.deodoro import AgentContext, AgentStatus

logger = logging.getLogger(__name__)

# Cache for agent instance
_zumbi_agent_instance: Optional[InvestigatorAgent] = None


async def get_zumbi_agent() -> InvestigatorAgent:
    """
    Get or create Zumbi agent instance with lazy loading.
    
    Returns:
        InvestigatorAgent instance
    """
    global _zumbi_agent_instance
    
    if _zumbi_agent_instance is None:
        logger.info("Creating new Zumbi agent instance")
        _zumbi_agent_instance = InvestigatorAgent()
        await _zumbi_agent_instance.initialize()
        
    return _zumbi_agent_instance


async def run_zumbi_investigation(
    query: str,
    organization_codes: Optional[list] = None,
    enable_open_data: bool = True,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run investigation using Zumbi agent.
    
    Args:
        query: Investigation query
        organization_codes: Optional organization codes
        enable_open_data: Enable dados.gov.br integration
        session_id: Session ID
        user_id: User ID
        
    Returns:
        Investigation results
    """
    try:
        # Get agent instance
        agent = await get_zumbi_agent()
        
        # Create investigation request
        investigation_request = InvestigationRequest(
            query=query,
            organization_codes=organization_codes,
            max_records=50,
            enable_open_data_enrichment=enable_open_data,
            anomaly_types=["price_anomaly", "vendor_concentration", "temporal_patterns"]
        )
        
        # Create context
        context = AgentContext(
            investigation_id=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id=user_id or "anonymous",
            correlation_id=session_id or "default"
        )
        
        # Create message
        message = {
            "action": "investigate",
            "payload": investigation_request.model_dump()
        }
        
        logger.info(f"Starting Zumbi investigation: {query}")
        
        # Process investigation
        response = await agent.process(message, context)
        
        # Format response
        if response.status == AgentStatus.COMPLETED:
            result = response.result
            
            # Extract key information
            investigation_data = {
                "status": "completed",
                "anomalies_found": result.get("metadata", {}).get("anomalies_detected", 0),
                "records_analyzed": result.get("metadata", {}).get("records_analyzed", 0),
                "anomalies": result.get("anomalies", []),
                "summary": result.get("summary", {}),
                "open_data_available": False,
                "related_datasets": []
            }
            
            # Check for open data enrichment
            if enable_open_data:
                # Count datasets found
                datasets_found = set()
                for anomaly in investigation_data["anomalies"]:
                    evidence = anomaly.get("evidence", {})
                    if evidence.get("_open_data_available"):
                        investigation_data["open_data_available"] = True
                        for dataset in evidence.get("_related_datasets", []):
                            datasets_found.add(dataset.get("title", "Unknown"))
                
                investigation_data["related_datasets"] = list(datasets_found)
                
            return investigation_data
            
        else:
            logger.error(f"Zumbi investigation failed: {response.error}")
            return {
                "status": "error",
                "error": response.error or "Investigation failed",
                "anomalies_found": 0,
                "records_analyzed": 0
            }
            
    except Exception as e:
        logger.error(f"Error in Zumbi investigation: {e}")
        return {
            "status": "error",
            "error": str(e),
            "anomalies_found": 0,
            "records_analyzed": 0
        }


def format_investigation_message(investigation_data: Dict[str, Any]) -> str:
    """
    Format investigation results for chat response.
    
    Args:
        investigation_data: Investigation results
        
    Returns:
        Formatted message
    """
    if investigation_data["status"] == "error":
        return f"❌ Erro na investigação: {investigation_data.get('error', 'Erro desconhecido')}"
    
    message = "🏹 **Investigação Concluída**\n\n"
    message += f"📊 **Resumo da Análise:**\n"
    message += f"• Registros analisados: {investigation_data['records_analyzed']}\n"
    message += f"• Anomalias detectadas: {investigation_data['anomalies_found']}\n"
    
    # Add open data information if available
    if investigation_data.get("open_data_available"):
        datasets_count = len(investigation_data.get("related_datasets", []))
        message += f"• 📂 Datasets abertos encontrados: {datasets_count}\n"
        
    message += "\n"
    
    # Show anomalies
    if investigation_data["anomalies_found"] > 0:
        message += "⚠️ **Anomalias Detectadas:**\n"
        
        for i, anomaly in enumerate(investigation_data["anomalies"][:5], 1):
            severity = anomaly.get("severity", 0)
            severity_emoji = "🔴" if severity > 0.7 else "🟡" if severity > 0.4 else "🟢"
            
            message += f"\n{severity_emoji} **{i}. {anomaly.get('anomaly_type', 'Unknown').replace('_', ' ').title()}**\n"
            message += f"   • Severidade: {severity:.2f}\n"
            message += f"   • {anomaly.get('description', 'Sem descrição')}\n"
            
            # Add open data reference if available
            evidence = anomaly.get("evidence", {})
            if evidence.get("_related_datasets"):
                message += f"   • 📂 Dados abertos relacionados disponíveis\n"
                
    else:
        message += "✅ Nenhuma anomalia significativa foi detectada nos dados analisados.\n"
    
    # Add summary statistics if available
    summary = investigation_data.get("summary", {})
    if summary:
        message += f"\n📈 **Estatísticas:**\n"
        if "total_value" in summary:
            message += f"• Valor total analisado: R$ {summary['total_value']:,.2f}\n"
        if "organizations_count" in summary:
            message += f"• Organizações: {summary['organizations_count']}\n"
        if "suppliers_count" in summary:
            message += f"• Fornecedores: {summary['suppliers_count']}\n"
    
    # Add note about open data if found
    if investigation_data.get("open_data_available"):
        message += f"\n💡 **Dados Abertos Disponíveis:**\n"
        message += f"Encontramos {len(investigation_data['related_datasets'])} conjuntos de dados relacionados no dados.gov.br "
        message += f"que podem fornecer informações adicionais para sua análise.\n"
        
        # List first 3 datasets
        for dataset in investigation_data["related_datasets"][:3]:
            message += f"• {dataset}\n"
    
    return message