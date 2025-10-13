# 🏹 Oxóssi - Caçador de Fraudes

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Status**: ✅ **100% Completo** (Produção - Pronto para uso)
**Arquivo**: `src/agents/oxossi.py`
**Tamanho**: 39KB
**Métodos Implementados**: ~20
**Testes**: ✅ Sim (`tests/unit/agents/test_oxossi.py`)
**TODOs**: 0
**NotImplementedError**: 0
**Última Atualização**: 2025-10-03 08:31:53 -03:00

---

## 🎯 Missão

Detecção e rastreamento de fraudes em contratos governamentais e transações financeiras com precisão cirúrgica, identificando esquemas complexos de corrupção através de análise de padrões e relacionamentos.

**Inspiração Cultural**: Oxóssi é o orixá da caça na mitologia Yorubá, conhecido por sua precisão, foco e habilidade de rastrear alvos através de qualquer terreno.

---

## 🔍 Tipos de Fraude Detectadas

### Enum FraudType (10 categorias)

```python
class FraudType(Enum):
    BID_RIGGING = "bid_rigging"                    # Manipulação de licitações
    PRICE_FIXING = "price_fixing"                  # Cartelização de preços
    PHANTOM_VENDOR = "phantom_vendor"              # Fornecedores fantasma
    INVOICE_FRAUD = "invoice_fraud"                # Fraude em notas fiscais
    KICKBACK_SCHEME = "kickback_scheme"            # Propina e suborno
    CONFLICT_OF_INTEREST = "conflict_of_interest"  # Conflito de interesses
    MONEY_LAUNDERING = "money_laundering"          # Lavagem de dinheiro
    FALSE_CLAIMS = "false_claims"                  # Reivindicações falsas
    PAYROLL_FRAUD = "payroll_fraud"                # Fraude na folha de pagamento
    PROCUREMENT_FRAUD = "procurement_fraud"        # Fraude em compras públicas
```

---

## 🧠 Algoritmos e Técnicas Implementadas

### 1. Detecção de Bid Rigging (Manipulação de Licitações)

**Indicadores**:
- ✅ Valores de proposta idênticos
- ✅ Números sequenciais de propostas
- ✅ Padrão de rotação entre vencedores
- ✅ Retiradas de última hora coordenadas

**Threshold**: 0.85 similaridade, 0.7 confiança mínima

### 2. Price Fixing (Cartelização)

**Indicadores**:
- ✅ Aumentos uniformes de preço entre competidores
- ✅ Preços idênticos entre fornecedores
- ✅ Estabilidade anômala de preços
- ✅ Market share estável entre concorrentes

**Threshold**: 2.5 desvios padrão, 0.65 confiança mínima

### 3. Phantom Vendor (Fornecedor Fantasma)

**Indicadores**:
- ✅ Ausência de endereço físico
- ✅ Registro recente (< 6 meses)
- ✅ Contrato único sem histórico
- ✅ Sem presença web verificável
- ✅ Informações de contato compartilhadas

**Threshold**: 0.75 confiança mínima

### 4. Invoice Fraud (Fraude em Notas Fiscais)

**Indicadores**:
- ✅ Notas fiscais duplicadas
- ✅ Números sequenciais suspeitos
- ✅ Valores arredondados anômalos
- ✅ Descrições incomuns ou genéricas
- ✅ Anomalias temporais (fins de semana, feriados)

**Threshold**: 0.7 confiança, 0.7 anomalia

### 5. Análise de Relacionamentos

**Técnicas**:
- ✅ Graph Analysis para rede de entidades
- ✅ Strength Score para conexões suspeitas
- ✅ Cluster Detection para grupos coordenados
- ✅ Temporal Correlation para padrões temporais

**Threshold**: 0.6 para força de relacionamento suspeito

---

## 📊 Severidade de Fraudes

```python
class FraudSeverity(Enum):
    LOW = "low"         # Risco < 3.0, Impacto < R$ 100k
    MEDIUM = "medium"   # Risco 3.0-6.0, Impacto R$ 100k-1M
    HIGH = "high"       # Risco 6.0-9.0, Impacto R$ 1M-10M
    CRITICAL = "critical" # Risco > 9.0, Impacto > R$ 10M
```

---

## 🔧 Capacidades Principais

### ✅ Análise de Contratos
```python
async def _analyze_contract_fraud(contracts, context) -> List[FraudPattern]
```
- Detecção de bid rigging
- Identificação de conflitos de interesse
- Análise de concentração de fornecedores
- Verificação de valores atípicos

### ✅ Análise de Transações
```python
async def _analyze_transaction_fraud(transactions, context) -> List[FraudPattern]
```
- Padrões de lavagem de dinheiro
- Transações estruturadas (smurfing)
- Rotas de pagamento suspeitas
- Timing anômalo

