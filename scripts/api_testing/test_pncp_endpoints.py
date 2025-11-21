#!/usr/bin/env python3
"""
Teste: Descobrir endpoints corretos do PNCP

Testa diferentes variações de endpoints para encontrar o correto para contratos.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime

import httpx


class Colors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    OKCYAN = "\033[96m"


# Diferentes variações de endpoints para testar
PNCP_ENDPOINTS = [
    # Baseado no padrão que funciona
    {
        "name": "Órgãos (confirmado funcionando)",
        "path": "/api/pncp/v1/orgaos",
        "params": {"pagina": 1, "tamanhoPagina": 5},
    },
    # Tentativas para contratos
    {
        "name": "Contratos v1 (simples)",
        "path": "/api/pncp/v1/contratos",
        "params": {"pagina": 1, "tamanhoPagina": 5},
    },
    {
        "name": "Contratos API consulta",
        "path": "/api/consulta/v1/contratos",
        "params": {"pagina": 1, "tamanhoPagina": 5},
    },
    {
        "name": "Contratos pncp-api",
        "path": "/pncp-api/v1/contratos",
        "params": {"pagina": 1, "tamanhoPagina": 5},
    },
    # Com data (padrão comum em APIs)
    {
        "name": "Contratos com data publicação",
        "path": "/api/pncp/v1/contratos",
        "params": {
            "dataInicial": "01/01/2024",
            "dataFinal": "31/01/2024",
            "pagina": 1,
            "tamanhoPagina": 5,
        },
    },
    # Por órgão específico (baseado no exemplo que vimos na busca)
    {
        "name": "Contratos por órgão (CNPJ Petrobras)",
        "path": "/pncp-api/v1/orgaos/33000167000101/contratos/2024",
        "params": {},
    },
    {
        "name": "Contratos por órgão v2 (CNPJ genérico)",
        "path": "/api/pncp/v1/orgaos/00000000000191/contratos",
        "params": {"ano": 2024, "pagina": 1},
    },
    # Licitações (pode ser útil também)
    {
        "name": "Licitações",
        "path": "/api/pncp/v1/licitacoes",
        "params": {"pagina": 1, "tamanhoPagina": 5},
    },
    {
        "name": "Licitações com data",
        "path": "/api/pncp/v1/licitacoes",
        "params": {"dataInicial": "01/01/2024", "dataFinal": "31/01/2024", "pagina": 1},
    },
    # Compras (alternativa)
    {
        "name": "Compras",
        "path": "/api/pncp/v1/compras",
        "params": {"pagina": 1, "tamanhoPagina": 5},
    },
]


async def test_endpoint(client: httpx.AsyncClient, endpoint: dict, base_url: str):
    """Test a single PNCP endpoint."""

    print(f"\n{Colors.BOLD}━━━ {endpoint['name']} ━━━{Colors.ENDC}")
    print(f"📍 Path: {endpoint['path']}")

    if endpoint["params"]:
        print(f"🔧 Params: {json.dumps(endpoint['params'], ensure_ascii=False)}")

    url = f"{base_url}{endpoint['path']}"

    try:
        response = await client.get(
            url, params=endpoint["params"], timeout=10.0, follow_redirects=True
        )

        print(f"📡 Status: {response.status_code}")

        if response.status_code == 200:
            print(f"{Colors.OKGREEN}✅ SUCESSO!{Colors.ENDC}")

            try:
                data = response.json()

                if isinstance(data, list):
                    count = len(data)
                    print(f"📊 Registros: {count}")
                    if count > 0:
                        print(f"🔍 Campos: {list(data[0].keys())[:8]}")
                        print(
                            f"\n{Colors.BOLD}Exemplo do primeiro registro:{Colors.ENDC}"
                        )
                        print(json.dumps(data[0], indent=2, ensure_ascii=False)[:500])
                    return {"status": "success", "records": count}

                elif isinstance(data, dict):
                    print(f"📦 Dict com chaves: {list(data.keys())[:10]}")

                    # Procurar array de dados dentro do dict
                    for key in ["items", "data", "contratos", "licitacoes", "results"]:
                        if key in data and isinstance(data[key], list):
                            count = len(data[key])
                            print(f"📊 {key}: {count} itens")
                            if count > 0:
                                print(f"🔍 Campos: {list(data[key][0].keys())[:8]}")
                            return {"status": "success", "records": count}

                    return {"status": "success", "records": 1}

            except Exception as e:
                print(f"{Colors.WARNING}⚠️  Erro ao parsear JSON: {e}{Colors.ENDC}")
                return {"status": "success_no_parse"}

        elif response.status_code == 404:
            print(f"{Colors.FAIL}❌ 404 Not Found{Colors.ENDC}")
            return {"status": "not_found"}

        elif response.status_code == 400:
            print(f"{Colors.WARNING}⚠️  400 Bad Request{Colors.ENDC}")
            try:
                error = response.json()
                print(f"Erro: {json.dumps(error, ensure_ascii=False)[:200]}")
            except:
                print(f"Erro: {response.text[:200]}")
            return {"status": "bad_request"}

        elif response.status_code == 403:
            print(f"{Colors.FAIL}❌ 403 Forbidden{Colors.ENDC}")
            return {"status": "forbidden"}

        else:
            print(f"{Colors.FAIL}❌ Status: {response.status_code}{Colors.ENDC}")
            return {"status": "error", "code": response.status_code}

    except httpx.TimeoutException:
        print(f"{Colors.FAIL}❌ Timeout{Colors.ENDC}")
        return {"status": "timeout"}

    except Exception as e:
        print(f"{Colors.FAIL}❌ Erro: {str(e)}{Colors.ENDC}")
        return {"status": "exception"}


async def main():
    """Test all PNCP endpoint variations."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TESTE: DESCOBRIR ENDPOINTS PNCP CORRETOS{Colors.ENDC}")
    print(
        f"{Colors.BOLD}Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    base_url = "https://pncp.gov.br"
    results = []

    async with httpx.AsyncClient(
        headers={"Accept": "application/json", "User-Agent": "CidadaoAI/1.0"},
        timeout=10.0,
    ) as client:

        for i, endpoint in enumerate(PNCP_ENDPOINTS, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(PNCP_ENDPOINTS)}]{Colors.ENDC}")

            result = await test_endpoint(client, endpoint, base_url)
            result["name"] = endpoint["name"]
            results.append(result)

            await asyncio.sleep(0.5)

    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}RESUMO{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    success = sum(1 for r in results if r["status"] == "success")
    not_found = sum(1 for r in results if r["status"] == "not_found")
    bad_request = sum(1 for r in results if r["status"] == "bad_request")

    print(f"📊 Total testado: {len(results)}")
    print(f"{Colors.OKGREEN}✅ Funcionando: {success}{Colors.ENDC}")
    print(f"{Colors.FAIL}❌ Não encontrado (404): {not_found}{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠️  Bad Request (400): {bad_request}{Colors.ENDC}\n")

    print(f"{Colors.BOLD}━━━ ENDPOINTS FUNCIONANDO ━━━{Colors.ENDC}\n")

    for result in results:
        if result["status"] == "success":
            records = result.get("records", "?")
            print(
                f"{Colors.OKGREEN}✅ {result['name']}: {records} registros{Colors.ENDC}"
            )

    if success > 1:
        print(
            f"\n{Colors.OKGREEN}🎉 Encontramos {success} endpoints funcionando!{Colors.ENDC}"
        )

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    return 0 if success > 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\nInterrompido")
        sys.exit(130)
