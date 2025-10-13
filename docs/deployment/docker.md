# 🐳 Dockerfiles Guide

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-07 21:38:00

## 📁 Arquivos Disponíveis

Este projeto possui **dois Dockerfiles diferentes** para diferentes ambientes de deploy:

### 1. `Dockerfile` - Railway/Render/Produção
**Uso**: Deploy em Railway, Render, ou qualquer plataforma de produção

**Características**:
- ✅ API completa (`src.api.app`)
- ✅ Porta dinâmica (`${PORT}`)
- ✅ PostgreSQL client incluído
- ✅ Healthcheck com 40s startup
- ✅ Suporte a Celery workers
- ✅ Otimizado para produção

**Como usar**:
```bash
docker build -t cidadao-ai-backend .
docker run -p 8000:8000 -e PORT=8000 cidadao-ai-backend
```

### 2. `Dockerfile.hf` - HuggingFace Spaces
**Uso**: Deploy no HuggingFace Spaces

**Características**:
- ✅ API simplificada (`start_hf.py`)
- ✅ Porta fixa 7860 (padrão HF Spaces)
- ✅ Healthcheck com 5s startup
- ✅ Sem dependências de DB
- ✅ Otimizado para ambiente HF

**Como usar no HuggingFace**:
1. Renomeie `Dockerfile.hf` para `Dockerfile`
2. Push para o branch `hf-fastapi`
3. HuggingFace detecta e faz deploy automático

**Como testar localmente**:
```bash
docker build -f Dockerfile.hf -t cidadao-ai-hf .
docker run -p 7860:7860 cidadao-ai-hf
```

## 🎯 Qual Usar?

### Railway/Render → Use `Procfile` (Recommended)
```bash
# Railway prioriza Procfile sobre Dockerfile
# Certifique-se de que railway.toml/railway.json NÃO existem
# Railway detecta e usa Procfile automaticamente
git push origin main
```

**IMPORTANTE**: Se railway.toml, railway.json ou nixpacks.toml existirem, faça backup:
```bash
mv railway.toml railway.toml.backup
mv railway.json railway.json.backup
mv nixpacks.toml nixpacks.toml.backup
```

### HuggingFace Spaces → Use `Dockerfile.hf`
```bash
# Copiar antes de fazer push para HF
cp Dockerfile.hf Dockerfile
git push huggingface main:hf-fastapi
```

### Docker Compose local → Use `docker-compose.yml`
```bash
# Usa Dockerfile automaticamente
docker-compose up
```

## 🔧 Diferenças Técnicas

| Feature | `Dockerfile` (Produção) | `Dockerfile.hf` (HF Spaces) |
|---------|------------------------|----------------------------|
| **Entry Point** | `src.api.app` | `start_hf.py` |
| **Porta** | Dinâmica (`${PORT}`) | Fixa (7860) |
| **PostgreSQL** | ✅ Cliente incluído | ❌ Não necessário |
| **Healthcheck Start** | 40s | 5s |
| **Celery Support** | ✅ Full | ❌ Não suportado |
| **WebSocket** | ✅ Completo | ✅ Básico |
| **Database** | PostgreSQL/Supabase | In-memory |

## 🚀 Deploy Automático

### Railway
```toml
# railway.toml - detecta Dockerfile automaticamente
[deploy]
startCommand = "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"
```

### HuggingFace Spaces
```yaml
# No HF, copie Dockerfile.hf para Dockerfile
# HF detecta automaticamente e faz build
```

## 📝 Notas Importantes

1. **Nunca commitar ambos como `Dockerfile`**: Isso causa confusão. Mantenha sempre:
   - `Dockerfile` → versão Railway/Render
   - `Dockerfile.hf` → versão HuggingFace

2. **Portas**:
   - Railway: Usa `PORT` env var (geralmente 3000-9000)
   - HuggingFace: Sempre 7860
   - Local: 8000 por padrão

3. **Environment Variables**:
   - Produção: Todas as vars necessárias (SUPABASE, GROQ, etc)
   - HF: Mesmas vars, mas algumas opcionais

4. **Healthcheck**:
   - Produção: 40s startup (agentes levam tempo pra inicializar)
   - HF: 5s startup (versão simplificada é rápida)

## 🔍 Troubleshooting

### Erro: "Port already in use"
```bash
# Matar processo na porta
lsof -ti:8000 | xargs kill -9
```

### Erro: "Invalid value for --port"
```bash
# Garantir que PORT está definida
export PORT=8000
docker run -e PORT=8000 ...
```

### Healthcheck falhando
```bash
# Ver logs do container
docker logs <container_id>

# Testar healthcheck manualmente
curl http://localhost:8000/health
```

## 📚 Recursos

- [Railway Docs](https://docs.railway.app/deploy/dockerfiles)
- [HuggingFace Spaces Docs](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
