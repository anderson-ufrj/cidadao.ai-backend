# 📊 Importar Dashboards no Grafana Cloud - Guia Rápido

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data**: 2025-10-30
**Tempo estimado**: 10 minutos

---

## 🎯 Objetivo

Importar os 6 dashboards prontos do Cidadão.AI para o Grafana Cloud e começar a monitorar a produção.

---

## 📋 Pré-requisitos

- ✅ Railway com variáveis Grafana Cloud configuradas
- ✅ Deploy concluído no Railway
- ✅ Conta Grafana Cloud criada

---

## 🚀 Passo a Passo

### 1️⃣ Login no Grafana Cloud

1. Acesse: https://grafana.com/
2. Clique em **"Sign in"**
3. Login com suas credenciais
4. Você será redirecionado para o dashboard

---

### 2️⃣ Acessar Seção de Dashboards

1. No menu lateral esquerdo, clique em **"Dashboards"** (ícone de 4 quadrados)
2. Clique no botão **"New"** (canto superior direito)
3. Selecione **"Import"**

---

### 3️⃣ Importar Dashboard 1 - Production Overview

1. Na tela de Import:
   - Clique em **"Upload JSON file"**
   - Navegue até: `monitoring/grafana/dashboards/1-production-overview.json`
   - Selecione o arquivo

2. Configure o dashboard:
   - **Name**: Mantenha "Cidadão.AI - Production Overview" (ou customize)
   - **Folder**: Selecione "General" ou crie uma pasta "Cidadão.AI"
   - **Data source**: Selecione seu Prometheus (deve aparecer automaticamente)
     - Nome padrão: `grafanacloud-xxxxx-prom`

3. Clique em **"Import"**

4. ✅ Dashboard importado! Você verá os painéis aparecendo.

---

### 4️⃣ Importar Dashboard 2 - Agents Performance

Repita o processo do passo 3 com:
- Arquivo: `monitoring/grafana/dashboards/2-agents-performance.json`
- Nome: "Cidadão.AI - Agents Performance"

---

### 5️⃣ Importar Dashboard 3 - Investigations

Repita o processo com:
- Arquivo: `monitoring/grafana/dashboards/3-investigations.json`
- Nome: "Cidadão.AI - Investigations"

---

### 6️⃣ Importar Dashboard 4 - Anomaly Detection

Repita o processo com:
- Arquivo: `monitoring/grafana/dashboards/4-anomaly-detection.json`
- Nome: "Cidadão.AI - Anomaly Detection"

---

### 7️⃣ Importar Dashboard 5 - API Performance

Repita o processo com:
- Arquivo: `monitoring/grafana/dashboards/5-api-performance.json`
- Nome: "Cidadão.AI - API Performance"

---

### 8️⃣ Importar Dashboard 6 - Infrastructure

Repita o processo com:
- Arquivo: `monitoring/grafana/dashboards/6-infrastructure.json`
- Nome: "Cidadão.AI - Infrastructure"

---

## ✅ Verificar Dashboards

### Checar se Dados Estão Chegando

1. Abra qualquer dashboard importado
2. No canto superior direito, ajuste o **Time range** para "Last 5 minutes"
3. Clique em **"Refresh"** (ícone de seta circular)

**Você deve ver**:
- Gráficos com dados (não vazios)
- Métricas como "Uptime", "Requests/s", etc.
- Se não aparecer dados: aguarde 1-2 minutos (primeiro push leva um tempo)

---

## 🔍 Teste Rápido

### Query Manual no Grafana Explore

1. No menu lateral, clique em **"Explore"** (ícone de bússola)
2. Certifique-se que o data source é o Prometheus
3. Digite a query:
   ```promql
   up{job="cidadao-ai-backend"}
   ```
4. Clique em **"Run query"**

**Resultado esperado**:
- Valor: `1` (sistema online)
- Timestamp recente (últimos 60 segundos)

Se aparecer `1`, significa que:
- ✅ Backend está enviando métricas
- ✅ Grafana Cloud está recebendo
- ✅ Tudo funcionando!

---

## 📊 Dashboards Disponíveis

### 1. Production Overview (Principal)
**O que mostra**:
- Uptime e disponibilidade
- Requests por segundo
- Error rate (4xx, 5xx)
- Latência (p50, p95, p99)
- Status geral do sistema

**Quando usar**: Visão rápida diária do sistema

---

### 2. Agents Performance
**O que mostra**:
- Tasks executadas por agente
- Duração média de cada agente
- Taxa de sucesso/erro por agente
- Agentes mais utilizados

**Quando usar**: Investigar performance de agentes específicos

