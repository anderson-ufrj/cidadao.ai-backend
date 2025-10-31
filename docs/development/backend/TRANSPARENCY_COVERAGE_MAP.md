# Mapa de Cobertura de Transparência do Brasil

## Visão Geral

Sistema de visualização interativa da cobertura de APIs de transparência pública no Brasil, mostrando em tempo real quais APIs estão funcionando, degradadas ou indisponíveis por estado.

**Data de Criação**: 2025-10-23
**Versão**: 1.0
**Status**: Em Planejamento

---

## 1. Objetivos

### 1.1 Objetivos Principais

1. **Transparência sobre Transparência**: Mostrar publicamente quais órgãos governamentais oferecem acesso programático aos seus dados
2. **Pressão Social**: Evidenciar estados/órgãos que não disponibilizam APIs, incentivando melhorias
3. **Monitoramento**: Acompanhar disponibilidade e saúde das APIs ao longo do tempo
4. **Credibilidade**: Demonstrar que o Cidadão.AI usa dados reais (ou explicar por que não consegue)
5. **Educação Cívica**: Informar cidadãos sobre seus direitos de acesso à informação pública

### 1.2 Benefícios

- **Para Usuários**: Entendem limitações e origens dos dados
- **Para Desenvolvedores**: Sabem quais APIs podem integrar
- **Para Órgãos Públicos**: Recebem feedback sobre infraestrutura
- **Para Ativismo**: Base para campanhas de transparência

---

## 2. Análise de Abordagens

### 2.1 Comparação de Opções

| Critério | Opção 1: Dinâmico | Opção 2: Híbrido (Cache) | Opção 3: Estático |
|----------|-------------------|--------------------------|-------------------|
| **Response Time** | 30-60s | <100ms ✅ | <10ms ✅ |
| **Atualização** | Tempo real ✅ | A cada 6h | Manual ❌ |
| **Precisão** | 100% ✅ | ~99% ✅ | Pode desatualizar ❌ |
| **Carga nas APIs** | Alta ❌ | Baixa ✅ | Zero ✅ |
| **Histórico** | Não ❌ | Sim ✅ | Manual |
| **UX** | Ruim (lento) ❌ | Excelente ✅ | Excelente ✅ |
| **Complexidade** | Baixa | Média | Muito baixa |

### 2.2 Decisão: Opção 2 (Híbrido com Cache)

**Justificativa**:
- Melhor equilíbrio entre precisão e performance
- Infraestrutura já existe (Celery Beat configurado)
- Permite histórico e análise temporal
- Escalável para 27 estados
- Não sobrecarrega APIs governamentais

---

## 3. Arquitetura Técnica

### 3.1 Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          TransparencyMap Component                  │    │
│  │  - Mapa interativo do Brasil (SVG)                  │    │
│  │  - Color coding por status                          │    │
│  │  - Tooltips com detalhes                            │    │
│  └──────────────────┬──────────────────────────────────┘    │
└─────────────────────┼──────────────────────────────────────┘
                      │ GET /api/v1/transparency/coverage/map
                      │
┌─────────────────────▼──────────────────────────────────────┐
│                     BACKEND (FastAPI)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        Coverage Map Endpoint                        │   │
│  │  - Retorna snapshot mais recente do cache          │   │
│  │  - Response time: <100ms                            │   │
│  │  - Fallback: gera on-demand (primeira vez)         │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │ Query
                      │
┌─────────────────────▼──────────────────────────────────────┐
│                    PostgreSQL                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  transparency_coverage_snapshots                    │   │
│  │  - id, snapshot_date, coverage_data (JSON)         │   │
│  │  - summary_stats (JSON)                             │   │
│  │  - state_code, state_status, coverage_percentage   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────▲──────────────────────────────────────┘
                      │ Insert new snapshot
                      │ (every 6 hours)
┌─────────────────────┴──────────────────────────────────────┐
│                   CELERY BEAT                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   update_transparency_coverage task                 │   │
│  │   - Schedule: crontab(hour='*/6')                   │   │
│  │   - Runs HealthCheckService.generate_report()      │   │
│  │   - Transforms to map format                        │   │
│  │   - Saves to PostgreSQL                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Fluxo de Dados

1. **Atualização Periódica (Celery Beat)**:
   ```
   Celery Beat (6h) → Health Check (13 APIs) → Transform to Map Format
                    → Save Snapshot to PostgreSQL → Log completion
   ```

2. **Requisição do Frontend**:
   ```
   Frontend → GET /coverage/map → Query latest snapshot → Return JSON (<100ms)
   ```

3. **Primeira Execução (Cold Start)**:
   ```
   Frontend → GET /coverage/map → No snapshot found → Generate on-demand
           → Save to DB → Return JSON (30-60s first time)
   ```

---

## 4. Estrutura de Dados

### 4.1 Modelo de Banco de Dados

```python
# src/models/transparency_coverage.py

from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from datetime import datetime

class TransparencyCoverageSnapshot(Base):
    """Snapshot of transparency API coverage for Brazil map visualization"""
    __tablename__ = "transparency_coverage_snapshots"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Timestamp
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    # Complete coverage data (JSON)
    coverage_data = Column(JSON, nullable=False)
    # Structure: { "last_update": "...", "states": {...}, "summary": {...} }

    # Summary statistics (JSON) - for quick queries
    summary_stats = Column(JSON, nullable=False)
    # Structure: { "total_states": 27, "states_with_apis": 5, ... }

    # Per-state data (for state-specific queries)
    state_code = Column(String(2), index=True)  # "SP", "MG", "RJ", etc.
    state_status = Column(String(20))  # "healthy", "degraded", "no_api", "unknown"
    coverage_percentage = Column(Float)  # 0.0 to 100.0

    # Indexes for performance
    __table_args__ = (
        Index('idx_snapshot_date_desc', snapshot_date.desc()),
        Index('idx_state_coverage', state_code, coverage_percentage),
    )
```

