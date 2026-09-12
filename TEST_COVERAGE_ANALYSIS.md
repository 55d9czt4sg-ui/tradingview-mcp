# Test Coverage Analysis — TradingView MCP Server

**Date:** 2026-06-25  
**Status:** Current test coverage is **0%** — no automated tests exist.

---

## Executive Summary

The TradingView MCP Server has **no automated tests**. The codebase implements 6 critical MCP tools that interact with external APIs (TradingView technical analysis, market screening, and symbol search). Without tests, the server is vulnerable to:

- Silent regressions when dependencies update
- Edge-case failures in data transformation pipelines
- Incorrect error handling breaking AI assistant workflows
- Inability to safely refactor or extend functionality

This document identifies key testing gaps and proposes a practical testing strategy.

---

## Current State: Zero Test Infrastructure

### What Exists
- **Source code:** `src/tradingview_mcp/server.py` (430 lines)
- **Test files:** None
- **Test framework configuration:** None (no pytest, tox, coverage config)
- **CI/CD test gates:** None

### What's Missing
- Unit tests for helper functions
- Integration tests for MCP tools
- Mock tests for external API calls
- Error handling validation
- Data transformation validation

---

## Code Structure Overview

### Helper Functions (Testable Units)
```
_resolve_interval()         — Map string interval to Interval constant
_resolve_screener()         — Map string screener to canonical name
_build_handler()            — Construct TA_Handler with validated params
_format_summary()           — Extract fields from Analysis object
_format_indicators()        — Filter/return indicator values
```

### MCP Tools (Integration Layer)
```
get_technical_analysis()    — Single symbol, single timeframe
get_multi_timeframe()       — Single symbol, multiple timeframes
get_indicator_values()      — Numeric indicator values
search_symbol()             — HTTP API call to TradingView symbol search
screen_market()             — Market screening with filters
get_price_data()            — OHLCV + price levels
```

---

## Critical Testing Gaps

### 1. **Helper Function Logic** (HIGH PRIORITY)
**Problem:** Interval and screener resolution have no validation.

**Gaps:**
- `_resolve_interval()` raises `ValueError` for unknown intervals — not tested
- `_resolve_screener()` silently falls back to user input — no validation of fallback
- `_build_handler()` constructs TA_Handler but doesn't validate its construction success
- Case-sensitivity edge cases (mixed-case inputs) untested

**Current Risk:**
```python
# What happens if interval is " 1D " (with spaces)?
# What if screener is "AMERICA" (uppercase)?
# These work, but only by accident. No tests prove it.
_resolve_interval("  1d  ")  # Passes: strips and lowercases
_resolve_screener("CRYPTO")  # Silently returns "CRYPTO", not "crypto"
```

**Test Cases Needed:**
- Valid intervals with whitespace and mixed case
- Invalid interval error messages
- All screener aliases map to canonical names
- Screener fallback behavior for unknown values

---

### 2. **Data Transformation** (HIGH PRIORITY)
**Problem:** `_format_summary()` and `_format_indicators()` extract nested data with no validation.

**Gaps:**
- No tests for missing/None fields in Analysis object
- No tests for NaN/inf values in indicator data
- JSON serialization not validated (custom `default=str` in screener)
- HTML stripping in `search_symbol()` untested

**Current Risk:**
```python
# What if analysis.summary is None?
# What if analysis.oscillators is missing?
# What if an indicator value is NaN?
_format_summary(analysis)  # Could crash or silently drop data
```

**Test Cases Needed:**
- Missing analysis fields → graceful handling
- NaN/inf indicators → proper JSON serialization
- HTML in description → proper stripping in search results
- Empty indicator lists

---

### 3. **External API Resilience** (HIGH PRIORITY)
**Problem:** All tools wrap calls in try/except but return error strings inconsistently.

**Gaps:**
- Network timeouts not tested (httpx timeout=15)
- API rate limiting not handled or tested
- Invalid JSON responses from search API not tested
- Screener import errors return string (not JSON) — inconsistent

**Current Risk:**
```python
# search_symbol() returns JSON on success but plain text on error
# This breaks MCP protocol and AI client parsing
return json.dumps(formatted, indent=2)  # Success → valid JSON
return f"Error searching: {e}"          # Failure → plain text
```

**Test Cases Needed:**
- Network timeout handling
- HTTP error responses (4xx, 5xx)
- Malformed API responses
- Rate limit detection
- Consistent error response format

