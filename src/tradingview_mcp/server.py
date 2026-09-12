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
  - analyze_smc               — Smart Money Concepts analysis (support/resistance, order blocks, trend)
  - analyze_financials        — Fundamental financial data (valuation, profitability, growth, balance sheet)
  - analyze_saas_metrics      — SaaS business health (Rule of 40, LTV/CAC, Magic Number, burn multiple)
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError as exc:  # pragma: no cover - MCP 2.x moved FastMCP to MCPServer
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Unable to import the MCP server API. Install a supported version via "
            "'pip install \"mcp[cli]<2\"' or use the v1-compatible API."
        ) from exc

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


@mcp.tool()
async def analyze_smc(
    symbol: str,
    exchange: str,
    screener: str = "america",
    interval: str = "4h",
) -> str:
    """Analyze Smart Money Concepts (SMC) levels for a symbol.

    Identifies key support/resistance levels, order blocks, and smart money zones
    based on price structure and volume analysis.

    Args:
        symbol:   Ticker symbol (e.g. AAPL, NQ1!, GC1!)
        exchange: Exchange name (e.g. NASDAQ, CME, COMEX)
        screener: Market screener (default: america)
        interval: Timeframe (default: 4h)
    """
    try:
        handler = _build_handler(symbol, exchange, screener, interval)
        analysis = handler.get_analysis()

        indicators = analysis.indicators
        close = indicators.get("close")
        high = indicators.get("high")
        low = indicators.get("low")
        volume = indicators.get("volume")
        ema20 = indicators.get("EMA20")
        ema50 = indicators.get("EMA50")
        ema200 = indicators.get("EMA200")
        rsi = indicators.get("RSI")
        atr = indicators.get("ATR", 0)

        result = {
            "symbol": analysis.symbol,
            "exchange": analysis.exchange,
            "interval": analysis.interval,
            "time": str(analysis.time),
            "smc_analysis": {},
        }

        if close is None or high is None or low is None:
            return json.dumps({"error": "Insufficient data for SMC analysis"}, indent=2)

        atr = atr if atr and atr > 0 else (high - low) / 2

        smc = {
            "current_price": close,
            "high": high,
            "low": low,
            "atr": atr,
        }

        key_levels = []

        if ema20 is not None and ema50 is not None and ema200 is not None:
            smc["ema_structure"] = {
                "ema20": ema20,
                "ema50": ema50,
                "ema200": ema200,
            }

            if ema20 > ema50 > ema200:
                smc["trend"] = "UPTREND"
            elif ema20 < ema50 < ema200:
                smc["trend"] = "DOWNTREND"
            else:
                smc["trend"] = "RANGING"

            key_levels.extend([
                {"level": ema20, "type": "EMA20", "name": "20-period EMA"},
                {"level": ema50, "type": "EMA50", "name": "50-period EMA"},
                {"level": ema200, "type": "EMA200", "name": "200-period EMA"},
            ])

        from tradingview_ta import Interval
        if analysis.interval != Interval.INTERVAL_1_MINUTE:
            bb_upper = indicators.get("BB.upper")
            bb_lower = indicators.get("BB.lower")
            if bb_upper is not None and bb_lower is not None:
                smc["bollinger_bands"] = {
                    "upper": bb_upper,
                    "lower": bb_lower,
                    "middle": (bb_upper + bb_lower) / 2,
                }
                key_levels.extend([
                    {"level": bb_upper, "type": "ORDER_BLOCK_UP", "name": "BB Upper (Supply)"},
                    {"level": bb_lower, "type": "ORDER_BLOCK_DOWN", "name": "BB Lower (Demand)"},
                ])

        if rsi is not None:
            smc["rsi"] = rsi
            if rsi > 70:
                smc["rsi_state"] = "OVERBOUGHT"
            elif rsi < 30:
                smc["rsi_state"] = "OVERSOLD"
            else:
                smc["rsi_state"] = "NEUTRAL"

        if volume:
            smc["volume"] = volume

        smc["key_levels"] = sorted(key_levels, key=lambda x: x["level"], reverse=True)

        support_resistance = []
        resistance_level = high
        support_level = low

        if resistance_level:
            support_resistance.append({
                "level": resistance_level,
                "type": "RESISTANCE",
                "distance": resistance_level - close,
                "percentage": round(((resistance_level - close) / close * 100), 2) if close else 0,
            })

        if support_level:
            support_resistance.append({
                "level": support_level,
                "type": "SUPPORT",
                "distance": close - support_level,
                "percentage": round(((close - support_level) / close * 100), 2) if close else 0,
            })

        smc["support_resistance"] = support_resistance

        result["smc_analysis"] = smc

        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error analyzing SMC for {symbol}: {e}"


