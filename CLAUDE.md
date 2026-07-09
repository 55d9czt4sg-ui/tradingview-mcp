# CLAUDE.md — TradingView MCP Server

**Project:** TradingView MCP Server  
**Version:** 0.1.0  
**Purpose:** Model Context Protocol (MCP) server exposing TradingView technical analysis, market screening, and indicator data to AI assistants.  
**Language:** Python 3.10+  
**Package Manager:** uv (or pip)

---

## Project Overview

This is a lightweight MCP bridge that gives AI assistants (Claude, Perplexity, etc.) access to real-time TradingView market data and technical analysis. It implements the [Model Context Protocol](https://modelcontextprotocol.io/) to expose financial data as tools that AI clients can call via JSON-RPC over stdio.

**Key Features:**
- 7 primary tools for technical analysis, screening, symbol search, and SMC analysis
- Multi-timeframe analysis (5m to 1M)
- 40+ technical indicators (RSI, MACD, Bollinger Bands, EMAs, etc.)
- Global market coverage (stocks, crypto, forex, futures, bonds, CFDs)
- Zero-configuration deployment
- Async-first design for concurrent requests
- Comprehensive error handling

**Target Audiences:**
- AI assistant users (Claude Desktop, Perplexity, Cursor, VS Code)
- Financial analysts integrating TradingView data into AI workflows
- Developers building MCP servers for financial markets

---

## Directory Structure

```
tradingview-mcp/
├── src/tradingview_mcp/
│   ├── __init__.py              # Package metadata (version)
│   └── server.py                # MCP server + 7 tool implementations (564 lines)
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures (mock handlers, analysis objects)
│   ├── test_tools.py            # 40+ tests for all tools (integration tests)
│   ├── test_helpers.py          # Tests for helper functions (interval, screener resolution)
│   └── README.md                # Testing guide
├── .gitignore                   # Standard Python .gitignore
├── LICENSE                      # MIT License
├── README.md                    # User-facing documentation (installation, quick start)
├── ARCHITECTURE.md              # Design principles, data flow, extension guide
├── EXAMPLES.md                  # Detailed tool usage examples
├── TEST_COVERAGE_ANALYSIS.md    # Test coverage report (85% line coverage, 42/42 passing)
├── pyproject.toml               # Project metadata, dependencies, test config
├── pytest.ini                   # Pytest configuration
└── uv.lock                      # Locked dependency versions
```

---

## Core Module: `src/tradingview_mcp/server.py`

**Responsibilities:**
- Instantiate FastMCP server and register tools
- Implement all 7 MCP tools as async functions
- Handle TradingView API calls and data transformations
- Error handling and JSON serialization

**Key Components:**

### 1. **FastMCP Instance**
```python
mcp = FastMCP(
    "tradingview",
    instructions="TradingView technical analysis, screening, and market data.",
)
```
- Handles tool registration, JSON-RPC routing, stdio transport
- Decorated functions (`@mcp.tool()`) become callable tools

### 2. **Helper Maps and Functions**

**INTERVAL_MAP** — Maps human-friendly timeframe strings to TradingView Interval constants:
- `"1m"` → `Interval.INTERVAL_1_MINUTE`
- `"5m"` → `Interval.INTERVAL_5_MINUTES`
- Full coverage: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1w, 1M

**SCREENER_MAP** — Maps market aliases to TradingView screener names:
- `"usa"` / `"us"` → `"america"`
- `"crypto"`, `"forex"`, `"cfd"`, regional markets (`"india"`, `"japan"`, etc.)

**Helper Functions:**
- `_resolve_interval(interval: str) -> str` — Validates and resolves interval strings
- `_resolve_screener(screener: str) -> str` — Resolves market screener names
- `_build_handler(symbol, exchange, screener, interval) -> TA_Handler` — Constructs TradingView handler
- `_format_summary(analysis) -> dict` — Extracts summary, oscillators, moving averages from analysis
- `_format_indicators(analysis, keys) -> dict` — Filters and returns raw indicator values

### 3. **The Seven Tools**

| Tool | Purpose | Returns |
|------|---------|---------|
| `get_technical_analysis` | Single symbol, single timeframe | BUY/SELL/NEUTRAL + oscillator/MA signals |
| `get_multi_timeframe` | Same symbol across multiple timeframes | Array of summary objects per timeframe |
| `get_indicator_values` | Raw numeric indicator data | 40+ indicators (RSI, MACD, BB, EMAs, pivots, etc.) |
| `search_symbol` | Find symbols by name/ticker | Symbol, exchange, type, description (up to 15 results) |
| `screen_market` | Filter and rank instruments | Ranked list with technical signals, volume, change % |
| `get_price_data` | OHLCV snapshot + key levels | Open, high, low, close, volume, VWAP, pivots, BB, ATR |
| `analyze_smc` | Smart Money Concepts analysis | Support/resistance, order blocks, trend, RSI state |

**Tool Pattern:**
```python
@mcp.tool()
async def tool_name(param1: str, param2: str = "default") -> str:
    """Brief description for AI clients."""
    try:
        handler = _build_handler(...)
        analysis = handler.get_analysis()
        # Format and return JSON
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"
```

All tools:
- Are **async** to support concurrent requests
- Return **strings** (JSON-serialized)
- Catch exceptions and return error messages (not exceptions)
- Accept human-friendly parameter names and resolve them internally

---

## Dependencies & Integrations

**Core Dependencies** (see `pyproject.toml`):
- **mcp[cli]** ≥1.2.0 — FastMCP framework (tool registration, JSON-RPC, stdio)
- **tradingview-ta** ≥3.3.0 — Technical analysis (TA_Handler, Interval, indicators)
- **tradingview-screener** ≥2.5.0 — Market screener (Query, Column, filtering)
- **httpx** ≥0.27.0 — Async HTTP client (symbol search API)

**Dev/Test Dependencies:**
- pytest, pytest-asyncio, pytest-cov, pytest-mock
- httpx[testing], pandas

**External APIs:**
- TradingView TA library (C++ backend via Python wrapper)
- TradingView screener API
- TradingView symbol search API (https://symbol-search.tradingview.com/symbol_search/v3/)

---

## Development Workflow

### 1. **Setup & Installation**

**Using uv (recommended):**
```bash
git clone https://github.com/55d9czt4sg-ui/tradingview-mcp.git
cd tradingview-mcp
uv sync              # Install dependencies and dev tools
```

**Using pip:**
```bash
pip install -e .
```

### 2. **Running the Server Locally**

```bash
# Using uv
uv run tradingview-mcp

# Or directly
uv run -m tradingview_mcp.server

# Or with pip
tradingview-mcp
```

The server will start on stdio transport. Press Ctrl+C to stop.

### 3. **Adding a New Tool**

**Step-by-step:**

1. **Write the tool function** in `server.py`:
   ```python
   @mcp.tool()
   async def new_tool(symbol: str, param2: str = "default") -> str:
       """One-line description for AI clients.
       
       Args:
           symbol: Description
           param2: Description
       """
       try:
           result = do_something(symbol, param2)
           return json.dumps(result, indent=2)
       except Exception as e:
           return f"Error: {e}"
   ```

2. **Document the tool:**
   - Add docstring with parameter descriptions
   - Update ARCHITECTURE.md with data flow
   - Update README.md with examples

3. **Write tests** in `tests/test_tools.py`:
   ```python
   @pytest.mark.asyncio
   async def test_new_tool_success(self, mock_handler_class):
       """Test successful invocation."""
       # Mock, invoke, assert
   ```

4. **Test locally:**
   ```bash
   uv run pytest tests/test_tools.py::TestNewTool -v
   ```

5. **Commit and push:**
   ```bash
   git add src/tradingview_mcp/server.py tests/test_tools.py ...
   git commit -m "Add new_tool — description"
   git push origin feature-branch
   ```

### 4. **Code Conventions**

**Python Style:**
- Use type hints on all function signatures
- Docstrings for public functions
- Error handling: catch exceptions, return error strings
- Async-first: all tools are `async def`
- JSON serialization: use `json.dumps()` with `indent=2`

**Naming:**
- Private helpers: `_resolve_interval()`, `_format_summary()`, `_build_handler()`
- Tools: snake_case, start with verb (`get_`, `search_`, `screen_`, `analyze_`)
- Constants: SCREAMING_SNAKE_CASE (INTERVAL_MAP, SCREENER_MAP)

**Logging:**
- Use `logging` module for debug/info messages
- Errors returned as strings to AI client (not logged exceptions)

---

## Testing & Validation

### 1. **Running Tests**

```bash
# Run all tests
uv run pytest

# Run specific test class
uv run pytest tests/test_tools.py::TestGetTechnicalAnalysis -v

# Run with coverage
uv run pytest --cov=tradingview_mcp --cov-report=html

# Run only helpers
uv run pytest tests/test_helpers.py -v
```

**Current Coverage:** 85% line coverage, 42/42 tests passing  
(See `TEST_COVERAGE_ANALYSIS.md` for full report)

### 2. **Test Structure**

**Fixtures** (in `conftest.py`):
- `mock_analysis` — Mock TA_Handler Analysis object
- `mock_handler_class` — Mocked TA_Handler class
- `search_response` — Mock symbol search API response

**Test Files:**
- `test_tools.py` — Integration tests for all 7 tools (mocked external APIs)
- `test_helpers.py` — Unit tests for `_resolve_interval()`, `_resolve_screener()`, etc.

**Mocking Strategy:**
- Mock `TA_Handler` class (prevents real API calls)
- Mock `httpx.AsyncClient` for symbol search
- Mock `tradingview_screener.Query` for market screening

### 3. **Before Committing**

1. Run full test suite: `uv run pytest`
2. Check coverage: `uv run pytest --cov=tradingview_mcp`
3. Ensure 85%+ coverage maintained
4. All tests should pass

---

## Common Tasks & Workflows

### **Debug a Tool Failure**

1. Check the error message returned to the user
2. Verify the symbol/exchange are correct and exist on TradingView
3. Add a test case with the failing params to reproduce
4. Debug with mock or live data
5. Update ARCHITECTURE.md if behavior changes

### **Add a New Indicator to `get_indicator_values`**

1. Verify the indicator key exists in TA_Handler (e.g., `"RSI"`, `"MACD.macd"`)
2. Add to the default `indicators` parameter in the tool docstring
3. Update ARCHITECTURE.md with the new key
4. Add a test case
5. Commit

### **Optimize Performance**

Current limitations:
- No caching (every call fetches fresh data)
- Single-symbol queries only

Possible improvements:
- Add Redis caching for 5–60 second TTL
- Batch multi-symbol queries into one API call
- Use `asyncio.gather()` for parallel requests

### **Deploy to Production**

1. Ensure all tests pass locally
2. Push to GitHub
3. Create a PR and get review
4. Merge to main
5. Install via uv: `uv tool run --from git+https://github.com/55d9czt4sg-ui/tradingview-mcp.git tradingview-mcp`
6. Or point MCP client to local installation

---

## Git Workflow

**Current Branch:** `claude/claude-md-docs-3oin3v`  
**Main Branch:** `main`

**Branching:**
- Feature branches: `feature/tool-name` or `claude/<description>`
- All PRs must pass tests before merge

**Commit Message Style:**
```
Add/Fix/Update <component> — brief description

Optional longer explanation of the why and design.
```

**Recent Commits:**
- Add SMC (Smart Money Concepts) analysis tool
- Fix test failures, achieve 85% coverage (42/42 passing)
- Add test coverage files to .gitignore

---

## File-Specific Notes

### `server.py` (564 lines)

- **Lines 1–40:** Module docstring, imports, logging setup, FastMCP instantiation
- **Lines 42–92:** Constants (INTERVAL_MAP, SCREENER_MAP) and helper functions
- **Lines 94–134:** Formatter functions (_format_summary, _format_indicators)
- **Lines 140–416:** 6 main tools (get_technical_analysis, get_multi_timeframe, get_indicator_values, search_symbol, screen_market, get_price_data)
- **Lines 419–549:** SMC analysis tool (analyze_smc)
- **Lines 556–563:** Entrypoint (main function)

### `conftest.py` (78 lines)

- `mock_analysis` fixture — Realistic mock data for tests
- `mock_handler_class` fixture — Monkeypatches TA_Handler
- `search_response` fixture — Sample symbol search results

### `test_tools.py` (350+ lines)

- `TestGetTechnicalAnalysis` — 3 tests (success, custom params, exception handling)
- `TestGetMultiTimeframe` — 2 tests (multiple timeframes, error handling)
- `TestGetIndicatorValues` — 2 tests (success, custom indicators)
- `TestSearchSymbol` — 2 tests (success, HTML stripping, error handling)
- `TestScreenMarket` — 2 tests (success, filtering)
- `TestGetPriceData` — 2 tests (success, error handling)
- `TestAnalyzeSMC` — 3 tests (full analysis, insufficient data, error handling)

### `test_helpers.py` (150+ lines)

- `test_resolve_interval()` — Valid/invalid intervals, aliases
- `test_resolve_screener()` — Valid/invalid screeners, aliases
- `test_build_handler()` — Correct TA_Handler instantiation

---

## Architecture & Design Principles

### **Why Async?**

All tools are `async def` to:
- Support concurrent requests from MCP clients
- Allow long-running API calls without blocking other tools
- Enable better scalability under load

### **Error Handling Strategy**

Tools catch exceptions and return error strings (not exceptions) to ensure the MCP client receives a readable response instead of a protocol error:

```python
try:
    result = handler.get_analysis()
    return json.dumps(result)
except Exception as e:
    return f"Error: {e}"  # ← Returned as string, not exception
```

### **JSON Serialization**

All tool results must be JSON strings for MCP compliance:

```python
return json.dumps(result, indent=2)  # Always indent for readability
```

### **Default Parameters**

Tools use sensible defaults to reduce friction:
- `screener="america"` — US stocks by default
- `interval="1d"` — Daily timeframe
- `limit=20` — 20 results from screener

---

## Useful Commands

```bash
# Install dependencies
uv sync

# Run server locally
uv run tradingview-mcp

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=tradingview_mcp

# Format code (if available)
uv run black src tests

# Check code style (if available)
uv run flake8 src tests

# Build the package
uv build

# Install locally for testing
uv pip install -e .
```

---

## Common Issues & Troubleshooting

### **"ModuleNotFoundError: No module named 'tradingview_ta'"**

→ Run `uv sync` to install dependencies

### **Tool Returns "Timeout" or Symbol Not Found**

→ Verify the symbol exists on TradingView directly  
→ Confirm correct exchange (NASDAQ for US stocks, BINANCE for crypto)  
→ Try with a different screener (e.g., `america` vs `cfd`)

### **Test Mocking Not Working**

→ Verify `monkeypatch.setattr(server, "TA_Handler", mock_handler_class)` in fixture  
→ Check mock call_args: `assert handler_class.called`  
→ Use `AsyncMock` for async functions if needed

### **JSON Serialization Error**

→ Use `default=str` in `json.dumps()` for non-serializable types  
→ Convert pandas Series/DataFrames to dict/list first

---

## Extending the Server

### **Adding a New Data Source (Beyond TradingView)**

1. Add dependency to `pyproject.toml`
2. Create a new helper function to wrap the library
3. Implement new tools using the helper
4. Write tests (mock the external API)
5. Document in ARCHITECTURE.md

### **Performance Optimization Ideas**

1. **Caching:** Store recent queries with timestamps (in-memory or Redis)
2. **Batch Operations:** Combine multi-symbol queries into one request
3. **Async Concurrency:** Use `asyncio.gather()` for parallel processing
4. **Lazy Loading:** Only fetch data when explicitly requested

### **Future Tools to Consider**

1. `analyze_sector` — Compare symbols within a sector
2. `rank_symbol_setups` — Rank multiple symbols by technical score
3. `calculate_correlation` — Compute correlation between symbols
4. `get_option_chain` — Options data (if TradingView exposes it)
5. `monitor_alerts` — Real-time alert tracking (requires WebSocket)

---

## Resources & References

**MCP Documentation:**
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlotz/fastmcp)

**TradingView Libraries:**
- [tradingview-ta Documentation](https://github.com/deathlyface/tradingview-ta)
- [tradingview-screener GitHub](https://github.com/shayneobrien/tradingview-screener)

**Related Docs in This Repo:**
- `README.md` — User-facing setup and usage
- `ARCHITECTURE.md` — Design, data flow, extension guide
- `EXAMPLES.md` — Detailed tool examples and output
- `TEST_COVERAGE_ANALYSIS.md` — Test coverage report

---

## Summary for AI Assistants

**When working on this codebase:**

1. **All changes go to `server.py`** — This is the single source of truth for tools
2. **All tools are async** — Use `async def` and `await` patterns
3. **Always return JSON strings** — Use `json.dumps()`, not Python dicts
4. **Catch exceptions, don't raise them** — Return error strings to the user
5. **Write tests first** — Before committing, ensure `uv run pytest` passes
6. **Use human-friendly parameters** — Resolve user inputs with helper functions
7. **Keep tools focused** — One purpose per tool (get_*, search_*, screen_*, analyze_*)
8. **Document docstrings** — AI clients read these to understand tool usage

**Test before pushing:**
```bash
uv run pytest && uv run pytest --cov=tradingview_mcp
```

**Deployment is automatic via GitHub** — Push to a branch, create a PR, and merge after review.

---

**Last Updated:** 2026-06-26  
**Maintained By:** Claude Code AI Assistant
