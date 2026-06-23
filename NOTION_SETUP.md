# Notion Integration Setup

This guide walks you through setting up daily TradingView technical analysis syncing to Notion.

## Prerequisites

- Python 3.10+
- A Notion account
- A Notion Workspace
- The Notion API (free tier available)

## Step 1: Create a Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click **"Create new integration"**
3. Name it: `TradingView Sync`
4. Select your workspace
5. Click **"Submit"**
6. Copy the **"Internal Integration Token"** (this is your API key)

## Step 2: Install Dependencies

```bash
uv sync
```

## Step 3: Set Up the Database

Run the interactive setup script:

```bash
uv run tradingview-setup-notion
```

The script will:
1. Ask for your Notion API token
2. Ask for the Notion Page ID where you want to create the database
3. Create a new Notion database with all required fields
4. Save the configuration to a `.env` file

### How to Get Your Notion Page ID

1. Open any Notion page in your workspace
2. Look at the URL: `https://www.notion.so/[YOUR-WORKSPACE]/[PAGE-ID]?v=...`
3. Extract the PAGE-ID (should be 36 characters including hyphens)

**Note:** The database will be created as a child of your specified page.

## Step 4: Run Daily Sync

### Option A: Manual Run

```bash
uv run tradingview-daily-sync
```

### Option B: Schedule with Cron (Linux/Mac)

Edit your crontab:
```bash
crontab -e
```

Add a line to run daily at 9 AM:
```
0 9 * * * cd /path/to/tradingview-mcp && uv run tradingview-daily-sync
```

### Option C: Schedule with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task → Name: "TradingView Daily Sync"
3. Set trigger to Daily at 9:00 AM
4. Set action to: `uv run tradingview-daily-sync`
5. Set working directory to your project folder

## Configuration

### Environment Variables

Create a `.env` file with:

```
NOTION_TOKEN=ntn_xxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Custom Symbol List

Edit `/src/tradingview_mcp/daily_sync.py` and modify `DEFAULT_SYMBOLS`:

```python
DEFAULT_SYMBOLS = [
    ("AAPL", "NASDAQ"),
    ("MSFT", "NASDAQ"),
    ("TSLA", "NASDAQ"),
    # Add your symbols here
]
```

## Database Schema

The Notion database includes the following fields:

| Field | Type | Description |
|-------|------|-------------|
| Symbol | Title | Stock ticker symbol |
| Exchange | Text | Stock exchange (NASDAQ, NYSE, etc.) |
| Price | Number | Current price |
| Change % | Percent | Daily % change |
| Recommendation | Select | BUY / SELL / NEUTRAL |
| RSI | Number | Relative Strength Index (0-100) |
| MACD | Number | MACD value |
| BB Upper | Number | Bollinger Band upper value |
| BB Lower | Number | Bollinger Band lower value |
| Entry Point | Number | Calculated entry price |
| Exit Point (TP) | Number | Take profit level |
| Stop Loss | Number | Stop loss level |
| Risk/Reward | Number | Risk/reward ratio |
| Last Updated | Date | Last sync timestamp |
| Timeframe | Select | Analysis timeframe (1h, 4h, 1d) |

## Entry/Exit Calculation

Entry and exit points are calculated based on:

- **Entry Point**: Positioned at the lower Bollinger Band (potential reversal)
- **Exit Point (TP)**: Positioned at the upper Bollinger Band (profit target)
- **Stop Loss**: Set below entry point by ATR distance
- **Risk/Reward Ratio**: Reward ÷ Risk (higher = better risk management)

## Troubleshooting

### "NOTION_TOKEN not provided"
- Make sure your `.env` file exists and contains the token
- Or run the setup script again: `uv run tradingview-setup-notion`

### "NOTION_DATABASE_ID not provided"
- Run the setup script: `uv run tradingview-setup-notion`
- Or manually set the ID in `.env`

### Connection fails
- Verify your Notion API token is correct
- Check that you've given the integration access to your workspace
- Ensure the database ID is valid

### Pages not updating
- Check that the integration has edit permissions to the database
- Verify the TradingView API is accessible
- Check logs for specific error messages

## Logs

By default, logs are printed to console. To save to a file:

```bash
uv run tradingview-daily-sync 2>&1 | tee sync.log
```

## Support

For issues with:
- **TradingView data**: Check [tradingview-ta docs](https://github.com/AnalyzerRE/tradingview-ta)
- **Notion API**: Check [Notion API docs](https://developers.notion.com/)
- **This project**: Check the GitHub issues
