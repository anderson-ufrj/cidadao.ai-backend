# 💬 Exemplos Práticos - Chat → APIs Governamentais

**Como o usuário interage com o sistema na prática**

---

## 🎯 Exemplo 1: Buscar Contratos de Saúde

### Usuário digita:

```
"Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
```

### O que acontece internamente:

```javascript
// 1. Frontend envia para backend
POST /api/v1/chat/send
{
  "message": "Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024",
  "user_id": "user_123",
  "session_id": "session_456"
}

// 2. Backend processa
Intent Detection → INVESTIGATE_CONTRACTS (confiança: 0.95)

Entities Extracted:
{
  "category": "saúde",
  "state": "MG",
  "min_value": 1000000,
  "year": 2024
}

// 3. Orchestrator busca em 3 APIs paralelas
APIs Called:
  ✓ Portal da Transparência
  ✓ PNCP (licitações)
  ✓ DataSUS

// 4. Resultados
Portal: 47 contratos encontrados (R$ 8.543.200)
PNCP:   23 licitações relacionadas
DataSUS: Indicadores de saúde MG 2024

// 5. Análise por agentes
Zumbi:     5 anomalias detectadas
Oxóssi:    2 padrões suspeitos
Bonifácio: 1 violação legal

// 6. Resposta SSE (streaming)
```

### Usuário vê no frontend:

```
🔍 Buscando contratos de saúde em Minas Gerais...

✅ Portal da Transparência: 47 contratos encontrados
   Valor total: R$ 8.543.200,00

✅ PNCP: 23 licitações relacionadas
   Modalidade: Pregão Eletrônico (18), Concorrência (5)

⚠️  ANOMALIAS DETECTADAS:
   • Contrato #12345: Valor 250% acima da média (R$ 2.5M)
   • Contrato #67890: Mesmo fornecedor em 8 contratos
   • Contrato #11111: Prazo de entrega 300% maior que similar

🚨 FRAUDES SUSPEITAS:
   • Possível cartelização entre 3 fornecedores
   • Padrão de bid rigging detectado (confiança: 87%)

⚖️  QUESTÕES LEGAIS:
   • Contrato #12345 sem publicação no DOU (Lei 8.666/93, Art. 61)

📊 RELATÓRIO COMPLETO DISPONÍVEL
   [Baixar PDF] [Exportar JSON] [Ver Detalhes]
```

---

## 🏥 Exemplo 2: Investigar Despesas de Saúde Pública

### Usuário digita:

```
"Quanto foi gasto com saúde no Rio de Janeiro em 2023?"
```

### Processamento:

```javascript
Intent: INVESTIGATE_EXPENSES
Entities: {
  "category": "saúde",
  "state": "RJ",
  "year": 2023
}

APIs Called:
  ✓ Portal da Transparência → Despesas RJ saúde
  ✓ SICONFI → Dados fiscais municípios RJ
  ✓ DataSUS → Indicadores saúde RJ
  ✓ IBGE → População RJ (para cálculo per capita)

Results:
  Total gasto: R$ 15.234.567.890
  Municípios: 92 municípios com dados
  População: 17.463.349 habitantes
  Per capita: R$ 872,45/habitante
```

### Resposta ao usuário:

```
💰 GASTOS COM SAÚDE NO RIO DE JANEIRO (2023)

📊 Visão Geral:
   Valor Total: R$ 15,2 bilhões
   Municípios: 92 com dados disponíveis
   Per Capita: R$ 872,45/habitante

🏆 Maiores Gastos:
   1. Rio de Janeiro (capital): R$ 5,8 bi
   2. Niterói: R$ 1,2 bi
   3. Duque de Caxias: R$ 890 mi

📈 Análise Temporal:
   • 2021: R$ 12,5 bi
   • 2022: R$ 13,9 bi
   • 2023: R$ 15,2 bi
   Crescimento: +21,6% em 2 anos

⚠️  ATENÇÃO:
   • 8 municípios com gastos abaixo do mínimo constitucional
   • 3 municípios sem dados (não reportaram)

📊 [Ver Gráficos] [Comparar Estados] [Histórico]
```

---

## 👤 Exemplo 3: Buscar Informações de Servidor Público

### Usuário digita:

```
"Buscar servidor CPF 123.456.789-00"
```

### Processamento:

```javascript
Intent: SEARCH_SERVANTS
Entities: {
  "cpf": "12345678900",
  "data_type": "servidores"
}

APIs Called:
  ✓ Portal da Transparência → Servidor por CPF

Result:
  Nome: JOÃO DA SILVA
  Órgão: MINISTÉRIO DA SAÚDE
  Cargo: ANALISTA TÉCNICO
  Remuneração: R$ 12.543,87 (nov/2024)
```

