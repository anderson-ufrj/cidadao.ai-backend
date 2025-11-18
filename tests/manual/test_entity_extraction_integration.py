#!/usr/bin/env python3
"""
Test Entity Extraction Integration with Zumbi
Validates that entities are correctly passed to InvestigationRequest
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.chat_data_integration import ChatDataIntegration


async def test_entity_extraction():
    """Test entity extraction for problem query."""
    print("\n" + "=" * 80)
    print("TESTE: Entity Extraction para Zumbi")
    print("=" * 80)
    print()

    # Query problema original
    query = "Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
    print(f'Query: "{query}"')
    print()

    # Extract entities
    chat_integration = ChatDataIntegration()
    entities = await chat_integration._extract_entities(query)

    print("🔍 Entidades extraídas:")
    for key, value in entities.items():
        print(f"   {key}: {value}")
    print()

    # Build parameters for InvestigationRequest
    date_range = None
    if entities.get("ano"):
        year = entities["ano"]
        date_range = (f"01/01/{year}", f"31/12/{year}")

    value_threshold = entities.get("valor")

    print("📊 Parâmetros para InvestigationRequest:")
    print(f"   date_range: {date_range}")
    print(f"   value_threshold: {value_threshold}")
    print()

    # Verify
    checks = {
        "Ano extraído": entities.get("ano") == 2024,
        "Date range gerado": date_range == ("01/01/2024", "31/12/2024"),
        "Valor extraído": value_threshold == 1000000.0,
        "Estado extraído": entities.get("estado") == "MG",
        "Código IBGE": entities.get("codigo_uf") == "31",
        "Categoria extraída": entities.get("categoria") == "saúde",
    }

    print("✅ Verificações:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 SUCESSO! Todos os parâmetros extraídos corretamente!")
        print()
        print("   Isso significa que:")
        print("   - Zumbi vai receber date_range = ('01/01/2024', '31/12/2024')")
        print("   - Zumbi vai receber value_threshold = 1000000.0")
        print("   - TransparencyDataCollector vai buscar dados de 2024")
        print("   - Filtro vai aplicar valor mínimo de R$ 1 milhão")
        print()
        return 0
    else:
        print("❌ FALHA! Alguns parâmetros não foram extraídos corretamente.")
        print("   Revisar src/services/chat_data_integration.py")
        print()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_entity_extraction())
    sys.exit(exit_code)
