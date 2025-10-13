# 🗄️ Supabase Setup Guide - Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

Este guia explica como configurar o Supabase para armazenar investigações e anomalias do sistema 24/7.

## 📋 Pré-requisitos

1. Conta no [Supabase](https://supabase.com)
2. Projeto criado no Supabase
3. Variáveis de ambiente configuradas no Railway

## 🚀 Passo 1: Criar as Tabelas

### 1.1. Acesse o SQL Editor do Supabase

1. Entre no seu projeto Supabase
2. Vá em **SQL Editor** no menu lateral
3. Clique em **New Query**

### 1.2. Execute o Schema SQL

Copie e cole o conteúdo completo do arquivo `supabase_schema.sql` e execute.

Este script irá criar:
- ✅ **investigations** - Registros de investigações
- ✅ **anomalies** - Anomalias detectadas
- ✅ **audit_logs** - Logs de auditoria
- ✅ **alerts** - Alertas de anomalias
- ✅ **katana_dispensas** - Cache de dispensas do Katana
- ✅ **Views** - Visualizações agregadas
- ✅ **Triggers** - Atualização automática de timestamps

## 🔑 Passo 2: Obter as Credenciais

### 2.1. URL do Projeto

1. Vá em **Project Settings** → **API**
2. Copie a **URL** (ex: `https://xxxxx.supabase.co`)

### 2.2. Service Role Key

1. Na mesma página de API Settings
2. Role até **Project API keys**
3. Copie a **service_role** key (⚠️ **NUNCA** compartilhe esta chave!)

## ⚙️ Passo 3: Configurar Railway

### 3.1. Adicionar Variáveis de Ambiente

No Railway, adicione estas variáveis em **TODOS os serviços** (api, worker, beat):

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...sua-chave-aqui
```

### 3.2. Verificar Configuração Atual

As variáveis já devem estar parcialmente configuradas. Verifique se estão corretas:

```bash
# No Railway Dashboard:
# Variables → Shared Variables (se usar) ou em cada serviço
```

## 🧪 Passo 4: Testar a Integração

### 4.1. Teste Manual via API

Após o deploy, teste o endpoint de monitoramento Katana:

```bash
# Obtenha um token de autenticação primeiro
POST https://seu-app.railway.app/auth/login
{
  "username": "seu-usuario",
  "password": "sua-senha"
}

# Dispare o monitoramento Katana
POST https://seu-app.railway.app/tasks/trigger/katana-monitor
Authorization: Bearer {seu-token}
```

### 4.2. Verificar no Supabase

1. Vá em **Table Editor** no Supabase
2. Verifique se os dados aparecem em:
   - `investigations`
   - `anomalies`
   - `katana_dispensas`

## 📊 Passo 5: Visualizar Dados

### 5.1. Usar as Views Criadas

O schema criou views úteis para análise:

```sql
-- Anomalias de alta severidade
SELECT * FROM high_severity_anomalies LIMIT 10;

-- Estatísticas por fonte
SELECT * FROM anomaly_stats_by_source;

-- Resumo de investigações
SELECT * FROM investigation_summary LIMIT 10;
```

### 5.2. Dashboard Customizado (Opcional)

Você pode criar um dashboard customizado no Supabase ou usar ferramentas como:
- Metabase
- Grafana
- Tableau
- Power BI

## 🔐 Segurança

### Row Level Security (RLS)

O Supabase possui RLS desabilitado por padrão para service_role. Se quiser adicionar segurança extra:

```sql
-- Habilitar RLS para a tabela anomalies
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;

-- Política de exemplo: apenas service_role pode inserir
CREATE POLICY "Service role can insert"
  ON anomalies FOR INSERT
  TO service_role
  USING (true);
```

## 🚨 Troubleshooting

### Erro: "Invalid API key"

- Verifique se copiou a `service_role` key (não a `anon` key)
- Certifique-se que não há espaços em branco na variável

### Erro: "relation does not exist"

- Execute o script `supabase_schema.sql` completo
- Verifique se está no schema público: `SET search_path TO public;`

### Dados não aparecem

- Verifique os logs do Worker no Railway
- Teste a conexão manualmente:

```python
import httpx

async def test_supabase():
    headers = {
        "apikey": "sua-service-role-key",
        "Authorization": "Bearer sua-service-role-key"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://xxxxx.supabase.co/rest/v1/investigations",
            headers=headers
        )
        print(response.json())
```

## 📈 Métricas e Monitoramento

### Queries Úteis

```sql
-- Total de anomalias por severidade (últimos 7 dias)
SELECT
    severity,
    COUNT(*) as total,
    AVG(anomaly_score) as avg_score
FROM anomalies
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY severity;

-- Anomalias não resolvidas
SELECT COUNT(*) FROM anomalies WHERE status != 'resolved';

-- Taxa de detecção por fonte
SELECT
    source,
    COUNT(*) as total_analyzed,
    COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed,
    ROUND(
        COUNT(CASE WHEN status = 'confirmed' THEN 1 END)::numeric /
        COUNT(*)::numeric * 100,
        2
    ) as confirmation_rate
FROM anomalies
GROUP BY source;
```

## 🎯 Próximos Passos

Após configurar o Supabase:

1. ✅ Configure alertas automáticos (Email/Webhook)
2. ✅ Crie dashboards de visualização
3. ✅ Configure backup automático
4. ✅ Defina políticas de retenção de dados

## 📚 Referências

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL JSON Functions](https://www.postgresql.org/docs/current/functions-json.html)
- [Supabase REST API](https://supabase.com/docs/guides/api)
