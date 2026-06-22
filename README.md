# TradingView MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that gives AI assistants access to real-time TradingView technical analysis, market screening, and indicator data. Built for **Perplexity**, Claude Desktop, Cursor, and any MCP-compatible client.

## Overview

This MCP server bridges AI assistants and TradingView's market data, enabling natural-language financial analysis. Query multiple timeframes, screen entire markets, retrieve precise indicator values, and get consensus buy/sell signals—all via conversational AI.

### Key Features

- **Multi-timeframe Analysis** — Analyze symbols across 5m, 15m, 1h, 4h, 1d, 1w, 1M timeframes simultaneously
- **Technical Analysis** — BUY/SELL/NEUTRAL signals with oscillator and moving-average breakdowns
- **Market Screening** — Filter stocks, crypto, forex, and futures by volume, change %, technical signals
- **40+ Indicators** — RSI, MACD, Bollinger Bands, EMA, VWMA, ADX, Stochastic, and more
- **Global Markets** — Stocks, crypto, forex, futures, CFDs, bonds, indexes, ETFs
- **Zero Configuration** — Works out-of-the-box; install and connect to your MCP client

## Tools

| Tool | Use Case | Returns |
|------|----------|---------|
| `get_technical_analysis` | Single symbol, single timeframe recommendation | BUY/SELL/NEUTRAL + oscillator/MA signals |
| `get_multi_timeframe` | Confluence checks across timeframes | Summary for each timeframe side-by-side |
| `get_indicator_values` | Precise numeric indicator data | Raw values for RSI, MACD, BB, pivots, etc. |
| `search_symbol` | Find symbols by name or ticker | Symbol, exchange, type, description |
| `screen_market` | Find top gainers, losers, active instruments | Ranked list with technical signals |
| `get_price_data` | Current snapshot + key levels | OHLCV + pivots, BB, VWAP, P.SAR, ATR |

## Supported Markets

| Market | Screener | Examples |
|--------|----------|----------|
| **US Stocks** | `america` | AAPL, TSLA, SPY, QQQ |
| **Crypto** | `crypto` | BTCUSDT, ETHUSDT (Binance); BTC (US) |
| **Futures** | `america`, `cme` | NQ1! (Nasdaq), GC1! (Gold), ES1! (S&P 500) |
| **Forex** | `forex` | EURUSD, GBPUSD, USDJPY |
| **Indices** | `america` | DXY, VIX, ^GSPC |
| **Bonds** | `bond` | US Treasury instruments |
| **CFDs** | `cfd` | Commodities, indices, stocks |
| **International** | `uk`, `japan`, `india`, `brazil`, `australia`, etc. | Regional exchanges |

## Quick Start

### Prerequisites

