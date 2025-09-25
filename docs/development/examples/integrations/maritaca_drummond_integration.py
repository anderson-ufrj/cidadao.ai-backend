#!/usr/bin/env python3
"""
Example: Maritaca AI integration with Drummond agent for conversational AI.

This example demonstrates how to use the Maritaca AI client (Sabiá-3 model)
with the Drummond agent for natural language generation in Brazilian Portuguese.
"""

import asyncio
import os
from datetime import datetime
from typing import List, Dict

from src.services.maritaca_client import create_maritaca_client, MaritacaModel
from src.agents.drummond import CommunicationAgent, AgentContext, AgentMessage
from src.core import get_logger

# Initialize logger
logger = get_logger(__name__)


async def example_maritaca_conversation():
    """Example of direct Maritaca AI conversation."""
    print("\n=== Example: Direct Maritaca AI Conversation ===\n")
    
    # Get API key from environment
    api_key = os.getenv("MARITACA_API_KEY")
    if not api_key:
        print("❌ Please set MARITACA_API_KEY environment variable")
        return
    
    # Create Maritaca client
    async with create_maritaca_client(
        api_key=api_key,
        model=MaritacaModel.SABIA_3
    ) as client:
        
        # Example 1: Simple completion
        print("1. Simple completion example:")
        messages = [
            {
                "role": "system",
                "content": "Você é um assistente especializado em transparência governamental brasileira."
            },
            {
                "role": "user",
                "content": "Explique brevemente o que é o Portal da Transparência."
            }
        ]
        
        response = await client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Tokens used: {response.usage.get('total_tokens', 'N/A')}")
        print(f"Response time: {response.response_time:.2f}s\n")
        
        # Example 2: Streaming response
        print("2. Streaming response example:")
        messages.append({
            "role": "assistant",
            "content": response.content
        })
        messages.append({
            "role": "user",
            "content": "Como posso acessar dados de licitações?"
        })
        
        print("Streaming response: ", end="", flush=True)
        async for chunk in await client.chat_completion(
            messages=messages,
            stream=True,
            max_tokens=150
        ):
            print(chunk, end="", flush=True)
        print("\n")
        
        # Example 3: Multi-turn conversation
        print("3. Multi-turn conversation example:")
        conversation = [
            {
                "role": "system",
                "content": "Você é um especialista em análise de gastos públicos. Responda de forma clara e objetiva."
            },
            {
                "role": "user",
                "content": "Quais são os principais tipos de despesas do governo federal?"
            }
        ]
        
        # First turn
        response = await client.chat_completion(conversation, max_tokens=200)
        print(f"Assistant: {response.content}")
        
        conversation.extend([
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": "E como posso verificar essas despesas online?"}
        ])
        
        # Second turn
        response = await client.chat_completion(conversation, max_tokens=200)
        print(f"Assistant: {response.content}")


