"""
Script para configurar variáveis de ambiente no Hugging Face Spaces
"""

import os
from huggingface_hub import HfApi, SpaceVariable

def setup_space_secrets(space_id: str, token: str):
    """Configurar secrets no HF Space"""
    
    api = HfApi(token=token)
    
    # Variáveis necessárias
    secrets = {
        "PORTAL_TRANSPARENCIA_API_KEY": "sua-chave-api",
        "GROQ_API_KEY": "sua-chave-groq",
        "TOGETHER_AI_API_KEY": "sua-chave-together",
        "HUGGINGFACE_API_KEY": "sua-chave-hf"
    }
    
    for key, value in secrets.items():
        api.add_space_variable(
            space_id,
            key,
            value,
            description=f"API key for {key.replace('_', ' ').title()}"
        )
    
    print(f"✅ Secrets configurados para {space_id}")

if __name__ == "__main__":
    # Uso: python setup_hf_space.py
    space_id = "SEU-USUARIO/cidadao-ai"
    hf_token = "hf_xxxxxxxxxxxxx"  # Seu token do HF
    
    setup_space_secrets(space_id, hf_token)