### 4.2 Formato JSON do Endpoint

```json
{
  "last_update": "2025-10-23T14:30:00Z",
  "cache_info": {
    "cached": true,
    "last_update": "2025-10-23T14:00:00Z",
    "age_minutes": 30
  },
  "states": {
    "SP": {
      "name": "São Paulo",
      "apis": [
        {
          "id": "SP-tce",
          "name": "TCE-SP (Tribunal de Contas do Estado)",
          "type": "tce",
          "status": "healthy",
          "response_time_ms": 1200,
          "last_check": "2025-10-23T14:29:45Z",
          "coverage": ["contracts", "expenses", "biddings"],
          "endpoints": [
            "/json/municipios",
            "/json/contratos",
            "/json/despesas"
          ]
        },
        {
          "id": "SP-ckan",
          "name": "Portal CKAN São Paulo",
          "type": "ckan",
          "status": "healthy",
          "response_time_ms": 890,
          "coverage": ["datasets", "open_data"],
          "endpoints": ["/api/3/action/package_list"]
        }
      ],
      "overall_status": "healthy",
      "coverage_percentage": 100.0,
      "color": "#22c55e"
    },
    "MG": {
      "name": "Minas Gerais",
      "apis": [
        {
          "id": "MG-tce",
          "name": "TCE-MG (Portal de Dados Abertos)",
          "type": "tce",
          "status": "blocked",
          "error": "Firewall authentication required - No API REST available",
          "error_details": {
            "issue": "Portal redesigned without API support (Nov 2024)",
            "legal_basis": "Decreto Estadual MG 48.383/2022 - Art. 22 (Dados Abertos)",
            "evidence": "https://dadosabertos.tce.mg.gov.br/ returns HTML only"
          },
          "issue_url": "https://github.com/anderson-ufrj/cidadao.ai/issues/MG-TCE-NO-API",
          "action": "Pedido LAI protocolado em 23/10/2025 - Aguardando resposta (20 dias)",
          "escalation": {
            "step": 1,
            "next_step": "Recurso à CGE-MG após 20 dias",
            "contacts": [
              {"entity": "TCE-MG e-SIC", "url": "https://www.tce.mg.gov.br/"},
              {"entity": "CGE-MG", "email": "transparencia@cge.mg.gov.br"}
            ]
          }
        }
      ],
      "overall_status": "no_api",
      "coverage_percentage": 0.0,
      "color": "#ef4444"
    },
    "RO": {
      "name": "Rondônia",
      "apis": [
        {
          "id": "RO-state",
          "name": "Portal da Transparência RO",
          "type": "state_portal",
          "status": "server_error",
          "error": "HTTP 500 Internal Server Error",
          "error_details": {
            "issue": "Server-side infrastructure problem",
            "tested_url": "https://portaldatransparencia.ro.gov.br/DadosAbertos/Api/",
            "fix_responsibility": "Governo de Rondônia (not fixable from our side)"
          },
          "last_working": null,
          "action": "Monitored automatically - Will recover when state fixes infrastructure"
        }
      ],
      "overall_status": "degraded",
      "coverage_percentage": 0.0,
      "color": "#f59e0b"
    },
    "CE": {
      "name": "Ceará",
      "apis": [
        {
          "id": "CE-tce",
          "name": "TCE-CE",
          "type": "tce",
          "status": "timeout",
          "error": "Request timeout after 90 seconds",
          "error_details": {
            "issue": "API responding extremely slowly (273+ seconds)",
            "likely_cause": "Server offline or severely overloaded",
            "average_response_time": "273000ms"
          },
          "last_working": "2025-09-15T10:30:00Z",
          "action": "Monitoring for recovery"
        }
      ],
      "overall_status": "degraded",
      "coverage_percentage": 0.0,
      "color": "#f59e0b"
    }
  },
  "summary": {
    "total_states": 27,
    "states_with_apis": 5,
    "states_working": 5,
    "states_degraded": 2,
    "states_no_api": 20,
    "overall_coverage_percentage": 18.5,
    "api_breakdown": {
      "healthy": 5,
      "degraded": 0,
      "unhealthy": 8,
      "blocked": 1,
      "unknown": 0
    }
  },
  "issues": [
    {
      "severity": "critical",
      "title": "TCE-MG removed API in portal redesign",
      "description": "Portal de Dados Abertos do TCE-MG não oferece API REST, apenas visualização web. Violação do Decreto Estadual 48.383/2022.",
      "affected_states": ["MG"],
      "action": "Pedido LAI protocolado - Acompanhe: [link]",
      "legal_basis": "Decreto MG 48.383/2022, Art. 22"
    },
    {
      "severity": "high",
      "title": "8 APIs with infrastructure issues",
      "description": "Multiple state transparency APIs are offline or timing out (CE, RJ, BA, PE, RO)",
      "affected_states": ["CE", "RJ", "BA", "PE", "RO"],
      "action": "Monitoring for recovery - Issues on state server side"
    }
  ],
  "call_to_action": {
    "title": "Cobre Transparência do Seu Estado",
    "description": "Seu estado não tem API de transparência? Protocole um pedido via Lei de Acesso à Informação!",
    "guide_url": "https://docs.cidadao.ai/activism/lai-request-guide"
  }
}
```

### 4.3 Status Codes e Cores

