#!/usr/bin/env python3
"""
Teste: Endpoint Servidores com CPF Específico

Testa o endpoint /servidores com o CPF fornecido pelo usuário.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime

import httpx

API_KEY = "***REDACTED-TRANSPARENCY-KEY***"
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"


class Colors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    OKCYAN = "\033[96m"


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


async def test_servidores_with_cpf():
    """Test /servidores endpoint with specific CPF."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TESTE: ENDPOINT /servidores COM CPF ESPECÍFICO{Colors.ENDC}")
    print(
        f"{Colors.BOLD}Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    # CPF fornecido pelo usuário (sem formatação)
    cpf_formatado = "098.428.606-39"
    cpf = "09842860639"

    print_info(f"CPF (formatado): {cpf_formatado}")
    print_info(f"CPF (limpo): {cpf}\n")

    url = f"{BASE_URL}/servidores"
    params = {
        "cpf": cpf,
        "pagina": 1,
        "tamanhoPagina": 100,  # Aumentado para pegar todos os registros
    }

    print_info(f"URL: {url}")
    print_info(f"Params: {json.dumps(params, ensure_ascii=False)}\n")

    async with httpx.AsyncClient(
        headers={
            "chave-api-dados": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CidadaoAI/1.0",
        },
        timeout=15.0,
    ) as client:

        try:
            start_time = datetime.now()
            response = await client.get(url, params=params)
            duration = (datetime.now() - start_time).total_seconds()

            print(f"⏱️  Tempo de resposta: {duration:.3f}s")
            print(f"📡 Status: {response.status_code} {response.reason_phrase}\n")

            if response.status_code == 200:
                print_success("SUCESSO! Endpoint /servidores funcionou com CPF")

                try:
                    data = response.json()

                    if isinstance(data, list):
                        record_count = len(data)
                        print(f"\n📊 Total de registros: {record_count}\n")

                        if record_count > 0:
                            print(
                                f"{Colors.BOLD}━━━ DADOS DO SERVIDOR ━━━{Colors.ENDC}\n"
                            )

                            for i, servidor in enumerate(data, 1):
                                print(
                                    f"{Colors.BOLD}[Registro {i}/{record_count}]{Colors.ENDC}\n"
                                )

                                # Campos principais
                                nome = servidor.get("nome", "N/A")
                                cpf_retorno = servidor.get("cpf", "N/A")
                                orgao = servidor.get("orgao", {})
                                orgao_nome = (
                                    orgao.get("nome", "N/A")
                                    if isinstance(orgao, dict)
                                    else "N/A"
                                )
                                cargo = servidor.get("cargo", "N/A")
                                situacao = servidor.get("situacao", "N/A")

                                print(f"👤 Nome: {nome}")
                                print(f"📋 CPF: {cpf_retorno}")
                                print(f"🏛️  Órgão: {orgao_nome}")
                                print(f"👔 Cargo: {cargo}")
                                print(f"📍 Situação: {situacao}")

                                # Todos os campos disponíveis
                                print("\n🔍 Todos os campos disponíveis:")
                                for key, value in servidor.items():
                                    if key not in [
                                        "nome",
                                        "cpf",
                                        "orgao",
                                        "cargo",
                                        "situacao",
                                    ]:
                                        print(f"   • {key}: {value}")

                                print()

                            # JSON completo
                            print(
                                f"{Colors.BOLD}━━━ RESPOSTA COMPLETA (JSON) ━━━{Colors.ENDC}\n"
                            )
                            print(json.dumps(data, indent=2, ensure_ascii=False))

                            return {
                                "status": "success",
                                "records": record_count,
                                "data": data,
                            }

                        else:
                            print(f"{Colors.WARNING}⚠️  Lista vazia{Colors.ENDC}")
                            print_info("Possíveis causas:")
                            print_info("  1. CPF não encontrado na base federal")
                            print_info("  2. Servidor é estadual ou municipal")
                            print_info("  3. CPF não está ativo no momento")

                            return {"status": "success_empty", "records": 0}

                except Exception as e:
                    print_error(f"Erro ao parsear resposta: {str(e)}")
                    print("\nRaw response (primeiros 500 chars):")
                    print(response.text[:500])

                    return {"status": "success_parse_error", "error": str(e)}

            elif response.status_code == 400:
                print_error("400 Bad Request - Parâmetros inválidos")

                try:
                    error = response.json()
                    print("\nErro da API:")
                    print(json.dumps(error, indent=2, ensure_ascii=False))
                except:
                    print(f"\nRaw error: {response.text[:300]}")

                return {
                    "status": "bad_request",
                    "error": error if "error" in locals() else response.text[:300],
                }

            elif response.status_code == 403:
                print_error("403 Forbidden - Endpoint bloqueado")
                print_info("Este endpoint requer permissões especiais na API key")

                return {"status": "forbidden"}

            elif response.status_code == 404:
                print_error("404 Not Found")
                print_info("CPF não encontrado na base de dados")

                return {"status": "not_found"}

            else:
                print_error(f"Status inesperado: {response.status_code}")

                return {"status": "error", "code": response.status_code}

        except httpx.TimeoutException:
            print_error("Timeout após 15 segundos")
            return {"status": "timeout"}

        except Exception as e:
            print_error(f"Exceção: {str(e)}")
            import traceback

            traceback.print_exc()

            return {"status": "exception", "error": str(e)}


async def main():
    """Run CPF test."""

    result = await test_servidores_with_cpf()

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}RESULTADO FINAL{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    status = result.get("status")

    if status == "success":
        records = result.get("records", 0)
        print_success("ENDPOINT /servidores FUNCIONA COM CPF!")
        print_success(f"Encontrados {records} registro(s) para este CPF")
        print_info(
            "Este endpoint pode ser usado para buscar servidores federais por CPF"
        )
        return 0

    elif status == "success_empty":
        print_success("ENDPOINT /servidores FUNCIONA!")
        print(
            f"{Colors.WARNING}⚠️  Mas não retornou dados para este CPF específico{Colors.ENDC}"
        )
        print_info("Endpoint está operacional, mas CPF pode não estar na base federal")
        return 0

    elif status == "forbidden":
        print_error("ENDPOINT BLOQUEADO (403)")
        print_info("Requer upgrade de API key")
        return 1

    elif status == "bad_request":
        print_error("ENDPOINT COM ERRO DE PARÂMETROS (400)")
        print_info("Parâmetros precisam de ajuste")
        return 1

    else:
        print_error(f"TESTE FALHOU: {status}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Erro fatal: {str(e)}{Colors.ENDC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
