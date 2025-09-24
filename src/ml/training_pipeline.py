"""
Pipeline de Treinamento para Cidadão.AI

Sistema completo de fine-tuning especializado para dados de transparência pública brasileira.
Inspirado nas técnicas do Kimi K2, mas otimizado para análise governamental.
"""

import os
from src.core import json_utils
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from tqdm import tqdm
import wandb
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from .cidadao_model import CidadaoAIForTransparency, CidadaoModelConfig, create_cidadao_model

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuração de treinamento"""
    
    # Hiperparâmetros principais
    learning_rate: float = 2e-5
    batch_size: int = 8
    num_epochs: int = 10
    warmup_steps: int = 1000
    max_grad_norm: float = 1.0
    weight_decay: float = 0.01
    
    # Configurações de dados
    max_sequence_length: int = 512
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    
    # Configurações do modelo
    model_size: str = "medium"
    specialized_tasks: List[str] = None
    use_mixed_precision: bool = True
    gradient_accumulation_steps: int = 4
    
    # Configurações de checkpoint
    save_strategy: str = "epoch"  # "steps" ou "epoch"
    save_steps: int = 500
    eval_steps: int = 100
    logging_steps: int = 50
    output_dir: str = "./models/cidadao-gpt"
    
    # Configurações de avaliação
    eval_strategy: str = "steps"
    metric_for_best_model: str = "eval_f1"
    greater_is_better: bool = True
    early_stopping_patience: int = 3
    
    # Configurações de experimentação
    experiment_name: str = "cidadao-gpt-v1"
    use_wandb: bool = True
    wandb_project: str = "cidadao-ai"
    
    def __post_init__(self):
        if self.specialized_tasks is None:
            self.specialized_tasks = ["all"]


class TransparencyDataset(Dataset):
    """Dataset especializado para dados de transparência pública"""
    
    def __init__(
        self,
        data_path: str,
        tokenizer: AutoTokenizer,
        max_length: int = 512,
        task_type: str = "multi_task"
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.task_type = task_type
        
        # Carregar dados
        self.data = self._load_data(data_path)
        
        # Preparar vocabulário especializado
        self._prepare_specialized_vocab()
        
    def _load_data(self, data_path: str) -> List[Dict]:
        """Carregar dados de transparência"""
        
        data_file = Path(data_path)
        
        if data_file.suffix == '.json':
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json_utils.load(f)
        elif data_file.suffix == '.jsonl':
            data = []
            with open(data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data.append(json_utils.loads(line))
        else:
            # Assumir dados do Portal da Transparência em formato estruturado
            data = self._load_transparency_data(data_path)
            
        logger.info(f"Carregados {len(data)} exemplos de {data_path}")
        return data
    
    def _load_transparency_data(self, data_path: str) -> List[Dict]:
        """Carregar dados reais do Portal da Transparência"""
        
        # Simular estrutura de dados reais
        # Em produção, isso seria conectado ao pipeline de dados real
        sample_data = []
        
        # Exemplos de contratos com diferentes tipos de problemas
        contract_examples = [
            {
                "text": "Contrato para aquisição de equipamentos médicos no valor de R$ 2.500.000,00 firmado entre Ministério da Saúde e Empresa XYZ LTDA. Processo licitatório 12345/2024, modalidade pregão eletrônico.",
                "anomaly_label": 0,  # Normal
                "financial_risk": 2,  # Médio
                "legal_compliance": 1,  # Conforme
                "contract_value": 2500000.0,
                "entity_types": [1, 2, 3],  # Ministério, Empresa, Equipamento
                "corruption_indicators": []
            },
            {
                "text": "Contrato emergencial sem licitação para fornecimento de insumos hospitalares. Valor: R$ 15.000.000,00. Empresa beneficiária: Alpha Beta Comercial S.A., CNPJ com irregularidades na Receita Federal.",
                "anomaly_label": 2,  # Anômalo
                "financial_risk": 4,  # Alto
                "legal_compliance": 0,  # Não conforme
                "contract_value": 15000000.0,
                "entity_types": [1, 2, 4],  # Ministério, Empresa, Insumos
                "corruption_indicators": [1, 3, 5]  # Emergencial, Sem licitação, CNPJ irregular
            }
        ]
        
        # Amplificar dados com variações
        for base_example in contract_examples:
            for i in range(50):  # 50 variações de cada exemplo
                example = base_example.copy()
                example["id"] = f"{len(sample_data)}"
                
                # Adicionar ruído realístico
                if np.random.random() > 0.5:
                    example["text"] = self._add_realistic_variations(example["text"])
                
                sample_data.append(example)
        
        return sample_data
    
    def _add_realistic_variations(self, text: str) -> str:
        """Adicionar variações realísticas ao texto"""
        
        variations = [
            text.replace("Ministério da Saúde", "MS"),
            text.replace("equipamentos médicos", "equipamentos hospitalares"),
            text.replace("pregão eletrônico", "concorrência pública"),
            text + " Processo administrativo arquivado em sistema SIASG.",
            text + " Valor atualizado conforme INPC/IBGE."
        ]
        
        return np.random.choice(variations)
    
    def _prepare_specialized_vocab(self):
        """Preparar vocabulário especializado para transparência"""
        
        # Termos técnicos de transparência pública
        self.transparency_terms = {
            # Entidades
            "ministerio", "secretaria", "orgao", "entidade", "empresa", "fornecedor",
            
            # Tipos de contrato
            "licitacao", "pregao", "concorrencia", "tomada_precos", "convite", "dispensa",
            
            # Indicadores financeiros
            "valor", "preco", "orcamento", "pagamento", "repasse", "empenho",
            
            # Termos jurídicos
            "conformidade", "irregularidade", "infração", "penalidade", "multa",
            
            # Indicadores de corrupção
            "superfaturamento", "direcionamento", "cartel", "fraude", "peculato"
        }
        
        # Adicionar tokens especiais se necessário
        special_tokens = ["[CONTRACT]", "[ENTITY]", "[VALUE]", "[ANOMALY]", "[LEGAL]"]
        self.tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        # Tokenizar texto
        encoding = self.tokenizer(
            item["text"],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # Preparar labels e features especializadas
        result = {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
        }
        
        # Adicionar labels específicos por tarefa
        if "anomaly_label" in item:
            result["anomaly_labels"] = torch.tensor(item["anomaly_label"], dtype=torch.long)
            
        if "financial_risk" in item:
            result["financial_risk_labels"] = torch.tensor(item["financial_risk"], dtype=torch.long)
            
        if "legal_compliance" in item:
            result["legal_compliance_labels"] = torch.tensor(item["legal_compliance"], dtype=torch.long)
        
        # Adicionar features especializadas
        if "entity_types" in item:
            entity_types = torch.zeros(self.max_length, dtype=torch.long)
            for i, entity_type in enumerate(item["entity_types"][:self.max_length]):
                entity_types[i] = entity_type
            result["entity_types"] = entity_types
            
        if "corruption_indicators" in item:
            corruption_indicators = torch.zeros(self.max_length, dtype=torch.long)
            for i, indicator in enumerate(item["corruption_indicators"][:self.max_length]):
                corruption_indicators[i] = indicator
            result["corruption_indicators"] = corruption_indicators
        
        return result


class CidadaoTrainer:
    """Trainer especializado para Cidadão.AI"""
    
    def __init__(
        self,
        model: CidadaoAIForTransparency,
        tokenizer: AutoTokenizer,
        config: TrainingConfig
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        
        # Configurar device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Configurar otimizador
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
        
        # Configurar mixed precision se disponível
        self.scaler = torch.cuda.amp.GradScaler() if config.use_mixed_precision else None
        
        # Métricas de treinamento
        self.training_history = {
            "train_loss": [],
            "eval_loss": [],
            "eval_metrics": []
        }
        
        # Early stopping
        self.best_metric = float('-inf') if config.greater_is_better else float('inf')
        self.patience_counter = 0
        
        # Configurar logging
        if config.use_wandb:
            wandb.init(
                project=config.wandb_project,
                name=config.experiment_name,
                config=asdict(config)
            )
    
    def train(
        self,
        train_dataset: TransparencyDataset,
        eval_dataset: Optional[TransparencyDataset] = None,
        test_dataset: Optional[TransparencyDataset] = None
    ):
        """Executar treinamento completo"""
        
        logger.info("🚀 Iniciando treinamento do Cidadão.AI")
        
        # Preparar data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=4
        )
        
        eval_loader = None
        if eval_dataset:
            eval_loader = DataLoader(
                eval_dataset,
                batch_size=self.config.batch_size,
                shuffle=False,
                num_workers=4
            )
        
        # Configurar scheduler
        total_steps = len(train_loader) * self.config.num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.config.warmup_steps,
            num_training_steps=total_steps
        )
        
        # Loop de treinamento
        global_step = 0
        
        for epoch in range(self.config.num_epochs):
            logger.info(f"📚 Época {epoch + 1}/{self.config.num_epochs}")
            
            # Treinamento
            train_loss = self._train_epoch(train_loader, epoch, global_step)
            self.training_history["train_loss"].append(train_loss)
            
            # Avaliação
            if eval_loader and (epoch + 1) % 1 == 0:  # Avaliar a cada época
                eval_metrics = self._evaluate(eval_loader, epoch)
                self.training_history["eval_metrics"].append(eval_metrics)
                
                # Early stopping check
                current_metric = eval_metrics[self.config.metric_for_best_model]
                if self._is_better_metric(current_metric):
                    self.best_metric = current_metric
                    self.patience_counter = 0
                    self._save_checkpoint(epoch, is_best=True)
                    logger.info(f"🎯 Novo melhor modelo! {self.config.metric_for_best_model}: {current_metric:.4f}")
                else:
                    self.patience_counter += 1
                    
                if self.patience_counter >= self.config.early_stopping_patience:
                    logger.info(f"⏰ Early stopping acionado após {self.patience_counter} épocas sem melhoria")
                    break
            
            # Salvar checkpoint regular
            if (epoch + 1) % 2 == 0:  # Salvar a cada 2 épocas
                self._save_checkpoint(epoch, is_best=False)
            
            global_step += len(train_loader)
        
        # Avaliação final
        if test_dataset:
            test_loader = DataLoader(
                test_dataset,
                batch_size=self.config.batch_size,
                shuffle=False,
                num_workers=4
            )
            
            logger.info("🧪 Executando avaliação final no conjunto de teste")
            final_metrics = self._evaluate(test_loader, epoch=-1, is_test=True)
            
            logger.info("📊 Métricas finais:")
            for metric, value in final_metrics.items():
                logger.info(f"  {metric}: {value:.4f}")
        
        # Finalizar treinamento
        self._finalize_training()
    
    def _train_epoch(self, train_loader: DataLoader, epoch: int, global_step: int) -> float:
        """Treinar uma época"""
        
        self.model.train()
        total_loss = 0.0
        progress_bar = tqdm(train_loader, desc=f"Treinamento Época {epoch + 1}")
        
        for step, batch in enumerate(progress_bar):
            # Mover dados para device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Forward pass com mixed precision
            if self.scaler:
                with torch.cuda.amp.autocast():
                    loss = self._compute_multi_task_loss(batch)
            else:
                loss = self._compute_multi_task_loss(batch)
            
            # Backward pass
            if self.scaler:
                self.scaler.scale(loss).backward()
                
                if (step + 1) % self.config.gradient_accumulation_steps == 0:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    self.scheduler.step()
                    self.optimizer.zero_grad()
            else:
                loss.backward()
                
                if (step + 1) % self.config.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                    self.optimizer.step()
                    self.scheduler.step()
                    self.optimizer.zero_grad()
            
            total_loss += loss.item()
            
            # Logging
            if step % self.config.logging_steps == 0:
                avg_loss = total_loss / (step + 1)
                progress_bar.set_postfix({"loss": f"{avg_loss:.4f}"})
                
                if self.config.use_wandb:
                    wandb.log({
                        "train/loss": avg_loss,
                        "train/learning_rate": self.scheduler.get_last_lr()[0],
                        "train/epoch": epoch,
                        "train/step": global_step + step
                    })
        
        return total_loss / len(train_loader)
    
    def _compute_multi_task_loss(self, batch: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Computar loss multi-tarefa"""
        
        total_loss = 0.0
        loss_weights = {
            "anomaly": 1.0,
            "financial": 0.8,
            "legal": 0.6
        }
        
        # Loss de detecção de anomalias
        if "anomaly_labels" in batch:
            anomaly_outputs = self.model.detect_anomalies(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                entity_types=batch.get("entity_types"),
                corruption_indicators=batch.get("corruption_indicators")
            )
            
            # Extrair logits dos resultados
            anomaly_logits = []
            for pred in anomaly_outputs["predictions"]:
                probs = [
                    pred["probabilities"]["normal"],
                    pred["probabilities"]["suspicious"], 
                    pred["probabilities"]["anomalous"]
                ]
                anomaly_logits.append(probs)
            
            anomaly_logits = torch.tensor(anomaly_logits, device=self.device)
            anomaly_loss = nn.CrossEntropyLoss()(anomaly_logits, batch["anomaly_labels"])
            total_loss += loss_weights["anomaly"] * anomaly_loss
        
        # Loss de análise financeira
        if "financial_risk_labels" in batch:
            financial_outputs = self.model.analyze_financial_risk(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )
            
            # Extrair logits dos resultados
            risk_logits = []
            for pred in financial_outputs["predictions"]:
                probs = list(pred["risk_probabilities"].values())
                risk_logits.append(probs)
            
            risk_logits = torch.tensor(risk_logits, device=self.device)
            financial_loss = nn.CrossEntropyLoss()(risk_logits, batch["financial_risk_labels"])
            total_loss += loss_weights["financial"] * financial_loss
        
        # Loss de conformidade legal
        if "legal_compliance_labels" in batch:
            legal_outputs = self.model.check_legal_compliance(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )
            
            # Extrair logits dos resultados
            compliance_logits = []
            for pred in legal_outputs["predictions"]:
                probs = [
                    pred["legal_analysis"]["non_compliant_prob"],
                    pred["legal_analysis"]["compliant_prob"]
                ]
                compliance_logits.append(probs)
            
            compliance_logits = torch.tensor(compliance_logits, device=self.device)
            legal_loss = nn.CrossEntropyLoss()(compliance_logits, batch["legal_compliance_labels"])
            total_loss += loss_weights["legal"] * legal_loss
        
        return total_loss
    
    def _evaluate(self, eval_loader: DataLoader, epoch: int, is_test: bool = False) -> Dict[str, float]:
        """Avaliar modelo"""
        
        self.model.eval()
        total_loss = 0.0
        
        # Coletar predições e labels
        all_predictions = {
            "anomaly": {"preds": [], "labels": []},
            "financial": {"preds": [], "labels": []},
            "legal": {"preds": [], "labels": []}
        }
        
        with torch.no_grad():
            for batch in tqdm(eval_loader, desc="Avaliação"):
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                # Computar loss
                loss = self._compute_multi_task_loss(batch)
                total_loss += loss.item()
                
                # Coletar predições
                self._collect_predictions(batch, all_predictions)
        
        avg_loss = total_loss / len(eval_loader)
        
        # Computar métricas
        metrics = {"eval_loss": avg_loss}
        
        for task, preds_labels in all_predictions.items():
            if preds_labels["preds"]:
                task_metrics = self._compute_task_metrics(
                    preds_labels["preds"], 
                    preds_labels["labels"],
                    task_name=task
                )
                metrics.update(task_metrics)
        
        # Logging
        prefix = "test" if is_test else "eval"
        log_metrics = {f"{prefix}/{k}": v for k, v in metrics.items()}
        
        if self.config.use_wandb:
            wandb.log(log_metrics)
        
        return metrics
    
    def _collect_predictions(self, batch: Dict[str, torch.Tensor], all_predictions: Dict):
        """Coletar predições para avaliação"""
        
        # Anomaly detection
        if "anomaly_labels" in batch:
            anomaly_outputs = self.model.detect_anomalies(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )
            
            for i, pred in enumerate(anomaly_outputs["predictions"]):
                anomaly_type_map = {"Normal": 0, "Suspeito": 1, "Anômalo": 2}
                pred_label = anomaly_type_map[pred["anomaly_type"]]
                all_predictions["anomaly"]["preds"].append(pred_label)
                all_predictions["anomaly"]["labels"].append(batch["anomaly_labels"][i].item())
        
        # Financial analysis
        if "financial_risk_labels" in batch:
            financial_outputs = self.model.analyze_financial_risk(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )
            
            for i, pred in enumerate(financial_outputs["predictions"]):
                risk_level_map = {"Muito Baixo": 0, "Baixo": 1, "Médio": 2, "Alto": 3, "Muito Alto": 4}
                pred_label = risk_level_map[pred["risk_level"]]
                all_predictions["financial"]["preds"].append(pred_label)
                all_predictions["financial"]["labels"].append(batch["financial_risk_labels"][i].item())
        
        # Legal compliance
        if "legal_compliance_labels" in batch:
            legal_outputs = self.model.check_legal_compliance(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )
            
            for i, pred in enumerate(legal_outputs["predictions"]):
                pred_label = 1 if pred["is_compliant"] else 0
                all_predictions["legal"]["preds"].append(pred_label)
                all_predictions["legal"]["labels"].append(batch["legal_compliance_labels"][i].item())
    
    def _compute_task_metrics(self, predictions: List, labels: List, task_name: str) -> Dict[str, float]:
        """Computar métricas para uma tarefa específica"""
        
        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='weighted'
        )
        
        metrics = {
            f"eval_{task_name}_accuracy": accuracy,
            f"eval_{task_name}_precision": precision,
            f"eval_{task_name}_recall": recall,
            f"eval_{task_name}_f1": f1
        }
        
        # Métrica composta para early stopping
        if task_name == "anomaly":  # Usar anomaly como principal
            metrics["eval_f1"] = f1
        
        return metrics
    
    def _is_better_metric(self, current_metric: float) -> bool:
        """Verificar se métrica atual é melhor"""
        if self.config.greater_is_better:
            return current_metric > self.best_metric
        else:
            return current_metric < self.best_metric
    
    def _save_checkpoint(self, epoch: int, is_best: bool = False):
        """Salvar checkpoint do modelo"""
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if is_best:
            save_path = output_dir / "best_model"
        else:
            save_path = output_dir / f"checkpoint-epoch-{epoch}"
        
        # Salvar modelo
        self.model.save_model(str(save_path))
        
        # Salvar estado do treinamento
        training_state = {
            "epoch": epoch,
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "best_metric": self.best_metric,
            "training_history": self.training_history
        }
        
        torch.save(training_state, save_path / "training_state.pt")
        
        logger.info(f"✅ Checkpoint salvo em {save_path}")
    
    def _finalize_training(self):
        """Finalizar treinamento"""
        
        # Salvar histórico de treinamento
        output_dir = Path(self.config.output_dir)
        
        with open(output_dir / "training_history.json", "w") as f:
            json_utils.dump(self.training_history, f, indent=2)
        
        # Plotar curvas de treinamento
        self._plot_training_curves()
        
        if self.config.use_wandb:
            wandb.finish()
        
        logger.info("🎉 Treinamento finalizado com sucesso!")
    
    def _plot_training_curves(self):
        """Plotar curvas de treinamento"""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss de treinamento
        epochs = range(1, len(self.training_history["train_loss"]) + 1)
        axes[0, 0].plot(epochs, self.training_history["train_loss"])
        axes[0, 0].set_title("Loss de Treinamento")
        axes[0, 0].set_xlabel("Época")
        axes[0, 0].set_ylabel("Loss")
        
        # Métricas de avaliação
        if self.training_history["eval_metrics"]:
            eval_epochs = range(1, len(self.training_history["eval_metrics"]) + 1)
            
            # F1 Score
            f1_scores = [m.get("eval_f1", 0) for m in self.training_history["eval_metrics"]]
            axes[0, 1].plot(eval_epochs, f1_scores, 'g-')
            axes[0, 1].set_title("F1 Score")
            axes[0, 1].set_xlabel("Época")
            axes[0, 1].set_ylabel("F1")
            
            # Accuracy
            accuracy_scores = [m.get("eval_anomaly_accuracy", 0) for m in self.training_history["eval_metrics"]]
            axes[1, 0].plot(eval_epochs, accuracy_scores, 'b-')
            axes[1, 0].set_title("Accuracy")
            axes[1, 0].set_xlabel("Época")
            axes[1, 0].set_ylabel("Accuracy")
            
            # Loss de avaliação
            eval_losses = [m.get("eval_loss", 0) for m in self.training_history["eval_metrics"]]
            axes[1, 1].plot(eval_epochs, eval_losses, 'r-')
            axes[1, 1].set_title("Loss de Avaliação")
            axes[1, 1].set_xlabel("Época")
            axes[1, 1].set_ylabel("Loss")
        
        plt.tight_layout()
        
        # Salvar plot
        output_dir = Path(self.config.output_dir)
        plt.savefig(output_dir / "training_curves.png", dpi=300, bbox_inches='tight')
        plt.close()


