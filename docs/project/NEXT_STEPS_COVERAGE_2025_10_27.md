# 🎯 Next Steps - Coverage Improvement

**Last Updated**: October 27, 2025, 22:00 -03
**Current Status**: 11/16 agents at 80%+ coverage (68.75%)
**Recent Progress**: +10 points in 2 hours (Sessions 10-11)

---

## 🚀 **IMMEDIATE ACTION ITEMS**

### **Priority 1: Bonifácio** 🔥
**Current**: 65.22% | **Target**: 80%+ | **Gap**: -14.78 points

**Why This Agent?**
- 151-line block in single method (`_apply_theory_of_change_framework`)
- Architectural bug discovered: Framework methods registered but not called
- High ROI potential once bug is fixed

**Action Plan**:
1. **Investigate bug** (30 min):
   ```python
   # Lines 143: _evaluation_frameworks dict defined
   # Lines 1280-1425: Methods exist but never executed
   # Find: Where should these methods be called?
   ```

2. **Fix execution flow** (30 min):
   - Add framework method calls in appropriate location
   - Test manually that methods execute

3. **Add coverage tests** (2-3 hours):
   - Test theory_of_change framework
   - Test logic_model framework
   - Test results_chain framework
   - Test cost_effectiveness framework

**Expected Result**: 65.22% → 82%+ (16+ points)

**Estimated Time**: 3-4 hours total

**Files**:
- Source: `src/agents/bonifacio.py`
- Tests: `tests/unit/agents/test_bonifacio.py`

---

### **Priority 2: Quick Wins** ✅

These agents are SO CLOSE to next threshold:

#### **A. Ayrton Senna (89.77% → 90%)**
- **Gap**: 0.23 points
- **Time**: 30 minutes
- **Action**: 1-2 simple tests
- **ROI**: 0.46 points/hour (quick win!)

#### **B. Dandara (86.32% → 90%)**
- **Gap**: 3.68 points
- **Time**: 1-2 hours
- **Action**: 3-4 tests for social justice metrics
- **ROI**: 2-4 points/hour

#### **C. Oxóssi (83.80% → 85%)**
- **Gap**: 1.20 points
- **Time**: 1 hour
- **Action**: 2-3 fraud detection edge cases
- **ROI**: 1.2 points/hour

**Total Quick Wins**: ~5 points in 3 hours

---

### **Priority 3: Nanã (Memory System)**
**Current**: 55.26% | **Target**: 80%+ | **Gap**: -24.74 points

**Why This Agent?**
- Memory system is critical infrastructure
- Framework exists, needs persistence integration
- Medium effort, high value

**Action Plan**:
1. **Review memory architecture** (1 hour):
   - Understand current in-memory implementation
   - Identify database integration points

2. **Add persistence tests** (3-4 hours):
   - Test memory storage
   - Test memory retrieval
   - Test memory search
   - Test memory expiration

3. **Integration tests** (1 hour):
   - Test with other agents
   - Test memory context passing

**Expected Result**: 55.26% → 78%+ (23+ points)

**Estimated Time**: 5-6 hours total

---

## ⚠️ **SKIP FOR NOW**

### **Low-Coverage Agents** (Require Architectural Work)

These agents have < 30% coverage and need significant refactoring:

| Agent | Coverage | Gap to 80% | Estimated Effort | Why Skip |
|-------|----------|------------|------------------|----------|
| **Maria Quitéria** | 23.23% | -56.77 | 6-10 hours | Too large, needs refactoring |
| **Abaporu** | 13.37% | -66.63 | 8-12 hours | Orchestration needs redesign |
| **Obaluaiê** | 13.11% | -66.89 | 8-12 hours | Corruption detection incomplete |
| **Céuci** | 10.49% | -69.51 | 10-15 hours | ML models not implemented |

**Recommendation**: Focus on agents that are 65-90% first. Revisit these in future sprint.

---

## 📋 **SUGGESTED SPRINT PLAN**

### **Week 1: High-Value Targets** (8-10 hours)

#### **Day 1-2: Bonifácio Fix + Tests** (3-4 hours)
- [ ] Debug framework execution issue
- [ ] Fix architectural bug
- [ ] Add 4 framework tests
- [ ] Target: 65.22% → 82%+

#### **Day 3: Quick Wins Sprint** (3 hours)
- [ ] Ayrton Senna: 89.77% → 90%+ (30 min)
- [ ] Dandara: 86.32% → 90%+ (1.5 hours)
- [ ] Oxóssi: 83.80% → 85%+ (1 hour)

#### **Day 4-5: Nanã Memory System** (5-6 hours)
- [ ] Review architecture (1 hour)
- [ ] Add persistence tests (3-4 hours)
- [ ] Integration tests (1 hour)
- [ ] Target: 55.26% → 78%+

**Week 1 Expected Results**:
- 4 agents improved
- ~45 points total gain
- 13/16 agents at 80%+ (81.25%)

---

### **Week 2: Polish & Documentation** (4-6 hours)