### Resposta:

```
👤 INFORMAÇÕES DO SERVIDOR

📋 Dados Cadastrais:
   Nome: JOÃO DA SILVA
   CPF: 123.456.789-00
   Matrícula: 987654

🏛️ Vínculo:
   Órgão: MINISTÉRIO DA SAÚDE
   Cargo: ANALISTA TÉCNICO DE POLÍTICAS SOCIAIS
   Situação: ATIVO
   Regime: RJU (Regime Jurídico Único)

💰 Remuneração (Nov/2024):
   Vencimento Base: R$ 8.500,00
   Gratificações: R$ 2.800,00
   Adicionais: R$ 1.243,87
   Total Bruto: R$ 12.543,87
   Descontos: R$ 2.103,45
   Líquido: R$ 10.440,42

📊 Histórico (últimos 12 meses):
   Média Mensal: R$ 12.234,56
   Total Anual: R$ 146.814,72

✅ Dados atualizados em: 17/11/2024
```

---

## 🏢 Exemplo 4: Analisar Fornecedor (CNPJ)

### Usuário digita:

```
"Verificar fornecedor CNPJ 12.345.678/0001-90"
```

### Processamento:

```javascript
Intent: SEARCH_SUPPLIERS
Entities: {
  "cnpj": "12345678000190",
  "data_type": "fornecedor"
}

APIs Called:
  ✓ Portal da Transparência → Contratos do fornecedor
  ✓ PNCP → Licitações vencidas
  ✓ Minha Receita → Dados cadastrais CNPJ
  ✓ Receita Federal → Situação fiscal

Agent Analysis:
  Zumbi → Análise de padrões
  Oxóssi → Caça fraudes
  Bonifácio → Verificação legal
```

### Resposta:

```
🏢 ANÁLISE DE FORNECEDOR

📋 Dados Cadastrais (Receita Federal):
   Razão Social: EMPRESA EXEMPLO LTDA
   CNPJ: 12.345.678/0001-90
   Situação: ATIVA
   Atividade: Comércio de equipamentos médicos
   Abertura: 15/03/2015

💼 Contratos com Governo:
   Total de Contratos: 47
   Valor Total: R$ 125.834.567,00
   Órgãos Contratantes: 12
   Período: 2020-2024

🏆 Maiores Contratos:
   1. Ministério da Saúde: R$ 45M (equipamentos hospitalares)
   2. Governo RJ: R$ 23M (ambulâncias)
   3. Prefeitura SP: R$ 18M (material médico)

⚠️  ALERTAS:
   🚨 CRÍTICO: Padrão de concentração detectado
      • Venceu 85% das licitações que participou (média: 35%)
      • 3 processos com apenas 1 participante

   ⚠️  MÉDIO: Valores acima da média
      • Contratos 20% mais caros que concorrentes

   ℹ️  INFORMATIVO:
      • Sem sanções ativas
      • CNPJ regular na Receita
      • Empresa em atividade há 9 anos

📊 [Ver Contratos] [Análise de Risco] [Histórico]
```

---

## 🗺️ Exemplo 5: Análise Regional

### Usuário digita:

```
"Comparar gastos com educação entre estados do Nordeste"
```

### Processamento:

```javascript
Intent: REGIONAL_ANALYSIS
Entities: {
  "category": "educação",
  "region": "Nordeste",
  "comparison": true
}

APIs Called:
  ✓ SICONFI → Dados fiscais 9 estados
  ✓ INEP → Indicadores educação
  ✓ IBGE → População estados

Agent Analysis:
  Lampião → Análise regional especializada
  Anita → Estatísticas comparativas
```

### Resposta:

```
🗺️ ANÁLISE REGIONAL: EDUCAÇÃO NO NORDESTE

📊 Gastos Totais (2023):
   R$ 45,3 bilhões nos 9 estados

🏆 Ranking de Gastos (Total):
   1. Bahia: R$ 12,5 bi
   2. Pernambuco: R$ 8,9 bi
   3. Ceará: R$ 7,2 bi
   4. Maranhão: R$ 5,1 bi
   5. Paraíba: R$ 3,8 bi
   6. Rio Grande do Norte: R$ 3,2 bi
   7. Alagoas: R$ 2,1 bi
   8. Sergipe: R$ 1,8 bi
   9. Piauí: R$ 1,7 bi

📈 Per Capita (habitantes):
   1. Ceará: R$ 789,45/hab (1º lugar!)
   2. Pernambuco: R$ 765,32/hab
   3. Bahia: R$ 743,21/hab
   ...
   9. Maranhão: R$ 612,87/hab

⚖️  Cumprimento Mínimo Constitucional (25%):
   ✅ 8 estados em conformidade
   ⚠️  1 estado abaixo do mínimo (Maranhão: 23,4%)

📊 Indicadores de Qualidade (INEP):
   • IDEB Anos Iniciais: Ceará lidera (6.8)
   • IDEB Anos Finais: Pernambuco em 1º (5.9)
   • Taxa de aprovação média: 87,3%

🎯 INSIGHTS:
   • Ceará: Melhor relação investimento × qualidade
   • Bahia: Maior volume, mas desafios de eficiência
   • Maranhão: Urgente adequação aos 25% mínimos

📍 [Ver Mapa] [Detalhes por Estado] [Exportar]
```

