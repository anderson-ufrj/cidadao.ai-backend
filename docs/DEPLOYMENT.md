# 🚀 Guia de Deploy - Cidadão.AI

Este guia detalha as opções de hospedagem e processo de deploy para a plataforma Cidadão.AI.

## 📋 Requisitos do Sistema

### Requisitos Mínimos
- **CPU**: 4 vCPUs
- **RAM**: 8 GB
- **Storage**: 100 GB SSD
- **Bandwidth**: 1 Gbps
- **OS**: Ubuntu 22.04 LTS ou CentOS 8+

### Requisitos Recomendados
- **CPU**: 8 vCPUs
- **RAM**: 16 GB
- **Storage**: 500 GB SSD NVMe
- **Bandwidth**: 10 Gbps
- **OS**: Ubuntu 22.04 LTS

## 🏗️ Opções de Hospedagem

### 1. 🇧🇷 Provedores Nacionais (Recomendado)

#### **Locaweb Cloud**
- **Prós**: Brasileiro, suporte 24/7, datacenter no Brasil
- **Contras**: Limitações em alguns recursos avançados
- **Custo**: R$ 300-800/mês
- **Ideal para**: Startups, projetos governamentais

```bash
# Configuração Locaweb
SERVER_TYPE="cloud-server-8gb"
REGION="sao-paulo"
MONTHLY_COST="R$ 450"
```

#### **UOL HOST Cloud**
- **Prós**: Tradicional, boa infraestrutura, compliance LGPD
- **Contras**: Interface mais antiga
- **Custo**: R$ 400-900/mês
- **Ideal para**: Empresas estabelecidas

#### **DigitalOcean (São Paulo)**
- **Prós**: Simplicidade, documentação excelente, preço competitivo
- **Contras**: Suporte apenas em inglês
- **Custo**: $40-120/mês
- **Ideal para**: Desenvolvedores, startups tech

```bash
# Droplet recomendado
doctl compute droplet create cidadao-ai \
  --size s-4vcpu-8gb \
  --image ubuntu-22-04-x64 \
  --region sao1 \
  --ssh-keys your-ssh-key
```

### 2. ☁️ Provedores Internacionais

#### **AWS (Região São Paulo)**
- **Prós**: Mais completo, escalabilidade infinita, muitos serviços
- **Contras**: Complexidade, custos podem escalar rapidamente
- **Custo**: $60-200/mês
- **Ideal para**: Projetos que precisam escalar globalmente

```yaml
# aws-infrastructure.yml
Resources:
  CidadaoEC2:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.large
      ImageId: ami-0123456789abcdef0  # Ubuntu 22.04
      SecurityGroupIds: 
        - !Ref CidadaoSecurityGroup
      SubnetId: !Ref PublicSubnet
```

#### **Google Cloud Platform**
- **Prós**: IA/ML integrada, créditos iniciais generosos
- **Contras**: Interface complexa para iniciantes
- **Custo**: $50-180/mês

#### **Microsoft Azure**
- **Prós**: Integração com Windows, compliance empresarial
- **Contras**: Curva de aprendizado
- **Custo**: $55-190/mês

### 3. 🏠 Hospedagem Própria (On-Premises)

#### **Servidor Dedicado**
- **Hardware**: Dell PowerEdge R750 ou similar
- **Specs**: 64GB RAM, 2TB NVMe, Intel Xeon
- **Custo**: R$ 15.000-25.000 (inicial) + R$ 500/mês (internet + energia)
- **Ideal para**: Órgãos públicos, dados ultra-sensíveis

## 🚀 Processo de Deploy

### 1. Preparação do Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y \
    docker.io \
    docker-compose \
    git \
    curl \
    htop \
    ufw \
    certbot \
    python3-certbot-nginx

# Configurar firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
```

### 2. Clone e Configuração

```bash
# Clone do projeto
git clone https://github.com/seu-usuario/cidadao-ai.git
cd cidadao-ai

# Configurar ambiente
cp .env.production .env
nano .env  # Editar configurações