---

### 4. **Tool Parameter Validation** (MEDIUM PRIORITY)
**Problem:** Tools accept string parameters but don't validate ranges/values upfront.

**Gaps:**
- `limit` in `screen_market()` is clamped to 50, but no test validates clamp
- `min_volume`, `min_change_pct`, `max_change_pct` ranges untested
- `sort_by` field name not validated against screener schema
- Empty `symbols` in search result not handled

**Current Risk:**
```python
# If sort_by="invalid_field", screener silently fails or returns empty
# No test catches this
q = q.order_by(sort_by, ascending=(sort_order.lower() == "asc"))
```

**Test Cases Needed:**
- Limit clamping (20 → clamped to 50)
- Negative min_volume/min_change values
- min/max change reversal (min > max)
- Invalid sort_by field behavior

---

### 5. **MCP Integration** (MEDIUM PRIORITY)
**Problem:** No tests verify tools are correctly registered as MCP tools.

**Gaps:**
- Tool docstrings not validated (AI clients read these)
- Async function execution not tested
- Return type consistency (all return `str`, some return error strings)
- Parameter defaults not tested

**Current Risk:**
```python
# Tool docstring says "comma-separated intervals", but if parsing fails:
# Tool silently returns error message instead of JSON
@mcp.tool()
async def get_multi_timeframe(..., intervals: str = "5m,15m,1h,4h,1d") -> str:
```

**Test Cases Needed:**
- All tools execute async without blocking
- Parameter defaults apply correctly
- Docstrings match parameter descriptions
- All return strings are valid JSON

---

### 6. **Edge Cases in Multi-Timeframe Analysis** (MEDIUM PRIORITY)
**Problem:** `get_multi_timeframe()` collects results from multiple intervals, but partial failures untested.

**Gaps:**
- If 3/5 intervals fail, result is mixed (2 successes, 3 errors) — not validated
- Empty intervals string handling
- Duplicate intervals not deduplicated
- Very long interval lists not rate-limited

**Current Risk:**
```python
# If one interval times out, whole response is degraded
# No test validates graceful degradation
for ivl in intervals.split(","):
    try:
        analysis = handler.get_analysis()  # May timeout
        results.append(_format_summary(analysis))
    except Exception as e:
        results.append({"interval": ivl, "error": str(e)})
```

**Test Cases Needed:**
- Partial success (some intervals succeed, some fail)
- Empty intervals string → empty results
- Duplicate intervals → deduplicate or preserve?
- 50+ intervals → rate limiting

---

### 7. **Screener Complex Filters** (MEDIUM PRIORITY)
**Problem:** `screen_market()` builds complex queries; filter logic untested.

**Gaps:**
- Filter combinations not tested (min_volume AND min_change together)
- NaN handling in DataFrame (converted to None, but inconsistently)
- Empty result set handling
- `get_scanner_data()` return structure not validated

**Current Risk:**
```python
# If result[1] (rows DataFrame) is empty or malformed, iteration silently fails
count = result[0]
rows = result[1]
for _, row in rows.iterrows():
    entry = row.to_dict()
    # What if row has unexpected columns?
```

**Test Cases Needed:**
- Filter combinations (multiple constraints)
- Empty result set (0 rows)
- NaN → None conversion validated
- Market type mapping (stock → america, etc.)

---

## Recommended Testing Strategy

### Phase 1: Unit Tests (Week 1)
**Focus:** Helper functions, input validation, data transformation

**Files to create:**
- `tests/test_helpers.py` — Unit tests for _resolve_*, _format_*, _build_*
- `tests/test_validators.py` — Parameter validation tests

**Coverage target:** 90%+ for helper functions

**Example test:**
```python
def test_resolve_interval_valid():
    assert _resolve_interval("1d") == Interval.INTERVAL_1_DAY
    assert _resolve_interval("  5m  ") == Interval.INTERVAL_5_MINUTES
    assert _resolve_interval("1H") == Interval.INTERVAL_1_HOUR

def test_resolve_interval_invalid():
    with pytest.raises(ValueError, match="Unknown interval"):
        _resolve_interval("99m")
```

### Phase 2: Integration Tests with Mocks (Week 2)
**Focus:** API interactions without hitting live APIs

