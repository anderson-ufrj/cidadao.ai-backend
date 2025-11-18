# Agent Coverage Matrix

**Purpose**: Track test coverage, documentation, and operational status for all agents
**Last Updated**: 2025-11-19 (Sprint 2025-11-19 - Dia 1)
**Total Agents**: 16 operational + 1 base framework

---

## 📊 Coverage Summary

| Metric | Count | Percentage | Status |
|--------|-------|------------|--------|
| **Agents with Tests** | 16/16 | 100% | ✅ Complete |
| **Agents with Docs** | 16/16 | 100% | ✅ Complete |
| **Tier 1 (Excellent)** | 13/16 | 81.3% | ✅ Excellent (+3 desde 18/11) |
| **Tier 2 (Good)** | 2/16 | 12.5% | 🟢 Improving (-3 desde 18/11) |
| **Tier 3 (Basic)** | 1/16 | 6.2% | ⚠️ Needs API integration |
| **Avg Test Coverage** | ~77%+ | - | 🟢 Improving (Target: 80%) |

---

## 🎯 Agent Matrix

### Tier 1: Excellent (>75% coverage, fully functional)

| Agent | File | Lines | Tests | Coverage | Docs | Status |
|-------|------|-------|-------|----------|------|--------|
| **Obaluaiê** 🆕 | `obaluaie.py` | 987 | ✅ 24 tests | **93.79%** 🚀 | ✅ Complete | 🟢 Production |
| **Drummond** | `drummond.py` | 1,707 | ✅ 64 tests | 79.32% | ✅ Complete | 🟢 Production |
| **Nanã** ✅ | `nana.py` | 1,123 | ✅ 28 tests | **80.16%** | ✅ Complete | 🟢 Production |
| **Zumbi** | `zumbi.py` | 1,523 | ✅ 45 tests | 85.23% | ✅ Complete | 🟢 Production |
| **Anita** | `anita.py` | 1,342 | ✅ 38 tests | 82.14% | ✅ Complete | 🟢 Production |
| **Oxóssi** | `oxossi.py` | 1,287 | ✅ 34 tests | 79.56% | ✅ Complete | 🟢 Production |
| **Lampião** | `lampiao.py` | 1,198 | ✅ 31 tests | 78.92% | ✅ Complete | 🟢 Production |
| **Senna** | `ayrton_senna.py` | 1,156 | ✅ 29 tests | 77.41% | ✅ Complete | 🟢 Production |
| **Tiradentes** | `tiradentes.py` | 1,543 | ✅ 19 tests | 76.20% | ✅ Complete | 🟢 Production |
| **Niemeyer** | `oscar_niemeyer.py` | 1,234 | ✅ 27 tests | 76.15% | ✅ Complete | 🟢 Production |
| **Machado** | `machado.py` | 1,089 | ✅ 25 tests | 75.84% | ✅ Complete | 🟢 Production |
| **Bonifácio** | `bonifacio.py` | 1,021 | ✅ 23 tests | 75.63% | ✅ Complete | 🟢 Production |
| **Maria Quitéria** | `maria_quiteria.py` | 978 | ✅ 21 tests | 75.22% | ✅ Complete | 🟢 Production |

**Tier 1 Summary**:
- **Total**: 13 agents (81.3% of fleet) 🚀 **+3 desde 18/11**
- **Avg Coverage**: ~79.2%
- **Avg Tests**: ~31.3 tests/agent
- **Status**: All production-ready
- **Recent Additions**: Obaluaiê (+21.60pp to 93.79%), Nanã (validated at 80.16%), Drummond (validated at 79.32%)

---

### Tier 2: Good (50-75% coverage, mostly functional)

| Agent | File | Lines | Tests | Coverage | Docs | Status |
|-------|------|-------|-------|----------|------|--------|
| **Abaporu** 🔄 | `abaporu.py` | 1,654 | ✅ 43 tests | **74.94%** (+1.46pp) | ✅ Complete | 🟡 Near prod (-1.06% to Tier 1) |
| **Céuci** ⚠️ | `ceuci.py` | 1,045 | ✅ 44 tests | **30.30%** (dual arch) | ✅ Complete | 🟡 Architecture refactor needed |

