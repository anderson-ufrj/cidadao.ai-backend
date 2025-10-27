# 🚀 Coverage Improvement - Quick Reference Guide

**Last Updated**: October 27, 2025
**Current Overall Coverage**: ~72%
**Target**: 80%+ for all operational agents

---

## ⚡ **QUICK START**

### **Step 1: Choose Your Target Agent**

```bash
# Run coverage for specific agent
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_<agent_name>.py \
  --cov=src.agents.<agent_name> \
  --cov-report=term-missing
```

### **Step 2: Identify Missing Blocks**

Look for:
- Lines with ranges (e.g., `964-1071`) = **BIG BLOCKS** 🎯
- Single lines (e.g., `740`) = Small gaps
- Branch indicators (e.g., `326->333`) = Conditional branches

**Priority**: Target blocks with 20+ lines first!

### **Step 3: Write Strategic Tests**

```python
class TestCoverageBoost:
    """Tests to boost <agent> coverage."""

    @pytest.mark.asyncio
    async def test_<method_name>(self, agent, agent_context):
        """Test <method> - Lines X-Y."""
        # Call the method directly or via process()
        result = await agent.<method>(...)

        # Verify expected behavior
        assert result is not None
```

### **Step 4: Verify & Commit**

```bash
# Run tests and check coverage
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_<agent>*.py \
  --cov=src.agents.<agent> \
  --cov-report=term-missing

# Commit (no AI mentions!)
git add tests/unit/agents/test_<agent>.py
git commit -m "test(agents): boost <Agent> coverage to XX.XX%"
```

---

## 🎯 **AGENT PRIORITY LIST**

### **🔥 HIGH PRIORITY** (Best ROI)

#### **1. Bonifácio (65.22% → 80%)**
- **Gap**: 14.78 points
- **Time**: 3-4 hours
- **Big Block**: Lines 1280-1425 (151 lines!)
- **Issue**: Framework methods not called
- **Action**: Fix bug + add tests

#### **2. Nanã (55.26% → 80%)**
- **Gap**: 24.74 points
- **Time**: 4-6 hours
- **Focus**: Memory persistence
- **Action**: Add database integration tests

### **✅ POLISH** (Near 90%)

#### **3. Ayrton Senna (89.77% → 90%)**
- **Gap**: 0.23 points
- **Time**: 30 min
- **Action**: 1-2 quick tests

#### **4. Dandara (86.32% → 90%)**
- **Gap**: 3.68 points
- **Time**: 1-2 hours
- **Action**: 3-4 tests

#### **5. Oxóssi (83.80% → 85%)**
- **Gap**: 1.20 points
- **Time**: 1 hour
- **Action**: 2-3 tests

### **⚠️ SKIP FOR NOW** (Too Much Effort)

- Maria Quitéria (23.23%): 6-10 hours
- Abaporu (13.37%): 8-12 hours
- Obaluaiê (13.11%): 8-12 hours
- Céuci (10.49%): 10-15 hours

**Reason**: These need architectural work first.

---

## 🛠️ **COMMON PATTERNS**

### **Pattern 1: Testing process() Method**

Most agent `process()` methods have 0% coverage!

```python
@pytest.mark.asyncio
async def test_process_with_action(self, agent):
    """Test process() with specific action."""
    from src.agents.deodoro import AgentContext, AgentMessage

    message = AgentMessage(
        sender="test_user",
        recipient="agent_name",
        action="action_name",  # e.g., "analyze", "process_chat"
        payload={
            # Action-specific data
        },
    )

    context = AgentContext(
        investigation_id="test_inv",
        user_id="test_user",
        session_id="test_session",
    )

    response = await agent.process(message, context)

    assert response.status.value == "completed"
    assert "result_key" in response.result
```

**ROI**: High! Often covers 50-100 lines.

### **Pattern 2: Mocking External Services**

