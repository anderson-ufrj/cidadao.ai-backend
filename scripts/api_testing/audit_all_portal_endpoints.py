#!/usr/bin/env python3
"""
Auditoria Completa: Portal da Transparência - Todos os 17 Endpoints

Testa sistematicamente TODOS os endpoints mapeados com parâmetros realistas
para identificar quais retornam dados REAIS.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any

import httpx

# API Configuration
API_KEY = "***REDACTED-TRANSPARENCY-KEY***"
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


# Complete endpoint configuration with realistic test parameters
ENDPOINTS_TO_TEST = [
    # ========== SERVIDORES (Public Servants) ==========
    {
        "name": "Servidores - Lista",
        "category": "SERVIDORES",
        "path": "/servidores",
        "params": {"pagina": 1, "tamanhoPagina": 10},
        "description": "Lista de servidores públicos federais",
        "expected": "400 or 403 (requires specific filters)",
        "priority": "HIGH",
    },
    {
        "name": "Servidores - Remuneração (CPF)",
        "category": "SERVIDORES",
        "path": "/servidores/09842860639/remuneracao",
        "params": {"mesAno": "08/2024"},
        "description": "Remuneração de servidor por CPF",
        "expected": "403 Forbidden (known limitation)",
        "priority": "CRITICAL",
    },
    # ========== CONTRATOS (Contracts) ==========
    {
        "name": "Contratos - Ministério da Saúde",
        "category": "CONTRATOS",
        "path": "/contratos",
        "params": {"codigoOrgao": "36000", "pagina": 1, "tamanhoPagina": 10},
        "description": "Contratos do Ministério da Saúde",
        "expected": "200 OK or 403",
        "priority": "HIGH",
    },
    # ========== LICITAÇÕES (Bids) ==========
    {
        "name": "Licitações - Ministério da Educação",
        "category": "LICITAÇÕES",
        "path": "/licitacoes",
        "params": {"codigoOrgao": "26000", "pagina": 1, "tamanhoPagina": 10},
        "description": "Licitações do Ministério da Educação",
        "expected": "200 OK or 403",
        "priority": "MEDIUM",
    },
    # ========== DESPESAS (Expenses) ==========
    {
        "name": "Despesas - Documentos",
        "category": "DESPESAS",
        "path": "/despesas/documentos",
        "params": {
            "codigoOrgao": "36000",
            "ano": 2024,
            "pagina": 1,
            "tamanhoPagina": 10,
        },
        "description": "Despesas por documento - Ministério da Saúde",
        "expected": "200 OK or 400/403",
        "priority": "HIGH",
    },
    {
        "name": "Despesas - Por Órgão",
        "category": "DESPESAS",
        "path": "/despesas/por-orgao",
        "params": {"ano": 2024, "mes": 8, "pagina": 1, "tamanhoPagina": 10},
        "description": "Despesas agrupadas por órgão",
        "expected": "200 OK or 400",
        "priority": "HIGH",
    },
    # ========== FORNECEDORES (Suppliers) ==========
    {
        "name": "Fornecedores - Lista",
        "category": "FORNECEDORES",
        "path": "/fornecedores",
        "params": {"pagina": 1, "tamanhoPagina": 10},
        "description": "Lista de fornecedores do governo",
        "expected": "200 OK or 403",
        "priority": "MEDIUM",
    },
    # ========== CONVÊNIOS (Agreements) ==========
    {
        "name": "Convênios",
        "category": "CONVÊNIOS",
        "path": "/convenios",
        "params": {"pagina": 1, "tamanhoPagina": 10},
        "description": "Convênios federais",
        "expected": "200 OK or 403",
        "priority": "MEDIUM",
    },
    # ========== CARTÕES DE PAGAMENTO (Payment Cards) ==========
    {
        "name": "Cartões Corporativos",
        "category": "CARTÕES",
        "path": "/cartoes",
        "params": {"mesAno": "202408", "pagina": 1, "tamanhoPagina": 10},
        "description": "Gastos com cartões corporativos",
        "expected": "200 OK or 403",
        "priority": "MEDIUM",
    },
    # ========== VIAGENS (Travel) ==========
    {
        "name": "Viagens",
        "category": "VIAGENS",
        "path": "/viagens",
        "params": {"pagina": 1, "tamanhoPagina": 10},
        "description": "Viagens a serviço",
        "expected": "200 OK or 403",
        "priority": "LOW",
    },
    # ========== EMENDAS PARLAMENTARES (Parliamentary Amendments) ==========
    {
        "name": "Emendas Parlamentares",
        "category": "EMENDAS",
        "path": "/emendas",
        "params": {"ano": 2024, "pagina": 1, "tamanhoPagina": 10},
        "description": "Emendas parlamentares",
        "expected": "200 OK or 403",
        "priority": "MEDIUM",
    },
    # ========== PROGRAMAS SOCIAIS (Social Programs) ==========
    {
        "name": "Auxílio Emergencial",
        "category": "PROGRAMAS SOCIAIS",
        "path": "/auxilio-emergencial",
        "params": {"mesAno": "202008", "pagina": 1, "tamanhoPagina": 10},
        "description": "Beneficiários do auxílio emergencial (COVID-19)",
        "expected": "200 OK or 404 (program ended)",
        "priority": "LOW",
    },
    {
        "name": "Bolsa Família - BH",
        "category": "PROGRAMAS SOCIAIS",
        "path": "/bolsa-familia-por-municipio",
        "params": {
            "mesAno": "202408",
            "codigoIbge": "3106200",
            "pagina": 1,
            "tamanhoPagina": 10,
        },
        "description": "Bolsa Família em Belo Horizonte",
        "expected": "200 OK (known to work)",
        "priority": "CRITICAL",
    },
    {
        "name": "BPC - BH",
        "category": "PROGRAMAS SOCIAIS",
        "path": "/bpc-por-municipio",
        "params": {
            "mesAno": "202408",
            "codigoIbge": "3106200",
            "pagina": 1,
            "tamanhoPagina": 10,
        },
        "description": "BPC (Benefício de Prestação Continuada) em BH",
        "expected": "200 OK",
        "priority": "HIGH",
    },
    # ========== SANÇÕES (Sanctions) ==========
    {
        "name": "CEIS - Empresas Inidôneas",
        "category": "SANÇÕES",
        "path": "/ceis",
        "params": {"pagina": 1, "tamanhoPagina": 10},
        "description": "Cadastro de Empresas Inidôneas e Suspensas",
        "expected": "200 OK",
        "priority": "HIGH",
    },
    {
        "name": "CNEP - Empresas Punidas",
        "category": "SANÇÕES",
        "path": "/cnep",
        "params": {"pagina": 1, "tamanhoPagina": 10},
        "description": "Cadastro Nacional de Empresas Punidas",
        "expected": "200 OK",
        "priority": "HIGH",
    },
    # ========== SEGURO DEFESO (Fishing Insurance) ==========
    {
        "name": "Seguro Defeso",
        "category": "SEGURO DEFESO",
        "path": "/seguro-defeso",
        "params": {"mesAno": "202408", "pagina": 1, "tamanhoPagina": 10},
        "description": "Seguro defeso de pescadores",
        "expected": "200 OK or 403",
        "priority": "LOW",
    },
]


async def test_endpoint(client: httpx.AsyncClient, endpoint: dict) -> dict[str, Any]:
    """Test a single endpoint with realistic parameters."""

    print(f"\n{Colors.BOLD}━━━ {endpoint['name']} ━━━{Colors.ENDC}")
    print(f"📂 Category: {endpoint['category']}")
    print(f"📍 Path: {endpoint['path']}")
    print(f"📋 Description: {endpoint['description']}")
    print(f"🎯 Expected: {endpoint['expected']}")
    print(f"⭐ Priority: {endpoint['priority']}")
    print(f"🔧 Params: {json.dumps(endpoint['params'], ensure_ascii=False)}")

    url = f"{BASE_URL}{endpoint['path']}"
    start_time = datetime.now()

    try:
        response = await client.get(url, params=endpoint["params"], timeout=15.0)

        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n⏱️  Response time: {duration:.3f}s")
        print(f"📡 Status: {response.status_code} {response.reason_phrase}")

        result = {
            "name": endpoint["name"],
            "category": endpoint["category"],
            "priority": endpoint["priority"],
            "status_code": response.status_code,
            "duration": duration,
            "success": response.status_code == 200,
            "path": endpoint["path"],
            "params": endpoint["params"],
        }

        if response.status_code == 200:
            print_success("SUCCESS! Endpoint retorna dados REAIS")

            try:
                data = response.json()

                # Analyze data structure
                if isinstance(data, list):
                    record_count = len(data)
                    print(f"📊 Response: Lista com {record_count} registros")

                    if record_count > 0:
                        print(f"🔍 Primeiro registro: {list(data[0].keys())[:10]}")
                        result["sample_data"] = data[0]
                        result["record_count"] = record_count

                        # Show a sample value
                        if len(data[0]) > 0:
                            first_key = list(data[0].keys())[0]
                            first_value = data[0][first_key]
                            print(f"💾 Exemplo: {first_key} = {first_value}")
                    else:
                        print_warning("Lista vazia (sem dados para o período/filtro)")
                        result["record_count"] = 0

                elif isinstance(data, dict):
                    print(f"📊 Response: Dict com keys: {list(data.keys())[:10]}")

                    # Check for pagination metadata
                    if "total" in data:
                        print(f"📈 Total de registros: {data.get('total')}")
                        result["total_records"] = data.get("total")

                    if "data" in data or "results" in data or "items" in data:
                        items_key = (
                            "data"
                            if "data" in data
                            else "results" if "results" in data else "items"
                        )
                        items = data[items_key]
                        print(f"📦 Items: {len(items)} registros")
                        result["record_count"] = len(items)
                        if len(items) > 0:
                            result["sample_data"] = items[0]
                    else:
                        result["sample_data"] = {
                            k: v for k, v in list(data.items())[:3]
                        }

            except Exception as e:
                print_warning(f"Não foi possível parsear JSON: {e}")
                print(f"📄 Raw response (primeiros 200 chars): {response.text[:200]}")
                result["parse_error"] = str(e)

        elif response.status_code == 403:
            print_error("403 Forbidden - Acesso negado (API key sem permissão)")
            result["error"] = "Forbidden - API key requires upgrade"

        elif response.status_code == 400:
            print_warning("400 Bad Request - Parâmetros inválidos")

            try:
                error_data = response.json()
                error_msg = json.dumps(error_data, indent=2, ensure_ascii=False)
                print(f"🔍 Detalhes do erro:\n{error_msg}")
                result["error"] = error_data
            except:
                print(f"📄 Error response: {response.text[:300]}")
                result["error"] = response.text[:300]

        elif response.status_code == 404:
            print_warning("404 Not Found - Endpoint ou recurso não encontrado")
            result["error"] = "Not Found"

        else:
            print_error(f"Status inesperado: {response.status_code}")
            result["error"] = response.reason_phrase

        return result

    except httpx.TimeoutException:
        print_error("Request timeout após 15s")
        return {
            "name": endpoint["name"],
            "category": endpoint["category"],
            "priority": endpoint["priority"],
            "status_code": 0,
            "duration": 15.0,
            "success": False,
            "error": "Timeout",
        }

    except Exception as e:
        print_error(f"Request falhou: {str(e)}")
        return {
            "name": endpoint["name"],
            "category": endpoint["category"],
            "priority": endpoint["priority"],
            "status_code": 0,
            "duration": (datetime.now() - start_time).total_seconds(),
            "success": False,
            "error": str(e),
        }


async def audit_all_endpoints():
    """Test all Portal da Transparência endpoints."""

    print_header("AUDITORIA COMPLETA: PORTAL DA TRANSPARÊNCIA - 17 ENDPOINTS")

    print_info(f"API Key: {'*' * 32}{API_KEY[-8:]}")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Total endpoints: {len(ENDPOINTS_TO_TEST)}\n")

    results = []

    async with httpx.AsyncClient(
        headers={
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0 Audit",
        },
        timeout=15.0,
    ) as client:

        for i, endpoint in enumerate(ENDPOINTS_TO_TEST, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(ENDPOINTS_TO_TEST)}]{Colors.ENDC}")

            result = await test_endpoint(client, endpoint)
            results.append(result)

            # Small delay between requests
            await asyncio.sleep(0.7)

    return results


def print_summary(results: list[dict]):
    """Print comprehensive summary of audit."""

    print_header("RESUMO FINAL DA AUDITORIA")

    # Overall statistics
    total = len(results)
    success = sum(1 for r in results if r.get("success"))
    forbidden = sum(1 for r in results if r.get("status_code") == 403)
    bad_request = sum(1 for r in results if r.get("status_code") == 400)
    not_found = sum(1 for r in results if r.get("status_code") == 404)
    errors = sum(
        1
        for r in results
        if not r.get("success") and r.get("status_code") not in [403, 400, 404]
    )

    print(f"📊 Total de endpoints testados: {total}")
    print(
        f"{Colors.OKGREEN}✅ Retornam dados REAIS (200 OK): {success} ({success/total*100:.1f}%){Colors.ENDC}"
    )
    print(
        f"{Colors.FAIL}❌ Bloqueados (403 Forbidden): {forbidden} ({forbidden/total*100:.1f}%){Colors.ENDC}"
    )
    print(
        f"{Colors.WARNING}⚠️  Parâmetros inválidos (400): {bad_request} ({bad_request/total*100:.1f}%){Colors.ENDC}"
    )
    print(
        f"{Colors.WARNING}⚠️  Não encontrado (404): {not_found} ({not_found/total*100:.1f}%){Colors.ENDC}"
    )
    print(f"{Colors.FAIL}❌ Outros erros: {errors}{Colors.ENDC}\n")

    # Group by category
    print(f"{Colors.BOLD}━━━ RESULTADOS POR CATEGORIA ━━━{Colors.ENDC}\n")

    categories = {}
    for result in results:
        cat = result.get("category", "UNKNOWN")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)

    for category, cat_results in sorted(categories.items()):
        cat_success = sum(1 for r in cat_results if r.get("success"))
        cat_total = len(cat_results)

        print(
            f"\n{Colors.BOLD}{category}:{Colors.ENDC} {cat_success}/{cat_total} funcionando"
        )

        for result in cat_results:
            name = result.get("name")
            status = result.get("status_code")
            priority = result.get("priority")

            priority_icon = (
                "🔴"
                if priority == "CRITICAL"
                else (
                    "🟠"
                    if priority == "HIGH"
                    else "🟡" if priority == "MEDIUM" else "⚪"
                )
            )

            if result.get("success"):
                record_count = result.get("record_count", "?")
                print(
                    f"  {priority_icon} {Colors.OKGREEN}✅ {name}: {status} OK ({record_count} registros){Colors.ENDC}"
                )
            elif status == 403:
                print(
                    f"  {priority_icon} {Colors.FAIL}❌ {name}: 403 Forbidden{Colors.ENDC}"
                )
            elif status == 400:
                print(
                    f"  {priority_icon} {Colors.WARNING}⚠️  {name}: 400 Bad Request{Colors.ENDC}"
                )
            elif status == 404:
                print(
                    f"  {priority_icon} {Colors.WARNING}⚠️  {name}: 404 Not Found{Colors.ENDC}"
                )
            else:
                error = result.get("error", "Unknown")
                print(f"  {priority_icon} {Colors.FAIL}❌ {name}: {error}{Colors.ENDC}")

    # Working endpoints
    print(
        f"\n{Colors.BOLD}━━━ ENDPOINTS QUE FUNCIONAM (DADOS REAIS) ━━━{Colors.ENDC}\n"
    )

    working = [r for r in results if r.get("success")]

    if working:
        for result in working:
            print(f"{Colors.OKGREEN}✅ {result['name']}{Colors.ENDC}")
            print(f"   Path: {result['path']}")
            print(f"   Params: {json.dumps(result['params'], ensure_ascii=False)}")
            print(f"   Registros: {result.get('record_count', '?')}")
            print()
    else:
        print_error("Nenhum endpoint retornando dados!")

    # Recommendations
    print(f"{Colors.BOLD}━━━ RECOMENDAÇÕES ━━━{Colors.ENDC}\n")

    if success > 0:
        print_success(
            f"{success} endpoints funcionando! Sistema pode buscar dados reais."
        )
        print_info("\n✓ Usar esses endpoints para queries do usuário")
        print_info("✓ Implementar fallbacks para endpoints bloqueados")
        print_info("✓ Cachear dados dos endpoints funcionais")

        if forbidden > 0:
            print_warning(f"\n{forbidden} endpoints bloqueados (403 Forbidden)")
            print_info("→ Solicitar upgrade da API key")
            print_info("→ Usar APIs alternativas (TCU, TCE estaduais)")
    else:
        print_error("NENHUM endpoint acessível!")
        print_info("\nAções necessárias:")
        print_info("1. Verificar se API key está ativa")
        print_info("2. Solicitar nova API key ou upgrade")
        print_info("3. Usar exclusivamente APIs alternativas")


async def main():
    """Run complete Portal da Transparência audit."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(
        f"{Colors.BOLD}AUDITORIA: PORTAL DA TRANSPARÊNCIA - TODOS OS ENDPOINTS{Colors.ENDC}"
    )
    print(
        f"{Colors.BOLD}Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")

    results = await audit_all_endpoints()

    print_summary(results)

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    # Exit code
    success_count = sum(1 for r in results if r.get("success"))
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nAuditoria interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Auditoria falhou: {str(e)}{Colors.ENDC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
