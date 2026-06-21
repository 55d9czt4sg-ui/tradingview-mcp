# TradingView MCP Server — Developer Guide

## Project Overview

**TradingView MCP Server** is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes TradingView's technical analysis, market screening, and real-time indicator data as tools for AI assistants (Claude, Perplexity, Cursor, etc.).

**Key traits:**
- **Beta status** (v0.1.0)
- **Python 3.10+** required
- **FastMCP** for the MCP server framework
- **No backend dependencies** — stateless, calls TradingView APIs directly
- **MIT licensed**

---

## Repository Structure

```
tradingview-mcp/
├── src/tradingview_mcp/
│   ├── __init__.py              # Package metadata (version, docstring)
│   └── server.py                # Main MCP server and all tool definitions
├── pyproject.toml               # Package metadata, dependencies, entry point
├── uv.lock                      # Locked dependency versions (uv tool)
├── README.md                    # User-facing quick-start guide
├── LICENSE                      # MIT license text
└── CLAUDE.md                    # This file
```

### Key Files

**`src/tradingview_mcp/server.py`** — The entire server implementation (430 lines):
- FastMCP instance setup (`mcp`)
- Constant maps: `INTERVAL_MAP`, `SCREENER_MAP`
- Helper functions: `_resolve_interval`, `_resolve_screener`, `_build_handler`, `_format_*`
- 6 MCP tool definitions (decorated with `@mcp.tool()`)
- `main()` entrypoint that runs the stdio transport

**`pyproject.toml`** — Python project metadata:
- **Entry point:** `tradingview-mcp = "tradingview_mcp.server:main"`
- **Dependencies:**
  - `mcp[cli]>=1.2.0` — MCP framework
  - `tradingview-ta>=3.3.0` — Technical analysis library
  - `tradingview-screener>=2.5.0` — Market screener
  - `httpx>=0.27.0` — Async HTTP client

---

## Architecture & Design

### High-Level Flow

1. **User (AI assistant) calls an MCP tool** with symbol, exchange, screener, interval, etc.
2. **MCP server receives the request** via stdio transport
3. **Tool handler** (Python async function) processes the request:
   - Validates inputs using helper functions (`_resolve_interval`, `_resolve_screener`)
   - Creates a TradingView handler (`TA_Handler` or HTTP request via `httpx`)
   - Fetches data from TradingView APIs
   - Formats the response as JSON
4. **Response returned** to the AI assistant as JSON string

### Tool Definitions

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `get_technical_analysis` | Full TA summary (BUY/SELL/NEUTRAL) | symbol, exchange, screener, interval |
| `get_multi_timeframe` | Same symbol across multiple timeframes | symbol, exchange, screener, intervals (CSV) |
| `get_indicator_values` | Raw indicator values | symbol, exchange, screener, interval, indicators (CSV) |
| `search_symbol` | Search TradingView for symbols | query, type (filter) |
| `screen_market` | Custom screener with filters | screener, sort_by, sort_order, limit, min_volume, min/max_change_pct, market_type |
| `get_price_data` | OHLCV snapshot + key levels | symbol, exchange, screener, interval |

### Key Constants

**Timeframes** (`INTERVAL_MAP`):
```python
"1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1w", "1M"
```

**Screeners** (`SCREENER_MAP`):
```python
"america", "crypto", "forex", "cfd", "india", "uk", "japan", "germany", "russia", etc.
```

Supports aliases (e.g., "usa" → "america", "us" → "america").

---

