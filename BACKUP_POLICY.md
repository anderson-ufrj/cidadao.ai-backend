# 🛡️ BACKUP POLICY - Cidadão.AI Backend

## ⚠️ REGRA FUNDAMENTAL: NUNCA COMMITAR BACKUPS

### 📋 Política de Backups

1. **Backups são SEMPRE locais**
   - Nunca devem ser commitados no Git
   - Nunca devem ir para GitHub
   - Nunca devem ir para HuggingFace

2. **Padrões Bloqueados**
   - `*backup*` - Qualquer arquivo/pasta com "backup"
   - `*.bak` - Arquivos de backup
   - `*.old` - Arquivos antigos
   - `*.orig` - Arquivos originais
   - `*.tmp` / `*.temp` - Arquivos temporários
   - Arquivos com timestamp: `*-20240124*`

3. **Proteções Implementadas**
   - ✅ `.gitignore` - Máxima proteção com 50+ padrões
   - ✅ `.hfignore` - Proteção no HuggingFace Spaces
   - ✅ `pre-commit hook` - Verificação automática antes de commits
   - ✅ Documentação clara sobre a política

### 🔧 Como Fazer Backups Corretamente

```bash
# CORRETO - Backup local
cp -r docs docs-backup-$(date +%Y%m%d-%H%M%S)

# ERRADO - Nunca faça commit de backups
git add docs-backup-*  # NUNCA FAÇA ISSO!
```

### 🚨 Se Você Encontrar Backups no Repositório

1. **Remova imediatamente**:
   ```bash
   git rm -r pasta-backup/
   git commit -m "chore: remove backup files from repository"
   git push
   ```

2. **Verifique se há mais**:
   ```bash
   git ls-tree -r HEAD | grep -E "backup|\.bak|\.old"
   ```

3. **Adicione ao .gitignore** se necessário

### 📊 Checklist de Verificação

Antes de cada commit, verifique:
- [ ] Não há pastas `*backup*` no staging
- [ ] Não há arquivos `.bak`, `.old`, `.orig`
- [ ] Não há arquivos com timestamp
- [ ] Não há arquivos temporários
- [ ] O pre-commit hook está ativo

### 🛡️ Proteções Automáticas

1. **Pre-commit Hook**: Bloqueia commits com backups
2. **CI/CD**: Pode ser configurado para rejeitar PRs com backups
3. **Code Review**: Sempre verificar se há backups em PRs

### 📝 Exceções

**NENHUMA!** Não há exceções para esta regra. Backups NUNCA devem estar no repositório.

---

**Última atualização**: 24 de Janeiro de 2025  
**Status**: ✅ POLÍTICA ATIVA E ENFORCED