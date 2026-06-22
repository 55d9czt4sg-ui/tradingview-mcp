# Architecture & Design

This document explains how the TradingView MCP Server works, its design principles, and how to extend it.

## Overview

The TradingView MCP Server is a lightweight bridge between AI assistants and TradingView's market data. It implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) to expose financial data as tools that Claude, Perplexity, and other AI clients can call.

```
┌─────────────────────┐
│  AI Assistant       │  (Claude, Perplexity, etc.)
│  (Claude, etc.)     │
└──────────┬──────────┘
           │ MCP Protocol (JSON-RPC over stdio)
           │
┌──────────▼──────────────────────────────┐
│  TradingView MCP Server                 │
│  ┌──────────────────────────────────┐   │
│  │ FastMCP Framework                │   │
│  │  - Tool Registration             │   │
│  │  - Request Routing               │   │
│  │  - stdio Transport               │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ Tool Implementations             │   │
│  │  - get_technical_analysis()      │   │
│  │  - get_multi_timeframe()         │   │
│  │  - get_indicator_values()        │   │
│  │  - search_symbol()               │   │
│  │  - screen_market()               │   │
│  │  - get_price_data()              │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ TradingView APIs                 │   │
│  │  - tradingview-ta (Analysis)     │   │
│  │  - tradingview-screener (Market) │   │
│  │  - HTTP API (Symbol Search)      │   │
│  └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
           │
           ├──→ TradingView APIs
           └──→ Market Data Providers
```

## Key Components

### 1. FastMCP Framework

Located in `server.py`, the FastMCP instance handles:
- **Tool Registration** — Decorators (`@mcp.tool()`) register Python functions as MCP tools
- **Request Parsing** — Receives JSON-RPC requests from the AI client
- **Response Formatting** — Returns results as JSON strings
- **Transport** — Communicates over stdio (standard input/output)

```python
mcp = FastMCP(
    "tradingview",
    instructions="TradingView technical analysis, screening, and market data.",
)
```

### 2. Tool Implementations

Each tool is an async function decorated with `@mcp.tool()`. Tools accept user inputs and return JSON strings.

**Pattern:**
```python
@mcp.tool()
async def tool_name(param1: str, param2: str = "default") -> str:
    """Docstring visible to AI clients."""
    try:
        # Call TradingView APIs
        result = do_something()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"
```

### 3. TradingView Data Sources

#### tradingview-ta Library
Provides technical analysis via `TA_Handler`:
- Single symbol, single timeframe analysis
- BUY/SELL/NEUTRAL recommendations
- Oscillator and moving-average signals
- Raw indicator values

```python
handler = TA_Handler(
    symbol="AAPL",
    exchange="NASDAQ",
    screener="america",
    interval=Interval.INTERVAL_1_DAY,
)
analysis = handler.get_analysis()
```

#### tradingview-screener Library
Provides market screening via `Query` and `Column`:
- Filter stocks, crypto, forex, futures
- Sort by price, volume, technical indicators
- Pagination support

```python
q = Query().select("name", "close", "volume", "RSI")
q = q.set_markets("america")
q = q.where(Column("volume") >= 1000000)
q = q.order_by("volume", ascending=False)
q = q.limit(20)
result = q.get_scanner_data()  # Returns (count, DataFrame)
```

#### Symbol Search API
HTTP endpoint for finding symbols:
- Query by name or ticker (e.g., "gold futures", "AAPL")
- Filter by type (stock, crypto, futures, etc.)
- Returns symbol, exchange, description

```python
params = {
    "text": "gold futures",
    "search_type": "futures",
}
resp = await httpx.get("https://symbol-search.tradingview.com/symbol_search/v3/", params=params)
symbols = resp.json()["symbols"]
```

## Design Decisions

### Why Async?

All tools are async (`async def`) to:
- Support concurrent requests from MCP clients
- Allow long-running API calls without blocking other tools
- Scale better on high-load scenarios

### Error Handling

Tools return error messages as strings (not exceptions):
```python
try:
    # ... do work ...
    return json.dumps(result)
except Exception as e:
    return f"Error: {e}"
```

This ensures the MCP client receives a readable response instead of a protocol error.

### Interval & Screener Resolution

The server provides helper functions to convert user-friendly inputs to TradingView constants:

```python
# "1d" → Interval.INTERVAL_1_DAY
_resolve_interval("1d")

# "america" or "usa" or "us" → "america"
_resolve_screener("usa")
```

This makes tools more user-friendly from natural-language prompts.

## Data Flow Example: `get_technical_analysis`

1. **AI Client Request:**
   ```json
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "get_technical_analysis",
       "arguments": {
         "symbol": "AAPL",
         "exchange": "NASDAQ",
         "screener": "america",
         "interval": "1d"
       }
     }
   }
   ```

