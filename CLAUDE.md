# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-25 18:00:00 -03:00 (São Paulo, Brazil)

## Project Overview

Cidadão.AI Backend is a multi-agent AI system for Brazilian government transparency analysis. Currently deployed on HuggingFace Spaces with 8 of 17 planned agents fully operational.

### Current Implementation State

✅ **Working Features**:
- 8 fully operational agents (Abaporu, Zumbi, Anita, Tiradentes, Senna, Nanã, Bonifácio, Machado)
- Portal da Transparência integration (22% of endpoints working, 78% return 403)
- Chat API with Portuguese intent detection
- SSE streaming for real-time responses
- FFT spectral analysis for anomaly detection
- In-memory caching (Redis optional)
- Prometheus/Grafana monitoring configured

🚧 **Partial/Planned**:
- 9 agents with structure but incomplete implementation
- ML models defined but not trained
- PostgreSQL integration (using in-memory currently)
- WebSocket for real-time investigations
- Advanced caching strategies

## Critical Development Commands

### Setup & Installation
```bash
# Install all dependencies including dev tools
make install-dev

# For HuggingFace deployment (minimal deps)
pip install -r requirements-minimal.txt
```

### Development Workflow
```bash
# Run locally with full features
make run-dev
# OR
python -m src.api.app

# Run HuggingFace version (simplified)
python app.py

# Run tests - ALWAYS before committing
make test              # All tests (80% coverage required)
make test-unit         # Unit tests only  
make test-agents       # Multi-agent system tests

# Code quality - MUST pass
make format            # Black + isort
make lint              # Ruff linter
make type-check        # MyPy
make check             # All checks

# Full CI locally
make ci
```

### Testing Specific Components
```bash
# Test a specific agent
python -m pytest tests/unit/agents/test_zumbi.py -v

# Test with coverage
python -m pytest tests/unit/agents/test_zumbi.py --cov=src.agents.zumbi

# Test API endpoints
python -m pytest tests/integration/test_chat_simple.py -v
```

### Monitoring & Debugging
```bash
# Start monitoring stack
make monitoring-up
# Grafana: http://localhost:3000 (admin/cidadao123)

# Interactive shell
make shell

# Check agent status
curl http://localhost:8000/api/v1/agents/status
```

## Architecture Overview

### Multi-Agent Communication Flow
```
User → Chat API → Intent Detection → Agent Router (Senna)
                                           ↓
                                    Agent Selection
                                           ↓
                          Direct Agent or Master (Abaporu)
                                           ↓
                                  Result + Response
```

### Key Implementation Details

1. **Agent States**: IDLE, THINKING, ACTING, WAITING, ERROR, COMPLETED
2. **Quality Threshold**: 0.8 for reflective agents (max 3 iterations)
3. **Anomaly Thresholds**: 
   - Price: 2.5 standard deviations
   - Supplier concentration: 70%
   - Duplicate contracts: 85% similarity
4. **API Rate Limits**: Configurable tiers per endpoint
5. **Cache TTL**: Short (5min), Medium (1hr), Long (24hr)

## Portal da Transparência Integration

### Working Endpoints (22%)
- `/api/v1/transparency/contracts` - Requires codigoOrgao parameter
- `/api/v1/transparency/servants` - Search by CPF only
- `/api/v1/transparency/agencies` - Organization info

### Blocked Endpoints (78% return 403)
- Expenses, suppliers, parliamentary amendments, benefits
- No official documentation about access tiers
- Salary/remuneration data not available

### Environment Variables
```bash
TRANSPARENCY_API_KEY=your-key  # For real data (optional)
GROQ_API_KEY=your-key         # LLM provider (required)
JWT_SECRET_KEY=your-secret    # Auth (required)
DATABASE_URL=postgresql://... # DB (optional, uses memory)
REDIS_URL=redis://...        # Cache (optional)
```

## Common Issues & Solutions

1. **Import errors**: Run `make install-dev`
2. **Test failures**: Check environment variables
3. **Agent timeouts**: Verify GROQ_API_KEY is set
4. **403 on Portal API**: Expected - most endpoints blocked
5. **Redis errors**: Optional - system works without it

## Development Tips

### Adding New Features
1. Write tests first (TDD approach)
2. Update API docs (docstrings)
3. Run `make check` before committing
4. Keep agents focused on single responsibility

### Performance Optimization
- Use async/await throughout
- Leverage caching for expensive operations
- Profile with `make profile` (if available)
- Monitor agent pool usage

### Debugging Agents
```python
# Enable debug logging
import logging
logging.getLogger("src.agents").setLevel(logging.DEBUG)

# Check agent state
agent = AgentPool.get_agent("zumbi")
print(agent.get_state())
```

## Deployment Notes

### HuggingFace Spaces
- Uses `app.py` (simplified version)
- No PostgreSQL/Redis required
- Automatic deployment on push
- Environment variables in Spaces settings

### Local Development
- Full `src.api.app` with all features
- Optional PostgreSQL/Redis
- Complete agent system
- Development tools available

## Current Limitations

1. **Database**: In-memory only (PostgreSQL integration incomplete)
2. **ML Models**: Basic threshold-based detection (no trained models)
3. **Portal API**: 78% of endpoints return 403 Forbidden
4. **WebSocket**: Partial implementation for investigations
5. **Some Agents**: 9 of 17 agents have incomplete implementation

## Testing Requirements

- **Coverage Target**: 80% (enforced)
- **Test Markers**: @pytest.mark.unit, @pytest.mark.integration
- **Async Tests**: Use pytest-asyncio
- **Mocking**: Mock external APIs in tests

## Git Commit Guidelines

- **IMPORTANT**: Do NOT include in commits:
  - `🤖 Generated with [Claude Code](https://claude.ai/code)`
  - `Co-Authored-By: Claude <noreply@anthropic.com>` 

Remember: This is a production system deployed on HuggingFace Spaces. Always test thoroughly and maintain backwards compatibility.