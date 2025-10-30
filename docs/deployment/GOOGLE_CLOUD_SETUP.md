# 🎙️ Google Cloud Voice API - Guia de Configuração

**Objetivo**: Configurar Google Cloud Text-to-Speech e Speech-to-Text para o sistema de voz do Cidadão.AI

**Tempo estimado**: 15-20 minutos
**Custo**: Grátis até os limites do free tier

---

## 📋 Pré-requisitos

- Conta Google (Gmail)
- Cartão de crédito (para verificação - Google oferece $300 em créditos grátis)
- Acesso ao terminal/command line

---

## 🚀 Passo 1: Criar Projeto no Google Cloud

### 1.1 Acesse o Console
- URL: https://console.cloud.google.com
- Faça login com sua conta Google

### 1.2 Criar Novo Projeto
1. Clique em **"Select a project"** no topo da página
2. Clique em **"NEW PROJECT"**
3. Preencha:
   - **Project name**: `cidadao-ai-voice` (ou nome de sua preferência)
   - **Organization**: (deixe em branco se não tiver)
4. Clique **"CREATE"**
5. Aguarde alguns segundos até o projeto ser criado
6. **Anote o Project ID** (aparece ao lado do nome, ex: `cidadao-ai-voice-123456`)

### 1.3 Ativar Faturamento (Free Trial)
1. Menu ☰ → **Billing**
2. Se primeira vez:
   - Clique **"Activate"** ou **"Add billing account"**
   - Preencha dados do cartão (não será cobrado automaticamente)
   - Aceite os $300 em créditos grátis por 90 dias

---

## 🔌 Passo 2: Habilitar APIs Necessárias

### 2.1 Cloud Text-to-Speech API
1. Menu ☰ → **APIs & Services** → **Library**
2. Na busca, digite: **"Cloud Text-to-Speech API"**
3. Clique no resultado
4. Clique **"ENABLE"**
5. Aguarde ativação (alguns segundos)

### 2.2 Cloud Speech-to-Text API
1. Ainda em **APIs & Services** → **Library**
2. Digite: **"Cloud Speech-to-Text API"**
3. Clique no resultado
4. Clique **"ENABLE"**
5. Aguarde ativação

✅ Confirmação: Ambas APIs devem aparecer em **APIs & Services** → **Dashboard** como "Enabled"

---

## 🔑 Passo 3: Criar Service Account

### 3.1 Criar a Conta
1. Menu ☰ → **IAM & Admin** → **Service Accounts**
2. Clique **"CREATE SERVICE ACCOUNT"**

### 3.2 Detalhes da Service Account
**Passo 1 do wizard**:
- **Service account name**: `cidadao-voice-service`
- **Service account ID**: (auto-preenchido como `cidadao-voice-service@...`)
- **Description**: `Service account for Cidadão.AI voice features (STT + TTS)`
- Clique **"CREATE AND CONTINUE"**

### 3.3 Adicionar Permissões
**Passo 2 do wizard**:
1. Clique em **"Select a role"**
2. Digite e selecione: **"Cloud Speech Client"**
3. Clique **"+ ADD ANOTHER ROLE"**
4. Digite e selecione: **"Cloud Text-to-Speech Client"**
5. Clique **"CONTINUE"**

### 3.4 Finalizar
**Passo 3 do wizard**:
- Deixe campos em branco (não precisa dar acesso a usuários)
- Clique **"DONE"**

---

## 📥 Passo 4: Baixar Chave JSON

### 4.1 Gerar Chave
1. Na lista de **Service Accounts**, encontre `cidadao-voice-service@...`
2. Clique nos **3 pontinhos verticais** (⋮) à direita
3. Selecione **"Manage keys"**
4. Clique **"ADD KEY"** → **"Create new key"**
5. Selecione formato: **JSON**
6. Clique **"CREATE"**

### 4.2 Arquivo Baixado
- Um arquivo JSON será baixado automaticamente
- Nome típico: `cidadao-ai-voice-xxxxx-yyyyyyy.json`
- **⚠️ IMPORTANTE**: Guarde este arquivo em local seguro
- **⚠️ NUNCA COMITE** este arquivo no Git

---

## 💻 Passo 5: Configurar Desenvolvimento Local

### 5.1 Mover Arquivo JSON
```bash
# Navegue até a raiz do projeto
cd /home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend

# Crie pasta para credenciais (se não existir)
mkdir -p config/credentials

# Mova o arquivo baixado (ajuste o nome do seu arquivo)
mv ~/Downloads/cidadao-ai-voice-*.json config/credentials/google-cloud-key.json

# Verifique permissões (apenas você deve ler)
chmod 600 config/credentials/google-cloud-key.json
```

