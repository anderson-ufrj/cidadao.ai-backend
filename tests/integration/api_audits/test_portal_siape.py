#!/usr/bin/env python3
"""
Test Portal da Transparência SIAPE API

Testa busca de salário de servidor público por nome.

Endpoint: http://api.portaldatransparencia.gov.br/api-de-dados/servidores
"""

import asyncio
import os

import httpx


async def search_servidor_by_name(nome: str):
    """Search for public servant salary by name."""

    api_key = os.getenv("TRANSPARENCY_API_KEY")
    if not api_key:
        print("⚠️  TRANSPARENCY_API_KEY não configurada")
        return None

    base_url = "http://api.portaldatransparencia.gov.br/api-de-dados"

    # Endpoint: /servidores/{cpf}
    # Mas precisamos buscar por nome primeiro

    # Tentativa 1: Buscar lista de servidores
    search_url = f"{base_url}/servidores"

    headers = {"chave-api-dados": api_key, "Accept": "application/json"}

    params = {"nome": nome, "pagina": 1}

    print(f"🔍 Buscando servidor: {nome}")
    print(f"📡 URL: {search_url}")
    print(f"🔑 API Key: {'*' * 20}{api_key[-4:]}")
    print(f"📋 Params: {params}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(search_url, headers=headers, params=params)

            print(f"📥 Status Code: {response.status_code}")
            print(f"📝 Response Headers: {dict(response.headers)}\n")

            if response.status_code == 200:
                data = response.json()
                print("✅ Dados recebidos!")
                print(
                    f"📊 Total de resultados: {len(data) if isinstance(data, list) else 'N/A'}"
                )
                print("\n🔍 Dados completos:")

                import json

                print(json.dumps(data, indent=2, ensure_ascii=False))

                return data

            elif response.status_code == 403:
                print("❌ 403 Forbidden - API Key inválida ou endpoint não autorizado")
                return None

            elif response.status_code == 404:
                print(
                    "❌ 404 Not Found - Servidor não encontrado ou endpoint incorreto"
                )
                return None

            else:
                print(f"⚠️  Status inesperado: {response.status_code}")
                print(f"Resposta: {response.text[:500]}")
                return None

        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
            import traceback

            traceback.print_exc()
            return None


async def test_portal_api_structure():
    """Test Portal API structure to find correct endpoint."""

    api_key = os.getenv("TRANSPARENCY_API_KEY")
    if not api_key:
        print("⚠️  TRANSPARENCY_API_KEY não configurada")
        return

    base_url = "http://api.portaldatransparencia.gov.br/api-de-dados"

    # Endpoints conhecidos do Portal da Transparência
    endpoints = [
        "/servidores",
        "/servidores/por-cpf",
        "/servidores/por-nome",
        "/servidores/siape",
        "/remuneracao",
        "/servidores/remuneracao",
    ]

    headers = {"chave-api-dados": api_key, "Accept": "application/json"}

    print("🔍 Testando endpoints do Portal da Transparência\n")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                print(f"\n📡 Testando: {url}")
                response = await client.get(url, headers=headers)
                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    print("   ✅ FUNCIONOU!")
                elif response.status_code == 403:
                    print("   ❌ 403 Forbidden")
                elif response.status_code == 404:
                    print("   ❌ 404 Not Found")
                else:
                    print(f"   ⚠️  {response.status_code}")

            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")

    print("\n" + "=" * 80)


async def main():
    print("=" * 80)
    print("TESTE: Portal da Transparência - SIAPE API")
    print("=" * 80)
    print()

    # Test 1: API structure
    print("TESTE 1: Estrutura da API")
    print("-" * 80)
    await test_portal_api_structure()

    print("\n\n")

    # Test 2: Search specific person
    print("TESTE 2: Busca por Nome")
    print("-" * 80)
    result = await search_servidor_by_name("Aracele Garcia de Oliveira Fassbinder")

    if result:
        print("\n✅ SUCESSO: Dados encontrados!")
    else:
        print("\n❌ FALHA: Não foi possível obter dados")
        print("\nℹ️  NOTA: Portal da Transparência tem limitações conhecidas:")
        print("   - 78% dos endpoints retornam 403 Forbidden")
        print("   - Endpoint de servidores pode requerer CPF específico")
        print("   - Busca por nome pode não estar disponível")


if __name__ == "__main__":
    asyncio.run(main())