def create_training_pipeline(
    data_path: str,
    config: Optional[TrainingConfig] = None
) -> Tuple[CidadaoAIForTransparency, CidadaoTrainer]:
    """
    Criar pipeline de treinamento completo
    
    Args:
        data_path: Caminho para dados de treinamento
        config: Configuração de treinamento
    
    Returns:
        Tuple com modelo e trainer
    """
    
    if config is None:
        config = TrainingConfig()
    
    logger.info("🏗️ Criando pipeline de treinamento Cidadão.AI")
    
    # Criar modelo
    model = create_cidadao_model(
        specialized_tasks=config.specialized_tasks,
        model_size=config.model_size
    )
    
    # Criar tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    tokenizer.pad_token = tokenizer.eos_token
    
    # Redimensionar embeddings se necessário
    model.model.model.resize_token_embeddings(len(tokenizer))
    
    # Criar trainer
    trainer = CidadaoTrainer(model, tokenizer, config)
    
    logger.info(f"✅ Pipeline criado - Modelo: {config.model_size}, Tarefas: {config.specialized_tasks}")
    
    return model, trainer


def prepare_transparency_data(data_path: str, output_dir: str = "./data/processed"):
    """
    Preparar dados de transparência para treinamento
    
    Esta função seria expandida para processar dados reais do Portal da Transparência
    """
    
    logger.info("📊 Preparando dados de transparência")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Aqui você implementaria:
    # 1. Conexão com Portal da Transparência API
    # 2. Extração e limpeza de dados
    # 3. Anotação de anomalias (semi-supervisionado)
    # 4. Balanceamento de classes
    # 5. Divisão train/val/test
    
    # Por enquanto, criar dados sintéticos
    logger.info("⚠️ Usando dados sintéticos para demonstração")
    
    # Implementação completa seria conectada aos dados reais
    sample_data = {
        "train": output_dir / "train.json",
        "val": output_dir / "val.json", 
        "test": output_dir / "test.json"
    }
    
    return sample_data


if __name__ == "__main__":
    # Exemplo de uso
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Configuração de treinamento
    config = TrainingConfig(
        experiment_name="cidadao-gpt-transparency-v1",
        num_epochs=5,
        batch_size=4,  # Reduzido para teste
        learning_rate=2e-5,
        use_wandb=False,  # Desabilitar para teste
        output_dir="./models/cidadao-gpt-test"
    )
    
    # Criar pipeline
    model, trainer = create_training_pipeline(
        data_path="./data/transparency_data.json",
        config=config
    )
    
    print("🤖 Cidadão.AI Training Pipeline criado com sucesso!")
    print(f"📊 Modelo: {config.model_size}")
    print(f"🎯 Tarefas especializadas: {config.specialized_tasks}")
    print(f"💾 Diretório de saída: {config.output_dir}")