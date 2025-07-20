#!/usr/bin/env python3
"""
Script para sincronizar READMEs entre GitHub e HuggingFace
Usage: python scripts/sync_readme.py [github|hf]
"""
import sys
import shutil
from pathlib import Path

def sync_to_github():
    """Copia README limpo (sem YAML) para README.md"""
    # README.md já está limpo, não precisa fazer nada
    print("✅ GitHub README already clean")

def sync_to_hf():
    """Copia README com YAML para README.md para deploy no HuggingFace"""
    src = Path("README_HF.md")
    dst = Path("README.md")
    
    if src.exists():
        shutil.copy2(src, dst)
        print("✅ HuggingFace README copied to README.md")
    else:
        print("❌ README_HF.md not found")

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['github', 'hf']:
        print("Usage: python scripts/sync_readme.py [github|hf]")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if target == 'github':
        sync_to_github()
    elif target == 'hf':
        sync_to_hf()

if __name__ == "__main__":
    main()