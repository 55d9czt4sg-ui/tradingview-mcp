# Usage Examples & Workflows

This guide provides detailed examples of how to use the TradingView MCP Server for real-world analysis tasks.

## Table of Contents

- [Stock Analysis](#stock-analysis)
  - [Example 1: Daily Chart Review (AAPL)](#example-1-daily-chart-review-aapl)
  - [Example 2: Multi-Timeframe Confluence (TSLA)](#example-2-multi-timeframe-confluence-tsla)
  - [Example 3: Finding Support & Resistance (SPY)](#example-3-finding-support--resistance-spy)
  - [Example 4: Smart Money Concepts Analysis (RVMD)](#example-4-smart-money-concepts-analysis-rvmd)
  - [Example 5: Screening for Quality Stocks](#example-5-screening-for-quality-stocks)
- [Crypto Trading](#crypto-trading)
- [Futures Analysis](#futures-analysis)
- [Market Screening](#market-screening)
- [Advanced Workflows](#advanced-workflows)

---

## Stock Analysis

### Example 1: Daily Chart Review (AAPL)

**Question to AI:**
> "Analyze Apple (AAPL) on the daily chart. Is it a buy or sell right now?"

**How the AI Uses the Tools:**
1. Calls `get_technical_analysis(symbol="AAPL", exchange="NASDAQ", screener="america", interval="1d")`
2. Retrieves BUY/SELL/NEUTRAL recommendation
3. Checks oscillators (RSI, MACD, Stochastic) and moving averages

**Expected Response:**
```
AAPL is currently showing NEUTRAL signals on the daily chart.
- The RSI is at 55 (neither overbought nor oversold)
- The MACD is bullish with the line above signal
- Moving averages: Price is above EMA20 and EMA50, but below EMA200
- Overall: Wait for a break above the 200-day EMA for a strong buy signal
```

### Example 2: Multi-Timeframe Confluence (TSLA)

**Question to AI:**
> "Check Tesla (TSLA) across multiple timeframes: 5m, 15m, 1h, and 4h. Are they aligned?"

**How the AI Uses the Tools:**
1. Calls `get_multi_timeframe(symbol="TSLA", exchange="NASDAQ", intervals="5m,15m,1h,4h")`
2. Compares signals across all timeframes
3. Identifies confluence (alignment) or divergence

**Expected Response:**
```
TSLA Multi-Timeframe Analysis:
- 5m: SELL (downtrend, RSI overbought)
- 15m: NEUTRAL (consolidating)
- 1h: BUY (bullish cross above 50 EMA)
- 4h: BUY (strong uptrend)

Analysis: The 1h and 4h show buy signals, but the 5m is overextended.
Best action: Wait for a 5m pullback or entry confirmation on higher timeframes.
```

### Example 3: Finding Support & Resistance (SPY)

**Question to AI:**
> "Get the current price, pivot points, and Bollinger Bands for SPY (S&P 500 ETF). Where are support and resistance?"

**How the AI Uses the Tools:**
1. Calls `get_price_data(symbol="SPY", exchange="NYSE", interval="1d")`
2. Retrieves OHLCV, pivot levels, Bollinger Bands, and key indicators

**Expected Response:**
```
SPY Current Analysis (Daily):
- Price: $425.50
- Pivot Point (Middle): $424.75
- Resistance: R1: $427.20 | R2: $429.50 | R3: $431.85
- Support: S1: $422.40 | S2: $420.10 | S3: $417.75
- Bollinger Bands: Upper: $430.20 | Lower: $418.80
- Trend: Price near middle pivot, room to R1 resistance

Trading Plan: Watch $427.20 (R1) for resistance. Support at $422.40 (S1).
```

### Example 4: Smart Money Concepts Analysis (RVMD)

**Question to AI:**
> "Analyze RVMD (Revere Copper & Gold) on the 4-hour chart using Smart Money Concepts. Where are the key support/resistance levels and order blocks?"

**How the AI Uses the Tools:**
1. Calls `analyze_smc(symbol="RVMD", exchange="NASDAQ", interval="4h")`
2. Identifies smart money zones, order blocks, and structural levels
3. Analyzes EMA structure for trend confirmation

**Expected Response:**
```
RVMD Smart Money Concepts Analysis (4-Hour Chart):

CURRENT STRUCTURE:
- Price: $8.45
- Daily Range: High $8.75 | Low $8.10 | ATR: $0.32
- Trend: UPTREND (EMA20 > EMA50 > EMA200)

EMA STRUCTURE (Trend Confirmation):
- EMA20: $8.32 (price above = bullish)
- EMA50: $8.18 (intact uptrend)
- EMA200: $8.02 (long-term support holding)

SMART MONEY ZONES (Order Blocks):
1. Supply Block (Upper): $8.75 (Bollinger Band upper = resistance)
   - Smart money resistance where sellers control
   - Previous high where institutional selling occurred
   
2. Demand Block (Lower): $8.10 (Bollinger Band lower = support)
   - Smart money support where buyers stepped in
   - Previous low where institutional accumulation likely

KEY LEVELS (Sorted by Price):
- $8.75 — RESISTANCE (Order Block Supply)
- $8.32 — EMA20 (Dynamic Support)
- $8.18 — EMA50 (Support)
- $8.10 — SUPPORT (Order Block Demand)
- $8.02 — EMA200 (Long-term Support)

MOMENTUM INDICATORS:
- RSI: 62 (NEUTRAL — healthy momentum, not overbought)
- Volume: 2.3M (solid buying support)

SMC TRADING INTERPRETATION:
1. Price is above all key EMAs = Uptrend intact
2. EMA20 acting as dynamic support = Bulls in control
3. Demand block at $8.10 holding = Smart money buying zone
4. Supply block at $8.75 = Next resistance to break

TRADING SETUP:
- Long Setup: Buy pullback to EMA20 ($8.32) with target at $8.75 (supply block breakout)
- Stop Loss: Below EMA50 at $8.18 (uptrend confirmation break)
- Risk: $0.14 | Reward: $0.43 | Ratio: 3:1 (favorable)

SMART MONEY SIGNAL: 
Institutional buyers have defended the $8.10 level (demand block).
As long as price holds above EMA20, the uptrend bias remains bullish.
Watch for a break above $8.75 as the next smart money target.
```

### Example 5: Screening for Quality Stocks

**Question to AI:**
> "Find US stocks with volume over 2 million that are up more than 3% today. Sort by volume."

**How the AI Uses the Tools:**
1. Calls `screen_market(screener="america", market_type="stock", min_volume=2000000, min_change_pct=3.0, sort_by="volume", limit=10)`
2. Returns top 10 active gainers with technical signals

**Expected Response:**
```
Top 10 US Stocks: Volume > 2M, Up > 3% Today

1. XYZ Corp (NYSE: XYZ) | Price: $45.20 | Change: +5.2% | Volume: 8.5M
   RSI: 72 (overbought) | Recommendation: NEUTRAL (pullback expected)

2. ABC Inc (NASDAQ: ABC) | Price: $123.40 | Change: +4.1% | Volume: 5.2M
   RSI: 68 (near overbought) | Recommendation: BUY

3. DEF Ltd (NYSE: DEF) | Price: $78.90 | Change: +3.8% | Volume: 3.1M
   ...

Action: ABC and DEF show better buy signals than XYZ (which is overbought).
```

---

## Crypto Trading

### Example 1: Bitcoin 4-Hour Trend

**Question to AI:**
> "What's the technical analysis for Bitcoin (BTCUSDT) on Binance on the 4-hour chart?"

**How the AI Uses the Tools:**
1. Calls `get_technical_analysis(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval="4h")`
2. Retrieves BUY/SELL signals and key indicators

**Expected Response:**
```
BTCUSDT (4-Hour Chart):
- Recommendation: BUY
- RSI: 58 (neutral, room to go up)
- MACD: Bullish (histogram above zero)
- Moving Averages: Price above EMA20, EMA50, EMA200 (strong uptrend)
- BB: Price in middle band, room to upper band

Action: Strong uptrend. Buy on pullback to EMA20 or continue if breakout occurs.
```

### Example 2: Crypto Gainers Screening

**Question to AI:**
> "Show me the top 10 crypto gainers today with RSI above 60 (strong momentum)."

**How the AI Uses the Tools:**
1. Calls `screen_market(screener="crypto", sort_by="change", sort_order="desc", limit=10)`
2. Filters results where RSI > 60

**Expected Response:**
```
Top Crypto Gainers (24h):

1. ETHUSDT (Ethereum) | Price: $2,450 | Change: +12.3% | RSI: 68
   Volume: 150K BTC | Status: OVERBOUGHT (caution on new buys)

2. BNBUSDT (Binance Coin) | Price: $620 | Change: +8.5% | RSI: 64
   Volume: 85K BTC | Status: Strong momentum, good for breakout

3. ADAUSDT (Cardano) | Price: $1.20 | Change: +7.2% | RSI: 62
   ...

Opportunity: BNBUSDT and ADAUSDT show momentum without extreme overbought levels.
```

### Example 3: Volatility Analysis (ETH 5-Minute)

**Question to AI:**
> "Get the current price, ATR (volatility), and Bollinger Bands for Ethereum (ETHUSDT) on the 5-minute chart for intraday trading."

**How the AI Uses the Tools:**
1. Calls `get_price_data(symbol="ETHUSDT", exchange="BINANCE", interval="5m")`
2. Retrieves ATR, BB width, and current levels

**Expected Response:**
```
ETHUSDT (5-Min Chart) - Volatility Check:
- Current Price: $2,445.50
- ATR (Average True Range): $8.20 (14-period)
- Bollinger Bands: Upper $2,458 | Middle $2,445 | Lower $2,432
- Band Width: ~$26 (moderate volatility)

Analysis:
- ATR ~$8 suggests good intraday swing opportunity
- Price near middle band = no extreme
- Best setup: Range-bound trading $2,432 to $2,458

Entry: Buy at lower band ($2,432), sell at upper band ($2,458). Risk: $16.
```

---

## Futures Analysis

### Example 1: Nasdaq Futures Multi-Timeframe (NQ1!)

**Question to AI:**
> "Analyze Nasdaq 100 futures (NQ1!) on the CME. Check 1-hour and 4-hour charts. Is it a buy?"

**How the AI Uses the Tools:**
1. Calls `get_multi_timeframe(symbol="NQ1!", exchange="CME", intervals="1h,4h")`
2. Compares signals across both timeframes

**Expected Response:**
```
NQ1! (Nasdaq 100 Futures) Analysis:

1-Hour Chart:
- Recommendation: BUY
- RSI: 62 (bullish, not overbought)
- MACD: Positive crossover
- Trend: Above all key MAs (EMA20, EMA50)

4-Hour Chart:
- Recommendation: BUY (STRONGER signal)
- RSI: 55 (neutral, room to go up)
- MACD: Strong bullish
- Trend: In strong uptrend, well above EMA200

Confluence: Both timeframes are BULLISH. The 4-hour is the dominant trend.
Action: BUY with 1h pullback as entry, 4h trend as confirmation. Stop below 4h EMA20.
```

### Example 2: Gold Futures Volatility (GC1!)

**Question to AI:**
> "Get current price, pivots, and ATR for gold futures (GC1!) on COMEX on the daily chart."

**How the AI Uses the Tools:**
1. Calls `get_price_data(symbol="GC1!", exchange="COMEX", interval="1d")`
2. Retrieves price levels, pivots, and volatility (ATR)

**Expected Response:**
```
GC1! (Gold Futures, Daily):
- Current Price: $2,045.50
- ATR (14-day): $18.75 (moderate volatility)
- Pivots:
  - Resistance: R1 $2,062 | R2 $2,080 | R3 $2,097
  - Support: S1 $2,028 | S2 $2,010 | S3 $1,993
- Bollinger Bands: Upper $2,085 | Lower $2,005

Trading Levels:
- Strong Support: $2,010 (Pivot S2)
- First Target: $2,062 (R1)
- Extended Target: $2,080 (R2)
- Stop Loss (if shorting): Above $2,097 (R3)

Action: Gold near pivot middle. Bias depends on broader market (equity downside = gold up).
```

### Example 3: S&P 500 Futures Trend (ES1!)

**Question to AI:**
> "Is the S&P 500 futures (ES1!) in an uptrend or downtrend right now? Check multiple timeframes."

**How the AI Uses the Tools:**
1. Calls `get_multi_timeframe(symbol="ES1!", exchange="CME", intervals="5m,15m,1h,4h,1d")`
2. Identifies trend across all timeframes

**Expected Response:**
```
ES1! (S&P 500 Futures) - Trend Analysis:

Timeframe Breakdown:
- 5m: SELL (pullback, oversold RSI)
- 15m: NEUTRAL (consolidating)
- 1h: BUY (above EMA20, RSI 60)
- 4h: BUY (strong uptrend, EMA20 > EMA50 > EMA200)
- 1d: BUY (daily uptrend intact)

Trend Hierarchy:
1. Daily (4h/1d) = STRONG UPTREND
2. Hourly (1h) = Bullish
3. Short-term (5m/15m) = Weak/Pullback

Action: The market is in a strong daily uptrend. The 5m pullback is a buying opportunity
within the larger uptrend. Buy on 5m strength, targeting 1h resistance.
```

---

## Market Screening

### Example 1: Find Oversold Stocks (RSI < 30)

**Question to AI:**
> "Screen for US stocks with RSI below 30 (oversold) and volume over 1 million. These might be reversal candidates."

**How the AI Uses the Tools:**
1. Calls `screen_market(screener="america", sort_by="RSI", sort_order="asc", min_volume=1000000, limit=15)`
2. Returns stocks sorted by lowest RSI first (most oversold)

**Expected Response:**
```
Oversold US Stocks (RSI < 30, Volume > 1M):

1. PLTR (Palantir) | Price: $18.50 | RSI: 22 | Volume: 45M
   Change: -8.2% | Status: HEAVILY OVERSOLD - Watch for reversal

2. COIN (Coinbase) | Price: $95.20 | RSI: 25 | Volume: 12M
   Change: -7.5% | Status: Oversold, potential bounce

3. RIOT (Riot Blockchain) | Price: $12.30 | RSI: 28 | Volume: 8.5M
   Change: -6.1% | Status: Approaching oversold, watch for support

Trading Strategy:
- Oversold stocks often bounce (mean reversion)
- Watch for confirmation: RSI bounce + price support hold
- Best trades: Combine with chart support levels and higher timeframe trends
```

### Example 2: Find High-Volume Breakout Candidates

**Question to AI:**
> "Find stocks that are up more than 2% today with volume above 3 million. Sort by volume—these might be breakouts."

**How the AI Uses the Tools:**
1. Calls `screen_market(screener="america", min_change_pct=2.0, min_volume=3000000, sort_by="volume", sort_order="desc", limit=10)`
2. Returns highest-volume gainers (potential breakouts)

**Expected Response:**
```
High-Volume Gainers (Up > 2%, Volume > 3M):

1. NVDA (NVIDIA) | Price: $875.50 | Volume: 52M | Change: +3.2%
   RSI: 65 | Recommendation: NEUTRAL (overbought on day, but uptrend intact)
   → Strong breakout on high volume, but overbought intraday

2. AVGO (Broadcom) | Price: $165.20 | Volume: 18M | Change: +2.5%
   RSI: 58 | Recommendation: BUY
   → Clean breakout on solid volume, room to go higher

3. AMD (Advanced Micro Devices) | Price: $142.80 | Volume: 15M | Change: +2.1%
   RSI: 61 | Recommendation: BUY
   → Momentum building, gap up breakout

Trading Action:
- AVGO and AMD are cleaner breakout plays (not overbought)
- Avoid NVDA intraday (overbought RSI), but could be long-term buy
- Watch for these to hold above support after initial move
```

### Example 3: Crypto Momentum Screen

**Question to AI:**
> "Show me the crypto market leaders today—top 5 gainers with strong technical signals (RSI 50-70)."

**How the AI Uses the Tools:**
1. Calls `screen_market(screener="crypto", sort_by="change", sort_order="desc", limit=20)`
2. Filters for RSI between 50–70 (momentum without overbought extremes)
3. Returns top 5 cleanest momentum plays

**Expected Response:**
```
Top Crypto Momentum Plays (50 < RSI < 70):

1. SOL (Solana) | $185.40 | Change: +18.2% | RSI: 68
   Volume: 450K BTC | Status: Strong momentum, near overbought
   Action: WATCH for pullback entry; momentum is intact but caution on new longs

2. BNBUSDT (Binance) | $625.80 | Change: +12.5% | RSI: 62
   Volume: 95K BTC | Status: Clean momentum
   Action: BUY breakouts, pullback support at EMA20

3. AVAXUSDT (Avalanche) | $58.20 | Change: +10.3% | RSI: 59
   Volume: 28K BTC | Status: Strong momentum building
   Action: Good risk/reward, follow the trend

Portfolio Strategy: These are trend-following plays. Use 1d/4h charts as reference,
enter on 1h/15m pullbacks. Avoid chasing at RSI extremes.
```

---

## Advanced Workflows

### Workflow 1: Complete Trading Setup Analysis

**Goal:** Set up a complete trade with entry, target, and stop loss

**Question to AI:**
> "I want to trade Apple (AAPL). Give me:
> 1. Current technical setup (daily + 1h)
> 2. Entry price and confirmation signal
> 3. Profit target and support/resistance levels
> 4. Stop loss level
> 5. Risk/reward ratio"

**How the AI Uses the Tools:**
1. `get_multi_timeframe(symbol="AAPL", exchange="NASDAQ", intervals="1h,1d")`
2. `get_price_data(symbol="AAPL", exchange="NASDAQ", interval="1d")`
3. `get_indicator_values(symbol="AAPL", exchange="NASDAQ", interval="1h", indicators="RSI,MACD.macd,BB.upper,BB.lower,EMA20,EMA50")`

**Expected Response:**
```
AAPL Trading Setup:

CURRENT SETUP:
- Daily: BUY (above EMA20, EMA50, EMA200)
- Hourly: BUY (RSI 62, MACD positive, above EMA20)
- Price: $182.50 | Daily Pivots: S1 $180.00 | R1 $186.00

ENTRY:
- Conservative: $182.00 (daily support + confirmation)
- Aggressive: $182.50 (break above hourly resistance)
- Confirmation: RSI > 55 and MACD histogram positive

PROFIT TARGETS:
- Target 1: $186.00 (daily R1)
- Target 2: $188.50 (4-hour resistance)
- Target 3: $192.00 (previous swing high)

STOP LOSS:
- Hard Stop: $180.00 (daily support S1) = Risk $2.50/share
- Trailing Stop: Adjust to EMA20 (currently at $181.20)

RISK/REWARD:
- Entry to Stop: $2.50 risk
- Entry to Target 1: $3.50 gain = 1.4:1 ratio
- Entry to Target 2: $6.00 gain = 2.4:1 ratio ← GOOD
- Entry to Target 3: $9.50 gain = 3.8:1 ratio

TRADE PLAN:
1. Buy AAPL at $182.00–$182.50 on hourly pullback
2. Stop loss at $180.00
3. Take profit at $186 (50%), $188.50 (30%), $192 (20%)
4. Trailing stop for remainder after $186 breakout
```

### Workflow 2: Market Regime Analysis

**Goal:** Understand the overall market regime (bullish, bearish, sideways)

**Question to AI:**
> "Analyze the S&P 500 (SPY), Nasdaq (QQQ), and bond ETF (TLT) to determine the market regime. Are we in risk-on or risk-off mode?"

**How the AI Uses the Tools:**
1. `get_multi_timeframe(symbol="SPY", exchange="NYSE", intervals="1d,4h")`
2. `get_multi_timeframe(symbol="QQQ", exchange="NASDAQ", intervals="1d,4h")`
3. `get_multi_timeframe(symbol="TLT", exchange="NASDAQ", intervals="1d")`
4. Compare: If stocks up & bonds down = risk-on. If stocks down & bonds up = risk-off.

**Expected Response:**
```
MARKET REGIME ANALYSIS:

US Equities:
- SPY (Large Cap): BUY signal, above all MAs, RSI 58 (momentum)
- QQQ (Tech): BUY signal, strong uptrend, RSI 62 (strong momentum)
→ Equities = BULLISH

Bonds (Risk Sentiment):
- TLT (Treasury Bond ETF): SELL, downtrend, below all MAs
→ Bonds = BEARISH

REGIME CONCLUSION:
Market is in RISK-ON mode (stocks up, bonds down). Investors are confident.
- Best for: Growth stocks, small-caps, crypto
- Avoid: Defensive plays, utilities, bonds
- Trend: Bullish until proven otherwise

NEXT WATCH:
- If QQQ momentum fades (RSI < 50): Risk-off could be coming
- If TLT breaks below support: Confirm risk-off
- Key level: SPY must hold above its 4h EMA50 to maintain bullish bias
```

### Workflow 3: Relative Strength Comparison

**Goal:** Find the strongest performers in a sector

**Question to AI:**
> "Compare Microsoft (MSFT), Apple (AAPL), and Nvidia (NVDA) on the daily chart. Which is the strongest right now?"

**How the AI Uses the Tools:**
1. `get_technical_analysis(symbol="MSFT", exchange="NASDAQ", interval="1d")`
2. `get_technical_analysis(symbol="AAPL", exchange="NASDAQ", interval="1d")`
3. `get_technical_analysis(symbol="NVDA", exchange="NASDAQ", interval="1d")`

**Expected Response:**
```
Tech Stock Strength Comparison (Daily):

1. NVIDIA (NVDA) - STRONGEST
   - Signal: BUY (9 oscillators bullish, 6 MAs bullish)
   - RSI: 72 (strong momentum, but overbought)
   - Price: Up +4.2% today | Trend: Strong uptrend
   - Issue: Overbought RSI may signal pullback coming

2. Microsoft (MSFT) - SECOND STRONGEST
   - Signal: BUY (8 oscillators bullish, 6 MAs bullish)
   - RSI: 58 (healthy, room to go up)
   - Price: Up +2.1% today | Trend: Solid uptrend
   - Advantage: Not overbought, healthier for continued gains

3. Apple (AAPL) - NEUTRAL
   - Signal: NEUTRAL (mixed signals)
   - RSI: 48 (flat, no momentum yet)
   - Price: +0.8% today | Trend: Choppy
   - Issue: Lagging the sector

RANKING:
1. MSFT = Best risk/reward (trending without extremes)
2. NVDA = Strongest but overbought (caution on entry)
3. AAPL = Wait for confirmation

TRADE IDEA: Buy MSFT, avoid NVDA until RSI resets, skip AAPL until it shows strength.
```

---

## Tips for Effective AI-Assisted Analysis

1. **Ask Natural Questions** — The AI understands context. Say "Is Apple strong?" instead of "Get AAPL analysis."

2. **Specify Timeframes** — Different timeframes tell different stories. Ask for both daily and intraday.

3. **Use Confluence** — Multiple indicators pointing the same direction = stronger signal.

4. **Check Relative Strength** — Compare the symbol to market indices (SPY, QQQ) to see if it's outperforming.

5. **Validate with Volume** — High-volume moves are more reliable than low-volume moves.

6. **Risk Management First** — Always ask for support/resistance and stop-loss levels before trading.

7. **Don't Overtrade** — Wait for clear signals (BUY or SELL) rather than guessing on NEUTRAL.

8. **Monitor for Changes** — Market conditions change. Re-check analysis regularly, especially before major news events.

---

## Common Mistakes to Avoid

❌ **Ignoring Overbought/Oversold** — Trading breakouts when RSI > 80 or < 20 often leads to whipsaws.

❌ **Relying on Single Timeframe** — Always check at least 2 timeframes for confluence.

❌ **Chasing Performance** — Best trades are at support/resistance, not at recent highs.

❌ **Trading Against the Trend** — Shorting an uptrend or longing a downtrend is hard. Follow the trend.

❌ **Ignoring Volume** — Low volume moves are easily reversed. Prioritize high-volume setups.

❌ **No Stop Loss** — Always know your exit before entering. Set stops at technical levels.

---

## Resources & Further Reading

- [TradingView Indicators Guide](https://www.tradingview.com/support/solutions/43000502009-technical-indicators-and-overlays/)
- [Technical Analysis Basics](https://www.investopedia.com/terms/t/technicalanalysis.asp)
- [Confluence Trading Strategy](https://www.babypips.com/forexschool/school/5)
- [Risk Management in Trading](https://www.investopedia.com/articles/forex/09/risk-management-trading.asp)

---

**Happy trading!** Use these examples as templates for your own analysis. The TradingView MCP Server is a powerful tool when combined with thoughtful strategy and risk management.
