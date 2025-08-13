#!/usr/bin/env python3
"""
Script para limpar e restaurar documentação de forma gradual
Remove completamente CSS, JavaScript e HTML problemático
"""

import os
import re
from pathlib import Path

def clean_mdx_content(content: str) -> str:
    """Limpa conteúdo MDX removendo tudo que pode quebrar"""
    
    # Remove frontmatter e extrai título
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_raw = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        
        # Extrai título do frontmatter
        title_match = re.search(r'title:\s*(.+)', frontmatter_raw)
        title = title_match.group(1).strip('"') if title_match else "Documentação"
    else:
        title = "Documentação"
        body = content
    
    # Remove COMPLETAMENTE todo CSS e JavaScript
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    body = re.sub(r'\.[\w-]+\s*\{[^}]*\}', '', body, flags=re.DOTALL)
    body = re.sub(r'\[data-theme[^\]]*\][^{]*\{[^}]*\}', '', body, flags=re.DOTALL)
    
    # Remove divs complexas
    body = re.sub(r'<div[^>]*class="[^"]*"[^>]*>.*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r'<div[^>]*style="[^"]*"[^>]*>.*?</div>', '', body, flags=re.DOTALL)
    
    # Remove spans com style
    body = re.sub(r'<span[^>]*style="[^"]*"[^>]*>(.*?)</span>', r'\1', body, flags=re.DOTALL)
    
    # Remove comentários HTML
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    
    # Remove tags vazias
    body = re.sub(r'<([^>]+)>\s*</\1>', '', body)
    body = re.sub(r'<[^>]*/?>', '', body)
    
    # Limpa espaços excessivos
    body = re.sub(r'\n\s*\n\s*\n+', '\n\n', body)
    body = re.sub(r'^\s+', '', body, flags=re.MULTILINE)
    
    # Remove linhas que são só espaços/tabs
    body = '\n'.join(line for line in body.split('\n') if line.strip())
    
    # Se ficou muito vazio, cria conteúdo básico
    clean_lines = [line for line in body.split('\n') if line.strip()]
    if len(clean_lines) < 5:
        body = f"""# {title}

*Documentação em desenvolvimento...*

Esta seção está sendo migrada da documentação anterior. 

## Conteúdo

- Informações técnicas detalhadas
- Exemplos práticos
- Diagramas explicativos

## Status

🚧 **Em construção** - Conteúdo será expandido em breve.
"""
    
    # Cria novo arquivo limpo
    clean_content = f"""---
title: "{title}"
sidebar_position: 1
description: "Documentação técnica do Cidadão.AI"
---

{body.strip()}
"""
    
    return clean_content

def process_directory(source_dir: Path, target_dir: Path, section_name: str):
    """Processa um diretório inteiro"""
    
    target_dir.mkdir(parents=True, exist_ok=True)
    processed = 0
    
    for file in source_dir.glob("*.md"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            clean_content = clean_mdx_content(content)
            
            target_file = target_dir / file.name
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            
            print(f"✅ Processado: {section_name}/{file.name}")
            processed += 1
            
        except Exception as e:
            print(f"❌ Erro em {file}: {e}")
    
    return processed

def restore_documentation():
    """Restaura toda a documentação de forma limpa"""
    
    source_base = Path("/home/anderson-henrique/Documentos/cidadao.ai-backend/docs_new/docs_problematic")
    target_base = Path("/home/anderson-henrique/Documentos/cidadao.ai-backend/docs_new/docs")
    
    print("🚀 Iniciando restauração limpa da documentação...")
    print("=" * 60)
    
    total_processed = 0
    
    # Seções a processar
    sections = [
        ("architecture", "🏗️ Arquitetura"),
        ("agents", "🤖 Agentes"),
        ("math", "🧮 Matemática"),
        ("api", "🔌 API"),
        ("infrastructure", "💾 Infraestrutura"),
        ("development", "🧪 Desenvolvimento"),
    ]
    
    for dir_name, display_name in sections:
        source_dir = source_base / dir_name
        target_dir = target_base / dir_name
        
        if source_dir.exists():
            print(f"\n📂 Processando: {display_name}")
            count = process_directory(source_dir, target_dir, dir_name)
            total_processed += count
            print(f"   → {count} arquivos processados")
        else:
            print(f"⚠️  Diretório não encontrado: {source_dir}")
    
    print("\n" + "=" * 60)
    print(f"✨ Restauração concluída: {total_processed} arquivos processados")
    print("🔧 Próximo passo: Testar servidor Docusaurus")

if __name__ == "__main__":
    restore_documentation()