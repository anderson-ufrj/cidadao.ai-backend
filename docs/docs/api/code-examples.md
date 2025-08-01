---
title: "Exemplos de Código"
sidebar_position: 1
description: "Documentação técnica do Cidadão.AI"
---

## 
💻 Exemplos de Código
Exemplos práticos de implementação e uso da API Cidadão.AI com código funcional e documentado.
### 🚀 Exemplo: Criar Investigação
```python
import requests
import json
# Configuração da API
API_BASE = "https://api.cidadao.ai/v1"
headers = {
"Authorization": "Bearer YOUR_API_TOKEN",
"Content-Type": "application/json"
}
# Criar nova investigação
investigation_data = {
"query": "contratos emergenciais sem licitação",
"filters": {
"valor_minimo": 100000,
"periodo": "2023-2024",
"orgao": "Ministério da Saúde"
},
"algorithms": ["isolation_forest", "lof", "one_class_svm"]
}
response = requests.post(
f"{API_BASE}/investigations",
headers=headers,
json=investigation_data
)
if response.status_code == 201:
investigation = response.json()
print(f"Investigação criada: {investigation['id']}")
else:
print(f"Erro: {response.status_code}")
```
### 🤖 Exemplo: Sistema Multi-Agente
```python
from cidadao_ai import MultiAgentSystem
import asyncio
# Inicializar sistema multi-agente
system = MultiAgentSystem(
agents=['master', 'investigator', 'analyst', 'reporter'],
config='production'
)
async def analyze_document():
# Análise de documento usando múltiplos agentes
document = {
"texto": "Contrato emergencial de R$ 1,000,000...",
"tipo": "contrato",
"metadata": {"orgao": "MS", "ano": 2024}
}
# Análise coordenada entre agentes
result = await system.analyze(document)
return {
"anomaly_score": result.anomaly_score,
"risk_level": result.risk_level,
"explanation": result.explanation,
"agents_consensus": result.consensus
}
# Executar análise
result = asyncio.run(analyze_document())
print(f"Score de anomalia: {result['anomaly_score']}")
```
### 📊 Exemplo: Análise em Lote
```python
# Processamento em lote de múltiplos documentos
documents = [
{"id": "doc1", "content": "Contrato 1..."},
{"id": "doc2", "content": "Contrato 2..."},
{"id": "doc3", "content": "Contrato 3..."}
]
# Análise assíncrona em paralelo
batch_payload = {
"documents": documents,
"config": {
"parallel_processing": True,
"max_workers": 4,
"timeout": 300
}
}
response = requests.post(
f"{API_BASE}/analyze/batch",
headers=headers,
json=batch_payload
)
results = response.json()
for result in results['analyses']:
print(f"Doc {result['document_id']}: {result['anomaly_score']}")
```
#### 📚 SDKs Disponíveis
Python SDK, Node.js SDK, e REST API direta. Documentação completa e exemplos em [docs.cidadao.ai](https://docs.cidadao.ai)
