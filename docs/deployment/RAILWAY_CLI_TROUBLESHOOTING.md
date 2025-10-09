# 🚂 Railway CLI - Troubleshooting Guide

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-09 09:30:00 -03:00 (Minas Gerais, Brasil)
**Status**: Problemas de autenticação identificados

---

## 🚨 Problema Identificado

O Railway CLI não consegue abrir o browser para autenticação no ambiente atual.

### Tentativas Realizadas

1. ✅ **Instalação**: `bash <(curl -fsSL cli.railway.app/install.sh)` - OK
2. ❌ **Login interativo**: `railway login` - Browser não abre
3. ❌ **Login browserless**: `railway login --browserless` - "Cannot login in non-interactive mode"
4. ❌ **Token via env**: `export RAILWAY_TOKEN=...` - "Unauthorized"
5. ❌ **Pairing codes**: "white-zestful-dream", "jade-mellow-friendship" - Não autorizaram

---

## ✅ Soluções Alternativas

### Opção 1: Railway Web Interface (RECOMENDADO)

Tudo que o CLI faz pode ser feito via interface web:

**Para adicionar variáveis de ambiente:**
```
1. Acesse: https://railway.app
2. Abra seu projeto: cidadao.ai-backend
3. Clique em: Variables (aba lateral)
4. Adicione as variáveis necessárias
5. Railway redesplega automaticamente
```

**Para ver logs:**
```
1. Acesse: https://railway.app
2. Abra o serviço (API, Worker ou Beat)
3. Clique em: Deployments → Ver logs
```

**Para ver status:**
```
Dashboard do projeto mostra:
- Status de cada serviço (running/stopped)
- CPU/Memory usage
- Deploy history
- Build logs
```

---

### Opção 2: Resolver Autenticação do CLI

Se você realmente precisa do CLI, tente estas opções:

#### A. Forçar abertura de browser

```bash
# 1. Verificar se xdg-open funciona
xdg-open https://google.com

# 2. Se não abrir, configurar browser padrão
export BROWSER=/usr/bin/firefox  # ou /usr/bin/google-chrome

# 3. Tentar login novamente
railway login
```

#### B. Usar token de API permanente

```bash
# 1. Criar token permanente na web interface:
#    https://railway.app/account/tokens

# 2. Exportar o token (adicionar ao ~/.zshrc):
export RAILWAY_TOKEN="seu-token-permanente-aqui"

# 3. Testar:
railway whoami
```

#### C. Login via SSH/API Key

Consulte a documentação oficial:
- https://docs.railway.app/reference/cli-api#authentication
- https://docs.railway.app/guides/cli#login

---

## 🔍 Diagnóstico Detalhado

### Erro 1: Browser não abre
```bash
$ railway login
? Would you like to open the browser to authenticate? Yes
# Nada acontece - browser não abre
```

**Causa provável**:
- Ambiente CLI não detecta browser corretamente
- xdg-open não configurado
- Variável $BROWSER não definida

**Solução**: Configurar BROWSER ou usar web interface

---

### Erro 2: Token não persiste
```bash
$ export RAILWAY_TOKEN=4ad776e7-c7f9-42d5-a259-4b586c944af1
$ railway whoami
Error: Unauthorized
```

**Causa provável**:
- Token de pairing (temporário) em vez de token de API (permanente)
- Token expirou
- Token não é válido para autenticação CLI

**Solução**: Criar token permanente em https://railway.app/account/tokens

---

### Erro 3: Pairing codes não funcionam
```bash
# Tentativas:
# - white-zestful-dream
# - jade-mellow-friendship
# Nenhum autorizou o acesso
```

**Causa provável**:
- Pairing codes expiraram (TTL curto)
- Códigos digitados incorretamente
- Problema de sincronização com Railway backend

**Solução**: Usar método alternativo (token permanente ou web interface)

---

## 📚 Comandos Railway CLI Úteis

Quando o CLI funcionar, estes comandos são úteis:

### Gerenciamento de Projeto
```bash
# Ver informações do projeto
railway status

# Ver variáveis de ambiente
railway variables

# Adicionar variável
railway variables set KEY=value

# Ver logs em tempo real
railway logs

# Ver serviços
railway service
```

### Deploy e Build
```bash
# Deploy manual
railway up

# Ver deploys recentes
railway deployments

# Rollback
railway rollback
```

### Debugging
```bash
# Shell interativo no container
railway shell

# Executar comando no container
railway run <command>

# Ver build logs
railway logs --build
```

---

## 🎯 Recomendação Final

**Para o caso de uso atual (adicionar variáveis Supabase)**:

✅ **USE A WEB INTERFACE** - É mais rápido e confiável:

1. Acesse https://railway.app
2. Abra `cidadao.ai-backend`
3. Variables → Add Variables:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_ANON_KEY`
4. Railway redesplega automaticamente em ~2 minutos

**Para uso futuro do CLI**:

📋 **Crie um token permanente**:
1. https://railway.app/account/tokens
2. Create Token → Copie o token
3. Adicione ao `~/.zshrc`:
   ```bash
   export RAILWAY_TOKEN="seu-token-aqui"
   ```
4. `source ~/.zshrc`
5. `railway whoami` (deve funcionar)

---

## 🐛 Reportar Problemas

Se o problema persistir, reporte no GitHub do Railway CLI:
- https://github.com/railwayapp/cli/issues

**Template do report**:
```
**Problema**: Browser não abre no `railway login`
**OS**: Linux (Pop!_OS 22.04 / Ubuntu-based)
**Railway CLI Version**: v3.x.x (verificar com `railway --version`)
**Ambiente**: Zsh terminal

**Steps to reproduce**:
1. `railway login`
2. Select "Yes" to open browser
3. Browser doesn't open

**Expected**: Browser opens with Railway auth page
**Actual**: Nothing happens, no error message

**Workaround used**: Web interface for variable management
```

---

## 📊 Comparação: CLI vs Web Interface

| Tarefa | CLI | Web Interface | Vencedor |
|--------|-----|---------------|----------|
| **Adicionar variáveis** | `railway variables set KEY=value` | Ponto e clica | ⚖️ Empate |
| **Ver logs** | `railway logs -f` (tempo real) | Precisa atualizar página | 🏆 CLI |
| **Deploy** | `railway up` | Git push automático | 🏆 Web |
| **Debugging** | `railway shell` (acesso direto) | Não disponível | 🏆 CLI |
| **Setup inicial** | Requer autenticação funcional | Sempre funciona | 🏆 Web |
| **Scripts/Automação** | Perfeito para CI/CD | Não automatizável | 🏆 CLI |

---

## ✅ Conclusão

**Para hoje**: Use a web interface para adicionar as variáveis Supabase.

**Para amanhã**: Invista tempo em configurar o CLI com token permanente para ter acesso a comandos avançados como `railway shell` e `railway logs -f`.

---

**Documentado por**: Anderson Henrique da Silva
**Última atualização**: 2025-10-09 09:30:00 -03:00
**Localização**: Minas Gerais, Brasil