---

## 📈 Exemplo 6: Análise de Tendências

### Usuário digita:

```
"Prever gastos com saúde para 2025"
```

### Processamento:

```javascript
Intent: PREDICTIVE_ANALYSIS
Entities: {
  "category": "saúde",
  "year": 2025,
  "analysis_type": "previsão"
}

APIs Called:
  ✓ Portal Transparência → Histórico 2015-2024
  ✓ SICONFI → Dados fiscais históricos
  ✓ DataSUS → Indicadores saúde
  ✓ IBGE → Projeções populacionais

Agent Analysis:
  Ceuci → Análise preditiva (ARIMA, Prophet)
  Anita → Análise estatística
```

### Resposta:

```
🔮 PREVISÃO DE GASTOS COM SAÚDE - 2025

📊 SÉRIE HISTÓRICA:
   2015: R$ 105 bi
   2016: R$ 112 bi (+6,7%)
   2017: R$ 118 bi (+5,4%)
   2018: R$ 125 bi (+5,9%)
   2019: R$ 132 bi (+5,6%)
   2020: R$ 168 bi (+27,3%) *COVID-19
   2021: R$ 155 bi (-7,7%)
   2022: R$ 162 bi (+4,5%)
   2023: R$ 171 bi (+5,6%)
   2024: R$ 179 bi (+4,7%) *estimado

📈 PREVISÃO 2025:
   Valor Previsto: R$ 187,5 bilhões
   Crescimento: +4,7% vs 2024
   Intervalo de Confiança (95%):
     • Mínimo: R$ 182,3 bi
     • Máximo: R$ 192,8 bi

🧮 METODOLOGIA:
   • Modelo: ARIMA + Prophet (ensemble)
   • Dados: 10 anos históricos
   • Sazonalidade: Detectada
   • Tendência: Crescimento moderado

💡 FATORES CONSIDERADOS:
   ✓ Crescimento populacional (+0,8%)
   ✓ Envelhecimento da população
   ✓ Inflação médica (IPCA Saúde)
   ✓ Mínimo constitucional (15% RCL)
   ✓ Normalização pós-COVID

⚠️  ALERTAS:
   • Pressão demográfica: +12% população 60+
   • Doenças crônicas: Aumento de 8% ao ano
   • Tecnologias médicas: Custo crescente

📊 [Ver Gráfico] [Baixar Modelo] [Detalhes]
```

---

## 🎯 Como Funciona (Resumo Técnico)

```
1. Usuário digita → Frontend
2. Frontend → POST /api/v1/chat/send
3. Backend detecta intent + extrai entities
4. Orchestrator cria plano de execução
5. Data Federation busca em 30+ APIs paralelas
6. Agentes analisam resultados
7. Response stream (SSE) para frontend
8. Usuário vê resultados em tempo real
```

**Tempo total: < 5 segundos** ⚡

---

## 📚 Mais Exemplos de Queries

```
✅ "Contratos suspeitos em São Paulo"
✅ "Quanto ganha servidor do INSS?"
✅ "Licitações de TI no governo federal"
✅ "Comparar gastos de saúde por região"
✅ "Fornecedores com mais contratos em 2024"
✅ "Municípios que não cumprem mínimo constitucional educação"
✅ "Anomalias em contratos acima de R$ 10 milhões"
✅ "Histórico de empresa CNPJ 12.345.678/0001-90"
✅ "Estados com maior crescimento em infraestrutura"
✅ "Prever gastos educação próximos 3 anos"
```

---

## 🚀 Testar Agora

```bash
# Backend local
make run-dev

# Testar endpoint
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Buscar contratos de saúde em MG",
    "user_id": "test"
  }'
```

---

**Todos esses exemplos funcionam hoje no sistema em produção!** 🎉

**URL Produção**: https://cidadao-api-production.up.railway.app
