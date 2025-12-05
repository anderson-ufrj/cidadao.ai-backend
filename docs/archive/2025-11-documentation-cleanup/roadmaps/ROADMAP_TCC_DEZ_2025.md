# Cidadão.AI - Roadmap TCC (Entrega Dezembro 2025)

**Status**: ✅ VALIDADO
**Data de Criação**: 14 de Novembro de 2025
**Autor**: Anderson Henrique da Silva
**Natureza**: Trabalho de Conclusão de Curso (TCC) - Versão Beta 1.0
**Prazo de Entrega**: **Dezembro 2025** (6 semanas)

---

## 🎯 Objetivo do TCC

Desenvolver e validar um **sistema multi-agente baseado em IA** para detecção automatizada de anomalias em contratos públicos brasileiros, demonstrando viabilidade técnica e científica da solução.

---

## ⏰ Cronograma Sprint (6 semanas)

### SEMANA 1-2: Estabilização & Documentação Base
**Período**: 14-28 Nov 2025
**Status**: 🟡 Em andamento

#### Tarefas Técnicas
- [x] ✅ Validar roadmap e planejar sprint
- [x] ✅ Documentar sistema atual (STATUS_ATUAL_2025_11_14.md)
- [x] ✅ Documentar streaming (STREAMING_IMPLEMENTATION.md)
- [ ] 🔄 Aumentar test coverage para 80% (atual: 76.29%)
- [ ] 🔄 Resolver 44 TODOs/FIXMEs identificados
- [ ] 🔄 Otimizar imports de agentes (já 367x mais rápido)

#### Documentação TCC
- [ ] Escrever Introdução (contexto, problema, objetivos)
- [ ] Escrever Fundamentação Teórica (multi-agent, ML, transparência)
- [ ] Revisar trabalhos relacionados (benchmark com sistemas similares)

**Entregas**:
- Capítulos 1, 2, 3 da monografia (rascunho)
- Test coverage >80%
- Código limpo (zero TODOs críticos)

---

### SEMANA 3-4: Validação Experimental & Resultados
**Período**: 29 Nov - 12 Dez 2025
**Status**: ⏳ Planejado

#### Experimentos
- [ ] **Dataset**: Coletar 1.000+ contratos reais via APIs
- [ ] **Testes de Anomalia**: Validar detecção com casos conhecidos
- [ ] **Performance**: Benchmarks de latência e throughput
- [ ] **Multi-Agent**: Testes de coordenação entre agentes
- [ ] **Métricas**: Precision, Recall, F1-score da detecção

#### Análise
- [ ] Análise estatística dos resultados
- [ ] Casos de uso documentados (mínimo 5)
- [ ] Comparação com baseline (detecção manual)
- [ ] Identificar limitações e melhorias

#### Documentação TCC
- [ ] Escrever Metodologia (arquitetura, algoritmos)
- [ ] Escrever Implementação (tecnologias, deployment)
- [ ] Escrever Resultados Experimentais (datasets, métricas)

**Entregas**:
- Capítulos 4, 5, 6 da monografia (rascunho)
- Relatório de experimentos
- 5+ casos de uso validados

---

### SEMANA 5-6: Finalização & Entrega
**Período**: 13-20 Dez 2025
**Status**: ⏳ Planejado

#### Finalização da Monografia
- [ ] Escrever Conclusões e Trabalhos Futuros
- [ ] Revisar todos os capítulos
- [ ] Revisão ortográfica e formatação ABNT
- [ ] Gerar sumário, lista de figuras, referências
- [ ] Preparar apresentação (slides)

#### Código Final
- [ ] Code review completo
- [ ] Documentação README atualizada
- [ ] Guia de instalação e deployment
- [ ] Comentários em código complexo
- [ ] Licença open-source (MIT)

#### Entrega
- [ ] Monografia PDF final
- [ ] Código fonte no GitHub
- [ ] Apresentação PowerPoint/PDF
- [ ] Demo ao vivo preparada
- [ ] Vídeo demonstração (5-10 min)

**Data de Entrega**: **20 de Dezembro de 2025**

---

## 📊 Sistema Atual (Baseline)

### Infraestrutura ✅
- **Produção**: Railway (99.9% uptime)
- **Database**: PostgreSQL + Redis cache
- **Monitoring**: Grafana + Prometheus
- **API**: FastAPI com documentação OpenAPI

### Agentes (17 total) ✅
- **Tier 1** (10 agentes): Totalmente operacionais, >75% coverage
- **Tier 2** (5 agentes): 85-95% funcionais
- **Tier 3** (1 agente): Framework completo
- **Base**: ReflectiveAgent (96.45% coverage)

