"""
Daily Notion Sync Script
========================
Runs daily technical analysis sync to Notion for tracked symbols.
"""

import asyncio
import logging
import os
from typing import Optional

from dotenv import load_dotenv

from tradingview_mcp.notion_sync import NotionSync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("daily-sync")

# Load environment variables
load_dotenv()

# Default trading symbols (US stocks)
DEFAULT_SYMBOLS = [
    ("ROAD", "NASDAQ"),
    ("PLMR", "NASDAQ"),
    ("VOYG", "NASDAQ"),
    ("ELVA", "NASDAQ"),
    ("ONTO", "NASDAQ"),
    ("MRVL", "NASDAQ"),
    ("WULF", "NASDAQ"),
    ("AMD", "NASDAQ"),
    ("COHR", "NASDAQ"),
    ("CAMT", "NASDAQ"),
    ("WDC", "NASDAQ"),
    ("TER", "NASDAQ"),
    ("AMPX", "NASDAQ"),
    ("RELY", "NASDAQ"),
    ("UCTT", "NASDAQ"),
    ("IOT", "NASDAQ"),
    ("CIEN", "NASDAQ"),
    ("FTAI", "NASDAQ"),
    ("AAOI", "NASDAQ"),
    ("SANM", "NASDAQ"),
    ("DUOL", "NYSE"),
    ("PLTR", "NYSE"),
    ("META", "NASDAQ"),
    ("CLS", "NYSE"),
    ("APH", "NASDAQ"),
    ("ALAB", "NYSE"),
    ("CRDO", "NASDAQ"),
    ("SEZL", "NASDAQ"),
    ("VRT", "NASDAQ"),
    ("AVGO", "NASDAQ"),
    ("FLEX", "NASDAQ"),
    ("LSCC", "NASDAQ"),
    ("CRWV", "NASDAQ"),
    ("ONON", "NYSE"),
    ("HSAI", "NASDAQ"),
    ("MU", "NASDAQ"),
    ("NESR", "NASDAQ"),
    ("EVR", "NYSE"),
    ("ETN", "NYSE"),
    ("TSM", "NYSE"),
    ("VIST", "NASDAQ"),
]


def sync_daily(
    notion_token: Optional[str] = None,
    database_id: Optional[str] = None,
    symbols: Optional[list[tuple[str, str]]] = None,
    timeframe: str = "1d",
) -> None:
    """
    Run daily sync of trading symbols to Notion.

    Args:
        notion_token: Notion API token. If None, reads from NOTION_TOKEN env var.
        database_id: Notion database ID. If None, reads from NOTION_DATABASE_ID env var.
        symbols: List of (symbol, exchange) tuples to sync. If None, uses defaults.
        timeframe: Timeframe for analysis (1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1w, 1M).
    """
    # Get configuration from env or arguments
    token = notion_token or os.getenv("NOTION_TOKEN")
    db_id = database_id or os.getenv("NOTION_DATABASE_ID")
    symbols_to_sync = symbols or DEFAULT_SYMBOLS

    if not token:
        logger.error("NOTION_TOKEN not provided. Set via argument or NOTION_TOKEN env var.")
        return

    if not db_id:
        logger.error("NOTION_DATABASE_ID not provided. Set via argument or NOTION_DATABASE_ID env var.")
        return

    logger.info(f"Starting daily sync for {len(symbols_to_sync)} symbols")
    logger.info(f"Timeframe: {timeframe}")
    logger.info(f"Database ID: {db_id}")

    # Initialize Notion sync
    sync = NotionSync(token)
    sync.database_id = db_id

    # Sync each symbol
    success_count = 0
    error_count = 0

    for symbol, exchange in symbols_to_sync:
        try:
            logger.info(f"Syncing {symbol} ({exchange})")
            sync.sync_symbol(symbol, exchange, timeframe=timeframe)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to sync {symbol}: {e}")
            error_count += 1

    logger.info(f"Daily sync complete. Success: {success_count}, Errors: {error_count}")


def main():
    """CLI entry point for daily sync."""
    import sys

    # Parse command line arguments
    timeframe = "1d"
    if "--timeframe" in sys.argv:
        idx = sys.argv.index("--timeframe")
        if idx + 1 < len(sys.argv):
            timeframe = sys.argv[idx + 1]

    sync_daily(timeframe=timeframe)


if __name__ == "__main__":
    main()