| Status | Descrição | Cor | Hex Code |
|--------|-----------|-----|----------|
| `healthy` | API funcionando normalmente | Verde | `#22c55e` |
| `degraded` | API com problemas temporários | Amarelo | `#f59e0b` |
| `unhealthy` | API offline ou erro persistente | Vermelho | `#ef4444` |
| `blocked` | API bloqueada por firewall/auth | Vermelho escuro | `#dc2626` |
| `no_api` | Estado não possui API | Cinza | `#6b7280` |
| `unknown` | Status não verificado | Cinza claro | `#94a3b8` |

---

## 5. Implementação Backend

### 5.1 Task Celery (Atualização Periódica)

```python
# src/infrastructure/queue/tasks/coverage_tasks.py

from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from src.infrastructure.database import SessionLocal
from src.services.transparency_apis.health_check import HealthCheckService
from src.models.transparency_coverage import TransparencyCoverageSnapshot

logger = logging.getLogger(__name__)

@shared_task(name="update_transparency_coverage", bind=True)
def update_transparency_coverage(self):
    """
    Update transparency coverage map snapshot

    Runs every 6 hours via Celery Beat to update API coverage status
    for all Brazilian states.

    Returns:
        dict: Summary of the update operation
    """
    try:
        logger.info("Starting transparency coverage update...")

        # Create database session
        db: Session = SessionLocal()

        try:
            # Run comprehensive health check on all APIs
            health_service = HealthCheckService()
            health_report = health_service.generate_report()  # Async call

            logger.info(f"Health check completed: {health_report.get('summary')}")

            # Transform health report into map-friendly format
            coverage_data = transform_to_map_format(health_report)

            # Create snapshot entry
            snapshot = TransparencyCoverageSnapshot(
                snapshot_date=datetime.utcnow(),
                coverage_data=coverage_data,
                summary_stats=coverage_data["summary"]
            )

            # Also create per-state entries for faster queries
            for state_code, state_info in coverage_data["states"].items():
                state_snapshot = TransparencyCoverageSnapshot(
                    snapshot_date=datetime.utcnow(),
                    coverage_data={"state": state_info},
                    summary_stats=state_info,
                    state_code=state_code,
                    state_status=state_info["overall_status"],
                    coverage_percentage=state_info["coverage_percentage"]
                )
                db.add(state_snapshot)

            # Add main snapshot
            db.add(snapshot)
            db.commit()

            logger.info(
                f"Coverage map updated successfully. "
                f"States with APIs: {coverage_data['summary']['states_with_apis']}/27, "
                f"Working: {coverage_data['summary']['states_working']}"
            )

            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": coverage_data["summary"]
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating coverage map: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Fatal error in coverage update task: {str(e)}", exc_info=True)
        # Celery will retry automatically based on retry policy
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


def transform_to_map_format(health_report: dict) -> dict:
    """
    Transform HealthCheckService report into map-friendly format

    Args:
        health_report: Output from HealthCheckService.generate_report()

    Returns:
        dict: Map-formatted data with states, APIs, and summary
    """
    from src.services.transparency_apis.registry import registry

    # State names mapping
    STATE_NAMES = {
        "SP": "São Paulo",
        "RJ": "Rio de Janeiro",
        "MG": "Minas Gerais",
        "RS": "Rio Grande do Sul",
        "SC": "Santa Catarina",
        "BA": "Bahia",
        "PE": "Pernambuco",
        "CE": "Ceará",
        "RO": "Rondônia",
        "BR": "Federal"  # Para Portal da Transparência Federal
    }

    # API to State mapping
    API_TO_STATE = {
        "SP-tce": "SP", "SP-ckan": "SP",
        "RJ-tce": "RJ", "RJ-ckan": "RJ",
        "MG-tce": "MG",
        "RS-ckan": "RS",
        "SC-ckan": "SC",
        "BA-tce": "BA", "BA-ckan": "BA",
        "PE-tce": "PE",
        "CE-tce": "CE",
        "RO-state": "RO",
        "FEDERAL-portal": "BR",
    }

    states_map = {}

    # Process each API from health report
    for api_key, state_code in API_TO_STATE.items():
        # Initialize state if not exists
        if state_code not in states_map:
            states_map[state_code] = {
                "name": STATE_NAMES.get(state_code, state_code),
                "apis": [],
                "overall_status": "unknown",
                "coverage_percentage": 0.0,
                "color": "#94a3b8"  # Default gray
            }

        # Find API details in health report
        api_detail = extract_api_detail(health_report, api_key)
        if api_detail:
            states_map[state_code]["apis"].append(api_detail)

    # Calculate overall status per state
    for state_code, state_info in states_map.items():
        apis = state_info["apis"]
        if not apis:
            state_info["overall_status"] = "no_api"
            state_info["coverage_percentage"] = 0.0
            state_info["color"] = "#6b7280"  # Gray
            continue

        healthy_count = sum(1 for api in apis if api["status"] == "healthy")
        degraded_count = sum(1 for api in apis if api["status"] == "degraded")

        state_info["coverage_percentage"] = (healthy_count / len(apis)) * 100

        if healthy_count == len(apis):
            state_info["overall_status"] = "healthy"
            state_info["color"] = "#22c55e"  # Green
        elif healthy_count > 0 or degraded_count > 0:
            state_info["overall_status"] = "degraded"
            state_info["color"] = "#f59e0b"  # Yellow
        else:
            state_info["overall_status"] = "unhealthy"
            state_info["color"] = "#ef4444"  # Red

    # Calculate summary statistics
    summary = calculate_summary_stats(states_map)

    return {
        "last_update": datetime.utcnow().isoformat(),
        "states": states_map,
        "summary": summary,
        "issues": extract_known_issues(states_map),
        "call_to_action": {
            "title": "Cobre Transparência do Seu Estado",
            "description": "Seu estado não tem API de transparência? Protocole um pedido via Lei de Acesso à Informação!",
            "guide_url": "https://docs.cidadao.ai/activism/lai-request-guide"
        }
    }


def extract_api_detail(health_report: dict, api_key: str) -> dict:
    """Extract detailed information for a specific API from health report"""
    # Implementation depends on HealthCheckService output structure
    # This is a placeholder - adjust based on actual health report format
    api_details = health_report.get("apis", {}).get("details", {})

    for category in ["healthy", "degraded", "unhealthy"]:
        if api_key in health_report.get("apis", {}).get(category, []):
            detail = api_details.get(api_key, {})
            return {
                "id": api_key,
                "name": detail.get("name", api_key),
                "type": detect_api_type(api_key),
                "status": category.replace("unhealthy", "unhealthy"),
                "response_time_ms": detail.get("response_time_ms"),
                "last_check": detail.get("last_check"),
                "error": detail.get("error"),
                "coverage": detail.get("coverage", [])
            }

    return None


def detect_api_type(api_key: str) -> str:
    """Detect API type from key"""
    if "tce" in api_key:
        return "tce"
    elif "ckan" in api_key:
        return "ckan"
    elif "state" in api_key:
        return "state_portal"
    elif "portal" in api_key:
        return "federal"
    return "unknown"


def calculate_summary_stats(states_map: dict) -> dict:
    """Calculate summary statistics from states map"""
    total_states = 27  # Brazil has 26 states + 1 DF
    states_with_apis = len([s for s in states_map.values() if s["apis"]])
    states_working = len([s for s in states_map.values() if s["overall_status"] == "healthy"])
    states_degraded = len([s for s in states_map.values() if s["overall_status"] == "degraded"])
    states_no_api = total_states - states_with_apis

    # Calculate overall coverage percentage
    total_apis = sum(len(s["apis"]) for s in states_map.values())
    healthy_apis = sum(
        sum(1 for api in s["apis"] if api["status"] == "healthy")
        for s in states_map.values()
    )
    overall_coverage = (healthy_apis / total_apis * 100) if total_apis > 0 else 0

    return {
        "total_states": total_states,
        "states_with_apis": states_with_apis,
        "states_working": states_working,
        "states_degraded": states_degraded,
        "states_no_api": states_no_api,
        "overall_coverage_percentage": round(overall_coverage, 2),
        "api_breakdown": {
            "healthy": healthy_apis,
            "degraded": sum(
                sum(1 for api in s["apis"] if api["status"] == "degraded")
                for s in states_map.values()
            ),
            "unhealthy": sum(
                sum(1 for api in s["apis"] if api["status"] not in ["healthy", "degraded"])
                for s in states_map.values()
            )
        }
    }


def extract_known_issues(states_map: dict) -> list:
    """Extract list of known issues for display"""
    issues = []

    # Check for TCE-MG specific issue
    if "MG" in states_map and states_map["MG"]["overall_status"] == "no_api":
        issues.append({
            "severity": "critical",
            "title": "TCE-MG removed API in portal redesign",
            "description": "Portal de Dados Abertos do TCE-MG não oferece API REST. Violação do Decreto Estadual 48.383/2022.",
            "affected_states": ["MG"],
            "action": "Pedido LAI protocolado - Acompanhe: github.com/anderson-ufrj/cidadao.ai/issues/MG-TCE",
            "legal_basis": "Decreto MG 48.383/2022, Art. 22"
        })

    # Check for multiple infrastructure issues
    unhealthy_states = [
        code for code, info in states_map.items()
        if info["overall_status"] in ["unhealthy", "degraded"]
    ]

    if len(unhealthy_states) >= 3:
        issues.append({
            "severity": "high",
            "title": f"{len(unhealthy_states)} estados com problemas de infraestrutura",
            "description": "Múltiplas APIs offline ou com timeout",
            "affected_states": unhealthy_states,
            "action": "Monitoramento ativo - Problemas de infraestrutura estadual"
        })

    return issues
```

