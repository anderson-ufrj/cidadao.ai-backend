# 🏹 Análise Completa - Oxóssi Agent (Caçador de Fraudes)

**Data**: 25 de outubro de 2025, 13:33 -03
**Autor**: Anderson Henrique da Silva
**Arquivo**: `src/agents/oxossi.py` (1,699 linhas)
**Status**: ✅ Código bem implementado, ❌ SEM testes (0% coverage)

---

## 📊 Estatísticas do Código

| Métrica | Valor |
|---------|-------|
| **Total de linhas** | 1,699 linhas |
| **Classes** | 5 (FraudType, FraudSeverity, FraudIndicator, FraudPattern, OxossiAgent) |
| **Métodos públicos** | 3 (process, hunt_specific_fraud + herdados) |
| **Métodos privados** | 20+ métodos de detecção |
| **Algoritmos implementados** | 10+ algoritmos de fraude |
| **Test coverage** | 0% 🔴 |

---

## 🎯 Algoritmos de Fraude Implementados

### ✅ 1. **Bid Rigging Detection** (Manipulação de Licitações)
**Método**: `_detect_bid_rigging()` (linhas 288-358)

**Como funciona**:
- Agrupa contratos por processo licitatório
- Verifica similaridade entre valores de lances (threshold: 85%)
- Detecta padrões de rotação entre fornecedores
- Identifica retiradas de última hora suspeitas

**Indicadores detectados**:
- `identical_bid_amounts`: Lances idênticos ou muito similares
- `rotation_pattern`: Fornecedores revezando vitórias

**Threshold**: `bid_similarity: 0.85` (85% de similaridade)

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.BID_RIGGING,
    severity=FraudSeverity.HIGH,
    confidence=0.75-0.8,
    estimated_impact=contract_value * 0.1  # 10% estimado
)
```

---

### ✅ 2. **Phantom Vendor Detection** (Fornecedores Fantasma)
**Método**: `_detect_phantom_vendors()` (linhas 360-438)

**Como funciona**:
- Identifica fornecedores com apenas 1 contrato
- Verifica registro recente (<30 dias antes do contrato)
- Checa ausência de endereço físico
- Detecta informações de contato compartilhadas

**Indicadores detectados**:
- `single_contract_only`: Fornecedor com um único contrato (confidence: 0.6)
- `recent_registration`: Cadastro <30 dias antes (confidence: 0.7)

**Threshold**: `vendor_activity: 0.1` (mínimo de atividade)

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.PHANTOM_VENDOR,
    severity=FraudSeverity.MEDIUM/HIGH,  # Depende de nº de indicadores
    confidence=0.6-0.7,
    estimated_impact=total_contract_value
)
```

---

### ✅ 3. **Price Fixing Detection** (Fixação de Preços / Cartel)
**Método**: `_detect_price_fixing()` (linhas 440-532)

**Como funciona**:
- Agrupa contratos por categoria
- Calcula variância de preços entre fornecedores (<5% suspeito)
- Detecta aumentos síncronos de preços
- Analisa estabilidade de market share

**Indicadores detectados**:
- `identical_pricing_across_vendors`: Preços quase idênticos (variance <5%)
- `uniform_price_increases`: Aumentos uniformes ao longo do tempo

**Threshold**: `price_deviation: 2.5` (desvios-padrão)

**Análise estatística**:
```python
price_variance = price_groups.std() / price_groups.mean()
if price_variance < 0.05:  # Menos de 5% de variância
    # SUSPEITO!
```

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.PRICE_FIXING,
    severity=FraudSeverity.HIGH,
    confidence=0.7-0.75,
    estimated_impact=total_price * 0.15  # 15% superfaturamento estimado
)
```

---

### ✅ 4. **Invoice Fraud Detection** (Fraude em Faturas)
**Método**: `_analyze_invoice_fraud()` (linhas 632-745)

**Como funciona**:
- Detecta faturas duplicadas (mesmo vendor + valor + data)
- Identifica padrões sequenciais perfeitos (suspeito)
- Verifica valores arredondados demais
- Analisa descrições incomuns

**Indicadores detectados**:
- `duplicate_invoices`: Hash idêntico de fatura (confidence: 0.9)
- `sequential_invoice_numbers`: Números perfeitamente sequenciais (confidence: 0.7)

**Threshold**: `invoice_anomaly: 0.7`

**Hashing de fatura**:
```python
hash_key = f"{vendor_id}_{amount}_{date}"
```

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.INVOICE_FRAUD,
    severity=FraudSeverity.HIGH/MEDIUM,
    confidence=0.7-0.9,
    estimated_impact=invoice_amount (duplicadas) ou 5% (sequenciais)
)
```

