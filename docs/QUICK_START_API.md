# 🚀 Guia Rápido - Configuração da API

## 📋 Portal da Transparência em 3 Passos

### 1️⃣ Obter Chave (Opcional para Dados Reais)
```bash
# Acesse o site e cadastre-se
https://www.portaldatransparencia.gov.br/api-de-dados
```

### 2️⃣ Configurar Ambiente
```bash
# Crie arquivo .env
echo "TRANSPARENCY_API_KEY=sua-chave-aqui" > .env
```

### 3️⃣ Executar
```bash
# Modo HuggingFace (porta 7860)
python app.py

# OU modo desenvolvimento (porta 8000)
make run-dev
```

## 🔍 Verificar Modo de Operação

### Logs do Sistema
```bash
# COM API key:
INFO: Using real Portal da Transparência data
INFO: Fetching contracts from Portal da Transparência (real data)

# SEM API key:
WARNING: Portal da Transparência API key not configured, using demo data
INFO: Using demonstration data (no API key configured)
```

### Testar Rapidamente
```bash
# Via curl
curl http://localhost:7860/health

# Resposta esperada
{
  "status": "healthy",
  "transparency_api": {
    "configured": true,  # ou false se sem API key
    "mode": "production" # ou "demo"
  }
}
```

## ⚡ Dicas

### Desenvolvimento Local
- Use modo **demo** para desenvolvimento rápido
- Não precisa de API key para testar funcionalidades
- Resultados mostram "[DEMO]" claramente

### Produção
- Configure API key via variáveis de ambiente
- Use cache para economizar chamadas
- Monitor rate limiting (90 req/min)

## 🆘 Problemas Comuns

### "API key inválida"
```bash
# Verifique se a chave está correta
# Remova espaços extras
# Confirme que está ativa no portal
```

### "Rate limit excedido"
```bash
# Sistema aguarda automaticamente
# Veja logs para tempo de espera
# Ajuste batch size se necessário
```

### "Sem dados retornados"
```bash
# Verifique filtros (órgão, período)
# Alguns órgãos têm poucos contratos
# Tente órgãos maiores: 26000, 20000
```

---

📚 [Documentação Completa](./PORTAL_TRANSPARENCIA_INTEGRATION.md) | 🏠 [Voltar ao README](../README.md)