### 5.2 Endpoint FastAPI

```python
# src/api/routes/transparency.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from src.infrastructure.database import get_db
from src.models.transparency_coverage import TransparencyCoverageSnapshot
from src.services.transparency_apis.health_check import HealthCheckService

router = APIRouter()


@router.get("/coverage/map", tags=["Transparency Coverage"])
async def get_coverage_map(
    include_history: bool = Query(
        default=False,
        description="Include last 7 days of historical snapshots"
    ),
    db: Session = Depends(get_db)
):
    """
    Get transparency API coverage map for Brazil

    Returns cached status of all transparency APIs by state, including:
    - Current health status per API
    - Error details and troubleshooting info
    - Legal basis for missing APIs
    - Call-to-action for civic engagement

    **Response Time**: <100ms (cached), 30-60s on first request (cold start)

    **Update Frequency**: Every 6 hours via Celery Beat

    **Parameters**:
    - `include_history`: Include last 7 days of snapshots for trend analysis

    **Example Response**:
    ```json
    {
      "last_update": "2025-10-23T14:30:00Z",
      "cache_info": {
        "cached": true,
        "age_minutes": 30
      },
      "states": {
        "SP": {
          "name": "São Paulo",
          "apis": [...],
          "overall_status": "healthy",
          "coverage_percentage": 100.0
        }
      },
      "summary": {
        "total_states": 27,
        "states_working": 5
      }
    }
    ```
    """

    # Query latest snapshot
    latest_snapshot = db.query(TransparencyCoverageSnapshot).filter(
        TransparencyCoverageSnapshot.state_code.is_(None)  # Main snapshot (not per-state)
    ).order_by(
        TransparencyCoverageSnapshot.snapshot_date.desc()
    ).first()

    if not latest_snapshot:
        # Cold start: No snapshot exists yet
        # Generate on-demand (this will be slow the first time)
        health_service = HealthCheckService()
        health_report = await health_service.generate_report()

        from src.infrastructure.queue.tasks.coverage_tasks import transform_to_map_format
        coverage_data = transform_to_map_format(health_report)

        # Save for next time
        snapshot = TransparencyCoverageSnapshot(
            snapshot_date=datetime.utcnow(),
            coverage_data=coverage_data,
            summary_stats=coverage_data["summary"]
        )
        db.add(snapshot)
        db.commit()

        coverage_data["cache_info"] = {
            "cached": False,
            "last_update": datetime.utcnow().isoformat(),
            "age_minutes": 0,
            "note": "Generated on-demand (first request)"
        }
    else:
        # Return cached data
        coverage_data = latest_snapshot.coverage_data
        age_minutes = int((datetime.utcnow() - latest_snapshot.snapshot_date).total_seconds() / 60)

        coverage_data["cache_info"] = {
            "cached": True,
            "last_update": latest_snapshot.snapshot_date.isoformat(),
            "age_minutes": age_minutes
        }

    # Include historical data if requested
    if include_history:
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        history_snapshots = db.query(TransparencyCoverageSnapshot).filter(
            TransparencyCoverageSnapshot.state_code.is_(None),
            TransparencyCoverageSnapshot.snapshot_date >= seven_days_ago
        ).order_by(
            TransparencyCoverageSnapshot.snapshot_date.desc()
        ).all()

        coverage_data["history"] = [
            {
                "date": snap.snapshot_date.isoformat(),
                "summary": snap.summary_stats
            }
            for snap in history_snapshots
        ]

    return coverage_data


@router.get("/coverage/state/{state_code}", tags=["Transparency Coverage"])
async def get_state_coverage(
    state_code: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed coverage information for a specific state

    **Parameters**:
    - `state_code`: Two-letter state code (e.g., "SP", "MG", "RJ")

    **Returns**:
    - Detailed API status for the state
    - Historical trends (last 7 days)
    - Specific issues and recommended actions
    """

    state_code = state_code.upper()

    # Get latest state snapshot
    latest = db.query(TransparencyCoverageSnapshot).filter(
        TransparencyCoverageSnapshot.state_code == state_code
    ).order_by(
        TransparencyCoverageSnapshot.snapshot_date.desc()
    ).first()

    if not latest:
        return {
            "error": "State not found",
            "state_code": state_code,
            "message": "No coverage data available for this state"
        }

    # Get historical trend (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    history = db.query(TransparencyCoverageSnapshot).filter(
        TransparencyCoverageSnapshot.state_code == state_code,
        TransparencyCoverageSnapshot.snapshot_date >= seven_days_ago
    ).order_by(
        TransparencyCoverageSnapshot.snapshot_date.desc()
    ).all()

    return {
        "state_code": state_code,
        "current": latest.coverage_data,
        "history": [
            {
                "date": snap.snapshot_date.isoformat(),
                "status": snap.state_status,
                "coverage_percentage": snap.coverage_percentage
            }
            for snap in history
        ],
        "trend": analyze_trend(history)
    }


def analyze_trend(history: list) -> dict:
    """Analyze coverage trend over time"""
    if len(history) < 2:
        return {"trend": "insufficient_data"}

    recent = history[0].coverage_percentage
    older = history[-1].coverage_percentage

    if recent > older + 10:
        return {"trend": "improving", "change": recent - older}
    elif recent < older - 10:
        return {"trend": "degrading", "change": recent - older}
    else:
        return {"trend": "stable", "change": recent - older}
```

