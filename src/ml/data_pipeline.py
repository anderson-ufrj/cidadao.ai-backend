"""
Pipeline de Dados do Portal da Transparência para Cidadão.AI

Sistema completo de coleta, processamento e preparação de dados
do Portal da Transparência para treinamento do modelo especializado.
"""

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np
import spacy
from sklearn.model_selection import train_test_split

from src.core import json_utils

# Importar ferramentas do projeto
from ..tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter

logger = logging.getLogger(__name__)


@dataclass
class DataPipelineConfig:
    """Configuração do pipeline de dados"""

    # Configurações de coleta
    start_date: str = "2020-01-01"
    end_date: str = "2024-12-31"
    batch_size: int = 1000
    max_samples_per_type: int = 10000

    # Configurações de processamento
    min_text_length: int = 50
    max_text_length: int = 2048
    anomaly_threshold: float = 0.8

    # Configurações de anotação
    enable_auto_annotation: bool = True
    manual_annotation_sample_rate: float = 0.1

    # Configurações de balanceamento
    balance_classes: bool = True
    normal_anomaly_ratio: float = 0.7  # 70% normal, 30% anomalias

    # Configurações de output
    output_dir: str = "./data/processed"
    save_intermediate: bool = True

    # Configurações de validação
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15


class AnomalyDetector:
    """Detector de anomalias baseado em regras para anotação automática"""

    def __init__(self):
        # Padrões suspeitos
        self.suspicious_patterns = {
            "high_value": {"threshold": 10000000, "weight": 0.3},  # 10 milhões
            "emergency_contract": {
                "keywords": ["emergencial", "urgente", "dispensa"],
                "weight": 0.4,
            },
            "sole_source": {
                "keywords": ["inexigibilidade", "fonte única", "exclusivo"],
                "weight": 0.3,
            },
            "short_deadline": {
                "keywords": ["prazo reduzido", "exíguo", "urgência"],
                "weight": 0.2,
            },
            "irregular_cnpj": {
                "keywords": ["cnpj irregular", "situação irregular", "bloqueado"],
                "weight": 0.5,
            },
            "related_parties": {
                "keywords": ["parentesco", "familiar", "cônjuge", "parente"],
                "weight": 0.6,
            },
            "suspicious_amounts": {
                "patterns": [r"\d+\.999\.\d+", r"\d+\.000\.000"],  # Valores suspeitos
                "weight": 0.4,
            },
        }

        # Padrões de conformidade legal
        self.legal_compliance_patterns = {
            "proper_bidding": {
                "keywords": ["licitação", "pregão", "concorrência", "tomada de preços"],
                "weight": 0.5,
            },
            "legal_justification": {
                "keywords": ["justificativa legal", "amparo legal", "fundamentação"],
                "weight": 0.3,
            },
            "proper_documentation": {
                "keywords": ["processo", "documentação", "termo de referência"],
                "weight": 0.2,
            },
        }

        # Carregar modelo de NLP se disponível
        try:
            self.nlp = spacy.load("pt_core_news_sm")
        except:
            logger.warning(
                "Modelo spaCy não encontrado. Usando análise de texto básica."
            )
            self.nlp = None

    def detect_anomalies(self, contract_data: dict) -> dict[str, Any]:
        """Detectar anomalias em dados de contrato"""

        text = self._extract_text(contract_data)
        value = contract_data.get("valor", 0)

        # Calcular scores de anomalia
        anomaly_score = 0.0
        anomaly_indicators = []

        # Verificar valor alto
        if value > self.suspicious_patterns["high_value"]["threshold"]:
            anomaly_score += self.suspicious_patterns["high_value"]["weight"]
            anomaly_indicators.append("high_value")

        # Verificar padrões de texto
        text_lower = text.lower()

        for pattern_name, pattern_config in self.suspicious_patterns.items():
            if pattern_name == "high_value":
                continue

            if "keywords" in pattern_config:
                for keyword in pattern_config["keywords"]:
                    if keyword in text_lower:
                        anomaly_score += pattern_config["weight"]
                        anomaly_indicators.append(pattern_name)
                        break

            if "patterns" in pattern_config:
                for pattern in pattern_config["patterns"]:
                    if re.search(pattern, text):
                        anomaly_score += pattern_config["weight"]
                        anomaly_indicators.append(pattern_name)
                        break

        # Normalizar score
        anomaly_score = min(anomaly_score, 1.0)

        # Classificar anomalia
        if anomaly_score >= 0.7:
            anomaly_label = 2  # Anômalo
            anomaly_type = "Anômalo"
        elif anomaly_score >= 0.4:
            anomaly_label = 1  # Suspeito
            anomaly_type = "Suspeito"
        else:
            anomaly_label = 0  # Normal
            anomaly_type = "Normal"

        return {
            "anomaly_score": anomaly_score,
            "anomaly_label": anomaly_label,
            "anomaly_type": anomaly_type,
            "anomaly_indicators": anomaly_indicators,
            "confidence": self._calculate_confidence(anomaly_score, anomaly_indicators),
        }

    def assess_financial_risk(self, contract_data: dict) -> dict[str, Any]:
        """Avaliar risco financeiro"""

        value = contract_data.get("valor", 0)
        text = self._extract_text(contract_data)

        # Fatores de risco
        risk_factors = []
        risk_score = 0.0

        # Risco por valor
        if value > 50000000:  # > 50M
            risk_score += 0.4
            risk_factors.append("very_high_value")
        elif value > 10000000:  # > 10M
            risk_score += 0.3
            risk_factors.append("high_value")
        elif value > 1000000:  # > 1M
            risk_score += 0.2
            risk_factors.append("medium_value")

        # Risco por características do contrato
        text_lower = text.lower()

        risk_keywords = {
            "obra": 0.2,
            "construção": 0.2,
            "reforma": 0.15,
            "equipamento": 0.1,
            "serviço": 0.05,
            "emergencial": 0.3,
            "tecnologia": 0.1,
        }

        for keyword, weight in risk_keywords.items():
            if keyword in text_lower:
                risk_score += weight
                risk_factors.append(f"keyword_{keyword}")

        # Normalizar e classificar
        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.8:
            risk_level = 4  # Muito Alto
        elif risk_score >= 0.6:
            risk_level = 3  # Alto
        elif risk_score >= 0.4:
            risk_level = 2  # Médio
        elif risk_score >= 0.2:
            risk_level = 1  # Baixo
        else:
            risk_level = 0  # Muito Baixo

        return {
            "financial_risk_score": risk_score,
            "financial_risk_level": risk_level,
            "risk_factors": risk_factors,
            "estimated_risk_value": value * risk_score,
        }

    def check_legal_compliance(self, contract_data: dict) -> dict[str, Any]:
        """Verificar conformidade legal"""

        text = self._extract_text(contract_data)
        text_lower = text.lower()

        compliance_score = 0.0
        compliance_indicators = []

        # Verificar indicadores de conformidade
        for pattern_name, pattern_config in self.legal_compliance_patterns.items():
            for keyword in pattern_config["keywords"]:
                if keyword in text_lower:
                    compliance_score += pattern_config["weight"]
                    compliance_indicators.append(pattern_name)
                    break

        # Verificar indicadores de não conformidade
        non_compliance_keywords = [
            "irregular",
            "ilegal",
            "inválido",
            "viciado",
            "sem licitação",
            "direcionamento",
            "favorecimento",
        ]

        for keyword in non_compliance_keywords:
            if keyword in text_lower:
                compliance_score -= 0.3
                compliance_indicators.append(f"non_compliant_{keyword}")

        # Normalizar score
        compliance_score = max(0.0, min(compliance_score, 1.0))

        # Determinar conformidade
        is_compliant = compliance_score >= 0.5
        compliance_label = 1 if is_compliant else 0

        return {
            "legal_compliance_score": compliance_score,
            "legal_compliance_label": compliance_label,
            "is_compliant": is_compliant,
            "compliance_indicators": compliance_indicators,
        }

    def _extract_text(self, contract_data: dict) -> str:
        """Extrair texto relevante dos dados do contrato"""

        text_fields = [
            "objeto",
            "descricao",
            "justificativa",
            "observacoes",
            "modalidade_licitacao",
            "situacao",
            "fornecedor_nome",
        ]

        text_parts = []
        for field in text_fields:
            if field in contract_data and contract_data[field]:
                text_parts.append(str(contract_data[field]))

        return " ".join(text_parts)

    def _calculate_confidence(self, score: float, indicators: list[str]) -> float:
        """Calcular confiança da detecção"""

        # Confiança baseada no número de indicadores e score
        indicator_confidence = min(len(indicators) * 0.1, 0.5)
        score_confidence = score * 0.5

        return min(indicator_confidence + score_confidence, 1.0)


