# Contributing to Cidadão.AI

Thank you for your interest in contributing to Cidadão.AI! This guide will help you understand how to contribute effectively to our multi-agent transparency analysis system.

## 🤖 Agent Implementation Guide

### Current Status
- **8/17 agents fully implemented** (47%)
- **7 agents partially implemented** (need completion)
- **1 agent missing** (needs creation)

### How to Implement a New Agent

#### 1. **Choose an Agent to Implement**

Priority order for pending agents:
1. **José Bonifácio** (`bonifacio.py`) - Structure ready, implement logic
2. **Carlos Drummond** (`drummond.py`) - Design complete, implement channels
3. **Maria Quitéria** (`maria_quiteria.py`) - Security auditor
4. **Oscar Niemeyer** (`niemeyer.py`) - Data visualization
5. Others: Ceuci, Obaluaiê, Lampião

#### 2. **Follow the Standard Pattern**

All agents must inherit from `ReflectiveAgent`:

```python
from typing import List, Dict, Any
from src.agents.deodoro import ReflectiveAgent, AgentMessage, AgentResponse

class YourAgent(ReflectiveAgent):
    """
    Brief description of the agent's purpose.
    
    This agent specializes in [specific domain].
    """
    
    def __init__(self):
        super().__init__(
            agent_id="your_agent_id",
            name="Full Agent Name", 
            description="Detailed description of capabilities",
            capabilities=[
                "capability_1",
                "capability_2",
                # List all specific capabilities
            ]
        )
        
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Main processing logic for the agent.
        
        Args:
            message: The agent message to process
            
        Returns:
            AgentResponse with results
        """
        context = message.context
        content = message.content
        
        # Your implementation logic here
        results = await self._analyze_data(content)
        
        # Use reflection if quality is low
        if results.get("confidence", 0) < 0.8:
            return await self.reflect_and_retry(message, results)
            
        return AgentResponse(
            agent_id=self.agent_id,
            message_id=message.message_id,
            content=results,
            metadata={
                "processing_time": time.time() - start_time,
                "confidence": results.get("confidence")
            }
        )
```

#### 3. **Required Methods**

Each agent must implement:
- `__init__()`: Initialize with unique ID and capabilities
- `process()`: Main async processing method
- Helper methods for specific analyses

#### 4. **Agent Capabilities Examples**

Reference our fully implemented agents:

**Anomaly Detection (Zumbi)**:
- Statistical analysis (Z-score)
- Spectral analysis (FFT)
- Pattern recognition
- Duplicate detection

**Analysis (Anita)**:
- Trend analysis
- Behavioral patterns
- Efficiency metrics
- Seasonal patterns

**Reporting (Tiradentes)**:
- Multi-format generation
- Audience adaptation
- Risk prioritization
- Multilingual support

#### 5. **Testing Requirements**

Create comprehensive tests in `tests/unit/test_agents/`:

```python
import pytest
from src.agents.your_agent import YourAgent

class TestYourAgent:
    @pytest.fixture
    def agent(self):
        return YourAgent()
        
    @pytest.fixture
    def sample_message(self):
        return AgentMessage(
            content={"data": "test"},
            sender="test",
            context=AgentContext(investigation_id="test-123")
        )
        
    async def test_process_valid_data(self, agent, sample_message):
        response = await agent.process(sample_message)
        assert response.status == "success"
        assert "results" in response.content
        
    async def test_handles_invalid_data(self, agent):
        # Test error handling
        pass
```

#### 6. **Documentation Requirements**

- Add docstrings to all methods
- Update `docs/AGENT_STATUS_2025.md` with implementation status
- Include usage examples in docstrings
- Document any external dependencies

### Code Style Guidelines

1. **Python Style**:
   - Follow PEP 8
   - Use type hints
   - Black formatter (88 char line length)
   - isort for imports

2. **Async Best Practices**:
   - Use `async`/`await` for all I/O operations
   - Proper exception handling with `try`/`except`
   - Timeout handling for external calls

3. **Security**:
   - Validate all inputs
   - No hardcoded secrets
   - Use `settings` from `src.core.config`

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(agents): implement José Bonifácio policy analysis agent

- Add policy evaluation metrics
- Implement SROI calculations
- Add comprehensive test coverage
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `test`: Tests only
- `docs`: Documentation only
- `refactor`: Code restructuring
- `style`: Formatting changes
- `chore`: Maintenance

### Testing

Run tests before submitting:

```bash
# All tests
make test

# Specific agent tests
pytest tests/unit/test_agents/test_your_agent.py -v

# With coverage
make test-coverage
```

Minimum requirements:
- 80% test coverage for new code
- All tests passing
- No linting errors

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/implement-agent-name`
3. Make your changes following the guidelines
4. Run all checks: `make check`
5. Commit with clear messages
6. Push to your fork
7. Create a Pull Request with:
   - Clear description of changes
   - Reference to any related issues
   - Test results screenshot
   - Documentation updates

### Getting Help

- Check existing agent implementations for examples
- Review `src/agents/deodoro.py` for base classes
- Ask questions in GitHub Issues
- Tag maintainers for complex questions

## 🚀 Other Contributions

### Bug Fixes
1. Create an issue describing the bug
2. Reference the issue in your PR
3. Include tests that verify the fix

### Documentation
- Fix typos and clarify explanations
- Add examples and use cases
- Translate documentation

### Performance Improvements
- Profile before optimizing
- Benchmark improvements
- Document performance gains

## 📋 Development Setup

```bash
# Clone the repo
git clone https://github.com/your-fork/cidadao.ai-backend
cd cidadao.ai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dev dependencies
make install-dev

# Run tests
make test
```

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Celebrate Brazilian culture and diversity

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** Open an issue with the `question` label.

**Ready to contribute?** Check our [good first issue](https://github.com/anderson-ufrj/cidadao.ai-backend/labels/good%20first%20issue) labels!