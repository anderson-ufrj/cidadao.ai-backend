# 🚀 Guia de Deploy Completo - Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## 📊 Comparação de Opções

| Opção | Custo | Complexidade | Recursos | Recomendado Para |
|-------|-------|--------------|----------|------------------|
| **HuggingFace Spaces** | Grátis | Fácil | Limitado (sem DB/Redis) | Demo/MVP |
| **Render.com** | Grátis/Pago | Médio | Completo | Produção pequena |
| **Railway.app** | $5-20/mês | Fácil | Completo | Produção média |
| **VPS + Docker** | $5-40/mês | Difícil | Completo | Controle total |
| **Kubernetes** | $100+/mês | Expert | Escalável | Produção grande |

## 🏃 Quick Start - Deploy Completo

### Opção 1: Render.com (Recomendado para começar)

1. **Crie conta no Render.com**
2. **Configure o Blueprint**:
   ```bash
   git add render.yaml
   git commit -m "Add Render deployment config"
   git push origin main
   ```

3. **No Render Dashboard**:
   - New > Blueprint
   - Connect GitHub repo
   - Add environment variables:
     - `MARITACA_API_KEY`
     - `GROQ_API_KEY`
     - `JWT_SECRET_KEY`
     - `SECRET_KEY`

### Opção 2: VPS com Docker (Mais controle)

1. **Prepare o VPS** (Ubuntu 22.04):
   ```bash
   # No seu computador
   export VPS_HOST=user@your-vps-ip
   ./deploy.sh vps
   ```

2. **Configure SSL**:
   ```bash
   ssh $VPS_HOST
   sudo certbot --nginx -d api.cidadao.ai
   ```

3. **Monitore**:
   ```bash
   docker-compose -f docker-compose.production.yml logs -f
   ```

## 🔧 Configuração Completa

### 1. Banco de Dados PostgreSQL

```sql
-- Criar database
CREATE DATABASE cidadao;
CREATE USER cidadao WITH ENCRYPTED PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE cidadao TO cidadao;

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### 2. Redis Configuration

```conf
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.cidadao.ai;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🔒 Segurança em Produção

1. **Firewall**:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Backups automáticos**:
   ```bash
   # Adicione ao crontab
   0 2 * * * pg_dump cidadao | gzip > /backups/cidadao_$(date +\%Y\%m\%d).sql.gz
   ```

3. **Monitoramento**:
   - Grafana: http://your-server:3000
   - Prometheus: http://your-server:9090

## 📈 Otimizações para Produção

1. **Database Indexes**:
   ```sql
   CREATE INDEX idx_contracts_date ON contracts(created_at);
   CREATE INDEX idx_contracts_value ON contracts(value);
   CREATE INDEX idx_investigations_status ON investigations(status);
   ```

2. **Redis Clustering** (opcional):
   ```bash
   # Para alta disponibilidade
   docker-compose -f docker-compose.redis-cluster.yml up -d
   ```

3. **CDN para Assets**:
   - Configure Cloudflare
   - Cache static files

## 🔍 Troubleshooting

### Problema: "Network is unreachable"
**Solução**: Configure DATABASE_URL corretamente

### Problema: "Redis connection refused"
**Solução**: Verifique REDIS_URL e senha

### Problema: "Out of memory"
**Solução**: Aumente limits no Docker:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

## 📊 Monitoramento

### Métricas importantes:
- API Latency P95 < 200ms
- Error Rate < 1%
- Cache Hit Rate > 80%
- Database Connections < 80%

### Alertas recomendados:
- CPU > 80% por 5 minutos
- Memory > 90%
- Error rate > 5%
- Database down

## 🚀 Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados com migrations rodadas
- [ ] Redis funcionando
- [ ] SSL/HTTPS configurado
- [ ] Backups automáticos
- [ ] Monitoramento ativo
- [ ] Logs centralizados
- [ ] Rate limiting configurado
- [ ] CORS para frontend
- [ ] Health checks passando

## 💡 Dicas Finais

1. **Comece pequeno**: Use Render.com gratuito
2. **Escale conforme necessário**: Migre para K8s quando precisar
3. **Monitore sempre**: Configure alertas antes de problemas
4. **Faça backups**: Automatize desde o dia 1
5. **Documente tudo**: Mantenha este guia atualizado
