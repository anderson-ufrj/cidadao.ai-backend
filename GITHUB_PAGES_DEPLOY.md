# 🚀 Deploy da Documentação no GitHub Pages

## 📋 Pré-requisitos

1. **Repositório no GitHub**: `anderson-ufrj/cidadao.ai`
2. **Pasta docs/** preparada com todos os arquivos
3. **Permissões de administrador** no repositório

## 🛠️ Passos para Deploy

### 1. Configurar GitHub Pages no Repositório

1. Vá para **Settings** → **Pages** no seu repositório GitHub
2. Em **Source**, selecione:
   - **Deploy from a branch**
   - **Branch**: `main` (ou `master`)
   - **Folder**: `/docs`
3. Clique em **Save**

### 2. Verificar Arquivos Necessários

Certifique-se que existem na pasta `docs/`:

```
docs/
├── index.html                 # ✅ Página principal
├── _config.yml               # ✅ Configuração Jekyll
├── .nojekyll                 # ✅ Desabilita Jekyll para arquivos _
├── _headers                  # ✅ Cabeçalhos de segurança
├── README.md                 # ✅ Documentação da pasta
└── sections/                 # ✅ 24 seções HTML
    ├── overview.html
    ├── theoretical-foundations.html
    ├── methodology.html
    ├── system-architecture.html
    └── ... (mais 20 arquivos)
```

### 3. Commit e Push

```bash
# No diretório raiz do projeto
git add docs/
git commit -m "feat: add complete technical documentation for GitHub Pages

- ✅ 24 comprehensive sections with academic content
- ✅ Responsive design with Brazilian theme
- ✅ Bilingual support (PT-BR/EN-US)
- ✅ Dark/light mode toggle
- ✅ MathJax for mathematical formulas
- ✅ Mermaid diagrams support
- ✅ GitHub Pages optimized paths
- ✅ SEO and security headers

🔗 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

### 4. Aguardar Deploy (2-5 minutos)

O GitHub Pages irá automaticamente:
1. Detectar mudanças na pasta `docs/`
2. Processar os arquivos
3. Publicar em: `https://anderson-ufrj.github.io/cidadao.ai/docs/`

### 5. Verificar Deploy

1. **Status**: Settings → Pages → veja "Your site is published at..."
2. **Actions**: Aba "Actions" para ver o build em progresso
3. **Teste**: Acesse a URL gerada

## 🔧 Configurações Específicas Implementadas

### ✅ Detecção Automática de Ambiente
```javascript
// GitHub Pages detection
if (window.location.hostname === 'anderson-ufrj.github.io' && 
    window.location.pathname.includes('/cidadao.ai/')) {
    basePath = '/cidadao.ai/docs/';
}
```

### ✅ URLs Canônicas
```html
<link rel="canonical" href="https://anderson-ufrj.github.io/cidadao.ai/docs/">
```

### ✅ Meta Tags Otimizadas
```html
<meta property="og:url" content="https://anderson-ufrj.github.io/cidadao.ai/docs/">
<meta name="robots" content="index, follow">
```

### ✅ Configuração Jekyll
```yaml
# _config.yml
baseurl: "/cidadao.ai"
url: "https://anderson-ufrj.github.io"
```

## 🎯 URLs Finais

- **Documentação Principal**: https://anderson-ufrj.github.io/cidadao.ai/docs/
- **Repositório**: https://github.com/anderson-ufrj/cidadao.ai
- **Status Pages**: https://github.com/anderson-ufrj/cidadao.ai/settings/pages

## 🐛 Resolução de Problemas

### Problema: 404 Not Found
- **Causa**: Paths incorretos ou arquivos não commitados
- **Solução**: Verificar se todos os arquivos estão na pasta `docs/`

### Problema: Seções não carregam
- **Causa**: CORS ou paths incorretos
- **Solução**: A detecção automática de ambiente deve resolver

### Problema: Styles não aplicados
- **Causa**: CSP ou recursos externos
- **Solução**: Verificar console do navegador para erros

### Problema: Deploy não acontece
- **Causa**: Configuração incorreta do Pages
- **Solução**: Re-configurar em Settings → Pages

## 📊 Métricas de Sucesso

Após deploy bem-sucedido, você deve ter:
- ✅ **24 seções** carregando corretamente
- ✅ **Navegação fluida** entre seções
- ✅ **Temas claro/escuro** funcionando
- ✅ **Seletor de idioma** (PT-BR/EN-US)
- ✅ **Matemática renderizada** (MathJax)
- ✅ **Código destacado** (Highlight.js)
- ✅ **Diagramas** (Mermaid)
- ✅ **Design responsivo** em dispositivos móveis

## 🚀 Próximos Passos

1. **Testar em diferentes dispositivos**
2. **Verificar SEO** com Google Search Console
3. **Monitorar analytics** (se configurado)
4. **Compartilhar URL** da documentação oficial

---

**🎉 Sua documentação estará disponível em:** 
**https://anderson-ufrj.github.io/cidadao.ai/docs/**