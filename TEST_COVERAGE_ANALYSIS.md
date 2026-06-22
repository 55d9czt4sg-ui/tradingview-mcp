# Test Coverage Analysis: TradingView MCP Server

## Executive Summary

The TradingView MCP Server (`src/tradingview_mcp/server.py`) currently has **zero test coverage**. This document analyzes the codebase, identifies critical untested components, and proposes a testing strategy to improve reliability and maintainability.

**Current State:**
- No test files exist
- No testing framework configured (pytest, unittest, etc.)
- No mocking setup for external API dependencies
- No CI/CD testing pipeline

**Risk Level:** High — critical code paths directly interact with external APIs (TradingView, symbol-search) with only error string returns as failure handling.

---

## Project Overview

The server exposes 6 MCP tools for technical analysis and market screening:

1. **`get_technical_analysis`** — TA summary (BUY/SELL/NEUTRAL)
2. **`get_multi_timeframe`** — Multi-timeframe analysis with error aggregation
3. **`get_indicator_values`** — Raw indicator extraction with optional filtering
4. **`search_symbol`** — TradingView symbol search via HTTP API
5. **`screen_market`** — Market screening with conditional filters
6. **`get_price_data`** — OHLCV snapshot with key technical levels

**Key Dependencies:**
- `tradingview-ta` — TA_Handler for live technical analysis
- `tradingview-screener` — Query builder for market screening
- `httpx` — Async HTTP client for symbol search
- `mcp` (FastMCP) — Protocol server framework

---

## Untested Components & Coverage Gaps

### 1. **Helper Functions (Core Logic)** — [0% coverage]

#### `_resolve_interval(interval: str) -> str`
**Purpose:** Maps human-friendly interval strings to TradingView Interval constants.

**Untested Paths:**
- ✗ Valid intervals: "1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1w", "1M"
- ✗ Case-insensitivity: "1H", "1D", "1m" should all work
- ✗ Whitespace stripping: " 1d " should resolve correctly
- ✗ Invalid intervals: Should raise ValueError with helpful message
- ✗ Empty string: Should raise ValueError
- ✗ None input: Behavior undefined

**Risk:** A typo in INTERVAL_MAP or a missed valid interval breaks the tool silently (error is returned as string, not raised).

---

#### `_resolve_screener(screener: str) -> str`
**Purpose:** Resolves market names (usa → america, etc.) with fallback to original.

**Untested Paths:**
- ✗ Mapped values: "usa" → "america", "us" → "america", "crypto" → "crypto"
- ✗ Case-insensitivity: "USA", "Crypto" should work
- ✗ Unmapped values: Should return the input as-is ("forex" → "forex")
- ✗ Whitespace handling: " america " should work
- ✗ Edge cases: empty string, None, special characters

**Risk:** Silently passes invalid screener names to TA_Handler, causing opaque downstream errors.

---

#### `_build_handler(symbol, exchange, screener, interval) -> TA_Handler`
**Purpose:** Constructs a TA_Handler with normalized inputs.

**Untested Paths:**
- ✗ Uppercase conversion: symbol="aapl", exchange="nasdaq" → TA_Handler receives "AAPL", "NASDAQ"
- ✗ Integration with resolution functions:
  - Invalid interval passed to _resolve_interval
  - Invalid screener passed to _resolve_screener
- ✗ Timeout handling: Is 15s appropriate? What if it times out?
- ✗ Exception propagation: Does TA_Handler raise or return error?

**Risk:** Inputs are normalized but error handling is unclear. Integration tests needed with mocked TA_Handler.

---

#### `_format_summary(analysis: Any) -> dict`
**Purpose:** Extracts safe fields from TA Analysis object.

**Untested Paths:**
- ✗ Happy path: Valid analysis object returns all 7 fields
- ✗ Missing attributes: If analysis.summary is None, .oscillators missing, etc.
- ✗ Time field conversion: `str(analysis.time)` — does it always serialize correctly?
- ✗ None values: Are None values preserved in JSON serialization?
- ✗ Attribute errors: Raises or returns partial dict?

**Risk:** If analysis object structure changes or is malformed, this silently fails or crashes the server.

---

#### `_format_indicators(analysis: Any, keys: list[str] | None = None) -> dict`
**Purpose:** Extracts raw indicator values, optionally filtered.

**Untested Paths:**
- ✗ No keys provided: Returns all indicators
- ✗ Key filtering: Only requested keys are included (e.g., ["RSI", "MACD.macd"])
- ✗ Missing key in indicators: `.get(k)` returns None gracefully
- ✗ Empty keys list: Should return empty indicators dict
- ✗ Non-existent keys: Are they included as None or silently omitted?
- ✗ Time field conversion: Same as `_format_summary`