### 5.3 Configuração Celery Beat

```python
# src/infrastructure/queue/celeryconfig.py

from celery.schedules import crontab

# ... existing config ...

CELERYBEAT_SCHEDULE = {
    # ... existing tasks ...

    'update-transparency-coverage-map': {
        'task': 'update_transparency_coverage',
        'schedule': crontab(hour='*/6'),  # Every 6 hours (0:00, 6:00, 12:00, 18:00)
        'options': {
            'expires': 21600,  # 6 hours (don't execute if delayed)
        }
    },
}
```

---

## 6. Implementação Frontend

### 6.1 Componente React/TypeScript

```typescript
// frontend/src/components/TransparencyMap.tsx

import { useEffect, useState } from 'react';
import { BrazilMap } from './BrazilMap';
import { StateDetailModal } from './StateDetailModal';

interface APIInfo {
  id: string;
  name: string;
  type: string;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'blocked' | 'no_api';
  response_time_ms?: number;
  error?: string;
  error_details?: Record<string, any>;
  action?: string;
}

interface StateInfo {
  name: string;
  apis: APIInfo[];
  overall_status: string;
  coverage_percentage: number;
  color: string;
}

interface CoverageMapData {
  last_update: string;
  cache_info?: {
    cached: boolean;
    last_update: string;
    age_minutes: number;
  };
  states: Record<string, StateInfo>;
  summary: {
    total_states: number;
    states_with_apis: number;
    states_working: number;
    states_degraded: number;
    states_no_api: number;
    overall_coverage_percentage: number;
  };
  issues?: Array<{
    severity: string;
    title: string;
    description: string;
    affected_states: string[];
    action: string;
  }>;
  call_to_action?: {
    title: string;
    description: string;
    guide_url: string;
  };
}

export function TransparencyMap() {
  const [mapData, setMapData] = useState<CoverageMapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCoverageData();
  }, []);

  const fetchCoverageData = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        'https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map'
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: CoverageMapData = await response.json();
      setMapData(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch coverage data:', err);
      setError('Erro ao carregar dados de cobertura. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error || !mapData) {
    return (
      <div className="error-container">
        <p>{error || 'Dados não disponíveis'}</p>
        <button onClick={fetchCoverageData}>Tentar Novamente</button>
      </div>
    );
  }

  return (
    <div className="transparency-map-container">
      {/* Header */}
      <header className="map-header">
        <h1>Mapa de Transparência do Brasil</h1>
        <p className="subtitle">
          Cobertura de APIs de Transparência Pública por Estado
        </p>

        {mapData.cache_info && (
          <div className="cache-info">
            <span className="icon">⏱️</span>
            Atualizado há {mapData.cache_info.age_minutes} minutos
            {mapData.cache_info.age_minutes > 360 && (
              <span className="warning"> (dados podem estar desatualizados)</span>
            )}
          </div>
        )}
      </header>

      {/* Interactive Brazil Map */}
      <div className="map-section">
        <BrazilMap
          states={mapData.states}
          onStateClick={(stateCode) => setSelectedState(stateCode)}
          colorScheme={{
            healthy: '#22c55e',
            degraded: '#f59e0b',
            unhealthy: '#ef4444',
            blocked: '#dc2626',
            no_api: '#6b7280',
            unknown: '#94a3b8'
          }}
        />
      </div>

      {/* Summary Statistics */}
      <div className="summary-stats">
        <StatCard
          icon="🗺️"
          label="Estados com APIs"
          value={`${mapData.summary.states_with_apis}/27`}
          subtitle={`${((mapData.summary.states_with_apis / 27) * 100).toFixed(1)}% do Brasil`}
        />
        <StatCard
          icon="✅"
          label="APIs Funcionando"
          value={mapData.summary.states_working}
          color="green"
          subtitle="100% de disponibilidade"
        />
        <StatCard
          icon="⚠️"
          label="APIs Degradadas"
          value={mapData.summary.states_degraded}
          color="yellow"
          subtitle="Com problemas temporários"
        />
        <StatCard
          icon="📊"
          label="Cobertura Nacional"
          value={`${mapData.summary.overall_coverage_percentage.toFixed(1)}%`}
          color={
            mapData.summary.overall_coverage_percentage > 50 ? 'green' :
            mapData.summary.overall_coverage_percentage > 20 ? 'yellow' : 'red'
          }
        />
      </div>

      {/* Known Issues Section */}
      {mapData.issues && mapData.issues.length > 0 && (
        <div className="issues-section">
          <h2>Problemas Conhecidos</h2>
          {mapData.issues.map((issue, idx) => (
            <IssueCard key={idx} issue={issue} />
          ))}
        </div>
      )}

      {/* Call to Action */}
      {mapData.call_to_action && (
        <div className="call-to-action">
          <h3>{mapData.call_to_action.title}</h3>
          <p>{mapData.call_to_action.description}</p>
          <a
            href={mapData.call_to_action.guide_url}
            target="_blank"
            rel="noopener noreferrer"
            className="cta-button"
          >
            Ver Guia Completo →
          </a>
        </div>
      )}

      {/* State Detail Modal */}
      {selectedState && (
        <StateDetailModal
          stateCode={selectedState}
          stateData={mapData.states[selectedState]}
          onClose={() => setSelectedState(null)}
        />
      )}
    </div>
  );
}

// Helper Components
function StatCard({ icon, label, value, subtitle, color }: any) {
  return (
    <div className={`stat-card stat-card-${color || 'default'}`}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
        {subtitle && <div className="stat-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
}

function IssueCard({ issue }: { issue: any }) {
  const severityColors = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'blue'
  };

  return (
    <div className={`issue-card issue-${issue.severity}`}>
      <div className="issue-header">
        <span className={`severity-badge ${severityColors[issue.severity]}`}>
          {issue.severity.toUpperCase()}
        </span>
        <h3>{issue.title}</h3>
      </div>
      <p className="issue-description">{issue.description}</p>
      <div className="issue-details">
        <div className="affected-states">
          <strong>Estados afetados:</strong> {issue.affected_states.join(', ')}
        </div>
        {issue.action && (
          <div className="issue-action">
            <strong>Ação:</strong> {issue.action}
          </div>
        )}
        {issue.legal_basis && (
          <div className="legal-basis">
            <strong>Base legal:</strong> {issue.legal_basis}
          </div>
        )}
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="loading-skeleton">
      <div className="skeleton-header" />
      <div className="skeleton-map" />
      <div className="skeleton-stats" />
    </div>
  );
}
```