class TransparencyDataProcessor:
    """Processador de dados de transparência"""

    def __init__(self, config: DataPipelineConfig):
        self.config = config
        self.anomaly_detector = AnomalyDetector()
        self.api_client = None

        # Estatísticas de processamento
        self.stats = {
            "total_contracts": 0,
            "processed_contracts": 0,
            "anomalous_contracts": 0,
            "errors": 0,
        }

    async def collect_transparency_data(self) -> list[dict]:
        """Coletar dados do Portal da Transparência"""

        logger.info("🔍 Iniciando coleta de dados do Portal da Transparência")

        all_data = []

        async with TransparencyAPIClient() as client:
            self.api_client = client

            # Coletar contratos
            contracts_data = await self._collect_contracts_data(client)
            all_data.extend(contracts_data)

            # Coletar despesas (opcional)
            # despesas_data = await self._collect_despesas_data(client)
            # all_data.extend(despesas_data)

            # Coletar convênios (opcional)
            # convenios_data = await self._collect_convenios_data(client)
            # all_data.extend(convenios_data)

        logger.info(f"✅ Coleta finalizada: {len(all_data)} registros")
        return all_data

    async def _collect_contracts_data(
        self, client: TransparencyAPIClient
    ) -> list[dict]:
        """Coletar dados de contratos"""

        contracts = []

        # Definir filtros para diferentes tipos de contratos
        filter_configs = [
            # Contratos de alto valor
            TransparencyAPIFilter(ano=2024, valor_inicial=10000000, pagina=1),  # > 10M
            # Contratos médio valor
            TransparencyAPIFilter(
                ano=2024, valor_inicial=1000000, valor_final=10000000, pagina=1
            ),
            # Contratos emergenciais (mais propensos a anomalias)
            TransparencyAPIFilter(ano=2024, modalidade_licitacao="Dispensa", pagina=1),
        ]

        for filters in filter_configs:
            try:
                logger.info(f"📋 Coletando contratos com filtros: {filters}")

                batch_contracts = await client.get_contracts(filters)

                if batch_contracts:
                    # Limitar número de contratos por tipo
                    limited_contracts = batch_contracts[
                        : self.config.max_samples_per_type
                    ]
                    contracts.extend(limited_contracts)

                    logger.info(f"✅ Coletados {len(limited_contracts)} contratos")

                    # Rate limiting
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ Erro ao coletar contratos: {e}")
                self.stats["errors"] += 1

        self.stats["total_contracts"] = len(contracts)
        return contracts

    def process_raw_data(self, raw_data: list[dict]) -> list[dict]:
        """Processar dados brutos"""

        logger.info(f"⚙️ Processando {len(raw_data)} registros")

        processed_data = []

        for item in raw_data:
            try:
                processed_item = self._process_single_item(item)
                if processed_item:
                    processed_data.append(processed_item)
                    self.stats["processed_contracts"] += 1

            except Exception as e:
                logger.error(f"❌ Erro ao processar item: {e}")
                self.stats["errors"] += 1

        logger.info(
            f"✅ Processamento concluído: {len(processed_data)} registros válidos"
        )
        return processed_data

    def _process_single_item(self, item: dict) -> Optional[dict]:
        """Processar um item individual"""

        # Extrair e limpar texto
        text = self._extract_and_clean_text(item)

        if not text or len(text) < self.config.min_text_length:
            return None

        # Truncar se muito longo
        if len(text) > self.config.max_text_length:
            text = text[: self.config.max_text_length]

        # Análise automática de anomalias
        anomaly_analysis = self.anomaly_detector.detect_anomalies(item)
        financial_analysis = self.anomaly_detector.assess_financial_risk(item)
        legal_analysis = self.anomaly_detector.check_legal_compliance(item)

        if anomaly_analysis["anomaly_label"] > 0:
            self.stats["anomalous_contracts"] += 1

        # Extrair features especializadas
        entity_types = self._extract_entity_types(item)
        financial_features = self._extract_financial_features(item)
        legal_features = self._extract_legal_features(item)

        processed_item = {
            # Dados básicos
            "id": item.get("id", hashlib.md5(text.encode()).hexdigest()[:12]),
            "text": text,
            "original_data": item,
            # Labels para treinamento
            "anomaly_label": anomaly_analysis["anomaly_label"],
            "financial_risk": financial_analysis["financial_risk_level"],
            "legal_compliance": legal_analysis["legal_compliance_label"],
            # Scores detalhados
            "anomaly_score": anomaly_analysis["anomaly_score"],
            "financial_risk_score": financial_analysis["financial_risk_score"],
            "legal_compliance_score": legal_analysis["legal_compliance_score"],
            # Features especializadas
            "entity_types": entity_types,
            "financial_features": financial_features,
            "legal_features": legal_features,
            # Metadados
            "confidence": anomaly_analysis["confidence"],
            "anomaly_indicators": anomaly_analysis["anomaly_indicators"],
            "risk_factors": financial_analysis["risk_factors"],
            "compliance_indicators": legal_analysis["compliance_indicators"],
            # Valor do contrato
            "contract_value": item.get("valor", 0),
            # Timestamp de processamento
            "processed_at": datetime.now().isoformat(),
        }

        return processed_item

    def _extract_and_clean_text(self, item: dict) -> str:
        """Extrair e limpar texto dos dados"""

        # Campos de texto relevantes
        text_fields = [
            "objeto",
            "descricao",
            "justificativa",
            "observacoes",
            "modalidade_licitacao",
            "situacao",
            "fornecedor_nome",
            "orgao_nome",
            "unidade_gestora_nome",
        ]

        text_parts = []

        for field in text_fields:
            value = item.get(field)
            if value and isinstance(value, str):
                # Limpar texto
                cleaned_value = re.sub(r"\s+", " ", value.strip())
                cleaned_value = re.sub(r"[^\w\s\-\.\,\;\:\(\)\[\]]", "", cleaned_value)

                if len(cleaned_value) > 10:  # Filtrar textos muito curtos
                    text_parts.append(cleaned_value)

        return " ".join(text_parts)

    def _extract_entity_types(self, item: dict) -> list[int]:
        """Extrair tipos de entidades"""

        entity_types = []

        # Mapear tipos de entidades
        entity_mapping = {
            "orgao": 1,
            "empresa": 2,
            "pessoa_fisica": 3,
            "equipamento": 4,
            "servico": 5,
            "obra": 6,
            "material": 7,
        }

        # Identificar entidades no texto
        text = self._extract_and_clean_text(item).lower()

        for entity_name, entity_id in entity_mapping.items():
            if entity_name in text or any(keyword in text for keyword in [entity_name]):
                entity_types.append(entity_id)

        # Garantir pelo menos um tipo
        if not entity_types:
            entity_types = [0]  # Tipo genérico

        return entity_types[:10]  # Limitar a 10 tipos

    def _extract_financial_features(self, item: dict) -> list[float]:
        """Extrair features financeiras"""

        features = []

        # Valor do contrato (normalizado)
        valor = item.get("valor", 0)
        valor_normalizado = min(valor / 100000000, 1.0)  # Normalizar por 100M
        features.append(valor_normalizado)

        # Ano do contrato
        ano = item.get("ano", 2024)
        ano_normalizado = (ano - 2020) / 10  # Normalizar para 0-1
        features.append(ano_normalizado)

        # Modalidade (codificada)
        modalidade_map = {
            "Pregão": 0.1,
            "Concorrência": 0.2,
            "Tomada de Preços": 0.3,
            "Convite": 0.4,
            "Dispensa": 0.7,
            "Inexigibilidade": 0.9,
        }

        modalidade = item.get("modalidade_licitacao", "")
        modalidade_valor = modalidade_map.get(modalidade, 0.5)
        features.append(modalidade_valor)

        return features

    def _extract_legal_features(self, item: dict) -> list[int]:
        """Extrair features legais"""

        features = []

        # Presença de documentação legal
        legal_docs = [
            "processo",
            "edital",
            "termo_referencia",
            "ata",
            "contrato",
            "aditivo",
            "apostilamento",
        ]

        text = self._extract_and_clean_text(item).lower()

        for doc in legal_docs:
            if doc in text:
                features.append(1)
            else:
                features.append(0)

        return features

    def create_training_datasets(
        self, processed_data: list[dict]
    ) -> dict[str, list[dict]]:
        """Criar datasets de treinamento"""

        logger.info("📊 Criando datasets de treinamento")

        # Balancear classes se solicitado
        if self.config.balance_classes:
            processed_data = self._balance_dataset(processed_data)

        # Dividir em train/val/test
        train_data, temp_data = train_test_split(
            processed_data,
            test_size=(1 - self.config.train_split),
            random_state=42,
            stratify=[item["anomaly_label"] for item in processed_data],
        )

        val_size = self.config.val_split / (
            self.config.val_split + self.config.test_split
        )
        val_data, test_data = train_test_split(
            temp_data,
            test_size=(1 - val_size),
            random_state=42,
            stratify=[item["anomaly_label"] for item in temp_data],
        )

        datasets = {"train": train_data, "val": val_data, "test": test_data}

        # Log estatísticas
        for split_name, split_data in datasets.items():
            logger.info(f"📈 {split_name}: {len(split_data)} exemplos")

            # Distribuição de classes
            anomaly_dist = {}
            for item in split_data:
                label = item["anomaly_label"]
                anomaly_dist[label] = anomaly_dist.get(label, 0) + 1

            logger.info(f"   Distribuição anomalias: {anomaly_dist}")

        return datasets

    def _balance_dataset(self, data: list[dict]) -> list[dict]:
        """Balancear dataset por classes"""

        logger.info("⚖️ Balanceando dataset")

        # Agrupar por classe de anomalia
        class_groups = {0: [], 1: [], 2: []}

        for item in data:
            label = item["anomaly_label"]
            if label in class_groups:
                class_groups[label].append(item)

        # Calcular tamanho alvo
        total_size = len(data)
        normal_size = int(total_size * self.config.normal_anomaly_ratio)
        anomaly_size = total_size - normal_size
        suspicious_size = anomaly_size // 2
        anomalous_size = anomaly_size - suspicious_size

        # Balancear
        balanced_data = []

        # Normal (classe 0)
        normal_data = class_groups[0]
        if len(normal_data) >= normal_size:
            balanced_data.extend(
                np.random.choice(normal_data, normal_size, replace=False)
            )
        else:
            # Oversample se necessário
            balanced_data.extend(normal_data)
            remaining = normal_size - len(normal_data)
            balanced_data.extend(np.random.choice(normal_data, remaining, replace=True))

        # Suspeito (classe 1)
        suspicious_data = class_groups[1]
        if len(suspicious_data) >= suspicious_size:
            balanced_data.extend(
                np.random.choice(suspicious_data, suspicious_size, replace=False)
            )
        else:
            balanced_data.extend(suspicious_data)
            remaining = suspicious_size - len(suspicious_data)
            if remaining > 0 and len(suspicious_data) > 0:
                balanced_data.extend(
                    np.random.choice(suspicious_data, remaining, replace=True)
                )

        # Anômalo (classe 2)
        anomalous_data = class_groups[2]
        if len(anomalous_data) >= anomalous_size:
            balanced_data.extend(
                np.random.choice(anomalous_data, anomalous_size, replace=False)
            )
        else:
            balanced_data.extend(anomalous_data)
            remaining = anomalous_size - len(anomalous_data)
            if remaining > 0 and len(anomalous_data) > 0:
                balanced_data.extend(
                    np.random.choice(anomalous_data, remaining, replace=True)
                )

        # Shuffle
        np.random.shuffle(balanced_data)

        logger.info(f"📊 Dataset balanceado: {len(balanced_data)} exemplos")
        return balanced_data

    def save_datasets(self, datasets: dict[str, list[dict]]):
        """Salvar datasets processados"""

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Salvar cada split
        for split_name, split_data in datasets.items():
            output_path = output_dir / f"{split_name}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json_utils.dump(split_data, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 {split_name} salvo em {output_path}")

        # Salvar estatísticas
        stats_path = output_dir / "processing_stats.json"
        with open(stats_path, "w", encoding="utf-8") as f:
            json_utils.dump(self.stats, f, indent=2)

        # Salvar configuração
        config_path = output_dir / "pipeline_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json_utils.dump(self.config.__dict__, f, indent=2)

        logger.info(f"📈 Estatísticas e configuração salvas em {output_dir}")

    def generate_data_report(self, datasets: dict[str, list[dict]]) -> str:
        """Gerar relatório dos dados processados"""

        report = []
        report.append("# 📊 Relatório de Processamento de Dados - Cidadão.AI\n")

        # Estatísticas gerais
        report.append("## 📈 Estatísticas Gerais\n")
        report.append(
            f"- **Total de contratos coletados**: {self.stats['total_contracts']:,}"
        )
        report.append(
            f"- **Contratos processados**: {self.stats['processed_contracts']:,}"
        )
        report.append(
            f"- **Contratos anômalos detectados**: {self.stats['anomalous_contracts']:,}"
        )
        report.append(f"- **Erros durante processamento**: {self.stats['errors']:,}")
        report.append(
            f"- **Taxa de anomalias**: {self.stats['anomalous_contracts']/max(self.stats['processed_contracts'],1)*100:.1f}%\n"
        )

        # Estatísticas por split
        report.append("## 📚 Estatísticas por Dataset\n")

        for split_name, split_data in datasets.items():
            report.append(f"### {split_name.title()}\n")
            report.append(f"- **Tamanho**: {len(split_data):,} exemplos\n")

            # Distribuição de anomalias
            anomaly_dist = {}
            financial_dist = {}
            legal_dist = {}

            for item in split_data:
                # Anomalias
                anomaly_label = item["anomaly_label"]
                anomaly_dist[anomaly_label] = anomaly_dist.get(anomaly_label, 0) + 1

                # Risco financeiro
                financial_risk = item["financial_risk"]
                financial_dist[financial_risk] = (
                    financial_dist.get(financial_risk, 0) + 1
                )

                # Conformidade legal
                legal_compliance = item["legal_compliance"]
                legal_dist[legal_compliance] = legal_dist.get(legal_compliance, 0) + 1

            report.append("**Distribuição de Anomalias:**")
            anomaly_labels = {0: "Normal", 1: "Suspeito", 2: "Anômalo"}
            for label, count in sorted(anomaly_dist.items()):
                pct = count / len(split_data) * 100
                report.append(
                    f"  - {anomaly_labels.get(label, label)}: {count:,} ({pct:.1f}%)"
                )

            report.append("\n**Distribuição de Risco Financeiro:**")
            risk_labels = {
                0: "Muito Baixo",
                1: "Baixo",
                2: "Médio",
                3: "Alto",
                4: "Muito Alto",
            }
            for level, count in sorted(financial_dist.items()):
                pct = count / len(split_data) * 100
                report.append(
                    f"  - {risk_labels.get(level, level)}: {count:,} ({pct:.1f}%)"
                )

            report.append("\n**Conformidade Legal:**")
            legal_labels = {0: "Não Conforme", 1: "Conforme"}
            for label, count in sorted(legal_dist.items()):
                pct = count / len(split_data) * 100
                report.append(
                    f"  - {legal_labels.get(label, label)}: {count:,} ({pct:.1f}%)"
                )

            report.append("\n")

        # Configuração utilizada
        report.append("## ⚙️ Configuração do Pipeline\n")
        for key, value in self.config.__dict__.items():
            report.append(f"- **{key}**: {value}")

        report.append("\n")
        report.append(
            f"**Relatório gerado em**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return "\n".join(report)


async def run_data_pipeline(
    config: Optional[DataPipelineConfig] = None,
) -> dict[str, list[dict]]:
    """
    Executar pipeline completo de dados

    Args:
        config: Configuração do pipeline

    Returns:
        Datasets de treinamento processados
    """

    if config is None:
        config = DataPipelineConfig()

    logger.info("🚀 Iniciando pipeline de dados Cidadão.AI")

    processor = TransparencyDataProcessor(config)

    # 1. Coletar dados
    raw_data = await processor.collect_transparency_data()

    # 2. Processar dados
    processed_data = processor.process_raw_data(raw_data)

    # 3. Criar datasets
    datasets = processor.create_training_datasets(processed_data)

    # 4. Salvar dados
    processor.save_datasets(datasets)

    # 5. Gerar relatório
    report = processor.generate_data_report(datasets)

    # Salvar relatório
    output_dir = Path(config.output_dir)
    report_path = output_dir / "data_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"📄 Relatório salvo em {report_path}")
    logger.info("✅ Pipeline de dados finalizado com sucesso!")

    return datasets


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Executar pipeline
    config = DataPipelineConfig(
        max_samples_per_type=100,  # Reduzido para teste
        output_dir="./data/cidadao_gpt_processed",
    )

    # Executar
    datasets = asyncio.run(run_data_pipeline(config))

    print("🎉 Pipeline de dados executado com sucesso!")
    print(f"📊 Datasets criados: {list(datasets.keys())}")
    for name, data in datasets.items():
        print(f"   {name}: {len(data)} exemplos")
