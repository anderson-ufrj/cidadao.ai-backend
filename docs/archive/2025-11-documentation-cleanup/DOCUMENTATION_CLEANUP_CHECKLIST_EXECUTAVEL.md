# ✅ CHECKLIST EXECUTÁVEL - LIMPEZA DA DOCUMENTAÇÃO

**Projeto**: Cidadão.AI Backend
**Data**: 17 de Novembro de 2025
**Analista**: Anderson Henrique da Silva
**Tempo Total**: 10 horas (3 semanas)
**Relatório Completo**: `docs/project/reports/DOCUMENTATION_FORENSIC_ANALYSIS_2025_11_17.md`

---

## 🚀 INÍCIO RÁPIDO (1 HORA - FAÇA AGORA!)

Execute os comandos abaixo **copy-paste direto no terminal**. Total: 60 minutos.

### ☑️ Passo 1: Criar estrutura (2 min)

```bash
mkdir -p docs/archive/2025-11-documentation-cleanup/roadmaps
mkdir -p docs/archive/2025-11-documentation-cleanup/status-reports
```

- [ ] Executado

---

### ☑️ Passo 2: Arquivar roadmaps (3 min)

```bash
# Arquivar roadmaps TCC
mv docs/project/ROADMAP_TCC_2025.md docs/archive/2025-11-documentation-cleanup/roadmaps/
mv docs/project/ROADMAP_TCC_DEZ_2025.md docs/archive/2025-11-documentation-cleanup/roadmaps/

# Criar README
cat > docs/archive/2025-11-documentation-cleanup/roadmaps/README.md << 'EOF'
# Roadmaps Arquivados - Novembro 2025

**Data**: 17/Nov/2025
**Motivo**: Consolidação de documentação

## Roadmap Oficial Atual

**Único roadmap válido**: `docs/project/ROADMAP_OFFICIAL_2025.md`

## Arquivos Nesta Pasta

- `ROADMAP_TCC_2025.md` - Versão focada em TCC/pesquisa
- `ROADMAP_TCC_DEZ_2025.md` - Versão de dezembro 2025

## Por Que Foram Arquivados

- Causavam confusão sobre qual roadmap seguir
- `ROADMAP_OFFICIAL_2025.md` foi marcado como "VALIDADO E APROVADO"
- Mantemos apenas um roadmap oficial para clareza

EOF

echo "✅ Roadmaps arquivados!"
```

- [ ] Executado

---

### ☑️ Passo 3: Arquivar status files (5 min)

```bash
# Arquivar status files antigos
mv docs/project/current/CURRENT_STATUS_2025_10.md docs/archive/2025-11-documentation-cleanup/status-reports/ 2>/dev/null || true
mv docs/project/current/CURRENT_STATUS.md docs/archive/2025-11-documentation-cleanup/status-reports/ 2>/dev/null || true
mv docs/project/current/IMPLEMENTATION_REALITY.md docs/archive/2025-11-documentation-cleanup/status-reports/ 2>/dev/null || true
mv docs/project/current/MILESTONE_16_AGENTS_COMPLETE_2025_10_27.md docs/archive/2025-11-documentation-cleanup/status-reports/ 2>/dev/null || true
mv docs/project/current/QUICK_STATUS.md docs/archive/2025-11-documentation-cleanup/status-reports/ 2>/dev/null || true
mv docs/project/current/TRANSPARENCY_MAP_IMPLEMENTATION_STATUS.md docs/archive/2025-11-documentation-cleanup/status-reports/ 2>/dev/null || true
mv docs/project/STATUS_ATUAL_2025_11.md docs/archive/2025-11-documentation-cleanup/status-reports/ 2>/dev/null || true

# Criar README
cat > docs/archive/2025-11-documentation-cleanup/status-reports/README.md << 'EOF'
# Status Reports Arquivados - Novembro 2025

**Data**: 17/Nov/2025
**Motivo**: Consolidação de status reports

## Status Oficial Atual

**Único status válido**: `docs/project/STATUS_ATUAL_2025_11_14.md`

## Arquivos Nesta Pasta

- `CURRENT_STATUS_2025_10.md` - Status de outubro
- `CURRENT_STATUS.md` - Status sem data específica
- `IMPLEMENTATION_REALITY.md` - Realidade de implementação (outdated)
- `MILESTONE_16_AGENTS_COMPLETE_2025_10_27.md` - Milestone de 27/out
- `QUICK_STATUS.md` - Status rápido (sem data)
- `TRANSPARENCY_MAP_IMPLEMENTATION_STATUS.md` - Status do mapa
- `STATUS_ATUAL_2025_11.md` - Status de nov (substituído por 14/nov)

## Por Que Foram Arquivados

- Causavam confusão sobre status atual do projeto
- Informações desatualizadas (outubro ou sem data clara)
- Mantemos apenas `STATUS_ATUAL_2025_11_14.md` como fonte única da verdade

EOF

echo "✅ Status files arquivados!"
```

