#!/usr/bin/env python3
"""
Script para corrigir frontmatter YAML dos arquivos migrados
"""

import os
import re
from pathlib import Path


def fix_frontmatter_file(file_path: Path):
    """Corrige frontmatter YAML de um arquivo"""

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extrai frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not frontmatter_match:
        return False

    frontmatter_raw = frontmatter_match.group(1)
    body = frontmatter_match.group(2)

    # Corrige sintaxe YAML
    lines = frontmatter_raw.split("\n")
    fixed_lines = []

    for line in lines:
        if ":" in line and not line.strip().startswith("  "):
            # Linha principal do frontmatter
            key, value = line.split(":", 1)
            value = value.strip()

            # Adiciona aspas se necessário
            if (
                value
                and not value.startswith('"')
                and ("ã" in value or "ç" in value or ":" in value)
            ):
                value = f'"{value}"'

            fixed_lines.append(f"{key}: {value}")
        else:
            # Mantém sub-items e linhas vazias
            fixed_lines.append(line)

    # Reconstrói arquivo
    new_content = "---\n" + "\n".join(fixed_lines) + "\n---\n" + body

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Corrigido: {file_path.name}")
    return True


def fix_all_frontmatters(docs_dir: str):
    """Corrige todos os frontmatters na pasta docs"""

    docs_path = Path(docs_dir)
    fixed_count = 0

    for md_file in docs_path.rglob("*.md"):
        if fix_frontmatter_file(md_file):
            fixed_count += 1

    print(f"\n✨ {fixed_count} arquivos corrigidos")


if __name__ == "__main__":
    docs_dir = "/home/anderson-henrique/Documentos/cidadao.ai-backend/docs_new/docs"
    fix_all_frontmatters(docs_dir)
