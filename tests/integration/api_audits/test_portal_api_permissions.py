#!/usr/bin/env python3
"""
Test Portal da Transparência API Permissions

Systematically tests different endpoints to understand access restrictions.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime

import httpx

# API Configuration
API_KEY = "e24f842355f7211a2f4895e301aa5bca"
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


# Endpoints to test (ordered by complexity)
ENDPOINTS_TO_TEST = [
    {
        "name": "Despesas Públicas (simples)",
        "path": "/despesas/por-orgao",
        "params": {"mesAno": "08/2024", "pagina": 1},
        "description": "Public expenditures by agency - should be open access",
        "expected": "200 OK",
    },
    {
        "name": "Contratos (simples)",
        "path": "/contratos",
        "params": {"pagina": 1},
        "description": "Government contracts - should be open access",
        "expected": "200 OK",
    },
    {
        "name": "Servidores - Lista Paginada",
        "path": "/servidores",
        "params": {"pagina": 1},
        "description": "List all public servants (paginated, no filters)",
        "expected": "200 OK or 403",
    },
    {
        "name": "Servidores - Busca por Nome",
        "path": "/servidores",
        "params": {"nome": "MARIA SILVA", "pagina": 1},
        "description": "Search servants by name (documented but may not work)",
        "expected": "400 Bad Request or 403",
    },
    {
        "name": "Remuneração por CPF (CRÍTICO)",
        "path": "/servidores/09842860639/remuneracao",
        "params": {"mesAno": "08/2024"},
        "description": "Salary by CPF - THE endpoint we need for user query",
        "expected": "403 Forbidden (known issue)",
    },
    {
        "name": "Bolsa Família",
        "path": "/bolsa-familia-por-municipio",
        "params": {"mesAno": "202408", "codigoIbge": "310620", "pagina": 1},
        "description": "Social program data - BH municipality",
        "expected": "200 OK or 403",
    },
]


async def test_endpoint(client: httpx.AsyncClient, endpoint: dict) -> dict:
    """Test a single endpoint."""

    print(f"\n{Colors.BOLD}━━━ {endpoint['name']} ━━━{Colors.ENDC}\n")
    print(f"📍 Path: {endpoint['path']}")
    print(f"📋 Description: {endpoint['description']}")
    print(f"🎯 Expected: {endpoint['expected']}")
    print(f"🔧 Params: {json.dumps(endpoint['params'], ensure_ascii=False)}")

    url = f"{BASE_URL}{endpoint['path']}"

    start_time = datetime.now()

    try:
        response = await client.get(url, params=endpoint["params"], timeout=10.0)

        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n⏱️  Response time: {duration:.3f}s")
        print(f"📡 Status: {response.status_code} {response.reason_phrase}")

        # Analyze response
        result = {
            "name": endpoint["name"],
            "status_code": response.status_code,
            "duration": duration,
            "success": response.status_code == 200,
        }

        if response.status_code == 200:
            print_success("SUCCESS! Endpoint is accessible")

            # Try to parse JSON
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"📊 Response: List with {len(data)} items")
                    if len(data) > 0:
                        print(f"🔍 First item keys: {list(data[0].keys())[:5]}")
                elif isinstance(data, dict):
                    print(f"📊 Response: Dict with keys: {list(data.keys())[:10]}")
                    if "total" in data:
                        print(f"📈 Total records: {data.get('total')}")

                result["data_sample"] = str(data)[:200]

            except Exception as e:
                print_warning(f"Could not parse JSON: {e}")
                print(f"📄 Raw response (first 200 chars): {response.text[:200]}")

        elif response.status_code == 403:
            print_error("403 Forbidden - Access denied despite valid API key")
            result["error"] = "Forbidden"

        elif response.status_code == 400:
            print_warning("400 Bad Request - Invalid parameters")
            result["error"] = "Bad Request"
            try:
                error_data = response.json()
                print(
                    f"🔍 Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}"
                )
            except:
                print(f"📄 Error response: {response.text[:200]}")

        elif response.status_code == 404:
            print_warning("404 Not Found - Endpoint or resource doesn't exist")
            result["error"] = "Not Found"

        else:
            print_error(f"Unexpected status: {response.status_code}")
            result["error"] = response.reason_phrase

        return result

    except httpx.TimeoutException:
        print_error("Request timed out after 10s")
        return {
            "name": endpoint["name"],
            "status_code": 0,
            "duration": 10.0,
            "success": False,
            "error": "Timeout",
        }

    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return {
            "name": endpoint["name"],
            "status_code": 0,
            "duration": (datetime.now() - start_time).total_seconds(),
            "success": False,
            "error": str(e),
        }


async def test_api_key_validity():
    """Test if API key is valid by checking basic endpoint."""

    print_header("TESTE 1: VALIDAÇÃO DA API KEY")

    print_info(f"API Key: {'*' * 32}{API_KEY[-8:]}")
    print_info(f"Base URL: {BASE_URL}\n")

    # Test with simplest possible endpoint
    url = f"{BASE_URL}/despesas/por-orgao"
    params = {"mesAno": "08/2024", "pagina": 1, "tamanhoPagina": 1}

    async with httpx.AsyncClient(
        headers={
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0 Test",
        },
        timeout=10.0,
    ) as client:

        try:
            print_info("Testing: /despesas/por-orgao (public expenditures)")
            response = await client.get(url, params=params)

            print(f"Status: {response.status_code} {response.reason_phrase}")

            if response.status_code == 200:
                print_success("API KEY IS VALID! ✓")
                print_success("Portal API is accessible with this key\n")
                return True

            elif response.status_code == 401:
                print_error("401 Unauthorized - API key is INVALID or EXPIRED")
                print_info("Please verify your API key at:")
                print_info(
                    "https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email\n"
                )
                return False

            elif response.status_code == 403:
                print_warning("403 Forbidden - API key valid but access restricted")
                print_info("API key works but this specific endpoint is blocked\n")
                return True  # Key is valid, just restricted

            else:
                print_warning(f"Unexpected status: {response.status_code}")
                print_info("Cannot determine API key validity conclusively\n")
                return None

        except Exception as e:
            print_error(f"Request failed: {str(e)}\n")
            return False


async def test_all_endpoints():
    """Test all endpoints systematically."""

    print_header("TESTE 2: VERIFICAÇÃO DE PERMISSÕES POR ENDPOINT")

    results = []

    async with httpx.AsyncClient(
        headers={
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0 Test",
        },
        timeout=10.0,
    ) as client:

        for i, endpoint in enumerate(ENDPOINTS_TO_TEST, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(ENDPOINTS_TO_TEST)}]{Colors.ENDC}")
            result = await test_endpoint(client, endpoint)
            results.append(result)

            # Small delay between requests
            await asyncio.sleep(0.5)

    return results


def print_summary(results: list):
    """Print summary of all tests."""

    print_header("RESUMO FINAL")

    success_count = sum(1 for r in results if r.get("success"))
    forbidden_count = sum(1 for r in results if r.get("status_code") == 403)
    bad_request_count = sum(1 for r in results if r.get("status_code") == 400)
    error_count = sum(
        1
        for r in results
        if not r.get("success") and r.get("status_code") not in [403, 400]
    )

    print(f"📊 Total endpoints tested: {len(results)}")
    print(f"{Colors.OKGREEN}✅ Accessible (200 OK): {success_count}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Forbidden (403): {forbidden_count}{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠️  Bad Request (400): {bad_request_count}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Other errors: {error_count}{Colors.ENDC}\n")

    # Detailed breakdown
    print(f"{Colors.BOLD}━━━ DETALHAMENTO POR ENDPOINT ━━━{Colors.ENDC}\n")

    for result in results:
        name = result.get("name")
        status = result.get("status_code")

        if result.get("success"):
            print(f"{Colors.OKGREEN}✅ {name}: {status} OK{Colors.ENDC}")
        elif status == 403:
            print(f"{Colors.FAIL}❌ {name}: 403 Forbidden{Colors.ENDC}")
        elif status == 400:
            print(f"{Colors.WARNING}⚠️  {name}: 400 Bad Request{Colors.ENDC}")
        else:
            error = result.get("error", "Unknown")
            print(f"{Colors.FAIL}❌ {name}: {error}{Colors.ENDC}")

    # Critical analysis
    print(f"\n{Colors.BOLD}━━━ ANÁLISE CRÍTICA ━━━{Colors.ENDC}\n")

    remuneracao_result = next(
        (r for r in results if "Remuneração" in r.get("name")), None
    )

    if remuneracao_result:
        if remuneracao_result.get("status_code") == 403:
            print_error("ENDPOINT DE REMUNERAÇÃO ESTÁ BLOQUEADO (403 Forbidden)")
            print_info("Este é o endpoint crítico para a query do usuário:")
            print_info(
                '  "Quanto ganha a professora Aracele Garcia de Oliveira Fassbinder?"'
            )
            print_info("\nPossíveis causas:")
            print_info("  1. API key sem permissão para dados de servidores")
            print_info("  2. Endpoint requer autorização adicional")
            print_info("  3. Restrição por IP/região")
            print_info(
                "  4. Limitação documentada (78% dos endpoints do Portal são restritos)"
            )

        elif remuneracao_result.get("success"):
            print_success("ENDPOINT DE REMUNERAÇÃO ESTÁ ACESSÍVEL! ✓")
            print_info("Sistema pode buscar salários de servidores federais!")

    # Recommendation
    print(f"\n{Colors.BOLD}━━━ RECOMENDAÇÃO ━━━{Colors.ENDC}\n")

    if success_count > 0:
        print_success(f"API key funciona! {success_count} endpoint(s) acessível(is)")

        if forbidden_count > 0:
            print_warning(f"Mas {forbidden_count} endpoint(s) retornam 403 Forbidden")
            print_info("Solução: Usar APIs alternativas para dados bloqueados:")
            print_info("  • TCU (Tribunal de Contas da União)")
            print_info("  • Portais estaduais (TCE-CE, TCE-PE, TCE-MG)")
            print_info("  • ComprasNet / PNCP para contratos")
            print_info("  • SIAPE para salários (se houver API pública)")
    else:
        print_error("Nenhum endpoint acessível!")
        print_info("Possíveis ações:")
        print_info("  1. Verificar se API key está ativa")
        print_info("  2. Registrar nova API key")
        print_info("  3. Contatar suporte do Portal da Transparência")


async def main():
    """Run all API permission tests."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TESTE DE PERMISSÕES: API PORTAL DA TRANSPARÊNCIA{Colors.ENDC}")
    print(
        f"{Colors.BOLD}Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")

    print_info("💡 Objetivo: Entender quais endpoints são acessíveis com nossa API key")
    print_info("💡 Foco especial no endpoint de remuneração (query do usuário)\n")

    # Test 1: Validate API key
    api_key_valid = await test_api_key_validity()

    if api_key_valid is False:
        print_error("API key inválida! Interrompendo testes.")
        return 1

    # Test 2: Test all endpoints
    results = await test_all_endpoints()

    # Print summary
    print_summary(results)

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    # Determine exit code
    success_count = sum(1 for r in results if r.get("success"))
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Teste falhou: {str(e)}{Colors.ENDC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