---

### 3. Investigations
**O que mostra**:
- Total de investigações
- Investigações por status (pending, running, completed, failed)
- Taxa de conclusão
- Tempo médio de investigação

**Quando usar**: Monitorar fluxo de investigações

---

### 4. Anomaly Detection
**O que mostra**:
- Anomalias detectadas por tipo
- Severidade das anomalias
- Taxa de detecção
- Anomalias por fonte de dados

**Quando usar**: Alertas de fraude e irregularidades

---

### 5. API Performance
**O que mostra**:
- Response time por endpoint
- Throughput (requests/s)
- Error rate por endpoint
- Endpoints mais lentos

**Quando usar**: Otimizar performance da API

---

### 6. Infrastructure
**O que mostra**:
- CPU e memória
- Database connections
- Redis cache hit rate
- Network I/O

**Quando usar**: Troubleshooting de problemas de infraestrutura

---

## 🔔 Configurar Alertas (Opcional)

### Criar Alerta de Sistema Offline

1. No menu lateral, vá em **"Alerting"** → **"Alert rules"**
2. Clique em **"New alert rule"**
3. Configure:
   - **Name**: "Backend Down"
   - **Query**:
     ```promql
     up{job="cidadao-ai-backend"} == 0
     ```
   - **Condition**: IS BELOW 1
   - **For**: 2m (2 minutos)
   - **Severity**: Critical

4. Em **"Contact points"**, selecione seu email ou Discord/Slack
5. Salve o alerta

---

## 📱 Mobile App (Opcional)

1. Baixe o app **Grafana** (iOS/Android)
2. Login com suas credenciais
3. Acesse seus dashboards no celular
4. Receba notificações push de alertas

---

## 🎯 Próximas Ações Recomendadas

Após importar dashboards:

1. **Star** seus dashboards favoritos (⭐ no canto superior)
2. Configurar alertas críticos (sistema down, error rate alto)
3. Criar uma **playlist** com dashboards principais para TV/monitor
4. Compartilhar dashboards com equipe (Settings → Sharing)

---

## 💡 Dicas

### Atalhos de Teclado
- `d + k`: Ir para dashboard
- `d + h`: Ir para home
- `e`: Explore
- `?`: Mostrar todos atalhos

### Customização
- Clique em qualquer painel → "Edit" para customizar
- Adicione suas próprias queries PromQL
- Ajuste thresholds de alertas conforme necessário

### Performance
- Use time range adequado (não carregar dados de 30 dias)
- "Last 6 hours" é bom para monitoramento diário
- "Last 30 days" apenas quando necessário

---

## 🐛 Troubleshooting

### Dashboard vazio (sem dados)

**Possíveis causas**:
1. Aguardar 1-2 minutos após deploy
2. Verificar se `GRAFANA_CLOUD_ENABLED=true` no Railway
3. Checar logs no Railway: `railway logs | grep -i grafana`
4. Verificar time range (últimos 5 minutos)

### "No data" em alguns painéis

**Normal**: Alguns painéis só terão dados após atividade:
- Investigations: Só após criar investigações
- Anomalies: Só após detectar anomalias
- Alguns agentes: Só após serem usados

### Data source não encontrado

1. Vá em **Connections** → **Data sources**
2. Verifique se Prometheus está "Working"
3. Se não, clique em "Test" e veja o erro

---

## 📚 Recursos Adicionais

- **Grafana Docs**: https://grafana.com/docs/grafana/latest/
- **PromQL Cheat Sheet**: https://promlabs.com/promql-cheat-sheet/
- **Dashboard Best Practices**: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/

---

## ✅ Checklist de Importação

- [ ] Login no Grafana Cloud
- [ ] Importar Dashboard 1 - Production Overview
- [ ] Importar Dashboard 2 - Agents Performance
- [ ] Importar Dashboard 3 - Investigations
- [ ] Importar Dashboard 4 - Anomaly Detection
- [ ] Importar Dashboard 5 - API Performance
- [ ] Importar Dashboard 6 - Infrastructure
- [ ] Verificar dados aparecendo (últimos 5min)
- [ ] Testar query manual: `up{job="cidadao-ai-backend"}`
- [ ] Criar alerta de sistema offline (opcional)
- [ ] Star dashboards favoritos

---

**Parabéns!** 🎉 Seu monitoramento profissional está configurado!

**Próximo passo**: Acompanhe os dashboards diariamente para identificar problemas antes que afetem usuários.

---

**Guia criado**: 2025-10-30
**Autor**: Anderson Henrique da Silva, Minas Gerais, Brasil
