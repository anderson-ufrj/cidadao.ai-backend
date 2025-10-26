# 📊 Zumbi Agent - Detailed Coverage Analysis

**Data**: Domingo, 26 de outubro de 2025, 19:00 -03
**Objetivo**: Análise detalhada do coverage para planejar melhorias estratégicas
**Baseline Coverage**: **88.26%** (395 statements, 36 missing, 150 branches, 26 partial)
**Target**: **95%+** coverage

---

## 🎯 **EXECUTIVE SUMMARY**

### **Current Status**
- **Coverage**: 88.26% (395 stmts, 36 miss, 150 branches, 26 partial)
- **Test Files**: 1 file (test_zumbi.py) with 37 tests passing, 3 skipped
- **Agent LOC**: 1,427 lines (medium-sized agent)
- **Missing Lines**: 36 lines + 26 partial branches

### **Strategic Position**
- **Tier 1 Agent**: Fully operational (Anomaly detection specialist with FFT spectral analysis)
- **Production Critical**: Core investigation agent used in real-time analysis
- **ROI Potential**: MEDIUM (only 11.74 points to reach 95%+, but already high at 88.26%)

### **Recommended Strategy**
Focus on **Error Handling & Edge Cases** - Skip complex ML fallback paths

---

## 📋 **MISSING LINES ANALYSIS**

### **Category 1: Models Client Fallback (LOW PRIORITY)** 🟢

**Lines**: 128-129
**Total**: 2 lines
**Coverage Impact**: ~0.5 percentage points
**Complexity**: TRIVIAL (logging only)

**What's Missing**:
```python
# Lines 128-129: Models API disabled fallback
else:
    self.models_client = None
    self.logger.info("Models API disabled, using only local ML")
```

**Why Not Covered**:
- Tests always run with models API enabled (`settings.models_api_enabled = True`)
- This is only hit when environment variable `MODELS_API_ENABLED=false`

**Tests Needed** (1 test):
1. `test_initialization_models_api_disabled` - Test Zumbi with `MODELS_API_ENABLED=false`

**Estimated Time**: 15 minutes
**Expected Coverage Gain**: +0.5 points (88.26% → 88.76%)

**Recommendation**: ⚠️ **SKIP** (not worth effort, low value)

---

### **Category 2: Date Range Parsing Exception (MEDIUM PRIORITY)** 🟡

**Lines**: 399-404
**Total**: 6 lines
**Coverage Impact**: ~1.5 percentage points
**Complexity**: LOW (exception handling)

**What's Missing**:
```python
# Lines 399-404: Date range parsing with fallback
if request.date_range:
    try:
        # Extract year from date range (format: DD/MM/YYYY)
        year_part = request.date_range[0].split("/")[2]
        year = int(year_part)
    except (IndexError, ValueError):
        pass  # ❌ Line 404 not covered - exception fallback
```

**Why Not Covered**:
- Tests always provide valid date ranges
- Exception path never exercised (malformed date like "invalid/date" or "2024")

**Tests Needed** (2 tests):
1. `test_collect_contracts_invalid_date_format` - Test with malformed date range
2. `test_collect_contracts_empty_date_parts` - Test with date like "2024" (no slashes)

**Estimated Time**: 30 minutes
**Expected Coverage Gain**: +1.5 points (88.76% → 90.26%)

**Recommendation**: ✅ **DO THIS** (good ROI, important edge case)

---

### **Category 3: Multi-Source Fetch Error Logging (MEDIUM PRIORITY)** 🟡

**Lines**: 451-457, 476-488
**Total**: 19 lines
**Coverage Impact**: ~4.8 percentage points
**Complexity**: MEDIUM (error handling from multiple sources)

**What's Missing**:
```python
# Lines 451-457: Error logging when some sources fail
for error in result.get("errors", []):
    TRANSPARENCY_API_DATA_FETCHED.labels(
        endpoint="contracts",
        organization=error.get("api", "unknown"),
        status="failed",
    ).inc()

    self.logger.warning(
        "source_fetch_failed",
        api=error.get("api"),
        error=error.get("error"),
        investigation_id=context.investigation_id,
    )

# Lines 476-488: Catastrophic failure fallback
except Exception as e:
    self.logger.error(
        "multi_source_fetch_failed",
        error=str(e),
        investigation_id=context.investigation_id,
    )

    TRANSPARENCY_API_DATA_FETCHED.labels(
        endpoint="contracts", organization="multi_source", status="failed"
    ).inc()

    return []  # Return empty list on total failure
```

