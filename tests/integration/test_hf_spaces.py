#!/usr/bin/env python3
"""
🔍 Teste de HuggingFace Spaces
Verifica se os Spaces estão rodando e quais endpoints respondem
"""

import asyncio

import httpx


async def test_hf_spaces():
    """🔍 Testa diferentes endpoints dos HF Spaces"""
    print("🔍 VERIFICANDO HUGGINGFACE SPACES")
    print("=" * 50)

    # URLs para testar
    backend_urls = [
        "https://neural-thinker-cidadao-ai-backend.hf.space",
        "https://neural-thinker-cidadao-ai-backend.hf.space/",
        "https://neural-thinker-cidadao-ai-backend.hf.space/health",
        "https://neural-thinker-cidadao-ai-backend.hf.space/docs",
        "https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend",
    ]

    models_urls = [
        "https://neural-thinker-cidadao-ai-models.hf.space",
        "https://neural-thinker-cidadao-ai-models.hf.space/",
        "https://neural-thinker-cidadao-ai-models.hf.space/health",
        "https://huggingface.co/spaces/neural-thinker/cidadao.ai-models",
    ]

    async with httpx.AsyncClient(timeout=10.0) as client:

        print("🏛️ TESTANDO BACKEND SPACES:")
        for url in backend_urls:
            try:
                response = await client.get(url)
                status = (
                    "✅"
                    if response.status_code == 200
                    else f"❌ {response.status_code}"
                )
                print(f"   {status} {url}")

                if (
                    response.status_code == 200
                    and "application/json" in response.headers.get("content-type", "")
                ):
                    try:
                        data = response.json()
                        if "status" in data:
                            print(f"       📊 Status: {data.get('status')}")
                        if "agents" in data:
                            print(
                                f"       🤖 Agentes: {list(data.get('agents', {}).keys())}"
                            )
                    except:
                        print("       📝 HTML response (não JSON)")

            except Exception as e:
                print(f"   ❌ {url} - Erro: {str(e)[:50]}...")

        print("\n🤖 TESTANDO MODELS SPACES:")
        for url in models_urls:
            try:
                response = await client.get(url)
                status = (
                    "✅"
                    if response.status_code == 200
                    else f"❌ {response.status_code}"
                )
                print(f"   {status} {url}")

                if (
                    response.status_code == 200
                    and "application/json" in response.headers.get("content-type", "")
                ):
                    try:
                        data = response.json()
                        if "api" in data:
                            print(f"       📊 API: {data.get('api')}")
                        if "version" in data:
                            print(f"       🔢 Version: {data.get('version')}")
                    except:
                        print("       📝 HTML response (não JSON)")

            except Exception as e:
                print(f"   ❌ {url} - Erro: {str(e)[:50]}...")


if __name__ == "__main__":
    asyncio.run(test_hf_spaces())