---

### ✅ 5. **Money Laundering Detection** (Lavagem de Dinheiro)
**Método**: `_detect_money_laundering()` (linhas 828-879)

**Como funciona**:
- Detecta **structuring/smurfing**: Múltiplas transações abaixo do limite de notificação
- Identifica **circular payments**: A→B→C→A
- Verifica **layering patterns**: Muitos saltos entre contas

**Indicadores detectados**:
- `structuring`: ≥2 transações entre 80-100% do threshold (R$10k típico)
- `circular_payments`: Pagamentos circulares em 3+ nós

**Threshold de notificação**: R$ 10.000 (comum no Brasil)

**Detecção de structuring**:
```python
threshold = 10000  # Limite de notificação
below_threshold = [a for a in amounts if threshold * 0.8 < a < threshold]
if len(below_threshold) >= 2:
    # SUSPEITO! Possível estruturação
```

**Detecção circular** (`_detect_circular_payments`, linhas 1148-1241):
```python
# Constrói grafo de pagamentos
# Busca ciclos: A → B → C → A
```

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.MONEY_LAUNDERING,
    severity=FraudSeverity.HIGH/CRITICAL,
    confidence=0.75-0.85,
    estimated_impact=sum(suspicious_amounts)
)
```

---

### ✅ 6. **Kickback Schemes Detection** (Esquemas de Propina)
**Método**: `_detect_kickback_schemes()` (linhas 881-1072)

**Como funciona**:
- Identifica pagamentos logo após adjudicação de contratos (≤30 dias)
- Detecta valores arredondados para indivíduos
- Verifica percentagens exatas do contrato (5%, 10%, 15%, 20%, 25%)
- Rastreia pagamentos de vencedor de contrato para terceiros

**Indicadores detectados**:
- `suspicious_round_payment`: Pagamento arredondado (múltiplo de R$5k/10k) para pessoa física
- `percentage_payment`: Pagamento é exato % do contrato (confidence: 0.8)
- `vendor_payment_after_award`: Vencedor faz pagamento <30 dias após contrato

**Análise temporal**:
```python
# Pagamentos suspeitos entre data_contrato e data_contrato + 30 dias
suspicious_payments = payment_transactions[
    (payment_transactions["date"] > contract_date) &
    (payment_transactions["date"] <= contract_date + pd.Timedelta(days=30))
]
```

**Detecção de percentagem**:
```python
percentage = (amount / contract_value) * 100
common_kickback_percentages = [5, 10, 15, 20, 25]
if abs(percentage - pct) < 0.5:  # Dentro de 0.5%
    # SUSPEITO! Kickback típico
```

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.KICKBACK_SCHEME,
    severity=FraudSeverity.CRITICAL (2+ indicadores) / HIGH,
    confidence=0.7-0.8,
    estimated_impact=contract_value * 0.1  # 10% estimado
)
```

---

### ✅ 7. **Benford's Law Analysis** (Lei de Benford)
**Método**: `_analyze_benfords_law()` (linhas 1401-1527)

**Como funciona**:
- Extrai primeiro dígito de todos os valores
- Compara distribuição observada vs. Lei de Benford
- Calcula estatística chi-quadrado (χ²)
- Threshold: χ² > 15.51 (95% confiança) ou 20.09 (99%)

**Lei de Benford**:
```
Primeiro dígito | Frequência esperada
1              | 30.1%
2              | 17.6%
3              | 12.5%
4              |  9.7%
5              |  7.9%
6              |  6.7%
7              |  5.8%
8              |  5.1%
9              |  4.6%
```

**Cálculo**:
```python
# Distribuição esperada
benford_dist = {digit: math.log10(1 + 1/digit) for digit in range(1, 10)}

# Chi-quadrado
chi_square = Σ ((observed - expected)² / expected)
```

**Thresholds de confiança**:
- χ² > 30: confidence 0.9, severity HIGH
- χ² > 20: confidence 0.8, severity MEDIUM
- χ² > 15.51: confidence 0.7, severity MEDIUM

