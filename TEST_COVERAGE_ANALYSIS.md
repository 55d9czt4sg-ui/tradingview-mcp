# Test Coverage Analysis — TradingView MCP Server

**Date:** 2026-09-12  
**Status:** Automated pytest coverage is now established, with core helper and tool-path coverage in place and the largest remaining gaps in the newer Notion sync modules.

---

## Executive Summary

The TradingView MCP Server now has an automated pytest suite covering helper behavior and mocked tool execution paths. The main remaining risk is uneven coverage: the new test suite protects the core MCP server flows, but newer modules and some exception paths still need dedicated tests.

- Silent regressions when dependencies update
- Edge-case failures in data transformation pipelines
- Incorrect error handling breaking AI assistant workflows
- Inability to safely refactor or extend functionality

This document summarizes the current baseline and the highest-value next steps to improve coverage further.

---

## Current State: Pytest Baseline In Place

### What Exists
- **Source code:** `src/tradingview_mcp/server.py` plus Notion sync modules under `src/tradingview_mcp/`
- **Test files:** `tests/test_helpers.py`, `tests/test_tools.py`, `tests/conftest.py`
- **Test framework configuration:** `pytest.ini`, pytest extras in `pyproject.toml`, coverage output
- **Execution command:** `python -m pytest`

### What's Missing
- Focused tests for `daily_sync.py`, `notion_sync.py`, and `setup_notion.py`
- Broader exception-path validation for integration failures
- CI/CD test gates
- Ongoing maintenance as new tools are added

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

### Phase 1: Expand Unit Tests
**Focus:** Helper functions, input validation, data transformation gaps

**Existing coverage to build on:**
- `tests/test_helpers.py` — Helper tests already present
- `tests/test_tools.py` — Mocked integration coverage already present
- `tests/conftest.py` — Shared fixtures already present

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

### Phase 2: Expand Integration Tests with Mocks
**Focus:** API interactions without hitting live APIs

**Priority additions:**
- Notion sync workflows
- Daily sync orchestration
- Breakout and financial screening edge cases

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

### Phase 3: Error Handling & Resilience
**Focus:** Network failures, malformed responses, timeout handling

**Recommended additions:**
- `tests/test_error_handling.py` — Cross-tool error scenarios

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
| Helper functions | Baseline coverage in place | 90% | Ongoing | 1-2 hours |
| Tool execution | Baseline coverage in place | 80% | Ongoing | 2-4 hours |
| Error handling | Partial | 80% | Next increment | 2-3 hours |
| Notion sync modules | Minimal | 70% | Next increment | 3-5 hours |
| **Overall** | **Core server paths covered** | **75%+** | **Incremental** | **~8-12 hours** |

---

## Quick Wins (Next)

### 1. **Add Notion sync module tests**
- Mock the Notion client for create/update flows
- Validate property mapping and payload formatting
- Cover failure reporting for missing configuration

### 2. **Add daily sync orchestration tests**
- Mock symbol iteration and analysis fetches
- Verify sync summary output
- Validate partial-failure handling

### 3. **Expand exception-path coverage**
- Network failures for symbol search and screeners
- Invalid or missing TradingView fields
- Notion API failures and retries

### 4. **Wire tests into CI**
- Run `python -m pytest` on pull requests
- Fail fast on regressions in tool output contracts

---

## Preventing Future Gaps

1. **Test-Driven Development:** Write tests before adding new tools
2. **Code Review Gate:** Require test coverage for tool additions
3. **CI/CD Integration:** Block merges if coverage drops below 70%
4. **Documentation:** Keep test examples in ARCHITECTURE.md

---

## Next Steps

1. Add focused tests for `notion_sync.py`, `daily_sync.py`, and `setup_notion.py`
2. Expand failure-path coverage for TradingView and Notion API errors
3. Add regression tests for future tool additions as they land
4. Integrate `python -m pytest` into CI/CD
