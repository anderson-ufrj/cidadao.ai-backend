#!/usr/bin/env python3
"""
Teste dos 7 Endpoints Corrigidos - Portal da Transparência

Testa os endpoints que retornavam 400 Bad Request com os parâmetros corretos.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta

import httpx

# API Configuration
API_KEY = "***REDACTED-TRANSPARENCY-KEY***"
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"


class Colors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


# Calculate date ranges
today = datetime.now()
one_month_ago = today - timedelta(days=30)
date_start = one_month_ago.strftime("%d/%m/%Y")
date_end = today.strftime("%d/%m/%Y")
mes_ano_hoje = today.strftime("%m/%Y")
mes_ano_passado = one_month_ago.strftime("%m/%Y")

# Corrected endpoints with proper parameters
CORRECTED_ENDPOINTS = [
    {
        "name": "1. Servidores - Lista (com código SIAPE)",
        "path": "/servidores",
        "params": {"codigoOrgaoLotacao": "36000", "pagina": 1, "tamanhoPagina": 5},
        "before": "400 - Faltava codigoOrgaoLotacao",
        "expected": "200 OK",
    },
    {
        "name": "2. Licitações (com datas - 30 dias)",
        "path": "/licitacoes",
        "params": {
            "codigoOrgao": "26000",
            "dataInicial": date_start,
            "dataFinal": date_end,
            "pagina": 1,
            "tamanhoPagina": 5,
        },
        "before": "400 - Faltava período de datas",
        "expected": "200 OK",
    },
    {
        "name": "3. Despesas - Documentos (com data de emissão)",
        "path": "/despesas/documentos",
        "params": {
            "codigoOrgao": "36000",
            "ano": 2024,
            "dataEmissao": "01/08/2024",
            "pagina": 1,
            "tamanhoPagina": 5,
        },
        "before": "400 - Faltava dataEmissao",
        "expected": "200 OK",
    },
    {
        "name": "4. Despesas - Por Órgão (com código)",
        "path": "/despesas/por-orgao",
        "params": {
            "ano": 2024,
            "mes": 8,
            "codigoOrgao": "36000",
            "pagina": 1,
            "tamanhoPagina": 5,
        },
        "before": "400 - Faltava codigoOrgao",
        "expected": "200 OK",
    },
    {
        "name": "5. Convênios (com UF)",
        "path": "/convenios",
        "params": {"uf": "MG", "pagina": 1, "tamanhoPagina": 5},
        "before": "400 - Faltava filtro (UF/município/órgão)",
        "expected": "200 OK",
    },
    {
        "name": "6. Cartões Corporativos (com órgão)",
        "path": "/cartoes",
        "params": {
            "mesAno": "202408",
            "codigoOrgao": "36000",
            "pagina": 1,
            "tamanhoPagina": 5,
        },
        "before": "400 - Faltava codigoOrgao",
        "expected": "200 OK",
    },
    {
        "name": "7. Viagens (com datas de ida)",
        "path": "/viagens",
        "params": {
            "dataIdaDe": date_start,
            "dataIdaAte": date_end,
            "pagina": 1,
            "tamanhoPagina": 5,
        },
        "before": "400 - Faltava dataIdaDe/dataIdaAte",
        "expected": "200 OK",
    },
]


async def test_corrected_endpoint(client, endpoint):
    """Test a corrected endpoint."""

    print(f"\n{Colors.BOLD}━━━ {endpoint['name']} ━━━{Colors.ENDC}")
    print(f"📍 Path: {endpoint['path']}")
    print(f"⚠️  Antes: {endpoint['before']}")
    print(f"🎯 Esperado: {endpoint['expected']}")
    print(
        f"🔧 Parâmetros corrigidos: {json.dumps(endpoint['params'], ensure_ascii=False)}"
    )

    url = f"{BASE_URL}{endpoint['path']}"
    start_time = datetime.now()

    try:
        response = await client.get(url, params=endpoint["params"], timeout=15.0)
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n⏱️  Tempo: {duration:.3f}s")
        print(f"📡 Status: {response.status_code} {response.reason_phrase}")

        if response.status_code == 200:
            print_success("CORRIGIDO! Endpoint agora retorna dados REAIS")

            try:
                data = response.json()

                if isinstance(data, list):
                    record_count = len(data)
                    print(f"📊 Registros: {record_count}")

                    if record_count > 0:
                        print(f"🔍 Campos: {list(data[0].keys())[:8]}")
                        first_key = list(data[0].keys())[0]
                        print(f"💾 Exemplo: {first_key} = {data[0][first_key]}")
                        return {"status": "success", "records": record_count}
                    else:
                        print_warning("Lista vazia (sem dados para filtros)")
                        return {"status": "success_empty", "records": 0}

                elif isinstance(data, dict):
                    print(f"📊 Dict: {list(data.keys())[:10]}")
                    if "data" in data or "items" in data or "results" in data:
                        items_key = (
                            "data"
                            if "data" in data
                            else "items" if "items" in data else "results"
                        )
                        items = data[items_key]
                        print(f"📦 Items: {len(items)} registros")
                        return {"status": "success", "records": len(items)}
                    return {"status": "success", "records": 1}

            except Exception as e:
                print_warning(f"Erro ao parsear JSON: {e}")
                return {"status": "success_no_parse", "records": 0}

        elif response.status_code == 403:
            print_error(
                "403 Forbidden - Endpoint ainda bloqueado (não é erro de parâmetros)"
            )
            return {"status": "forbidden"}

        elif response.status_code == 400:
            print_error("400 Bad Request - AINDA HÁ ERRO DE PARÂMETROS")

            try:
                error_data = response.json()
                print(
                    f"🔍 Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}"
                )
                return {"status": "bad_request", "error": error_data}
            except:
                print(f"📄 Erro: {response.text[:300]}")
                return {"status": "bad_request", "error": response.text[:300]}

        elif response.status_code == 404:
            print_warning(
                "404 Not Found - Endpoint não existe ou dados não encontrados"
            )
            return {"status": "not_found"}

        else:
            print_error(f"Status inesperado: {response.status_code}")
            return {"status": "error", "code": response.status_code}

    except httpx.TimeoutException:
        print_error("Timeout após 15s")
        return {"status": "timeout"}

    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return {"status": "exception", "error": str(e)}


async def main():
    """Test all corrected endpoints."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(
        f"{Colors.BOLD}TESTE: 7 ENDPOINTS CORRIGIDOS - PORTAL DA TRANSPARÊNCIA{Colors.ENDC}"
    )
    print(
        f"{Colors.BOLD}Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")

    results = []

    async with httpx.AsyncClient(
        headers={
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0 Test",
        },
        timeout=15.0,
    ) as client:

        for i, endpoint in enumerate(CORRECTED_ENDPOINTS, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(CORRECTED_ENDPOINTS)}]{Colors.ENDC}")
            result = await test_corrected_endpoint(client, endpoint)
            result["name"] = endpoint["name"]
            results.append(result)
            await asyncio.sleep(0.7)

    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}RESUMO FINAL{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    success = sum(1 for r in results if r["status"].startswith("success"))
    forbidden = sum(1 for r in results if r["status"] == "forbidden")
    bad_request = sum(1 for r in results if r["status"] == "bad_request")
    errors = sum(
        1
        for r in results
        if r["status"]
        not in [
            "success",
            "success_empty",
            "success_no_parse",
            "forbidden",
            "bad_request",
        ]
    )

    print(f"📊 Total testado: {len(results)}")
    print(f"{Colors.OKGREEN}✅ Corrigidos (200 OK): {success}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Ainda bloqueados (403): {forbidden}{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠️  Ainda com erro (400): {bad_request}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Outros erros: {errors}{Colors.ENDC}\n")

    # Detailed results
    print(f"{Colors.BOLD}━━━ DETALHAMENTO ━━━{Colors.ENDC}\n")

    for result in results:
        name = result.get("name")
        status = result.get("status")

        if status in ["success", "success_empty", "success_no_parse"]:
            records = result.get("records", "?")
            print(f"{Colors.OKGREEN}✅ {name}: OK ({records} registros){Colors.ENDC}")
        elif status == "forbidden":
            print(f"{Colors.FAIL}❌ {name}: 403 Forbidden{Colors.ENDC}")
        elif status == "bad_request":
            print(
                f"{Colors.WARNING}⚠️  {name}: 400 Bad Request (ainda incorreto){Colors.ENDC}"
            )
        else:
            print(f"{Colors.FAIL}❌ {name}: {status}{Colors.ENDC}")

    # Final verdict
    print(f"\n{Colors.BOLD}━━━ RESULTADO ━━━{Colors.ENDC}\n")

    if success == len(results):
        print_success(f"🎉 PERFEITO! Todos os {success} endpoints foram corrigidos!")
        print(
            f"{Colors.OKGREEN}Sistema agora tem acesso a MAIS dados reais!{Colors.ENDC}"
        )
        total_working = 6 + success  # 6 que já funcionavam + corrigidos
        print(
            f"{Colors.OKGREEN}Total de endpoints funcionais: {total_working}/17 ({total_working/17*100:.1f}%){Colors.ENDC}"
        )

    elif success > 0:
        print_success(f"{success}/{len(results)} endpoints corrigidos com sucesso")

        if forbidden > 0:
            print_warning(
                f"{forbidden} endpoints ainda bloqueados (403 - não é erro nosso)"
            )

        if bad_request > 0:
            print_error(
                f"{bad_request} endpoints ainda com erro 400 (precisam de mais ajustes)"
            )

    else:
        print_error("Nenhum endpoint foi corrigido")
        print_warning("Verificar se os parâmetros estão corretos")

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    return 0 if success >= 5 else 1  # Sucesso se pelo menos 5 funcionarem


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Teste falhou: {str(e)}{Colors.ENDC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