2. **Server Processing:**
   ```python
   # Build handler
   handler = TA_Handler(symbol="AAPL", exchange="NASDAQ", ...)
   
   # Get analysis
   analysis = handler.get_analysis()
   
   # Format output
   result = {
       "symbol": "AAPL",
       "summary": {"BUY": 7, "NEUTRAL": 3, "SELL": 0},
       "oscillators": {"RSI": 65, "MACD.macd": 0.5, ...},
       "moving_averages": {"EMA20": 180.5, "EMA50": 178.2, ...},
   }
   ```

3. **Response to AI Client:**
   ```json
   {
     "jsonrpc": "2.0",
     "result": "{\"symbol\": \"AAPL\", \"summary\": {...}, ...}"
   }
   ```

4. **AI Interpretation:**
   Claude, Perplexity, etc., parse the JSON and present to the user in natural language.

## Extending the Server

### Adding a New Tool

1. **Define the tool:**
   ```python
   @mcp.tool()
   async def new_tool(symbol: str, param2: str) -> str:
       """One-line description for AI clients."""
       try:
           result = do_analysis(symbol, param2)
           return json.dumps(result)
       except Exception as e:
           return f"Error: {e}"
   ```

2. **Document parameters in the docstring** — AI clients read these to understand tool usage

3. **Test locally:**
   ```bash
   uv run tradingview-mcp
   # Send JSON-RPC requests via stdin to test
   ```

4. **Commit and push** to GitHub

### Adding New Data Sources

If TradingView releases new APIs or libraries:

1. Add the dependency to `pyproject.toml`
2. Create helper functions (like `_build_handler()`) to wrap the library
3. Implement new tools using the helpers
4. Update documentation

### Performance Optimization

If response times are slow:

1. **Add caching** — Store recent queries with timestamps
2. **Batch requests** — Combine multi-symbol queries into one API call
3. **Async concurrency** — Use `asyncio.gather()` for parallel requests
4. **Lazy loading** — Only fetch data when explicitly requested

## MCP Protocol Overview

The server communicates with AI clients via JSON-RPC over stdio:

**Tool Registration (Server → Client on startup):**
```json
{
  "tools": [
    {
      "name": "get_technical_analysis",
      "description": "Get a full technical analysis summary...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "symbol": {"type": "string"},
          "exchange": {"type": "string"},
          ...
        },
        "required": ["symbol", "exchange"]
      }
    },
    ...
  ]
}
```

**Tool Call (Client → Server):**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_technical_analysis",
    "arguments": {...}
  }
}
```

**Response (Server → Client):**
```json
{
  "jsonrpc": "2.0",
  "result": "{...json result...}"
}
```

## Limitations & Future Work

### Current Limitations

1. **No Caching** — Every tool call fetches fresh data (can be slow)
2. **No Authentication** — Uses public TradingView APIs only
3. **No Persistence** — No database or state tracking
4. **Single-Symbol Queries** — Multi-symbol queries require multiple API calls

### Potential Enhancements

1. **Redis Caching** — Cache results for 5–60 seconds
2. **Batch Operations** — Combine multiple symbols into one request
3. **WebSocket Support** — Real-time streaming (requires TradingView Pro)
4. **Custom Indicators** — Allow AI to define custom technical analysis formulas
5. **Portfolio Tracking** — Monitor user watchlists and alerts
6. **Sentiment Analysis** — Integrate with news/social sentiment APIs

## Testing

### Unit Tests (Future)

```python
import pytest
from tradingview_mcp.server import get_technical_analysis

@pytest.mark.asyncio
async def test_get_technical_analysis_aapl():
    result = await get_technical_analysis("AAPL", "NASDAQ")
    data = json.loads(result)
    assert data["symbol"] == "AAPL"
    assert "summary" in data
```

### Manual Testing

```bash
# Start server
uv run tradingview-mcp

# In another terminal, send a JSON-RPC request
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_technical_analysis","arguments":{"symbol":"AAPL","exchange":"NASDAQ"}}}' | nc localhost 9000
```

## Deployment

### Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["tradingview-mcp"]
```

### Systemd (Linux)

```ini
[Unit]
Description=TradingView MCP Server
After=network.target

[Service]
Type=simple
User=tradingview
ExecStart=/usr/local/bin/tradingview-mcp
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## References

- [MCP Specification](https://modelcontextprotocol.io/introduction)
- [FastMCP Documentation](https://github.com/jlotz/fastmcp)
- [TradingView TA Repository](https://github.com/deathlyface/tradingview-ta)
- [TradingView Screener Repository](https://github.com/shayneobrien/tradingview-screener)
