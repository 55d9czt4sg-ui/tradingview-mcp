# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**TradingView MCP Server** is a Model Context Protocol (MCP) server that exposes TradingView's technical analysis, market screening, and indicator data as tools for AI assistants (Claude, Perplexity, Cursor). It bridges the gap between conversational AI and financial market data.

- **Version:** 0.1.0 (Beta)
- **Python:** 3.10+
- **Package Manager:** uv (recommended) or pip
- **Entry Point:** `src/tradingview_mcp/server.py`
- **Main MCP Server:** FastMCP instance in `server.py`

## Development Commands

### Setup
```bash
# Install dependencies (requires uv)
uv sync

# Or with pip
pip install -e .
```

### Running
```bash
# Run the server (stdio transport)
uv run tradingview-mcp

# Or directly
uv run -m tradingview_mcp.server

# With pip
tradingview-mcp
```

### Testing & Linting
```bash
# No formal test suite yet. To manually test a tool:
uv run python
>>> import asyncio
>>> from tradingview_mcp.server import get_technical_analysis
>>> result = asyncio.run(get_technical_analysis("AAPL", "NASDAQ", "america", "1d"))
>>> print(result)

# Check syntax/imports
python -m py_compile src/tradingview_mcp/server.py

# Type checking (if mypy is added)
mypy src/tradingview_mcp/
```

### Publishing
```bash
# Build distribution (uv handles this automatically)
uv build
```

## Architecture

### Data Flow

```
AI Client (Claude, Perplexity, etc.)
    ↓ (JSON-RPC over stdio)
FastMCP Framework (Tool registration, request routing)
    ↓
Tool Implementations (@mcp.tool() functions)
    ↓
TradingView APIs (tradingview-ta, tradingview-screener, HTTP endpoints)
    ↓
Market Data
```

### Key Components

**1. FastMCP Server (`server.py` top-level)**
- Singleton `mcp = FastMCP("tradingview", instructions=...)` instance
- Handles tool registration, request parsing, stdio transport
- All tools are decorated with `@mcp.tool()` for auto-registration

**2. Tool Functions (async, in `server.py`)**
- `get_technical_analysis()` — Full BUY/SELL/NEUTRAL summary for one symbol + timeframe
- `get_multi_timeframe()` — Same symbol across multiple timeframes (confluence checks)
- `get_indicator_values()` — Raw numeric indicator data (RSI, MACD, BB, pivots, etc.)
- `search_symbol()` — Find symbols by name/ticker via TradingView HTTP API
- `screen_market()` — Filter/rank instruments by technical signals, volume, change %, etc.
- `get_price_data()` — Current OHLCV snapshot + support levels (pivots, VWAP, ATR)

**3. Helper Functions & Constants**
- `_resolve_interval(interval: str) -> str` — Convert "1d" → Interval.INTERVAL_1_DAY
- `_resolve_screener(screener: str) -> str` — Normalize market names (usa → america)
- `_build_handler()` — Construct TA_Handler with normalized inputs + 15s timeout
- `_format_summary()` & `_format_indicators()` — Extract & reshape Analysis object fields
- `INTERVAL_MAP`, `SCREENER_MAP` — Lookup tables for human-friendly input → API constants

**4. Data Sources**
- **tradingview-ta** — TA_Handler for single-symbol, single-timeframe technical analysis
- **tradingview-screener** — Query/Column API for filtering markets
- **TradingView HTTP API** — Symbol search endpoint at `symbol-search.tradingview.com`

### Key Design Patterns

1. **All tools are async** — Enables concurrent requests without blocking
2. **Error handling via strings** — Tools return error messages (not exceptions) so MCP client gets readable responses
3. **JSON output** — All results returned as `json.dumps(dict, indent=2)` strings
4. **Interval/Screener abstraction** — User passes "1d", "usa"; helpers normalize to TradingView constants
5. **Multi-timeframe via iteration** — `get_multi_timeframe()` loops and builds list of analyses, one per interval

## Key Conventions

### Tool Signatures
- **Parameters:** Always include `symbol`, `exchange`, optionally `screener` (default: "america")
- **Timeframes:** Use human-friendly strings ("1m", "5m", "1h", "1d", etc.) — never Interval constants
- **Return type:** Always `str` (JSON-serialized dict or error message)
- **Docstring:** One-line summary, then Args section describing all parameters — this is shown to AI clients

### Error Handling
```python
try:
    result = handler.get_analysis()
    return json.dumps(formatted_result, indent=2)
except Exception as e:
    return f"Error fetching analysis for {symbol}: {e}"
```
Never raise exceptions; always return error strings.

### Screener & Exchange Names
- **Screeners:** "america" (US stocks), "crypto", "forex", "cfd", "india", "japan", etc.
- **Exchanges:** "NASDAQ", "NYSE", "BINANCE", "COMEX", "CME" (match TradingView symbols exactly)
- **User flexibility:** `_resolve_screener()` maps user variations ("usa", "us" → "america")

### Timeframes Supported
- **Intraday:** 1m, 5m, 15m, 30m
- **Hourly:** 1h, 2h, 4h
- **Daily+:** 1d, 1w, 1M

Use `_resolve_interval()` to convert strings to Interval constants.

