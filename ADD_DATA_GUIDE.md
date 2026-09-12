# How to Add Data to Your Notion Database

The API is returning 403 Forbidden errors, which means the integration needs additional permissions. Here are your options:

## Option 1: Fix Notion Integration Permissions (Recommended)

### Step 1: Grant Workspace Access
1. Go to your Notion workspace settings
2. Click **Settings & Members** → **Integrations** (or **Connected apps**)
3. Find **"TradingView Sync"** in the list
4. Click to open it and ensure:
   - Status shows "Connected"
   - Permissions show "Editor" or "Full access"
5. If missing, click **"Connect"** and authorize

### Step 2: Grant Database Access
1. Open your Notion database page
2. Click the **Share** button (top right)
3. Search for **"TradingView Sync"**
4. Select it and set permissions to **"Editor"**
5. Click **"Invite"**

### Step 3: Test Connection
```bash
cd /home/user/tradingview-mcp
uv run python -c "
from tradingview_mcp.notion_sync import NotionSync
sync = NotionSync('YOUR_NOTION_TOKEN_FROM_ENV')
print('✅ Connection successful!')
"
```

---

## Option 2: Manually Add Data to Notion

If you prefer to add data manually, use this data:

### AAPL - Apple
- **Symbol:** AAPL | **Exchange:** NASDAQ
- **Price:** $225.50 | **Change %:** +2.5%
- **Recommendation:** BUY
- **RSI:** 65 | **MACD:** 2.35
- **BB Upper:** 228.75 | **BB Lower:** 220.25
- **Entry Point:** 220.25 | **Exit/TP:** 228.75
- **Stop Loss:** 215.50 | **Risk/Reward:** 2.14
- **Timeframe:** 1d

### MSFT - Microsoft
- **Symbol:** MSFT | **Exchange:** NASDAQ
- **Price:** $440.75 | **Change %:** +1.8%
- **Recommendation:** NEUTRAL
- **RSI:** 55 | **MACD:** 1.2
- **BB Upper:** 450 | **BB Lower:** 430
- **Entry Point:** 430 | **Exit/TP:** 450
- **Stop Loss:** 420 | **Risk/Reward:** 1.82
- **Timeframe:** 1d

### TSLA - Tesla
- **Symbol:** TSLA | **Exchange:** NASDAQ
- **Price:** $245.80 | **Change %:** +4.2%
- **Recommendation:** BUY
- **RSI:** 72 | **MACD:** 3.5
- **BB Upper:** 255 | **BB Lower:** 235
- **Entry Point:** 235 | **Exit/TP:** 255
- **Stop Loss:** 228 | **Risk/Reward:** 2.35
- **Timeframe:** 1d

### NVDA - Nvidia
- **Symbol:** NVDA | **Exchange:** NASDAQ
- **Price:** $135.25 | **Change %:** -3.2%
- **Recommendation:** SELL
- **RSI:** 35 | **MACD:** -0.85
- **BB Upper:** 142.5 | **BB Lower:** 128
- **Entry Point:** 142.5 | **Exit/TP:** 128
- **Stop Loss:** 145 | **Risk/Reward:** 1.65
- **Timeframe:** 1d

### GOOGL - Google
- **Symbol:** GOOGL | **Exchange:** NASDAQ
- **Price:** $185.40 | **Change %:** +1.5%
- **Recommendation:** BUY
- **RSI:** 60 | **MACD:** 1.8
- **BB Upper:** 190 | **BB Lower:** 180
- **Entry Point:** 180 | **Exit/TP:** 190
- **Stop Loss:** 175 | **Risk/Reward:** 2.0
- **Timeframe:** 1d

### AMD - Advanced Micro Devices
- **Symbol:** AMD | **Exchange:** NASDAQ
- **Price:** $198.75 | **Change %:** +3.1%
- **Recommendation:** BUY
- **RSI:** 68 | **MACD:** 2.1
- **BB Upper:** 205 | **BB Lower:** 192
- **Entry Point:** 192 | **Exit/TP:** 205
- **Stop Loss:** 188 | **Risk/Reward:** 2.23
- **Timeframe:** 1d

### How to Add Manually
1. Open your Notion database
2. Click **"New"** or **"+"**
3. Fill in the Symbol first (this is your Title field)
4. Fill in remaining fields from the data above
5. Repeat for each symbol

---

## Option 3: Use Automated Script (Once Permissions Fixed)

Once permissions are fixed:
```bash
cd /home/user/tradingview-mcp
uv run python << 'EOF'
from notion_client import Client
from datetime import datetime
import os

# Load from .env
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=notion_token)

# Sample data...
# (See SAMPLE_DATA.json for full dataset)

# Create pages with properties
EOF
```

---

## Troubleshooting

### Still getting 403 errors?

1. **Check integration status:**
   - Notion Settings → Integrations
   - Verify "TradingView Sync" is listed and "Connected"

2. **Check database permissions:**
   - Open your database page
   - Click Share → Look for "TradingView Sync"
   - Ensure it has Editor access

3. **Regenerate token:**
   - Go to My Integrations
   - Click "TradingView Sync"
   - Click refresh icon on "Internal Integration Token"
   - Update `.env` file with new token
   - Test again

4. **Verify workspace access:**
   - Your Notion workspace must have the integration enabled
   - Admin may need to approve integrations

---

## Next Steps

1. **Fix permissions** using Option 1 above
2. **Test the API** with the connection test command
3. **Run daily sync:** `uv run tradingview-daily-sync`
4. **Check Notion database** for populated data

Once working, the sync will automatically update your database daily! 📊