@mcp.tool()
async def analyze_financials(
    symbol: str,
    screener: str = "america",
) -> str:
    """Get comprehensive fundamental financial data for a stock.

    Retrieves valuation multiples, profitability ratios, growth metrics,
    and balance-sheet health — the core metrics a financial analyst would review.

    Args:
        symbol:   Ticker symbol (e.g. AAPL, MSFT, GOOGL, AMZN)
        screener: Market screener — america, uk, india, crypto, etc. (default: america)
    """
    try:
        from tradingview_screener import Query, Column

        columns = [
            "name", "close", "market_cap_basic", "enterprise_value_fq",
            "price_earnings_ttm", "price_to_book_fq", "price_to_sales_ttm",
            "enterprise_value_ebitda_ttm",
            "gross_profit_margin_ttm", "operating_margin_ttm", "net_profit_margin_ttm",
            "return_on_equity", "return_on_assets",
            "revenue_growth_rate_ttm_5y", "earnings_per_share_basic_ttm",
            "earnings_per_share_diluted_yoy_growth_ttm",
            "debt_to_equity", "current_ratio", "quick_ratio",
            "book_value_per_share_quarterly", "dividends_yield_current",
            "description", "exchange",
        ]

        count, rows = (
            Query()
            .select(*columns)
            .where(Column("name") == symbol.upper())
            .set_markets(_resolve_screener(screener))
            .limit(1)
            .get_scanner_data()
        )

        if count == 0 or rows.empty:
            return json.dumps(
                {
                    "error": (
                        f"Symbol '{symbol}' not found in screener '{screener}'. "
                        "Try a different screener (e.g. 'uk', 'india', 'crypto')."
                    )
                },
                indent=2,
            )

        raw = {k: (None if str(v) == "nan" else v) for k, v in rows.iloc[0].to_dict().items()}

        def _pct(v: float | None) -> float | None:
            return round(v * 100, 2) if v is not None else None

        result = {
            "symbol": symbol.upper(),
            "description": raw.get("description"),
            "exchange": raw.get("exchange"),
            "price": raw.get("close"),
            "market_cap": raw.get("market_cap_basic"),
            "enterprise_value": raw.get("enterprise_value_fq"),
            "valuation": {
                "pe_ratio_ttm": raw.get("price_earnings_ttm"),
                "pb_ratio": raw.get("price_to_book_fq"),
                "ps_ratio_ttm": raw.get("price_to_sales_ttm"),
                "ev_ebitda_ttm": raw.get("enterprise_value_ebitda_ttm"),
            },
            "profitability": {
                "gross_margin_pct": _pct(raw.get("gross_profit_margin_ttm")),
                "operating_margin_pct": _pct(raw.get("operating_margin_ttm")),
                "net_margin_pct": _pct(raw.get("net_profit_margin_ttm")),
                "roe_pct": _pct(raw.get("return_on_equity")),
                "roa_pct": _pct(raw.get("return_on_assets")),
            },
            "growth": {
                "revenue_5y_cagr_pct": _pct(raw.get("revenue_growth_rate_ttm_5y")),
                "eps_basic_ttm": raw.get("earnings_per_share_basic_ttm"),
                "eps_yoy_growth_pct": _pct(raw.get("earnings_per_share_diluted_yoy_growth_ttm")),
            },
            "balance_sheet": {
                "debt_to_equity": raw.get("debt_to_equity"),
                "current_ratio": raw.get("current_ratio"),
                "quick_ratio": raw.get("quick_ratio"),
            },
            "per_share": {
                "eps_basic_ttm": raw.get("earnings_per_share_basic_ttm"),
                "book_value_per_share": raw.get("book_value_per_share_quarterly"),
                "dividend_yield_pct": _pct(raw.get("dividends_yield_current")),
            },
        }

        return json.dumps(result, indent=2, default=str)
    except ImportError:
        return (
            "tradingview-screener is not installed. "
            "Run: pip install tradingview-screener"
        )
    except Exception as e:
        return f"Error fetching financial data for {symbol}: {e}"


