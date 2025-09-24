"""
Module: tools.data_visualizer
Description: Data visualization utilities for government transparency data
Author: Anderson H. Silva
Date: 2025-01-15
"""

from src.core import json_utils
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataVisualizer:
    """Create visualizations for government transparency data."""
    
    def __init__(self):
        self.color_palette = {
            "primary": "#3b82f6",
            "secondary": "#10b981",
            "warning": "#f59e0b", 
            "danger": "#ef4444",
            "success": "#10b981",
            "info": "#6366f1"
        }
    
    def _extract_numeric_value(self, value_str: str) -> float:
        """Extract numeric value from currency string."""
        try:
            if isinstance(value_str, (int, float)):
                return float(value_str)
            
            # Remove currency symbols and convert to float
            numeric = re.sub(r'[^\d,.-]', '', str(value_str))
            numeric = numeric.replace(',', '.')
            return float(numeric)
        except:
            return 0.0
    
    def _format_currency(self, value: float) -> str:
        """Format currency for display."""
        if value >= 1_000_000_000:
            return f"R$ {value/1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"R$ {value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"R$ {value/1_000:.1f}K"
        else:
            return f"R$ {value:.2f}"
    
    def create_summary_cards(self, data: Dict[str, Any]) -> str:
        """Create summary cards visualization."""
        if not data.get("success") or not data.get("data"):
            return ""
        
        items = data.get("data", [])
        data_type = data.get("data_type", "unknown")
        
        # Calculate summary statistics
        total_items = len(items)
        total_value = 0
        avg_value = 0
        max_value = 0
        
        for item in items:
            if data_type == "contracts":
                value = self._extract_numeric_value(item.get("value", 0))
            elif data_type == "expenses":
                value = self._extract_numeric_value(item.get("value", 0))
            elif data_type == "biddings":
                value = self._extract_numeric_value(item.get("value", 0))
            else:
                value = 0
            
            total_value += value
            max_value = max(max_value, value)
        
        avg_value = total_value / total_items if total_items > 0 else 0
        
        # Create HTML cards
        cards_html = f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 20px 0;">
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: {self.color_palette['primary']};">{total_items}</div>
                <div style="font-size: 14px; color: rgba(255, 255, 255, 0.7);">Total de Registros</div>
            </div>
            
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: {self.color_palette['success']};">{self._format_currency(total_value)}</div>
                <div style="font-size: 14px; color: rgba(255, 255, 255, 0.7);">Valor Total</div>
            </div>
            
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: {self.color_palette['warning']};">{self._format_currency(avg_value)}</div>
                <div style="font-size: 14px; color: rgba(255, 255, 255, 0.7);">Valor Médio</div>
            </div>
            
            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: {self.color_palette['info']};">{self._format_currency(max_value)}</div>
                <div style="font-size: 14px; color: rgba(255, 255, 255, 0.7);">Maior Valor</div>
            </div>
        </div>
        """
        
        return cards_html
    
    def create_top_entities_chart(self, data: Dict[str, Any]) -> str:
        """Create top entities chart."""
        if not data.get("success") or not data.get("data"):
            return ""
        
        items = data.get("data", [])
        data_type = data.get("data_type", "unknown")
        
        # Count entities
        entity_counts = {}
        entity_values = {}
        
        for item in items:
            if data_type == "contracts":
                entity = item.get("contractor", "Desconhecido")
                value = self._extract_numeric_value(item.get("value", 0))
            elif data_type == "expenses":
                entity = item.get("beneficiary", "Desconhecido")
                value = self._extract_numeric_value(item.get("value", 0))
            elif data_type == "biddings":
                entity = item.get("organ", "Desconhecido")
                value = self._extract_numeric_value(item.get("value", 0))
            else:
                continue
            
            # Truncate long names
            if len(entity) > 40:
                entity = entity[:37] + "..."
            
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
            entity_values[entity] = entity_values.get(entity, 0) + value
        
        # Get top 10 entities by count
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if not top_entities:
            return ""
        
        # Create horizontal bar chart
        max_count = max(count for _, count in top_entities)
        
        chart_html = f"""
        <div style="margin: 20px 0;">
            <h3 style="color: white; margin-bottom: 16px;">
                📊 Top 10 {"Contratados" if data_type == "contracts" else "Beneficiários" if data_type == "expenses" else "Órgãos"}
            </h3>
            <div style="background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 16px;">
        """
        
        for entity, count in top_entities:
            width_percentage = (count / max_count) * 100
            total_value = entity_values.get(entity, 0)
            
            chart_html += f"""
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="color: rgba(255, 255, 255, 0.9); font-size: 14px; font-weight: 500;">{entity}</span>
                        <span style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">{count} • {self._format_currency(total_value)}</span>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.1); border-radius: 6px; height: 8px;">
                        <div style="background: linear-gradient(90deg, {self.color_palette['primary']}, {self.color_palette['secondary']}); border-radius: 6px; height: 8px; width: {width_percentage}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            """
        
        chart_html += """
            </div>
        </div>
        """
        
        return chart_html
    
    def create_risk_indicators(self, risk_analysis: Dict[str, Any]) -> str:
        """Create risk indicators visualization."""
        if not risk_analysis:
            return ""
        
        risk_score = risk_analysis.get("risk_score", 0)
        risk_level = risk_analysis.get("risk_level", "BAIXO")
        risk_factors = risk_analysis.get("risk_factors", [])
        
        # Color based on risk level
        risk_colors = {
            "BAIXO": self.color_palette["success"],
            "MÉDIO": self.color_palette["warning"],
            "ALTO": self.color_palette["danger"],
            "CRÍTICO": "#dc2626"
        }
        
        risk_color = risk_colors.get(risk_level, self.color_palette["info"])
        
        # Risk score bar
        score_percentage = (risk_score / 10) * 100
        
        risk_html = f"""
        <div style="margin: 20px 0;">
            <h3 style="color: white; margin-bottom: 16px;">🚨 Análise de Risco</h3>
            <div style="background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 16px;">
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <div>
                        <div style="color: {risk_color}; font-size: 24px; font-weight: bold;">{risk_level}</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 14px;">Nível de Risco</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {risk_color}; font-size: 24px; font-weight: bold;">{risk_score:.1f}/10</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 14px;">Score de Risco</div>
                    </div>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.1); border-radius: 6px; height: 12px; margin-bottom: 16px;">
                    <div style="background: linear-gradient(90deg, {self.color_palette['success']}, {self.color_palette['warning']}, {self.color_palette['danger']}); border-radius: 6px; height: 12px; width: {score_percentage}%; transition: width 0.3s ease;"></div>
                </div>
        """
        
        # Risk factors
        if risk_factors:
            risk_html += """
                <div style="margin-top: 16px;">
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 16px; font-weight: 600; margin-bottom: 8px;">Fatores de Risco Identificados:</div>
            """
            
            for factor in risk_factors[:5]:  # Show max 5 factors
                contract_id = factor.get("contract_id", factor.get("expense_id", "N/A"))
                factors_list = factor.get("factors", [])
                
                if factors_list:
                    risk_html += f"""
                        <div style="margin-bottom: 8px; padding: 8px; background: rgba(239, 68, 68, 0.1); border-radius: 6px; border-left: 3px solid {self.color_palette['danger']};">
                            <div style="color: rgba(255, 255, 255, 0.9); font-size: 14px; font-weight: 500;">ID: {contract_id}</div>
                            <div style="color: rgba(255, 255, 255, 0.7); font-size: 12px;">• {' • '.join(factors_list)}</div>
                        </div>
                    """
            
            risk_html += "</div>"
        
        risk_html += """
            </div>
        </div>
        """
        
        return risk_html
    
    def create_timeline_chart(self, data: Dict[str, Any]) -> str:
        """Create timeline chart for temporal analysis."""
        if not data.get("success") or not data.get("data"):
            return ""
        
        items = data.get("data", [])
        data_type = data.get("data_type", "unknown")
        
        # Extract dates and values
        date_values = {}
        
        for item in items:
            try:
                if data_type == "contracts":
                    date_str = item.get("start_date", "")
                    value = self._extract_numeric_value(item.get("value", 0))
                elif data_type == "expenses":
                    date_str = item.get("date", "")
                    value = self._extract_numeric_value(item.get("value", 0))
                else:
                    continue
                
                if date_str and date_str != "N/A":
                    # Parse date
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                    month_key = date_obj.strftime("%Y-%m")
                    
                    if month_key not in date_values:
                        date_values[month_key] = {"count": 0, "value": 0}
                    
                    date_values[month_key]["count"] += 1
                    date_values[month_key]["value"] += value
            except:
                continue
        
        if not date_values:
            return ""
        
        # Sort by date
        sorted_dates = sorted(date_values.items())
        
        if len(sorted_dates) < 2:
            return ""
        
        # Create timeline
        max_value = max(data["value"] for _, data in sorted_dates)
        
        timeline_html = f"""
        <div style="margin: 20px 0;">
            <h3 style="color: white; margin-bottom: 16px;">📈 Linha do Tempo</h3>
            <div style="background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 16px;">
        """
        
        for month, data in sorted_dates:
            height_percentage = (data["value"] / max_value) * 100 if max_value > 0 else 0
            
            # Format month
            try:
                month_obj = datetime.strptime(month, "%Y-%m")
                month_display = month_obj.strftime("%b/%Y")
            except:
                month_display = month
            
            timeline_html += f"""
                <div style="display: inline-block; margin-right: 16px; margin-bottom: 16px; text-align: center; min-width: 80px;">
                    <div style="height: 100px; display: flex; align-items: end; justify-content: center;">
                        <div style="background: linear-gradient(180deg, {self.color_palette['primary']}, {self.color_palette['secondary']}); width: 30px; border-radius: 4px 4px 0 0; height: {height_percentage}%; min-height: 4px; transition: height 0.3s ease;"></div>
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 12px; font-weight: 500; margin-top: 4px;">{month_display}</div>
                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 10px;">{data['count']} • {self._format_currency(data['value'])}</div>
                </div>
            """
        
        timeline_html += """
            </div>
        </div>
        """
        
        return timeline_html
    
    def create_comprehensive_visualization(
        self, 
        data: Dict[str, Any], 
        risk_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create comprehensive visualization combining all charts."""
        if not data.get("success"):
            return ""
        
        visualization = ""
        
        # Summary cards
        visualization += self.create_summary_cards(data)
        
        # Risk indicators
        if risk_analysis:
            visualization += self.create_risk_indicators(risk_analysis)
        
        # Top entities chart
        visualization += self.create_top_entities_chart(data)
        
        # Timeline chart
        visualization += self.create_timeline_chart(data)
        
        return visualization


# Factory function
def create_data_visualizer() -> DataVisualizer:
    """Create a data visualizer instance."""
    return DataVisualizer()