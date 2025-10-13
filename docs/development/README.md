# 💻 Development Guide - Cidadão.AI Backend

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Author**: Anderson Henrique da Silva
**Last Updated**: 2025-10-03 (São Paulo, Brazil)

This directory contains comprehensive developer guides and implementation references for contributing to the Cidadão.AI Backend project.

## 📚 Available Guides

### Getting Started

- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Complete contribution guide
  - Code standards and conventions
  - Git workflow and commit guidelines
  - Pull request process
  - Development environment setup

### Implementation Guides

- **[CONVERSATIONAL_AI_IMPLEMENTATION.md](./CONVERSATIONAL_AI_IMPLEMENTATION.md)** - Conversational AI system
  - Portuguese intent detection
  - Multi-agent dialogue flow
  - Context management
  - Response generation

- **[INDEX_CHAT_IMPLEMENTATION.md](./INDEX_CHAT_IMPLEMENTATION.md)** - Chat implementation details
  - Real-time chat architecture
  - SSE streaming responses
  - Message handling patterns
  - Error recovery strategies

- **[maritaca_integration.md](./maritaca_integration.md)** - Maritaca LLM integration
  - API integration patterns
  - Optimization techniques
  - Rate limiting and caching
  - Cost optimization

### Technical Implementation

- **[CORS_CONFIGURATION.md](./CORS_CONFIGURATION.md)** - CORS setup and security
  - Production-ready CORS configuration
  - Security best practices
  - Vercel/HuggingFace deployment specifics

- **[CURSOR_PAGINATION_IMPLEMENTATION.md](./CURSOR_PAGINATION_IMPLEMENTATION.md)** - Cursor-based pagination
  - Efficient pagination for large datasets
  - Performance optimizations
  - API design patterns

- **[GZIP_COMPRESSION_IMPLEMENTATION.md](./GZIP_COMPRESSION_IMPLEMENTATION.md)** - Response compression
  - GZIP middleware configuration
  - Compression strategies
  - Performance impact analysis

- **[FRONTEND_INTEGRATION_GUIDE.md](./FRONTEND_INTEGRATION_GUIDE.md)** - Frontend integration
  - API client setup
  - Authentication flow
  - WebSocket integration
  - Error handling patterns

### Code Examples

- **[examples/](./examples/)** - Working code examples
  - Integration examples
  - Agent usage patterns
  - API client implementations

## 🚀 Quick Start for Developers

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# Install dependencies
make install-dev

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run Development Server

```bash
# Start backend with hot reload
make run-dev

# Or directly with Python
python -m src.api.app
```

### 3. Run Tests

```bash
# Run all tests with coverage (80% minimum required)
make test

# Run specific test categories
make test-unit        # Unit tests only
make test-agents      # Multi-agent tests
make test-integration # Integration tests
```

### 4. Code Quality Checks

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Run all checks
make check

# Full CI locally
make ci
```

## 📋 Development Workflow

### 1. Before Starting
- Read [CONTRIBUTING.md](./CONTRIBUTING.md)
- Set up pre-commit hooks (optional but recommended)
- Join our communication channels (if available)

### 2. During Development
- Follow code standards from CONTRIBUTING.md
- Write tests for new features (TDD approach)
- Update documentation as you code
- Run `make check` frequently

### 3. Before Committing
- Run `make ci` to ensure all checks pass
- Write descriptive commit messages (conventional commits)
- Update relevant documentation
- Add tests for new functionality

### 4. Pull Request
- Follow PR template guidelines
- Ensure CI passes
- Request review from maintainers
- Address review feedback promptly

## 🏗️ Architecture References

For architectural decisions and patterns:
- [Architecture Overview](../architecture/README.md)
- [Agent System Design](../architecture/AGENT_LAZY_LOADING.md)
- [Performance Optimization](../architecture/PERFORMANCE_OPTIMIZATION.md)
- [Monitoring & Observability](../architecture/MONITORING_OBSERVABILITY.md)

## 🤖 Agent Development

For creating or modifying agents:
- [Agent Documentation](../agents/README.md)
- [Abaporu (Master Orchestrator)](../agents/abaporu.md)
- [Zumbi (Anomaly Detection)](../agents/zumbi.md)
- [Agent Status Overview](../planning/AGENT_STATUS_2025.md)

## 🔧 Common Development Tasks

### Adding a New Agent
1. Create agent class in `src/agents/`
2. Register in `src/agents/__init__.py`
3. Add tests in `tests/unit/agents/`
4. Create documentation in `docs/agents/`
5. Update agent status document

### Adding a New API Endpoint
1. Create/update router in `src/api/routers/`
2. Add endpoint to `src/api/app.py`
3. Write integration tests
4. Update API documentation
5. Add to [API_ENDPOINTS_MAP.md](../api/API_ENDPOINTS_MAP.md)

### Performance Optimization
1. Profile the code to identify bottlenecks
2. Implement caching where appropriate
3. Use async/await for I/O operations
4. Add monitoring metrics
5. Document optimizations

## 📊 Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Agent Tests**: Test multi-agent coordination
- **Performance Tests**: Benchmark critical paths
- **Security Tests**: Validate authentication and authorization

Target: **80% code coverage** (enforced in CI)

## 🔒 Security Considerations

- Never commit secrets or API keys
- Use environment variables for configuration
- Follow OWASP security best practices
- Validate all user inputs
- Implement rate limiting on public endpoints
- Keep dependencies updated

## 🐛 Debugging Tips

```python
# Enable debug logging for agents
import logging
logging.getLogger("src.agents").setLevel(logging.DEBUG)

# Use pdb for interactive debugging
import pdb; pdb.set_trace()

# Profile performance
from src.core.monitoring import agent_metrics
# Metrics automatically collected
```

## 📖 Additional Resources

- [API Documentation](../api/README.md)
- [Deployment Guide](../deployment/README.md)
- [Troubleshooting](../troubleshooting/)
- [Project Roadmap](../planning/ROADMAP_MELHORIAS_2025.md)

## 🤝 Getting Help

If you encounter issues:
1. Check [Troubleshooting Guide](../troubleshooting/)
2. Search existing GitHub issues
3. Review relevant documentation
4. Create a new issue with detailed information

---

**Happy coding!** 🚀

Remember: Quality over speed. Write tests, document your code, and follow best practices.
