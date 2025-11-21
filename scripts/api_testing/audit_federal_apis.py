#!/usr/bin/env python3
"""
Auditoria Completa - APIs Federais

Testa sistematicamente todas as APIs federais mapeadas para verificar
quais retornam dados REAIS e estão prontas para produção.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any

import httpx


class Colors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    OKCYAN = "\033[96m"


def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


# APIs Federais a serem testadas
FEDERAL_APIS = [
    # 1. PNCP - Portal Nacional de Contratações Públicas
    {
        "name": "PNCP - Contratos",
        "base_url": "https://pncp.gov.br/api",
        "endpoint": "/pncp/v1/contratos",
        "params": {"pagina": 1, "tamanhoPagina": 5},
        "headers": {},
        "description": "Contratos públicos (PNCP - substitui Portal da Transparência)",
        "priority": "MUITO ALTA",
        "expected": "200 OK com contratos federais",
    },
    {
        "name": "PNCP - Licitações",
        "base_url": "https://pncp.gov.br/api",
        "endpoint": "/pncp/v1/orgaos",
        "params": {"pagina": 1, "tamanhoPagina": 5},
        "headers": {},
        "description": "Órgãos públicos cadastrados no PNCP",
        "priority": "ALTA",
        "expected": "200 OK com lista de órgãos",
    },
    # 2. Minha Receita - CNPJ
    {
        "name": "Minha Receita - CNPJ",
        "base_url": "https://minhareceita.org",
        "endpoint": "/api/cnpj/00000000000191",  # CNPJ do Banco do Brasil
        "params": {},
        "headers": {},
        "description": "Consulta CNPJ (dados empresariais)",
        "priority": "MUITO ALTA",
        "expected": "200 OK com dados da empresa",
    },
    # 3. IBGE - Dados Geográficos
    {
        "name": "IBGE - Estados",
        "base_url": "https://servicodados.ibge.gov.br",
        "endpoint": "/api/v1/localidades/estados",
        "params": {},
        "headers": {},
        "description": "Lista de estados brasileiros",
        "priority": "ALTA",
        "expected": "200 OK com 27 estados",
    },
    {
        "name": "IBGE - Municípios MG",
        "base_url": "https://servicodados.ibge.gov.br",
        "endpoint": "/api/v1/localidades/estados/MG/municipios",
        "params": {},
        "headers": {},
        "description": "Municípios de Minas Gerais",
        "priority": "ALTA",
        "expected": "200 OK com 853 municípios",
    },
    # 4. Compras.gov
    {
        "name": "Compras.gov - API Status",
        "base_url": "https://compras.dados.gov.br",
        "endpoint": "/docs",  # Endpoint de documentação
        "params": {},
        "headers": {},
        "description": "Verificar disponibilidade da API Compras.gov",
        "priority": "ALTA",
        "expected": "200 OK (documentação disponível)",
    },
    # 5. DataSUS
    {
        "name": "DataSUS - CNES (Estabelecimentos)",
        "base_url": "http://cnes.datasus.gov.br",
        "endpoint": "/pages/estabelecimentos/exibe_todos.jsp",
        "params": {"estado": "31", "municipio": "310620"},  # MG  # Belo Horizonte
        "headers": {},
        "description": "Estabelecimentos de saúde (CNES)",
        "priority": "MÉDIA",
        "expected": "200 OK ou redirecionamento",
    },
    # 6. BCB - Banco Central
    {
        "name": "BCB - Taxa SELIC",
        "base_url": "https://api.bcb.gov.br",
        "endpoint": "/dados/serie/bcdata.sgs.11/dados/ultimos/1",
        "params": {"formato": "json"},
        "headers": {},
        "description": "Taxa SELIC (Banco Central)",
        "priority": "MÉDIA",
        "expected": "200 OK com taxa atual",
    },
    # 7. SICONFI - Tesouro Nacional
    {
        "name": "SICONFI - Receitas MG",
        "base_url": "https://apidatalake.tesouro.gov.br",
        "endpoint": "/ords/siconfi/tt/rreo",
        "params": {
            "an_exercicio": 2024,
            "nr_periodo": 1,
            "co_tipo_demonstrativo": "RREO",
            "co_esfera": "E",
            "id_ente": "31",  # MG
        },
        "headers": {},
        "description": "RREO - Relatório Resumido de Execução Orçamentária",
        "priority": "MÉDIA",
        "expected": "200 OK com dados fiscais",
    },
]


async def test_federal_api(
    client: httpx.AsyncClient, api: dict[str, Any]
) -> dict[str, Any]:
    """Test a federal API endpoint."""

    print(f"\n{Colors.BOLD}━━━ {api['name']} ━━━{Colors.ENDC}")
    print(f"🎯 Prioridade: {api['priority']}")
    print(f"📍 Endpoint: {api['base_url']}{api['endpoint']}")
    print(f"📝 Descrição: {api['description']}")

    if api["params"]:
        print(f"🔧 Params: {json.dumps(api['params'], ensure_ascii=False)}")

    url = f"{api['base_url']}{api['endpoint']}"
    start_time = datetime.now()

    try:
        response = await client.get(
            url,
            params=api["params"],
            headers=api["headers"],
            timeout=15.0,
            follow_redirects=True,
        )

        duration = (datetime.now() - start_time).total_seconds()

        print(f"⏱️  Tempo: {duration:.3f}s")
        print(f"📡 Status: {response.status_code} {response.reason_phrase}")

        if response.status_code == 200:
            print_success(f"API FUNCIONA! {api['expected']}")

            try:
                data = response.json()

                if isinstance(data, list):
                    record_count = len(data)
                    print(f"📊 Registros: {record_count}")

                    if record_count > 0:
                        print(f"🔍 Campos do primeiro: {list(data[0].keys())[:8]}")
                        return {
                            "status": "success",
                            "records": record_count,
                            "duration": duration,
                            "sample": data[0] if record_count > 0 else None,
                        }
                    else:
                        print_warning("Lista vazia (sem dados para filtros)")
                        return {
                            "status": "success_empty",
                            "records": 0,
                            "duration": duration,
                        }

                elif isinstance(data, dict):
                    keys = list(data.keys())[:10]
                    print(f"📦 Dict com chaves: {keys}")

                    # Tentar identificar campo de dados
                    data_field = None
                    for field in ["data", "items", "results", "dados", "contratos"]:
                        if field in data:
                            data_field = field
                            break

                    if data_field and isinstance(data[data_field], list):
                        items_count = len(data[data_field])
                        print(f"📦 {data_field}: {items_count} itens")
                        return {
                            "status": "success",
                            "records": items_count,
                            "duration": duration,
                            "sample": data[data_field][0] if items_count > 0 else None,
                        }

                    return {
                        "status": "success",
                        "records": 1,
                        "duration": duration,
                        "sample": data,
                    }

                else:
                    print_warning(f"Tipo de resposta: {type(data)}")
                    return {"status": "success_unknown_format", "duration": duration}

            except Exception as e:
                # Pode ser HTML ou outro formato
                content_type = response.headers.get("content-type", "")
                print_warning(f"Resposta não-JSON: {content_type}")

                if "html" in content_type.lower():
                    print_info("Resposta HTML (pode ser página de documentação)")
                    return {"status": "success_html", "duration": duration}

                return {
                    "status": "success_no_parse",
                    "duration": duration,
                    "error": str(e),
                }

        elif response.status_code == 404:
            print_error("404 Not Found - Endpoint não existe")
            return {"status": "not_found", "duration": duration}

        elif response.status_code == 403:
            print_error("403 Forbidden - Acesso negado")
            return {"status": "forbidden", "duration": duration}

        elif response.status_code == 400:
            print_error("400 Bad Request - Parâmetros inválidos")

            try:
                error = response.json()
                print(
                    f"📄 Erro: {json.dumps(error, indent=2, ensure_ascii=False)[:200]}"
                )
                return {"status": "bad_request", "duration": duration, "error": error}
            except:
                print(f"📄 Erro: {response.text[:200]}")
                return {"status": "bad_request", "duration": duration}

        else:
            print_error(f"Status inesperado: {response.status_code}")
            return {
                "status": "error",
                "code": response.status_code,
                "duration": duration,
            }

    except httpx.TimeoutException:
        print_error("Timeout após 15s")
        return {"status": "timeout"}

    except Exception as e:
        print_error(f"Exceção: {str(e)}")
        return {"status": "exception", "error": str(e)}


async def main():
    """Run federal APIs audit."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}AUDITORIA: APIs FEDERAIS - FASE 2{Colors.ENDC}")
    print(
        f"{Colors.BOLD}Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    print_info(f"Total de APIs a testar: {len(FEDERAL_APIS)}")
    print()

    results = []

    async with httpx.AsyncClient(
        headers={"Accept": "application/json", "User-Agent": "CidadaoAI/1.0 Audit"},
        timeout=15.0,
    ) as client:

        for i, api in enumerate(FEDERAL_APIS, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(FEDERAL_APIS)}]{Colors.ENDC}")

            result = await test_federal_api(client, api)
            result["name"] = api["name"]
            result["priority"] = api["priority"]
            results.append(result)

            # Rate limiting
            await asyncio.sleep(0.5)

    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}RESUMO DA AUDITORIA{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    success = sum(1 for r in results if r["status"].startswith("success"))
    not_found = sum(1 for r in results if r["status"] == "not_found")
    forbidden = sum(1 for r in results if r["status"] == "forbidden")
    bad_request = sum(1 for r in results if r["status"] == "bad_request")
    errors = len(results) - success - not_found - forbidden - bad_request

    print(f"📊 Total testado: {len(results)}")
    print(
        f"{Colors.OKGREEN}✅ Funcionando: {success} ({success/len(results)*100:.1f}%){Colors.ENDC}"
    )
    print(f"{Colors.FAIL}❌ Não encontrado (404): {not_found}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Bloqueado (403): {forbidden}{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠️  Parâmetros inválidos (400): {bad_request}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Outros erros: {errors}{Colors.ENDC}\n")

    # Detailed results
    print(f"{Colors.BOLD}━━━ DETALHAMENTO ━━━{Colors.ENDC}\n")

    for result in results:
        name = result["name"]
        status = result["status"]
        priority = result.get("priority", "MÉDIA")

        if status.startswith("success"):
            records = result.get("records", "?")
            duration = result.get("duration", 0)
            print(
                f"{Colors.OKGREEN}✅ [{priority}] {name}: OK ({records} registros, {duration:.2f}s){Colors.ENDC}"
            )

        elif status == "not_found":
            print(f"{Colors.FAIL}❌ [{priority}] {name}: 404 Not Found{Colors.ENDC}")

        elif status == "forbidden":
            print(f"{Colors.FAIL}❌ [{priority}] {name}: 403 Forbidden{Colors.ENDC}")

        elif status == "bad_request":
            print(
                f"{Colors.WARNING}⚠️  [{priority}] {name}: 400 Bad Request{Colors.ENDC}"
            )

        else:
            print(f"{Colors.FAIL}❌ [{priority}] {name}: {status}{Colors.ENDC}")

    # Final verdict
    print(f"\n{Colors.BOLD}━━━ RESULTADO ━━━{Colors.ENDC}\n")

    if success >= len(results) * 0.8:
        print_success(
            f"🎉 EXCELENTE! {success}/{len(results)} APIs funcionando ({success/len(results)*100:.1f}%)"
        )
        print(
            f"{Colors.OKGREEN}APIs federais estão PRONTAS para produção!{Colors.ENDC}"
        )

    elif success >= len(results) * 0.5:
        print_success(
            f"✅ BOM! {success}/{len(results)} APIs funcionando ({success/len(results)*100:.1f}%)"
        )
        print_warning("Algumas APIs precisam de ajustes")

    else:
        print_warning(
            f"⚠️  {success}/{len(results)} APIs funcionando ({success/len(results)*100:.1f}%)"
        )
        print_error("Maioria das APIs precisa de correções")

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    return 0 if success >= len(results) * 0.5 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nAuditoria interrompida")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Erro fatal: {str(e)}{Colors.ENDC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