**Files to create:**
- `tests/test_tools.py` — Mocked integration tests for each tool
- `tests/conftest.py` — Pytest fixtures for mock Analysis and Handler

**Coverage target:** 70%+ for tool functions

**Example test:**
```python
@pytest.mark.asyncio
async def test_get_technical_analysis_success(mock_handler):
    mock_handler.get_analysis.return_value = Mock(
        symbol="AAPL",
        exchange="NASDAQ",
        interval="1d",
        summary="BUY",
        oscillators={"RSI": 75},
        moving_averages={"EMA20": 150.0},
    )
    
    result = await get_technical_analysis("AAPL", "NASDAQ")
    data = json.loads(result)
    assert data["symbol"] == "AAPL"
    assert data["summary"] == "BUY"
```

### Phase 3: Error Handling & Resilience (Week 3)
**Focus:** Network failures, malformed responses, timeout handling

**Files to create:**
- `tests/test_error_handling.py` — Error scenarios

**Coverage target:** 80%+ for exception paths

**Example test:**
```python
@pytest.mark.asyncio
async def test_search_symbol_network_timeout():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.TimeoutException("timeout")
        result = await search_symbol("AAPL")
        assert "Error searching" in result

@pytest.mark.asyncio
async def test_search_symbol_malformed_json():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json.side_effect = json.JSONDecodeError("error", "", 0)
        result = await search_symbol("AAPL")
        assert "Error searching" in result
```

### Phase 4: Regression Tests (Ongoing)
**Focus:** Document known behavior, catch future regressions

**Files to create:**
- `tests/test_regressions.py` — Tests for reported issues

---

## Testing Infrastructure Setup

### 1. **Install Testing Dependencies**
Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "pytest-mock>=3.10",
    "httpx[testing]>=0.27",
]
```

Command:
```bash
uv pip install -e ".[test]"
```

### 2. **Create Test Structure**
```
tradingview-mcp/
├── src/tradingview_mcp/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_helpers.py          # Unit tests
│   ├── test_validators.py       # Parameter validation
│   ├── test_tools.py            # Tool integration tests
│   ├── test_error_handling.py   # Error scenarios
│   └── test_regressions.py      # Known issues
└── pytest.ini                   # Pytest config
```

### 3. **Pytest Configuration**
Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    --strict-markers
    --cov=src/tradingview_mcp
    --cov-report=html
    --cov-report=term-missing
    --tb=short
markers =
    asyncio: async test
    integration: integration test
    slow: slow test
```

### 4. **Run Tests**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run specific test file
pytest tests/test_helpers.py -v

# Run async tests only
pytest -m asyncio
```

---

## Coverage Goals by Priority

| Category | Current | Target | Timeline | Effort |
|----------|---------|--------|----------|--------|
| Helper functions | 0% | 90% | Week 1 | 3 hours |
| Tool execution | 0% | 70% | Week 2 | 5 hours |
| Error handling | 0% | 80% | Week 3 | 4 hours |
| Edge cases | 0% | 60% | Ongoing | 2 hours/week |
| **Overall** | **0%** | **75%** | **3 weeks** | **~14 hours** |

---

## Quick Wins (Start Here)

### 1. **Test `_resolve_interval()`** (30 min)
- Valid cases: "1d", "5m", "1h"
- Invalid case: "99m" raises ValueError
- Edge cases: "  1D  " (whitespace, uppercase)

### 2. **Test `_resolve_screener()`** (20 min)
- All aliases: "usa" → "america", "crypto" → "crypto"
- Fallback: Unknown screener returns as-is
- Case normalization

### 3. **Test `_format_summary()` with missing fields** (30 min)
- Mock Analysis with None fields
- Ensure output doesn't crash
- Verify JSON serializability

### 4. **Test `screen_market()` parameter clamp** (20 min)
- Verify limit=100 becomes limit=50
- Verify negative min_volume handled

---

## Preventing Future Gaps

1. **Test-Driven Development:** Write tests before adding new tools
2. **Code Review Gate:** Require test coverage for tool additions
3. **CI/CD Integration:** Block merges if coverage drops below 70%
4. **Documentation:** Keep test examples in ARCHITECTURE.md

---

## Next Steps

1. Set up testing infrastructure (pytest, fixtures)
2. Write unit tests for helper functions
3. Create mock fixtures for Analysis and Handler
4. Add integration tests for each tool
5. Add error scenario tests
6. Integrate coverage checks into CI/CD
