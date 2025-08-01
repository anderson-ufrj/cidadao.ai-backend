#!/usr/bin/env python3
"""
Script de migração de documentação: docs/ → docs_new/
Converte MDX com HTML inline para Markdown puro compatível com Docusaurus
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

class DocsConverter:
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # Mapeamento de seções antigas → novas
        self.section_mapping = {
            'fundamentacao': 'architecture',
            'arquitetura': 'architecture', 
            'ia': 'math',
            'api': 'api',
            'validacao': 'validation',
            'conclusao': 'references'
        }
        
    def clean_html_inline(self, content: str) -> str:
        """Remove HTML inline e converte para Markdown puro"""
        
        # Remove divs de estilo inline
        content = re.sub(r'<div[^>]*style="[^"]*"[^>]*>', '', content)
        content = re.sub(r'</div>', '', content)
        
        # Converte spans de destaque para **bold**
        content = re.sub(r'<span[^>]*font-weight[^>]*>([^<]+)</span>', r'**\1**', content)
        
        # Remove classes CSS
        content = re.sub(r'class="[^"]*"', '', content)
        
        # Converte headings HTML para Markdown
        for i in range(1, 7):
            content = re.sub(rf'<h{i}[^>]*>([^<]+)</h{i}>', rf'{"#" * i} \1', content)
            
        # Converte links
        content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', r'[\2](\1)', content)
        
        # Remove tags vazias
        content = re.sub(r'<[^>]*></[^>]*>', '', content)
        content = re.sub(r'<[^>]*/?>', '', content)
        
        # Limpa espaços extras
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    def extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extrai frontmatter e adapta para Docusaurus"""
        
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not frontmatter_match:
            return {}, content
            
        frontmatter_raw = frontmatter_match.group(1)
        content_body = frontmatter_match.group(2)
        
        # Parse frontmatter básico
        frontmatter = {}
        for line in frontmatter_raw.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"')
        
        # Adapta para formato Docusaurus
        docusaurus_frontmatter = {
            'sidebar_position': frontmatter.get('order', 1),
            'description': f"Documentação técnica: {frontmatter.get('title', 'Cidadão.AI')}",
            'last_update': {
                'date': frontmatter.get('lastUpdated', '2025-01-31'),
                'author': frontmatter.get('author', 'Anderson Henrique')
            }
        }
        
        if 'title' in frontmatter:
            docusaurus_frontmatter['title'] = frontmatter['title']
            
        return docusaurus_frontmatter, content_body
    
    def convert_file(self, source_file: Path, target_file: Path) -> bool:
        """Converte um arquivo MDX → MD"""
        
        try:
            # Lê arquivo original
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrai e adapta frontmatter
            frontmatter, body = self.extract_frontmatter(content)
            
            # Limpa HTML inline
            clean_body = self.clean_html_inline(body)
            
            # Monta novo arquivo
            new_content = "---\n"
            for key, value in frontmatter.items():
                if isinstance(value, dict):
                    new_content += f"{key}:\n"
                    for subkey, subvalue in value.items():
                        new_content += f"  {subkey}: {subvalue}\n"
                else:
                    new_content += f"{key}: {value}\n"
            new_content += "---\n\n"
            new_content += clean_body
            
            # Cria diretório se não existir
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Escreve arquivo convertido
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"✅ Convertido: {source_file.name} → {target_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao converter {source_file}: {e}")
            return False
    
    def migrate_section(self, old_section: str, files_to_migrate: List[str]) -> int:
        """Migra uma seção específica"""
        
        converted_count = 0
        new_section = self.section_mapping.get(old_section, old_section)
        
        source_section_dir = self.source_dir / 'content' / old_section
        target_section_dir = self.target_dir / 'docs' / new_section
        
        if not source_section_dir.exists():
            print(f"⚠️  Seção {old_section} não encontrada em {source_section_dir}")
            return 0
            
        for file_name in files_to_migrate:
            source_file = source_section_dir / f"{file_name}.mdx"
            target_file = target_section_dir / f"{file_name}.md"
            
            if source_file.exists():
                if self.convert_file(source_file, target_file):
                    converted_count += 1
            else:
                print(f"⚠️  Arquivo não encontrado: {source_file}")
                
        return converted_count
    
    def run_migration(self):
        """Executa migração completa"""
        
        print("🚀 Iniciando migração docs/ → docs_new/")
        print("=" * 50)
        
        total_converted = 0
        
        # Migração por seções prioritárias
        migrations = {
            'arquitetura': [
                'system-architecture',
                'multi-agent-system', 
                'data-pipeline',
                'technical-implementation'
            ],
            'ia': [
                'math-foundations',
                'xai-algorithms',
                'mathematical-proofs',
                'algorithms'
            ],
            'fundamentacao': [
                'overview',
                'methodology',
                'theoretical-foundations',
                'literature-review'
            ],
            'api': [
                'api-reference',
                'datasets',
                'code-examples'
            ]
        }
        
        for section, files in migrations.items():
            print(f"\n📂 Migrando seção: {section}")
            count = self.migrate_section(section, files)
            total_converted += count
            print(f"   → {count} arquivos convertidos")
        
        print("\n" + "=" * 50)
        print(f"✨ Migração concluída: {total_converted} arquivos convertidos")
        print("🔧 Próximo passo: npm run build para testar")

if __name__ == "__main__":
    # Configuração dos caminhos
    source_dir = "/home/anderson-henrique/Documentos/cidadao.ai-backend/docs"
    target_dir = "/home/anderson-henrique/Documentos/cidadao.ai-backend/docs_new"
    
    # Executa migração
    converter = DocsConverter(source_dir, target_dir)
    converter.run_migration()