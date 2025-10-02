#!/usr/bin/env python3
"""
Demo: Chat with dados.gov.br integration

This script demonstrates how users can chat with Cidadão.AI
and automatically get enriched results from dados.gov.br.
"""

import asyncio
import json
from datetime import datetime
import aiohttp

# API configuration
API_BASE_URL = "http://localhost:8000"  # Adjust if needed
API_KEY = "demo-key"  # Replace with actual API key if required


async def send_chat_message(session, message: str, session_id: str = None):
    """Send a message to the chat API"""
    url = f"{API_BASE_URL}/api/v1/chat/message"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "message": message,
        "session_id": session_id
    }
    
    async with session.post(url, json=data, headers=headers) as response:
        return await response.json()


async def demo_investigation_with_open_data():
    """Demonstrate an investigation that includes dados.gov.br data"""
    print("=" * 70)
    print("🇧🇷 CIDADÃO.AI - Demonstração de Integração com dados.gov.br")
    print("=" * 70)
    print()
    
    async with aiohttp.ClientSession() as session:
        # Create a session ID
        session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Example 1: Simple investigation
        print("📋 Exemplo 1: Investigação Simples")
        print("-" * 40)
        
        message = "Quero investigar contratos do Ministério da Saúde"
        print(f"👤 Usuário: {message}")
        print()
        
        try:
            response = await send_chat_message(session, message, session_id)
            
            print(f"🤖 Cidadão.AI:")
            print(response.get("message", "Sem resposta"))
            print()
            
            # Check if open data was found
            metadata = response.get("metadata", {})
            if metadata.get("dados_gov_enabled"):
                print("✅ Integração com dados.gov.br ativada!")
                
                # Show suggested actions if available
                actions = response.get("suggested_actions", [])
                if actions:
                    print("\n💡 Ações sugeridas:")
                    for action in actions:
                        print(f"   • {action}")
            print()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return
        
        # Example 2: Investigation with specific focus
        print("\n" + "=" * 70)
        print("📋 Exemplo 2: Investigação com Foco Específico")
        print("-" * 40)
        
        message = "Investigar anomalias em contratos de medicamentos e vacinas"
        print(f"👤 Usuário: {message}")
        print()
        
        try:
            response = await send_chat_message(session, message, session_id)
            
            print(f"🤖 Cidadão.AI:")
            print(response.get("message", "Sem resposta"))
            
        except Exception as e:
            print(f"❌ Erro: {e}")


async def demo_chat_flow():
    """Demonstrate a complete chat flow"""
    print("\n" + "=" * 70)
    print("💬 Demonstração de Conversa Completa")
    print("=" * 70)
    print()
    
    async with aiohttp.ClientSession() as session:
        session_id = f"chat_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conversations = [
            "Olá, o que você pode fazer?",
            "Quero investigar contratos suspeitos",
            "Analise contratos de TI do governo federal em 2024",
            "Existem dados abertos sobre esses contratos?"
        ]
        
        for i, msg in enumerate(conversations, 1):
            print(f"\n🔹 Mensagem {i}:")
            print(f"👤 Usuário: {msg}")
            
            try:
                response = await send_chat_message(session, msg, session_id)
                
                print(f"\n🤖 Cidadão.AI:")
                print(response.get("message", "Sem resposta"))
                
                # Show metadata if interesting
                metadata = response.get("metadata", {})
                if metadata.get("intent_type"):
                    print(f"\n[Intent detectado: {metadata['intent_type']}]")
                    
                await asyncio.sleep(1)  # Small delay between messages
                
            except Exception as e:
                print(f"❌ Erro: {e}")
                break


def print_instructions():
    """Print instructions for running the demo"""
    print("\n" + "=" * 70)
    print("📖 INSTRUÇÕES")
    print("=" * 70)
    print()
    print("1. Certifique-se de que o backend está rodando:")
    print("   $ make run-dev")
    print()
    print("2. Se necessário, ajuste API_BASE_URL e API_KEY no script")
    print()
    print("3. Execute o script:")
    print("   $ python examples/chat_dados_gov_demo.py")
    print()
    print("4. Observe como o sistema:")
    print("   • Detecta automaticamente pedidos de investigação")
    print("   • Busca dados no Portal da Transparência")
    print("   • Enriquece com informações do dados.gov.br")
    print("   • Sugere explorar datasets relacionados")
    print()


async def check_api_health():
    """Check if API is available"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    return True
    except:
        pass
    return False


async def main():
    """Main demo function"""
    print_instructions()
    
    # Check API health
    print("🔍 Verificando conexão com a API...")
    if not await check_api_health():
        print("❌ API não está disponível em", API_BASE_URL)
        print("   Execute 'make run-dev' primeiro")
        return
    
    print("✅ API disponível!")
    print()
    
    # Run demos
    await demo_investigation_with_open_data()
    await demo_chat_flow()
    
    print("\n" + "=" * 70)
    print("✅ Demonstração concluída!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())