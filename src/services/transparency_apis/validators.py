"""
Data Validators for Transparency APIs

Provides validation utilities for data returned from Brazilian transparency APIs.
Ensures data quality, format consistency, and detects anomalies in fiscal data.

Author: Anderson Henrique da Silva
Created: 2025-10-09 15:10:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

import re
from datetime import datetime
from typing import Any, Optional


class DataValidator:
    """
    Validator for transparency API data.

    Provides methods to validate contracts, expenses, suppliers, and other
    fiscal data from Brazilian government sources.
    """

    # Brazilian CNPJ pattern: XX.XXX.XXX/XXXX-XX
    CNPJ_PATTERN = re.compile(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$")

    # Brazilian CPF pattern: XXX.XXX.XXX-XX
    CPF_PATTERN = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$")

    # IBGE municipality code pattern: 7 digits
    IBGE_CODE_PATTERN = re.compile(r"^\d{7}$")

    @staticmethod
    def validate_cnpj(cnpj: Optional[str]) -> bool:
        """
        Validate Brazilian CNPJ (company tax ID).

        Args:
            cnpj: CNPJ string (formatted or not)

        Returns:
            True if valid CNPJ format, False otherwise
        """
        if not cnpj:
            return False

        # Remove formatting
        cnpj_clean = re.sub(r"[^\d]", "", cnpj)

        if len(cnpj_clean) != 14:
            return False

        # Check if all digits are the same (invalid)
        if cnpj_clean == cnpj_clean[0] * 14:
            return False

        return True

    @staticmethod
    def validate_cpf(cpf: Optional[str]) -> bool:
        """
        Validate Brazilian CPF (individual tax ID).

        Args:
            cpf: CPF string (formatted or not)

        Returns:
            True if valid CPF format, False otherwise
        """
        if not cpf:
            return False

        # Remove formatting
        cpf_clean = re.sub(r"[^\d]", "", cpf)

        if len(cpf_clean) != 11:
            return False

        # Check if all digits are the same (invalid)
        if cpf_clean == cpf_clean[0] * 11:
            return False

        return True

    @staticmethod
    def validate_ibge_code(code: Optional[str]) -> bool:
        """
        Validate IBGE municipality code.

        Args:
            code: IBGE code (7 digits)

        Returns:
            True if valid format, False otherwise
        """
        if not code:
            return False

        return bool(DataValidator.IBGE_CODE_PATTERN.match(str(code)))

    @staticmethod
    def validate_date(date_str: Optional[str]) -> bool:
        """
        Validate date string in various Brazilian formats.

        Args:
            date_str: Date string (YYYY-MM-DD, DD/MM/YYYY, etc.)

        Returns:
            True if valid date, False otherwise
        """
        if not date_str:
            return False

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
        ]

        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue

        return False

    @staticmethod
    def validate_value(value: Any) -> bool:
        """
        Validate monetary value.

        Args:
            value: Value to validate (can be float, int, or string)

        Returns:
            True if valid positive value, False otherwise
        """
        try:
            val = float(value)
            return val >= 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
        """
        Validate contract data.

        Args:
            contract: Contract dictionary

        Returns:
            Validation result with issues found
        """
        issues = []

        # Check required fields
        if not contract.get("contract_id"):
            issues.append("Missing contract_id")

        if not contract.get("supplier_name"):
            issues.append("Missing supplier_name")

        # Validate supplier ID (CNPJ or CPF)
        supplier_id = contract.get("supplier_id")
        if supplier_id:
            if not (
                DataValidator.validate_cnpj(supplier_id)
                or DataValidator.validate_cpf(supplier_id)
            ):
                issues.append(f"Invalid supplier_id format: {supplier_id}")

        # Validate value
        value = contract.get("value")
        if value is not None:
            if not DataValidator.validate_value(value):
                issues.append(f"Invalid value: {value}")
            elif float(value) == 0:
                issues.append("Zero value contract")

        # Validate date
        date = contract.get("date")
        if date and not DataValidator.validate_date(date):
            issues.append(f"Invalid date format: {date}")

        # Validate municipality code
        municipality_code = contract.get("municipality_code")
        if municipality_code and not DataValidator.validate_ibge_code(
            municipality_code
        ):
            issues.append(f"Invalid IBGE code: {municipality_code}")

        return {"valid": len(issues) == 0, "issues": issues, "data": contract}

    @staticmethod
    def validate_expense(expense: dict[str, Any]) -> dict[str, Any]:
        """
        Validate expense data.

        Args:
            expense: Expense dictionary

        Returns:
            Validation result with issues found
        """
        issues = []

        # Check required fields
        if not expense.get("expense_id"):
            issues.append("Missing expense_id")

        # Validate value
        value = expense.get("value")
        if value is not None:
            if not DataValidator.validate_value(value):
                issues.append(f"Invalid value: {value}")
            elif float(value) == 0:
                issues.append("Zero value expense")

        # Validate date
        date = expense.get("date")
        if date and not DataValidator.validate_date(date):
            issues.append(f"Invalid date format: {date}")

        # Validate supplier ID if present
        supplier_id = expense.get("supplier_id")
        if supplier_id:
            if not (
                DataValidator.validate_cnpj(supplier_id)
                or DataValidator.validate_cpf(supplier_id)
            ):
                issues.append(f"Invalid supplier_id format: {supplier_id}")

        return {"valid": len(issues) == 0, "issues": issues, "data": expense}

    @staticmethod
    def validate_supplier(supplier: dict[str, Any]) -> dict[str, Any]:
        """
        Validate supplier data.

        Args:
            supplier: Supplier dictionary

        Returns:
            Validation result with issues found
        """
        issues = []

        # Check required fields
        if not supplier.get("supplier_name"):
            issues.append("Missing supplier_name")

        # Validate supplier ID (CNPJ or CPF)
        supplier_id = supplier.get("supplier_id")
        if not supplier_id:
            issues.append("Missing supplier_id")
        else:
            if not (
                DataValidator.validate_cnpj(supplier_id)
                or DataValidator.validate_cpf(supplier_id)
            ):
                issues.append(f"Invalid supplier_id format: {supplier_id}")

        return {"valid": len(issues) == 0, "issues": issues, "data": supplier}

    @staticmethod
    def validate_bidding(bidding: dict[str, Any]) -> dict[str, Any]:
        """
        Validate bidding process data.

        Args:
            bidding: Bidding dictionary

        Returns:
            Validation result with issues found
        """
        issues = []

        # Check required fields
        if not bidding.get("bidding_id"):
            issues.append("Missing bidding_id")

        if not bidding.get("modality"):
            issues.append("Missing modality")

        # Validate value
        value = bidding.get("value")
        if value is not None:
            if not DataValidator.validate_value(value):
                issues.append(f"Invalid value: {value}")

        # Validate date
        date = bidding.get("date")
        if date and not DataValidator.validate_date(date):
            issues.append(f"Invalid date format: {date}")

        return {"valid": len(issues) == 0, "issues": issues, "data": bidding}

    @staticmethod
    def validate_batch(
        data: list[dict[str, Any]], data_type: str = "contract"
    ) -> dict[str, Any]:
        """
        Validate batch of data.

        Args:
            data: List of data dictionaries
            data_type: Type of data (contract, expense, supplier, bidding)

        Returns:
            Batch validation summary
        """
        validators = {
            "contract": DataValidator.validate_contract,
            "expense": DataValidator.validate_expense,
            "supplier": DataValidator.validate_supplier,
            "bidding": DataValidator.validate_bidding,
        }

        validator = validators.get(data_type, DataValidator.validate_contract)

        results = [validator(item) for item in data]

        valid_count = sum(1 for r in results if r["valid"])
        invalid_count = len(results) - valid_count

        all_issues = []
        for r in results:
            if not r["valid"]:
                all_issues.extend(r["issues"])

        return {
            "total": len(data),
            "valid": valid_count,
            "invalid": invalid_count,
            "validation_rate": valid_count / len(data) if data else 0,
            "common_issues": DataValidator._count_issues(all_issues),
            "results": results,
        }

    @staticmethod
    def _count_issues(issues: list[str]) -> dict[str, int]:
        """Count occurrences of each issue type."""
        counts = {}
        for issue in issues:
            counts[issue] = counts.get(issue, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


class AnomalyDetector:
    """
    Detect anomalies in fiscal data.

    Identifies suspicious patterns, outliers, and potential irregularities
    in government spending data.
    """

    @staticmethod
    def detect_value_outliers(
        data: list[dict[str, Any]], std_threshold: float = 3.0
    ) -> list[dict[str, Any]]:
        """
        Detect value outliers using statistical methods.

        Args:
            data: List of data with 'value' field
            std_threshold: Number of standard deviations for outlier detection

        Returns:
            List of outlier records with anomaly score
        """
        if not data:
            return []

        values = [float(item.get("value", 0)) for item in data if item.get("value")]

        if not values:
            return []

        # Calculate statistics
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5

        outliers = []
        for item in data:
            value = float(item.get("value", 0))
            if value > 0:
                z_score = abs((value - mean) / std_dev) if std_dev > 0 else 0
                if z_score > std_threshold:
                    outliers.append(
                        {
                            **item,
                            "anomaly_score": z_score,
                            "anomaly_type": "value_outlier",
                            "mean_value": mean,
                            "std_dev": std_dev,
                        }
                    )

        return sorted(outliers, key=lambda x: x["anomaly_score"], reverse=True)

    @staticmethod
    def detect_duplicate_contracts(
        contracts: list[dict[str, Any]], similarity_threshold: float = 0.85
    ) -> list[dict[str, Any]]:
        """
        Detect potentially duplicate contracts.

        Args:
            contracts: List of contract dictionaries
            similarity_threshold: Threshold for considering contracts similar

        Returns:
            List of suspected duplicate pairs
        """
        duplicates = []

        for i, contract1 in enumerate(contracts):
            for contract2 in contracts[i + 1 :]:
                # Check for same supplier and similar values
                if (
                    contract1.get("supplier_id") == contract2.get("supplier_id")
                    and contract1.get("supplier_id") is not None
                ):

                    value1 = float(contract1.get("value", 0))
                    value2 = float(contract2.get("value", 0))

                    if value1 > 0 and value2 > 0:
                        similarity = min(value1, value2) / max(value1, value2)

                        if similarity >= similarity_threshold:
                            duplicates.append(
                                {
                                    "contract1": contract1,
                                    "contract2": contract2,
                                    "similarity": similarity,
                                    "anomaly_type": "potential_duplicate",
                                }
                            )

        return duplicates

    @staticmethod
    def detect_supplier_concentration(
        contracts: list[dict[str, Any]], concentration_threshold: float = 0.5
    ) -> dict[str, Any]:
        """
        Detect high concentration of contracts with few suppliers.

        Args:
            contracts: List of contract dictionaries
            concentration_threshold: Threshold for concentration alert

        Returns:
            Concentration analysis results
        """
        if not contracts:
            return {"concentrated": False}

        # Count contracts per supplier
        supplier_counts = {}
        total_value = 0

        for contract in contracts:
            supplier_id = contract.get("supplier_id")
            value = float(contract.get("value", 0))

            if supplier_id:
                if supplier_id not in supplier_counts:
                    supplier_counts[supplier_id] = {
                        "count": 0,
                        "value": 0,
                        "name": contract.get("supplier_name"),
                    }

                supplier_counts[supplier_id]["count"] += 1
                supplier_counts[supplier_id]["value"] += value
                total_value += value

        # Calculate concentration
        top_suppliers = sorted(
            supplier_counts.items(), key=lambda x: x[1]["value"], reverse=True
        )[:3]

        top3_value = sum(s[1]["value"] for s in top_suppliers)
        concentration_ratio = top3_value / total_value if total_value > 0 else 0

        return {
            "concentrated": concentration_ratio >= concentration_threshold,
            "concentration_ratio": concentration_ratio,
            "total_suppliers": len(supplier_counts),
            "total_contracts": len(contracts),
            "total_value": total_value,
            "top_suppliers": [
                {
                    "supplier_id": s[0],
                    "supplier_name": s[1]["name"],
                    "contract_count": s[1]["count"],
                    "total_value": s[1]["value"],
                    "percentage": s[1]["value"] / total_value if total_value > 0 else 0,
                }
                for s in top_suppliers
            ],
        }