**Why Not Covered**:
- Tests always use mocked successful responses
- Never simulate API errors or source failures

**Tests Needed** (3 tests):
1. `test_collect_contracts_with_source_errors` - Test when some sources fail (partial success)
2. `test_collect_contracts_total_failure` - Test when collector raises exception
3. `test_collect_contracts_error_metrics` - Verify Prometheus metrics on errors

**Estimated Time**: 1-1.5 hours
**Expected Coverage Gain**: +4.8 points (90.26% → 95.06%)

**Recommendation**: ✅ **DO THIS** (critical error handling, production important)

---

### **Category 4: Open Data Enrichment Success Path (LOW-MEDIUM PRIORITY)** 🟢

**Lines**: 519-522
**Total**: 4 lines
**Coverage Impact**: ~1.0 percentage points
**Complexity**: LOW (success logging)

**What's Missing**:
```python
# Lines 519-522: Open data found and logged
if result.success and result.data:
    related_datasets[org_name] = result.data.get("datasets", [])

    self.logger.info(
        "open_data_found",
        organization=org_name,
        datasets_count=len(related_datasets[org_name]),
        # ... more fields
    )
```

**Why Not Covered**:
- `_enrich_with_open_data` is called but DadosGovTool always returns empty/failed results in tests
- Need to mock successful open data retrieval

**Tests Needed** (1 test):
1. `test_enrich_with_open_data_success` - Mock DadosGovTool returning datasets

**Estimated Time**: 30-45 minutes
**Expected Coverage Gain**: +1.0 points (95.06% → 96.06%)

**Recommendation**: 🟡 **OPTIONAL** (good for completeness, but already at 95%)

---

### **Category 5: Spectral Analysis Exception Handling (LOW PRIORITY)** 🟢

**Lines**: 1185-1186
**Total**: 2 lines
**Coverage Impact**: ~0.5 percentage points
**Complexity**: LOW (exception logging)

**What's Missing**:
```python
# Lines 1185-1186: Spectral analysis exception fallback
except Exception as e:
    self.logger.error(f"Error in spectral anomaly detection: {str(e)}")
    # Don't fail the entire investigation if spectral analysis fails
```

**Why Not Covered**:
- SpectralAnalyzer never raises exceptions in tests
- Need to mock analyzer to raise exception

**Tests Needed** (1 test):
1. `test_detect_spectral_anomalies_exception` - Mock SpectralAnalyzer raising exception

**Estimated Time**: 20 minutes
**Expected Coverage Gain**: +0.5 points (96.06% → 96.56%)

**Recommendation**: ⚠️ **SKIP** (low value, already >96%)

---

### **Category 6: Time Series Date Parsing Edge Cases (LOW PRIORITY)** 🟢

**Lines**: 1206, 1211->1197, 1223->1197, 1235-1236
**Total**: ~6 lines
**Coverage Impact**: ~1.5 percentage points
**Complexity**: LOW (date parsing fallbacks)

**What's Missing**:
```python
# Line 1206: No date found in contract
if not date_str:
    continue

# Lines 1211, 1223: Date parsing failures
# Various branches for date format parsing errors
```

**Why Not Covered**:
- Tests always provide contracts with valid dates
- Never test contracts with missing/invalid dates

**Tests Needed** (2 tests):
1. `test_prepare_time_series_missing_dates` - Test contracts with no date fields
2. `test_prepare_time_series_invalid_date_formats` - Test contracts with malformed dates

**Estimated Time**: 30 minutes
**Expected Coverage Gain**: +1.5 points (96.56% → 98.06%)

**Recommendation**: ⚠️ **SKIP** (diminishing returns, already >96%)

---

### **Category 7: Reflection Method & Other Branches (SKIP)** ⚪

**Lines**: 1351-1352, 1369-1372, various other branches
**Total**: ~15 lines
**Coverage Impact**: ~3.8 percentage points
**Complexity**: HIGH (complex logic paths)

**Recommendation**: ⚠️ **SKIP** (too complex, low ROI for 88.26% → 92%)

---

## 🎯 **STRATEGIC ROADMAP**

### **RECOMMENDED APPROACH: Focus on Categories 2 + 3 Only**