**Tier 2 Notes**:
- **Abaporu**: Improved from 73.48% to 74.94% (+1.46pp). Only **1.06% away from Tier 1**. Core workflow (lines 293-398, 110 lines) needs integration tests.
- **Céuci**: **CRITICAL DISCOVERY** - Dual architecture pattern identified:
  - **Simple API** (process() → stubs): 30% covered
  - **Complex ML API** (predict_time_series() → full pipeline): 0% covered (lines 292-1202 never executed)
  - **44 tests added** (+8 integration tests) prepare for future unification
  - **Cannot boost coverage** without connecting both APIs or architectural decision

**Tier 2 Summary**:
- **Total**: 2 agents (12.5% of fleet) 🟢 **-3 desde 18/11** (great progress!)
- **Avg Coverage**: ~52.6% (affected by Céuci's dual architecture)
- **Status**: 1 near Tier 1, 1 blocked by architecture

---

### Tier 3: Basic (framework complete, integration pending)

| Agent | File | Lines | Tests | Coverage | Docs | Status |
|-------|------|-------|-------|----------|------|--------|
| **Dandara** | `dandara.py` | 1,234 | ✅ 18 tests | 86.32% | ✅ Complete | 🟡 Framework ready |

**Tier 3 Notes**:
- Dandara has excellent test coverage (86.32%)
- Framework is complete and well-tested
- Missing real API integration (using mock data)
- Will move to Tier 1 once APIs are integrated

**Tier 3 Summary**:
- **Total**: 1 agent (6.2% of fleet)
- **Coverage**: 86.32%
- **Status**: Framework complete, API integration pending

---

### Base Framework

| Component | File | Lines | Tests | Coverage | Docs | Status |
|-----------|------|-------|-------|----------|------|--------|
| **Deodoro** | `deodoro.py` | 478 | ✅ Inherited | 96.45% | ✅ Complete | 🟢 Production |

**Base Framework Notes**:
- Deodoro is the foundation for all 16 agents
- Not counted in "operational agent" statistics
- Excellent coverage from all agent tests
- Contains ReflectiveAgent, BaseAgent, AgentMessage, etc.

---

## 📈 Detailed Metrics

### Test Distribution

```
Tests by Agent:
Drummond    ████████████████████████████████████████  117 tests
Zumbi       ████████████████                           45 tests
Abaporu     ████████████████                           42 tests
Anita       █████████████                              38 tests
Oxóssi      ███████████                                34 tests
Lampião     ██████████                                 31 tests
Senna       █████████                                  29 tests
Nanã        ████████                                   28 tests
Niemeyer    ████████                                   27 tests
Machado     ███████                                    25 tests
Céuci       ███████                                    24 tests
Bonifácio   ██████                                     23 tests
Obaluaiê    ██████                                     22 tests
Maria Q.    ██████                                     21 tests
Tiradentes  █████                                      19 tests
Dandara     █████                                      18 tests
```

**Total Tests**: 563 tests across 16 agents
**Average**: 35.2 tests per agent
**Median**: 26 tests per agent

### Coverage Distribution

```
Coverage Ranges:
90%+   ██  2 agents (Drummond 91.54%, Dandara 86.32%)
80-90% ████████  8 agents (Tier 1 top performers)
70-80% ██████  4 agents (Tier 1 lower + Tier 2 top)
60-70% ██  2 agents (Tier 2 bottom)
<60%   ∅  0 agents (excellent!)
```

### Lines of Code

```
Total Lines by Tier:
Tier 1:  11,831 lines (47.0%)
Tier 2:   6,516 lines (25.9%)
Tier 3:   1,234 lines ( 4.9%)
Base:       478 lines ( 1.9%)
Utils:    1,846 lines ( 7.3%)
Tests:    3,261 lines (13.0%)

Grand Total: 25,166 lines
```

---

## 🎯 Quality Gates

### ✅ Passing Gates

- [x] 100% agents have tests (16/16)
- [x] 100% agents have documentation (16/16)
- [x] 62.5% agents in Tier 1 (excellent)
- [x] 0% agents without coverage

### ⚠️ Improvement Needed

- [ ] Average coverage < 80% (current: 76.29%, gap: 3.71%)
- [ ] 5 agents in Tier 2 (need 5-10% coverage boost)
- [ ] 1 agent in Tier 3 (needs API integration)
- [ ] Drummond import issue on HuggingFace Spaces

---

## 🚀 Roadmap to 100%

### Phase 1: Boost Tier 2 to Tier 1 (Est: 2-3 days)

**Target Agents**:
1. **Nanã** (68.92% → 76%): Add 5 edge case tests
2. **Céuci** (65.31% → 76%): Add 7 validation tests
3. **Obaluaiê** (62.18% → 76%): Add 9 error handling tests
4. **Abaporu** (73.45% → 76%): Add 2 reflection tests

**Expected Outcome**: 14/16 agents in Tier 1 (87.5%)

### Phase 2: Resolve Drummond Import Issue (Est: 1 day)

**Problem**: Circular dependency with MaritacaClient causes HF Spaces failure
**Solution Options**:
1. Lazy import MaritacaClient inside methods
2. Create drummond_full.py and drummond_simple.py split
3. Move MaritacaClient to separate module

**Expected Outcome**: Drummond uncommented in `__init__.py`

### Phase 3: Integrate Dandara APIs (Est: 3-5 days)

**Required Work**:
1. Connect to real government transparency APIs
2. Replace mock data with live data fetching
3. Add API error handling
4. Add rate limiting
5. Add caching layer

**Expected Outcome**: Dandara moves to Tier 1

### Final Goal

**Target Metrics** (achievable in 1-2 weeks):
- ✅ 100% agents with tests (already achieved!)
- ✅ 100% agents with docs (already achieved!)
- ⏳ 95% average coverage (from 76.29%)
- ⏳ 15/16 agents in Tier 1 (93.75%)
- ⏳ 0 agents in Tier 3

---

## 🔍 Coverage Analysis by Agent

### Top Performers 🏆

1. **Drummond** - 91.54% (117 tests) - Exception due to HF issue
2. **Dandara** - 86.32% (18 tests) - Framework complete
3. **Zumbi** - 85.23% (45 tests) - Investigation leader
4. **Anita** - 82.14% (38 tests) - Analysis expert
5. **Oxóssi** - 79.56% (34 tests) - Pattern detective

### Needs Attention ⚠️

1. **Céuci** - 30.30% (44 tests) - ⚠️ **BLOCKED: Dual architecture needs refactoring**
2. **Abaporu** - 74.94% (43 tests) - Only **1.06% away from Tier 1**

**Strategy Update (2025-11-19)**:
- ✅ **Obaluaiê**: COMPLETED - Moved to Tier 1 with 93.79% (+21.60pp)
- ✅ **Nanã**: Already Tier 1 - Validated at 80.16%
- 🟡 **Abaporu**: Add 2-3 integration tests to close 1.06% gap
- ⚠️ **Céuci**: Architectural decision required before coverage boost

---

## 📚 Documentation Status

All agents have complete documentation in `docs/agents/`:

| Agent | Doc File | Sections | Examples | Status |
|-------|----------|----------|----------|--------|
| Zumbi | `zumbi.md` | 12 | ✅ 5 | ✅ Complete |
| Anita | `anita.md` | 10 | ✅ 4 | ✅ Complete |
| Oxóssi | `oxossi.md` | 11 | ✅ 4 | ✅ Complete |
| Lampião | `lampiao.md` | 9 | ✅ 3 | ✅ Complete |
| Senna | `ayrton_senna.md` | 8 | ✅ 3 | ✅ Complete |
| Tiradentes | `tiradentes.md` | 10 | ✅ 4 | ✅ Complete |
| Niemeyer | `oscar_niemeyer.md` | 9 | ✅ 3 | ✅ Complete |
| Machado | `machado.md` | 8 | ✅ 3 | ✅ Complete |
| Bonifácio | `bonifacio.md` | 7 | ✅ 2 | ✅ Complete |
| Maria Quitéria | `maria_quiteria.md` | 7 | ✅ 2 | ✅ Complete |
| Abaporu | `abaporu.md` | 11 | ✅ 4 | ✅ Complete |
| Nanã | `nana.md` | 8 | ✅ 3 | ✅ Complete |
| Drummond | `drummond.md` | 13 | ✅ 6 | ✅ Complete |
| Céuci | `ceuci.md` | 7 | ✅ 2 | ✅ Complete |
| Obaluaiê | `obaluaie.md` | 7 | ✅ 2 | ✅ Complete |
| Dandara | `dandara.md` | 9 | ✅ 3 | ✅ Complete |

**Total**: 144 documentation sections, 51 code examples

---

## 🎬 Action Items

### Immediate (Sprint 2025-11-19 - In Progress)

1. ✅ Create test for Tiradentes (DONE - 19 tests added, Sprint anterior)
2. ✅ Add 9 tests for Obaluaiê (DONE - 93.79% coverage achieved 🚀)
3. ✅ Validate Nanã coverage (DONE - Already at 80.16%, no work needed)
4. ✅ Validate Drummond import (DONE - No issue exists, 79.32% coverage)
5. 🔄 Add integration tests for Abaporu (IN PROGRESS - 74.94%, need +1.06%)
6. ⚠️ Decide Céuci architecture strategy (BLOCKED - Dual architecture discovered)

### Short Term (Next 2-3 Days)

1. ✅ Drummond import issue (Already resolved - no issue exists)
2. 🟡 Finish Abaporu boost to 76%+ (2-3 integration tests needed)
3. ⚠️ Make architectural decision for Céuci (unify vs document vs deprecate)
4. ⏳ Begin Dandara API integration (Planned for Dia 3-4)
5. ⏳ Update CI to enforce 80% coverage

### Long Term (Next Month)

1. Complete Dandara API integration
2. Achieve 15/16 agents in Tier 1
3. Reach 95% average coverage
4. Document Tier 1 best practices

---

## 📊 Historical Progress

| Date | Agents w/ Tests | Avg Coverage | Tier 1 Count |
|------|----------------|--------------|--------------|
| 2025-10-01 | 12/16 (75%) | 68.5% | 6 agents |
| 2025-10-15 | 14/16 (87.5%) | 72.3% | 8 agents |
| 2025-11-01 | 15/16 (93.8%) | 74.8% | 9 agents |
| 2025-11-14 | 15/16 (93.8%) | 76.1% | 10 agents |
| 2025-11-18 | 16/16 (100%) | 76.29% | 10 agents |
| **2025-11-19** | **16/16 (100%)** | **~77%+** | **13 agents** 🚀 |

**Trend**: Accelerated improvement, +3 agents to Tier 1 in 1 day (Sprint 2025-11-19)
**Recent Win**: Obaluaiê +21.60pp (72.19% → 93.79%), now top Tier 1 performer

---

## 🏆 Agent Tiers Definition

### Tier 1: Excellent ⭐⭐⭐
- **Coverage**: >75%
- **Tests**: Comprehensive suite
- **Status**: Production-ready
- **Documentation**: Complete with examples
- **Functionality**: 100% operational

### Tier 2: Good ⭐⭐
- **Coverage**: 50-75%
- **Tests**: Solid suite, gaps exist
- **Status**: Near production
- **Documentation**: Complete
- **Functionality**: 85-95% operational

### Tier 3: Basic ⭐
- **Coverage**: <50% or framework-only
- **Tests**: Basic suite
- **Status**: Framework ready
- **Documentation**: Complete
- **Functionality**: Framework complete, integration pending

---

**Last Updated**: 2025-11-19 (Sprint 2025-11-19 - Dia 1 completed)
**Next Review**: 2025-11-20 (Dia 2)
**Maintained By**: Anderson Henrique da Silva

---

## 📝 Sprint 2025-11-19 Updates

### Dia 1 Achievements (19 Nov 2025)
- ✅ **Obaluaiê**: 72.19% → **93.79%** (+21.60pp) - Moved to Tier 1 🚀
- ✅ **Nanã**: Validated at **80.16%** - Already Tier 1 (matriz estava desatualizada)
- ✅ **Drummond**: Validated at **79.32%** - Already Tier 1 (issue fantasma resolvido)
- 🔄 **Abaporu**: 73.48% → **74.94%** (+1.46pp) - Gap de apenas 1.06% para Tier 1
- ⚠️ **Céuci**: **Arquitetura dual descoberta** - 30.30% (bloqueado até decisão arquitetural)

### Key Discoveries
1. **Matriz desatualizada**: Nanã e Drummond já eram Tier 1
2. **Céuci dual architecture**: Simple API (30%) vs Complex ML API (0%) não conectadas
3. **Drummond import**: Issue não existe, funciona perfeitamente
4. **Abaporu workflow**: Core investigation (lines 293-398) precisa integration tests

### Progress
- **Tier 1**: 10 → 13 agentes (+3 em 1 dia) 🚀
- **Tier 2**: 5 → 2 agentes (-3 movidos para Tier 1)
- **Coverage média**: 76.29% → ~77%+ (improving)
- **Testes adicionados**: 19 novos testes
- **Commits**: 4 commits pushed com sucesso
