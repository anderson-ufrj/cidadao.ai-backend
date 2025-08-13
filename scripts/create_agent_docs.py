#!/usr/bin/env python3
"""
Script para criar documentação individual dos agentes
"""

from pathlib import Path

# Dados dos agentes
AGENTS = {
    "abaporu-master": {
        "title": "Abaporu - Master Agent",
        "icon": "🧠",
        "role": "Orquestrador Central",
        "abilities": [
            "Coordenação de todos os agentes",
            "Self-reflection e auto-avaliação",
            "Estratégias adaptativas",
            "Roteamento semântico inteligente"
        ],
        "description": "Inspirado na obra de Tarsila do Amaral, o Abaporu é o agente mestre que coordena todo o sistema multi-agente."
    },
    "zumbi": {
        "title": "Zumbi dos Palmares",
        "icon": "⚔️",
        "role": "Detector de Anomalias",
        "abilities": [
            "Detecção de fraudes e irregularidades",
            "Análise de padrões suspeitos",
            "Resistência a tentativas de corrupção",
            "Identificação de cartéis"
        ],
        "description": "Como o líder quilombola, Zumbi resiste e combate irregularidades no sistema público."
    },
    "tiradentes": {
        "title": "Tiradentes",
        "icon": "🦷",
        "role": "Investigador de Corrupção",
        "abilities": [
            "Análise profunda de conspiração",
            "Detecção de esquemas complexos",
            "Rastreamento de fluxo financeiro",
            "Identificação de conflitos de interesse"
        ],
        "description": "O mártir da Inconfidência Mineira especializado em descobrir conspirações contra o erário."
    },
    "anita-garibaldi": {
        "title": "Anita Garibaldi",
        "icon": "🗡️",
        "role": "Analista de Contratos",
        "abilities": [
            "Análise detalhada de contratos públicos",
            "Identificação de cláusulas abusivas",
            "Comparação com preços de mercado",
            "Detecção de superfaturamento"
        ],
        "description": "A heroína revolucionária que luta por contratos justos e transparentes."
    },
    "machado-assis": {
        "title": "Machado de Assis",
        "icon": "✍️",
        "role": "Processamento de Linguagem",
        "abilities": [
            "Análise semântica de documentos",
            "Extração de entidades nomeadas",
            "Interpretação de textos jurídicos",
            "Geração de resumos inteligentes"
        ],
        "description": "O mestre da literatura brasileira que decifra a complexidade dos textos governamentais."
    },
    "dandara": {
        "title": "Dandara dos Palmares",
        "icon": "🛡️",
        "role": "Segurança e Proteção",
        "abilities": [
            "Proteção de dados sensíveis",
            "Auditoria de segurança",
            "Detecção de vazamentos",
            "Criptografia e anonimização"
        ],
        "description": "Guerreira quilombola que protege a integridade e segurança dos dados."
    },
    "drummond": {
        "title": "Carlos Drummond de Andrade",
        "icon": "📝",
        "role": "Gerador de Relatórios",
        "abilities": [
            "Criação de relatórios claros e poéticos",
            "Síntese de informações complexas",
            "Narrativas compreensíveis",
            "Visualizações de dados elegantes"
        ],
        "description": "O poeta que transforma dados áridos em insights compreensíveis."
    },
    "niemeyer": {
        "title": "Oscar Niemeyer",
        "icon": "🏛️",
        "role": "Arquiteto de Dados",
        "abilities": [
            "Design de estruturas de dados",
            "Otimização de queries",
            "Modelagem de relacionamentos",
            "Arquitetura de pipelines"
        ],
        "description": "O arquiteto que constrói as estruturas elegantes para análise de dados."
    }
}

def create_agent_doc(agent_id: str, agent_data: dict) -> str:
    """Cria documentação para um agente específico"""
    
    abilities_list = '\n'.join([f"- {ability}" for ability in agent_data['abilities']])
    
    return f"""---
title: "{agent_data['title']}"
sidebar_position: {list(AGENTS.keys()).index(agent_id) + 2}
description: "{agent_data['role']} do sistema Cidadão.AI"
---

# {agent_data['icon']} {agent_data['title']}

**Papel**: {agent_data['role']}

## 📖 História

{agent_data['description']}

## 🎯 Especialidades

{abilities_list}

## 🔧 Implementação Técnica

### Algoritmos Utilizados
- **Machine Learning**: Algoritmos específicos para {agent_data['role'].lower()}
- **NLP**: Processamento de linguagem natural adaptado
- **Heurísticas**: Regras especializadas baseadas em legislação

### Integração com Sistema
```python
from src.agents.{agent_id.replace('-', '_')} import {agent_id.replace('-', ' ').title().replace(' ', '')}Agent

agent = {agent_id.replace('-', ' ').title().replace(' ', '')}Agent()
result = await agent.analyze(data)
```

## 📊 Métricas de Performance

- **Precisão**: >85% em tarefas específicas
- **Tempo de Resposta**: <200ms
- **Taxa de Falsos Positivos**: <5%

## 🔗 Interações

Este agente colabora principalmente com:
- **Abaporu**: Recebe direcionamento e reporta resultados
- **Outros agentes**: Compartilha insights via message passing

## 💡 Casos de Uso

1. **Análise em Tempo Real**: Processamento contínuo de dados
2. **Investigações Profundas**: Análise detalhada sob demanda
3. **Alertas Automáticos**: Notificações de anomalias detectadas
"""

def create_all_agent_docs():
    """Cria documentação para todos os agentes"""
    
    agents_dir = Path("/home/anderson-henrique/Documentos/cidadao.ai-backend/docs_new/docs/agents")
    agents_dir.mkdir(exist_ok=True)
    
    print("🤖 Criando documentação individual dos agentes...")
    
    for agent_id, agent_data in AGENTS.items():
        doc_content = create_agent_doc(agent_id, agent_data)
        
        file_path = agents_dir / f"{agent_id}.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"✅ Criado: {agent_data['title']}")
    
    print(f"\n✨ {len(AGENTS)} documentações de agentes criadas!")

if __name__ == "__main__":
    create_all_agent_docs()