#### **Phase 1: Date Range Exception Handling (30 min)** ✅ MEDIUM PRIORITY
- **Target**: Lines 399-404 (~6 lines)
- **Tests**: 2 new tests in `TestZumbiEdgeCases` class
- **Expected Coverage**: 88.26% → 90.26% (+2.0 points)
- **Confidence**: HIGH (simple exception handling)

**Test Class Structure**:
```python
class TestZumbiEdgeCases:
    """Test edge cases and error handling in Zumbi agent."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_collect_contracts_invalid_date_format(self, zumbi_agent, agent_context):
        """Test date range parsing with invalid format - Lines 399-404."""
        request = ContractRequest(
            date_range=["invalid/date/format", "25/10/2025"],
            max_records=10
        )

        # Should not crash, should use default year 2024
        contracts = await zumbi_agent._collect_contracts(request, agent_context)
        # Assertions...

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_collect_contracts_empty_date_parts(self, zumbi_agent, agent_context):
        """Test date range parsing with missing parts - Line 404."""
        request = ContractRequest(
            date_range=["2024", "2025"],  # No slashes
            max_records=10
        )

        # Should fall back to default year
        contracts = await zumbi_agent._collect_contracts(request, agent_context)
        # Assertions...
```

#### **Phase 2: Multi-Source Error Handling (1-1.5 hours)** 🔥 HIGH PRIORITY
- **Target**: Lines 451-457, 476-488 (~19 lines)
- **Tests**: 3 new tests in `TestZumbiErrorHandling` class
- **Expected Coverage**: 90.26% → 95.06% (+4.8 points)
- **Confidence**: HIGH (critical production error paths)

**Test Class Structure**:
```python
class TestZumbiErrorHandling:
    """Test error handling and resilience in Zumbi agent."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_collect_contracts_with_source_errors(self, zumbi_agent, agent_context, mocker):
        """Test partial source failures - Lines 451-457."""
        # Mock collector to return success with some errors
        mock_collector = mocker.Mock()
        mock_collector.collect_contracts = AsyncMock(return_value={
            "total": 5,
            "contracts": [...],  # 5 contracts
            "sources": ["portal_transparencia", "tce_sp"],
            "errors": [
                {"api": "tce_rj", "error": "Connection timeout"},
                {"api": "ckan_sp", "error": "404 Not Found"}
            ]
        })
        mocker.patch("src.agents.zumbi.get_transparency_collector", return_value=mock_collector)

        # Should log warnings but not fail
        contracts = await zumbi_agent._collect_contracts(request, agent_context)
        assert len(contracts) == 5
        # Verify metrics were incremented for failed sources

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_collect_contracts_total_failure(self, zumbi_agent, agent_context, mocker):
        """Test catastrophic collector failure - Lines 476-488."""
        # Mock collector to raise exception
        mock_collector = mocker.Mock()
        mock_collector.collect_contracts = AsyncMock(side_effect=Exception("Database connection failed"))
        mocker.patch("src.agents.zumbi.get_transparency_collector", return_value=mock_collector)

        # Should return empty list, not crash
        contracts = await zumbi_agent._collect_contracts(request, agent_context)
        assert contracts == []
        # Verify error was logged and metric incremented

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_collect_contracts_error_metrics(self, zumbi_agent, agent_context, mocker):
        """Test Prometheus metrics on errors - Lines 451-457, 484-486."""
        # Mock collector with errors
        # Verify TRANSPARENCY_API_DATA_FETCHED.labels(...).inc() was called
        # with correct parameters
```

#### **Phase 3 (Optional): Open Data Enrichment (30-45 min)** 🟢
- **Target**: Lines 519-522 (~4 lines)
- **Tests**: 1 new test
- **Expected Coverage**: 95.06% → 96.06%
- **Confidence**: MEDIUM
- **Decision**: Only if we want >95% coverage

---

## 📊 **ROI ANALYSIS**

### **Effort vs. Impact**

