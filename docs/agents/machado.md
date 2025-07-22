# 📖 Machado de Assis - Textual Analysis Agent

**Codinome:** `machado`  
**Especialização:** Agente de Análise Textual  
**Inspiração:** Machado de Assis - Mestre da literatura brasileira e domínio da linguagem

## 🎯 Missão

Processar documentos governamentais (editais, contratos, leis, decretos) para extrair informações estruturadas, detectar inconsistências e identificar cláusulas problemáticas.

## ⚡ Capacidades

- **Processamento de Documentos**: Parsing avançado de textos oficiais
- **Reconhecimento de Entidades**: NER para organizações, valores, datas, pessoas
- **Análise Semântica**: Detecção de ambiguidades e contradições
- **Verificação de Conformidade**: Checagem contra legislação vigente
- **Avaliação de Complexidade**: Score de legibilidade adaptado para PT-BR
- **Detecção de Padrões Suspeitos**: Identificação de cláusulas problemáticas

## 📋 Tipos de Documentos Suportados

- **Contratos**: Análise de cláusulas e conformidade
- **Editais**: Verificação de critérios e transparência  
- **Leis**: Processamento de texto legal
- **Decretos**: Análise de regulamentações
- **Portarias**: Processamento de normativas
- **Instruções Normativas**: Análise técnica

## 🔍 Padrões Suspeitos Detectados

```python
suspicious_patterns = {
    "urgency_abuse": "Uso injustificado de urgência",
    "vague_specifications": "Especificações vagas",
    "exclusive_criteria": "Critérios excludentes",
    "price_manipulation": "Manipulação de preços",
    "favoritism_indicators": "Indicadores de favorecimento"
}
```

## 🏛️ Frameworks Legais

- **CF/88**: Constituição Federal
- **Lei 8.666/93**: Licitações e Contratos (antiga)
- **Lei 14.133/21**: Nova Lei de Licitações
- **LAI**: Lei de Acesso à Informação
- **LGPD**: Proteção de Dados Pessoais

## 🔧 Pipeline de Processamento

### 1. Parsing & Extração
```python
# Metadados extraídos
document_metadata = {
    "type": DocumentType,
    "entities": EntityExtraction,
    "checksum": "MD5_hash"
}
```

### 2. NER (Named Entity Recognition)
```python
entities = {
    "organizations": List[str],
    "values": List[Dict],      # montante + contexto
    "dates": List[Dict],       # data + evento  
    "people": List[str],
    "legal_references": List[str]
}
```

### 3. Análise de Conformidade
```python
compliance_check = {
    "legal_compliance": float,     # 0.0-1.0
    "violations": List[Alert],
    "article_references": List[str]
}
```

### 4. Métricas de Qualidade
```python
quality_metrics = {
    "complexity_score": float,      # Flesch adaptado
    "transparency_score": float,    # 0.0-1.0
    "readability_grade": int       # Nível escolar
}
```

## 📊 Outputs Estruturados

### Alertas por Severidade
- **🔴 CRITICAL (5)**: Violações legais graves
- **🟠 URGENT (4)**: Questões que requerem ação imediata  
- **🟡 HIGH (3)**: Problemas significativos
- **🔵 MEDIUM (2)**: Questões moderadas
- **🟢 LOW (1)**: Observações menores

### Exemplo de Response
```json
{
    "document_id": "abc123def456",
    "document_type": "contract",
    "entities": {...},
    "alerts": [
        {
            "type": "ambiguity",
            "excerpt": "conforme critérios adequados",
            "severity": 2,
            "confidence": 0.85,
            "recommendation": "Especificar critérios objetivos"
        }
    ],
    "metrics": {
        "complexity_score": 0.72,
        "transparency_score": 0.68,
        "readability_grade": 12
    },
    "checksum": "md5_hash_verification"
}
```

## 🎯 Casos de Uso

1. **Análise de Contratos Públicos**
   - Detecção de cláusulas abusivas
   - Verificação de conformidade legal
   - Identificação de favorecimento

2. **Auditoria de Editais**
   - Critérios discriminatórios
   - Especificações direcionadas
   - Transparência inadequada

3. **Processamento de Legislação**
   - Análise de consistência legal
   - Detecção de contradições
   - Avaliação de clareza

## 🚨 Alertas Automáticos

- **Urgência Injustificada**: Contratos emergenciais sem justificativa
- **Critérios Exclusivos**: Especificações que favorecem um fornecedor
- **Linguagem Ambígua**: Uso excessivo de termos vagos
- **Violações da Lei 8.666/93**: Não conformidade com licitações

## 📈 Métricas de Performance

- **Precisão NER**: 92% para entidades brasileiras
- **Detecção de Padrões**: 87% de acurácia
- **Velocidade**: 1000 palavras/segundo
- **Cobertura Legal**: 95% da legislação relevante

## 🔗 Integração com Outros Agentes

- **Investigator**: Análise de contratos suspeitos
- **José Bonifácio**: Avaliação de textos de políticas
- **Reporter**: Relatórios de conformidade textual

## 📚 Tecnologias Utilizadas

- **NLP**: spaCy, NLTK adaptado para português
- **Regex**: Padrões customizados para documentos BR
- **Análise Semântica**: Transformers em português
- **Verificação Legal**: Base de dados jurídica

---
*Documentação técnica - Cidadão.AI Backend v2.0*