### Response Formats
**All tools return JSON. Common structure:**
```json
{
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "interval": "1d",
  "time": "2024-01-15 16:00:00",
  "summary": {"BUY": 7, "NEUTRAL": 3, "SELL": 0},
  "oscillators": {"RSI": 65.2, "MACD.macd": 0.45, ...},
  "moving_averages": {"EMA20": 180.5, "EMA50": 178.2, ...}
}
```

## Implementation Notes

### Adding a New Tool

1. **Define the tool function** in `server.py`:
   ```python
   @mcp.tool()
   async def new_tool(symbol: str, exchange: str, screener: str = "america") -> str:
       """One-line description visible to AI clients.
       
       Args:
           symbol: Ticker (e.g. AAPL, NQ1!)
           exchange: Exchange name (e.g. NASDAQ, CME)
           screener: Market — america, crypto, forex, etc. (default: america)
       """
       try:
           handler = _build_handler(symbol, exchange, screener, "1d")
           # ... do work ...
           return json.dumps(result, indent=2)
       except Exception as e:
           return f"Error: {e}"
   ```

2. **Docstring matters** — AI clients read it to understand how to call the tool. Be precise about parameters.

3. **Test locally:**
   ```bash
   uv run tradingview-mcp
   # Send JSON-RPC requests via stdin, or test in Python REPL
   ```

4. **Commit & push** to GitHub.

### Adding New Dependencies

1. Update `pyproject.toml` `dependencies` list
2. Run `uv sync` to regenerate lock file
3. Commit both `pyproject.toml` and `uv.lock`

Current dependencies:
- **mcp[cli]** >= 1.2.0 — FastMCP, MCP protocol
- **tradingview-ta** >= 3.3.0 — Technical analysis library
- **tradingview-screener** >= 2.5.0 — Market screener
- **httpx** >= 0.27.0 — Async HTTP client for symbol search

### Performance Considerations

- **No caching** — Every tool call fetches fresh data (can be slow for repeated queries)
- **15-second timeouts** — Set in `_build_handler()` to avoid hanging on slow API responses
- **Symbol search limits to 15 results** — Prevents oversized responses
- **Screener results capped at 50** — Query API limit; `limit` parameter enforces this

**Possible future optimizations:**
- Redis caching (5–60 second TTLs)
- Batch requests (combine multi-symbol queries)
- Parallel requests with `asyncio.gather()`

### Testing Approach

- No pytest suite yet (future: add `tests/` directory with fixtures)
- Manual testing: Import tool functions in Python REPL, call with `asyncio.run()`
- Integration testing: Start server with `uv run tradingview-mcp` and send JSON-RPC requests

Example:
```python
import asyncio
import json
from tradingview_mcp.server import get_technical_analysis

# Test a single symbol
result = asyncio.run(get_technical_analysis("AAPL", "NASDAQ", "america", "1d"))
data = json.loads(result)
print(f"Symbol: {data['symbol']}, Signals: {data['summary']}")
```

## Documentation Files

- **README.md** — Setup, quick-start, tool reference, troubleshooting
- **ARCHITECTURE.md** — Detailed design, data flow, MCP protocol overview, deployment
- **EXAMPLES.md** — Real-world usage workflows (stock analysis, crypto trading, screening)

When adding a feature:
1. Document the tool parameters in its docstring (for AI clients)
2. Add an example in EXAMPLES.md if it's a new workflow
3. Update ARCHITECTURE.md if the design changes

## Common Workflows

### Analyzing a Single Symbol
```bash
# User query: "What's the technical analysis for Tesla on the daily?"
# Tool chain:
# 1. get_technical_analysis("TSLA", "NASDAQ", "america", "1d")
# 2. Returns BUY/SELL/NEUTRAL + oscillators + MAs
```

### Multi-Timeframe Confluence Check
```bash
# User query: "Check Bitcoin on 5m, 15m, 1h, and 4h. Are they aligned?"
# Tool chain:
# 1. get_multi_timeframe("BTCUSDT", "BINANCE", "crypto", "5m,15m,1h,4h")
# 2. Returns list of analyses, one per timeframe
```

### Market Screening
```bash
# User query: "Find the top 20 crypto gainers right now."
# Tool chain:
# 1. screen_market(screener="crypto", sort_by="change", limit=20)
# 2. Returns DataFrame-like rows with price, volume, technicals
```

### Finding a Symbol
```bash
# User query: "What's the symbol for gold futures on TradingView?"
# Tool chain:
# 1. search_symbol("gold futures", type="futures")
# 2. Returns list of matching symbols with exchange, description
```

## Deployment Notes

- **CLI entry point** defined in `pyproject.toml`: `tradingview-mcp = "tradingview_mcp.server:main"`
- **Stdio transport** — Server runs on stdin/stdout for MCP clients (Claude Desktop, Perplexity, Cursor)
- **Python 3.10+** — Required; no asyncio backports needed
- **No external services** — All data from public TradingView APIs; no authentication required

## Useful References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlotz/fastmcp)
- [TradingView TA Library](https://github.com/deathlyface/tradingview-ta)
- [TradingView Screener](https://github.com/shayneobrien/tradingview-screener)