# Configurar SSL (Let's Encrypt)
sudo certbot certonly --standalone -d cidadao.ai -d www.cidadao.ai
sudo cp /etc/letsencrypt/live/cidadao.ai/fullchain.pem infrastructure/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/cidadao.ai/privkey.pem infrastructure/nginx/ssl/key.pem
```

### 3. Deploy Automatizado

```bash
# Deploy completo
./scripts/deploy.sh production

# Verificar status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔧 Configurações Avançadas

### Load Balancer (Nginx + Multiple APIs)

```nginx
upstream api_cluster {
    server api1:8000;
    server api2:8000;
    server api3:8000;
    ip_hash;
}
```

### Auto-scaling com Docker Swarm

```bash
# Inicializar swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.swarm.yml cidadao
```

### Backup Automatizado

```bash
# Script de backup (crontab)
0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
```

## 📊 Monitoramento

### Grafana Dashboards
- **Sistema**: CPU, RAM, Disk, Network
- **Aplicação**: Response time, Error rate, Throughput
- **Negócio**: Investigações/dia, Anomalias detectadas

### Alertas Críticos
```yaml
# alerts.yml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 5m
  annotations:
    summary: "Taxa de erro alta na API"
```

## 💰 Análise de Custos

### Breakdown de Custos Mensais

| Componente | AWS | DigitalOcean | Locaweb |
|------------|-----|--------------|---------|
| Servidor | $80 | $48 | R$ 300 |
| Banco | $25 | $15 | R$ 100 |
| CDN | $10 | $5 | R$ 50 |
| SSL | Free | Free | R$ 30 |
| Backup | $15 | $10 | R$ 80 |
| **Total** | **$130** | **$78** | **R$ 560** |

### Otimização de Custos

1. **Reserved Instances** (AWS): 30-60% desconto
2. **Spot Instances**: Para processamento batch
3. **Auto-scaling**: Redimensionar conforme demanda
4. **Compression**: Gzip, Brotli para reduzir bandwidth

## 🛡️ Segurança

### Checklist de Segurança

- [ ] Firewall configurado (UFW/iptables)
- [ ] SSL/TLS com certificados válidos
- [ ] Backup automatizado e testado
- [ ] Logs centralizados
- [ ] Rate limiting ativo
- [ ] WAF configurado (se aplicável)
- [ ] Monitoramento de intrusão
- [ ] Atualizações automáticas de segurança

### Hardening

```bash
# Fail2ban para proteção SSH
sudo apt install fail2ban

# Configurar SSH mais seguro
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
# Port 2222
```

## 📈 Escalabilidade

### Fase 1: Single Server (0-1k usuários)
- 1 servidor com Docker Compose
- PostgreSQL + Redis local
- Nginx para load balancing

### Fase 2: Cluster (1k-10k usuários)
- 3-5 servidores com Docker Swarm
- PostgreSQL replicado
- Redis Cluster
- CDN para assets estáticos

### Fase 3: Microserviços (10k+ usuários)
- Kubernetes cluster
- Databases segregados por domínio
- Message queues (RabbitMQ/Kafka)
- Auto-scaling baseado em métricas

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to server
        run: |
          ssh ${{ secrets.SERVER_HOST }} '
            cd /app/cidadao-ai &&
            git pull origin main &&
            ./scripts/deploy.sh production
          '
```

## 📞 Suporte e Manutenção

### Contatos Recomendados

- **Hospedagem**: [Lista de fornecedores]
- **SSL**: Let's Encrypt (grátis) ou Cloudflare
- **CDN**: Cloudflare, AWS CloudFront
- **Monitoramento**: Uptimerobot, Pingdom

### Cronograma de Manutenção

- **Diário**: Backup automático
- **Semanal**: Atualizações de segurança
- **Mensal**: Review de performance
- **Trimestral**: Upgrade de dependências

---

## 🎯 Recomendação Final

Para a **Cidadão.AI**, recomendamos:

1. **Início**: DigitalOcean São Paulo ($48/mês)
2. **Crescimento**: AWS com auto-scaling
3. **Maturidade**: Infraestrutura própria ou hybrid cloud

O custo inicial de aproximadamente **R$ 200-400/mês** é muito acessível para o valor entregue pela plataforma.

**Próximo passo**: Escolher o provedor e executar `./scripts/deploy.sh production`! 🚀