# 📚 Documentação Técnica - Cidadão.AI

## 🌐 Acesso Online

**📖 Documentação Oficial:** https://anderson-ufrj.github.io/cidadao.ai/docs/

## 🚀 Como visualizar localmente

### Opção 1: Servidor Web Local (Recomendado)
```bash
# Na pasta docs/
python3 -m http.server 8000

# Acesse: http://localhost:8000
```

### Opção 2: Live Server (VS Code)
1. Instale a extensão "Live Server" no VS Code
2. Clique com botão direito no `index.html`
3. Selecione "Open with Live Server"

### Opção 3: Outras Plataformas
- **Hugging Face Spaces:** https://huggingface.co/spaces/neural-thinker/cidadao-ai
- **GitHub Pages:** https://anderson-ufrj.github.io/cidadao.ai/docs/

## 📁 Estrutura dos Arquivos

- `index.html` - Página principal da documentação
- `sections/` - Seções individuais da documentação
  - `overview.html` - Visão geral do sistema
  - `theoretical-foundations.html` - Fundamentos teóricos
  - `system-architecture.html` - Arquitetura do sistema
  - `methodology.html` - Metodologia de pesquisa
  - ... (24 seções no total)

## 🛠️ Funcionalidades

- ✅ Interface responsiva com tema claro/escuro
- ✅ Suporte bilíngue (PT-BR/EN-US)
- ✅ Navegação modular entre seções
- ✅ Rendering de fórmulas matemáticas (MathJax)
- ✅ Destacamento de sintaxe (Highlight.js)
- ✅ Diagramas Mermaid
- ✅ Modo impressão otimizado

## 🔧 Resolução de Problemas

Se você encontrar o erro "Failed to fetch", isso significa que os arquivos precisam ser servidos por um servidor web devido às políticas de CORS dos navegadores modernos.

**Soluções:**
1. Use um servidor web local (ver Opção 1 acima)
2. Use a extensão Live Server do VS Code
3. Acesse a versão online no Hugging Face Spaces