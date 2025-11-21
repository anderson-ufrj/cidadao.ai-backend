#!/usr/bin/env python3
"""
Teste Final: 4 Endpoints Remanescentes com Correções Completas

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta

import httpx

API_KEY = "***REDACTED-TRANSPARENCY-KEY***"
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"


class Colors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


today = datetime.now()
one_month_ago = today - timedelta(days=30)
date_start = one_month_ago.strftime("%d/%m/%Y")
date_end = today.strftime("%d/%m/%Y")

# Final corrections with all discovered parameters
FINAL_TESTS = [
    {
        "name": "1. Servidores - Lista (tentativa 2)",
        "path": "/servidores",
        "params": {
            "codigoOrgao": "36000",  # Try codigoOrgao instead
            "pagina": 1,
            "tamanhoPagina": 5,
        },
    },
    {
        "name": "1b. Servidores - Com CPF específico",
        "path": "/servidores",
        "params": {
            "cpf": "09842860639",  # Try with CPF
            "pagina": 1,
            "tamanhoPagina": 5,
        },
    },
    {
        "name": "2. Despesas - Documentos (com fase)",
        "path": "/despesas/documentos",
        "params": {
            "codigoOrgao": "36000",
            "ano": 2024,
            "dataEmissao": "01/08/2024",
            "fase": "3",  # Added: Fase 3 = Pagamento
            "pagina": 1,
            "tamanhoPagina": 5,
        },
    },
    {
        "name": "3. Despesas - Por Órgão (só ano + órgão)",
        "path": "/despesas/por-orgao",
        "params": {
            "ano": 2024,
            "codigoOrgao": "36000",  # Simplified: only year + organ
            "pagina": 1,
            "tamanhoPagina": 5,
        },
    },
    {
        "name": "4. Viagens (com datas de ida E retorno)",
        "path": "/viagens",
        "params": {
            "dataIdaDe": date_start,
            "dataIdaAte": date_end,
            "dataRetornoDe": date_start,  # Added
            "dataRetornoAte": date_end,  # Added
            "pagina": 1,
            "tamanhoPagina": 5,
        },
    },
]


async def test_endpoint(client, test):
    """Test endpoint."""

    print(f"\n{Colors.BOLD}━━━ {test['name']} ━━━{Colors.ENDC}")
    print(f"📍 Path: {test['path']}")
    print(f"🔧 Params: {json.dumps(test['params'], ensure_ascii=False)}")

    url = f"{BASE_URL}{test['path']}"

    try:
        response = await client.get(url, params=test["params"], timeout=15.0)

        print(f"📡 Status: {response.status_code}")

        if response.status_code == 200:
            print(f"{Colors.OKGREEN}✅ SUCESSO!{Colors.ENDC}")

            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"📊 Registros: {len(data)}")
                    if len(data) > 0:
                        print(f"🔍 Campos: {list(data[0].keys())[:8]}")
                    return {"status": "success", "records": len(data)}
            except:
                pass

            return {"status": "success"}

        elif response.status_code == 400:
            print(f"{Colors.WARNING}⚠️  400 Bad Request{Colors.ENDC}")
            try:
                error = response.json()
                print(f"   Erro: {json.dumps(error, ensure_ascii=False)}")
                return {"status": "bad_request", "error": error}
            except:
                return {"status": "bad_request"}

        elif response.status_code == 403:
            print(f"{Colors.FAIL}❌ 403 Forbidden{Colors.ENDC}")
            return {"status": "forbidden"}

        else:
            print(f"{Colors.FAIL}❌ {response.status_code}{Colors.ENDC}")
            return {"status": "error"}

    except Exception as e:
        print(f"{Colors.FAIL}❌ Exceção: {str(e)}{Colors.ENDC}")
        return {"status": "exception"}


async def main():
    """Test final corrections."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TESTE FINAL: 4 ENDPOINTS REMANESCENTES{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")

    results = []

    async with httpx.AsyncClient(
        headers={
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0",
        },
        timeout=15.0,
    ) as client:

        for test in FINAL_TESTS:
            result = await test_endpoint(client, test)
            result["name"] = test["name"]
            results.append(result)
            await asyncio.sleep(0.7)

    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}RESUMO{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    success = sum(1 for r in results if r["status"] == "success")

    for result in results:
        name = result["name"]
        status = result["status"]

        if status == "success":
            records = result.get("records", "?")
            print(f"{Colors.OKGREEN}✅ {name}: OK ({records} registros){Colors.ENDC}")
        elif status == "forbidden":
            print(f"{Colors.FAIL}❌ {name}: 403 Forbidden{Colors.ENDC}")
        elif status == "bad_request":
            print(f"{Colors.WARNING}⚠️  {name}: 400 Bad Request{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ {name}: Erro{Colors.ENDC}")

    print(
        f"\n{Colors.OKGREEN}✅ Total corrigido: {success}/{len(results)}{Colors.ENDC}\n"
    )

    return 0 if success >= 3 else 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(130)