| Category | Lines | Tests | Hours | Coverage Gain | ROI (points/hour) |
|----------|-------|-------|-------|---------------|-------------------|
| **Category 2 (Date)** | 6 | 2 | 0.5 | +2.0% | **4.0** 🔥 BEST! |
| **Category 3 (Errors)** | 19 | 3 | 1.0-1.5 | +4.8% | **3.2-4.8** 🔥 EXCELLENT! |
| **Category 4 (OpenData)** | 4 | 1 | 0.5-0.75 | +1.0% | **1.3-2.0** ⭐ |
| Category 1 (Models) | 2 | 1 | 0.25 | +0.5% | 2.0 ❌ Skip |
| Category 5 (Spectral) | 2 | 1 | 0.3 | +0.5% | 1.7 ❌ Skip |
| Category 6 (TimeSeries) | 6 | 2 | 0.5 | +1.5% | 3.0 ❌ Skip (>96%) |
| Category 7 (Reflection) | 15 | 5+ | 2-3 | +3.8% | 1.3-1.9 ❌ Skip |

### **BEST STRATEGY: Categories 2 + 3 Only**
- **Total Time**: 1.5-2 hours
- **Total Tests**: 5 tests
- **Coverage Gain**: +6.8 points (88.26% → **95.06%**!) 🎉
- **Average ROI**: **3.4-4.5 points/hour** (excellent!)

### **Why Skip Other Categories?**
1. **Category 1 (Models Fallback)**: Low value, only hit in specific config
2. **Category 5 (Spectral Exception)**: Low value, already >96% after Phase 2
3. **Category 6 (Time Series)**: Diminishing returns (>96%)
4. **Category 7 (Reflection)**: Complex, low ROI, high effort

---

## 🚀 **EXECUTION PLAN**

### **Today (Domingo 26/10 - Evening)**

**Phase 1: Date Range Exception Tests (30 min)** ⚡
- **Time**: 30 minutes (quick!)
- **Result**: 88.26% → 90.26%
- **Files**: Add `TestZumbiEdgeCases` tests to `test_zumbi.py`

**Phase 2: Multi-Source Error Tests (1-1.5 hours)** 🔥 RECOMMENDED!
- **Time**: 1-1.5 hours
- **Result**: 90.26% → 95.06%
- **Files**: Add `TestZumbiErrorHandling` class to `test_zumbi.py`
- **Rationale**: Critical production error paths, high ROI

### **Recommended Workflow**

1. **Phase 1 First** - Quick win, builds momentum
2. **Phase 2 Second** - Main coverage boost
3. **Commit & Document** - Preserve progress
4. **Optional Phase 3** - Only if time permits and we want >95%

---

## 💡 **STRATEGIC RECOMMENDATION**

### **DO PHASES 1 + 2** 🥇

**Why?**
1. ✅ **High ROI**: 3.4-4.5 points/hour (excellent efficiency)
2. ✅ **Production Critical**: Tests real error handling paths
3. ✅ **Reaches 95%**: Excellent coverage threshold
4. ✅ **Manageable Time**: 1.5-2 hours total
5. ✅ **Clear Target**: Well-defined test cases

**Why Not Phase 3?**
- 95.06% is already excellent coverage
- Diminishing returns for 1% gain
- Phase 3 can be done later if needed

---

## 📁 **FILES TO MODIFY**

### **Primary Target**
- `tests/unit/agents/test_zumbi.py` - Add 2 new test classes

### **Code Reference**
- `src/agents/zumbi.py` - Lines 399-404, 451-488 (error handling)

### **Documentation**
- `docs/project/SESSION_6_ZUMBI_2025_10_26.md` - Session log (to be created)

---

## 🎯 **SUCCESS CRITERIA**

### **Minimum Success (Phases 1 + 2)**
- ✅ 5 new tests passing
- ✅ Coverage: 88.26% → 95.06%
- ✅ All existing 37 tests still passing
- ✅ Documentation updated

### **Full Success (All 3 Phases)**
- ✅ 6 new tests passing
- ✅ Coverage: 88.26% → 96.06%
- ✅ All 43 tests passing
- ✅ Session documented

---

## 🔥 **NEXT ACTION**

**IMMEDIATE**: Start implementing Phase 1 (Date Range Exception Tests)

1. Add `TestZumbiEdgeCases` class to `test_zumbi.py`
2. Implement 2 tests for invalid date formats
3. Run tests and verify coverage reaches 90.26%
4. Commit Phase 1
5. Proceed to Phase 2 (Error Handling Tests)

**Expected Timeline**: 1.5-2 hours total
**Expected Result**: 🎉 **95.06%+ coverage!** (from 88.26%)

---

**Analysis completed**: Domingo, 26 de outubro de 2025, 19:00 -03
**Recommendation**: **Phases 1 + 2** for best ROI and production-critical coverage! 🚀
