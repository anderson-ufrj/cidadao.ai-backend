# ÍNDICE DE DOCUMENTAÇÃO INTERNA - CIDADÃO.AI

**Autor:** Anderson Henrique da Silva  
**Data:** 20 de Setembro de 2025  
**Hora:** 17:52:00 (Horário de São Paulo, Brasil)  
**Local:** São Paulo, SP, Brasil

---

## ESTRUTURA DE DOCUMENTAÇÃO

### 1. RELATÓRIOS INTERNOS
**Local:** `/docs/internal/`
- `RELATORIO_TRABALHO_2025_09_20.md` - Relatório completo da resolução de problemas HuggingFace

### 2. INTEGRAÇÃO FRONTEND
**Local:** `/docs/frontend-integration/`
- `FRONTEND_CHAT_INTEGRATION.md` - Guia de integração do chat
- `FRONTEND_INTEGRATION.md` - Integração geral do frontend  
- `FRONTEND_STABLE_INTEGRATION.md` - Integração com endpoint estável

### 3. RESOLUÇÃO DE PROBLEMAS
**Local:** `/docs/troubleshooting/`
- `EMERGENCY_SOLUTION.md` - Solução de emergência para chat
- `FIX_HUGGINGFACE_DEPLOYMENT.md` - Correções do deployment HF

### 4. OTIMIZAÇÃO
**Local:** `/docs/optimization/`
- `MARITACA_OPTIMIZATION_GUIDE.md` - Guia de otimização com Maritaca AI

### 5. ANÁLISES E RELATÓRIOS
**Local:** `/docs/reports/`
- `CODEBASE_ANALYSIS_REPORT.md` - Análise completa do código base

### 6. SCRIPTS DE DEBUG
**Local:** `/scripts/debug/`
- `debug_drummond_import.py` - Debug de imports do Drummond
- `debug_hf_error.py` - Debug de erros HuggingFace

### 7. BACKUPS
**Local:** `/backups/`
- Arquivos `app_*.py` - Versões anteriores do app.py

### 8. TESTES DE INTEGRAÇÃO
**Local:** `/tests/integration/`
- `test_hf_chat.py` - Testes do chat HuggingFace
- `test_chat_detailed.py` - Testes detalhados
- `test_stable_endpoint.py` - Testes do endpoint estável
- Outros arquivos de teste movidos da raiz

---

## NOTAS IMPORTANTES

### Confidencialidade
- Esta documentação é **INTERNA** e **NÃO DEVE** ser commitada no GitHub
- Adicionar `/docs/internal/` ao `.gitignore`
- Manter backups locais apenas

### Organização
- Todos os arquivos foram organizados em diretórios apropriados
- Estrutura segue padrões de organização de projetos
- Facilita manutenção e localização de documentos

### Manutenção
- Atualizar este índice sempre que novos documentos forem adicionados
- Manter timestamp e autoria em todos os documentos
- Revisar e limpar backups periodicamente

---

## COMANDOS ÚTEIS

### Para listar documentação interna
```bash
find docs/internal -name "*.md" -type f
```

### Para criar backup da documentação
```bash
tar -czf docs_backup_$(date +%Y%m%d).tar.gz docs/internal/
```

### Para verificar o que não está no git
```bash
git status --ignored
```

---

**Última Atualização:** 20/09/2025 17:52:00 -03:00  
**Por:** Anderson Henrique da Silva

*Este documento deve ser mantido atualizado sempre que houver mudanças na estrutura de documentação.*