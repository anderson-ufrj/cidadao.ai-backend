# 📋 Plano de Melhoria Completo - 16 Agentes Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-09 13:30:00 -03:00 (Minas Gerais, Brasil)
**Objetivo**: Finalizar TODOS os 16 agentes para backend 100% funcional
**Status**: Em execução

---

## 🎯 Visão Geral

**Meta**: Completar os 16 agentes do sistema Cidadão.AI, garantindo que todos estejam 100% funcionais, testados e prontos para produção.

**Status Atual**:
- ✅ **5 agentes 100%** (Zumbi, Anita, Senna, Machado, Oxóssi)
- ⚠️ **2 agentes 71-78%** (Tiradentes, Bonifácio)
- ⚠️ **5 agentes 50-70%** (Abaporu, Nanã, Lampião, Maria Quitéria, Niemeyer)
- 🚧 **4 agentes 10-30%** (Dandara, Drummond, Ceuci, Obaluaiê)

**Tempo Total Estimado**: 120-150 horas (3-4 semanas de trabalho full-time)

---

## 📊 Estratégia de Execução

### Abordagem: 3 Fases Incrementais

**FASE 1: COMPLETAR TIER 1** (Semana 1)
- Foco: 2 agentes com problemas (Tiradentes, Bonifácio)
- Meta: 7/7 agentes Tier 1 = 100%
- Tempo: 30-40 horas

**FASE 2: COMPLETAR TIER 2** (Semana 2)
- Foco: 5 agentes substanciais (Abaporu, Nanã, Lampião, Maria Quitéria, Niemeyer)
- Meta: 12/16 agentes = 75%
- Tempo: 50-60 horas

**FASE 3: IMPLEMENTAR TIER 3** (Semana 3-4)
- Foco: 4 agentes planejados (Dandara, Drummond, Ceuci, Obaluaiê)
- Meta: 16/16 agentes = 100%
- Tempo: 40-50 horas

---

## 🔴 FASE 1: COMPLETAR TIER 1 (30-40h)

### Prioridade CRÍTICA

#### 1. Tiradentes (Gerador de Relatórios)
**Status Atual**: 71% implementado
**Arquivo**: `src/agents/tiradentes.py` (1,066 linhas)

**Problemas Identificados**:
- ❌ 9 métodos são placeholders que retornam HTML estático
- ❌ Relatórios de análise (Anita) ficam incompletos
- ✅ Relatórios de investigação (Zumbi) funcionam 100%

**Tarefas**:
1. ✅ Implementar `_create_analysis_executive_summary()` - 2h
2. ✅ Implementar `_create_analysis_overview()` - 2h
3. ✅ Implementar `_create_pattern_sections()` - 3h
4. ✅ Implementar `_create_correlation_section()` - 2h
5. ✅ Implementar `_create_combined_executive_summary()` - 2h
6. ✅ Implementar `_create_combined_conclusions()` - 2h
7. ✅ Implementar `_create_high_priority_anomaly_summary()` - 2h
8. ✅ Implementar `_create_category_anomaly_summary()` - 2h
9. ✅ Implementar `_create_trend_analysis_content()` - 3h
10. ✅ Testar integração completa Anita → Tiradentes - 2h

**Tempo Estimado**: 20-24 horas
**Prioridade**: 🔥 CRÍTICA (bloqueia relatórios de análise)

---

#### 2. José Bonifácio (Políticas Públicas)
**Status Atual**: 78% implementado
**Arquivo**: `src/agents/bonifacio.py` (657 linhas)

**Problemas Identificados**:
- ❌ Usa `asyncio.sleep(3)` para simular processamento
- ❌ Dados simulados com `np.random` em vez de APIs reais
- ❌ 4 frameworks não implementados (apenas `pass`)
- ✅ Algoritmos de cálculo estão corretos

