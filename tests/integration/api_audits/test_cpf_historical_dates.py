#!/usr/bin/env python3
"""
Test CPF with Historical Dates

Tests salary query with different historical dates to find available data.

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend")

from src.services.portal_transparencia_service_improved import (
    ImprovedPortalTransparenciaService,
)


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


async def test_cpf_with_date(service, cpf, mes_ano):
    """Test salary query with specific date."""

    print(f"\n{Colors.BOLD}━━━ Testando: {mes_ano} ━━━{Colors.ENDC}\n")

    try:
        result = await service.search_servidor_remuneracao(cpf=cpf, mes_ano=mes_ano)

        print(f"📅 Período: {mes_ano}")
        print(f"🔌 API Status: {result.get('api_status')}")

        if result.get("error"):
            api_status = result.get("api_status", "")

            if "forbidden" in api_status or "403" in str(result.get("error")):
                print_error("403 Forbidden")
                return {"status": "forbidden", "mes_ano": mes_ano}

            elif "not_found" in api_status or "404" in str(result.get("error")):
                print_warning("404 Not Found - Sem dados para este período")
                return {"status": "not_found", "mes_ano": mes_ano}

            else:
                print_error(f"Erro: {result['error']}")
                return {"status": "error", "mes_ano": mes_ano, "error": result["error"]}

        # Success!
        remuneracao = result.get("remuneracao")
        if remuneracao and len(remuneracao) > 0:
            print(f"\n{Colors.OKGREEN}{'━'*80}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{Colors.BOLD}💰 DADOS ENCONTRADOS!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'━'*80}{Colors.ENDC}\n")

            rem = remuneracao[0]
            print(f"💵 Remuneração Básica: R$ {rem.get('remuneracaoBasica', 0):,.2f}")
            print(f"🎁 Gratificações: R$ {rem.get('gratificacoes', 0):,.2f}")
            print(f"📊 Total Bruto: R$ {rem.get('remuneracaoBruta', 0):,.2f}")
            print(f"➖ Descontos: R$ {rem.get('descontos', 0):,.2f}")
            print(
                f"\n{Colors.OKGREEN}{Colors.BOLD}💰 TOTAL LÍQUIDO: R$ {rem.get('remuneracaoLiquida', 0):,.2f}{Colors.ENDC}"
            )

            if rem.get("cargo"):
                print(f"\n👔 Cargo: {rem.get('cargo')}")
            if rem.get("orgao"):
                print(f"🏛️  Órgão: {rem.get('orgao')}")

            return {
                "status": "success",
                "mes_ano": mes_ano,
                "data": rem,
                "full_result": result,
            }

        else:
            print_warning("Resposta vazia")
            return {"status": "empty", "mes_ano": mes_ano}

    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return {"status": "exception", "mes_ano": mes_ano, "error": str(e)}


async def test_multiple_dates():
    """Test CPF with multiple historical dates."""

    print_header("TESTE: CPF COM DIFERENTES DATAS HISTÓRICAS")

    cpf = "09842860639"
    print_info("CPF: 098.428.606-39\n")

    # Dates to test (from newest to oldest)
    dates_to_test = [
        "08/2024",  # Agosto 2024 (3 meses atrás)
        "06/2024",  # Junho 2024 (5 meses atrás)
        "03/2024",  # Março 2024 (8 meses atrás)
        "12/2023",  # Dezembro 2023
        "09/2023",  # Setembro 2023
        "06/2023",  # Junho 2023
    ]

    service = ImprovedPortalTransparenciaService()

    # Check API key
    if not service.api_key:
        print_error("TRANSPARENCY_API_KEY não configurada!")
        return False

    print_success(f"API Key configurada: {'*' * 20}{str(service.api_key)[-4:]}\n")

    results = []

    try:
        for mes_ano in dates_to_test:
            result = await test_cpf_with_date(service, cpf, mes_ano)
            results.append(result)

            # If we found data, show full details and stop
            if result.get("status") == "success":
                print(f"\n{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
                print(
                    f"{Colors.OKGREEN}{Colors.BOLD}🎉 SUCESSO! Dados encontrados em {mes_ano}!{Colors.ENDC}"
                )
                print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}\n")

                # Show full JSON
                print(f"{Colors.BOLD}━━━ RESPOSTA COMPLETA (JSON) ━━━{Colors.ENDC}\n")
                print(json.dumps(result["full_result"], indent=2, ensure_ascii=False))

                break

            # Small delay between requests
            await asyncio.sleep(0.5)

    finally:
        await service.close()

    # Summary
    print(f"\n{Colors.BOLD}━━━ RESUMO DOS TESTES ━━━{Colors.ENDC}\n")

    for result in results:
        mes_ano = result.get("mes_ano")
        status = result.get("status")

        if status == "success":
            print(f"{Colors.OKGREEN}✅ {mes_ano}: DADOS ENCONTRADOS!{Colors.ENDC}")
        elif status == "forbidden":
            print(f"{Colors.FAIL}❌ {mes_ano}: 403 Forbidden{Colors.ENDC}")
        elif status == "not_found":
            print(
                f"{Colors.WARNING}⚠️  {mes_ano}: 404 Not Found (sem dados){Colors.ENDC}"
            )
        elif status == "empty":
            print(f"{Colors.WARNING}⚠️  {mes_ano}: Resposta vazia{Colors.ENDC}")
        else:
            print(
                f"{Colors.FAIL}❌ {mes_ano}: Erro - {result.get('error', 'unknown')}{Colors.ENDC}"
            )

    # Check if we found any data
    success_count = sum(1 for r in results if r.get("status") == "success")

    return success_count > 0


async def main():
    """Run historical dates test."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TESTE: CONSULTA DE SALÁRIO COM DATAS HISTÓRICAS{Colors.ENDC}")
    print(
        f"{Colors.BOLD}Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")

    print_info("💡 Insight: Portal da Transparência tem atraso de 2-3 meses nos dados")
    print_info("💡 Vamos testar com datas de 2024 e 2023\n")

    success = await test_multiple_dates()

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")

    if success:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ TESTE COMPLETO: SUCESSO{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Conseguimos encontrar dados de salário!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Sistema está funcionando perfeitamente!{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  TESTE COMPLETO: SEM DADOS{Colors.ENDC}")
        print(f"{Colors.WARNING}Nenhuma data testada retornou dados{Colors.ENDC}")
        print_info("Possíveis causas:")
        print_info("  1. CPF não está na base federal (pode ser estadual/municipal)")
        print_info("  2. API key sem permissão para este endpoint")
        print_info("  3. Endpoint está bloqueado (403 Forbidden)")

    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print_error(f"Teste falhou: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
