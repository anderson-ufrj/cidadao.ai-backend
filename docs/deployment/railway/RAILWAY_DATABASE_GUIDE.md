# 🚀 Como Adicionar a Coluna no Railway (Passo a Passo)

## 📋 Passo 1: Acessar o Database no Railway

1. Vá para o Railway Dashboard: https://railway.app/
2. Clique no seu projeto **cidadao.ai**
3. Clique no serviço **PostgreSQL** (Database)
4. Clique na aba **"Data"** ou **"Query"**

## 💻 Passo 2: Executar os Comandos SQL

Copie e cole os comandos abaixo no Query Editor do Railway:

```sql
-- Adicionar a coluna investigation_metadata
ALTER TABLE investigations
ADD COLUMN IF NOT EXISTS investigation_metadata JSONB DEFAULT '{}';

-- Adicionar comentário
COMMENT ON COLUMN investigations.investigation_metadata IS 'Additional metadata for the investigation';

-- Criar índice para performance
CREATE INDEX IF NOT EXISTS ix_investigations_metadata
ON investigations USING gin (investigation_metadata);
```

## ✅ Passo 3: Verificar se funcionou

Execute este comando para verificar:

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'investigations'
AND column_name = 'investigation_metadata';
```

Você deve ver algo como:
```
column_name              | data_type | is_nullable | column_default
investigation_metadata   | jsonb     | YES         | '{}'::jsonb
```

## 🎯 Passo 4: Testar a Investigação

Depois de adicionar a coluna, volte aqui e me avise! Vou rodar um teste completo para verificar se as investigações com Maritaca AI estão funcionando.

## 🔍 Troubleshooting

Se der algum erro:

1. **Erro de permissão**: Certifique-se de estar usando o usuário correto do PostgreSQL
2. **Coluna já existe**: Se aparecer erro dizendo que a coluna já existe, tudo bem! Use:
   ```sql
   ALTER TABLE investigations
   ADD COLUMN IF NOT EXISTS investigation_metadata JSONB DEFAULT '{}';
   ```
3. **Erro de sintaxe**: Verifique se copiou todo o comando corretamente

---

## 📝 Comandos Individuais (caso prefira executar um por vez)

### 1. Adicionar coluna:
```sql
ALTER TABLE investigations
ADD COLUMN IF NOT EXISTS investigation_metadata JSONB DEFAULT '{}';
```

### 2. Adicionar comentário:
```sql
COMMENT ON COLUMN investigations.investigation_metadata
IS 'Additional metadata for the investigation';
```

### 3. Criar índice:
```sql
CREATE INDEX IF NOT EXISTS ix_investigations_metadata
ON investigations USING gin (investigation_metadata);
```

---

**Dica**: No Railway, você pode executar todos os comandos de uma vez colando tudo no Query Editor e clicando em "Run" ou "Execute".
