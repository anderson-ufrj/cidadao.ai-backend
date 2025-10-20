# Debug & Test Scripts

Scripts para diagnóstico e teste do sistema em desenvolvimento e produção.

## 📋 Scripts de Verificação

### Database
- `check_database.py` - Verifica conexão e schema do PostgreSQL
- `fix_database.py` - Aplica correções de schema
- `check_investigation.py` - Verifica investigações no banco

### LLM Configuration
- `check_llm_config.py` - Verifica configuração do Maritaca AI / LLMs

### Agents
- `test_agent_directly.py` - Testa agentes diretamente
- `test_agent_direct.py` - Teste de agente sem API

### Data Collection
- `test_data_collection.py` - Testa coleta de APIs de transparência
- `test_debug_endpoints.py` - Testa endpoints /debug/

### Monitoring
- `monitor_investigation.py` - Monitora investigação em tempo real
- `test_single_investigation.py` - Testa investigação completa end-to-end (na raiz)

## 🚀 Como Usar

### Teste Rápido em Produção
```bash
# Da raiz do projeto
python test_single_investigation.py
```

### Verificar Banco de Dados
```bash
python scripts/debug/check_database.py
```

### Verificar LLM
```bash
python scripts/debug/check_llm_config.py
```

## 📝 Notas

- Todos os scripts usam environment variables do .env
- Para produção, apontam para Railway
- Sempre teste localmente primeiro antes de rodar em produção
