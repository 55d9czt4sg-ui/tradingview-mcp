# TradingView MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that gives AI assistants access to TradingView technical analysis, market screening, and real-time indicator data.

Built to work with **Perplexity**, Claude Desktop, Cursor, and any other MCP-compatible client.

## Tools

| Tool | Description |
|------|-------------|
| `get_technical_analysis` | Full TA summary (BUY/SELL/NEUTRAL) for a symbol with oscillator + MA breakdown |
| `get_multi_timeframe` | Analyse one symbol across multiple timeframes at once (confluence check) |
| `get_indicator_values` | Raw indicator values — RSI, MACD, Bollinger Bands, EMA, VWMA, ADX, Stoch, etc. |
| `search_symbol` | Search TradingView for symbols by name or ticker |
| `screen_market` | Custom screener — top gainers, losers, high volume, breakout candidates |
| `get_price_data` | Current OHLCV snapshot with key levels (pivots, BB, VWAP, P.SAR, ATR) |

## Supported Markets

Stocks, crypto, forex, futures (gold, Nasdaq, S&P), CFDs, bonds, and more — anything available on TradingView.

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install

```bash
# Clone the repo
git clone https://github.com/whisperingotter29/tradingview-mcp.git
cd tradingview-mcp

# Option A: uv (recommended)
uv sync

# Option B: pip
pip install -e .
```

### Run the server

```bash
# With uv
uv run tradingview-mcp

# With pip install
tradingview-mcp
```

## Connect to Perplexity (Mac)

1. Open **Perplexity** → **Settings** → **Connectors**
2. Install the **Perplexity Helper** if you haven't already
3. Click **Add Connector** → **Simple** tab
4. Set the server name to `TradingView`
5. Set the command to:

```
uv tool run --from git+https://github.com/whisperingotter29/tradingview-mcp.git tradingview-mcp
```

Or if you cloned locally:

```
/path/to/tradingview-mcp/.venv/bin/tradingview-mcp
```

6. Click **Save** and wait for "Running" status
7. Toggle the connector on under **Sources** in a new chat

### Advanced JSON config (Perplexity)

```json
{
  "command": "uv",
  "args": [
    "tool", "run", "--from",
    "git+https://github.com/whisperingotter29/tradingview-mcp.git",
    "tradingview-mcp"
  ],
  "env": {}
}
```

## Connect to Claude Desktop

Add to your `claude_desktop_config.json`:

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

## Connect to Cursor / VS Code

Add to `.cursor/mcp.json` or `.vscode/mcp.json`:

```json
{
  "servers": {
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

## Example Prompts

Once connected, try asking your AI assistant:

- "What's the technical analysis for gold futures (GC1!) on the 5-minute chart?"
- "Show me RSI, MACD, and Bollinger Bands for NQ1! across 5m, 15m, 1h, and 4h"
- "Find the top 10 crypto gainers right now"
- "Search for Nasdaq futures symbols on TradingView"
- "Get the current price, VWAP, and pivot levels for AAPL"
- "Screen US stocks with volume over 1 million that are up more than 5% today"

## Available Indicators

The `get_indicator_values` tool supports all TradingView indicators, including:

**Oscillators:** RSI, MACD.macd, MACD.signal, Stoch.K, Stoch.D, CCI20, ADX, AO, Mom, W.R, Stoch.RSI.K, UO, BBPower

**Moving Averages:** EMA5, EMA10, EMA20, EMA50, EMA100, EMA200, SMA5, SMA10, SMA20, SMA50, SMA100, SMA200, VWMA, HullMA9, Ichimoku.BLine

**Bands & Levels:** BB.upper, BB.lower, P.SAR, Pivot.M.Classic.R1/R2/R3, Pivot.M.Classic.S1/S2/S3, Pivot.M.Classic.Middle

**Price:** open, high, low, close, volume, change, change_abs, ATR

## Timeframes

`1m` · `5m` · `15m` · `30m` · `1h` · `2h` · `4h` · `1d` · `1w` · `1M`

## License

MIT
