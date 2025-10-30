# Railway Voice Integration - Credentials Troubleshooting

**Data**: 2025-10-30
**Status**: 🔧 Troubleshooting em andamento

---

## 🚨 Problema Identificado

### Sintoma
```bash
POST /api/v1/voice/speak
Status: 500 Internal Server Error

Erro:
"Failed to synthesize speech: Your default credentials were not found.
To set up Application Default Credentials, see
https://cloud.google.com/docs/authentication/external/set-up-adc"
```

### Diagnóstico Realizado

#### 1. ✅ Código Backend - OK
- ✅ `src/services/voice_service.py` suporta credenciais base64
- ✅ Prioridade correta: base64 → arquivo → default
- ✅ Logging implementado para debug
- ✅ Health endpoint melhorado com diagnóstico detalhado

#### 2. ✅ Railway Variables - CONFIGURADA
- ✅ `GOOGLE_CREDENTIALS_BASE64` existe no Railway
- ✅ `GOOGLE_CLOUD_PROJECT_ID=cidadao-ai` configurado
- ⚠️ **POSSÍVEL PROBLEMA**: Valor pode estar incorreto/corrompido

#### 3. 🔍 Testes Realizados
```bash
# Health check mostra:
curl https://cidadao-api-production.up.railway.app/api/v1/voice/health
{
  "configuration": {
    "credentials_configured": false  # ❌ PROBLEMA!
  }
}

# TTS retorna erro 500:
curl -X POST .../api/v1/voice/speak -d '{"text":"teste"}'
Status: 500 - Credentials not found
```

---

## 🔧 Solução: Atualizar Credenciais no Railway

### Passo 1: Gerar Base64 Correto

Executar script local:
```bash
cd /home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend
./scripts/deployment/generate_google_credentials_base64.sh
```

**Output esperado**:
```
✅ Base64 generated successfully!
📊 Statistics:
  Original file size: 2348 bytes
  Base64 length: 3132 characters
📁 Full base64 saved to: /tmp/google_credentials_base64.txt
```

### Passo 2: Copiar Base64

```bash
# Linux (com xclip)
cat /tmp/google_credentials_base64.txt | xclip -selection clipboard

# macOS
cat /tmp/google_credentials_base64.txt | pbcopy

# Manual
cat /tmp/google_credentials_base64.txt
```

**Valor gerado** (3132 caracteres):
```
ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY2lkYWRhby1haSIsC...
(copiar valor completo de /tmp/google_credentials_base64.txt)
```

### Passo 3: Atualizar no Railway

1. **Acessar Railway Dashboard**:
   - URL: https://railway.app/project/cidadao-ai/settings
   - Seção: **Shared Variables** → **production**

2. **Localizar variável**:
   - Nome: `GOOGLE_CREDENTIALS_BASE64`
   - Status atual: ⚠️ Valor pode estar incorreto

3. **Atualizar valor**:
   - Clicar em **GOOGLE_CREDENTIALS_BASE64**
   - Colar o novo valor de `/tmp/google_credentials_base64.txt`
   - **IMPORTANTE**: Deve ser uma única linha sem quebras
   - Comprimento: **3132 caracteres**

4. **Verificar formato**:
   ```
   ✅ Correto:
   ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC...VuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo=

   ❌ Incorreto (com quebras de linha):
   ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC
   iAgInByb2plY3RfaWQiOiAiY2lkYWRhby1haSIs...
   ```

5. **Salvar mudanças**:
   - Clicar em **Update**
   - Railway iniciará redeploy automático (~2-3 minutos)

### Passo 4: Aguardar Redeploy

**Monitorar logs do Railway**:
1. Ir para: https://railway.app/project/cidadao-ai/deployments
2. Aguardar status: **Success** ✅
3. Tempo estimado: 2-3 minutos

**Logs esperados durante inicialização**:
```
[voice_service] INFO google_credentials_loaded_from_base64 project_id=cidadao-ai
[voice_service] INFO stt_client_initialized
[voice_service] INFO tts_client_initialized
```

### Passo 5: Validar Configuração

#### Teste 1: Health Check Detalhado
```bash
curl https://cidadao-api-production.up.railway.app/api/v1/voice/health | jq '.configuration'
```

**Resultado esperado** ✅:
```json
{
  "language": "pt-BR",
  "credentials_configured": true,
  "credentials_valid": true,
  "credential_source": "base64_env_var",
  "has_base64_credentials": true,
  "has_file_credentials": false,
  "credential_error": null
}
```

**Se ainda estiver com erro** ❌:
```json
{
  "credentials_configured": false,
  "credentials_valid": false,
  "credential_error": "Detailed error message here"
}
```
→ Verificar se base64 foi colado corretamente (sem quebras de linha)

#### Teste 2: Síntese de Voz Real
```bash
curl -X POST https://cidadao-api-production.up.railway.app/api/v1/voice/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Olá! Teste de integração de voz bem-sucedido!","voice_name":"pt-BR-Chirp3-HD-Zephyr"}' \
  --output test_voice_railway.mp3

# Verificar arquivo gerado
ls -lh test_voice_railway.mp3
# Deve ter ~20-30KB

# Ouvir o áudio
mpv test_voice_railway.mp3  # ou vlc, mplayer, etc.
```

