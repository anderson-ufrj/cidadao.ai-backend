# ROADMAP - DEZEMBRO 2025

**Data de Criação:** 02 de Dezembro de 2025
**Autor:** Anderson Henrique da Silva
**Baseado em:** Resultados do teste de produção com 100 cenários (01/12/2025)

---

## Sumário Executivo

Este roadmap foi criado com base nos resultados do teste de produção realizado em 01/12/2025, que avaliou 100 cenários de chat diferentes. O sistema apresentou **99% de taxa de sucesso**, mas identificamos oportunidades críticas de melhoria.

### Métricas Atuais (Baseline)

| Métrica | Valor Atual | Meta |
|---------|-------------|------|
| Taxa de Sucesso | 99% | 99.5% |
| Tempo Médio de Resposta | 3.71s | < 2.5s |
| Tempo Máximo | 16.49s | < 8s |
| Intent Classification | 13% correto | > 80% |
| Diversidade de Agentes | 1 (Abaporu) | 5+ |

---

## FASE 1: INTENT CLASSIFICATION (Prioridade CRÍTICA)

**Problema Identificado:** 87% das mensagens são classificadas como "unknown"

**Impacto:** Usuários não recebem respostas especializadas dos agentes corretos

### Sprint 1.1 - Melhoria do Classificador de Intent (3-5 dias)

#### Tarefas:

- [ ] **1.1.1** Auditar `src/services/chat_service.py` - padrões regex atuais
- [ ] **1.1.2** Expandir keywords para cada IntentType:
  - `GREETING`: adicionar variações regionais (opa, e aí, fala)
  - `HELP_REQUEST`: adicionar "como usar", "não entendo", "tutorial"
  - `INVESTIGATE`: adicionar "buscar", "procurar", "encontrar", "mostrar"
  - `ANALYZE`: adicionar "analisar", "comparar", "verificar"
  - `ABOUT_SYSTEM`: adicionar "quem fez", "criador", "autor"
- [ ] **1.1.3** Implementar fallback inteligente baseado em embeddings
- [ ] **1.1.4** Adicionar logging de intents para análise contínua
- [ ] **1.1.5** Criar testes unitários para cada intent type

#### Arquivos a Modificar:
```
src/services/chat_service.py
src/services/orchestration/query_planner/intent_classifier.py
tests/unit/services/test_intent_classifier.py (novo)
```

#### Critérios de Sucesso:
- Intent "unknown" reduzido para < 20%
- Cada categoria de teste com intent correto > 80%

---

## FASE 2: PERFORMANCE OPTIMIZATION (Prioridade ALTA)

**Problema Identificado:**
- Greeting: 7.63s médio (alguns até 13s!)
- Complex: 5.38s médio (pico de 16.49s)

**Impacto:** UX degradada, usuários podem abandonar antes da resposta

### Sprint 2.1 - Otimização de Greeting (2-3 dias)

#### Análise do Problema:
```
Tempos de greeting observados:
- Rápidos: 1.93s, 1.98s, 1.99s, 2.89s
- LENTOS: 11.82s, 12.47s, 13.07s, 13.22s
```

A discrepância sugere que algumas saudações estão passando por processamento desnecessário (provavelmente chamando LLM quando não deveria).

#### Tarefas:

- [ ] **2.1.1** Implementar resposta instantânea para greetings simples (sem LLM)
- [ ] **2.1.2** Criar cache de respostas para saudações comuns
- [ ] **2.1.3** Adicionar short-circuit no router para intents triviais
- [ ] **2.1.4** Medir e documentar melhoria

#### Código Sugerido:
```python
# Em src/api/routes/chat.py
INSTANT_RESPONSES = {
    "greeting": [
        "Olá! Sou o Cidadão.AI. Como posso ajudá-lo?",
        "Oi! Pronto para investigar a transparência pública?",
        "Bom dia! Em que posso ajudar hoje?",
    ]
}

# Se intent == GREETING e confidence > 0.9, responder instantaneamente
```

#### Critérios de Sucesso:
- Tempo médio de greeting < 1s
- Nenhum greeting > 3s

### Sprint 2.2 - Otimização de Queries Complexas (3-4 dias)

#### Tarefas:

- [ ] **2.2.1** Implementar streaming de pensamento (mostrar progresso)
- [ ] **2.2.2** Paralelizar chamadas de API quando possível
- [ ] **2.2.3** Adicionar timeout com fallback graceful
- [ ] **2.2.4** Implementar cache de resultados de queries comuns

#### Critérios de Sucesso:
- Tempo médio de complex < 4s
- Tempo máximo < 10s

---

## FASE 3: AGENT ROUTING DIVERSIFICATION (Prioridade MÉDIA)

**Problema Identificado:** 99% das requisições vão para Abaporu

**Impacto:** Agentes especializados não estão sendo utilizados

### Sprint 3.1 - Router de Agentes Inteligente (4-5 dias)

#### Tarefas:

- [ ] **3.1.1** Auditar `src/services/agent_routing.py`
- [ ] **3.1.2** Criar mapeamento intent → agente especializado:
  ```python
  AGENT_ROUTING = {
      "investigate": "zumbi",      # Investigador
      "analyze": "anita",          # Analista
      "report": "tiradentes",      # Relator
      "question": "drummond",      # Comunicador
      "legal": "bonifacio",        # Jurista
      "anomaly": "obaluaie",       # Detector de Corrupção
      "search": "oxossi",          # Caçador de Dados
      "regional": "lampiao",       # Especialista Regional
      "security": "maria_quiteria", # Segurança
  }
  ```
- [ ] **3.1.3** Implementar fallback para Abaporu (orquestrador) apenas quando necessário
- [ ] **3.1.4** Adicionar logging de qual agente foi selecionado
- [ ] **3.1.5** Criar dashboard de uso de agentes

#### Critérios de Sucesso:
- Pelo menos 5 agentes diferentes sendo usados
- Abaporu usado em < 50% dos casos

---

## FASE 4: EDGE CASES & ROBUSTNESS (Prioridade MÉDIA)

**Status Atual:** 9/10 edge cases passaram (90%)

### Sprint 4.1 - Tratamento de Edge Cases (2 dias)

#### Tarefas:

- [ ] **4.1.1** Melhorar validação de mensagem vazia
- [ ] **4.1.2** Tratar mensagens muito curtas (< 3 chars)
- [ ] **4.1.3** Sanitizar emojis e caracteres especiais
- [ ] **4.1.4** Implementar rate limiting por sessão
- [ ] **4.1.5** Adicionar proteção contra SQL injection nos logs

#### Critérios de Sucesso:
- 100% dos edge cases tratados graciosamente
- Nenhum erro 500 em produção

---

## FASE 5: OBSERVABILITY & MONITORING (Prioridade BAIXA)

### Sprint 5.1 - Dashboard de Métricas (3 dias)

#### Tarefas:

- [ ] **5.1.1** Implementar métricas Prometheus para:
  - Tempo de resposta por categoria
  - Intent detection accuracy
  - Uso de agentes
  - Taxa de erro por tipo
- [ ] **5.1.2** Criar dashboard Grafana
- [ ] **5.1.3** Configurar alertas para:
  - Tempo de resposta > 10s
  - Taxa de erro > 5%
  - Intent unknown > 50%

---

## Cronograma Sugerido

```
DEZEMBRO 2025
═══════════════════════════════════════════════════════════════

Semana 1 (02-08 Dez)
├── Sprint 1.1: Intent Classification
└── Sprint 2.1: Greeting Optimization

Semana 2 (09-15 Dez)
├── Sprint 2.2: Complex Query Optimization
└── Sprint 3.1: Agent Routing (início)

Semana 3 (16-22 Dez)
├── Sprint 3.1: Agent Routing (conclusão)
└── Sprint 4.1: Edge Cases

Semana 4 (23-31 Dez)
├── Sprint 5.1: Observability
├── Testes de Regressão
└── Deploy Final 2025
```

---

## Métricas de Acompanhamento

### Teste Semanal Obrigatório

Executar semanalmente:
```bash
python tests/e2e/test_chat_production.py --save
```

### KPIs a Monitorar

| KPI | Baseline | Semana 1 | Semana 2 | Semana 3 | Semana 4 |
|-----|----------|----------|----------|----------|----------|
| Success Rate | 99% | | | | |
| Avg Response Time | 3.71s | | | | |
| Max Response Time | 16.49s | | | | |
| Unknown Intent % | 87% | | | | |
| Agent Diversity | 1 | | | | |
| Greeting Avg Time | 7.63s | | | | |

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Regressão de performance | Média | Alto | Testes automatizados antes de cada deploy |
| Breaking changes no router | Baixa | Alto | Feature flags para rollback rápido |
| Sobrecarga do LLM | Média | Médio | Cache agressivo + respostas instantâneas |

---

## Definição de Pronto (DoD)

Uma tarefa só está completa quando:

1. Código implementado e testado
2. Testes unitários passando
3. Teste de produção (100 cenários) executado
4. Métricas comparadas com baseline
5. Documentação atualizada
6. Code review aprovado
7. Deploy em produção realizado

---

## Próximos Passos Imediatos

1. **HOJE (02/12):** Iniciar Sprint 1.1 - Auditar classificador de intent
2. **AMANHÃ (03/12):** Expandir keywords de intent
3. **04/12:** Implementar e testar novas classificações
4. **05/12:** Deploy e validação com teste de 100 cenários

---

## Referências

- Relatório de Teste: `docs/reports/chat_test_report_20251201_211132.json`
- Script de Teste: `tests/e2e/test_chat_production.py`
- Roadmap Anterior: `docs/project/ROADMAP_OFFICIAL_2025.md`

---

**Última Atualização:** 02 de Dezembro de 2025
**Próxima Revisão:** 09 de Dezembro de 2025