### Performance Atual ✅
- Latência p50: 80ms
- Latência p95: 145ms
- Throughput: 1.000 req/s
- Agent import: 3.81ms (367x otimização)
- Test coverage: 76.29%

### Funcionalidades ✅
- ✅ Streaming SSE + WebSocket
- ✅ Multi-agent orchestration
- ✅ 30+ APIs governamentais integradas
- ✅ Cache multi-camadas
- ✅ Circuit breakers
- ✅ Detecção de anomalias (FFT spectral)

---

## 🎓 Estrutura da Monografia TCC

### Capítulos (70-100 páginas)

**1. Introdução** (8-10 páginas)
- Contexto: Transparência pública no Brasil
- Problema: Volume de contratos vs. capacidade de auditoria
- Objetivos: Sistema multi-agente para detecção automatizada
- Contribuições: Arquitetura, algoritmos, validação
- Organização do trabalho

**2. Fundamentação Teórica** (15-20 páginas)
- Multi-Agent Systems
  - Definições e conceitos
  - Arquiteturas de agentes
  - Comunicação e coordenação
- Machine Learning
  - Detecção de anomalias
  - FFT spectral analysis
  - Métricas de avaliação
- Transparência Pública
  - Legislação brasileira (LAI)
  - Portal da Transparência
  - APIs governamentais

**3. Trabalhos Relacionados** (10-12 páginas)
- Sistemas de transparência existentes
  - Portal da Transparência
  - Controladoria-Geral da União
  - TCU (Tribunal de Contas da União)
- IA aplicada a detecção de fraudes
  - Fraud detection systems
  - Anomaly detection em contratos
- Multi-agent systems
  - Aplicações comerciais
  - Sistemas acadêmicos
- Análise comparativa
  - Tabela de features
  - Diferenciais do Cidadão.AI

**4. Metodologia** (12-15 páginas)
- Arquitetura do Sistema
  - Diagrama geral
  - FastAPI + PostgreSQL + Redis
  - 17 agentes especializados
- Agentes Implementados
  - ReflectiveAgent (base framework)
  - Zumbi (investigador)
  - Anita (analista)
  - Ayrton Senna (orchestrador)
  - Outros 13 agentes
- Algoritmos
  - FFT spectral analysis
  - Detecção de outliers
  - Graph analytics (NetworkX)
- Integrações
  - 30+ APIs governamentais
  - Portal da Transparência
  - PNCP, IBGE, DataSUS, INEP

**5. Implementação** (12-15 páginas)
- Tecnologias Utilizadas
  - Python 3.11, FastAPI, SQLAlchemy
  - PostgreSQL, Redis
  - Maritaca AI (LLM)
  - Docker, Railway (deployment)
- Arquitetura Multi-Agente
  - ReflectiveAgent pattern
  - Agent pool e lazy loading
  - Message passing e coordenação
- Streaming e Real-time
  - Server-Sent Events (SSE)
  - WebSocket bidirectional
  - Compression middleware
- Deployment
  - Railway production
  - CI/CD pipeline
  - Monitoring (Grafana/Prometheus)

**6. Resultados Experimentais** (15-20 páginas)
- Dataset
  - Fonte: Portal da Transparência, PNCP
  - Tamanho: 1.000+ contratos
  - Período: 2023-2025
- Experimentos
  - Performance (latência, throughput)
  - Detecção de anomalias (P, R, F1)
  - Multi-agent coordination
  - Escalabilidade
- Casos de Uso
  - Caso 1: Superfaturamento em saúde
  - Caso 2: Cartel em licitações
  - Caso 3: Empresa laranja
  - Caso 4: Direcionamento de edital
  - Caso 5: Fracionamento irregular
- Análise de Resultados
  - Gráficos e tabelas
  - Comparação com baseline
  - Discussão de limitações

**7. Conclusões** (5-8 páginas)
- Resumo das Contribuições
  - Técnicas: Arquitetura multi-agente
  - Científicas: Validação experimental
  - Sociais: Ferramenta de transparência
- Limitações
  - Qualidade dos dados governamentais
  - APIs com restrições (78% bloqueadas)
  - Necessidade de validação humana
- Trabalhos Futuros
  - ML preditivo (FASE 2 do roadmap)
  - Graph analytics com Neo4j
  - NLP para análise de cláusulas
  - Expansão para outros estados
  - Mobile app (PWA)
- Considerações Finais

