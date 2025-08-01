---
title: "Início Rápido"
sidebar_position: 2
---

# ⚡ Início Rápido

Guia para configurar e executar o Cidadão.AI Backend em sua máquina local.

## 📋 Pré-requisitos

- **Python 3.11+**
- **PostgreSQL 16**
- **Redis 7**
- **Docker** (opcional)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/anderson-ufrj/cidadao.ai-backend.git
cd cidadao.ai-backend
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas configurações
```

### 4. Execute as migrações

```bash
python -m alembic upgrade head
```

### 5. Inicie o servidor

```bash
uvicorn src.api.app:app --reload
```

## 🌐 Acesso

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 Próximos Passos

- [Arquitetura do Sistema](./architecture/overview.md)
- [Configuração Avançada](./configuration.md)
- [Guia de Desenvolvimento](./development.md)