### 6.2 Componente BrazilMap (SVG Interativo)

```typescript
// frontend/src/components/BrazilMap.tsx

import { useState } from 'react';
import './BrazilMap.css';

interface BrazilMapProps {
  states: Record<string, any>;
  onStateClick: (stateCode: string) => void;
  colorScheme: Record<string, string>;
}

export function BrazilMap({ states, onStateClick, colorScheme }: BrazilMapProps) {
  const [hoveredState, setHoveredState] = useState<string | null>(null);

  const getStateColor = (stateCode: string): string => {
    const stateData = states[stateCode];
    if (!stateData) return colorScheme.unknown;

    return stateData.color || colorScheme[stateData.overall_status] || colorScheme.unknown;
  };

  const getStateTooltip = (stateCode: string): string => {
    const stateData = states[stateCode];
    if (!stateData) return `${stateCode}: Sem dados`;

    const apiCount = stateData.apis.length;
    const healthyCount = stateData.apis.filter((api: any) => api.status === 'healthy').length;

    return `${stateData.name}\n${healthyCount}/${apiCount} APIs funcionando\nCobertura: ${stateData.coverage_percentage.toFixed(1)}%`;
  };

  return (
    <div className="brazil-map">
      <svg
        viewBox="0 0 1000 1000"
        xmlns="http://www.w3.org/2000/svg"
        className="brazil-map-svg"
      >
        {/* SVG paths for each Brazilian state */}
        {/* Note: This is simplified - actual implementation would include all state paths */}

        {/* Example: São Paulo */}
        <path
          id="SP"
          d="M600,700 L650,720 L670,750 L640,780 L600,770 L580,740 Z"
          fill={getStateColor('SP')}
          stroke="#ffffff"
          strokeWidth="2"
          className="state-path"
          onMouseEnter={() => setHoveredState('SP')}
          onMouseLeave={() => setHoveredState(null)}
          onClick={() => onStateClick('SP')}
          style={{ cursor: 'pointer' }}
        >
          <title>{getStateTooltip('SP')}</title>
        </path>

        {/* Example: Minas Gerais */}
        <path
          id="MG"
          d="M650,600 L700,620 L720,660 L690,700 L650,690 L630,660 Z"
          fill={getStateColor('MG')}
          stroke="#ffffff"
          strokeWidth="2"
          className="state-path"
          onMouseEnter={() => setHoveredState('MG')}
          onMouseLeave={() => setHoveredState(null)}
          onClick={() => onStateClick('MG')}
          style={{ cursor: 'pointer' }}
        >
          <title>{getStateTooltip('MG')}</title>
        </path>

        {/* Additional states... */}
        {/* Full implementation would include all 27 Brazilian states */}
      </svg>

      {/* Floating tooltip for hovered state */}
      {hoveredState && (
        <div className="state-tooltip">
          {getStateTooltip(hoveredState).split('\n').map((line, idx) => (
            <div key={idx}>{line}</div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div className="map-legend">
        <h4>Legenda</h4>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: colorScheme.healthy }} />
          <span>APIs Funcionando</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: colorScheme.degraded }} />
          <span>APIs com Problemas</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: colorScheme.unhealthy }} />
          <span>APIs Offline</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: colorScheme.no_api }} />
          <span>Sem API</span>
        </div>
      </div>
    </div>
  );
}
```

