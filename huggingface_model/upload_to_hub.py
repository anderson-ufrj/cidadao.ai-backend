#!/usr/bin/env python3
"""
Script para upload do Cidadão.AI para o Hugging Face Hub

Este script configura e faz upload do modelo especializado em transparência
pública para o repositório do Hugging Face.
"""

import os
import sys
import json
import torch
from pathlib import Path
import logging
from typing import Dict, Any
from huggingface_hub import HfApi, Repository, login, create_repo
from transformers import AutoTokenizer

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.ml.hf_cidadao_model import (
    CidadaoAIConfig, CidadaoAIModel,
    CidadaoAIForAnomalyDetection,
    CidadaoAIForFinancialAnalysis,
    CidadaoAIForLegalCompliance
)

logger = logging.getLogger(__name__)


class CidadaoAIHubUploader:
    """Gerenciador de upload para Hugging Face Hub"""
    
    def __init__(
        self,
        model_name: str = "neural-thinker/cidadao-gpt",
        local_model_path: str = None,
        hub_token: str = None
    ):
        self.model_name = model_name
        self.local_model_path = local_model_path
        self.hub_token = hub_token or os.getenv("HUGGINGFACE_HUB_TOKEN")
        
        # Diretório de trabalho
        self.work_dir = Path("./huggingface_model")
        self.work_dir.mkdir(exist_ok=True)
        
        # API do HF
        self.api = HfApi()
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)

    def setup_authentication(self):
        """Configurar autenticação no HF Hub"""
        
        if not self.hub_token:
            logger.error("❌ Token do Hugging Face não encontrado!")
            logger.info("💡 Configure com: export HUGGINGFACE_HUB_TOKEN=seu_token")
            logger.info("💡 Ou obtenha em: https://huggingface.co/settings/tokens")
            return False
        
        try:
            login(token=self.hub_token)
            logger.info("✅ Autenticação no Hugging Face realizada com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            return False

    def create_model_config(self) -> CidadaoAIConfig:
        """Criar configuração do modelo"""
        
        logger.info("🔧 Criando configuração do modelo...")
        
        config = CidadaoAIConfig(
            # Configurações base
            vocab_size=50257,
            hidden_size=768,
            num_hidden_layers=12,
            num_attention_heads=12,
            intermediate_size=3072,
            max_position_embeddings=8192,
            
            # Configurações especializadas
            transparency_vocab_size=2048,
            corruption_detection_layers=4,
            financial_analysis_dim=512,
            legal_understanding_dim=256,
            
            # Dropout
            hidden_dropout_prob=0.1,
            attention_probs_dropout_prob=0.1,
            
            # Tarefas habilitadas
            enable_anomaly_detection=True,
            enable_financial_analysis=True,
            enable_legal_reasoning=True,
            
            # Labels
            num_anomaly_labels=3,
            num_financial_labels=5,
            num_legal_labels=2,
            
            # Metadados do modelo
            architectures=["CidadaoAIModel"],
            model_type="cidadao-gpt",
        )
        
        logger.info(f"✅ Configuração criada: {config.hidden_size}H-{config.num_hidden_layers}L")
        return config

    def create_or_load_model(self, config: CidadaoAIConfig) -> CidadaoAIModel:
        """Criar ou carregar modelo"""
        
        if self.local_model_path and Path(self.local_model_path).exists():
            logger.info(f"📂 Carregando modelo de {self.local_model_path}")
            try:
                model = CidadaoAIModel.from_pretrained(self.local_model_path)
                logger.info("✅ Modelo carregado com sucesso")
                return model
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar modelo local: {e}")
                logger.info("🔄 Criando modelo novo...")
        
        logger.info("🆕 Criando modelo novo...")
        model = CidadaoAIModel(config)
        
        # Inicializar com pesos aleatórios (em produção, use pesos treinados)
        logger.warning("⚠️ Usando pesos aleatórios - substitua por modelo treinado!")
        
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"✅ Modelo criado com {total_params:,} parâmetros")
        
        return model

    def setup_tokenizer(self):
        """Configurar tokenizer"""
        
        logger.info("🔤 Configurando tokenizer...")
        
        # Usar tokenizer base do GPT-2
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        
        # Adicionar tokens especiais para transparência
        special_tokens = [
            "[CONTRACT]", "[ENTITY]", "[VALUE]", "[ANOMALY]", 
            "[LEGAL]", "[FINANCIAL]", "[CORRUPTION]", "[COMPLIANCE]"
        ]
        
        tokenizer.add_special_tokens({
            "additional_special_tokens": special_tokens
        })
        
        # Configurar padding token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        logger.info(f"✅ Tokenizer configurado com {len(tokenizer)} tokens")
        return tokenizer

    def create_model_card(self) -> str:
        """Criar model card"""
        
        # Ler README existente
        readme_path = self.work_dir / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Criar model card básico se não existir
        model_card = """---
language: pt
license: mit
tags:
- transparency
- government
- corruption-detection
pipeline_tag: text-classification
---

# Cidadão.AI

Modelo especializado em análise de transparência pública brasileira.

## Uso

```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("neural-thinker/cidadao-gpt")
tokenizer = AutoTokenizer.from_pretrained("neural-thinker/cidadao-gpt")
```
"""
        return model_card

    def save_model_files(self, model: CidadaoAIModel, tokenizer, config: CidadaoAIConfig):
        """Salvar arquivos do modelo"""
        
        logger.info("💾 Salvando arquivos do modelo...")
        
        # Salvar modelo
        model.save_pretrained(self.work_dir)
        logger.info(f"✅ Modelo salvo em {self.work_dir}")
        
        # Salvar tokenizer
        tokenizer.save_pretrained(self.work_dir)
        logger.info(f"✅ Tokenizer salvo em {self.work_dir}")
        
        # Salvar configuração adicional
        config_dict = config.to_dict()
        config_path = self.work_dir / "config.json"
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        # Criar model card
        model_card = self.create_model_card()
        readme_path = self.work_dir / "README.md"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(model_card)
        
        logger.info("✅ Model card criado")

    def create_additional_files(self):
        """Criar arquivos adicionais"""
        
        # requirements.txt
        requirements = [
            "torch>=1.9.0",
            "transformers>=4.20.0",
            "tokenizers>=0.12.0",
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "scikit-learn>=1.0.0"
        ]
        
        req_path = self.work_dir / "requirements.txt"
        with open(req_path, 'w') as f:
            f.write('\n'.join(requirements))
        
        # gitattributes para Git LFS
        gitattributes = """
*.bin filter=lfs diff=lfs merge=lfs -text
*.safetensors filter=lfs diff=lfs merge=lfs -text
*.h5 filter=lfs diff=lfs merge=lfs -text
*.tflite filter=lfs diff=lfs merge=lfs -text
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.ot filter=lfs diff=lfs merge=lfs -text
*.onnx filter=lfs diff=lfs merge=lfs -text
"""
        
        attr_path = self.work_dir / ".gitattributes"
        with open(attr_path, 'w') as f:
            f.write(gitattributes.strip())
        
        # Arquivo de exemplo de uso
        example_code = '''
"""
Exemplo de uso do Cidadão.AI
"""

from transformers import AutoModel, AutoTokenizer
import torch

def analyze_transparency(text: str):
    """Analisar transparência de um texto"""
    
    # Carregar modelo e tokenizer
    model_name = "neural-thinker/cidadao-gpt"
    model = AutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Tokenizar entrada
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )
    
    # Inferência
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Processar resultados
    results = {}
    
    # Anomalias
    if hasattr(outputs, 'anomaly_logits'):
        anomaly_probs = torch.softmax(outputs.anomaly_logits, dim=-1)
        anomaly_pred = torch.argmax(anomaly_probs, dim=-1)
        
        anomaly_labels = ["Normal", "Suspeito", "Anômalo"]
        results["anomaly"] = {
            "label": anomaly_labels[anomaly_pred.item()],
            "confidence": anomaly_probs.max().item()
        }
    
    # Risco financeiro
    if hasattr(outputs, 'financial_logits'):
        financial_probs = torch.softmax(outputs.financial_logits, dim=-1)
        financial_pred = torch.argmax(financial_probs, dim=-1)
        
        financial_labels = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
        results["financial"] = {
            "label": financial_labels[financial_pred.item()],
            "confidence": financial_probs.max().item()
        }
    
    # Conformidade legal
    if hasattr(outputs, 'legal_logits'):
        legal_probs = torch.softmax(outputs.legal_logits, dim=-1)
        legal_pred = torch.argmax(legal_probs, dim=-1)
        
        legal_labels = ["Não Conforme", "Conforme"]
        results["legal"] = {
            "label": legal_labels[legal_pred.item()],
            "confidence": legal_probs.max().item()
        }
    
    return results

if __name__ == "__main__":
    # Exemplo de uso
    texto_teste = """
    Contrato emergencial no valor de R$ 25.000.000,00 para aquisição 
    de equipamentos médicos dispensando licitação. Fornecedor: Empresa XYZ LTDA.
    """
    
    resultado = analyze_transparency(texto_teste)
    
    print("🔍 Análise de Transparência:")
    for categoria, dados in resultado.items():
        print(f"  {categoria}: {dados['label']} ({dados['confidence']:.2%})")
'''
        
        example_path = self.work_dir / "example_usage.py"
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_code)
        
        logger.info("✅ Arquivos adicionais criados")

    def upload_to_hub(self):
        """Upload para Hugging Face Hub"""
        
        logger.info(f"🚀 Fazendo upload para {self.model_name}...")
        
        try:
            # Criar repositório se não existir
            try:
                create_repo(
                    repo_id=self.model_name,
                    token=self.hub_token,
                    repo_type="model",
                    exist_ok=True
                )
                logger.info("✅ Repositório criado/verificado")
            except Exception as e:
                logger.warning(f"⚠️ Repositório pode já existir: {e}")
            
            # Upload dos arquivos
            self.api.upload_folder(
                folder_path=str(self.work_dir),
                repo_id=self.model_name,
                token=self.hub_token,
                repo_type="model",
                commit_message="🤖 Upload Cidadão.AI - Modelo especializado em transparência pública brasileira"
            )
            
            logger.info(f"🎉 Upload concluído com sucesso!")
            logger.info(f"🌐 Modelo disponível em: https://huggingface.co/{self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Erro no upload: {e}")
            raise

    def run_full_upload(self):
        """Executar processo completo de upload"""
        
        logger.info("🚀 Iniciando processo de upload do Cidadão.AI para Hugging Face Hub")
        
        try:
            # 1. Autenticação
            if not self.setup_authentication():
                return False
            
            # 2. Criar configuração
            config = self.create_model_config()
            
            # 3. Criar/carregar modelo
            model = self.create_or_load_model(config)
            
            # 4. Configurar tokenizer
            tokenizer = self.setup_tokenizer()
            
            # 5. Redimensionar embeddings se necessário
            if len(tokenizer) > model.backbone.wte.num_embeddings:
                logger.info("🔧 Redimensionando embeddings...")
                model.backbone.resize_token_embeddings(len(tokenizer))
            
            # 6. Salvar arquivos
            self.save_model_files(model, tokenizer, config)
            
            # 7. Criar arquivos adicionais
            self.create_additional_files()
            
            # 8. Upload
            self.upload_to_hub()
            
            logger.info("🎉 Processo concluído com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no processo: {e}")
            return False

    def validate_upload(self):
        """Validar upload testando download"""
        
        logger.info("🔍 Validando upload...")
        
        try:
            from transformers import AutoModel, AutoTokenizer
            
            # Tentar carregar modelo do Hub
            model = AutoModel.from_pretrained(self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Teste básico
            test_text = "Contrato teste para validação"
            inputs = tokenizer(test_text, return_tensors="pt")
            outputs = model(**inputs)
            
            logger.info("✅ Validação bem-sucedida!")
            logger.info(f"📊 Output shape: {outputs.last_hidden_state.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return False


def main():
    """Função principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload Cidadão.AI para Hugging Face Hub")
    parser.add_argument("--model-name", default="neural-thinker/cidadao-gpt", help="Nome do modelo no Hub")
    parser.add_argument("--local-path", help="Caminho para modelo local treinado")
    parser.add_argument("--token", help="Token do Hugging Face")
    parser.add_argument("--validate", action="store_true", help="Validar upload após conclusão")
    
    args = parser.parse_args()
    
    # Criar uploader
    uploader = CidadaoAIHubUploader(
        model_name=args.model_name,
        local_model_path=args.local_path,
        hub_token=args.token
    )
    
    # Executar upload
    success = uploader.run_full_upload()
    
    if success:
        logger.info("✅ Upload concluído com sucesso!")
        
        if args.validate:
            uploader.validate_upload()
        
        logger.info(f"🌐 Acesse o modelo em: https://huggingface.co/{args.model_name}")
    else:
        logger.error("❌ Falha no upload")
        sys.exit(1)


if __name__ == "__main__":
    main()