## Development Workflow

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd tradingview-mcp
   ```

2. **Install dependencies with `uv` (recommended):**
   ```bash
   uv sync
   ```
   Or with pip:
   ```bash
   pip install -e .
   ```

3. **Verify installation:**
   ```bash
   uv run tradingview-mcp --help
   # Or: tradingview-mcp --help (after pip install -e .)
   ```

### Running Locally

**Via uv:**
```bash
uv run tradingview-mcp
```

**Via pip (after `pip install -e .`):**
```bash
tradingview-mcp
```

The server runs on **stdio transport** (reads stdin, writes stdout) and is ready for MCP-compatible clients to connect.

### Testing Integration

To verify a tool works end-to-end:

1. **Connect the server to an MCP client** (Claude Desktop, Perplexity, Cursor, etc.)
   - See README.md for setup instructions for each client

2. **Test a simple query** in the AI assistant:
   - "What's the technical analysis for AAPL on the 1d chart?"
   - "Show me RSI and MACD for NQ1! on a 5m chart"
   - "Search for gold futures on TradingView"

3. **Monitor server logs** (stderr) for any errors during execution

### Git Workflow

**Current branch:** `claude/claude-md-docs-m40dfa` (development branch for this documentation update)

**Workflow for changes:**
1. Always develop on the designated branch (e.g., `claude/claude-md-docs-m40dfa`)
2. Create small, focused commits with clear messages
3. Push to the designated branch: `git push -u origin <branch-name>`
4. Create a pull request (as draft) after pushing
5. Once approved, merge to `main`

**Commit message conventions:**
- Use imperative mood ("Add tool", not "Added tool")
- Be specific about what changed and why
- Reference issue numbers if applicable
- Example: `Add get_price_data tool for OHLCV + key levels`

---

## Common Development Tasks

### Adding a New Tool

1. **Define the tool function** in `server.py`, decorated with `@mcp.tool()`:
   ```python
   @mcp.tool()
   async def my_new_tool(symbol: str, exchange: str) -> str:
       """Brief docstring describing what the tool does.
       
       Args:
           symbol: Description
           exchange: Description
       """
       try:
           # Implementation
           handler = _build_handler(symbol, exchange, "america", "1d")
           analysis = handler.get_analysis()
           # Format and return as JSON string
           return json.dumps(data, indent=2)
       except Exception as e:
           return f"Error: {e}"
   ```

2. **Use helper functions** for common patterns:
   - `_build_handler()` — Creates a TradingView handler
   - `_resolve_interval()` — Converts human-friendly interval strings
   - `_resolve_screener()` — Maps screener aliases
   - `_format_summary()`, `_format_indicators()` — Format responses

3. **Always return JSON strings** (not Python dicts). Use `json.dumps()`.

4. **Include error handling** with try/except, returning error message as string.

5. **Add the tool to the README.md** tools table and example prompts.

6. **Test with an MCP client** before committing.

### Modifying an Existing Tool

1. **Check the docstring** for the tool's current behavior and parameters
2. **Consider backward compatibility** — changing parameter names will break client integrations
3. **Test the tool** with the modified signature in an MCP client
4. **Update the README** if you add/remove parameters or change defaults
5. **Commit with a clear message** explaining the change

### Handling API Errors

Most tools catch exceptions and return an error message as a string:
```python
except Exception as e:
    return f"Error fetching {thing}: {e}"