### 5.2 Configurar .env
```bash
# Edite o arquivo .env
nano .env

# Adicione estas linhas (ajuste o path se necessário):
GOOGLE_CREDENTIALS_PATH=/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend/config/credentials/google-cloud-key.json
GOOGLE_CLOUD_PROJECT_ID=cidadao-ai-voice

# Opcionais (valores padrão já otimizados):
GOOGLE_SPEECH_LANGUAGE_CODE=pt-BR
GOOGLE_TTS_VOICE_NAME=pt-BR-Wavenet-A
GOOGLE_TTS_SPEAKING_RATE=1.0
GOOGLE_TTS_PITCH=0.0

# Salve e feche (Ctrl+O, Enter, Ctrl+X)
```

### 5.3 Verificar Project ID
Se não souber o Project ID exato:

**Opção 1**: No Google Cloud Console
- Topo da página, ao lado do nome do projeto
- Formato: `cidadao-ai-voice` ou `cidadao-ai-voice-123456`

**Opção 2**: No arquivo JSON baixado
```bash
# Veja o campo project_id
cat config/credentials/google-cloud-key.json | grep project_id
# Saída: "project_id": "cidadao-ai-voice",
```

### 5.4 Testar Configuração
```bash
# 1. Inicie o servidor (se não estiver rodando)
make run-dev

# 2. Em outro terminal, teste o health endpoint
curl http://localhost:8000/api/v1/voice/health | jq

# Resposta esperada:
# {
#   "status": "healthy",
#   "google_cloud_configured": true,  ← DEVE SER TRUE
#   "features": {
#     "speech_to_text": true,
#     "text_to_speech": true
#   },
#   "configuration": {
#     "language": "pt-BR",
#     "default_voice": "pt-BR-Wavenet-A",
#     "credentials_loaded": true  ← DEVE SER TRUE
#   }
# }
```

### 5.5 Teste Text-to-Speech Real
```bash
# Teste voz padrão (Drummond)
curl -X POST "http://localhost:8000/api/v1/voice/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Olá! Esta é a voz de Drummond testando o Google Cloud Text to Speech."}' \
  --output test_drummond.mp3

# Teste voz de Ayrton Senna (rápida - 1.15x)
curl -X POST "http://localhost:8000/api/v1/voice/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Teste de voz",
    "agent_id": "ayrton_senna",
    "return_audio": true
  }' \
  --output test_senna.mp3

# Teste voz de Machado (lenta e profunda - 0.85x, -2 pitch)
curl -X POST "http://localhost:8000/api/v1/voice/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Teste de narrativa",
    "agent_id": "machado",
    "return_audio": true
  }' \
  --output test_machado.mp3

# Reproduza os áudios
mpg123 test_drummond.mp3
mpg123 test_senna.mp3
mpg123 test_machado.mp3

# Ou use VLC
vlc test_drummond.mp3
```

---

## ☁️ Passo 6: Configurar no Railway (Produção)

### Opção A: Usando Variável de Ambiente (Recomendado)

**6.1 Encode JSON para Base64**
```bash
# No terminal local
cat config/credentials/google-cloud-key.json | base64 -w 0 > google-creds-base64.txt

# O arquivo google-creds-base64.txt contém uma linha longa
# Copie todo o conteúdo
cat google-creds-base64.txt
```

**6.2 Configurar no Railway Dashboard**
1. Acesse: https://railway.app/
2. Navegue até seu projeto: **cidadao.ai-backend**
3. Clique na aba **"Variables"**
4. Adicione estas variáveis:

```
GOOGLE_CLOUD_PROJECT_ID=cidadao-ai-voice
GOOGLE_CREDENTIALS_BASE64=<cole aqui o base64 do passo 6.1>
```

**6.3 Atualizar Código para Suportar Base64**

O código já está preparado para isso! O `voice_service.py` detecta automaticamente se existe `GOOGLE_CREDENTIALS_BASE64` e decodifica.

### Opção B: Upload de Arquivo (Railway CLI)

**6.1 Instalar Railway CLI**
```bash
# Instale globalmente
npm install -g @railway/cli

# Ou use npx (sem instalar)
npx @railway/cli
```

**6.2 Fazer Login e Link**
```bash
# Login
railway login

# Link ao projeto (dentro da pasta do backend)
cd /home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend
railway link
# Selecione: cidadao.ai-backend (production)
```

