#!/usr/bin/env python3
"""
Teste de integração com Maritaca AI
Verifica se o sistema está configurado corretamente para usar Maritaca
"""

import asyncio
import os
import sys
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variáveis de ambiente para teste
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret"
os.environ["SECRET_KEY"] = "test_secret"

# IMPORTANTE: Configure a API Key da Maritaca aqui ou no .env
# os.environ["MARITACA_API_KEY"] = "sk-xxxxx"  # Substitua com sua chave

# Forçar o uso do Maritaca como provider
os.environ["LLM_PROVIDER"] = "maritaca"
os.environ["LLM_MODEL_NAME"] = "sabiazinho-4"  # Modelo mais econômico


async def test_maritaca_provider():
    """Testa se o provider Maritaca está funcionando"""

    print("\n" + "=" * 60)
    print("🤖 TESTE DE INTEGRAÇÃO COM MARITACA AI")
    print("=" * 60)

    # 1. Verificar configuração
    print("\n1. Verificando configuração...")
    from src.core import settings

    print(f"   LLM Provider: {settings.llm_provider}")
    print(f"   LLM Model: {settings.llm_model_name}")

    if settings.maritaca_api_key:
        api_key_preview = str(settings.maritaca_api_key.get_secret_value())[:10] + "..."
        print(f"   Maritaca API Key: {api_key_preview}")
    else:
        print("   ⚠️  MARITACA_API_KEY não configurada!")
        print("   Configure a variável de ambiente MARITACA_API_KEY")
        return False

    # 2. Testar criação do LLM Manager
    print("\n2. Criando LLM Manager com Maritaca...")
    try:
        from src.llm.providers import LLMRequest, create_llm_manager

        llm_manager = create_llm_manager(
            primary_provider="maritaca",
            enable_fallback=False,  # Não usar fallback para testar só Maritaca
        )
        print("   ✅ LLM Manager criado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao criar LLM Manager: {e}")
        import traceback

        traceback.print_exc()
        return False

    # 3. Testar uma requisição simples
    print("\n3. Testando requisição ao Maritaca...")
    try:
        request = LLMRequest(
            prompt="Olá! Responda em português: Qual é a capital do Brasil?",
            max_tokens=100,
            temperature=0.5,
        )

        response = await llm_manager.complete(request)

        print("   ✅ Resposta recebida!")
        print(f"   Conteúdo: {response.content[:200]}...")
        print(f"   Provider usado: {response.provider}")
        print(f"   Tempo de resposta: {response.response_time:.2f}s")
        print(f"   Tokens usados: {response.usage.get('total_tokens', 0)}")

        return True

    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return False
    finally:
        await llm_manager.close()


