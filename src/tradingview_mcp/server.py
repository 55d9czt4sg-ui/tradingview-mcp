"""
TradingView MCP Server
=====================
Exposes TradingView technical analysis, screening, and market data
as MCP tools that any MCP-compatible AI assistant can call.

Tools:
  - get_technical_analysis    — Full TA summary for a single symbol
  - get_multi_timeframe       — Same symbol across multiple timeframes at once
  - get_indicator_values      — Raw indicator values (RSI, MACD, BB, etc.)
  - search_symbol             — Find TradingView symbols by name/ticker
  - screen_market             — Custom screener with filters (top gainers/losers, etc.)
  - get_price_data            — Current OHLCV snapshot for a symbol
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from tradingview_ta import TA_Handler, Interval

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tradingview-mcp")

# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "tradingview",
    instructions="TradingView technical analysis, screening, and market data.",
)

# ---------------------------------------------------------------------------
# Constants / helpers
# ---------------------------------------------------------------------------

INTERVAL_MAP: dict[str, str] = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "30m": Interval.INTERVAL_30_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR,
    "2h": Interval.INTERVAL_2_HOURS,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY,
    "1w": Interval.INTERVAL_1_WEEK,
    "1M": Interval.INTERVAL_1_MONTH,
}

# Common screener names expected by tradingview_ta
SCREENER_MAP: dict[str, str] = {
    "america": "america",
    "usa": "america",
    "us": "america",
    "crypto": "crypto",
    "forex": "forex",
    "cfd": "cfd",
    "india": "india",
    "uk": "uk",
    "indonesia": "indonesia",
    "brazil": "brazil",
    "australia": "australia",
    "japan": "japan",
    "germany": "germany",
    "spain": "spain",
    "turkey": "turkey",
    "russia": "russia",
    "korea": "korea",
}


def _resolve_interval(interval: str) -> str:
    """Return the Interval constant string from a human-friendly key."""
    key = interval.strip().lower()
    if key in INTERVAL_MAP:
        return INTERVAL_MAP[key]
    raise ValueError(
        f"Unknown interval '{interval}'. "
        f"Valid values: {', '.join(INTERVAL_MAP.keys())}"
    )


def _resolve_screener(screener: str) -> str:
    key = screener.strip().lower()
    return SCREENER_MAP.get(key, key)


def _build_handler(
    symbol: str,
    exchange: str,
    screener: str,
    interval: str,
) -> TA_Handler:
    return TA_Handler(
        symbol=symbol.upper(),
        exchange=exchange.upper(),
        screener=_resolve_screener(screener),
        interval=_resolve_interval(interval),
        timeout=15,
    )


def _format_summary(analysis: Any) -> dict:
    """Extract the most useful fields from an Analysis object."""
    return {
        "symbol": analysis.symbol,
        "exchange": analysis.exchange,
        "interval": analysis.interval,
        "time": str(analysis.time),
        "summary": analysis.summary,
        "oscillators": analysis.oscillators,
        "moving_averages": analysis.moving_averages,
    }


def _format_indicators(analysis: Any, keys: list[str] | None = None) -> dict:
    """Return raw indicator values, optionally filtered to *keys*."""
    indicators = analysis.indicators
    if keys:
        indicators = {k: indicators.get(k) for k in keys}
    return {
        "symbol": analysis.symbol,
        "exchange": analysis.exchange,
        "interval": analysis.interval,
        "time": str(analysis.time),
        "indicators": indicators,
    }


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_technical_analysis(
    symbol: str,
    exchange: str,
    screener: str = "america",
    interval: str = "1d",
) -> str:
    """Get a full technical analysis summary for a symbol.

    Returns overall recommendation (BUY/SELL/NEUTRAL), oscillator signals,
    and moving-average signals.

    Args:
        symbol:   Ticker symbol (e.g. AAPL, BTCUSDT, NQ1!, GC1!)
        exchange: Exchange name (e.g. NASDAQ, BINANCE, COMEX, CME)
        screener: Market screener — america, crypto, forex, cfd, etc. (default: america)
        interval: Timeframe — 1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1w, 1M (default: 1d)
    """
    try:
        handler = _build_handler(symbol, exchange, screener, interval)
        analysis = handler.get_analysis()
        return json.dumps(_format_summary(analysis), indent=2)
    except Exception as e:
        return f"Error fetching analysis for {symbol}: {e}"


@mcp.tool()
async def get_multi_timeframe(
    symbol: str,
    exchange: str,
    screener: str = "america",
    intervals: str = "5m,15m,1h,4h,1d",
) -> str:
    """Analyse a symbol across multiple timeframes at once.

    Great for confluence checks — see if the trend aligns on
    higher and lower timeframes simultaneously.

    Args:
        symbol:    Ticker symbol (e.g. AAPL, NQ1!, GC1!)
        exchange:  Exchange name (e.g. NASDAQ, CME, COMEX)
        screener:  Market screener (default: america)
        intervals: Comma-separated timeframes, e.g. "5m,15m,1h,4h,1d"
    """
    results: list[dict] = []
    for ivl in intervals.split(","):
        ivl = ivl.strip()
        try:
            handler = _build_handler(symbol, exchange, screener, ivl)
            analysis = handler.get_analysis()
            results.append(_format_summary(analysis))
        except Exception as e:
            results.append({"interval": ivl, "error": str(e)})
    return json.dumps(results, indent=2)


@mcp.tool()
async def get_indicator_values(
    symbol: str,
    exchange: str,
    screener: str = "america",
    interval: str = "5m",
    indicators: str = "RSI,MACD.macd,MACD.signal,BB.upper,BB.lower,close,open,high,low,volume,EMA20,EMA50,EMA200,VWMA,ADX,Stoch.K,Stoch.D,CCI20,Mom,AO,W.R",
) -> str:
    """Get raw indicator values for a symbol.

    Use this when you need exact numeric values rather than BUY/SELL signals.

    Args:
        symbol:     Ticker symbol (e.g. GC1!, NQ1!, AAPL, BTCUSDT)
        exchange:   Exchange name (e.g. CME, COMEX, NASDAQ, BINANCE)
        screener:   Market screener (default: america)
        interval:   Timeframe (default: 5m)
        indicators: Comma-separated indicator keys.
                    Common keys: RSI, MACD.macd, MACD.signal, BB.upper, BB.lower,
                    close, open, high, low, volume, EMA5, EMA10, EMA20, EMA50,
                    EMA100, EMA200, SMA5, SMA10, SMA20, SMA50, SMA100, SMA200,
                    VWMA, ADX, Stoch.K, Stoch.D, CCI20, Mom, AO, W.R,
                    P.SAR, HullMA9, Ichimoku.BLine, Rec.Stoch.RSI,
                    Pivot.M.Classic.R1, Pivot.M.Classic.S1, change, Recommend.All
    """
    keys = [k.strip() for k in indicators.split(",") if k.strip()]
    try:
        handler = _build_handler(symbol, exchange, screener, interval)
        analysis = handler.get_analysis()
        return json.dumps(_format_indicators(analysis, keys), indent=2)
    except Exception as e:
        return f"Error fetching indicators for {symbol}: {e}"


@mcp.tool()
async def search_symbol(query: str, type: str = "") -> str:
    """Search for TradingView symbols by name or ticker.

    Args:
        query: Search query (e.g. "gold futures", "AAPL", "bitcoin", "NQ1")
        type:  Optional filter — stock, crypto, futures, forex, index, bond, fund, dr, cfd, economic
    """
    try:
        params: dict[str, Any] = {
            "text": query,
            "hl": 1,
            "exchange": "",
            "lang": "en",
            "search_type": type or "undefined",
            "domain": "production",
            "sort_by_country": "US",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://symbol-search.tradingview.com/symbol_search/v3/",
                params=params,
                headers={
                    "User-Agent": "tradingview-mcp/0.1",
                    "Origin": "https://www.tradingview.com",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        symbols = data.get("symbols", [])
        formatted = []
        for s in symbols[:15]:
            desc = s.get("description", "")
            # Strip HTML highlight tags
            desc = re.sub(r"<[^>]+>", "", desc)
            formatted.append(
                {
                    "symbol": s.get("symbol", ""),
                    "exchange": s.get("exchange", ""),
                    "type": s.get("type", ""),
                    "description": desc,
                }
            )
        return json.dumps(formatted, indent=2)
    except Exception as e:
        return f"Error searching for '{query}': {e}"


@mcp.tool()
async def screen_market(
    screener: str = "america",
    sort_by: str = "change",
    sort_order: str = "desc",
    limit: int = 20,
    min_volume: int | None = None,
    min_change_pct: float | None = None,
    max_change_pct: float | None = None,
    market_type: str = "stock",
) -> str:
    """Screen the market for top gainers, losers, active stocks, etc.

    Uses TradingView's official screener API to find instruments matching
    your criteria. Supports stocks, crypto, forex, futures, bonds.

    Args:
        screener:       Market — america, crypto, forex, cfd, india, etc. (default: america)
        sort_by:        Field to sort by — change, volume, market_cap_basic, close, Recommend.All, RSI, MACD.macd, etc. (default: change)
        sort_order:     "asc" or "desc" (default: desc)
        limit:          Number of results to return, max 50 (default: 20)
        min_volume:     Minimum volume filter (optional)
        min_change_pct: Minimum % change filter (optional, e.g. 5.0 for +5%)
        max_change_pct: Maximum % change filter (optional, e.g. -5.0 for -5%)
        market_type:    stock, crypto, forex, futures, bond, cfd (default: stock)
    """
    try:
        from tradingview_screener import Query, Column

        q = Query().select(
            "name",
            "close",
            "change",
            "change_abs",
            "volume",
            "market_cap_basic",
            "Recommend.All",
            "RSI",
            "MACD.macd",
            "BB.upper",
            "BB.lower",
            "exchange",
            "description",
            "type",
        )

        # Market type
        type_map = {
            "stock": "america",
            "crypto": "crypto",
            "forex": "forex",
            "futures": "america",
            "bond": "bond",
            "cfd": "cfd",
        }
        market = type_map.get(market_type.lower(), screener)
        q = q.set_markets(market)

        # Filters
        if min_volume is not None:
            q = q.where(Column("volume") >= min_volume)
        if min_change_pct is not None:
            q = q.where(Column("change") >= min_change_pct)
        if max_change_pct is not None:
            q = q.where(Column("change") <= max_change_pct)

        # Sort
        q = q.order_by(sort_by, ascending=(sort_order.lower() == "asc"))
        q = q.limit(min(limit, 50))

        result = q.get_scanner_data()
        count = result[0]
        rows = result[1]

        formatted = []
        for _, row in rows.iterrows():
            entry = row.to_dict()
            # Convert NaN to None for JSON
            entry = {k: (None if str(v) == "nan" else v) for k, v in entry.items()}
            formatted.append(entry)

        return json.dumps(
            {"total_matching": count, "results": formatted},
            indent=2,
            default=str,
        )
    except ImportError:
        return (
            "tradingview-screener is not installed. "
            "Run: pip install tradingview-screener"
        )
    except Exception as e:
        return f"Error running screener: {e}"


@mcp.tool()
async def get_price_data(
    symbol: str,
    exchange: str,
    screener: str = "america",
    interval: str = "5m",
) -> str:
    """Get current OHLCV price snapshot and key levels for a symbol.

    Returns open, high, low, close, volume, VWAP (via VWMA), daily pivots,
    Bollinger Bands, and % change.

    Args:
        symbol:   Ticker symbol (e.g. GC1!, NQ1!, AAPL)
        exchange: Exchange name (e.g. CME, COMEX, NASDAQ, BINANCE)
        screener: Market screener (default: america)
        interval: Timeframe (default: 5m)
    """
    keys = [
        "open", "high", "low", "close", "volume",
        "change", "change_abs",
        "VWMA",
        "BB.upper", "BB.lower",
        "Pivot.M.Classic.R1", "Pivot.M.Classic.R2", "Pivot.M.Classic.R3",
        "Pivot.M.Classic.S1", "Pivot.M.Classic.S2", "Pivot.M.Classic.S3",
        "Pivot.M.Classic.Middle",
        "P.SAR",
        "ATR",
        "EMA20", "EMA50", "EMA200",
    ]
    try:
        handler = _build_handler(symbol, exchange, screener, interval)
        analysis = handler.get_analysis()
        data = {k: analysis.indicators.get(k) for k in keys}
        data["symbol"] = analysis.symbol
        data["exchange"] = analysis.exchange
        data["interval"] = analysis.interval
        data["time"] = str(analysis.time)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error fetching price data for {symbol}: {e}"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main():
    """Run the MCP server (stdio transport by default)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