**6.3 Configurar Variáveis**
```bash
# Project ID
railway variables set GOOGLE_CLOUD_PROJECT_ID=cidadao-ai-voice

# JSON codificado
railway variables set GOOGLE_CREDENTIALS_BASE64=$(cat config/credentials/google-cloud-key.json | base64 -w 0)

# Verificar
railway variables
```

**6.4 Deploy**
```bash
# Deploy manual (se necessário)
railway up

# Ou aguarde auto-deploy do GitHub
git push origin main
```

### Opção C: Upload de Arquivo via Dashboard (Alternativa)

1. Railway Dashboard → Seu projeto
2. **Settings** → **Files**
3. Upload do arquivo `google-cloud-key.json`
4. Path será: `/app/google-cloud-key.json`
5. Em **Variables**, adicione:
   ```
   GOOGLE_CREDENTIALS_PATH=/app/google-cloud-key.json
   GOOGLE_CLOUD_PROJECT_ID=cidadao-ai-voice
   ```

---

## 🧪 Passo 7: Validar no Railway

### 7.1 Health Check
```bash
# Verifique se está configurado
curl https://cidadao-api-production.up.railway.app/api/v1/voice/health | jq

# Deve retornar:
# {
#   "status": "healthy",
#   "google_cloud_configured": true,
#   "features": {
#     "speech_to_text": true,
#     "text_to_speech": true
#   }
# }
```

### 7.2 Teste TTS em Produção
```bash
# Teste voz padrão
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/voice/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Olá do Railway!"}' \
  --output railway_test.mp3

# Reproduza
mpg123 railway_test.mp3
```

### 7.3 Teste Perfis de Agentes
```bash
# Liste perfis de voz
curl https://cidadao-api-production.up.railway.app/api/v1/voice/agent-voices | jq '.statistics'

# Teste voz de Senna (mais rápida - 1.15x)
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/voice/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Olá!",
    "agent_id": "ayrton_senna",
    "return_audio": true
  }' \
  --output senna_railway.mp3
```

---

## 💰 Custos e Limites

### Free Tier (Mensal)
| Serviço | Free Tier | Após Free Tier |
|---------|-----------|----------------|
| **Text-to-Speech** | 0-1M caracteres: GRÁTIS | $16 por 1M caracteres |
| | WaveNet/Neural2: 0-1M: GRÁTIS | $16 por 1M caracteres |
| **Speech-to-Text** | 0-60 minutos: GRÁTIS | Standard: $0.006 / 15 seg |

### Estimativa de Uso (1,000 conversas/dia)
```
Text-to-Speech:
- 1,000 conversas × 200 caracteres/resposta = 200,000 chars/dia
- 200,000 × 30 dias = 6M caracteres/mês
- Custo: 6M × ($16/1M) = $96/mês

Speech-to-Text:
- 1,000 conversas × 10 segundos/audio = 10,000 segundos/dia
- 10,000 × 30 = 300,000 segundos/mês = 83 horas
- Custo: 83 horas × $1.44/hora = ~$120/mês

Total estimado: ~$216/mês para 30,000 conversas/mês
```

### Otimização de Custos
1. **Cache**: Respostas comuns em cache (FAQ, greetings)
2. **Limites**: Máximo de caracteres por resposta
3. **Qualidade**: Usar Standard ao invés de Neural2/WaveNet (economiza muito)
4. **Monitoramento**: Alertas quando ultrapassar limites

---

## 🔒 Segurança

### ✅ Práticas Recomendadas
- ✅ Arquivo JSON em `.gitignore` (já configurado)
- ✅ Permissões restritas: `chmod 600 google-cloud-key.json`
- ✅ Service Account com mínimas permissões necessárias
- ✅ Rotação de chaves a cada 90 dias
- ✅ Monitoramento de uso no Google Cloud Console

### ❌ NUNCA FAÇA
- ❌ Comitar arquivo JSON no Git
- ❌ Compartilhar credenciais via email/chat
- ❌ Dar permissões além do necessário (Owner, Editor)
- ❌ Usar mesma Service Account para múltiplos projetos
- ❌ Hardcoded credentials no código

---

## 🐛 Troubleshooting

### Problema 1: "google_cloud_configured": false

**Causa**: Credenciais não encontradas

**Solução**:
```bash
# Verifique se arquivo existe
ls -la config/credentials/google-cloud-key.json

# Verifique .env
grep GOOGLE_CREDENTIALS_PATH .env

# Verifique se o path está correto (absoluto, não relativo)
echo $GOOGLE_CREDENTIALS_PATH
```

### Problema 2: "Permission denied" ao acessar JSON

**Causa**: Permissões incorretas

