#!/usr/bin/env python3
"""
Test Salary Query End-to-End

Tests the complete flow for salary queries:
1. Intent classification
2. Entity extraction
3. Investigation orchestration
4. Traceability output

Author: Anderson Henrique da Silva
Date: 2025-11-21
"""

import asyncio
import json
from datetime import datetime


# Colors for console output
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


async def test_salary_query_complete():
    """Test complete salary query flow with traceability."""

    print_header("TESTE COMPLETO: CONSULTA DE SALÁRIO")

    query = "Quanto ganha a professora Aracele Garcia de Oliveira Fassbinder?"

    print_info(f"Query: {query}")
    print_info(
        "Testando fluxo completo: Intent → Entities → Investigation → Traceability\n"
    )

    # Step 1: Intent Classification
    print(f"{Colors.BOLD}PASSO 1: CLASSIFICAÇÃO DE INTENT{Colors.ENDC}")
    print("-" * 80)

    from src.services.orchestration.query_planner.intent_classifier import (
        IntentClassifier,
    )

    classifier = IntentClassifier(keyword_only=True)
    intent_result = await classifier.classify(query)

    print(f"Intent: {intent_result['intent'].value}")
    print(f"Confidence: {intent_result['confidence']:.0%}")
    print(f"Reasoning: {intent_result['reasoning']}")
    print(f"Method: {intent_result['method']}")

    if (
        intent_result["intent"].value == "supplier_investigation"
        and intent_result["confidence"] >= 0.85
    ):
        print_success("Intent corretamente classificado!")
    else:
        print_error(f"Intent incorreto: {intent_result['intent'].value}")
        return False

    # Step 2: Entity Extraction
    print(f"\n{Colors.BOLD}PASSO 2: EXTRAÇÃO DE ENTIDADES{Colors.ENDC}")
    print("-" * 80)

    from src.services.orchestration.query_planner.entity_extractor import (
        EntityExtractor,
    )

    extractor = EntityExtractor()
    entities = extractor.extract(query)

    print(f"Entidades extraídas: {json.dumps(entities, indent=2, ensure_ascii=False)}")

    if entities:
        print_success(f"Extraídas {len(entities)} entidades")
    else:
        print_warning("Nenhuma entidade extraída (pode ser normal)")

    # Step 3: Investigation Orchestration
    print(f"\n{Colors.BOLD}PASSO 3: ORQUESTRAÇÃO DE INVESTIGAÇÃO{Colors.ENDC}")
    print("-" * 80)

    from src.services.orchestration.orchestrator import InvestigationOrchestrator

    orchestrator = InvestigationOrchestrator()

    print_info("Iniciando investigação...")
    start_time = datetime.now()

    try:
        result = await orchestrator.investigate(
            query=query, user_id="test_user", session_id="test_session"
        )

        duration = (datetime.now() - start_time).total_seconds()

        print_success(f"Investigação completada em {duration:.2f}s")

        # Step 4: Traceability Analysis
        print(f"\n{Colors.BOLD}PASSO 4: ANÁLISE DE RASTREABILIDADE{Colors.ENDC}")
        print("-" * 80)

        print(
            f"\n📊 {Colors.BOLD}Investigation ID:{Colors.ENDC} {result.investigation_id}"
        )
        print(f"📋 {Colors.BOLD}Status:{Colors.ENDC} {result.status}")
        print(
            f"⏱️  {Colors.BOLD}Duration:{Colors.ENDC} {result.total_duration_seconds:.2f}s"
        )
        print(f"🎯 {Colors.BOLD}Intent:{Colors.ENDC} {result.intent.value}")
        print(f"💯 {Colors.BOLD}Confidence:{Colors.ENDC} {result.confidence_score:.0%}")

        print(f"\n{Colors.OKBLUE}📊 FONTES DE DADOS CONSULTADAS:{Colors.ENDC}")
        if result.data_sources_used:
            for i, source in enumerate(result.data_sources_used, 1):
                print(f"  {i}. {source}")
        else:
            print_warning("  Nenhuma API foi consultada")

        print(f"\n{Colors.OKBLUE}🎯 ESTÁGIOS DE EXECUÇÃO:{Colors.ENDC}")
        if result.stage_results:
            for stage in result.stage_results:
                status_icon = (
                    "✅"
                    if stage.status == "success"
                    else "⚠️" if stage.status == "partial_success" else "❌"
                )
                print(
                    f"\n  {status_icon} {Colors.BOLD}{stage.stage_name.upper()}{Colors.ENDC}"
                )
                print(f"     Status: {stage.status}")
                print(f"     Duration: {stage.duration_seconds:.2f}s")
                print(
                    f"     APIs: {', '.join(stage.api_calls) if stage.api_calls else 'None'}"
                )
                if stage.errors:
                    print(f"     Errors: {', '.join(stage.errors)}")
        else:
            print_warning("  Nenhum estágio executado")

        print(f"\n{Colors.OKBLUE}🔍 ENTIDADES ENCONTRADAS:{Colors.ENDC}")
        if result.entities_found:
            for key, value in result.entities_found.items():
                print(f"  • {key}: {value}")
        else:
            print_warning("  Nenhuma entidade identificada")

        # Verification
        print(f"\n{Colors.BOLD}VERIFICAÇÃO DE REQUISITOS:{Colors.ENDC}")
        print("-" * 80)

        checks = []

        # Check 1: Intent correct
        if result.intent.value == "supplier_investigation":
            print_success("Intent correto: supplier_investigation")
            checks.append(True)
        else:
            print_error(f"Intent incorreto: {result.intent.value}")
            checks.append(False)

        # Check 2: High confidence
        if result.confidence_score >= 0.85:
            print_success(f"Confiança alta: {result.confidence_score:.0%}")
            checks.append(True)
        else:
            print_warning(f"Confiança baixa: {result.confidence_score:.0%}")
            checks.append(False)

        # Check 3: Traceability present
        if result.stage_results:
            print_success(
                f"Rastreabilidade presente: {len(result.stage_results)} estágios"
            )
            checks.append(True)
        else:
            print_error("Rastreabilidade ausente")
            checks.append(False)

        # Check 4: Duration acceptable
        if result.total_duration_seconds < 10:
            print_success(f"Duração aceitável: {result.total_duration_seconds:.2f}s")
            checks.append(True)
        else:
            print_warning(f"Duração longa: {result.total_duration_seconds:.2f}s")
            checks.append(False)

        # Final result
        print(f"\n{Colors.BOLD}RESULTADO FINAL:{Colors.ENDC}")
        print("-" * 80)

        passed = sum(checks)
        total = len(checks)
        percentage = (passed / total) * 100

        if percentage == 100:
            print_success(f"TODOS OS TESTES PASSARAM ({passed}/{total}) 🎉")
            return True
        elif percentage >= 75:
            print_warning(f"MAIORIA DOS TESTES PASSOU ({passed}/{total})")
            return True
        else:
            print_error(f"MUITOS TESTES FALHARAM ({passed}/{total})")
            return False

    except Exception as e:
        print_error(f"Erro durante investigação: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run salary query test."""

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(
        f"{Colors.BOLD}TESTE END-TO-END: CONSULTA DE SALÁRIO DE SERVIDOR PÚBLICO{Colors.ENDC}"
    )
    print(
        f"{Colors.BOLD}Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")

    success = await test_salary_query_complete()

    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    if success:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ TESTE COMPLETO: SUCESSO{Colors.ENDC}")
        print(
            f"{Colors.OKGREEN}Sistema está funcionando corretamente para queries de salário{Colors.ENDC}"
        )
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ TESTE COMPLETO: FALHOU{Colors.ENDC}")
        print(f"{Colors.FAIL}Sistema precisa de ajustes{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

    return 0 if success else 1


if __name__ == "__main__":
    import sys

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