**Tarefas**:
1. ✅ Remover todas as simulações (`asyncio.sleep`) - 1h
2. ✅ Integrar API Portal da Transparência para dados reais - 3h
3. ✅ Integrar API IBGE para indicadores sociais - 2h
4. ✅ Implementar `_apply_logic_model_framework()` - 2h
5. ✅ Implementar `_apply_results_chain_framework()` - 2h
6. ✅ Implementar `_apply_theory_of_change_framework()` - 2h
7. ✅ Implementar `_apply_cost_effectiveness_framework()` - 2h
8. ✅ Testar com dados reais de políticas públicas - 2h

**Tempo Estimado**: 14-18 horas
**Prioridade**: 🔴 ALTA (análise de políticas não é confiável)

---

## 🟡 FASE 2: COMPLETAR TIER 2 (50-60h)

### Prioridade ALTA

#### 3. Abaporu (Master Orquestrador)
**Status Atual**: 70% implementado
**Arquivo**: `src/agents/abaporu.py` (710 linhas)

**Problemas Identificados**:
- ❌ Coordenação multi-agente usa `asyncio.sleep` em vez de chamar agentes reais
- ❌ Reflexão tem placeholders
- ✅ Framework de delegação está bem estruturado

**Tarefas**:
1. ✅ Implementar coordenação real de múltiplos agentes - 4h
2. ✅ Remover `asyncio.sleep`, chamar `agent.process()` real - 2h
3. ✅ Implementar lógica de reflexão real (quality > 0.8) - 3h
4. ✅ Criar workflows complexos (investigação + análise + relatório) - 3h
5. ✅ Testar orquestração end-to-end - 2h

**Tempo Estimado**: 12-16 horas
**Prioridade**: 🟡 ALTA (orquestrador mestre do sistema)

---

#### 4. Nanã (Memória e Aprendizado)
**Status Atual**: 65% implementado
**Arquivo**: `src/agents/nana.py` (685 linhas)

**Problemas Identificados**:
- ❌ Persistência não funciona (PostgreSQL/Redis não integrados)
- ❌ Aprendizado de padrões é stub
- ✅ Estrutura de memória em camadas bem feita

**Tarefas**:
1. ✅ Integrar Supabase para persistência de memória - 4h
2. ✅ Integrar Redis para cache de contexto - 2h
3. ✅ Implementar aprendizado de padrões real - 4h
4. ✅ Criar índices para busca eficiente - 2h
5. ✅ Testar persistência e recuperação - 2h

**Tempo Estimado**: 12-16 horas
**Prioridade**: 🟡 ALTA (memória é crítica para aprendizado)

---

#### 5. Lampião (Análise Regional)
**Status Atual**: 60% implementado
**Arquivo**: `src/agents/lampiao.py` (921 linhas)

**Problemas Identificados**:
- ❌ Análises usam `asyncio.sleep` e dados simulados
- ❌ API do IBGE não integrada (stub)
- ✅ Métricas de desigualdade estão corretas (Gini, Theil)

**Tarefas**:
1. ✅ Integrar API do IBGE (população, PIB, IDH) - 3h
2. ✅ Remover `asyncio.sleep`, implementar análises reais - 4h
3. ✅ Implementar algoritmos de clustering geográfico - 3h
4. ✅ Adicionar análise espacial (distâncias, vizinhanças) - 2h
5. ✅ Testar com dados reais dos 27 estados - 2h

**Tempo Estimado**: 12-16 horas
**Prioridade**: 🟡 MÉDIA (análise regional importante mas não crítica)

---

#### 6. Maria Quitéria (Segurança e Compliance)
**Status Atual**: 55% implementado
**Arquivo**: `src/agents/maria_quiteria.py` (823 linhas)

**Problemas Identificados**:
- ❌ Métodos de detecção têm `# TODO: Implementar`
- ❌ Detecção de intrusão retorna listas vazias
- ✅ Framework de compliance bem estruturado

**Tarefas**:
1. ✅ Implementar detecção de SQL injection - 2h
2. ✅ Implementar detecção de XSS - 2h
3. ✅ Implementar scan de vulnerabilidades - 3h
4. ✅ Implementar detecção de intrusão (patterns suspeitos) - 3h
5. ✅ Criar regras de compliance LGPD/ISO27001 - 2h
6. ✅ Testar com casos reais de ataque - 2h