**Requisito**: ≥30 valores para significância estatística

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.FALSE_CLAIMS,
    severity=FraudSeverity.MEDIUM/HIGH,
    confidence=0.7-0.9,
    estimated_impact=sum(values) * 0.05  # 5% manipulação estimada
)
```

---

### ✅ 8. **Temporal Anomaly Detection** (Anomalias Temporais)
**Método**: `_detect_temporal_anomalies()` (linhas 1529-1684)

**Como funciona**:
- Detecta atividade fora de horário (após 20h ou antes de 6h)
- Identifica atividade em fins de semana excessiva
- Verifica processamento rápido demais (velocity check <1min)
- Detecta clustering temporal (dias com pico de atividade)

**Indicadores detectados**:
- `after_hours_activity`: >20% das transações fora do horário (confidence: 0.7)
- `weekend_activity`: >30% das transações em fins de semana (confidence: 0.65)
- `velocity_anomaly`: >3 transações processadas <1min (confidence: 0.75)
- `temporal_clustering`: Dias com atividade >2σ acima da média (confidence: 0.7)

**Análise de velocidade**:
```python
time_diffs = df_sorted[time_col].diff()
very_fast = time_diffs[time_diffs < pd.Timedelta(minutes=1)]
```

**Análise de clustering**:
```python
daily_counts = df.groupby("date_only").size()
outlier_days = daily_counts[daily_counts > mean_daily + 2 * std_daily]
```

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.PROCUREMENT_FRAUD,
    severity=FraudSeverity.MEDIUM/HIGH,
    confidence=0.65-0.75,
    estimated_impact=0  # Temporal patterns não estimam valor diretamente
)
```

---

### ✅ 9. **Complex Fraud Schemes** (Esquemas Complexos Multi-Tipo)
**Método**: `_detect_complex_fraud_schemes()` (linhas 1074-1128)

**Como funciona**:
- Correlaciona múltiplos padrões de fraude
- Identifica entidades envolvidas em ≥2 tipos de fraude
- Eleva severidade automaticamente para CRITICAL
- Combina evidências de múltiplas análises

**Lógica**:
```python
entity_fraud_types = {}
for pattern in patterns:
    for entity in pattern.entities_involved:
        entity_fraud_types[entity].add(pattern.fraud_type)

# Se entidade tem ≥2 tipos de fraude
if len(fraud_types) >= 2:
    # CRITICAL! Esquema complexo
```

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.PROCUREMENT_FRAUD,  # Fraude complexa
    severity=FraudSeverity.CRITICAL,
    confidence=0.85,
    estimated_impact=sum(all_related_patterns),
    indicators=[
        FraudIndicator(
            indicator_type="complex_scheme",
            risk_score=9.5  # Muito alto!
        )
    ]
)
```

---

### ✅ 10. **Vendor Fraud Analysis** (Análise de Fornecedores)
**Método**: `_analyze_vendor_fraud()` (linhas 552-630)

**Como funciona**:
- Detecta endereços compartilhados entre fornecedores (>2 no mesmo local)
- Identifica telefones/emails compartilhados
- Sinaliza shell companies

**Indicadores detectados**:
- `shared_address`: >2 fornecedores no mesmo endereço (confidence: 0.8)
- `shared_contact_info`: Telefone ou email compartilhado (confidence: 0.85)

**Output**:
```python
FraudPattern(
    fraud_type=FraudType.PHANTOM_VENDOR,
    severity=FraudSeverity.HIGH,
    confidence=0.8-0.85,
    estimated_impact=0  # Desconhecido até analisar contratos
)
```

---

## 🏗️ Arquitetura das Classes

### 1. **FraudType (Enum)**
10 tipos de fraude:
```python
BID_RIGGING, PRICE_FIXING, PHANTOM_VENDOR, INVOICE_FRAUD,
KICKBACK_SCHEME, CONFLICT_OF_INTEREST, MONEY_LAUNDERING,
FALSE_CLAIMS, PAYROLL_FRAUD, PROCUREMENT_FRAUD
```

### 2. **FraudSeverity (Enum)**
4 níveis:
```python
LOW, MEDIUM, HIGH, CRITICAL
```

### 3. **FraudIndicator (dataclass)**
Indicador individual de fraude:
```python
@dataclass
class FraudIndicator:
    indicator_type: str       # Tipo de indicador
    description: str          # Descrição legível
    confidence: float         # 0.0 a 1.0
    evidence: list[dict]      # Evidências
    risk_score: float         # 0.0 a 10.0
