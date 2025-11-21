"""
Pipeline de ML Profissional com MLOps
Sistema completo de treinamento, versionamento e deployment de modelos
"""

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ML Libraries
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

# MLOps Tools
try:
    import mlflow
    import mlflow.pytorch

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class ModelType(Enum):
    """Tipos de modelo"""

    ANOMALY_DETECTOR = "anomaly_detector"
    FINANCIAL_ANALYZER = "financial_analyzer"
    LEGAL_COMPLIANCE = "legal_compliance"
    ENSEMBLE = "ensemble"


class TrainingStatus(Enum):
    """Status do treinamento"""

    PENDING = "pending"
    PREPROCESSING = "preprocessing"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ModelMetrics:
    """Métricas do modelo"""

    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    auc_roc: float = 0.0
    loss: float = 0.0
    val_accuracy: float = 0.0
    val_loss: float = 0.0
    inference_time_ms: float = 0.0
    model_size_mb: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrainingRun:
    """Execução de treinamento"""

    id: str
    model_type: ModelType
    status: TrainingStatus
    config: dict[str, Any]
    metrics: Optional[ModelMetrics] = None
    artifacts_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    experiment_id: Optional[str] = None


class MLPipelineConfig(BaseModel):
    """Configuração do pipeline ML"""

    # Model settings
    model_name: str = "cidadao-transparency-model"
    model_version: str = "1.0.0"
    base_model: str = "neuralmind/bert-base-portuguese-cased"

    # Training parameters
    learning_rate: float = 2e-5
    batch_size: int = 16
    num_epochs: int = 10
    warmup_steps: int = 500
    weight_decay: float = 0.01
    max_length: int = 512

    # Data parameters
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15
    min_samples_per_class: int = 100
    data_augmentation: bool = True

    # Infrastructure
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    num_workers: int = 4
    pin_memory: bool = True
    mixed_precision: bool = True

    # MLOps
    experiment_tracking: bool = True
    model_registry: bool = True
    auto_deployment: bool = False
    artifacts_dir: str = "./models/artifacts"
    models_dir: str = "./models/trained"

    # Performance
    early_stopping_patience: int = 3
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0

    # Evaluation
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100


class TransparencyDataset(Dataset):
    """Dataset para dados de transparência"""

    def __init__(
        self, texts: list[str], labels: list[int], tokenizer, max_length: int = 512
    ):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "label": torch.tensor(label, dtype=torch.long),
        }


class TransparencyClassifier(nn.Module):
    """Classificador especializado para transparência"""

    def __init__(self, model_name: str, num_labels: int = 3, dropout: float = 0.3):
        super().__init__()

        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)

        # Multi-head classifier
        hidden_size = self.bert.config.hidden_size

        # Anomaly detection head
        self.anomaly_classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_labels),
        )

        # Financial risk head
        self.financial_classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 5),  # Risk levels
        )

        # Legal compliance head
        self.legal_classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 4, 2),  # Compliant/Non-compliant
        )

        # Confidence estimation
        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid(),
        )

    def forward(self, input_ids, attention_mask, labels=None, task="anomaly"):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)

        # Get predictions for all tasks
        anomaly_logits = self.anomaly_classifier(pooled_output)
        financial_logits = self.financial_classifier(pooled_output)
        legal_logits = self.legal_classifier(pooled_output)
        confidence = self.confidence_head(pooled_output)

        outputs = {
            "anomaly_logits": anomaly_logits,
            "financial_logits": financial_logits,
            "legal_logits": legal_logits,
            "confidence": confidence,
        }

        # Calculate loss if labels provided
        if labels is not None:
            if task == "anomaly":
                loss = F.cross_entropy(anomaly_logits, labels)
            elif task == "financial":
                loss = F.cross_entropy(financial_logits, labels)
            elif task == "legal":
                loss = F.cross_entropy(legal_logits, labels)
            else:
                # Multi-task loss (assuming labels is a dict)
                loss = 0
                if "anomaly" in labels:
                    loss += F.cross_entropy(anomaly_logits, labels["anomaly"])
                if "financial" in labels:
                    loss += F.cross_entropy(financial_logits, labels["financial"])
                if "legal" in labels:
                    loss += F.cross_entropy(legal_logits, labels["legal"])

            outputs["loss"] = loss

        return outputs