**Tempo Estimado**: 12-16 horas
**Prioridade**: 🟡 MÉDIA (segurança importante para produção)

---

#### 7. Oscar Niemeyer (Visualização)
**Status Atual**: 50% implementado
**Arquivos**: `niemeyer.py` (416 linhas) + `oscar_niemeyer.py` (648 linhas)

**Problemas Identificados**:
- ❌ Rendering retorna HTML placeholder
- ❌ Integrações D3.js/Plotly não configuradas
- ✅ Tipos de visualização bem definidos

**Tarefas**:
1. ✅ Integrar Plotly para gráficos interativos - 4h
2. ✅ Implementar rendering real de gráficos - 3h
3. ✅ Criar templates D3.js para visualizações avançadas - 3h
4. ✅ Implementar mapas geográficos (Folium/Plotly) - 3h
5. ✅ Criar dashboards interativos - 3h
6. ✅ Testar com dados reais de análises - 2h

**Tempo Estimado**: 16-20 horas
**Prioridade**: 🟡 MÉDIA (visualização importante para frontend)

---

## 🟢 FASE 3: IMPLEMENTAR TIER 3 (40-50h)

### Prioridade BAIXA (Mas necessário para 100%)

#### 8. Dandara (Justiça Social)
**Status Atual**: 30% implementado
**Arquivo**: `src/agents/dandara.py` (385 linhas)

**Problemas Identificados**:
- ❌ Tudo usa `asyncio.sleep` + random
- ✅ Métricas de equidade bem definidas

**Tarefas**:
1. ✅ Implementar análise de distribuição de recursos - 3h
2. ✅ Calcular índices de equidade real (Gini social) - 2h
3. ✅ Analisar acessibilidade a serviços públicos - 3h
4. ✅ Integrar dados do Censo/IBGE - 2h
5. ✅ Testar com dados reais de políticas sociais - 2h

**Tempo Estimado**: 10-14 horas
**Prioridade**: 🟢 BAIXA

---

#### 9. Carlos Drummond (Comunicação)
**Status Atual**: 25% implementado
**Arquivo**: `src/agents/drummond.py` (958 linhas)

**Problemas Identificados**:
- ❌ Integrações (Discord, Slack, Email) são stubs
- ❌ Tradução não funciona
- ✅ Sistema de templates bem estruturado

**Tarefas**:
1. ✅ Integrar API do Discord - 3h
2. ✅ Integrar API do Slack - 3h
3. ✅ Implementar envio de Email (SMTP) - 2h
4. ✅ Integrar serviço de tradução (Google Translate API) - 2h
5. ✅ Criar templates de mensagens - 2h
6. ✅ Testar notificações em todos os canais - 2h

**Tempo Estimado**: 12-16 horas
**Prioridade**: 🟢 BAIXA (comunicação não é core)

---

#### 10. Ceuci (Análise Preditiva)
**Status Atual**: 10% implementado
**Arquivo**: `src/agents/ceuci.py` (595 linhas)

**Problemas Identificados**:
- ❌ TODOS os métodos são TODO
- ❌ Nenhum modelo ML treinado
- ✅ Documentação excelente de algoritmos

**Tarefas**:
1. ✅ Implementar ARIMA para séries temporais - 4h
2. ✅ Implementar LSTM com TensorFlow/PyTorch - 4h
3. ✅ Implementar Prophet (Facebook) - 2h
4. ✅ Treinar modelos com dados históricos - 4h
5. ✅ Implementar validação e backtesting - 2h
6. ✅ Testar previsões com dados reais - 2h

**Tempo Estimado**: 16-20 horas
**Prioridade**: 🟢 BAIXA (preditivo é nice-to-have)

---

#### 11. Obaluaiê (Detecção de Corrupção)
**Status Atual**: 15% implementado
**Arquivo**: `src/agents/obaluaie.py` (236 linhas)

**Problemas Identificados**:
- ❌ Lei de Benford não implementada
- ❌ Análises são stubs
- ✅ Estrutura de alertas bem feita