**Risk:** Silent truncation or None values in output could mislead users.

---

### 2. **MCP Tools (Public API)** — [0% coverage]

#### `get_technical_analysis(symbol, exchange, screener="america", interval="1d")`

**Untested Paths:**
- ✗ Happy path: Valid symbol on valid exchange returns formatted analysis
- ✗ Invalid symbol/exchange: Error handling (returns error string)
- ✗ Network timeout: What happens if TA_Handler times out?
- ✗ API unavailability: Does exception propagate or get caught?
- ✗ Parameter validation: Missing symbol, exchange?
- ✗ Default parameters: "america" screener, "1d" interval applied correctly?
- ✗ Special characters in symbol: "NQ1!", "GC1!" handled correctly?

**Risk:** All errors are returned as strings, making it impossible to distinguish tool success from API failure in calling code.

---

#### `get_multi_timeframe(symbol, exchange, screener="america", intervals="5m,15m,1h,4h,1d")`

**Untested Paths:**
- ✗ All intervals succeed: Returns list of 5 analysis objects
- ✗ One interval fails: Error dict is inserted in results, others continue
- ✗ Empty intervals string: What happens?
- ✗ Invalid interval mixed with valid: Aggregates errors correctly?
- ✗ Comma parsing: "1d, 1w" (space after comma) handled correctly?
- ✗ Duplicate intervals: "1d,1d" — does it call TA_Handler twice?
- ✗ Interval count: Performance impact of requesting many intervals?

**Risk:** Partial failures silently returned in array; client must parse to detect errors. No clear success/failure contract.

---

#### `search_symbol(query: str, type: str = "")`

**Untested Paths:**
- ✗ Happy path: Valid query returns formatted symbols (up to 15)
- ✗ Query with spaces: "gold futures" handled correctly by API?
- ✗ Empty query: API behavior? Empty result or error?
- ✗ Type filtering: type="crypto" only returns crypto symbols?
- ✗ HTML stripping: `<b>gold</b>` stripped to "gold" by regex?
- ✗ Missing fields: If s.get("symbol") missing, does it skip or fail?
- ✗ Network timeout/DNS failure: Exception handling?
- ✗ API rate limiting: 429 response handling?
- ✗ Invalid JSON response: resp.json() raises ValueError?

**Risk:** External API dependency with only basic error handling. Regex for HTML stripping is fragile.

---

#### `screen_market(screener="america", sort_by="change", sort_order="desc", limit=20, ...filters...)`

**Untested Paths:**
- ✗ Happy path: Valid screener and sort returns top 20 results
- ✗ Limit enforcement: limit=100 capped to 50?
- ✗ Sort order: "asc" vs "desc" correctly applied?
- ✗ Filter combinations:
  - min_volume filter applied
  - min_change_pct filter applied (e.g., 5.0)
  - max_change_pct filter applied (e.g., -5.0)
  - All three together (interaction testing)
- ✗ None filters: Skipped correctly (not applied as 0)?
- ✗ NaN handling: str(v) == "nan" conversion works?
- ✗ market_type mapping: "stock" → "america", "crypto" → "crypto", etc.
- ✗ Invalid sort_by field: Does Query accept arbitrary fields?
- ✗ Empty result set: Returns {"total_matching": 0, "results": []}?
- ✗ ImportError: tradingview-screener not installed (returns error string)
- ✗ Query API changes: Column API, Query API methods still work?

**Risk:** Complex query building with many conditional branches; no integration tests verify filter application.

---

#### `get_price_data(symbol, exchange, screener="america", interval="5m")`

**Untested Paths:**
- ✗ Happy path: Returns all 18 price/level keys
- ✗ Missing keys in analysis.indicators: Returns None for missing keys
- ✗ Time field conversion: Works correctly?
- ✗ Invalid symbol: Error handling?
- ✗ Interval affects OHLCV: 5m vs 1d data differs?

**Risk:** No verification that all 18 requested keys are available or meaningful.

---

### 3. **External API Integration** — [0% coverage]

#### TradingView Technical Analysis API (tradingview-ta)
- ✗ TA_Handler initialization
- ✗ .get_analysis() call and response structure
- ✗ Network failures and timeout behavior
- ✗ API rate limiting (is there one?)
- ✗ Malformed responses