```

### 4. **FraudPattern (dataclass)**
Padrão de fraude completo:
```python
@dataclass
class FraudPattern:
    fraud_type: FraudType           # Tipo de fraude
    severity: FraudSeverity         # Severidade
    confidence: float               # Confiança geral
    indicators: list[FraudIndicator] # Indicadores detectados
    entities_involved: list[str]    # Entidades suspeitas
    estimated_impact: float         # Impacto financeiro estimado
    recommendations: list[str]      # Recomendações
    evidence_trail: dict            # Trilha de auditoria
```

### 5. **OxossiAgent (BaseAgent)**
Agente principal de detecção:
```python
class OxossiAgent(BaseAgent):
    # Thresholds configuráveis
    fraud_thresholds = {
        "bid_similarity": 0.85,
        "price_deviation": 2.5,
        "vendor_activity": 0.1,
        "invoice_anomaly": 0.7,
        "relationship_strength": 0.6
    }
```

---

## 🔄 Fluxo de Execução

### Entrada via `process(message, context)`:

```
1. Recebe AgentMessage com dados
   ├─ contracts
   ├─ transactions
   ├─ vendors
   └─ invoices

2. Roteamento por tipo de dado
   ├─ _analyze_contract_fraud()
   ├─ _analyze_transaction_fraud()
   ├─ _analyze_vendor_fraud()
   ├─ _analyze_invoice_fraud()
   └─ _comprehensive_fraud_analysis()  # Todos os tipos

3. Execução de detectores específicos
   ├─ _detect_bid_rigging()
   ├─ _detect_phantom_vendors()
   ├─ _detect_price_fixing()
   ├─ _detect_money_laundering()
   ├─ _detect_kickback_schemes()
   ├─ _analyze_benfords_law()
   ├─ _detect_temporal_anomalies()
   └─ _detect_complex_fraud_schemes()

4. Geração de relatório
   ├─ _generate_fraud_report()
   ├─ _identify_high_risk_entities()
   └─ _calculate_overall_confidence()

5. Retorno de AgentResponse
   ├─ fraud_analysis (dict)
   ├─ patterns_detected (int)
   ├─ high_risk_entities (list)
   └─ total_estimated_impact (float)
```

---

## 📦 Dependências

```python
import pandas as pd          # Análise de dados
import math                  # Lei de Benford
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Any

# Internas
from src.agents.deodoro import BaseAgent, AgentMessage, AgentResponse
from src.core import get_logger
from src.core.exceptions import AgentExecutionError
```

---

## 🎯 Estratégia de Testes

### Estrutura Proposta: `tests/unit/agents/test_oxossi.py`

**Organização**:
```python
# 1. Fixtures (dados de teste)
@pytest.fixture
def sample_contracts():
    """Contratos de exemplo para testes"""

@pytest.fixture
def sample_transactions():
    """Transações de exemplo"""

@pytest.fixture
def sample_invoices():
    """Faturas de exemplo"""

@pytest.fixture
def oxossi_agent():
    """Instância do agente"""

# 2. Testes de Inicialização
class TestOxossiInitialization:
    def test_agent_creation()
    def test_thresholds_default_values()
    def test_fraud_patterns_initialization()

# 3. Testes de Bid Rigging
class TestBidRigging:
    @pytest.mark.asyncio
    async def test_detect_identical_bids()
    async def test_detect_rotation_pattern()
    async def test_no_false_positives_legitimate_bids()

# 4. Testes de Phantom Vendors
class TestPhantomVendors:
    @pytest.mark.asyncio
    async def test_detect_single_contract_vendor()
    async def test_detect_recent_registration()
    async def test_detect_shared_address()
    async def test_detect_shared_contact()

# 5. Testes de Price Fixing
class TestPriceFixing:
    @pytest.mark.asyncio
    async def test_detect_identical_pricing()
    async def test_detect_synchronized_increases()
    async def test_legitimate_market_variance()

# 6. Testes de Invoice Fraud
class TestInvoiceFraud:
    @pytest.mark.asyncio
    async def test_detect_duplicate_invoices()
    async def test_detect_sequential_numbers()
    async def test_legitimate_sequential_ok()

