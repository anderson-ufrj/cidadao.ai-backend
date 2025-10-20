#!/usr/bin/env python3
"""
Monitorar investigação em tempo real
"""

import httpx
import time
from datetime import datetime

API_URL = "https://cidadao-api-production.up.railway.app"
INVESTIGATION_ID = "c5757228-7b81-4490-bfa7-36faaf659e32"

print("\n" + "="*60)
print(f"🔍 MONITORANDO INVESTIGAÇÃO: {INVESTIGATION_ID}")
print("="*60)

with httpx.Client(timeout=30.0) as client:
    for i in range(20):  # Monitorar por até 100 segundos
        response = client.get(f"{API_URL}/api/v1/investigations/{INVESTIGATION_ID}/status")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            progress = data.get("progress", 0)
            phase = data.get("current_phase", "unknown")
            
            # Barra de progresso
            bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
            print(f"\r[{bar}] {progress*100:.0f}% - {phase} - {status}", end="", flush=True)
            
            if status == "completed":
                print(f"\n\n✅ INVESTIGAÇÃO CONCLUÍDA COM SUCESSO!")
                print(f"Tempo: {i*5} segundos")
                
                # Buscar resultados (usando endpoint de status que funciona)
                result = data
                print(f"\nAnomaliaa detectadas: {result.get('anomalies_detected', 0)}")
                print(f"Registros processados: {result.get('records_processed', 0)}")
                break
                
            elif status == "failed":
                print(f"\n\n❌ INVESTIGAÇÃO FALHOU!")
                print(f"Fase: {phase}")
                break
        else:
            print(f"\n❌ Erro ao verificar status: {response.status_code}")
            break
            
        time.sleep(5)
    else:
        print(f"\n\n⏱️ Timeout - ainda processando após {20*5} segundos")
        print(f"Último status: {status} em {progress*100:.0f}%")
