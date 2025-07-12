"""Pattern analysis for government spending trends."""

from typing import Dict, List, Optional
from collections import defaultdict, Counter
from datetime import datetime
from .models import MLModel


class PatternAnalyzer(MLModel):
    """Analyzes patterns in government spending data."""
    
    def __init__(self):
        super().__init__("pattern_analyzer")
        self._patterns = {}
    
    async def train(self, data: List[Dict], **kwargs) -> Dict:
        """Train pattern analysis model."""
        self._patterns = await self._extract_patterns(data)
        self._is_trained = True
        
        return {
            "status": "trained",
            "samples": len(data),
            "patterns_found": len(self._patterns),
            "model": self.model_name
        }
    
    async def predict(self, data: List[Dict]) -> List[Dict]:
        """Analyze patterns in new data."""
        patterns = await self._extract_patterns(data)
        
        pattern_analysis = []
        for pattern_type, pattern_data in patterns.items():
            pattern_analysis.append({
                "pattern_type": pattern_type,
                "pattern_data": pattern_data,
                "confidence": self._calculate_confidence(pattern_data),
                "significance": self._calculate_significance(pattern_data)
            })
        
        return pattern_analysis
    
    async def evaluate(self, data: List[Dict]) -> Dict:
        """Evaluate pattern analysis."""
        patterns = await self.predict(data)
        return {
            "total_patterns": len(patterns),
            "high_confidence_patterns": len([p for p in patterns if p["confidence"] > 0.7]),
            "significant_patterns": len([p for p in patterns if p["significance"] > 0.6])
        }
    
    async def _extract_patterns(self, data: List[Dict]) -> Dict:
        """Extract spending patterns from data."""
        patterns = {
            "temporal": self._analyze_temporal_patterns(data),
            "supplier": self._analyze_supplier_patterns(data),
            "value": self._analyze_value_patterns(data),
            "category": self._analyze_category_patterns(data)
        }
        
        return patterns
    
    def _analyze_temporal_patterns(self, data: List[Dict]) -> Dict:
        """Analyze temporal spending patterns."""
        monthly_spending = defaultdict(float)
        
        for item in data:
            # Extract month from date (simplified)
            date_str = item.get("data", "")
            if date_str:
                try:
                    # Assume format YYYY-MM-DD or similar
                    month = date_str[:7]  # YYYY-MM
                    value = float(item.get("valor", 0))
                    monthly_spending[month] += value
                except (ValueError, TypeError):
                    continue
        
        return {
            "monthly_totals": dict(monthly_spending),
            "peak_months": self._find_peak_periods(monthly_spending),
            "seasonal_trends": self._detect_seasonal_trends(monthly_spending)
        }
    
    def _analyze_supplier_patterns(self, data: List[Dict]) -> Dict:
        """Analyze supplier patterns."""
        supplier_counts = Counter()
        supplier_values = defaultdict(float)
        
        for item in data:
            supplier = item.get("fornecedor", {}).get("nome", "Unknown")
            value = float(item.get("valor", 0))
            
            supplier_counts[supplier] += 1
            supplier_values[supplier] += value
        
        return {
            "top_suppliers_by_count": supplier_counts.most_common(10),
            "top_suppliers_by_value": sorted(
                supplier_values.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            "supplier_concentration": self._calculate_concentration(supplier_values)
        }
    
    def _analyze_value_patterns(self, data: List[Dict]) -> Dict:
        """Analyze value distribution patterns."""
        values = [float(item.get("valor", 0)) for item in data if item.get("valor")]
        
        if not values:
            return {"error": "No value data available"}
        
        values.sort()
        n = len(values)
        
        return {
            "total_count": n,
            "total_value": sum(values),
            "mean_value": sum(values) / n,
            "median_value": values[n // 2],
            "quartiles": {
                "q1": values[n // 4],
                "q3": values[3 * n // 4]
            },
            "outliers": self._detect_value_outliers(values)
        }
    
    def _analyze_category_patterns(self, data: List[Dict]) -> Dict:
        """Analyze spending by category."""
        category_spending = defaultdict(float)
        
        for item in data:
            # Extract category from object description (simplified)
            obj_desc = item.get("objeto", "").lower()
            category = self._categorize_spending(obj_desc)
            value = float(item.get("valor", 0))
            
            category_spending[category] += value
        
        return {
            "category_totals": dict(category_spending),
            "category_distribution": self._calculate_distribution(category_spending)
        }
    
    def _categorize_spending(self, description: str) -> str:
        """Categorize spending based on description."""
        categories = {
            "technology": ["software", "hardware", "sistema", "tecnologia"],
            "services": ["serviço", "consultoria", "manutenção"],
            "infrastructure": ["obra", "construção", "reforma"],
            "supplies": ["material", "equipamento", "mobiliário"],
            "other": []
        }
        
        description_lower = description.lower()
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return "other"
    
    def _find_peak_periods(self, monthly_data: Dict) -> List[str]:
        """Find peak spending periods."""
        if not monthly_data:
            return []
        
        avg_spending = sum(monthly_data.values()) / len(monthly_data)
        return [month for month, value in monthly_data.items() if value > avg_spending * 1.5]
    
    def _detect_seasonal_trends(self, monthly_data: Dict) -> Dict:
        """Detect seasonal spending trends."""
        # Simplified seasonal analysis
        return {"trend": "stable", "seasonality": "low"}
    
    def _calculate_concentration(self, supplier_values: Dict) -> float:
        """Calculate supplier concentration (simplified Herfindahl index)."""
        total_value = sum(supplier_values.values())
        if total_value == 0:
            return 0
        
        concentration = sum((value / total_value) ** 2 for value in supplier_values.values())
        return concentration
    
    def _detect_value_outliers(self, sorted_values: List[float]) -> List[float]:
        """Detect value outliers using IQR method."""
        n = len(sorted_values)
        if n < 4:
            return []
        
        q1 = sorted_values[n // 4]
        q3 = sorted_values[3 * n // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [value for value in sorted_values if value < lower_bound or value > upper_bound]
    
    def _calculate_distribution(self, category_data: Dict) -> Dict:
        """Calculate percentage distribution."""
        total = sum(category_data.values())
        if total == 0:
            return {}
        
        return {category: (value / total) * 100 for category, value in category_data.items()}
    
    def _calculate_confidence(self, pattern_data: Dict) -> float:
        """Calculate confidence score for pattern."""
        # Simplified confidence calculation
        if not pattern_data or isinstance(pattern_data, dict) and not pattern_data:
            return 0.0
        
        return 0.8  # Default high confidence for stub
    
    def _calculate_significance(self, pattern_data: Dict) -> float:
        """Calculate significance score for pattern."""
        # Simplified significance calculation
        if not pattern_data:
            return 0.0
        
        return 0.7  # Default medium significance for stub