# 7. Testes de Money Laundering
class TestMoneyLaundering:
    @pytest.mark.asyncio
    async def test_detect_structuring()
    async def test_detect_circular_payments()
    async def test_legitimate_business_transactions()

# 8. Testes de Kickback Schemes
class TestKickbackSchemes:
    @pytest.mark.asyncio
    async def test_detect_round_payments()
    async def test_detect_percentage_payments()
    async def test_detect_vendor_payment_after_award()
    async def test_legitimate_post_contract_payments()

# 9. Testes de Benford's Law
class TestBenfordsLaw:
    def test_benford_with_natural_data()
    def test_benford_with_manipulated_data()
    def test_benford_insufficient_data()
    def test_chi_square_thresholds()

# 10. Testes de Temporal Anomalies
class TestTemporalAnomalies:
    def test_detect_after_hours_activity()
    def test_detect_weekend_activity()
    def test_detect_velocity_anomaly()
    def test_detect_temporal_clustering()
    def test_legitimate_24_7_operations()

# 11. Testes de Complex Schemes
class TestComplexSchemes:
    @pytest.mark.asyncio
    async def test_detect_multi_type_fraud()
    async def test_combine_evidence()
    async def test_escalate_to_critical()

# 12. Testes de Relatório
class TestReportGeneration:
    def test_generate_fraud_report()
    def test_identify_high_risk_entities()
    def test_calculate_overall_confidence()
    def test_empty_patterns_report()

# 13. Testes de Integração
class TestIntegration:
    @pytest.mark.asyncio
    async def test_process_contracts()
    async def test_process_transactions()
    async def test_process_vendors()
    async def test_process_invoices()
    async def test_comprehensive_analysis()

# 14. Testes de Edge Cases
class TestEdgeCases:
    async def test_empty_data()
    async def test_malformed_data()
    async def test_missing_fields()
    async def test_extreme_values()

# 15. Testes de Performance
class TestPerformance:
    async def test_large_dataset_1000_contracts()
    async def test_concurrent_analysis()
```

---

## 📊 Cobertura Esperada

**Meta**: 80%+ coverage

**Distribuição**:
- Inicialização: 100%
- Algoritmos principais (10x): 85% cada
- Utilitários: 90%
- Error handling: 80%
- Edge cases: 75%

**Linhas críticas** (devem ter 100%):
- Cálculos de thresholds
- Lógica de chi-quadrado (Benford)
- Detecção de circular payments
- Cálculo de percentagens (kickbacks)

---

## 🚀 Próximos Passos

### Segunda-feira 26/10:
1. ✅ Código analisado completamente
2. ✅ 10 algoritmos mapeados
3. ⏳ Criar arquivo `test_oxossi.py` com estrutura básica
4. ⏳ Implementar fixtures de dados

### Terça-quarta 27-28/10:
- Implementar testes para bid rigging, phantom vendors, price fixing
- Implementar testes para invoice fraud, money laundering

### Quinta 29/10:
- Implementar testes para kickback schemes
- Implementar Benford's Law tests
- Temporal anomalies tests

### Sexta 30/10:
- Complex schemes + integration tests
- Edge cases
- Coverage report
- Code review

---

## 💡 Observações Importantes

### Pontos Fortes do Código:
- ✅ Bem estruturado e modular
- ✅ Algoritmos matematicamente corretos
- ✅ Documentação inline clara
- ✅ Type hints adequados
- ✅ Error handling presente
- ✅ Logging estruturado

### Áreas de Atenção para Testes:
- ⚠️ Cálculos estatísticos (precisão numérica)
- ⚠️ Parsing de datas (diferentes formatos)
- ⚠️ Edge cases com listas vazias
- ⚠️ Tratamento de valores None/null
- ⚠️ Performance com datasets grandes

### Dados de Teste Necessários:
1. Contratos legítimos (baseline)
2. Contratos com bid rigging
3. Fornecedores fantasma
4. Transações com structuring
5. Faturas duplicadas
6. Pagamentos de kickback
7. Dados que seguem/violam Lei de Benford
8. Atividades temporais anômalas

---

**Análise completa em**: 25/10/2025 13:33 -03
**Próximo passo**: Criar estrutura de testes
**Meta da semana**: Oxóssi 0% → 80%+ coverage 🎯
