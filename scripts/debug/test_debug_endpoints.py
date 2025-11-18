#!/usr/bin/env python3
"""
Testar endpoints de debug
"""


import httpx

# URLs para teste
LOCAL_URL = "http://localhost:8000"
PRODUCTION_URL = "https://cidadao-api-production.up.railway.app"


def test_debug_endpoints(base_url, environment="Local"):
    """Testa os endpoints de debug"""

    print(f"\n{'='*60}")
    print(f"🔍 TESTANDO ENDPOINTS DE DEBUG - {environment}")
    print(f"📡 URL: {base_url}")
    print(f"{'='*60}")

    with httpx.Client(timeout=30.0) as client:
        # 1. Testar /debug/llm-config
        print("\n1️⃣  Testando /debug/llm-config...")
        try:
            response = client.get(f"{base_url}/debug/llm-config")

            if response.status_code == 200:
                data = response.json()

                print("\n📊 CONFIGURAÇÃO DO LLM:")
                print("-" * 40)

                # Configuration from settings
                config = data.get("configuration", {})
                print(f"Provider: {config.get('llm_provider')}")
                print(f"Model: {config.get('llm_model_name')}")
                print(f"Temperature: {config.get('llm_temperature')}")
                print(f"Max Tokens: {config.get('llm_max_tokens')}")

                # Environment variables
                env_vars = data.get("environment_variables", {})
                print("\n🔑 VARIÁVEIS DE AMBIENTE:")
                print(f"LLM_PROVIDER: {env_vars.get('LLM_PROVIDER')}")
                print(f"MARITACA_API_KEY: {env_vars.get('MARITACA_API_KEY')}")
                print(f"MARITACA_MODEL: {env_vars.get('MARITACA_MODEL')}")
                print(f"GROQ_API_KEY: {env_vars.get('GROQ_API_KEY')}")

                # Provider status
                provider_status = data.get("provider_status", {})

                # Maritaca status
                maritaca = provider_status.get("maritaca", {})
                print("\n🇧🇷 STATUS DO MARITACA:")
                print(f"API Key Configured: {maritaca.get('api_key_configured')}")
                print(f"Model: {maritaca.get('model')}")
                print(f"Base URL: {maritaca.get('base_url')}")

                # Initialization status
                init_status = provider_status.get("initialization", {})
                print("\n⚙️  INICIALIZAÇÃO DO LLM:")
                print(f"Status: {init_status.get('status')}")
                if init_status.get("status") == "success":
                    print(f"Primary Provider: {init_status.get('primary_provider')}")
                    print(
                        f"Available Providers: {init_status.get('providers_available')}"
                    )
                else:
                    print(f"Error: {init_status.get('error')}")

                # Test call status
                test_call = provider_status.get("test_call", {})
                print("\n🧪 TESTE DE CHAMADA:")
                print(f"Status: {test_call.get('status')}")
                if test_call.get("status") == "success":
                    print(f"Provider Used: {test_call.get('provider_used')}")
                    print(f"Response Preview: {test_call.get('response_preview')}")
                else:
                    print(f"Error: {test_call.get('error')}")
                    print(f"Error Type: {test_call.get('type')}")

            else:
                print(f"❌ Erro: Status {response.status_code}")
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Erro ao testar /debug/llm-config: {e}")

        # 2. Testar /debug/investigation/{id}/logs se tivermos um ID
        if environment == "Production":
            print("\n2️⃣  Testando /debug/investigation/logs...")
            # Use o ID da investigação que criamos anteriormente
            test_id = "c5757228-7b81-4490-bfa7-36faaf659e32"

            try:
                response = client.get(f"{base_url}/debug/investigation/{test_id}/logs")

                if response.status_code == 200:
                    data = response.json()

                    print("\n📝 LOGS DA INVESTIGAÇÃO:")
                    print("-" * 40)

                    status = data.get("status", {})
                    print(f"Status: {status.get('current_status')}")
                    print(f"Progress: {status.get('progress', 0)*100:.0f}%")
                    print(f"Phase: {status.get('current_phase')}")
                    print(f"Anomalies Found: {status.get('anomalies_found')}")

                    if status.get("error_message"):
                        print("\n❌ ERROR MESSAGE:")
                        print(status.get("error_message"))

                    # LLM info from investigation
                    llm_info = data.get("llm_info", {})
                    if llm_info:
                        print("\n💬 LLM INFO FROM INVESTIGATION:")
                        print(f"Provider: {llm_info.get('provider')}")
                        print(f"Model: {llm_info.get('model')}")
                        print(f"Response Time: {llm_info.get('llm_response_time')}")

                    # Current config for comparison
                    current_config = data.get("current_llm_config", {})
                    print("\n🔧 CURRENT LLM CONFIG:")
                    print(f"Provider: {current_config.get('provider')}")
                    print(f"Model: {current_config.get('model')}")
                    print(
                        f"Maritaca Configured: {current_config.get('maritaca_configured')}"
                    )

                else:
                    print(f"❌ Erro: Status {response.status_code}")

            except Exception as e:
                print(f"❌ Erro ao testar investigation logs: {e}")


if __name__ == "__main__":
    print("\n🚀 TESTE DE ENDPOINTS DE DEBUG")

    # Testar localmente
    print("\n" + "=" * 60)
    print("TESTANDO LOCALMENTE")
    print("=" * 60)
    test_debug_endpoints(LOCAL_URL, "Local")

    # Testar em produção
    print("\n" + "=" * 60)
    print("TESTANDO EM PRODUÇÃO")
    print("=" * 60)
    test_debug_endpoints(PRODUCTION_URL, "Production")

    print("\n✅ Testes concluídos!")
