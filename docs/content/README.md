# 📁 Content Directory

Esta pasta contém o conteúdo modular para o site de documentação.

## Estrutura

```
content/
└── sections/
    ├── math-foundations.html     # Fundamentos matemáticos PhD-level
    ├── xai-algorithms.html       # Algoritmos XAI avançados
    └── [future-sections].html    # Futuras seções modulares
```

## Como Adicionar Nova Seção

1. Criar arquivo HTML na pasta `sections/`
2. Usar paths relativos para assets (ex: `../../assets/img/`)
3. Incluir estilos inline ou em tag `<style>`
4. Adicionar placeholder no `index.html` se necessário
5. ContentManager carregará automaticamente

## Formato dos Arquivos

```html
<!-- NÃO incluir tags html, head, body -->
<!-- Começar direto com conteúdo -->

<h3 style="...">Título da Seção</h3>

<style>
/* Estilos específicos desta seção */
</style>

<!-- Conteúdo da seção -->
```

## Paths Relativos

- CSS: `../../assets/css/main.css`
- Imagens: `../../assets/img/example.png`
- JS: `../../assets/js/script.js`