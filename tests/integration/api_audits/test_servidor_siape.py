#!/usr/bin/env python3
"""
Teste: Buscar Servidor por SIAPE

Testa o endpoint /servidores com código SIAPE de servidor federal confirmado.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys

import httpx

API_KEY = "e24f842355f7211a2f4895e301aa5bca"
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"


class Colors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    OKCYAN = "\033[96m"


async def test_servidor_by_siape():
    """Test /servidores with SIAPE code."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TESTE: BUSCAR SERVIDOR POR CÓDIGO SIAPE{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    # SIAPE da Aracele Garcia de Oliveira Fassbinder
    # Fonte: Portaria nº214/2024/GAB-MUZ/MUZ/IFSULDEMINAS
    siape = "1566251"
    nome_esperado = "Aracele Garcia de Oliveira Fassbinder"

    print(f"{Colors.OKCYAN}ℹ️  SIAPE: {siape}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}ℹ️  Nome esperado: {nome_esperado}{Colors.ENDC}")
    print(
        f"{Colors.OKCYAN}ℹ️  Instituição: IFSULDEMINAS - Campus Muzambinho{Colors.ENDC}\n"
    )

    # Tentar diferentes formas de busca
    tests = [
        {
            "name": "1. Busca por codigoOrgaoLotacao (MEC - 26000)",
            "params": {
                "codigoOrgaoLotacao": "26000",
                "pagina": 1,
                "tamanhoPagina": 100,
            },
        },
        {
            "name": "2. Busca por codigoOrgaoExercicio (MEC - 26000)",
            "params": {
                "codigoOrgaoExercicio": "26000",
                "pagina": 1,
                "tamanhoPagina": 100,
            },
        },
    ]

    url = f"{BASE_URL}/servidores"

    async with httpx.AsyncClient(
        headers={
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0",
        },
        timeout=30.0,
    ) as client:

        for test in tests:
            print(f"\n{Colors.BOLD}━━━ {test['name']} ━━━{Colors.ENDC}")
            print(f"Params: {json.dumps(test['params'], ensure_ascii=False)}")

            try:
                response = await client.get(url, params=test["params"])
                print(f"Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()

                    if isinstance(data, list):
                        print(f"📊 Total de servidores: {len(data)}")

                        # Procurar Aracele nos resultados
                        aracele_found = None
                        for servidor in data:
                            nome = servidor.get("nome", "")
                            if (
                                "ARACELE" in nome.upper()
                                or "FASSBINDER" in nome.upper()
                            ):
                                aracele_found = servidor
                                break

                        if aracele_found:
                            print(
                                f"\n{Colors.OKGREEN}✅ SERVIDOR ENCONTRADO!{Colors.ENDC}\n"
                            )
                            print(f"👤 Nome: {aracele_found.get('nome')}")
                            print(f"📋 CPF: {aracele_found.get('cpf')}")
                            print(f"📍 SIAPE: {aracele_found.get('codigoOrgao')}")

                            # Mostrar todos os campos
                            print(f"\n{Colors.BOLD}Todos os campos:{Colors.ENDC}")
                            for key, value in aracele_found.items():
                                print(f"  • {key}: {value}")

                            # JSON completo
                            print(f"\n{Colors.BOLD}JSON completo:{Colors.ENDC}")
                            print(
                                json.dumps(aracele_found, indent=2, ensure_ascii=False)
                            )

                            return {"status": "success", "data": aracele_found}
                        else:
                            print(
                                f"{Colors.WARNING}⚠️  Aracele não encontrada nesta página{Colors.ENDC}"
                            )
                            if len(data) > 0:
                                print("\nPrimeiro servidor da lista:")
                                print(f"  Nome: {data[0].get('nome')}")
                                print(f"  Campos: {list(data[0].keys())}")

                elif response.status_code == 400:
                    error = response.json()
                    print(f"{Colors.WARNING}400 Bad Request:{Colors.ENDC}")
                    print(json.dumps(error, indent=2, ensure_ascii=False))

                elif response.status_code == 403:
                    print(f"{Colors.FAIL}403 Forbidden{Colors.ENDC}")

            except Exception as e:
                print(f"{Colors.FAIL}Erro: {str(e)}{Colors.ENDC}")

            await asyncio.sleep(1)

    # Se não encontrou, vamos tentar buscar remuneração diretamente
    print(
        f"\n{Colors.BOLD}━━━ 3. Tentando buscar remuneração diretamente ━━━{Colors.ENDC}"
    )
    print(
        f"{Colors.OKCYAN}Nota: CPF não temos, mas vamos documentar que existe SIAPE{Colors.ENDC}\n"
    )

    return {"status": "not_found_in_listing"}


async def main():
    """Run test."""

    result = await test_servidor_by_siape()

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}CONCLUSÃO{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    if result.get("status") == "success":
        print(f"{Colors.OKGREEN}✅ SUCESSO! Servidor federal encontrado{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Endpoint /servidores retorna dados REAIS{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.WARNING}⚠️  Servidor não encontrado na listagem{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Possíveis causas:{Colors.ENDC}")
        print("  1. Servidor do IF (federal) mas não aparece na base do Portal")
        print("  2. Paginação - pode estar em outra página")
        print("  3. Endpoint lista apenas servidores de órgãos específicos")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\nInterrompido")
        sys.exit(130)