#### TradingView Symbol Search API (httpx)
- ✗ Endpoint reachability and response format
- ✗ Query parameter encoding
- ✗ Response error codes (4xx, 5xx)
- ✗ HTML entity encoding in descriptions

#### TradingView Screener API (tradingview-screener)
- ✗ Query builder API changes
- ✗ Column name validation
- ✗ Screener market availability
- ✗ Large result set pagination (not implemented)

---

### 4. **Error Handling & Edge Cases** — [0% coverage]

**Current Error Handling Pattern:**
```python
try:
    # logic
    return json.dumps(result, indent=2)
except Exception as e:
    return f"Error fetching X: {e}"
```

**Problems:**
- ✗ All errors returned as strings, not JSON
- ✗ No structured error response (HTTP status, error code, details)
- ✗ Exception details exposed to client (security risk)
- ✗ No logging (can't debug production issues)
- ✗ No retry logic for transient failures
- ✗ No timeout handling (could hang indefinitely)

**Untested Edge Cases:**
- ✗ Very large result sets (screen_market with 50 symbols)
- ✗ Unicode and special characters in names
- ✗ Very long query strings (symbol search)
- ✗ Concurrent tool calls (are they thread-safe?)
- ✗ JSON serialization failures (datetime objects, custom types)

---

## Proposed Testing Strategy

### Phase 1: Unit Tests (Weeks 1-2)

**Scope:** Helper functions, no external dependencies

**Tools:** pytest + pytest-asyncio for async tools

**Setup:**
```bash
pip install pytest pytest-asyncio pytest-cov
pip install -e ".[dev]"  # Add dev dependencies to pyproject.toml
```

**Files to Create:**
- `tests/test_helpers.py` — Test `_resolve_interval()`, `_resolve_screener()`, `_build_handler()`, `_format_summary()`, `_format_indicators()`
- `tests/conftest.py` — Shared fixtures (mock Analysis objects, mock TA_Handler)

**Coverage Target:** 80%+ for helper functions

**Estimated Tests:** ~50-60 test cases

---

### Phase 2: Unit Tests with Mocking (Weeks 2-3)

**Scope:** MCP tools with mocked external dependencies

**Tools:** pytest + pytest-mock (or unittest.mock)

**Mock Targets:**
- `tradingview_ta.TA_Handler` — Mock .get_analysis() responses
- `httpx.AsyncClient` — Mock symbol search API responses
- `tradingview_screener.Query` — Mock query building and .get_scanner_data()

**Files to Create:**
- `tests/test_tools.py` — Test all 6 MCP tools
- `tests/mocks.py` — Mock responses and fixtures

**Coverage Target:** 80%+ for all tools

**Estimated Tests:** ~80-100 test cases covering:
- Happy paths
- Invalid inputs
- API failures
- Error handling
- Edge cases (empty results, missing fields, etc.)

**Example Structure:**
```python
@pytest.mark.asyncio
async def test_get_technical_analysis_success(mock_ta_handler):
    mock_ta_handler.return_value.get_analysis.return_value = mock_analysis
    result = await get_technical_analysis("AAPL", "NASDAQ")
    assert "BUY" in result or "SELL" in result  # JSON string
    data = json.loads(result)
    assert data["symbol"] == "AAPL"

@pytest.mark.asyncio
async def test_get_technical_analysis_invalid_interval():
    result = await get_technical_analysis("AAPL", "NASDAQ", interval="invalid")
    assert "Error" in result  # Current error handling
```

---

### Phase 3: Integration Tests (Weeks 3-4)

**Scope:** Full tool chain with real or test API responses

**Tools:** pytest + responses (HTTP mocking) or VCR.py (request recording)

**Approach:**
1. **Option A: Live Testing** — Use real TradingView APIs (with network isolation in CI)
2. **Option B: Recorded Responses** — Use VCR.py to record real responses, replay in tests
3. **Option C: Mock Servers** — Spin up mock HTTP servers for predictable responses

**Files to Create:**
- `tests/test_integration.py` — End-to-end tool workflows
- `tests/cassettes/` — Recorded API responses (if using VCR.py)

**Coverage Target:** Critical user workflows

**Estimated Tests:** ~20-30 integration tests covering:
- Multi-step workflows (search symbol → get technical analysis)
- Realistic data from real APIs
- Network error scenarios
- Rate limiting

---

### Phase 4: Configuration & CI/CD (Week 4)

**Setup pytest in pyproject.toml:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "responses>=0.22.0",  # Or vcrpy
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=src/tradingview_mcp --cov-report=html --cov-report=term-missing"
```

**CI/CD Pipeline (.github/workflows/test.yml):**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: "3.10" }
      - run: pip install -e ".[dev]"
      - run: pytest --cov=src/tradingview_mcp
      - uses: codecov/codecov-action@v3
```

---

## Priority Test Areas (High → Low)

### 🔴 **Critical (Implement First)**

1. **`_resolve_interval()` and `_resolve_screener()`** — Core path, used by all tools
2. **`get_technical_analysis()` & `get_multi_timeframe()`** — Most-used tools
3. **Error handling & exception paths** — Currently all return strings; need validation

### 🟡 **Important (Implement Next)**

4. **`search_symbol()` HTTP integration** — Network-dependent
5. **`screen_market()` filter combinations** — Complex query building
6. **JSON serialization edge cases** — Unicode, NaN, None values

### 🟢 **Nice-to-Have (Implement Later)**

7. **Performance tests** — Large result sets, concurrent calls
8. **Timeout/retry logic** — If added to error handling
9. **Documentation coverage** — Docstring examples in tests

---

## Estimated Effort

| Phase | Task | Effort | Timeline |
|-------|------|--------|----------|
| 1 | Unit tests (helpers) | 16h | Week 1-2 |
| 2 | Unit tests (tools + mocking) | 24h | Week 2-3 |
| 3 | Integration tests | 12h | Week 3-4 |
| 4 | CI/CD setup | 4h | Week 4 |
| **Total** | **Full test suite** | **56h** | **4 weeks** |

**Per-Test Estimate:** ~0.5-1 hour per test (write + debug + documentation)

---

## Immediate Next Steps

1. **Setup:** Create `tests/` directory, install pytest
2. **Quick Win:** Test `_resolve_interval()` — ~10 test cases, 1-2 hours
3. **Mock Fixtures:** Create reusable mock objects for Analysis, TA_Handler
4. **Core Tools:** Test `get_technical_analysis()` — foundational for all other TA tools
5. **Iterate:** 5-10 tests per day, review coverage gaps

---

## Code Quality & Testing Best Practices

### Recommendations

1. **Separate Error Types** — Instead of catching all Exceptions, catch specific types:
   ```python
   except httpx.TimeoutException:
       return "Request timeout"
   except httpx.HTTPError as e:
       return f"API error: {e.status_code}"
   except ValueError as e:
       return f"Invalid input: {e}"
   ```

2. **Structured Error Response** — Return JSON errors consistently:
   ```python
   return json.dumps({
       "error": "timeout",
       "message": "Request took too long",
       "symbol": symbol
   })
   ```

3. **Add Logging** — Log API calls, errors, and performance:
   ```python
   logger.debug(f"Fetching {symbol} on {interval}")
   logger.error(f"API error: {e}", exc_info=True)
   ```

4. **Input Validation** — Validate before calling external APIs:
   ```python
   if not symbol or not exchange:
       raise ValueError("symbol and exchange are required")
   ```

5. **Type Hints** — Already good; add return type to async functions:
   ```python
   async def get_technical_analysis(...) -> str:
   ```

6. **Async Timeouts** — Use asyncio.timeout for external calls:
   ```python
   async with asyncio.timeout(15):
       analysis = handler.get_analysis()
   ```

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| External API changes | Medium | High | Integration tests, version pinning, CI monitoring |
| Network timeouts | High | Medium | Implement retry logic, configurable timeouts, tests |
| Large result sets | Low | Medium | Add pagination, limit results, performance tests |
| Malformed API responses | Medium | High | Schema validation, field existence checks, error logging |
| Regex fragility (HTML stripping) | Medium | Low | Use HTML parser instead, comprehensive tests |

---

## Success Criteria

✅ **80%+ line coverage** across all modules  
✅ **All helper functions** have unit tests with edge cases  
✅ **All 6 MCP tools** have mocked unit tests  
✅ **Error paths** tested (invalid inputs, API failures)  
✅ **CI/CD pipeline** runs tests on every push  
✅ **No silent failures** — errors properly logged and returned  
✅ **Documentation** — README with test instructions  

---

## Conclusion

The TradingView MCP Server has **significant untested areas** with **zero current coverage**. The codebase is relatively small (430 lines), making it an ideal candidate for **rapid test development**. Implementing this testing strategy will:

- **Reduce bugs** in production by catching regressions early
- **Enable refactoring** with confidence
- **Improve maintainability** by documenting expected behavior
- **Build trust** in the API's reliability

**Recommendation:** Start with Phase 1 (helper functions) for a quick foundation, then expand to tools with mocking. Target 80%+ coverage within 4 weeks.