**Solução**:
```bash
# Corrija permissões
chmod 600 config/credentials/google-cloud-key.json

# Verifique
ls -la config/credentials/google-cloud-key.json
# Deve mostrar: -rw------- (somente dono lê/escreve)
```

### Problema 3: "API not enabled"

**Causa**: APIs não habilitadas no projeto

**Solução**:
1. Acesse: https://console.cloud.google.com/apis/library
2. Procure: "Cloud Text-to-Speech API"
3. Clique "ENABLE"
4. Repita para "Cloud Speech-to-Text API"

### Problema 4: "Invalid project_id"

**Causa**: Project ID incorreto no .env

**Solução**:
```bash
# Veja o project_id correto no JSON
cat config/credentials/google-cloud-key.json | grep project_id

# Atualize .env com o valor exato
nano .env
```

### Problema 5: Áudio não é gerado (erro 500)

**Causa**: Quota excedida ou billing não ativado

**Solução**:
1. Acesse: https://console.cloud.google.com/billing
2. Verifique se billing está ativo
3. Veja quotas: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/quotas
4. Se excedeu free tier, adicione cartão de crédito

### Problema 6: Railway não encontra credenciais

**Causa**: Variável de ambiente não configurada corretamente

**Solução**:
```bash
# Verifique no Railway CLI
railway variables | grep GOOGLE

# Se vazio, configure novamente:
railway variables set GOOGLE_CREDENTIALS_BASE64=$(cat config/credentials/google-cloud-key.json | base64 -w 0)
railway variables set GOOGLE_CLOUD_PROJECT_ID=cidadao-ai-voice

# Force redeploy
railway up --force
```

---

## 📊 Monitoramento

### Google Cloud Console
1. Acesse: https://console.cloud.google.com
2. Menu ☰ → **APIs & Services** → **Dashboard**
3. Veja métricas de uso:
   - Requests por dia
   - Erros
   - Latência

### Configurar Alertas
1. Menu ☰ → **Monitoring** → **Alerting**
2. **Create Policy**
3. Exemplos de alertas:
   - Custo diário > $10
   - Requisições/hora > 1000
   - Taxa de erro > 5%

---

## ✅ Checklist de Configuração

### Desenvolvimento Local
- [ ] Projeto criado no Google Cloud
- [ ] APIs habilitadas (Text-to-Speech + Speech-to-Text)
- [ ] Service Account criada com permissões corretas
- [ ] Arquivo JSON baixado
- [ ] Arquivo JSON movido para `config/credentials/`
- [ ] `.env` configurado com paths corretos
- [ ] Health endpoint retorna `"google_cloud_configured": true`
- [ ] Teste de TTS gera áudio válido
- [ ] Teste com diferentes agentes funciona

### Produção (Railway)
- [ ] Variáveis configuradas no Railway Dashboard
- [ ] `GOOGLE_CREDENTIALS_BASE64` ou arquivo uploaded
- [ ] `GOOGLE_CLOUD_PROJECT_ID` configurado
- [ ] Deploy realizado com sucesso
- [ ] Health endpoint em produção retorna configurado: true
- [ ] Teste de TTS em produção funciona
- [ ] Monitoramento configurado

---

## 🔗 Links Úteis

- **Google Cloud Console**: https://console.cloud.google.com
- **Text-to-Speech Pricing**: https://cloud.google.com/text-to-speech/pricing
- **Speech-to-Text Pricing**: https://cloud.google.com/speech-to-text/pricing
- **Vozes disponíveis (pt-BR)**: https://cloud.google.com/text-to-speech/docs/voices
- **Railway Dashboard**: https://railway.app/dashboard
- **Cidadão.AI API Docs**: https://cidadao-api-production.up.railway.app/docs

---

## 📞 Suporte

Se encontrar problemas:

1. **Verifique logs**:
   ```bash
   # Local
   tail -f logs/app.log

   # Railway
   railway logs
   ```

2. **Teste isolado**:
   ```bash
   # Teste apenas autenticação
   python -c "
   from google.oauth2 import service_account
   credentials = service_account.Credentials.from_service_account_file(
       'config/credentials/google-cloud-key.json'
   )
   print('Credenciais válidas!')
   "
   ```

3. **Consulte documentação**:
   - Sistema de voz: `docs/project/reports/2025-10/VOICE_PERSONALITY_SYSTEM_2025_10_30.md`
   - Progresso: `docs/project/reports/2025-10/VOICE_INTEGRATION_PROGRESS_2025_10_30.md`

---

**Última atualização**: 2025-10-30
**Versão**: 1.0.0
**Status**: Guia completo e testado