- [ ] Executado

---

### ☑️ Passo 4: Verificar métricas REAIS (10 min)

```bash
# Análise de testes
echo "=== ANÁLISE DE TESTES - $(date '+%Y-%m-%d %H:%M') ===" > test_analysis_2025_11_17.txt
echo "" >> test_analysis_2025_11_17.txt

echo "1. Total de arquivos Python em tests/:" >> test_analysis_2025_11_17.txt
find tests/ -name "*.py" -type f | tee -a test_files_all.txt | wc -l >> test_analysis_2025_11_17.txt
echo "" >> test_analysis_2025_11_17.txt

echo "2. Arquivos test_*.py:" >> test_analysis_2025_11_17.txt
find tests/ -name "test_*.py" -type f | tee -a test_files_test.txt | wc -l >> test_analysis_2025_11_17.txt
echo "" >> test_analysis_2025_11_17.txt

echo "3. Arquivos Python excluindo __init__:" >> test_analysis_2025_11_17.txt
find tests/ -name "*.py" -type f ! -name "__*" | tee -a test_files_clean.txt | wc -l >> test_analysis_2025_11_17.txt
echo "" >> test_analysis_2025_11_17.txt

echo "=== EXECUTANDO COBERTURA ===" >> test_analysis_2025_11_17.txt
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest --cov=src --cov-report=term -q 2>&1 | tail -30 >> test_analysis_2025_11_17.txt

# Mostrar resultado
cat test_analysis_2025_11_17.txt

echo ""
echo "✅ Análise salva em test_analysis_2025_11_17.txt"
echo "📊 Use os números acima para atualizar a documentação"
```

- [ ] Executado
- [ ] **ANOTAR AQUI OS NÚMEROS REAIS**:
  - Total arquivos: ______
  - Test files: ______
  - Coverage %: ______

---

### ☑️ Passo 5: Atualizar ROADMAP com aviso (5 min)

```bash
# Backup
cp docs/project/ROADMAP_OFFICIAL_2025.md docs/project/ROADMAP_OFFICIAL_2025.md.backup

# Adicionar aviso no topo (após o header YAML)
# FAZER MANUALMENTE: abrir docs/project/ROADMAP_OFFICIAL_2025.md e adicionar após linha 8:
```

**Adicione manualmente** após a linha 8 do `ROADMAP_OFFICIAL_2025.md`:

```markdown
---

> **⚠️ ATENÇÃO - ÚNICO ROADMAP OFICIAL**
>
> Este é o **ÚNICO roadmap válido** do projeto Cidadão.AI.
>
> **Roadmaps arquivados**: `docs/archive/2025-11-documentation-cleanup/roadmaps/`
>
> Qualquer outro roadmap no repositório deve ser considerado **arquivado e inválido**.
>
> **Última atualização**: 17 de Novembro de 2025

---
```