async def test_investigation_with_maritaca():
    """Testa uma investigação usando Maritaca"""

    print("\n" + "=" * 60)
    print("🔍 TESTE DE INVESTIGAÇÃO COM MARITACA")
    print("=" * 60)

    # Verificar se Maritaca está configurado
    from src.core import settings

    if not settings.maritaca_api_key:
        print("   ⚠️  MARITACA_API_KEY não configurada!")
        print("   Pule este teste ou configure a API key")
        return False

    print("\n1. Importando agente Zumbi...")
    try:
        from src.agents.deodoro import AgentContext, AgentMessage
        from src.agents.zumbi import ZumbiAgent

        agent = ZumbiAgent()
        print("   ✅ Agente Zumbi importado")
    except Exception as e:
        print(f"   ❌ Erro ao importar: {e}")
        return False

    print("\n2. Criando mensagem de teste...")
    message = AgentMessage(
        content={
            "query": "Detectar anomalias em contratos usando Maritaca AI",
            "data": [
                {"valor": 10000, "fornecedor": "Empresa A", "modalidade": "Pregão"},
                {
                    "valor": 500000,
                    "fornecedor": "Empresa B",
                    "modalidade": "Pregão",
                },  # Anomalia
                {"valor": 12000, "fornecedor": "Empresa C", "modalidade": "Pregão"},
            ],
            "anomaly_types": ["price"],
        },
        sender_id="test_user",
        receiver_id="zumbi",
    )

    context = AgentContext()

    print("\n3. Processando com agente...")
    try:
        start_time = datetime.now()
        response = await agent.process(message, context)
        end_time = datetime.now()

        print("   ✅ Processamento concluído!")
        print(f"   Status: {response.status}")
        print(f"   Tempo: {(end_time - start_time).total_seconds():.2f}s")

        if response.content.get("anomalies"):
            print(f"   Anomalias detectadas: {len(response.content['anomalies'])}")

        return response.status == "success"

    except Exception as e:
        print(f"   ❌ Erro no processamento: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_llm_service():
    """Testa o LLM Service com Maritaca"""

    print("\n" + "=" * 60)
    print("🛠️ TESTE DO LLM SERVICE")
    print("=" * 60)

    from src.llm.services import LLMService, LLMServiceConfig

    print("\n1. Criando LLM Service com Maritaca...")
    try:
        config = LLMServiceConfig(
            primary_provider="maritaca",
            enable_fallback=False,
            temperature=0.5,
            max_tokens=200,
        )

        service = LLMService(config)
        print("   ✅ LLM Service criado")
    except Exception as e:
        print(f"   ❌ Erro ao criar service: {e}")
        return False

    print("\n2. Testando summarization...")
    try:
        text = """
        O Portal da Transparência do Governo Federal é uma ferramenta que
        permite ao cidadão acompanhar como o dinheiro público está sendo
        utilizado. Por meio dele, é possível consultar informações sobre
        recursos federais transferidos a estados, municípios e outros.
        """

        summary = await service.summarize(text, max_length=50)
        print("   ✅ Resumo gerado:")
        print(f"   {summary}")

        return True

    except Exception as e:
        print(f"   ❌ Erro na summarização: {e}")
        return False


def main():
    """Executa todos os testes"""

    print("\n🚀 INICIANDO TESTES DE INTEGRAÇÃO COM MARITACA AI")
    print("=" * 60)

    # Verificar se API key está configurada
    if not os.environ.get("MARITACA_API_KEY"):
        print("\n⚠️  ATENÇÃO: MARITACA_API_KEY não encontrada!")
        print("\nPara configurar:")
        print("1. Obtenha uma API key em: https://chat.maritaca.ai")
        print("2. Configure no .env: MARITACA_API_KEY=sk-xxxxx")
        print("3. Ou defina aqui no script na linha 19")
        print("\n" + "=" * 60)

        # Em ambiente não-interativo, continuar mesmo assim
        if not sys.stdin.isatty():
            print("\n⚠️  Executando em modo não-interativo - continuando sem API key")
        else:
            resposta = input("\nDeseja continuar mesmo assim? (s/n): ")
            if resposta.lower() != "s":
                return

    # Executar testes
    asyncio.run(run_tests())

    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(
        """
Se todos os testes passaram:
✅ Maritaca AI está configurado corretamente!

Para usar em produção (Railway):
1. Configure no Railway Dashboard:
   - LLM_PROVIDER=maritaca
   - MARITACA_API_KEY=sk-xxxxx
   - LLM_MODEL_NAME=sabiazinho-4

2. Reinicie o serviço no Railway

3. Teste uma investigação:
   curl -X POST https://cidadao-api-production.up.railway.app/api/v1/investigations/start \\
     -H "Content-Type: application/json" \\
     -d '{"query":"Teste Maritaca","data_source":"contracts","filters":{},"anomaly_types":["price"]}'
"""
    )


async def run_tests():
    """Executa os testes assincronamente"""

    results = {}

    # Teste 1: Provider básico
    print("\n" + "-" * 60)
    print("TESTE 1: Provider Maritaca")
    print("-" * 60)
    results["provider"] = await test_maritaca_provider()

    # Teste 2: LLM Service
    if results["provider"]:
        print("\n" + "-" * 60)
        print("TESTE 2: LLM Service")
        print("-" * 60)
        results["service"] = await test_llm_service()

    # Teste 3: Investigação (mais demorado)
    if results.get("provider"):
        print("\n" + "-" * 60)
        print("TESTE 3: Investigação com Agente")
        print("-" * 60)
        results["investigation"] = await test_investigation_with_maritaca()

    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("🎯 RESULTADOS DOS TESTES")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {test_name.upper()}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("   Maritaca AI está funcionando corretamente")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("   Verifique a configuração e tente novamente")

    return all_passed


if __name__ == "__main__":
    main()
