#!/usr/bin/env python3
"""
Script de limpeza final dos arquivos migrados
Remove CSS inline, JavaScript e HTML residual que quebra o parsing MDX
"""

import os
import re
from pathlib import Path


def clean_file_content(file_path: Path):
    """Limpa conteúdo problemático de um arquivo MD"""

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Remove blocos CSS
    content = re.sub(
        r"\.[\w-]+\s*\{[^}]+\}", "", content, flags=re.MULTILINE | re.DOTALL
    )

    # Remove style attributes inline
    content = re.sub(r'style="[^"]*"', "", content)

    # Remove divs vazias e com classes
    content = re.sub(r"<div[^>]*></div>", "", content)
    content = re.sub(r'<div[^>]*class="[^"]*"[^>]*>', "", content)

    # Remove spans de loading
    content = re.sub(
        r'<div class="content-loading">.*?</div>', "", content, flags=re.DOTALL
    )

    # Remove JavaScript inline
    content = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)

    # Limpa tags HTML vazias
    content = re.sub(r"<([^>]+)>\s*</\1>", "", content)

    # Remove comentários HTML
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

    # Limpa espaços em excesso
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
    content = re.sub(r"^\s+", "", content, flags=re.MULTILINE)

    # Se o arquivo ficou muito vazio, cria conteúdo básico
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if len(lines) < 10:  # Arquivo muito vazio
        # Extrai título do frontmatter
        title_match = re.search(r"title:\s*(.+)", content)
        title = (
            title_match.group(1).strip('"')
            if title_match
            else file_path.stem.replace("-", " ").title()
        )

        content = re.sub(
            r"(---.*?---)",
            r"\1\n\n# "
            + title
            + "\n\n*Documentação em desenvolvimento...*\n\nEsta seção será expandida em breve com conteúdo detalhado sobre este tópico.\n\n## Próximos Passos\n\n- [ ] Expandir documentação\n- [ ] Adicionar exemplos práticos\n- [ ] Incluir diagramas explicativos\n",
            content,
            flags=re.DOTALL,
        )

    # Só reescreve se houve mudanças significativas
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Limpo: {file_path.name}")
        return True

    return False


def clean_all_files(docs_dir: str):
    """Limpa todos os arquivos MD na pasta docs"""

    docs_path = Path(docs_dir)
    cleaned_count = 0

    for md_file in docs_path.rglob("*.md"):
        if clean_file_content(md_file):
            cleaned_count += 1

    print(f"\n✨ {cleaned_count} arquivos limpos")


if __name__ == "__main__":
    docs_dir = "/home/anderson-henrique/Documentos/cidadao.ai-backend/docs_new/docs"
    clean_all_files(docs_dir)