#### **Day 1: Final Polish** (2 hours)
- [ ] Review all 80%+ agents
- [ ] Add missing edge case tests
- [ ] Target: Get 3-4 agents to 90%+

#### **Day 2: Documentation Update** (2 hours)
- [ ] Update coverage analysis docs
- [ ] Document architectural fixes
- [ ] Create test patterns guide

#### **Day 3: Strategic Review** (2 hours)
- [ ] Re-assess low-coverage agents
- [ ] Plan refactoring strategy
- [ ] Prioritize next sprint

**Week 2 Expected Results**:
- All operational agents at 80%+
- 6-7 agents at 90%+
- Updated documentation
- Clear strategy for < 30% agents

---

## 🎓 **KEY LEARNINGS TO APPLY**

From Sessions 10-11 (October 27, 2025):

### **1. Always Verify Actual Coverage**
```bash
# Don't trust documentation, run this FIRST:
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_<agent>.py \
  --cov=src.agents.<agent> \
  --cov-report=term-missing
```

**Example**: Maria Quitéria documented at 78.48%, reality was 23.23%!

### **2. Target Massive Blocks**
Look for lines like `964-1071` (108 lines in one method!)

**Success Story**: Drummond's `process()` method
- 108-line block with 0% coverage
- Added 1 test for `process_chat` action
- Result: +8.84 points with 1 test!

### **3. Mock Everything External**
```python
from unittest.mock import AsyncMock, patch

with patch(
    "src.agents.tiradentes.export_service.generate_pdf",
    new_callable=AsyncMock,
    return_value=mock_pdf_bytes,
):
    result = await agent._render_pdf(...)
```

### **4. Know When to Stop**
- 90%+ is excellent, don't chase 100%
- Remaining gaps are often scattered partial branches
- ROI drops significantly after 90%

**Example**: Tiradentes stopped at 92.18%
- Remaining 2.82 points would need ~7-8 tests
- Better to move to next agent

---

## 🛠️ **QUICK START COMMANDS**

```bash
# Check specific agent coverage
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_bonifacio.py \
  --cov=src.agents.bonifacio \
  --cov-report=term-missing

# Find missing lines
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_bonifacio.py \
  --cov=src.agents.bonifacio \
  --cov-report=term-missing:skip-covered 2>&1 | grep "bonifacio.py"

# Run single test
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
  tests/unit/agents/test_bonifacio.py::TestClass::test_method -v

# Full test suite
JWT_SECRET_KEY=test SECRET_KEY=test make test-unit
```

---

## 📚 **REFERENCE DOCUMENTS**

### **Must Read Before Starting**:
1. **Quick Reference**: `docs/project/COVERAGE_QUICK_REFERENCE_2025_10_27.md`
   - Common patterns
   - Troubleshooting guide
   - Testing checklist

2. **Session 10-11 Report**: `docs/project/SESSIONS_10_11_COVERAGE_SPRINT_2025_10_27.md`
   - Complete analysis
   - Lessons learned
   - Technical details

3. **Overall Coverage**: `docs/project/COVERAGE_ANALYSIS_COMPLETE_2025_10_25.md`
   - All agents status
   - Historical data

### **Agent-Specific Docs**:
- `docs/agents/bonifacio.md` - Legal compliance agent
- `docs/agents/nana.md` - Memory system agent
- `docs/agents/ayrton_senna.md` - Intent detection agent

---

## 🎯 **SUCCESS CRITERIA**

### **Sprint Goal: 80%+ for All Operational Agents**

**Current**: 11/16 agents at 80%+ (68.75%)
**Target**: 14/16 agents at 80%+ (87.5%)

**Metrics to Track**:
- [ ] Bonifácio: 65.22% → 82%+
- [ ] Ayrton Senna: 89.77% → 90%+
- [ ] Dandara: 86.32% → 90%+
- [ ] Oxóssi: 83.80% → 85%+
- [ ] Nanã: 55.26% → 78%+

**Stretch Goals**:
- [ ] 7+ agents at 90%+ coverage
- [ ] Overall project coverage: 75%+
- [ ] All Tier 1 agents at 85%+

---

## ⚡ **TL;DR - Start Here!**

1. **Read**: `docs/project/COVERAGE_QUICK_REFERENCE_2025_10_27.md`

2. **Run**: Verify Bonifácio coverage
   ```bash
   JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/pytest \
     tests/unit/agents/test_bonifacio.py \
     --cov=src.agents.bonifacio \
     --cov-report=term-missing
   ```

3. **Investigate**: Lines 1280-1425 (151-line method)
   - Why aren't framework methods being called?
   - Where should execution happen?

4. **Fix**: Architectural bug

5. **Test**: Add 4 framework tests

6. **Result**: 65.22% → 82%+ 🎉

---

**Ready to start? Open the Quick Reference guide and let's boost that coverage!** 🚀

**Questions?** Check `docs/project/SESSIONS_10_11_COVERAGE_SPRINT_2025_10_27.md` for detailed examples and troubleshooting.

---

**Last Session Results**: +10 points in 2 hours | ROI: 15 points/hour | Keep that momentum! 💪
