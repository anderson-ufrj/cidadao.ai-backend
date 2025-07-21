# 📚 Documentação Técnica - Cidadão.AI

## 🌐 Acesso

**📖 Documentação Online**: https://anderson-ufrj.github.io/cidadao.ai/docs/

## 🏃‍♂️ Visualização Local

```bash
# Na pasta docs/
python3 -m http.server 8000
# Acesse: http://localhost:8000
```

## 📁 Estrutura

- `index.html` - Interface principal da documentação
- `sections/` - Seções técnicas detalhadas
- `_config.yml` - Configuração Jekyll para GitHub Pages

## 🔧 Desenvolvimento

Para editar a documentação:

1. Edite os arquivos HTML em `sections/`
2. Mantenha o padrão bilíngue (PT-BR/EN-US)
3. Teste localmente antes de commitar
4. A documentação é automaticamente publicada no GitHub Pages

## 🚀 Deploy

A documentação é automaticamente publicada no GitHub Pages quando alterações são feitas na pasta `docs/` do branch `main`.