```

This keeps the tool graceful — the MCP client will see the error message but won't crash.

For debugging, check the server's stderr output for stack traces.

### Adding Timeframes or Screeners

1. **Add to `INTERVAL_MAP` or `SCREENER_MAP`** in `server.py`
2. **Include aliases** if applicable (e.g., "usa" → "america")
3. **No need to update tool signatures** — they use these maps internally
4. **Update the README** if you're adding new user-facing options

### Updating Dependencies

Use `uv` to add/upgrade dependencies:
```bash
uv add package_name
uv sync
```

This will:
- Update `pyproject.toml` and `uv.lock`
- Preserve lock file integrity

If using pip, manually edit `pyproject.toml` and reinstall:
```bash
pip install -e .
```

---

## Code Conventions

### Style & Formatting

- **Python version:** 3.10+ (type hints, modern syntax)
- **Imports:** Group standard library, third-party, local
- **Type hints:** Use them for function parameters and return types
- **Async:** All MCP tools are `async def` (FastMCP requirement)

### Naming Conventions

- **Tool names:** `snake_case`, descriptive (e.g., `get_technical_analysis`)
- **Functions:** `snake_case`
- **Constants:** `UPPER_CASE` (see `INTERVAL_MAP`, `SCREENER_MAP`)
- **Classes:** `PascalCase` (none currently in use)
- **Private functions:** Prefix with `_` (e.g., `_build_handler`)

### Documentation

- **Docstrings:** Use triple quotes, include Args section
- **Comments:** Minimal — code is self-documenting
- **README updates:** Required when adding/removing user-facing features
- **CLAUDE.md updates:** Keep in sync with code changes

### Error Handling

- **No silent failures** — always return an error message the user can see
- **Use try/except** at the top level of each tool
- **Preserve stack traces** in stderr for debugging
- **Return JSON** even for errors (consistency)

---

## Key Dependencies & Concepts

### FastMCP
- Lightweight MCP server framework
- Handles stdio transport, tool registration, parameter validation
- Decorators: `@mcp.tool()` for registering tools
- `.run(transport="stdio")` to start the server

### tradingview_ta
- Python library for TradingView technical analysis
- Core class: `TA_Handler(symbol, exchange, screener, interval, timeout)`
- Methods: `.get_analysis()` returns Analysis object with:
  - `.symbol`, `.exchange`, `.interval`, `.time`
  - `.summary` — overall recommendation
  - `.oscillators` — signal dictionary
  - `.moving_averages` — signal dictionary
  - `.indicators` — all raw indicator values

### tradingview_screener
- Library for TradingView market screening
- API: `Query().select(...).set_markets(...).where(...).order_by(...).limit(...).get_scanner_data()`
- Returns: `(total_count, dataframe)`

### httpx
- Async HTTP client (for `search_symbol` API calls)
- Used for the TradingView symbol search endpoint

---

## Testing & Verification

### Manual Testing

1. **Connect the server to an MCP client** (see README.md)
2. **Try each tool** with various inputs
3. **Check for:**
   - JSON formatting issues (must be valid JSON)
   - API errors or missing symbols
   - Timeout issues (15-second timeout per handler)
   - Indicator/screener availability

### Example Queries to Test

- `get_technical_analysis` with AAPL, NQ1!, BTCUSDT (stocks, futures, crypto)
- `get_multi_timeframe` with 5m, 15m, 1h, 4h, 1d
- `get_indicator_values` with a subset of indicators (RSI, MACD, BB)
- `search_symbol` with "gold", "bitcoin", "nasdaq"
- `screen_market` with different sorts (change, volume, RSI)
- `get_price_data` with various timeframes and intervals

### No Automated Tests Currently

The project has no test suite yet. Any tool additions should be manually verified with real MCP client integrations.

---

## Deployment & Configuration

### CLI Entry Point

The `pyproject.toml` defines:
```toml
[project.scripts]
tradingview-mcp = "tradingview_mcp.server:main"
```

This makes `tradingview-mcp` an available command after installation.

### Client Configuration

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "tradingview": {
      "command": "uv",
      "args": [
        "tool", "run", "--from",
        "git+https://github.com/whisperingotter29/tradingview-mcp.git",
        "tradingview-mcp"
      ]
    }
  }
}
```

**Perplexity** (Connectors UI):
- Server name: `TradingView`
- Command: `uv tool run --from git+https://github.com/whisperingotter29/tradingview-mcp.git tradingview-mcp`

**Cursor / VS Code** (`.cursor/mcp.json` or `.vscode/mcp.json`):
```json
{
  "servers": {
    "tradingview": {
      "command": "uv",
      "args": ["tool", "run", "--from", "git+...", "tradingview-mcp"]
    }
  }
}
```

### Timeouts

- **TA_Handler timeout:** 15 seconds (TradingView API calls)
- **HTTP client timeout:** 15 seconds (symbol search)

These are hardcoded in `server.py` and may need adjustment for slower networks.

---

## Troubleshooting

### Tool Returns Error Message Instead of Data

