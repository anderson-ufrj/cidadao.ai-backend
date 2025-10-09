# Celery Beat Setup no Railway - Investigações 24/7

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-09
**Objetivo**: Configurar o Celery Beat no Railway para executar auto-investigations 24/7

---

## 🎯 Objetivo

Fazer o sistema criar investigações automáticas a cada 6 horas, monitorando contratos do Portal da Transparência sem intervenção manual.

---

## 📋 O que é o Celery Beat?

O **Celery Beat** é um scheduler (agendador) que dispara tasks do Celery em intervalos específicos. É como um cron job, mas integrado com o Celery.

**No nosso sistema:**
- **Celery Worker** = Executa as tasks (análise de contratos)
- **Celery Beat** = Agenda quando as tasks devem rodar (a cada 6h)

---

## 🚀 Configuração no Railway

### Passo 1: Verificar os 3 Serviços

Você deve ter **3 serviços** no Railway:

1. **cidadao-api** - API FastAPI (porta 8000)
2. **cidadao-worker** - Celery Worker
3. **cidadao-beat** - Celery Beat ← **ESTE É O IMPORTANTE!**

### Passo 2: Configurar o Serviço `cidadao-beat`

#### 2.1. Comando Start

No Railway → `cidadao-beat` → Settings → Deploy → **Start Command**:

```bash
celery -A src.infrastructure.queue.celery_app beat --loglevel=info
```

#### 2.2. Variáveis de Ambiente

As mesmas dos outros serviços:

```bash
# Supabase (OBRIGATÓRIO para persistência)
SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# System User (OBRIGATÓRIO para auto-investigations)
SYSTEM_AUTO_MONITOR_USER_ID=58050609-2fe2-49a6-a342-7cf66d83d216

# Redis (OBRIGATÓRIO para Celery)
REDIS_URL=redis://...

# LLM (OBRIGATÓRIO para análise de contratos)
GROQ_API_KEY=gsk_...

# Portal da Transparência (OPCIONAL)
TRANSPARENCY_API_KEY=***REDACTED-TRANSPARENCY-KEY***
```

#### 2.3. Verificar Health

O serviço deve estar:
- ✅ **Status**: Active (verde)
- ✅ **Logs**: Mostrando "beat: Starting..." e schedule das tasks

---

## 📊 Schedule Configurado

As tasks estão em `src/infrastructure/queue/celery_app.py`:

| Task | Intervalo | Descrição |
|------|-----------|-----------|
| `auto-monitor-new-contracts-6h` | **6 horas** | Monitora contratos novos |
| `auto-monitor-priority-orgs-4h` | 4 horas | Monitora organizações prioritárias |
| `auto-reanalyze-historical-weekly` | 7 dias | Reanálise histórica |
| `auto-investigation-health-hourly` | 1 hora | Health check do sistema |

---

## 🔍 Como Verificar se Está Funcionando

### Método 1: Logs do Railway

```
Railway → cidadao-beat → Logs
```

Deve aparecer:
```
[INFO] beat: Starting...
[INFO] Scheduler: Sending due task auto-monitor-new-contracts-6h
```

### Método 2: Supabase Dashboard

```
https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks/editor
```

1. Abra a tabela `investigations`
2. Filtre por `user_id = 58050609-2fe2-49a6-a342-7cf66d83d216`
3. Verifique se aparecem novas linhas a cada 6 horas

### Método 3: Script de Verificação

```bash
python3 check_celery_status.py
```

Mostra:
- Próximas execuções
- Últimas investigações criadas
- Status do sistema

---

## 🐛 Troubleshooting

### Problema 1: Celery Beat não inicia

**Sintoma**: Serviço fica "Crashed" ou "Restarting"

**Soluções**:
1. Verifique se o comando está correto (veja Passo 2.1)
2. Verifique se `REDIS_URL` está configurado
3. Verifique logs: pode ter erro de import

### Problema 2: Celery Beat inicia mas não cria investigations

**Sintoma**: Logs mostram "beat: Starting..." mas nenhuma investigation é criada

**Soluções**:
1. Verifique se `SYSTEM_AUTO_MONITOR_USER_ID` está configurado
2. Verifique se `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` estão corretos
3. Verifique se o Worker está rodando (precisa dele para executar as tasks)

### Problema 3: "No module named 'src.infrastructure'"

**Sintoma**: Erro de import no log

**Solução**:
- Verifique se o código está atualizado no Railway
- Force um novo deploy

### Problema 4: Tasks aparecem nos logs mas não executam

**Sintoma**: Logs mostram "Sending due task..." mas nada acontece

**Soluções**:
1. Verifique se o **Worker** está rodando (Beat só agenda, Worker executa!)
2. Verifique logs do Worker: `Railway → cidadao-worker → Logs`

---

## ✅ Checklist Final

Antes de considerar pronto, verifique:

- [ ] Serviço `cidadao-beat` está Active (verde)
- [ ] Comando está correto: `celery -A src.infrastructure.queue.celery_app beat --loglevel=info`
- [ ] Todas as variáveis de ambiente estão configuradas
- [ ] Logs mostram "beat: Starting..." e schedule das tasks
- [ ] Serviço `cidadao-worker` também está rodando
- [ ] Após 1 hora, verificar no Supabase se aparecem novas investigations
- [ ] Filtrar por `user_id = 58050609-2fe2-49a6-a342-7cf66d83d216`

---

## 📞 Próximos Passos

Depois que o Celery Beat estiver rodando:

1. **Aguarde 6 horas** para a primeira auto-investigation
2. **Monitore o Supabase** para confirmar que está criando investigations
3. **Configure alertas** para ser notificado de anomalias detectadas
4. **Ajuste o intervalo** se necessário (atualmente 6h)

---

## 🎉 Sucesso!

Quando estiver tudo funcionando, você verá:

- ✅ Investigations sendo criadas automaticamente a cada 6h
- ✅ `user_id` sempre `58050609-2fe2-49a6-a342-7cf66d83d216` (system user)
- ✅ `filters.auto_triggered = true`
- ✅ Análise completa de anomalias em contratos públicos

**O sistema estará rodando 24/7 sem necessidade de intervenção manual!** 🚀