- **Python 3.10+** — Make sure your Python version is 3.10 or later: `python3 --version`
- **[uv](https://docs.astral.sh/uv/)** (recommended) or **pip** — Package manager for Python

### Installation

#### Option A: Using uv (Recommended)

```bash
git clone https://github.com/whisperingotter29/tradingview-mcp.git
cd tradingview-mcp
uv sync
```

#### Option B: Using pip

```bash
git clone https://github.com/whisperingotter29/tradingview-mcp.git
cd tradingview-mcp
pip install -e .
```

#### Option C: Direct from GitHub

```bash
# With uv
uv tool run --from git+https://github.com/whisperingotter29/tradingview-mcp.git tradingview-mcp

# With pip
pip install git+https://github.com/whisperingotter29/tradingview-mcp.git
```

### Running the Server Standalone

Once installed, run the server to verify it works:

```bash
# If installed with uv
uv run tradingview-mcp

# If installed with pip
tradingview-mcp
```

You should see a message confirming the MCP server is running on stdio transport. Press `Ctrl+C` to stop.

## Setup: Connect to Your MCP Client

### Perplexity (Mac)

1. **Settings** → **Connectors** → **Add Connector**
2. Select **Simple** tab
3. Configure:
   - **Server name:** `TradingView`
   - **Command:**
     ```
     uv tool run --from git+https://github.com/whisperingotter29/tradingview-mcp.git tradingview-mcp
     ```
     Or if cloned locally:
     ```
     /path/to/tradingview-mcp/.venv/bin/tradingview-mcp
     ```
4. Click **Save** → Wait for "Running" status
5. In a new chat, toggle **TradingView** under **Sources**

**Advanced JSON config (Perplexity):**
```json
{
  "command": "uv",
  "args": ["tool", "run", "--from", "git+https://github.com/whisperingotter29/tradingview-mcp.git", "tradingview-mcp"],
  "env": {}
}
```

### Claude Desktop

1. Find your config file:
   - **macOS/Linux:** `~/.config/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. Add or update the `mcpServers` section:
```json
{
  "mcpServers": {
    "tradingview": {
      "command": "uv",
      "args": ["tool", "run", "--from", "git+https://github.com/whisperingotter29/tradingview-mcp.git", "tradingview-mcp"]
    }
  }
}
```

3. Restart Claude Desktop
4. The **TradingView** tools will now appear in Claude's tool list

### Cursor / VS Code (Claude Code)

Add to `.cursor/mcp.json` or `.vscode/mcp.json`:
```json
{
  "servers": {
    "tradingview": {
      "command": "uv",
      "args": ["tool", "run", "--from", "git+https://github.com/whisperingotter29/tradingview-mcp.git", "tradingview-mcp"]
    }
  }
}
```

### Local Development (No uv needed)

If you've cloned the repo locally and want to point to it directly:

**Claude Desktop:**
```json
{
  "mcpServers": {
    "tradingview": {
      "command": "python",
      "args": ["-m", "tradingview_mcp.server"],
      "cwd": "/path/to/tradingview-mcp"
    }
  }
}
```

**Cursor/VS Code:**
```json
{
  "servers": {
    "tradingview": {
      "command": "python",
      "args": ["-m", "tradingview_mcp.server"],
      "cwd": "/path/to/tradingview-mcp"
    }
  }
}
```

## Example Prompts

Once connected to your MCP client, ask your AI assistant any of these:

### Technical Analysis
- "What's the technical analysis for gold futures (GC1!) on the 5-minute chart?"
- "Is NQ1! (Nasdaq 100 futures) in an uptrend on the daily?"
- "Check AAPL on the 1-hour and 4-hour — is there confluence?"

### Multi-Timeframe Analysis
- "Show me RSI, MACD, and Bollinger Bands for NQ1! across 5m, 15m, 1h, and 4h"
- "Analyze BTCUSDT (Bitcoin) on 15m, 1h, 4h, and 1d. Any confluence signals?"
- "Give me the technical summary for ES1! (S&P 500 futures) on 1m through 4h"

### Market Screening
- "Find the top 10 crypto gainers right now"
- "Screen US stocks with volume over 1 million that are up more than 5% today"
- "Show me stocks with RSI above 70 (overbought) today"
- "What are the worst performers in the crypto market?"

### Symbol Search
- "Search for Nasdaq futures symbols on TradingView"
- "Find gold-related symbols — futures and ETFs"
- "What's the ticker for Tesla options?"

### Price & Indicators
- "Get the current price, VWAP, and pivot levels for AAPL"
- "What are the current Bollinger Band levels for SPY?"
- "Show me the RSI, Stochastic, and ADX for GC1! (gold futures)"

### Advanced Workflows
- "Check if there's a golden cross on MSFT's daily chart (EMA50 > EMA200)"
- "Which sectors have the best momentum right now?"
- "Screen for stocks with high volume and small price moves (low volatility breakout candidates)"

## Available Indicators

The `get_indicator_values` tool returns raw numeric values for 40+ TradingView indicators:

### Oscillators (Momentum)
- **RSI** — Relative Strength Index (0–100)
- **MACD** — MACD.macd, MACD.signal, MACD.histogram
- **Stochastic** — Stoch.K, Stoch.D (0–100)
- **CCI20** — Commodity Channel Index
- **ADX** — Average Directional Index (trend strength)
- **AO** — Awesome Oscillator
- **Mom** — Momentum
- **W.R** — Williams %R
- **UO** — Ultimate Oscillator
- **BBPower** — Bollinger Bands Power
- **Stoch.RSI** — Stochastic RSI

### Moving Averages
- **EMA** — Exponential: 5, 10, 20, 50, 100, 200
- **SMA** — Simple: 5, 10, 20, 50, 100, 200
- **VWMA** — Volume-Weighted Moving Average
- **HullMA9** — Hull Moving Average
- **Ichimoku.BLine** — Ichimoku Base Line

### Bands & Levels
- **Bollinger Bands** — BB.upper, BB.lower, BB.middle (typical: 20-period, 2 STD)
- **Pivot Points** — Pivot.M.Classic.R1/R2/R3, Pivot.M.Classic.S1/S2/S3, Pivot.M.Classic.Middle
- **P.SAR** — Parabolic SAR (stop-and-reverse)
- **ATR** — Average True Range (volatility measure)

### Price & Volume
- **OHLCV** — open, high, low, close, volume
- **Change** — Absolute and percentage change
- **Recommend.All** — TradingView's aggregate buy/sell/neutral score

## Timeframes

**Intraday:** `1m` · `5m` · `15m` · `30m`  
**Hourly:** `1h` · `2h` · `4h`  
**Daily+:** `1d` · `1w` · `1M`

Use any timeframe with any tool. Multi-timeframe analysis is most powerful for confluence checks (e.g., "is the hourly and daily aligned?").

## Troubleshooting

### "MCP Server Not Found" / "Connection Refused"

**Problem:** Your MCP client can't find or start the server.

**Solutions:**
1. Verify Python 3.10+ is installed: `python3 --version`
2. Ensure the server starts manually: `uv run tradingview-mcp` or `tradingview-mcp`
3. Check the command path in your config file matches your installation
4. On Windows, use full paths without relative paths like `~/`
5. Restart your MCP client (e.g., Claude Desktop, Perplexity)

### "Timeout" or "Symbol Not Found"

**Problem:** A symbol query times out or returns no data.

**Solutions:**
1. Verify the symbol exists on TradingView (check the website directly)
2. Use the correct exchange (e.g., `NASDAQ` for US stocks, `BINANCE` for crypto)
3. Try with a different market screener (e.g., `america` vs `cfd`)
4. For futures, include the contract month or quarter (e.g., `NQ1!` for Nasdaq, not `NQ`)

### Tools Not Showing Up

**Problem:** You've installed the server but tools don't appear in your AI chat.

**Solutions:**
1. Restart your MCP client completely
2. Check the MCP server logs (see your client's settings/logs)
3. Verify the config file syntax is valid JSON
4. Ensure the Python path in your config is correct (`which python3` on Mac/Linux)

## Development

### Running Locally

```bash
# Clone and install dependencies
git clone https://github.com/whisperingotter29/tradingview-mcp.git
cd tradingview-mcp
uv sync

# Run the server in stdio mode (for testing)
uv run -m tradingview_mcp.server

# Or use the CLI wrapper
uv run tradingview-mcp
```

### Project Structure

```
tradingview-mcp/
├── src/tradingview_mcp/
│   ├── __init__.py          # Version info
│   └── server.py            # MCP server + tool implementations
├── pyproject.toml           # Project metadata and dependencies
├── README.md                # This file
└── LICENSE                  # MIT License
```

### Adding a New Tool

1. Define the tool as an `@mcp.tool()` async function in `server.py`
2. Add docstring with args and return description
3. Use `json.dumps()` to return structured data
4. Test with `uv run tradingview-mcp` and query manually
5. Push to GitHub

### Dependencies

- **mcp** — Model Context Protocol SDK (handles tool registration, stdio transport)
- **tradingview-ta** — TradingView technical analysis library (TA_Handler)
- **tradingview-screener** — TradingView market screener (Query, Column)
- **httpx** — Async HTTP client (for symbol search API)

See `pyproject.toml` for versions.

### Testing

No test suite is included yet. To manually test:

```python
# In Python REPL
import asyncio
from tradingview_mcp.server import get_technical_analysis

result = asyncio.run(get_technical_analysis("AAPL", "NASDAQ", "america", "1d"))
print(result)
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Test your changes locally
4. Commit with clear messages
5. Push to GitHub and open a pull request

## Resources

- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [TradingView TA Library](https://github.com/deathlyface/tradingview-ta)
- [TradingView Screener](https://github.com/shayneobrien/tradingview-screener)

## License

MIT — See [LICENSE](LICENSE) for details.