async def example_drummond_with_maritaca():
    """Example of Drummond agent using Maritaca AI for NLG."""
    print("\n=== Example: Drummond Agent with Maritaca AI ===\n")
    
    # Get API key
    api_key = os.getenv("MARITACA_API_KEY")
    if not api_key:
        print("❌ Please set MARITACA_API_KEY environment variable")
        return
    
    # Create context for Drummond agent
    context = AgentContext(
        user_id="example_user",
        session_id="example_session",
        metadata={
            "llm_provider": "maritaca",
            "llm_model": MaritacaModel.SABIA_3,
            "api_key": api_key
        }
    )
    
    # Initialize Drummond agent
    drummond = CommunicationAgent()
    
    # Example investigation data to communicate
    investigation_data = {
        "type": "anomaly_detection",
        "title": "Despesas Irregulares em Contratos de TI",
        "summary": "Análise identificou possíveis irregularidades em contratos de TI",
        "findings": [
            {
                "contract_id": "CT-2024-001",
                "supplier": "TechCorp Ltda",
                "value": 5000000.00,
                "anomaly_score": 0.92,
                "issues": [
                    "Valor 300% acima da média de mercado",
                    "Fornecedor sem histórico anterior",
                    "Prazo de entrega incompatível"
                ]
            },
            {
                "contract_id": "CT-2024-002",
                "supplier": "DataSys S.A.",
                "value": 3200000.00,
                "anomaly_score": 0.85,
                "issues": [
                    "Especificações técnicas genéricas",
                    "Ausência de justificativa para escolha"
                ]
            }
        ],
        "recommendations": [
            "Realizar auditoria detalhada dos contratos",
            "Verificar documentação dos fornecedores",
            "Comparar com preços de referência do mercado"
        ]
    }
    
    # Create message for Drummond to process
    message = AgentMessage(
        sender="zumbi",  # From Zumbi agent (anomaly detector)
        receiver="drummond",
        action="generate_report",
        payload={
            "investigation": investigation_data,
            "target_audience": "citizens",
            "language": "pt-BR",
            "tone": "informative_accessible",
            "channels": ["portal_web", "email"],
            "use_maritaca": True  # Signal to use Maritaca AI
        }
    )
    
    print("Processing investigation report with Drummond + Maritaca AI...")
    
    # Process with Drummond
    # Note: This would normally use the agent's process method
    # but for this example, we'll simulate the key parts
    
    # Simulate Drummond using Maritaca for report generation
    async with create_maritaca_client(api_key=api_key) as maritaca:
        # Generate citizen-friendly report
        report_prompt = f"""
        Como especialista em comunicação governamental, crie um relatório acessível ao cidadão sobre a seguinte análise:
        
        Tipo: {investigation_data['type']}
        Título: {investigation_data['title']}
        Resumo: {investigation_data['summary']}
        
        Achados principais:
        {format_findings(investigation_data['findings'])}
        
        Recomendações:
        {format_list(investigation_data['recommendations'])}
        
        Requisitos:
        - Linguagem clara e acessível
        - Evite jargões técnicos
        - Explique a importância para o cidadão
        - Máximo 300 palavras
        - Tom informativo mas não alarmista
        """
        
        response = await maritaca.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Você é Carlos Drummond de Andrade, o comunicador oficial do sistema Cidadão.AI. Sua missão é traduzir análises técnicas em linguagem acessível ao cidadão brasileiro."
                },
                {
                    "role": "user",
                    "content": report_prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        print("\n📄 Relatório Gerado (via Maritaca AI):")
        print("-" * 50)
        print(response.content)
        print("-" * 50)
        
        # Generate email version
        email_prompt = """
        Agora crie uma versão resumida deste relatório para envio por email (máximo 150 palavras).
        Inclua:
        - Assunto sugestivo
        - Resumo dos principais pontos
        - Call-to-action para ver relatório completo
        """
        
        response = await maritaca.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em comunicação por email."
                },
                {
                    "role": "user",
                    "content": email_prompt
                }
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        print("\n📧 Versão Email (via Maritaca AI):")
        print("-" * 50)
        print(response.content)
        print("-" * 50)


def format_findings(findings: List[Dict]) -> str:
    """Format findings for prompt."""
    result = []
    for i, finding in enumerate(findings, 1):
        issues = ", ".join(finding['issues'])
        result.append(
            f"{i}. Contrato {finding['contract_id']} - {finding['supplier']}: "
            f"R$ {finding['value']:,.2f} (Score anomalia: {finding['anomaly_score']:.0%}). "
            f"Problemas: {issues}"
        )
    return "\n".join(result)


def format_list(items: List[str]) -> str:
    """Format list items."""
    return "\n".join(f"- {item}" for item in items)


async def example_health_check():
    """Example of checking Maritaca AI service health."""
    print("\n=== Example: Maritaca AI Health Check ===\n")
    
    api_key = os.getenv("MARITACA_API_KEY")
    if not api_key:
        print("❌ Please set MARITACA_API_KEY environment variable")
        return
    
    async with create_maritaca_client(api_key=api_key) as client:
        health = await client.health_check()
        
        print(f"Status: {health['status']}")
        print(f"Provider: {health['provider']}")
        print(f"Model: {health['model']}")
        print(f"Circuit Breaker: {health['circuit_breaker']}")
        print(f"Timestamp: {health['timestamp']}")
        
        if health.get('error'):
            print(f"Error: {health['error']}")


async def main():
    """Run all examples."""
    print("🤖 Maritaca AI + Drummond Agent Integration Examples")
    print("=" * 60)
    
    # Run examples
    await example_health_check()
    await example_maritaca_conversation()
    await example_drummond_with_maritaca()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    # Note: Set MARITACA_API_KEY environment variable before running
    asyncio.run(main())