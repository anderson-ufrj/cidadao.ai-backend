---
title: "Fundamentos Teóricos"
sidebar_position: 5
description: "Base teórica e matemática do sistema"
---

# 🧮 Fundamentos Teóricos

Base matemática e teórica que sustenta o Cidadão.AI.

## 📐 Teoria dos Grafos

### Modelagem de Relacionamentos
Utilizamos grafos direcionados G = (V, E) onde:
- **V**: Conjunto de entidades (contratos, empresas, órgãos)
- **E**: Conjunto de relações (pagamentos, vínculos)

### Detecção de Comunidades
Algoritmo de Louvain para identificar clusters suspeitos:
- Modularidade Q > 0.3 indica estrutura significativa
- Comunidades densas podem indicar cartéis

## 🎲 Teoria da Informação

### Entropia de Shannon
Medimos a incerteza em distribuições de contratos.

Alta entropia indica distribuição equilibrada, baixa entropia sugere concentração suspeita.

### Divergência KL
Comparamos distribuições esperadas vs observadas para detectar anomalias.

## 🤖 Machine Learning

### Isolation Forest
Para detecção de anomalias não supervisionada:
- Isola pontos anômalos com menos partições
- Score de anomalia baseado em profundidade

### LSTM Networks
Para análise temporal de padrões:
- Memória de longo prazo para tendências
- Gates para controle de informação

## 📊 Estatística Aplicada

### Teste de Benford
Verificação de autenticidade em valores financeiros:
- Primeiro dígito deve seguir distribuição logarítmica
- Desvios indicam possível manipulação

### Z-Score Modificado
Para detecção robusta de outliers usando MAD (Median Absolute Deviation).

## 🎯 Aplicação Prática

Todos esses fundamentos convergem para criar um sistema que:
1. **Detecta** anomalias com alta precisão
2. **Explica** suas decisões matematicamente
3. **Aprende** continuamente com novos dados
4. **Adapta** estratégias baseado em resultados