class MLPipelineManager:
    """Gerenciador avançado de pipeline ML"""

    def __init__(self, config: MLPipelineConfig):
        self.config = config
        self.device = torch.device(config.device)

        # Create directories
        Path(config.artifacts_dir).mkdir(parents=True, exist_ok=True)
        Path(config.models_dir).mkdir(parents=True, exist_ok=True)

        # Initialize tracking
        self.training_runs: dict[str, TrainingRun] = {}
        self.models: dict[str, Any] = {}

        # MLOps setup
        self._setup_experiment_tracking()

    def _setup_experiment_tracking(self):
        """Configurar experiment tracking"""

        if not self.config.experiment_tracking:
            return

        if MLFLOW_AVAILABLE:
            try:
                mlflow.set_experiment(f"cidadao-ai-{self.config.model_name}")
                logger.info("✅ MLflow experiment tracking configurado")
            except Exception as e:
                logger.warning(f"⚠️ MLflow setup falhou: {e}")

        if WANDB_AVAILABLE:
            try:
                # wandb.init would be called in training function
                logger.info("✅ W&B tracking disponível")
            except Exception as e:
                logger.warning(f"⚠️ W&B setup falhou: {e}")

    async def prepare_data(
        self,
        contracts_data: list[dict[str, Any]],
        model_type: ModelType = ModelType.ANOMALY_DETECTOR,
    ) -> tuple[DataLoader, DataLoader, DataLoader]:
        """Preparar dados para treinamento"""

        logger.info(f"🔄 Preparando dados para {model_type.value}...")

        # Extract text and generate labels
        texts = []
        labels = []

        for contract in contracts_data:
            # Create descriptive text
            text = self._create_contract_text(contract)
            texts.append(text)

            # Generate label based on model type
            if model_type == ModelType.ANOMALY_DETECTOR:
                label = self._generate_anomaly_label(contract)
            elif model_type == ModelType.FINANCIAL_ANALYZER:
                label = self._generate_financial_label(contract)
            elif model_type == ModelType.LEGAL_COMPLIANCE:
                label = self._generate_legal_label(contract)
            else:
                label = 0

            labels.append(label)

        # Split data
        train_texts, temp_texts, train_labels, temp_labels = train_test_split(
            texts,
            labels,
            test_size=(1 - self.config.train_split),
            random_state=42,
            stratify=labels,
        )

        val_size = self.config.val_split / (
            self.config.val_split + self.config.test_split
        )
        val_texts, test_texts, val_labels, test_labels = train_test_split(
            temp_texts,
            temp_labels,
            test_size=(1 - val_size),
            random_state=42,
            stratify=temp_labels,
        )

        # Create tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)

        # Create datasets
        train_dataset = TransparencyDataset(
            train_texts, train_labels, tokenizer, self.config.max_length
        )
        val_dataset = TransparencyDataset(
            val_texts, val_labels, tokenizer, self.config.max_length
        )
        test_dataset = TransparencyDataset(
            test_texts, test_labels, tokenizer, self.config.max_length
        )

        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
        )

        test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
        )

        logger.info(
            f"✅ Dados preparados: {len(train_dataset)} treino, {len(val_dataset)} validação, {len(test_dataset)} teste"
        )

        return train_loader, val_loader, test_loader

    def _create_contract_text(self, contract: dict[str, Any]) -> str:
        """Criar texto descritivo do contrato"""

        parts = []

        if "objeto" in contract:
            parts.append(f"Objeto: {contract['objeto']}")

        if "valor" in contract or "valorInicial" in contract:
            valor = contract.get("valor", contract.get("valorInicial", 0))
            parts.append(f"Valor: R$ {valor:,.2f}")

        if "nomeRazaoSocialFornecedor" in contract:
            parts.append(f"Fornecedor: {contract['nomeRazaoSocialFornecedor']}")

        if "modalidadeLicitacao" in contract:
            parts.append(f"Modalidade: {contract['modalidadeLicitacao']}")

        if "situacao" in contract:
            parts.append(f"Situação: {contract['situacao']}")

        return ". ".join(parts)

    def _generate_anomaly_label(self, contract: dict[str, Any]) -> int:
        """Gerar label de anomalia (0=Normal, 1=Suspeito, 2=Anômalo)"""

        valor = contract.get("valor", contract.get("valorInicial", 0))
        modalidade = contract.get("modalidadeLicitacao", "").lower()

        # Simple rule-based labeling for training data
        score = 0

        # High value contracts
        if valor > 50_000_000:
            score += 1

        # Emergency or direct awards
        if any(
            word in modalidade
            for word in ["emergencial", "dispensa", "inexigibilidade"]
        ):
            score += 1

        # Missing information
        if not contract.get("objeto") or len(contract.get("objeto", "")) < 10:
            score += 1

        return min(score, 2)  # Cap at 2 (Anômalo)

    def _generate_financial_label(self, contract: dict[str, Any]) -> int:
        """Gerar label de risco financeiro (0=Muito Baixo, 1=Baixo, 2=Médio, 3=Alto, 4=Muito Alto)"""

        valor = contract.get("valor", contract.get("valorInicial", 0))

        if valor < 100_000:
            return 0  # Muito Baixo
        elif valor < 1_000_000:
            return 1  # Baixo
        elif valor < 10_000_000:
            return 2  # Médio
        elif valor < 50_000_000:
            return 3  # Alto
        else:
            return 4  # Muito Alto

    def _generate_legal_label(self, contract: dict[str, Any]) -> int:
        """Gerar label de conformidade legal (0=Não Conforme, 1=Conforme)"""

        modalidade = contract.get("modalidadeLicitacao", "").lower()

        # Simple compliance check
        if "pregao" in modalidade or "concorrencia" in modalidade:
            return 1  # Conforme
        else:
            return 0  # Potentially non-compliant

    async def train_model(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        model_type: ModelType = ModelType.ANOMALY_DETECTOR,
    ) -> str:
        """Treinar modelo"""

        run_id = f"{model_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        training_run = TrainingRun(
            id=run_id,
            model_type=model_type,
            status=TrainingStatus.TRAINING,
            config=self.config.dict(),
        )

        self.training_runs[run_id] = training_run

        try:
            logger.info(f"🚀 Iniciando treinamento {run_id}...")

            # Initialize tracking
            if WANDB_AVAILABLE and self.config.experiment_tracking:
                wandb.init(project="cidadao-ai", name=run_id, config=self.config.dict())

            if MLFLOW_AVAILABLE and self.config.experiment_tracking:
                mlflow.start_run(run_name=run_id)

            # Create model
            num_labels = (
                3
                if model_type == ModelType.ANOMALY_DETECTOR
                else (5 if model_type == ModelType.FINANCIAL_ANALYZER else 2)
            )
            model = TransparencyClassifier(self.config.base_model, num_labels)
            model.to(self.device)

            # Setup optimizer
            optimizer = optim.AdamW(
                model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
            )

            # Setup scheduler
            total_steps = len(train_loader) * self.config.num_epochs
            scheduler = optim.lr_scheduler.LinearLR(
                optimizer, start_factor=1.0, end_factor=0.1, total_iters=total_steps
            )

            # Mixed precision training
            scaler = (
                torch.cuda.amp.GradScaler() if self.config.mixed_precision else None
            )

            # Training variables
            best_val_acc = 0.0
            patience_counter = 0
            global_step = 0

            training_run.started_at = datetime.now(UTC)

            # Training loop
            for epoch in range(self.config.num_epochs):
                logger.info(f"📚 Época {epoch + 1}/{self.config.num_epochs}")

                # Training phase
                model.train()
                train_loss = 0.0
                train_correct = 0
                train_total = 0

                for batch_idx, batch in enumerate(train_loader):
                    input_ids = batch["input_ids"].to(self.device)
                    attention_mask = batch["attention_mask"].to(self.device)
                    labels = batch["label"].to(self.device)

                    optimizer.zero_grad()

                    # Forward pass
                    if self.config.mixed_precision and scaler:
                        with torch.cuda.amp.autocast():
                            outputs = model(
                                input_ids,
                                attention_mask,
                                labels,
                                task=model_type.value.split("_")[0],
                            )
                            loss = outputs["loss"]
                    else:
                        outputs = model(
                            input_ids,
                            attention_mask,
                            labels,
                            task=model_type.value.split("_")[0],
                        )
                        loss = outputs["loss"]

                    # Backward pass
                    if self.config.mixed_precision and scaler:
                        scaler.scale(loss).backward()
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            model.parameters(), self.config.max_grad_norm
                        )
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(
                            model.parameters(), self.config.max_grad_norm
                        )
                        optimizer.step()

                    scheduler.step()

                    # Statistics
                    train_loss += loss.item()

                    # Get predictions for accuracy
                    task_key = f"{model_type.value.split('_')[0]}_logits"
                    if task_key in outputs:
                        _, predicted = torch.max(outputs[task_key], 1)
                        train_total += labels.size(0)
                        train_correct += (predicted == labels).sum().item()

                    global_step += 1

                    # Logging
                    if global_step % self.config.logging_steps == 0:
                        current_lr = scheduler.get_last_lr()[0]
                        logger.info(
                            f"Step {global_step}, Loss: {loss.item():.4f}, LR: {current_lr:.2e}"
                        )

                        if WANDB_AVAILABLE and self.config.experiment_tracking:
                            wandb.log(
                                {
                                    "train_loss": loss.item(),
                                    "learning_rate": current_lr,
                                    "step": global_step,
                                }
                            )

                # Validation phase
                if epoch % 1 == 0:  # Validate every epoch
                    val_metrics = await self._validate_model(
                        model, val_loader, model_type
                    )

                    logger.info(
                        f"📊 Validação - Acc: {val_metrics.val_accuracy:.4f}, Loss: {val_metrics.val_loss:.4f}"
                    )

                    # Early stopping
                    if val_metrics.val_accuracy > best_val_acc:
                        best_val_acc = val_metrics.val_accuracy
                        patience_counter = 0

                        # Save best model
                        model_path = Path(self.config.models_dir) / f"{run_id}_best.pt"
                        torch.save(
                            {
                                "model_state_dict": model.state_dict(),
                                "optimizer_state_dict": optimizer.state_dict(),
                                "config": self.config.dict(),
                                "metrics": val_metrics.__dict__,
                                "epoch": epoch,
                            },
                            model_path,
                        )

                    else:
                        patience_counter += 1

                        if patience_counter >= self.config.early_stopping_patience:
                            logger.info(f"⏹️ Early stopping após {epoch + 1} épocas")
                            break

                    # Log to tracking systems
                    if WANDB_AVAILABLE and self.config.experiment_tracking:
                        wandb.log(
                            {
                                "val_accuracy": val_metrics.val_accuracy,
                                "val_loss": val_metrics.val_loss,
                                "val_f1": val_metrics.f1_score,
                                "epoch": epoch,
                            }
                        )

                    if MLFLOW_AVAILABLE and self.config.experiment_tracking:
                        mlflow.log_metrics(
                            {
                                "val_accuracy": val_metrics.val_accuracy,
                                "val_loss": val_metrics.val_loss,
                                "val_f1": val_metrics.f1_score,
                            },
                            step=epoch,
                        )

            # Final validation
            final_metrics = await self._validate_model(model, val_loader, model_type)
            training_run.metrics = final_metrics
            training_run.status = TrainingStatus.COMPLETED
            training_run.completed_at = datetime.now(UTC)

            # Save final model
            final_model_path = Path(self.config.models_dir) / f"{run_id}_final.pt"
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "config": self.config.dict(),
                    "metrics": final_metrics.__dict__,
                    "run_id": run_id,
                },
                final_model_path,
            )

            training_run.artifacts_path = str(final_model_path)

            # Register model
            if self.config.model_registry:
                await self._register_model(run_id, final_model_path, final_metrics)

            logger.info(f"✅ Treinamento {run_id} concluído com sucesso!")

            return run_id

        except Exception as e:
            training_run.status = TrainingStatus.FAILED
            training_run.error_message = str(e)
            training_run.completed_at = datetime.now(UTC)
            logger.error(f"❌ Treinamento {run_id} falhou: {e}")
            raise

        finally:
            # Cleanup tracking
            if WANDB_AVAILABLE and self.config.experiment_tracking:
                wandb.finish()

            if MLFLOW_AVAILABLE and self.config.experiment_tracking:
                mlflow.end_run()

    async def _validate_model(
        self, model, val_loader: DataLoader, model_type: ModelType
    ) -> ModelMetrics:
        """Validar modelo"""

        model.eval()
        val_loss = 0.0
        all_predictions = []
        all_labels = []
        all_confidences = []

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                outputs = model(
                    input_ids,
                    attention_mask,
                    labels,
                    task=model_type.value.split("_")[0],
                )

                val_loss += outputs["loss"].item()

                # Get predictions
                task_key = f"{model_type.value.split('_')[0]}_logits"
                if task_key in outputs:
                    _, predicted = torch.max(outputs[task_key], 1)

                    all_predictions.extend(predicted.cpu().numpy())
                    all_labels.extend(labels.cpu().numpy())
                    all_confidences.extend(outputs["confidence"].cpu().numpy())

        # Calculate metrics
        val_loss /= len(val_loader)

        accuracy = accuracy_score(all_labels, all_predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_predictions, average="weighted"
        )

        # AUC for binary classification
        auc = 0.0
        if len(set(all_labels)) == 2:
            try:
                auc = roc_auc_score(all_labels, all_confidences)
            except:
                pass

        return ModelMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc_roc=auc,
            val_accuracy=accuracy,
            val_loss=val_loss,
            inference_time_ms=0.0,  # TODO: measure inference time
        )

    async def _register_model(
        self, run_id: str, model_path: Path, metrics: ModelMetrics
    ):
        """Registrar modelo no registry"""

        try:
            if MLFLOW_AVAILABLE:
                # Log model to MLflow
                mlflow.pytorch.log_model(
                    pytorch_model=model_path,
                    artifact_path="model",
                    registered_model_name=f"{self.config.model_name}-{run_id}",
                )
                logger.info(f"✅ Modelo {run_id} registrado no MLflow")

        except Exception as e:
            logger.error(f"❌ Erro ao registrar modelo: {e}")

    async def load_model(self, run_id: str) -> Optional[TransparencyClassifier]:
        """Carregar modelo treinado"""

        model_path = Path(self.config.models_dir) / f"{run_id}_best.pt"
        if not model_path.exists():
            model_path = Path(self.config.models_dir) / f"{run_id}_final.pt"

        if not model_path.exists():
            logger.error(f"❌ Modelo {run_id} não encontrado")
            return None

        try:
            checkpoint = torch.load(model_path, map_location=self.device)

            # Recreate model
            model = TransparencyClassifier(self.config.base_model)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.to(self.device)
            model.eval()

            self.models[run_id] = model

            logger.info(f"✅ Modelo {run_id} carregado")
            return model

        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo {run_id}: {e}")
            return None

    async def predict(
        self, model: TransparencyClassifier, text: str, model_type: ModelType
    ) -> dict[str, Any]:
        """Fazer predição"""

        tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)

        # Tokenize
        encoding = tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.config.max_length,
            return_tensors="pt",
        )

        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        # Predict
        with torch.no_grad():
            outputs = model(input_ids, attention_mask)

        # Process outputs
        results = {}

        # Anomaly detection
        if "anomaly_logits" in outputs:
            anomaly_probs = F.softmax(outputs["anomaly_logits"], dim=-1)
            anomaly_pred = torch.argmax(anomaly_probs, dim=-1)

            labels = ["Normal", "Suspeito", "Anômalo"]
            results["anomaly"] = {
                "label": labels[anomaly_pred.item()],
                "confidence": anomaly_probs.max().item(),
                "probabilities": anomaly_probs.squeeze().tolist(),
            }

        # Financial risk
        if "financial_logits" in outputs:
            financial_probs = F.softmax(outputs["financial_logits"], dim=-1)
            financial_pred = torch.argmax(financial_probs, dim=-1)

            labels = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
            results["financial"] = {
                "label": labels[financial_pred.item()],
                "confidence": financial_probs.max().item(),
                "probabilities": financial_probs.squeeze().tolist(),
            }

        # Legal compliance
        if "legal_logits" in outputs:
            legal_probs = F.softmax(outputs["legal_logits"], dim=-1)
            legal_pred = torch.argmax(legal_probs, dim=-1)

            labels = ["Não Conforme", "Conforme"]
            results["legal"] = {
                "label": labels[legal_pred.item()],
                "confidence": legal_probs.max().item(),
                "probabilities": legal_probs.squeeze().tolist(),
            }

        # Overall confidence
        if "confidence" in outputs:
            results["overall_confidence"] = outputs["confidence"].item()

        return results

    def get_training_status(self, run_id: str) -> Optional[TrainingRun]:
        """Obter status do treinamento"""
        return self.training_runs.get(run_id)

    def list_models(self) -> list[dict[str, Any]]:
        """Listar modelos disponíveis"""

        models = []
        models_dir = Path(self.config.models_dir)

        for model_file in models_dir.glob("*.pt"):
            try:
                checkpoint = torch.load(model_file, map_location="cpu")
                models.append(
                    {
                        "filename": model_file.name,
                        "run_id": checkpoint.get("run_id", "unknown"),
                        "metrics": checkpoint.get("metrics", {}),
                        "created": datetime.fromtimestamp(model_file.stat().st_mtime),
                    }
                )
            except:
                continue

        return models


