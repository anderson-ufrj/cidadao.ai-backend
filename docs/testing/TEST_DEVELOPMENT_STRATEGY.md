# Test Development Strategy Guide

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-22
**Purpose**: Prevent common test development pitfalls and ensure effective coverage expansion

---

## 🎯 Core Principle: API-First Testing

**NEVER write tests before verifying the actual API exists.**

### The Problem

In multiple sessions, tests were created calling non-existent methods:
- `_run_clustering()` ❌ (doesn't exist in Anita)
- `_analyze_user_behavior()` ❌ (doesn't exist in Maria Quitéria)
- `_select_agent_with_load_balancing()` ❌ (doesn't exist in Ayrton Senna)

### The Solution

**3-Step Test Development Process:**

```bash
# STEP 1: List actual methods
grep -n "^\s*async def \|^\s*def " src/agents/<agent_name>.py

# STEP 2: Read method signatures
# Verify parameters, return types, actual behavior

# STEP 3: Write tests for ACTUAL methods
# Not hypothetical ones!
```

---

## 📊 Coverage Expansion Workflow

### Phase 1: Measure Current State
```bash
# Get baseline coverage for specific agent
JWT_SECRET_KEY=test SECRET_KEY=test \
  venv/bin/pytest tests/unit/agents/test_<agent>.py \
  --cov=src.agents.<agent> \
  --cov-report=term-missing \
  --no-cov-on-fail -q
```

### Phase 2: Identify Gaps
```bash
# Example output:
# src/agents/drummond.py  420  48  112  13  87.78%
# Missing: 300-302, 389-393, 696, 704, 754, ...
```

**Analyze Missing Lines:**
1. Are they error handlers? (often hard to trigger)
2. Are they edge cases? (need specific test scenarios)
3. Are they fallback logic? (need mocked failures)
4. Are they private methods? (test via public API)

### Phase 3: Read the Code
```python
# Read actual implementation
# Don't assume - verify!
```

**Example:**
```bash
# Check lines 300-302
sed -n '298,305p' src/agents/drummond.py
```

### Phase 4: Write Targeted Tests

**Focus on:**
- ✅ Public API methods
- ✅ Error handling paths
- ✅ Edge cases
- ✅ Fallback logic

**Avoid:**
- ❌ Testing private methods directly
- ❌ Testing implementation details
- ❌ Calling non-existent methods
- ❌ Over-mocking (reduces test value)

### Phase 5: Verify Improvement
```bash
# Run tests and check new coverage
JWT_SECRET_KEY=test SECRET_KEY=test \
  venv/bin/pytest tests/unit/agents/test_<agent>*.py \
  --cov=src.agents.<agent> \
  --cov-report=term-missing
```

---

## 🎓 Lessons Learned (October 2025)

### Lesson 1: Coverage Scope Matters

**Issue**: Maria Quitéria reported at 78.27% in one measurement, 23.23% in another

**Root Cause**: Different measurement scopes
- Whole module vs specific class
- With/without related imports
- Different test file combinations

**Solution**: Always specify exact module
```bash
--cov=src.agents.maria_quiteria  # Specific module
```

### Lesson 2: Private Methods Are Not Test Targets

**Issue**: Created tests calling `_analyze_user_behavior()`, `_run_clustering()`, etc.

**Root Cause**: Misunderstanding test-driven development
- Private methods are implementation details
- They change frequently
- Testing them creates brittle tests

**Solution**: Test public API, let private methods be covered implicitly
```python
# ✅ Good - test public API
async def test_process_security_audit():
    response = await agent.process(message, context)
    assert response.status == AgentStatus.COMPLETED

# ❌ Bad - test private method
async def test_analyze_user_behavior():
    result = await agent._analyze_user_behavior(data, context)
```

### Lesson 3: Agent Method Names Are Not Uniform

**Issue**: Assumed `SecurityAgent` class name, assumed method names

**Root Cause**: Didn't verify actual class/method names

**Solution**: Always grep first
```bash
# Find class name
grep "^class.*Agent" src/agents/<agent>.py

# Find method names
grep "^\s*async def " src/agents/<agent>.py
```

### Lesson 4: Mock Complete Interfaces

**Issue**: Nanã tests failed due to incomplete Redis mock

**Root Cause**: Mocked only `get/set`, forgot `setex`, `keys`, `delete`, `exists`

**Solution**: Mock ALL methods used by code
```python
@pytest.fixture
def mock_redis_client():
    client = AsyncMock()
    client.get.return_value = None
    client.set.return_value = True
    client.setex.return_value = True  # DON'T FORGET!
    client.keys.return_value = []
    client.delete.return_value = 1
    client.exists.return_value = False
    return client
```

### Lesson 5: Error Paths Need Special Setup

**Issue**: Coverage missing on exception handlers (lines 300-302, 389-393)

**Root Cause**: Tests only cover happy path

**Solution**: Create tests that trigger errors
```python
@pytest.mark.asyncio
async def test_initialization_failure():
    """Test agent handles initialization errors gracefully."""
    with patch.object(agent, '_setup_resources', side_effect=Exception("Setup failed")):
        # Should handle gracefully, not crash
        await agent.initialize()
```

### Lesson 6: Type System Strictness

**Issue**: Pydantic models rejected strings when expecting dicts

**Root Cause**: Type validation is strict

**Solution**: Normalize inputs
```python
# Normalize content
if isinstance(content, str):
    content = {"description": content}
```

### Lesson 7: LLM Client Differences

**Issue**: Mocked `generate()` but client uses `chat_completion()`

**Root Cause**: Different LLM providers have different APIs

**Solution**: Check actual client methods
```bash
grep "^\s*async def " src/services/maritaca_client.py
```

---

## 📋 Coverage Expansion Checklist

Before writing ANY test, complete this checklist:

### ✅ Pre-Development
- [ ] Run coverage to get baseline percentage
- [ ] Identify specific missing lines
- [ ] Read code at those lines
- [ ] List actual method names with `grep`
- [ ] Verify class names
- [ ] Check method signatures (parameters, return types)

### ✅ During Development
- [ ] Test public API, not private methods
- [ ] Mock complete interfaces (all methods)
- [ ] Create error-triggering scenarios
- [ ] Test edge cases
- [ ] Use actual method names (no assumptions!)

### ✅ Post-Development
- [ ] Run tests - verify they pass
- [ ] Measure new coverage
- [ ] Check if target reached (usually 80% or 90%)
- [ ] If not reached, analyze remaining gaps
- [ ] Commit working tests

---

## 🎯 Coverage Targets by Agent Tier

### Tier 1: Operational Agents (10 agents)
**Target**: 90%+ coverage
**Priority**: HIGH

- Zumbi (88.26%) → needs 1.74%
- Anita (69.94%) → needs 20.06%
- Tiradentes (91.03%) → ✅ DONE
- Machado (93.55%) → ✅ DONE
- Senna (89.77%) → needs 0.23%
- Bonifácio (49.13%) → needs 40.87%
- Maria Quitéria (78.27%*) → needs verification
- Oxóssi (83.80%) → needs 6.20%
- Lampião (91.26%) → ✅ DONE
- Oscar Niemeyer (93.78%) → ✅ DONE

**Note**: * Coverage percentages vary by measurement scope

### Tier 2: Framework Agents (5 agents)
**Target**: 50%+ coverage
**Priority**: MEDIUM

- Abaporu (13.37%) → needs 36.63%
- Nanã (55.26%) → ✅ MET (was 11.76%, now 55.26%)
- Drummond (87.78%) → almost Tier 1!
- Céuci (10.49%) → needs 39.51%
- Obaluaiê (13.11%) → needs 36.89%

### Tier 3: Minimal Agents (1 agent)
**Target**: 30%+ coverage
**Priority**: LOW

- Dandara (86.32%) → ✅ EXCEEDS (actually very good!)

---

## 🔍 Quick Reference Commands

### Find Agent Class Name
```bash
grep "^class.*Agent" src/agents/<agent>.py
```

### List All Methods
```bash
grep -n "^\s*async def \|^\s*def " src/agents/<agent>.py
```

### Check Coverage for Agent
```bash
JWT_SECRET_KEY=test SECRET_KEY=test \
  venv/bin/pytest tests/unit/agents/test_<agent>*.py \
  --cov=src.agents.<agent> \
  --cov-report=term-missing -q
```

### View Specific Lines
```bash
sed -n '<start>,<end>p' src/agents/<agent>.py
```

### Count Test Cases
```bash
grep -c "^\s*async def test_\|^\s*def test_" tests/unit/agents/test_<agent>.py
```

---

## 💡 Best Practices

### DO ✅
1. **Verify before writing**: Check method exists
2. **Test public API**: Focus on user-facing methods
3. **Mock completely**: Include all interface methods
4. **Test error paths**: Force failures, test recovery
5. **Measure incrementally**: Check coverage after each test batch
6. **Document learnings**: Note what works/doesn't work
7. **Commit frequently**: Small, working increments

### DON'T ❌
1. **Assume method names**: Always grep first
2. **Test private methods**: They're implementation details
3. **Partial mocking**: Mock complete interfaces
4. **Ignore errors**: Coverage gaps often in error handlers
5. **Batch blindly**: Verify each test adds coverage
6. **Commit broken tests**: Only commit passing tests
7. **Skip documentation**: Future you will thank current you

---

## 📊 Expected Coverage Timeline

### Realistic Estimates (per agent)

**High Coverage Agents (80%+)**:
- Time: 30-60 minutes
- Effort: Add 3-5 targeted tests
- Example: Senna 89.77% → 90%

**Medium Coverage Agents (50-79%)**:
- Time: 2-3 hours
- Effort: Add 10-15 comprehensive tests
- Example: Nanã 55.26% → 80%

**Low Coverage Agents (<50%)**:
- Time: 4-6 hours
- Effort: Add 20-30 tests + API audit
- Example: Bonifácio 49.13% → 80%

**Very Low Coverage Agents (<20%)**:
- Time: Full day (8 hours)
- Effort: Complete test suite creation
- Example: Céuci 10.49% → 80%

---

## 🚀 Recommended Approach

### Sprint Planning

**Week 1: Quick Wins**
- Senna: 89.77% → 90% (30 min)
- Zumbi: 88.26% → 90% (1 hour)
- Oxóssi: 83.80% → 90% (2 hours)

**Week 2: Medium Effort**
- Nanã: 55.26% → 80% (3 hours) - DONE ✅
- Drummond: 87.78% → 90% (1 hour)
- Maria Quitéria: API audit + tests (4 hours)

**Week 3-4: High Effort**
- Anita: 69.94% → 80% (4 hours)
- Bonifácio: 49.13% → 80% (6 hours)

**Future Sprints**:
- Abaporu, Céuci, Obaluaiê (Tier 2)
- Focus on implementation completion first
- Then add tests

---

## 📝 Test Template

Use this template for new test files:

```python
"""
Coverage expansion tests for <Agent Name>
Target: Increase coverage from <current>% to <target>%
Focus: <main uncovered functionality>
"""

from unittest.mock import AsyncMock, patch
import pytest

from src.agents.<agent_module> import <AgentClass>
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus


@pytest.fixture
def agent_context():
    """Create agent context for testing."""
    return AgentContext(
        investigation_id="test_<agent>",
        user_id="test_user",
        session_id="test_session",
    )


@pytest.fixture
def <agent>_agent():
    """Create <Agent Name> instance."""
    return <AgentClass>()


class Test<FunctionalityName>:
    """Test <specific functionality> edge cases."""

    @pytest.mark.asyncio
    async def test_<specific_scenario>(
        self, <agent>_agent, agent_context
    ):
        """Test <what this test does>."""
        # Arrange
        message = AgentMessage(
            sender="test",
            recipient="<AgentClass>",
            action="<actual_action_name>",  # VERIFY THIS EXISTS!
            payload={"key": "value"},
        )

        # Act
        response = await <agent>_agent.process(message, agent_context)

        # Assert
        assert response.status == AgentStatus.COMPLETED
        assert "expected_key" in response.result
```

---

## 🎓 Summary

**Key Takeaways:**
1. Always verify API before writing tests
2. Focus on public methods, not private ones
3. Mock complete interfaces
4. Test error paths explicitly
5. Measure coverage incrementally
6. Document learnings for future reference

**Current Status** (2025-10-22):
- ✅ 644/644 tests passing (100% success rate)
- ✅ All test failures eliminated
- ⚠️ Coverage expansion requires API verification
- 📋 Strategy guide created for future sessions

---

**Generated**: 2025-10-22
**Last Updated**: 2025-10-22
**Status**: Living Document - Update as patterns emerge
