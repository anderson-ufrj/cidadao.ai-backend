# 🔑 Guia de Configuração de Tokens - Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-03

## ✅ Token Dados.gov.br Configurado!

### 📊 Seu Token

```
Token: ***REMOVED-JWT***
Usuário: ANDERSON HENRIQUE DA SILVA (@andersonhs90@hotmail.com)
CPF: 109.472.466-14
Criado em: 02/10/2025 15:17:09
```

### ✅ Já Configurado no `.env`

```bash
DADOS_GOV_API_KEY=***REMOVED-JWT***
```

## 🎯 Tokens Configurados

| Token | Status | Observação |
|-------|--------|------------|
| **DADOS_GOV_API_KEY** | ✅ Configurado | Token JWT do Portal Brasileiro de Dados Abertos |
| **TRANSPARENCY_API_KEY** | ✅ Configurado | Chave ***REDACTED-TRANSPARENCY-KEY*** |
| **GROQ_API_KEY** | ⚠️ Pendente | Necessário para agentes IA funcionarem |

## 🚀 Próximo Passo: Configurar GROQ

O **único token faltante** é o GROQ_API_KEY para os agentes IA funcionarem.

### Como Obter (GRÁTIS):

1. **Acesse**: https://console.groq.com/
2. **Crie uma conta** (grátis)
3. **Vá em "API Keys"**
4. **Clique "Create API Key"**
5. **Copie a chave** (começa com `gsk_`)

### Adicione no `.env`:

```bash
GROQ_API_KEY=gsk_sua_chave_aqui_xxxxxxxxxxxxx
```

### Limites Gratuitos:

- ✅ 30 requests/minuto
- ✅ ~14,400 tokens/minuto
- ✅ Modelos rápidos: Llama 3, Mixtral, Gemma

## 📦 O Que Cada Token Faz

### 1. DADOS_GOV_API_KEY (dados.gov.br)

**Permite acesso a**:
- 📊 **16,000+ datasets** de dados governamentais abertos
- 🏛️ **Organizações** do governo federal
- 📑 **Recursos** e arquivos de dados públicos
- 🏷️ **Tags e categorias** de datasets

**Usado pelos agentes**:
- 🏜️ **Lampião** - Análise regional com dados IBGE
- 🔍 **Zumbi** - Detecção de anomalias em dados públicos
- 📊 **Anita** - Análise de padrões em séries temporais
- 📝 **Tiradentes** - Geração de relatórios com dados reais

**Endpoints disponíveis**:
```python
# Buscar datasets
GET /api/3/action/package_search?q=educação

# Detalhes de dataset
GET /api/3/action/package_show?id={dataset_id}

# Listar organizações
GET /api/3/action/organization_list

# Listar tags
GET /api/3/action/tag_list
```

### 2. TRANSPARENCY_API_KEY (Portal da Transparência)

**Limitações conhecidas**:
- ✅ 22% dos endpoints funcionam
- ❌ 78% retornam 403 Forbidden

**Endpoints que funcionam**:
```python
# Contratos (com codigoOrgao)
GET /contratos?codigoOrgao=123456

# Servidores (por CPF)
GET /servidores?cpf=12345678900
```

### 3. GROQ_API_KEY (LLM para Agentes)

**Usado para**:
- 🤖 Inteligência dos 13 agentes
- 💬 Chat conversacional
- 📊 Análise de dados com IA
- 📝 Geração de relatórios
- 🎯 Roteamento semântico

## 🧪 Testando a Configuração

### Teste 1: Verificar .env

```bash
grep "DADOS_GOV_API_KEY" .env
grep "TRANSPARENCY_API_KEY" .env
grep "GROQ_API_KEY" .env
```

### Teste 2: Executar o sistema

```bash
make run-dev
# ou
python -m src.api.app
```

### Teste 3: Acessar documentação

```
http://localhost:8000/docs
```

### Teste 4: Testar endpoint dados.gov.br

```bash
curl http://localhost:8000/api/v1/dados-gov/datasets/search?q=educacao&rows=5
```

## 🔒 Segurança

### ⚠️ NUNCA COMMITAR O .ENV!

O `.env` está no `.gitignore`. Verifique:

```bash
git check-ignore .env
# Deve retornar: .env
```

### 🔐 Regenerar Token

Se precisar regenerar o token dados.gov.br:

1. Acesse: https://dados.gov.br (logado)
2. Vá em "Minha Conta"
3. Seção "TOKEN API"
4. Clique "Regerar"
5. Copie o novo token
6. Atualize no `.env`

## ✅ Checklist Final

- [x] Token dados.gov.br obtido
- [x] Token dados.gov.br configurado no .env
- [x] Token Portal da Transparência configurado
- [ ] Token GROQ obtido
- [ ] Token GROQ configurado no .env
- [ ] Sistema testado com `make run-dev`
- [ ] Agentes respondendo corretamente

## 🎉 Pronto!

Com todos os tokens configurados, você terá:

1. ✅ **13 agentes IA** operacionais
2. ✅ **Acesso a 16,000+ datasets** do governo
3. ✅ **Análises regionais** com dados IBGE
4. ✅ **Detecção de anomalias** em dados reais
5. ✅ **Chat conversacional** inteligente
6. ✅ **Relatórios automáticos** com dados governamentais

---

**Dúvidas?** Consulte:
- [Documentação dados.gov.br](https://dados.gov.br/pagina/sobre-o-catalogo)
- [Documentação GROQ](https://console.groq.com/docs)
- [README do projeto](./README.md)
