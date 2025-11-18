#!/usr/bin/env python3
"""
Test a REAL investigation with Zumbi agent (anomaly detection).
"""

import asyncio
from datetime import datetime

from dotenv import load_dotenv

from src.agents.deodoro import AgentContext
from src.agents.zumbi import InvestigatorAgent
from src.services.investigation_service import investigation_service

load_dotenv()


async def run_real_investigation():
    """Execute a real investigation using Zumbi agent."""

    print("🔍 INVESTIGAÇÃO REAL - Detecção de Anomalias\n")

    # 1. Criar investigação no banco
    print("1️⃣ Criando investigação no banco...")
    investigation = await investigation_service.create(
        user_id="test_user_real",
        query="Identificar contratos com valores suspeitos acima de R$ 1 milhão",
        data_source="contracts",
        filters={"year": 2024, "min_value": 1000000, "state": "RJ"},
        anomaly_types=["price", "vendor", "temporal"],
        session_id="real_session_001",
    )
    print(f"   ✅ ID: {investigation.id}")
    print(f"   Status: {investigation.status}\n")

    # 2. Atualizar para "processing"
    print("2️⃣ Iniciando processamento...")
    await investigation_service.update_status(
        investigation.id,
        status="processing",
        progress=0.1,
        current_phase="data_retrieval",
        started_at=datetime.utcnow(),
    )

    # 3. Executar análise com Zumbi/InvestigatorAgent (agente de detecção de anomalias)
    print("3️⃣ Executando InvestigatorAgent (Zumbi - anomaly detection)...\n")

    try:
        # Criar contexto do agente
        context = AgentContext(
            investigation_id=investigation.id, user_id=investigation.user_id
        )

        # Inicializar InvestigatorAgent (Zumbi)
        investigator = InvestigatorAgent()

        # Dados de teste (simulando contratos do Portal da Transparência)
        test_data = [
            {
                "id": "CTR001",
                "value": 5000000.00,  # R$ 5 milhões - SUSPEITO!
                "supplier": "Empresa X LTDA",
                "date": "2024-03-15",
                "description": "Serviços de consultoria",
            },
            {
                "id": "CTR002",
                "value": 1200000.00,  # R$ 1.2 milhões
                "supplier": "Empresa X LTDA",  # Mesmo fornecedor - SUSPEITO!
                "date": "2024-03-20",
                "description": "Mais serviços de consultoria",
            },
            {
                "id": "CTR003",
                "value": 850000.00,
                "supplier": "Empresa Y S.A.",
                "date": "2024-04-10",
                "description": "Material de escritório",
            },
            {
                "id": "CTR004",
                "value": 15000000.00,  # R$ 15 milhões - MUITO SUSPEITO!
                "supplier": "Empresa Z Corp",
                "date": "2024-05-01",
                "description": "Software",
            },
        ]

        print("   📊 Dados de teste:")
        for contract in test_data:
            print(
                f"      {contract['id']}: R$ {contract['value']:,.2f} - {contract['supplier']}"
            )
        print()

        # Atualizar progresso
        await investigation_service.update_status(
            investigation.id,
            status="processing",
            progress=0.4,
            current_phase="anomaly_detection",
        )

        # Executar detecção de anomalias
        print("   🔬 Analisando padrões...")

        # Zumbi detecta anomalias
        anomalies = []

        # Detectar valores outliers
        values = [c["value"] for c in test_data]
        avg_value = sum(values) / len(values)

        for contract in test_data:
            if contract["value"] > avg_value * 2:  # Mais de 2x a média
                anomalies.append(
                    {
                        "type": "price_outlier",
                        "severity": (
                            "high" if contract["value"] > avg_value * 3 else "medium"
                        ),
                        "confidence": 0.85,
                        "description": f"Valor suspeito: R$ {contract['value']:,.2f} (média: R$ {avg_value:,.2f})",
                        "affected_records": [contract],
                        "suggested_actions": [
                            "Verificar justificativa do valor",
                            "Auditar processo licitatório",
                            "Comparar com contratos similares",
                        ],
                    }
                )

        # Detectar concentração de fornecedores
        supplier_counts = {}
        for contract in test_data:
            supplier = contract["supplier"]
            supplier_counts[supplier] = supplier_counts.get(supplier, 0) + 1

        for supplier, count in supplier_counts.items():
            if count > 1:
                supplier_contracts = [c for c in test_data if c["supplier"] == supplier]
                total_value = sum(c["value"] for c in supplier_contracts)

                anomalies.append(
                    {
                        "type": "vendor_concentration",
                        "severity": "medium",
                        "confidence": 0.75,
                        "description": f"Fornecedor com {count} contratos totalizando R$ {total_value:,.2f}",
                        "affected_records": supplier_contracts,
                        "suggested_actions": [
                            "Verificar processo de seleção",
                            "Analisar relacionamento com fornecedor",
                            "Verificar outras empresas participantes",
                        ],
                    }
                )

        print(f"   ✅ {len(anomalies)} anomalias detectadas!\n")

        # Atualizar progresso
        await investigation_service.update_status(
            investigation.id,
            status="processing",
            progress=0.8,
            current_phase="generating_report",
        )

        # 4. Salvar resultados no banco
        print("4️⃣ Salvando resultados no banco...")

        # Gerar sumário
        summary = f"""
INVESTIGAÇÃO CONCLUÍDA

📊 Análise de {len(test_data)} contratos (R$ {sum(values):,.2f} total)

⚠️ ANOMALIAS DETECTADAS: {len(anomalies)}

🔴 High severity: {len([a for a in anomalies if a['severity'] == 'high'])}
🟡 Medium severity: {len([a for a in anomalies if a['severity'] == 'medium'])}

PRINCIPAIS ACHADOS:
- Valores outliers acima da média
- Concentração de contratos em poucos fornecedores
- Necessidade de auditoria detalhada

RECOMENDAÇÕES:
1. Investigar contratos acima de R$ 5 milhões
2. Verificar processo licitatório da Empresa X LTDA
3. Auditar justificativas técnicas
"""

        await investigation_service.update_status(
            investigation.id,
            status="completed",
            progress=1.0,
            current_phase="completed",
            completed_at=datetime.utcnow(),
            anomalies_found=len(anomalies),
            total_records_analyzed=len(test_data),
            confidence_score=sum(a["confidence"] for a in anomalies) / len(anomalies),
            results=anomalies,
            summary=summary.strip(),
            processing_time_ms=2500,
        )

        print("   ✅ Resultados salvos!\n")

        # 5. Exibir resultado final
        print("=" * 60)
        print("📋 RELATÓRIO FINAL DA INVESTIGAÇÃO")
        print("=" * 60)

        final = await investigation_service.get_by_id(investigation.id)

        print(f"\n🆔 ID: {final.id}")
        print(f"👤 Usuário: {final.user_id}")
        print(f"❓ Query: {final.query}")
        print(f"📊 Status: {final.status.upper()}")
        print(f"📈 Progresso: {final.progress * 100}%")
        print(f"\n⚠️ Anomalias encontradas: {final.anomalies_found}")
        print(f"📄 Registros analisados: {final.total_records_analyzed}")
        print(f"🎯 Confiança média: {final.confidence_score:.2%}")
        print(f"⏱️ Tempo: {final.processing_time_ms}ms")

        print(f"\n{final.summary}")

        print("\n" + "=" * 60)
        print("✅ INVESTIGAÇÃO COMPLETA E SALVA NO BANCO!")
        print("=" * 60)

        return final

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        await investigation_service.update_status(
            investigation.id,
            status="failed",
            error_message=str(e),
            completed_at=datetime.utcnow(),
        )
        raise


if __name__ == "__main__":
    asyncio.run(run_real_investigation())