### ✅ Análise de Fornecedores
```python
async def _analyze_vendor_fraud(vendors, context) -> List[FraudPattern]
```
- Verificação de fornecedores fantasma
- Análise de histórico de atividades
- Validação de documentação
- Rede de relacionamentos

### ✅ Análise de Notas Fiscais
```python
async def _analyze_invoice_fraud(invoices, context) -> List[FraudPattern]
```
- Detecção de duplicatas
- Análise de padrões sequenciais
- Verificação de valores arredondados
- Anomalias de timing

### ✅ Análise Abrangente
```python
async def _comprehensive_fraud_analysis(data, context) -> List[FraudPattern]
```
- Combina todas as técnicas
- Cross-referência entre fontes
- Identificação de esquemas complexos
- Trilha de evidências completa

---

## 📋 Estrutura de Dados

### FraudIndicator
```python
@dataclass
class FraudIndicator:
    indicator_type: str
    description: str
    confidence: float  # 0.0 to 1.0
    evidence: List[Dict[str, Any]]
    risk_score: float  # 0.0 to 10.0
```

### FraudPattern
```python
@dataclass
class FraudPattern:
    fraud_type: FraudType
    severity: FraudSeverity
    confidence: float
    indicators: List[FraudIndicator]
    entities_involved: List[str]
    estimated_impact: float  # Em reais (R$)
    recommendations: List[str]
    evidence_trail: Dict[str, Any]
```

---

## 💻 Exemplo de Uso

### Detectar Fraude em Licitação

```python
from src.agents.oxossi import OxossiAgent, FraudType

# Inicializar agente
oxossi = OxossiAgent()
await oxossi.initialize()

# Dados de licitação
message = AgentMessage(
    content="Analisar licitação para possível bid rigging",
    data={
        "contracts": [
            {
                "id": "001/2025",
                "vendor": "Empresa A LTDA",
                "value": 500_000.00,
                "bid_date": "2025-01-15"
            },
            {
                "id": "002/2025",
                "vendor": "Empresa B LTDA",
                "value": 500_000.00,  # Mesmo valor!
                "bid_date": "2025-01-15"  # Mesma data!
            },
            {
                "id": "003/2025",
                "vendor": "Empresa C LTDA",
                "value": 499_999.99,  # Quase idêntico!
                "bid_date": "2025-01-15"
            }
        ]
    }
)

# Processar
response = await oxossi.process(message, context)

# Resultado
print(response.data["fraud_analysis"])
# {
#   "patterns_detected": 1,
#   "fraud_type": "BID_RIGGING",
#   "severity": "HIGH",
#   "confidence": 0.92,
#   "indicators": [
#     {"type": "identical_bid_amounts", "confidence": 0.95},
#     {"type": "suspicious_timing", "confidence": 0.88}
#   ],
#   "entities_involved": ["Empresa A", "Empresa B", "Empresa C"],
#   "estimated_impact": 1_500_000.00,
#   "recommendations": [
#     "Investigar relacionamento entre empresas",
#     "Verificar sócios e representantes legais",
#     "Analisar licitações anteriores",
#     "Acionar Controladoria Geral da União"
#   ]
# }
```

### Identificar Fornecedor Fantasma

```python
message = AgentMessage(
    content="Verificar legitimidade de fornecedor",
    data={
        "vendors": [{
            "name": "ABC Consultoria LTDA",
            "cnpj": "12.345.678/0001-99",
            "registration_date": "2025-01-10",  # Recente!
            "physical_address": None,  # Sem endereço!
            "website": None,  # Sem site!
            "contracts": [
                {"id": "001/2025", "value": 2_000_000.00}  # Único contrato!
            ],
            "contact": {
                "phone": "11-98765-4321",  # Mesmo de outra empresa?
                "email": "contato@xyz.com"  # Email genérico
            }
        }]
    }
)

response = await oxossi.process(message, context)

# Detecta PHANTOM_VENDOR com alta confiança
print(response.data["fraud_analysis"]["fraud_type"])
# "PHANTOM_VENDOR"
print(response.data["fraud_analysis"]["confidence"])
# 0.89
```

---

## 🧪 Testes

### Cobertura de Testes

- ✅ **Testes unitários**: `tests/unit/agents/test_oxossi.py`
- ✅ **Testes de integração**: Incluído em multi-agent tests
- ✅ **Testes de performance**: Verificação com grandes datasets

### Cenários Testados

1. **Bid Rigging Detection**
   - Propostas idênticas
   - Rotação de vencedores
   - Retiradas coordenadas

2. **Price Fixing**
   - Cartel de preços
   - Aumentos sincronizados
   - Estabilidade anômala

3. **Phantom Vendors**
   - Sem documentação
   - Registro recente
   - Contrato único

4. **Invoice Fraud**
   - Duplicatas
   - Valores suspeitos
   - Timing anômalo

---

## 🔄 Integração com Outros Agentes

### Consumidores

1. **Abaporu (Master)**
   - Recebe análise de fraude como parte de investigações
   - Coordena ações com outros agentes