---

## 7. Migração de Banco de Dados

### 7.1 Alembic Migration Script

```python
# migrations/versions/008_transparency_coverage_snapshots.py

"""Add transparency coverage snapshots table

Revision ID: 008_transparency_coverage
Revises: 007
Create Date: 2025-10-23 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '008_transparency_coverage'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Create transparency_coverage_snapshots table
    op.create_table(
        'transparency_coverage_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('snapshot_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('coverage_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('summary_stats', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('state_code', sa.String(length=2), nullable=True, index=True),
        sa.Column('state_status', sa.String(length=20), nullable=True),
        sa.Column('coverage_percentage', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index(
        'idx_snapshot_date_desc',
        'transparency_coverage_snapshots',
        [sa.text('snapshot_date DESC')]
    )
    op.create_index(
        'idx_state_coverage',
        'transparency_coverage_snapshots',
        ['state_code', 'coverage_percentage']
    )


def downgrade():
    op.drop_index('idx_state_coverage', table_name='transparency_coverage_snapshots')
    op.drop_index('idx_snapshot_date_desc', table_name='transparency_coverage_snapshots')
    op.drop_table('transparency_coverage_snapshots')
```

### 7.2 Executar Migração

```bash
# Criar migração
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic revision --autogenerate -m "Add transparency coverage snapshots"

# Aplicar migração
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic upgrade head

# Verificar
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic current
```

---

## 8. Testes

### 8.1 Testes Unitários

```python
# tests/unit/services/test_coverage_map.py

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.infrastructure.queue.tasks.coverage_tasks import (
    transform_to_map_format,
    extract_api_detail,
    calculate_summary_stats
)


class TestCoverageMapTransformation:
    """Test transformation of health report to map format"""

    def test_transform_basic_health_report(self):
        """Test basic transformation with healthy APIs"""
        health_report = {
            "apis": {
                "healthy": ["SP-tce", "SP-ckan"],
                "degraded": [],
                "unhealthy": [],
                "details": {
                    "SP-tce": {
                        "name": "TCE-SP",
                        "status": "healthy",
                        "response_time_ms": 1200
                    },
                    "SP-ckan": {
                        "name": "CKAN-SP",
                        "status": "healthy",
                        "response_time_ms": 890
                    }
                }
            }
        }

        result = transform_to_map_format(health_report)

        assert "SP" in result["states"]
        assert len(result["states"]["SP"]["apis"]) == 2
        assert result["states"]["SP"]["overall_status"] == "healthy"
        assert result["states"]["SP"]["coverage_percentage"] == 100.0

    def test_transform_with_mixed_status(self):
        """Test transformation with mixed API statuses"""
        health_report = {
            "apis": {
                "healthy": ["SP-tce"],
                "degraded": ["SP-ckan"],
                "unhealthy": [],
                "details": {
                    "SP-tce": {"name": "TCE-SP", "status": "healthy"},
                    "SP-ckan": {"name": "CKAN-SP", "status": "degraded"}
                }
            }
        }

        result = transform_to_map_format(health_report)

        assert result["states"]["SP"]["overall_status"] == "degraded"
        assert result["states"]["SP"]["coverage_percentage"] == 50.0

    def test_summary_statistics_calculation(self):
        """Test summary statistics calculation"""
        states_map = {
            "SP": {
                "apis": [
                    {"status": "healthy"},
                    {"status": "healthy"}
                ],
                "overall_status": "healthy"
            },
            "MG": {
                "apis": [
                    {"status": "unhealthy"}
                ],
                "overall_status": "unhealthy"
            }
        }

        summary = calculate_summary_stats(states_map)

        assert summary["total_states"] == 27
        assert summary["states_with_apis"] == 2
        assert summary["states_working"] == 1
        assert summary["overall_coverage_percentage"] > 0


class TestCoverageMapEndpoint:
    """Test coverage map API endpoint"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock()
        return session

    @pytest.mark.asyncio
    async def test_get_coverage_map_with_cache(self, mock_db_session):
        """Test endpoint returns cached data"""
        from src.api.routes.transparency import get_coverage_map

        # Mock snapshot in database
        mock_snapshot = Mock()
        mock_snapshot.coverage_data = {
            "last_update": "2025-10-23T14:00:00Z",
            "states": {},
            "summary": {}
        }
        mock_snapshot.snapshot_date = datetime.utcnow()

        mock_db_session.query().filter().order_by().first.return_value = mock_snapshot

        result = await get_coverage_map(db=mock_db_session)

        assert "cache_info" in result
        assert result["cache_info"]["cached"] is True

    @pytest.mark.asyncio
    async def test_get_coverage_map_cold_start(self, mock_db_session):
        """Test endpoint generates data on first request"""
        from src.api.routes.transparency import get_coverage_map

        # No snapshot exists
        mock_db_session.query().filter().order_by().first.return_value = None

        with patch('src.api.routes.transparency.HealthCheckService') as mock_health:
            mock_health.return_value.generate_report.return_value = {
                "apis": {"healthy": [], "degraded": [], "unhealthy": []}
            }

            result = await get_coverage_map(db=mock_db_session)

            assert "cache_info" in result
            assert result["cache_info"]["cached"] is False
```