**Tarefas**:
1. ✅ Implementar Lei de Benford (primeiro dígito) - 3h
2. ✅ Implementar análise de red flags - 2h
3. ✅ Criar scoring de corrupção - 2h
4. ✅ Integrar com Zumbi e Oxóssi - 2h
5. ✅ Testar com casos conhecidos de corrupção - 2h

**Tempo Estimado**: 10-14 horas
**Prioridade**: 🟢 BAIXA (Oxóssi já faz detecção de fraude)

---

## 📊 Resumo Executivo

### Tempo Total por Fase

| Fase | Agentes | Tempo | Prioridade |
|------|---------|-------|------------|
| **FASE 1** | Tiradentes, Bonifácio | 30-40h | 🔥 CRÍTICA |
| **FASE 2** | Abaporu, Nanã, Lampião, Maria, Niemeyer | 50-60h | 🟡 ALTA |
| **FASE 3** | Dandara, Drummond, Ceuci, Obaluaiê | 40-50h | 🟢 BAIXA |
| **TOTAL** | 16 agentes | **120-150h** | 3-4 semanas |

### Ordem de Execução Recomendada

1. **Semana 1**: Tiradentes (20-24h) + Bonifácio (14-18h) = 34-42h
2. **Semana 2**: Abaporu (12-16h) + Nanã (12-16h) + Lampião (12-16h) = 36-48h
3. **Semana 3**: Maria Quitéria (12-16h) + Niemeyer (16-20h) + Dandara (10-14h) = 38-50h
4. **Semana 4**: Drummond (12-16h) + Ceuci (16-20h) + Obaluaiê (10-14h) = 38-50h

### Métricas de Sucesso

**Objetivo**: 16/16 agentes 100% funcionais

**Critérios de "100% funcional"**:
- ✅ Sem `asyncio.sleep` (exceto delays legítimos)
- ✅ Sem dados simulados (`np.random`)
- ✅ Sem métodos vazios (`pass` ou `TODO`)
- ✅ Integração com APIs externas reais
- ✅ Testes unitários com cobertura >70%
- ✅ Documentação completa de capacidades

---

## 🚀 Próximos Passos

### Ação Imediata

**Começar AGORA com Tiradentes** (Prioridade CRÍTICA):
1. Abrir `src/agents/tiradentes.py`
2. Implementar os 9 métodos placeholder
3. Testar integração com Anita
4. Tempo: 20-24 horas

### Após Tiradentes

**Continuar com Bonifácio**:
1. Remover simulações
2. Integrar APIs reais (Portal Transparência + IBGE)
3. Implementar 4 frameworks
4. Tempo: 14-18 horas

### Acompanhamento

**Criar arquivo de tracking**:
- `docs/project/PROGRESS_AGENTES.md`
- Atualizar diariamente com progresso
- Marcar tarefas concluídas

---

## 📝 Notas Importantes

### Dependências Externas

**APIs que precisam de integração**:
- ✅ Portal da Transparência (já configurado)
- ⚠️ IBGE API (precisa configurar)
- ⚠️ Dados.gov.br (já configurado parcialmente)
- ⚠️ Google Translate API (precisa chave)
- ⚠️ Discord/Slack (precisa webhooks)

### Bibliotecas Adicionais

**Podem ser necessárias**:
```bash
pip install prophet          # Ceuci - previsões
pip install tensorflow       # Ceuci - LSTM
pip install plotly          # Niemeyer - visualizações
pip install folium          # Niemeyer - mapas
pip install discord.py      # Drummond - notificações
pip install slack-sdk       # Drummond - notificações
```

---

## 🎯 Meta Final

**16/16 agentes 100% funcionais**
- Tier 1: 7/7 ✅
- Tier 2: 5/5 ✅
- Tier 3: 4/4 ✅

**Cobertura de testes: >70%**

**Backend pronto para integração com frontend!**

---

**Data de Início**: 09/10/2025
**Data Estimada de Conclusão**: 06/11/2025 (4 semanas)
**Responsável**: Anderson Henrique da Silva

---

*Este plano é vivo e será atualizado conforme progresso* 🚀