**Elementos Pós-Textuais**
- Referências Bibliográficas (ABNT)
- Apêndice A: Manual de Instalação
- Apêndice B: Documentação de APIs
- Apêndice C: Códigos Principais

---

## 📈 Métricas de Sucesso (TCC)

### Requisitos Mínimos
- [x] ✅ Sistema em produção (Railway, 99.9% uptime)
- [ ] Test coverage ≥80% (atual: 76.29%)
- [ ] Monografia 70-100 páginas
- [ ] 5+ casos de uso validados
- [ ] Apresentação 20-30 min
- [ ] Demo ao vivo funcional

### Requisitos Desejáveis
- [ ] Test coverage >85%
- [ ] Detecção de anomalias: Precision >85%, Recall >80%
- [ ] Performance: p95 <100ms
- [ ] 1.000+ contratos analisados
- [ ] Artigo científico submetido (bonus)

---

## 🎬 Apresentação Final (20-30 min)

### Estrutura da Defesa

**1. Introdução** (3 min)
- Apresentação pessoal
- Contextualização do problema
- Objetivos do TCC

**2. Fundamentação** (4 min)
- Multi-agent systems
- Detecção de anomalias
- Transparência pública

**3. Sistema Desenvolvido** (8 min)
- Arquitetura geral (diagrama)
- 17 agentes implementados
- Tecnologias utilizadas
- **DEMO AO VIVO** (5 min)
  - Buscar contrato suspeito
  - Sistema detecta anomalias
  - Agentes investigam e reportam
  - Mostrar streaming real-time

**4. Resultados** (8 min)
- Métricas de performance
- Casos de uso validados
- Comparação com baseline
- Limitações identificadas

**5. Conclusões** (3 min)
- Contribuições
- Trabalhos futuros
- Impacto social esperado

**6. Perguntas** (5-10 min)

---

## 📚 Referências Essenciais

### Multi-Agent Systems
1. Wooldridge, M. (2009). *An Introduction to MultiAgent Systems*. Wiley.
2. Ferber, J. (1999). *Multi-Agent Systems: An Introduction to Distributed AI*. Addison-Wesley.
3. Russell, S., Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.).

### Machine Learning
4. Géron, A. (2019). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*.
5. Goodfellow, I. et al. (2016). *Deep Learning*. MIT Press.
6. Chandola, V. et al. (2009). "Anomaly detection: A survey". *ACM Computing Surveys*.

### Transparência e Corrupção
7. Rose-Ackerman, S. (1999). *Corruption and Government*. Cambridge University Press.
8. Transparência Internacional (2024). *Corruption Perceptions Index*.
9. Brasil. Lei nº 12.527/2011 - Lei de Acesso à Informação.

### Artigos Técnicos
10. Portal da Transparência (2024). Documentação de APIs.
11. PNCP (2024). Portal Nacional de Contratações Públicas.
12. FastAPI (2024). Official Documentation.

---

## 📅 Checklist Final

### Semana 1-2 (14-28 Nov)
- [ ] Test coverage >80%
- [ ] Capítulos 1, 2, 3 (rascunho)
- [ ] Resolver TODOs críticos

### Semana 3-4 (29 Nov - 12 Dez)
- [ ] 1.000+ contratos analisados
- [ ] 5+ casos de uso validados
- [ ] Capítulos 4, 5, 6 (rascunho)

### Semana 5-6 (13-20 Dez)
- [ ] Monografia completa e revisada
- [ ] Apresentação pronta
- [ ] Demo testada e funcional
- [ ] Código documentado
- [ ] Entrega final (20/Dez)

---

## 🚀 Próximos Passos Imediatos

### Hoje (14/Nov)
- [x] ✅ Roadmap TCC validado
- [ ] Começar Introdução da monografia
- [ ] Listar referências bibliográficas

### Esta Semana
- [ ] Resolver 10 TODOs prioritários
- [ ] Adicionar testes (coverage 76% → 80%)
- [ ] Escrever Capítulo 1 completo

### Próxima Semana
- [ ] Escrever Capítulos 2 e 3
- [ ] Preparar dataset de experimentos
- [ ] Validar 2 primeiros casos de uso

---

## 📞 Contato

**Autor**: Anderson Henrique da Silva
**Email**: anderson@cidadao.ai
**GitHub**: github.com/anderson-ufrj/cidadao.ai-backend
**Produção**: https://cidadao-api-production.up.railway.app

---

**Criado**: 14 de Novembro de 2025
**Entrega**: 20 de Dezembro de 2025
**Tempo Restante**: 36 dias / 6 semanas