- [ ] Aviso adicionado manualmente ao ROADMAP

---

### ☑️ Passo 6: Atualizar STATUS com números reais (10 min)

Abrir `docs/project/STATUS_ATUAL_2025_11_14.md` e fazer as seguintes alterações:

**Mudança 1** - Linha 59 (Test Files):
```markdown
# ANTES:
| **Test Files** | 98 files | ✅ Cobertura ampla |

# DEPOIS (usar número do Passo 4):
| **Test Files** | ___ files | ✅ Cobertura ampla |
```

**Mudança 2** - Linha 57 (Coverage Geral - se diferente):
```markdown
| **Geral** | __.__% | 🟡 Próximo de 80% |
```

**Mudança 3** - Adicionar após linha 320:
```markdown
---

> **📊 Últimas Métricas Verificadas**
>
> - **Data**: 17 de Novembro de 2025
> - **Testes executados**: Sim
> - **Cobertura verificada**: Sim
> - **Arquivo de análise**: `test_analysis_2025_11_17.txt`
>
> Este status é atualizado semanalmente. Próxima atualização: 24/Nov/2025.

---
```

- [ ] STATUS atualizado com números reais

---

### ☑️ Passo 7: Atualizar CLAUDE.md com Maritaca (15 min)

Abrir `~/.claude/CLAUDE.md` e **substituir** toda a seção de Backend (.env):

**SUBSTITUIR ISTO**:
```markdown
# Backend (.env)
GROQ_API_KEY=your-key              # LLM provider
```

**POR ISTO**:
```markdown
# Backend (.env)

## LLM Provider (ATUALIZADO EM OUT/2025)

# Primary Provider - Maritaca AI (Brazilian Portuguese optimized)
LLM_PROVIDER=maritaca
MARITACA_API_KEY=<your-key>              # Get at https://maritaca.ai
MARITACA_MODEL=sabia-3.1                 # Latest (default) or sabiazinho-3 (faster)

# Backup Provider (optional, auto-fallback)
ANTHROPIC_API_KEY=<your-key>             # Claude Sonnet 4.5
ANTHROPIC_MODEL=claude-sonnet-4-20250514

## ⚠️ BREAKING CHANGE (October 2025)
# OLD: GROQ_API_KEY (deprecated, removed)
# NEW: MARITACA_API_KEY (current)
# Reason: Better Brazilian Portuguese support and cultural context understanding
```

- [ ] CLAUDE.md atualizado

---

### ☑️ Passo 8: Commit das mudanças (10 min)

```bash
# Adicionar tudo
git add docs/archive/2025-11-documentation-cleanup/
git add docs/project/ROADMAP_OFFICIAL_2025.md
git add docs/project/STATUS_ATUAL_2025_11_14.md
git add test_analysis_2025_11_17.txt
git add DOCUMENTATION_CLEANUP_CHECKLIST_EXECUTAVEL.md
git add docs/project/reports/DOCUMENTATION_FORENSIC_ANALYSIS_2025_11_17.md

# Verificar mudanças
git status

# Commit
git commit -m "docs: archive outdated documentation and fix critical discrepancies

Critical fixes completed:
- Archive conflicting roadmaps (ROADMAP_TCC_*.md → archive/)
- Archive old status files (keep only STATUS_ATUAL_2025_11_14.md)
- Fix test coverage metrics (153 files found vs 98 documented)
- Update LLM provider docs (Maritaca replaces deprecated GROQ)
- Add single source of truth note to ROADMAP_OFFICIAL
- Create archive structure for 2025-11 cleanup

Impact:
- Eliminates confusion about which roadmap/status to follow
- Corrects test metrics (56% discrepancy identified)
- Updates setup instructions for Maritaca migration
- Improves developer onboarding experience

Files archived: 9 files
Files updated: 4 files
New documentation: 3 files

Based on forensic analysis: DOCUMENTATION_FORENSIC_ANALYSIS_2025_11_17.md"
```

