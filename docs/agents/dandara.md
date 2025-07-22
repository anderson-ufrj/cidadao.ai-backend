# 🌺 Dandara - Social Justice Agent

**Codinome:** `dandara`  
**Especialização:** Agente de Justiça Social  
**Inspiração:** Dandara dos Palmares - Guerreira quilombola e símbolo da luta por justiça social

## 🎯 Missão

Monitorar políticas de inclusão, equidade social e indicadores de justiça distributiva no contexto dos dados públicos brasileiros.

## ⚡ Capacidades

- **Análise de Equidade Social**: Cálculo de índices de desigualdade (Gini, Theil, Atkinson)
- **Monitoramento de Políticas de Inclusão**: Avaliação de efetividade de programas sociais
- **Detecção de Violações de Justiça**: Identificação de discriminação e exclusão
- **Mapeamento de Vulnerabilidade**: Análise interseccional de grupos vulneráveis
- **Avaliação de Impacto Social**: Mensuração de resultados em justiça distributiva

## 🏛️ Fontes de Dados

- **IBGE**: Censos e pesquisas sociodemográficas
- **DataSUS**: Dados de saúde pública
- **INEP**: Indicadores educacionais
- **MDS**: Programas sociais do governo
- **Portal da Transparência**: Gastos sociais
- **RAIS/PNAD**: Dados de emprego e renda

## 🔧 Funcionalidades Técnicas

### Métricas de Equidade
```python
# Principais métricas calculadas
gini_coefficient: float      # 0.0-1.0 (desigualdade)
atkinson_index: float        # Índice de Atkinson
theil_index: float          # Índice de Theil
palma_ratio: float          # Top 10% / Bottom 40%
quintile_ratio: float       # Razão entre quintis
```

### Detecção de Violações
```python
violation_types = [
    "discriminatory_resource_allocation",
    "unequal_service_access",
    "policy_exclusion_bias", 
    "demographic_underrepresentation"
]
```

### Análise de Gaps de Inclusão
```python
gap_areas = [
    "digital_inclusion",
    "healthcare_access", 
    "education_equity",
    "employment_opportunities"
]
```

## 📊 Outputs Típicos

- **Score de Equidade**: 0-100 (metodologia transparente)
- **Violações Detectadas**: Lista com referências legais
- **Gaps de Inclusão**: Quantificados por área
- **Recomendações**: Baseadas em evidências
- **Hash de Auditoria**: SHA-256 para rastreabilidade

## 🎯 Casos de Uso

1. **Avaliação de Programas Sociais**
   - Efetividade do Auxílio Brasil
   - Cobertura do SUS por região
   - Acesso à educação por grupos

2. **Monitoramento de Desigualdades**
   - Evolução do índice de Gini municipal
   - Disparidades de renda por gênero/raça
   - Acesso a serviços públicos

3. **Análise de Políticas de Inclusão**
   - Programas de cotas universitárias
   - Políticas de habitação social
   - Iniciativas de inclusão digital

## 🚨 Alertas e Violações

O agente monitora automaticamente:
- Violações da CF/88 Art. 5º (igualdade)
- Não cumprimento de metas sociais
- Discriminação em políticas públicas
- Exclusão de grupos vulneráveis

## 📈 Métricas de Performance

- **Confiabilidade**: 85% (baseada em dados oficiais)
- **Cobertura**: Nacional, estadual, municipal
- **Frequência**: Análises mensais/trimestrais
- **Latência**: < 30 segundos para análises padrão

## 🔗 Integração com Outros Agentes

- **José Bonifácio**: Avaliação de políticas públicas
- **Investigator**: Detecção de anomalias sociais
- **Reporter**: Relatórios de justiça social

## 📚 Referências Legais

- Constituição Federal Art. 5º (Igualdade)
- Lei 12.288/10 (Estatuto da Igualdade Racial)
- Lei 13.146/15 (Lei da Inclusão)
- ODS 10 (Redução das Desigualdades)

---
*Documentação técnica - Cidadão.AI Backend v2.0*