# Singleton instance
_ml_pipeline_manager: Optional[MLPipelineManager] = None


async def get_ml_pipeline_manager() -> MLPipelineManager:
    """Obter instância singleton do ML pipeline manager"""

    global _ml_pipeline_manager

    if _ml_pipeline_manager is None:
        config = MLPipelineConfig()
        _ml_pipeline_manager = MLPipelineManager(config)

    return _ml_pipeline_manager


if __name__ == "__main__":
    # Teste do pipeline
    import asyncio

    async def test_ml_pipeline():
        """Teste do pipeline ML"""

        print("🧪 Testando pipeline ML...")

        # Get pipeline manager
        pipeline = await get_ml_pipeline_manager()

        # Mock data for testing
        mock_contracts = [
            {
                "objeto": "Aquisição de equipamentos médicos",
                "valor": 5000000,
                "nomeRazaoSocialFornecedor": "Empresa XYZ",
                "modalidadeLicitacao": "Pregão Eletrônico",
            },
            {
                "objeto": "Obra de construção hospitalar",
                "valor": 100000000,
                "nomeRazaoSocialFornecedor": "Construtora ABC",
                "modalidadeLicitacao": "Dispensa de Licitação",
            },
        ] * 50  # Duplicate for testing

        try:
            # Prepare data
            train_loader, val_loader, test_loader = await pipeline.prepare_data(
                mock_contracts, ModelType.ANOMALY_DETECTOR
            )

            print(f"✅ Dados preparados: {len(train_loader)} batches de treino")

            # Train model (quick test with 1 epoch)
            pipeline.config.num_epochs = 1

            run_id = await pipeline.train_model(
                train_loader, val_loader, ModelType.ANOMALY_DETECTOR
            )

            print(f"✅ Modelo treinado: {run_id}")

            # Load and test model
            model = await pipeline.load_model(run_id)
            if model:
                result = await pipeline.predict(
                    model,
                    "Contrato emergencial de R$ 50 milhões sem licitação",
                    ModelType.ANOMALY_DETECTOR,
                )
                print(f"✅ Predição: {result}")

            # List models
            models = pipeline.list_models()
            print(f"✅ Modelos disponíveis: {len(models)}")

        except Exception as e:
            print(f"❌ Erro no teste: {e}")

        print("✅ Teste concluído!")

    asyncio.run(test_ml_pipeline())
