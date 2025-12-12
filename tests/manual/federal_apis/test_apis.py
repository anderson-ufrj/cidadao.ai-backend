"""
Script para gerar métricas de teste das Federal APIs.
"""

import asyncio


async def test_federal_apis():
    """Testa as Federal APIs para gerar métricas."""
    print("🧪 Iniciando testes das Federal APIs...\n")

    # Import clients
    from src.services.transparency_apis.federal_apis.datasus_client import DataSUSClient
    from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient
    from src.services.transparency_apis.federal_apis.inep_client import INEPClient

    results = []

    # Test IBGE
    print("📊 Testando IBGE API...")
    try:
        async with IBGEClient() as ibge:
            # Get states
            states = await ibge.get_states()
            print(f"  ✅ Estados: {len(states)} encontrados")
            results.append(("IBGE get_states", "success", len(states)))

            # Get municipalities for RJ
            municipalities = await ibge.get_municipalities(state_code="33")
            print(f"  ✅ Municípios RJ: {len(municipalities)} encontrados")
            results.append(("IBGE get_municipalities", "success", len(municipalities)))

            # Get population
            population = await ibge.get_population(state_code="33")
            print(f"  ✅ População RJ: {population.get('total', 'N/A')}")
            results.append(("IBGE get_population", "success", 1))

    except Exception as e:
        print(f"  ❌ Erro IBGE: {e}")
        results.append(("IBGE", "error", str(e)))

    print()

    # Test DataSUS
    print("🏥 Testando DataSUS API...")
    try:
        async with DataSUSClient() as datasus:
            # Search datasets
            datasets = await datasus.search_datasets("saúde", limit=5)
            count = datasets.get("result", {}).get("count", 0)
            print(f"  ✅ Datasets encontrados: {count}")
            results.append(("DataSUS search_datasets", "success", count))

            # Get health indicators
            indicators = await datasus.get_health_indicators(state_code="RJ")
            print("  ✅ Indicadores de saúde obtidos")
            results.append(("DataSUS get_health_indicators", "success", 1))

    except Exception as e:
        print(f"  ❌ Erro DataSUS: {e}")
        results.append(("DataSUS", "error", str(e)))

    print()

    # Test INEP
    print("🎓 Testando INEP API...")
    try:
        async with INEPClient() as inep:
            # Search institutions
            institutions = await inep.search_institutions(state="RJ", limit=5)
            count = institutions.get("total", 0)
            print(f"  ✅ Instituições RJ: {count} encontradas")
            results.append(("INEP search_institutions", "success", count))

            # Get indicators
            indicators = await inep.get_education_indicators(state="RJ")
            print("  ✅ Indicadores educacionais obtidos")
            results.append(("INEP get_education_indicators", "success", 1))

    except Exception as e:
        print(f"  ❌ Erro INEP: {e}")
        results.append(("INEP", "error", str(e)))

    print("\n" + "=" * 60)
    print("📈 RESUMO DOS TESTES:")
    print("=" * 60)

    success_count = sum(1 for r in results if r[1] == "success")
    error_count = sum(1 for r in results if r[1] == "error")

    for operation, status, data in results:
        status_icon = "✅" if status == "success" else "❌"
        print(f"{status_icon} {operation}: {data if status == 'success' else 'erro'}")

    print(f"\n✅ Sucesso: {success_count}")
    print(f"❌ Erros: {error_count}")
    print(f"📊 Total: {len(results)} operações")

    print("\n" + "=" * 60)
    print("🎯 Métricas geradas! Verifique:")
    print("   http://localhost:8000/health/metrics | grep federal_api")
    print("   http://localhost:9090 (Prometheus)")
    print("   http://localhost:3000 (Grafana - admin/cidadao123)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_federal_apis())