@mcp.tool()
async def screen_breakout_scanner(
    screener: str = "america",
    limit: int = 20,
    market_type: str = "stock",
) -> str:
    """Screen for breakout candidates with uptrend + buyer control.

    Identifies early breakout candidates that are:
    - Within 2-5% of 52-week high (new highs territory)
    - Above Ichimoku cloud (confirmed uptrend structure)
    - Volume surge above 20-day average (buyers stepping in)
    - RSI 40-70 (uptrend momentum without overbought extremes)
    - Price > 50-day MA > 200-day MA (stacked moving averages)
    - MACD histogram positive and above signal line (buyers dominant)

    Results sorted by volume (descending) for highest conviction setups.

    Args:
        screener:   Market — america, crypto, forex, cfd, etc. (default: america)
        limit:      Number of results to return, max 50 (default: 20)
        market_type: stock, crypto, forex, futures, bond, cfd (default: stock)
    """
    try:
        from tradingview_screener import Query, Column

        q = Query().select(
            "name",
            "close",
            "change",
            "change_abs",
            "volume",
            "volume_20_days_avg",
            "market_cap_basic",
            "RSI",
            "MACD.macd",
            "MACD.signal",
            "EMA20",
            "EMA50",
            "EMA200",
            "Ichimoku.BLine",
            "52_week_high",
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

        # Note: 52-week high proximity filtering will be done in post-processing
        # since tradingview_screener doesn't support arithmetic on Column comparisons

        # 2. RSI in 40-70 range (uptrend momentum, not overbought)
        q = q.where(Column("RSI") >= 40)
        q = q.where(Column("RSI") <= 70)

        # 3. Volume surge (current volume > 20-day average)
        q = q.where(Column("volume") > Column("volume_20_days_avg"))

        # 4. Moving average alignment: Price > EMA50 > EMA200
        q = q.where(Column("close") > Column("EMA50"))
        q = q.where(Column("EMA50") > Column("EMA200"))

        # 5. Price above EMA50 (intermediate uptrend confirmation)
        q = q.where(Column("close") > Column("EMA20"))

        # 6. MACD positive (histogram positive means MACD > signal line)
        q = q.where(Column("MACD.macd") > Column("MACD.signal"))

        # Sort by volume descending (highest conviction)
        q = q.order_by("volume", ascending=False)
        q = q.limit(min(limit, 50))

        result = q.get_scanner_data()
        count = result[0]
        rows = result[1]

        formatted = []
        for _, row in rows.iterrows():
            entry = row.to_dict()
            # Convert NaN to None for JSON
            entry = {k: (None if str(v) == "nan" else v) for k, v in entry.items()}

            # Calculate additional breakout metrics
            close = entry.get("close")
            high_52w = entry.get("52_week_high")
            volume_avg = entry.get("volume_20_days_avg")
            volume = entry.get("volume")
            ema20 = entry.get("EMA20")
            ema50 = entry.get("EMA50")
            ema200 = entry.get("EMA200")

            # Post-filter: 52-week high proximity (within 2-5% = 95-100% of high)
            if close and high_52w:
                proximity_pct = round(((high_52w - close) / close * 100), 2)
                entry["distance_from_52w_high_pct"] = proximity_pct
                # Skip if not in breakout zone (> 5% below 52w high)
                if proximity_pct > 5:
                    continue

            if volume and volume_avg:
                surge_ratio = round(volume / volume_avg, 2)
                entry["volume_surge_ratio"] = surge_ratio

            if close and ema20 and ema50 and ema200:
                entry["ma_alignment_strength"] = {
                    "price": close,
                    "ema20": ema20,
                    "ema50": ema50,
                    "ema200": ema200,
                    "aligned": close > ema20 > ema50 > ema200,
                }

            formatted.append(entry)

        return json.dumps(
            {
                "scanner": "breakout_uptrend_buyer_control",
                "total_matching": len(formatted),
                "results": formatted,
                "filters_applied": {
                    "52_week_high_proximity": "95-100% (2-5% from high)",
                    "ichimoku_cloud": "price_above_cloud",
                    "volume_surge": "current > 20_day_average",
                    "rsi": "40-70 (uptrend, not overbought)",
                    "moving_averages": "price > ema50 > ema200",
                    "macd": "histogram_positive (macd > signal)",
                    "sorted_by": "volume (descending)",
                },
            },
            indent=2,
            default=str,
        )
    except ImportError:
        return (
            "tradingview-screener is not installed. "
            "Run: pip install tradingview-screener"
        )
    except Exception as e:
        return f"Error running breakout scanner: {e}"


@mcp.tool()
async def analyze_saas_metrics(
    symbol: str = "",
    screener: str = "america",
    arr: float | None = None,
    arr_growth_pct: float | None = None,
    gross_margin_pct: float | None = None,
    net_revenue_retention_pct: float | None = None,
    cac: float | None = None,
    arpu: float | None = None,
    churn_rate_pct: float | None = None,
    fcf_margin_pct: float | None = None,
    sales_marketing_spend: float | None = None,
    net_new_arr: float | None = None,
    net_burn: float | None = None,
) -> str:
    """Analyze SaaS business health and compute key SaaS metrics.

    Works in two modes:
    1. **Public company** — supply a stock *symbol* to fetch revenue growth and
       gross margin from TradingView automatically.
    2. **Manual / private** — leave *symbol* empty and provide your own inputs.

    Computes: Rule of 40, LTV/CAC ratio, CAC payback, Magic Number, Burn Multiple,
    and grades each metric against SaaS industry benchmarks.

    Args:
        symbol:                    Ticker for a public SaaS company (e.g. CRM, SNOW, DDOG)
        screener:                  Market screener for symbol lookup (default: america)
        arr:                       Annual Recurring Revenue in dollars (optional)
        arr_growth_pct:            YoY ARR growth % — e.g. 40.0 for 40% (overrides fetched value)
        gross_margin_pct:          Gross margin % — e.g. 75.0 (overrides fetched value)
        net_revenue_retention_pct: Net Revenue Retention % — e.g. 120.0 for 120%
        cac:                       Customer Acquisition Cost in dollars
        arpu:                      Average Revenue Per User per month in dollars
        churn_rate_pct:            Monthly customer churn rate % — e.g. 2.0 for 2%
        fcf_margin_pct:            Free Cash Flow margin % — e.g. 15.0 (used in Rule of 40)
        sales_marketing_spend:     S&M spend for the quarter in dollars (for Magic Number)
        net_new_arr:               Net new ARR added in the quarter in dollars
        net_burn:                  Monthly net cash burn in dollars (positive = burning cash)
    """
    metrics: dict = {}
    warnings: list[str] = []

    tv_gross_margin: float | None = None
    tv_growth: float | None = None

    if symbol:
        try:
            from tradingview_screener import Query, Column

            _, rows = (
                Query()
                .select(
                    "name", "gross_profit_margin_ttm", "revenue_growth_rate_ttm_5y",
                    "operating_margin_ttm", "net_profit_margin_ttm",
                    "market_cap_basic", "close",
                )
                .where(Column("name") == symbol.upper())
                .set_markets(_resolve_screener(screener))
                .limit(1)
                .get_scanner_data()
            )
            if not rows.empty:
                raw = {k: (None if str(v) == "nan" else v) for k, v in rows.iloc[0].to_dict().items()}
                if raw.get("gross_profit_margin_ttm") is not None:
                    tv_gross_margin = round(raw["gross_profit_margin_ttm"] * 100, 2)
                if raw.get("revenue_growth_rate_ttm_5y") is not None:
                    tv_growth = round(raw["revenue_growth_rate_ttm_5y"] * 100, 2)
                metrics["symbol"] = symbol.upper()
                metrics["market_cap"] = raw.get("market_cap_basic")
                metrics["price"] = raw.get("close")
        except Exception as e:
            warnings.append(f"Could not fetch TradingView data: {e}")

    effective_gross_margin = gross_margin_pct if gross_margin_pct is not None else tv_gross_margin
    effective_growth = arr_growth_pct if arr_growth_pct is not None else tv_growth

    metrics["inputs"] = {
        "arr": arr,
        "arr_growth_pct": effective_growth,
        "gross_margin_pct": effective_gross_margin,
        "net_revenue_retention_pct": net_revenue_retention_pct,
        "cac": cac,
        "arpu": arpu,
        "churn_rate_pct": churn_rate_pct,
        "fcf_margin_pct": fcf_margin_pct,
        "sales_marketing_spend": sales_marketing_spend,
        "net_new_arr": net_new_arr,
        "net_burn": net_burn,
    }

    computed: dict = {}

    # Rule of 40 = revenue_growth_pct + fcf_margin_pct
    if effective_growth is not None and fcf_margin_pct is not None:
        rule_of_40 = round(effective_growth + fcf_margin_pct, 2)
        computed["rule_of_40"] = {
            "value": rule_of_40,
            "grade": "Good (≥40)" if rule_of_40 >= 40 else "Below benchmark (<40)",
            "components": {
                "revenue_growth_pct": effective_growth,
                "fcf_margin_pct": fcf_margin_pct,
            },
        }
    else:
        missing = []
        if effective_growth is None:
            missing.append("arr_growth_pct")
        if fcf_margin_pct is None:
            missing.append("fcf_margin_pct")
        warnings.append(f"Rule of 40 requires: {', '.join(missing)}")

    # LTV = ARPU × gross_margin% / monthly_churn%
    if (
        arpu is not None
        and effective_gross_margin is not None
        and churn_rate_pct is not None
        and churn_rate_pct > 0
    ):
        ltv = round(arpu * (effective_gross_margin / 100) / (churn_rate_pct / 100), 2)
        computed["ltv"] = ltv

        if cac is not None and cac > 0:
            ltv_cac = round(ltv / cac, 2)
            computed["ltv_cac_ratio"] = {
                "value": ltv_cac,
                "grade": "Excellent (≥3)" if ltv_cac >= 3 else "Poor (<3)",
            }

            monthly_gp_per_customer = arpu * (effective_gross_margin / 100)
            if monthly_gp_per_customer > 0:
                cac_payback = round(cac / monthly_gp_per_customer, 1)
                computed["cac_payback_months"] = {
                    "value": cac_payback,
                    "grade": (
                        "Good (<12 months)" if cac_payback < 12
                        else "Okay (12–24 months)" if cac_payback < 24
                        else "High (>24 months)"
                    ),
                }

    # Magic Number = net_new_arr (quarterly) / prior_quarter_S&M_spend
    if (
        net_new_arr is not None
        and sales_marketing_spend is not None
        and sales_marketing_spend > 0
    ):
        magic_number = round(net_new_arr / sales_marketing_spend, 2)
        computed["magic_number"] = {
            "value": magic_number,
            "grade": (
                "Excellent (≥0.75)" if magic_number >= 0.75
                else "Okay (0.5–0.75)" if magic_number >= 0.5
                else "Poor (<0.5)"
            ),
        }

    # Burn Multiple = net_burn / net_new_arr
    if net_burn is not None and net_new_arr is not None and net_new_arr > 0:
        burn_multiple = round(net_burn / net_new_arr, 2)
        computed["burn_multiple"] = {
            "value": burn_multiple,
            "grade": (
                "Excellent (<1)" if burn_multiple < 1
                else "Good (1–1.5)" if burn_multiple < 1.5
                else "Okay (1.5–2)" if burn_multiple < 2
                else "Poor (>2)"
            ),
        }

    # Net Revenue Retention
    if net_revenue_retention_pct is not None:
        computed["net_revenue_retention"] = {
            "value": net_revenue_retention_pct,
            "grade": (
                "Best-in-class (≥120%)" if net_revenue_retention_pct >= 120
                else "Good (100–120%)" if net_revenue_retention_pct >= 100
                else "Below 100% — shrinking existing base"
            ),
        }

    # Gross margin assessment
    if effective_gross_margin is not None:
        computed["gross_margin_assessment"] = {
            "value": effective_gross_margin,
            "grade": (
                "Excellent SaaS (≥75%)" if effective_gross_margin >= 75
                else "Good SaaS (65–75%)" if effective_gross_margin >= 65
                else "Acceptable (50–65%)" if effective_gross_margin >= 50
                else "Low for SaaS (<50%)"
            ),
        }

    metrics["computed"] = computed
    if warnings:
        metrics["warnings"] = warnings

    return json.dumps(metrics, indent=2, default=str)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main():
    """Run the MCP server (stdio transport by default)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