2. **Zumbi (Investigator)**
   - Complementa detecção de anomalias
   - Fornece dados de contratos para análise

3. **Tiradentes (Reporter)**
   - Gera relatórios de fraude em linguagem clara
   - Formata trilha de evidências

4. **Drummond (Communicator)**
   - Envia alertas de fraude crítica
   - Notifica stakeholders relevantes

### Fontes de Dados

- ✅ Portal da Transparência (contratos, fornecedores)
- ✅ Dados.gov.br (informações cadastrais)
- ✅ Base interna de padrões conhecidos
- ⚠️ Receita Federal (via API - requer credenciais)

---

## 📊 Métricas e Monitoramento

### Métricas Prometheus

```python
# Fraudes detectadas
oxossi_fraud_patterns_detected_total{type="bid_rigging", severity="high"}

# Tempo de análise
oxossi_analysis_duration_seconds{type="comprehensive"}

# Confiança média
oxossi_detection_confidence_avg{type="phantom_vendor"}

# Impacto financeiro total
oxossi_fraud_impact_total_brl
```

---

## 🏆 Diferenciais

### Por que Oxóssi é Único

1. **✅ 100% Implementado** - Sem TODOs ou placeholders
2. **🎯 Precisão Cirúrgica** - 10 tipos de fraude específicos
3. **🧠 ML-Ready** - Estrutura preparada para modelos treinados
4. **📈 Scalable** - Análise de milhares de transações
5. **🔗 Network Analysis** - Detecta esquemas complexos multi-entidade
6. **📊 Evidence Trail** - Trilha completa de evidências para auditoria

### Comparação com Zumbi (Investigator)

| Aspecto | Zumbi | Oxossi |
|---------|-------|--------|
| **Foco** | Anomalias estatísticas | Padrões de fraude |
| **Técnica** | FFT, Z-score | Graph analysis, Pattern matching |
| **Saída** | Anomalias gerais | Fraudes específicas |
| **Severidade** | Baseada em desvio | Baseada em impacto + risco |
| **Uso** | Triagem inicial | Investigação profunda |

**Trabalham juntos**: Zumbi detecta anomalias → Oxóssi classifica como fraude específica

---

## 🚀 Roadmap Futuro

### Melhorias Planejadas

1. **Machine Learning**
   - Treinar modelo de classificação de fraudes
   - Fine-tuning em dados brasileiros
   - Detecção de novos padrões automaticamente

2. **Integrações Externas**
   - API Receita Federal (validação CNPJ)
   - Junta Comercial (verificação de sócios)
   - TSE (doações de campanha - conflitos)

3. **Visualizações**
   - Network graphs de relacionamentos
   - Timeline de eventos suspeitos
   - Heatmap de riscos por órgão

4. **Analytics Preditiva**
   - Score de risco de fornecedores
   - Predição de fraudes futuras
   - Early warning system

---

## 📚 Referências

### Cultural
- **Orixá Oxóssi**: Caçador da mitologia Yorubá
- **Atributos**: Precisão, foco, rastreamento, justiça

### Técnicas
- **Network Analysis**: Graph theory para relacionamentos
- **Pattern Recognition**: Template matching avançado
- **Fraud Triangle**: Motivação, Oportunidade, Racionalização
- **Benford's Law**: Detecção de números fabricados

### Legislação Brasileira
- Lei 8.666/93 (Licitações)
- Lei 12.846/13 (Lei Anticorrupção)
- Lei 14.133/21 (Nova Lei de Licitações)

---

## ⚠️ Limitações Conhecidas

### Técnicas
- ❌ Não detecta fraudes nunca vistas (requer padrões conhecidos)
- ❌ Não acessa sistemas externos automaticamente (requer APIs)
- ⚠️ Alta dependência da qualidade dos dados de entrada

### Legais
- ⚠️ Detecção não constitui prova jurídica
- ⚠️ Requer validação humana antes de ações legais
- ⚠️ Resultados devem ser auditados por especialistas

---

## 🤝 Contribuindo

Para melhorar Oxóssi:

1. **Adicionar novos padrões de fraude** específicos do Brasil
2. **Integrar fontes de dados** governamentais
3. **Treinar modelos ML** com dados históricos
4. **Expandir testes** com casos reais anonimizados

---

## ✅ Status de Produção

**Deploy**: ✅ Pronto para produção
**Testes**: ✅ 100% dos cenários críticos cobertos
**Documentação**: ✅ Completa
**Performance**: ✅ Testado com 10k+ transações
**Segurança**: ✅ Logs de auditoria implementados

**Aprovado para uso em**:
- ✅ Investigações internas
- ✅ Auditorias automatizadas
- ✅ Triagem de denúncias
- ⚠️ Casos judiciais (como ferramenta de apoio)

---

**Autor**: Anderson Henrique da Silva
**Manutenção**: Ativa
**Versão**: 1.0 (Produção)
**License**: Proprietary