**Resultado esperado** ✅:
- Status: `200 OK`
- Arquivo MP3 gerado (~25KB)
- Reproduz áudio "Olá! Teste de integração..."

#### Teste 3: Diferentes Vozes de Agentes
```bash
# Drummond (feminino, suave)
curl -X POST .../speak -d '{"text":"Sou Drummond","voice_name":"pt-BR-Chirp3-HD-Zephyr"}' -o drummond.mp3

# Zumbi (masculino, feroz)
curl -X POST .../speak -d '{"text":"Sou Zumbi","voice_name":"pt-BR-Chirp3-HD-Fenrir"}' -o zumbi.mp3

# Anita (feminino, energética)
curl -X POST .../speak -d '{"text":"Sou Anita","voice_name":"pt-BR-Chirp3-HD-Callirrhoe"}' -o anita.mp3
```

---

## 📋 Checklist de Verificação

### Antes de Atualizar Railway
- [ ] Script `generate_google_credentials_base64.sh` executado
- [ ] Base64 gerado em `/tmp/google_credentials_base64.txt`
- [ ] Comprimento: 3132 caracteres
- [ ] Inicia com: `ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC`
- [ ] Termina com: `VuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo=`

### Durante Atualização Railway
- [ ] Acessou Railway Dashboard
- [ ] Localizou `GOOGLE_CREDENTIALS_BASE64` em Shared Variables
- [ ] Colou valor SEM quebras de linha
- [ ] Clicou em **Update**
- [ ] Railway iniciou redeploy

### Após Redeploy
- [ ] Deploy com status **Success**
- [ ] Health check: `credentials_configured: true`
- [ ] Health check: `credentials_valid: true`
- [ ] Health check: `credential_source: "base64_env_var"`
- [ ] TTS endpoint retorna 200 OK
- [ ] Arquivo MP3 gerado e reproduzível
- [ ] Múltiplas vozes funcionando

---

## 🔍 Troubleshooting Avançado

### Problema 1: Base64 com Quebras de Linha

**Sintoma**:
```
credential_error: "Invalid base64 encoding"
```

**Solução**:
```bash
# Gerar sem quebras de linha
base64 -w 0 config/credentials/google-cloud-key.json > /tmp/creds.txt

# Verificar que é uma linha única
wc -l /tmp/creds.txt
# Deve mostrar: 1 /tmp/creds.txt
```

### Problema 2: JSON Corrompido

**Sintoma**:
```
credential_error: "Invalid JSON in base64"
```

**Solução**:
```bash
# Validar JSON original
jq empty config/credentials/google-cloud-key.json
# Deve sair sem erros

# Testar decodificação
base64 -d /tmp/google_credentials_base64.txt | jq empty
# Deve sair sem erros
```

### Problema 3: Service Account sem Permissões

**Sintoma**:
```
Error: Permission denied on Cloud Text-to-Speech API
```

**Solução**: Verificar no Google Cloud Console:
1. Ir para: https://console.cloud.google.com/iam-admin/iam?project=cidadao-ai
2. Localizar: `cidadao-ai@cidadao-ai.iam.gserviceaccount.com`
3. Garantir roles:
   - **Cloud Text-to-Speech User**
   - **Cloud Speech-to-Text User**

### Problema 4: APIs não Habilitadas

**Sintoma**:
```
Error: Cloud Text-to-Speech API has not been used in project
```

**Solução**: Habilitar APIs no Google Cloud:
```bash
# Habilitar Cloud Text-to-Speech API
gcloud services enable texttospeech.googleapis.com --project=cidadao-ai

# Habilitar Cloud Speech-to-Text API
gcloud services enable speech.googleapis.com --project=cidadao-ai
```

Ou via Console:
- https://console.cloud.google.com/apis/library/texttospeech.googleapis.com?project=cidadao-ai
- https://console.cloud.google.com/apis/library/speech.googleapis.com?project=cidadao-ai

---

## 📊 Status Final Esperado

### Health Endpoint
```json
{
  "status": "healthy",
  "service": "voice",
  "configuration": {
    "language": "pt-BR",
    "credentials_configured": true,
    "credentials_valid": true,
    "credential_source": "base64_env_var",
    "has_base64_credentials": true,
    "has_file_credentials": false,
    "credential_error": null
  }
}
```

### Agent Voices
```bash
curl .../api/v1/voice/agent-voices | jq '.statistics'
{
  "total_agents": 20,
  "quality_distribution": {
    "chirp3-hd": 20
  },
  "gender_distribution": {
    "female": 8,
    "male": 12
  }
}
```

### TTS Working
```bash
curl -X POST .../speak -d '{"text":"teste"}' --output test.mp3
# HTTP 200, arquivo ~25KB MP3
```

---

## 📞 Próximos Passos

Após credenciais configuradas:

1. **✅ Validar todos os endpoints de voz**
2. **✅ Testar integração com frontend**
3. **✅ Documentar vozes dos 20 agentes**
4. **✅ Criar exemplos de uso para desenvolvedores**

---

## 📝 Informações da Credencial

**Project**: cidadao-ai
**Service Account**: cidadao-ai@cidadao-ai.iam.gserviceaccount.com
**Base64 Length**: 3132 characters
**File Location**: `/tmp/google_credentials_base64.txt`

---

**Status**: 🔄 Aguardando atualização da variável no Railway