- [ ] Commit realizado

```bash
# Se quiser fazer push
# git push origin main
```

- [ ] (Opcional) Push realizado

---

## ✅ CHECKPOINT: INÍCIO RÁPIDO COMPLETO!

**Parabéns! 🎉** Você completou o Início Rápido (1 hora).

**Problemas críticos resolvidos**:
- ✅ Conflito de roadmaps (3 → 1 oficial)
- ✅ Proliferação de status (9 → 1 atual)
- ✅ Métricas verificadas e corrigidas
- ✅ Setup atualizado (Maritaca)

**Próximos passos opcionais**: Continue com as 3 semanas abaixo se quiser documentação perfeita.

---

## 📅 SEMANA 1: REFINAMENTO (1h adicional - opcional)

### Investigar drummond_simple.py (20 min)

```bash
# Ver arquivo
cat src/agents/drummond_simple.py

# Histórico
git log --oneline --follow src/agents/drummond_simple.py | head -5

# Onde é usado
grep -r "drummond_simple" src/ tests/ --include="*.py"
```

**Decisão**:
- [ ] Se não usado → Remover
- [ ] Se usado → Documentar como variante

### Padronizar terminologia de agentes (20 min)

**Escolher UMA opção**:
- [ ] **Opção A**: "17 agentes (incluindo Deodoro como base framework)"
- [ ] **Opção B**: "16 agentes especializados + 1 base framework = 17 total"

**Atualizar estes arquivos** com a opção escolhida:
- [ ] `docs/project/STATUS_ATUAL_2025_11_14.md`
- [ ] `CLAUDE.md`
- [ ] `cidadao.ai-backend/CLAUDE.md`
- [ ] `docs/agents/README.md`

### Criar CONTRIBUTING.md (20 min)

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to Cidadão.AI

## Quick Start

1. Fork & clone
2. `make install-dev`
3. `cp .env.example .env` (add your API keys)
4. Make changes
5. `make check` (format + lint + test)
6. Commit with conventional commits
7. Open PR

## Commit Format

- `feat(scope): description`
- `fix(scope): description`
- `docs(scope): description`

## Testing

- Minimum 80% coverage
- All tests must pass
- Run: `JWT_SECRET_KEY=test SECRET_KEY=test make test`

## Questions?

Open an issue or email: anderson@cidadao.ai
EOF

git add CONTRIBUTING.md
git commit -m "docs: add contribution guidelines"
```

- [ ] CONTRIBUTING.md criado

---

## 📅 SEMANA 2-3: DOCUMENTAÇÃO COMPLETA (opcional, 7h)

Se quiser documentação **100% perfeita**, continue aqui:

### Criar documentos essenciais (3h)

- [ ] `TESTING.md` - Guia de testes (30 min)
- [ ] `docs/ARCHITECTURE_OVERVIEW.md` - Visão geral (1h)
- [ ] `SECURITY.md` - Política de segurança (30 min)
- [ ] `API_CHANGELOG.md` - Breaking changes (30 min)
- [ ] `docs/api/API_MASTER_INDEX.md` - Índice de APIs (30 min)

### Melhorias organizacionais (4h)

- [ ] Adicionar headers com data em todos os .md (2h)
- [ ] Criar `docs/archive/INDEX.md` (1h)
- [ ] Corrigir typos e links quebrados (1h)

---

## 🎯 RESUMO

| Fase | Tempo | Status |
|------|-------|--------|
| **Início Rápido** | 1h | [ ] |
| **Semana 1** | 1h | [ ] |
| **Semana 2-3** | 7h | [ ] |
| **TOTAL** | 9h | [ ] |

---

**Recomendação**: Faça o Início Rápido HOJE (1h). As outras fases são opcionais.

**Próxima ação**: Ir para o Passo 1 e começar! 🚀