**Possible causes:**
1. Invalid symbol/exchange combination (check TradingView for correct format)
2. Network timeout — TradingView API took >15s to respond
3. TradingView screener is down or rate-limiting
4. Missing screener/market type

**Debug steps:**
1. Check server stderr for full stack trace
2. Try the symbol directly on TradingView.com
3. Verify exchange name (e.g., NASDAQ, not NASDAQ100)

### JSON Parsing Error on AI Assistant Side

**Possible cause:**
- Tool returned non-JSON string (e.g., error message without JSON formatting)

**Fix:**
- Ensure all tool return statements use `json.dumps()` or are formatted as error strings

### Screener Returns No Results

**Possible causes:**
1. Market screener doesn't have data for that criteria
2. Sort key doesn't exist (e.g., custom indicator that TradingView doesn't expose)
3. Filters are too restrictive

**Debug steps:**
1. Try a broader query (e.g., no volume filter)
2. Check the tradingview-screener documentation for valid sort keys
3. Use the web UI to find a working filter combination

---

## Future Enhancements

Potential improvements (not yet implemented):

- **Real-time alerts** — Subscribe to price/indicator changes
- **Backtesting engine** — Run strategies against historical data
- **Custom indicators** — User-defined TA formulas
- **Watchlist management** — Create/read/update watchlists
- **Test suite** — Unit tests for helper functions, mock API responses
- **Logging** — More structured logging for debugging

---

## Quick Reference

### Running Commands

| Task | Command |
|------|---------|
| Install | `uv sync` or `pip install -e .` |
| Run locally | `uv run tradingview-mcp` |
| Add dependency | `uv add <package>` |
| Verify setup | `uv run tradingview-mcp --help` |

### Key Files & Line Ranges

| File | Purpose | Key Lines |
|------|---------|-----------|
| `server.py:1–36` | Imports, logging, MCP instance setup | |
| `server.py:42–74` | Constant maps (`INTERVAL_MAP`, `SCREENER_MAP`) | |
| `server.py:77–105` | Helper functions (`_resolve_*`, `_build_handler`) | |
| `server.py:140–163` | `get_technical_analysis` tool | |
| `server.py:167–193` | `get_multi_timeframe` tool | |
| `server.py:196–227` | `get_indicator_values` tool | |
| `server.py:231–277` | `search_symbol` tool | |
| `server.py:281–372` | `screen_market` tool | |
| `server.py:376–415` | `get_price_data` tool | |
| `server.py:423–429` | `main()` entrypoint | |

### Tool Parameters Quick Reference

**All analysis tools require:**
- `symbol` (e.g., "AAPL", "NQ1!", "BTCUSDT")
- `exchange` (e.g., "NASDAQ", "CME", "BINANCE")
- `screener` (default: "america") — can also be "crypto", "forex", "cfd", etc.
- `interval` (default varies by tool) — e.g., "1m", "5m", "15m", "1h", "1d"

**Special parameters:**
- `intervals` (in `get_multi_timeframe`) — comma-separated, e.g., "5m,15m,1h,4h,1d"
- `indicators` (in `get_indicator_values`) — comma-separated, e.g., "RSI,MACD.macd,BB.upper"
- `query` and `type` (in `search_symbol`) — no exchange/screener needed

---

## Questions for AI Assistants

**When modifying this codebase, consider:**
1. Does this tool maintain backward compatibility?
2. Is the error handling graceful (returns string, not crash)?
3. Have you tested with real TradingView data?
4. Does the README need updating?
5. Are new timeframes/screeners/indicators in the constants?

**When adding a feature:**
1. Add the tool function with `@mcp.tool()` decorator
2. Include full docstring with Args section
3. Return JSON via `json.dumps()` or error string
4. Handle exceptions without crashing
5. Update README.md with the new tool
6. Test with an MCP client before committing
7. Commit with a descriptive message

---

**Document last updated:** 2026-06-21  
**Version:** 0.1.0  
**Status:** Beta
