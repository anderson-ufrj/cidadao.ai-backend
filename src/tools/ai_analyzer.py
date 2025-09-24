"""
Module: tools.ai_analyzer
Description: AI-powered analysis of government transparency data
Author: Anderson H. Silva
Date: 2025-01-15
"""

import asyncio
from src.core import json_utils
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

from .data_integrator import DataIntegrator
from .transparency_api import TransparencyAPIFilter
from .data_visualizer import DataVisualizer

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered analyzer for government transparency data."""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_api_key = groq_api_key
        self.data_integrator = DataIntegrator()
        self.visualizer = DataVisualizer()
    
    async def __aenter__(self):
        await self.data_integrator.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.data_integrator.__aexit__(exc_type, exc_val, exc_tb)
    
    def _calculate_risk_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk score for government data."""
        risk_factors = []
        risk_score = 0
        
        if data.get("data_type") == "contracts":
            for contract in data.get("data", []):
                factors = []
                
                # High value contracts
                value_str = contract.get("value", "R$ 0,00")
                try:
                    numeric_value = float(re.sub(r'[^\d,.-]', '', value_str).replace(',', '.'))
                    if numeric_value > 10000000:  # > 10M
                        factors.append("High value contract (>R$ 10M)")
                        risk_score += 3
                    elif numeric_value > 1000000:  # > 1M
                        factors.append("Significant value contract (>R$ 1M)")
                        risk_score += 1
                except:
                    pass
                
                # Emergency contracts
                modality = contract.get("modality", "").lower()
                if "emergenc" in modality or "dispensa" in modality:
                    factors.append("Emergency/Dispensed contract")
                    risk_score += 2
                
                # Recent contracts
                try:
                    start_date = datetime.strptime(contract.get("start_date", ""), "%d/%m/%Y")
                    if (datetime.now() - start_date).days < 90:
                        factors.append("Recent contract (<90 days)")
                        risk_score += 1
                except:
                    pass
                
                if factors:
                    risk_factors.append({
                        "contract_id": contract.get("id", "N/A"),
                        "factors": factors
                    })
        
        elif data.get("data_type") == "expenses":
            for expense in data.get("data", []):
                factors = []
                
                # High value expenses
                value_str = expense.get("value", "R$ 0,00")
                try:
                    numeric_value = float(re.sub(r'[^\d,.-]', '', value_str).replace(',', '.'))
                    if numeric_value > 5000000:  # > 5M
                        factors.append("High value expense (>R$ 5M)")
                        risk_score += 3
                    elif numeric_value > 1000000:  # > 1M
                        factors.append("Significant value expense (>R$ 1M)")
                        risk_score += 1
                except:
                    pass
                
                if factors:
                    risk_factors.append({
                        "expense_id": expense.get("id", "N/A"),
                        "factors": factors
                    })
        
        # Normalize risk score
        total_items = len(data.get("data", []))
        if total_items > 0:
            risk_score = min(risk_score / total_items, 10)  # Max 10
        
        return {
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "risk_factors": risk_factors,
            "total_items_analyzed": total_items
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to risk level."""
        if score >= 7:
            return "CRÍTICO"
        elif score >= 5:
            return "ALTO"
        elif score >= 3:
            return "MÉDIO"
        else:
            return "BAIXO"
    
    def _analyze_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in government data."""
        patterns = {
            "temporal_patterns": [],
            "value_patterns": [],
            "entity_patterns": [],
            "anomalies": []
        }
        
        if data.get("data_type") == "contracts":
            # Analyze contractor patterns
            contractors = {}
            values_by_month = {}
            
            for contract in data.get("data", []):
                contractor = contract.get("contractor", "Unknown")
                contractors[contractor] = contractors.get(contractor, 0) + 1
                
                # Analyze temporal patterns
                try:
                    start_date = datetime.strptime(contract.get("start_date", ""), "%d/%m/%Y")
                    month_key = start_date.strftime("%Y-%m")
                    if month_key not in values_by_month:
                        values_by_month[month_key] = 0
                    
                    value_str = contract.get("value", "R$ 0,00")
                    numeric_value = float(re.sub(r'[^\d,.-]', '', value_str).replace(',', '.'))
                    values_by_month[month_key] += numeric_value
                except:
                    pass
            
            # Find top contractors
            top_contractors = sorted(contractors.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns["entity_patterns"] = [
                f"{contractor}: {count} contratos" for contractor, count in top_contractors
            ]
            
            # Find temporal anomalies
            if values_by_month:
                avg_value = sum(values_by_month.values()) / len(values_by_month)
                for month, value in values_by_month.items():
                    if value > avg_value * 2:  # 2x average
                        patterns["anomalies"].append(f"Pico de gastos em {month}: {value:,.2f}")
        
        elif data.get("data_type") == "expenses":
            # Analyze beneficiary patterns
            beneficiaries = {}
            organs = {}
            
            for expense in data.get("data", []):
                beneficiary = expense.get("beneficiary", "Unknown")
                beneficiaries[beneficiary] = beneficiaries.get(beneficiary, 0) + 1
                
                organ = expense.get("organ", "Unknown")
                organs[organ] = organs.get(organ, 0) + 1
            
            # Find top beneficiaries and organs
            top_beneficiaries = sorted(beneficiaries.items(), key=lambda x: x[1], reverse=True)[:5]
            top_organs = sorted(organs.items(), key=lambda x: x[1], reverse=True)[:5]
            
            patterns["entity_patterns"] = [
                f"Beneficiários: {beneficiary} ({count} despesas)" 
                for beneficiary, count in top_beneficiaries
            ] + [
                f"Órgãos: {organ} ({count} despesas)" 
                for organ, count in top_organs
            ]
        
        return patterns
    
    def _generate_ai_prompt(self, data: Dict[str, Any], analysis_type: str = "comprehensive") -> str:
        """Generate AI prompt for data analysis."""
        data_summary = f"""
DADOS GOVERNAMENTAIS PARA ANÁLISE:

Tipo de dados: {data.get('data_type', 'unknown')}
Total de registros: {data.get('total_records', 0)}
Registros analisados: {data.get('returned_records', 0)}

AMOSTRA DOS DADOS:
"""
        
        # Add sample data
        for i, item in enumerate(data.get("data", [])[:3], 1):
            data_summary += f"\\n{i}. {json_utils.dumps(item, indent=2, ensure_ascii=False)[:500]}...\\n"
        
        if analysis_type == "comprehensive":
            prompt = f"""Você é o Cidadão.AI, especialista em análise de transparência pública brasileira.

{data_summary}

Realize uma análise COMPLETA e TÉCNICA dos dados acima, seguindo este formato:

🔍 **ANÁLISE DE DADOS REAIS**:
[Descreva os principais achados nos dados apresentados]

🚨 **ANOMALIAS DETECTADAS**:
[Identifique padrões suspeitos, valores discrepantes, ou irregularidades]

💰 **ANÁLISE FINANCEIRA**:
[Avalie valores, tendências e impactos financeiros]

⚖️ **CONFORMIDADE LEGAL**:
[Verifique aderência às leis brasileiras - Lei 14.133/2021, Lei 8.666/93]

🎯 **PADRÕES IDENTIFICADOS**:
[Identifique padrões nos dados - concentração de contratos, beneficiários frequentes, etc.]

📋 **RECOMENDAÇÕES**:
[Sugira ações específicas baseadas nos dados analisados]

🔎 **PONTOS DE ATENÇÃO**:
[Destaque aspectos que merecem investigação mais aprofundada]

INSTRUÇÕES:
- Seja específico e baseie-se nos dados reais fornecidos
- Use números e estatísticas quando disponíveis
- Mencione leis e normas relevantes
- Mantenha tom profissional e técnico
- Destaque tanto pontos positivos quanto negativos"""
        
        elif analysis_type == "risk_assessment":
            prompt = f"""Você é o Cidadão.AI, especialista em análise de risco para transparência pública.

{data_summary}

Avalie os RISCOS associados aos dados apresentados:

🚨 **NÍVEL DE RISCO**: [Baixo/Médio/Alto/Crítico]

⚠️ **FATORES DE RISCO IDENTIFICADOS**:
[Liste específicos fatores de risco encontrados nos dados]

🔍 **INDICADORES DE ALERTA**:
[Identifique red flags nos dados analisados]

📊 **AVALIAÇÃO QUANTITATIVA**:
[Use números dos dados para fundamentar a análise]

🎯 **RECOMENDAÇÕES URGENTES**:
[Sugira ações imediatas baseadas no nível de risco]

Base sua análise exclusivamente nos dados fornecidos."""
        
        return prompt
    
    async def analyze_with_ai(self, data: Dict[str, Any], analysis_type: str = "comprehensive") -> str:
        """Analyze government data using AI."""
        try:
            import requests
            
            if not self.groq_api_key:
                return "❌ **API Key não configurada**\\n\\nPara usar análise de IA, configure a variável GROQ_API_KEY."
            
            # Generate AI prompt
            prompt = self._generate_ai_prompt(data, analysis_type)
            
            # Call Groq API
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2048
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"❌ **Erro na API**: {response.status_code}\\n\\n{response.text}"
        
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return f"❌ **Erro na análise**: {str(e)}"
    
    async def comprehensive_analysis(
        self, 
        query: str, 
        data_type: str = "contracts",
        include_ai: bool = True
    ) -> Dict[str, Any]:
        """Perform comprehensive analysis combining data search and AI analysis."""
        try:
            # Step 1: Search real data
            if data_type == "contracts":
                # Parse query for parameters
                cnpj_match = re.search(r'\\b\\d{2}\\.\\d{3}\\.\\d{3}/\\d{4}-\\d{2}\\b|\\b\\d{14}\\b', query)
                cnpj = cnpj_match.group() if cnpj_match else None
                
                year_match = re.search(r'\\b(20\\d{2})\\b', query)
                year = int(year_match.group()) if year_match else None
                
                value_match = re.search(r'\\b(?:acima|maior|superior)\\s+(?:de\\s+)?(?:r\\$\\s*)?([\\d.,]+)\\b', query.lower())
                min_value = None
                if value_match:
                    try:
                        value_str = value_match.group(1).replace(',', '.')
                        min_value = float(value_str)
                    except:
                        pass
                
                real_data = await self.data_integrator.search_contracts(
                    cnpj=cnpj,
                    year=year,
                    min_value=min_value,
                    limit=20
                )
            else:
                real_data = {"success": False, "error": "Data type not implemented"}
            
            # Step 2: Calculate risk score
            risk_analysis = self._calculate_risk_score(real_data) if real_data.get("success") else {}
            
            # Step 3: Analyze patterns
            pattern_analysis = self._analyze_patterns(real_data) if real_data.get("success") else {}
            
            # Step 4: AI analysis
            ai_analysis = ""
            if include_ai and real_data.get("success") and real_data.get("data"):
                ai_analysis = await self.analyze_with_ai(real_data)
            
            # Step 5: Combine results
            result = {
                "query": query,
                "data_type": data_type,
                "timestamp": datetime.now().isoformat(),
                "real_data": real_data,
                "risk_analysis": risk_analysis,
                "pattern_analysis": pattern_analysis,
                "ai_analysis": ai_analysis,
                "success": real_data.get("success", False)
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def format_comprehensive_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format comprehensive analysis for display."""
        if not analysis.get("success"):
            return f"❌ **Erro na análise**: {analysis.get('error', 'Erro desconhecido')}"
        
        # Build formatted response
        response = f"🔍 **ANÁLISE COMPLETA: {analysis['query']}**\\n\\n"
        
        # Real data summary
        real_data = analysis.get("real_data", {})
        if real_data.get("success"):
            response += f"📊 **DADOS ENCONTRADOS**\\n"
            response += f"• Total de registros: {real_data.get('total_records', 0):,}\\n"
            response += f"• Registros analisados: {real_data.get('returned_records', 0)}\\n\\n"
        
        # Add visualizations
        risk_analysis = analysis.get("risk_analysis", {})
        if real_data.get("success") and real_data.get("data"):
            visualizations = self.visualizer.create_comprehensive_visualization(
                real_data, risk_analysis
            )
            if visualizations:
                response += f"\\n{visualizations}\\n"
        
        # Risk analysis text
        if risk_analysis:
            risk_score = risk_analysis.get("risk_score", 0)
            risk_level = risk_analysis.get("risk_level", "BAIXO")
            
            response += f"🚨 **ANÁLISE DE RISCO**\\n"
            response += f"• Nível de risco: **{risk_level}**\\n"
            response += f"• Score de risco: {risk_score:.1f}/10\\n"
            
            risk_factors = risk_analysis.get("risk_factors", [])
            if risk_factors:
                response += f"• Fatores de risco encontrados: {len(risk_factors)}\\n"
            
            response += "\\n"
        
        # Pattern analysis
        pattern_analysis = analysis.get("pattern_analysis", {})
        if pattern_analysis:
            entity_patterns = pattern_analysis.get("entity_patterns", [])
            if entity_patterns:
                response += f"🎯 **PADRÕES IDENTIFICADOS**\\n"
                for pattern in entity_patterns[:5]:  # Top 5
                    response += f"• {pattern}\\n"
                response += "\\n"
            
            anomalies = pattern_analysis.get("anomalies", [])
            if anomalies:
                response += f"⚠️ **ANOMALIAS DETECTADAS**\\n"
                for anomaly in anomalies[:3]:  # Top 3
                    response += f"• {anomaly}\\n"
                response += "\\n"
        
        # AI analysis
        ai_analysis = analysis.get("ai_analysis", "")
        if ai_analysis and ai_analysis.strip():
            response += f"🤖 **ANÁLISE INTELIGENTE**\\n\\n{ai_analysis}\\n\\n"
        
        # Data display
        if real_data.get("success") and real_data.get("data"):
            response += self.data_integrator.format_data_for_display(real_data)
        
        return response


# Factory function
def create_ai_analyzer(groq_api_key: Optional[str] = None) -> AIAnalyzer:
    """Create an AI analyzer instance."""
    return AIAnalyzer(groq_api_key=groq_api_key)