Always mock: APIs, LLMs, file I/O, databases

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_external_service(self, agent):
    """Test method that uses external service."""

    mock_result = {"data": "test"}

    with patch(
        "src.agents.agent_name.external_service.method",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        result = await agent.method_under_test()
        assert result == mock_result
```

### **Pattern 3: Testing Conditional Branches**

One test per condition:

```python
# Test 1: Condition A
def test_method_condition_a(self, agent):
    """Test when value >= threshold."""
    result = agent.method(value=100)  # Triggers condition A
    assert "expected_for_a" in result

# Test 2: Condition B
def test_method_condition_b(self, agent):
    """Test when value < threshold."""
    result = agent.method(value=50)   # Triggers condition B
    assert "expected_for_b" in result
```

### **Pattern 4: Direct Method Testing**

When `process()` doesn't call the method:

```python
@pytest.mark.asyncio
async def test_private_method_directly(self, agent, agent_context):
    """Test private method directly - Lines X-Y."""

    # Create required data structures
    data = [...]
    request = RequestClass(...)

    # Call private method directly
    result = await agent._private_method(data, request, agent_context)

    assert isinstance(result, list)
    assert len(result) > 0
```

---

## 🐛 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: Data Structure Errors**

**Error**: `TypeError: __init__() got an unexpected keyword argument 'X'`

**Solution**: Read the class definition first!

```bash
# Find class definition
grep -n "class ClassName" src/**/*.py

# Read it
cat src/path/to/file.py | grep -A 20 "class ClassName"
```

### **Issue 2: Wrong Agent Name**

**Error**: `AssertionError: assert 'agent' == 'Agent'`

**Solution**: Check actual values (often lowercase)

```python
# Correct ✅
assert response.agent_name == "drummond"

# Wrong ❌
assert response.agent_name == "Drummond"
```

### **Issue 3: Method Not Covered**

**Error**: Tests pass but coverage doesn't increase

**Solution**: Method might not be called via `process()`

```python
# Option 1: Call directly
result = await agent._method_name(...)

# Option 2: Use correct action
message = AgentMessage(action="correct_action_name", ...)
```

### **Issue 4: External Service Not Mocked**

**Error**: Tests fail with network/API errors

**Solution**: Mock all external calls

```python
# Mock BEFORE calling method
with patch("path.to.external.service", return_value=mock_data):
    result = await agent.method()
```

---

## 📊 **ROI CALCULATOR**

### **Expected ROI by Coverage Range**

| Current Coverage | Target | Estimated Tests | Estimated Time | ROI (points/hour) |
|------------------|--------|-----------------|----------------|-------------------|
| 90-95% | 95%+ | 5-10 | 1-2 hours | 2-3 (Low) |
| 85-90% | 90%+ | 5-8 | 1-2 hours | 3-5 (Medium) |
| 80-85% | 85%+ | 3-5 | 1 hour | 5-8 (Good) |
| 75-80% | 80%+ | 2-4 | 1 hour | 5-10 (Good) |
| 65-75% | 80%+ | 8-12 | 2-4 hours | 4-7 (Medium) |
| <65% | 80%+ | 20-40 | 4-8 hours | 3-5 (Low) |

**Sweet Spot**: Agents at 75-85% give best ROI!

---

## ✅ **TESTING CHECKLIST**

### **Before Starting**

- [ ] Run actual coverage report (don't trust docs!)
- [ ] Identify 3 largest missing blocks
- [ ] Calculate estimated ROI
- [ ] Read method signatures for data structures

### **During Testing**

- [ ] Mock all external dependencies
- [ ] Test one condition per test
- [ ] Run tests incrementally (after each test)
- [ ] Verify coverage increases as expected

### **Before Committing**

- [ ] All tests pass
- [ ] Coverage increased by expected amount
- [ ] No AI mentions in commit message
- [ ] Professional English commit message
- [ ] Black formatting applied

### **Commit Message Template**

```
test(agents): boost <Agent> coverage to XX.XX%

Add N focused tests to improve <Agent> (<Description>) coverage:
- test_method_1: Cover <description> (lines X-Y)
- test_method_2: Cover <description> (lines A-B)

Coverage improvement: XX.XX% → YY.YY% (+Z.ZZ points)
Tests added: N new tests in Test<Class>Boost class
Statements reduced: X → Y missing (-Z statements)
```

---

## 🎓 **LEARNING FROM PAST SESSIONS**

### **Session 10-11 Key Insights** (Oct 27, 2025)

1. **Always verify actual coverage** (Maria Quitéria: docs 78.48%, reality 23.23%!)
2. **Target massive blocks** (Drummond: 108-line method = +8.84 points with 1 test)
3. **Mock external services** (Tiradentes: AsyncMock for export_service)
4. **Know when to stop** (Tiradentes: 92.18% is excellent, don't chase 100%)

### **Session 7-8 Key Insights** (Oct 26, 2025)

1. **Direct method calls** when `process()` doesn't trigger (Anita spectral patterns)
2. **Mocking for thresholds** (Anita: Mock SpectralAnalyzer for amplitude > 0.1)
3. **Edge case testing** (Lampião: Division by zero, insufficient data)

---

## 🔗 **USEFUL COMMANDS**

```bash
# Quick coverage check
JWT_SECRET_KEY=test SECRET_KEY=test make test-unit

# Specific agent coverage
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_<agent>.py \
  --cov=src.agents.<agent> \
  --cov-report=term-missing

# Run single test
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_<agent>.py::<TestClass>::<test_method> -v

# Coverage with HTML report
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  --cov=src --cov-report=html
# Open: htmlcov/index.html

# Format code
make format

# All checks
make check
```

---

## 📚 **REFERENCE DOCUMENTS**

- **Session History**: `docs/project/SESSIONS_*_COVERAGE_SPRINT_*.md`
- **Overall Analysis**: `docs/project/COVERAGE_ANALYSIS_COMPLETE_*.md`
- **Agent Docs**: `docs/agents/<agent_name>.md`

---

**Pro Tip**: Start with Bonifácio (65.22%) next session - 151-line block waiting to be covered! 🎯