### 8.2 Testes de Integração

```python
# tests/integration/test_coverage_map_integration.py

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from src.infrastructure.database import SessionLocal
from src.models.transparency_coverage import TransparencyCoverageSnapshot
from src.infrastructure.queue.tasks.coverage_tasks import update_transparency_coverage


class TestCoverageMapIntegration:
    """Integration tests for coverage map system"""

    @pytest.fixture
    def db_session(self):
        """Real database session for integration tests"""
        session = SessionLocal()
        yield session
        session.close()

    def test_celery_task_creates_snapshot(self, db_session):
        """Test Celery task creates database snapshot"""
        # Run the task
        result = update_transparency_coverage()

        assert result["status"] == "success"

        # Verify snapshot was created
        snapshot = db_session.query(TransparencyCoverageSnapshot).order_by(
            TransparencyCoverageSnapshot.snapshot_date.desc()
        ).first()

        assert snapshot is not None
        assert snapshot.coverage_data is not None
        assert "states" in snapshot.coverage_data
        assert "summary" in snapshot.coverage_data

    def test_endpoint_returns_valid_data(self, client):
        """Test API endpoint returns valid coverage data"""
        response = client.get("/api/v1/transparency/coverage/map")

        assert response.status_code == 200
        data = response.json()

        assert "states" in data
        assert "summary" in data
        assert "cache_info" in data

        # Verify data structure
        summary = data["summary"]
        assert "total_states" in summary
        assert "overall_coverage_percentage" in summary
        assert summary["total_states"] == 27
```

---

## 9. Deployment

### 9.1 Railway Configuration

```bash
# Definir variáveis no Railway
railway variables set ENABLE_COVERAGE_MAP=true

# Verificar Celery Beat está rodando
railway logs -f | grep "celerybeat"

# Verificar task schedule
railway run celery -A src.infrastructure.queue.celery_app inspect scheduled
```

### 9.2 Monitoramento

```bash
# Ver logs da task
railway logs -f | grep "update_transparency_coverage"

# Verificar snapshots no banco
railway run psql $DATABASE_URL -c "SELECT snapshot_date, summary_stats FROM transparency_coverage_snapshots ORDER BY snapshot_date DESC LIMIT 5;"

# Testar endpoint
curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map | jq '.summary'
```

---

## 10. Considerações Finais

### 10.1 Performance

- **Cache Hit**: <100ms response time
- **Cache Miss**: 30-60s (primeira vez apenas)
- **Update Job**: 30-60s a cada 6 horas (low impact)
- **Database Size**: ~50KB por snapshot, ~200MB/ano

### 10.2 Escalabilidade

- Suporta 27 estados + centenas de APIs
- Pode adicionar municípios no futuro
- Histórico ilimitado (com cleanup opcional)

### 10.3 Manutenção

- **Atualização automática**: Celery Beat (zero manutenção)
- **Cleanup opcional**: Script para remover snapshots > 90 dias
- **Monitoramento**: Logs + métricas Prometheus

### 10.4 Próximos Passos

1. ✅ Criar migration do banco de dados
2. ✅ Implementar task Celery
3. ✅ Criar endpoint FastAPI
4. ⏳ Implementar frontend React
5. ⏳ Deploy Railway + testes
6. ⏳ Documentação para usuários
7. ⏳ Campanha de divulgação (redes sociais)

---

## 11. Referências

- **Decreto MG 48.383/2022**: Base legal para dados abertos em Minas Gerais
- **Lei Federal 12.527/2011**: Lei de Acesso à Informação
- **Lei Federal 14.129/2021**: Lei do Governo Digital
- **Portal da Transparência**: https://portaldatransparencia.gov.br/
- **CKAN Documentation**: https://docs.ckan.org/

---

**Documento criado em**: 2025-10-23
**Última atualização**: 2025-10-23
**Versão**: 1.0
**Autor**: Anderson Henrique da Silva
**Status**: Em Planejamento
