#!/usr/bin/env python3
"""
Script para corrigir frontmatter YAML malformado
"""

import re
from pathlib import Path

def fix_yaml_frontmatter(file_path: Path):
    """Corrige YAML frontmatter malformado"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procura por frontmatter malformado
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        return False
    
    frontmatter_raw = frontmatter_match.group(1)
    body = frontmatter_match.group(2)
    
    # Corrige problemas específicos do YAML
    fixed_frontmatter = []
    in_last_update = False
    
    for line in frontmatter_raw.split('\n'):
        if line.strip().startswith('last_update:'):
            fixed_frontmatter.append('last_update:')
            in_last_update = True
        elif in_last_update and line.strip().startswith('date:'):
            fixed_frontmatter.append('  date: "2025-01-30"')
        elif in_last_update and line.strip().startswith('author:'):
            fixed_frontmatter.append('  author: "Anderson Henrique"')
            in_last_update = False
        elif not in_last_update:
            fixed_frontmatter.append(line)
    
    # Reconstrói arquivo
    new_content = "---\n" + '\n'.join(fixed_frontmatter) + "\n---\n\n" + body.strip()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ YAML corrigido: {file_path.name}")
    return True

def fix_all_yaml(docs_dir: str):
    """Corrige todos os YAMLs malformados"""
    
    docs_path = Path(docs_dir)
    fixed_count = 0
    
    for md_file in docs_path.rglob("*.md"):
        if fix_yaml_frontmatter(md_file):
            fixed_count += 1
    
    print(f"\n✨ {fixed_count} frontmatters YAML corrigidos")

if __name__ == "__main__":
    docs_dir = "/home/anderson-henrique/Documentos/cidadao.ai-backend/docs_new/docs"
    fix_all_yaml(docs_dir)