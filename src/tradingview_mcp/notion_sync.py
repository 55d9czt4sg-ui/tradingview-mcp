"""
Notion Sync Module
==================
Syncs TradingView technical analysis to a Notion database.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from notion_client import Client
from tradingview_ta import TA_Handler, Interval

logger = logging.getLogger("tradingview-notion-sync")


class NotionSync:
    def __init__(self, notion_token: str):
        """Initialize Notion client."""
        self.client = Client(auth=notion_token)
        self.database_id = None

    def create_database(self, parent_page_id: str, title: str = "TradingView Analysis") -> str:
        """Create a new Notion database for trading analysis."""
        properties = {
            "Symbol": {"title": {}},
            "Exchange": {"rich_text": {}},
            "Price": {"number": {"format": "dollar"}},
            "Change %": {"number": {"format": "percent"}},
            "Recommendation": {"select": {"options": [
                {"name": "BUY", "color": "green"},
                {"name": "SELL", "color": "red"},
                {"name": "NEUTRAL", "color": "gray"},
            ]}},
            "RSI": {"number": {"format": "number"}},
            "MACD": {"number": {"format": "number"}},
            "BB Upper": {"number": {"format": "number"}},
            "BB Lower": {"number": {"format": "number"}},
            "Entry Point": {"number": {"format": "dollar"}},
            "Exit Point (TP)": {"number": {"format": "dollar"}},
            "Stop Loss": {"number": {"format": "dollar"}},
            "Risk/Reward": {"number": {"format": "number"}},
            "Last Updated": {"date": {}},
            "Timeframe": {"select": {"options": [
                {"name": "1h"},
                {"name": "4h"},
                {"name": "1d"},
            ]}},
        }

        response = self.client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=properties,
        )
        self.database_id = response["id"]
        logger.info(f"Created Notion database: {self.database_id}")
        return self.database_id

    def get_or_create_page(self, symbol: str, exchange: str) -> str:
        """Get existing page for symbol or create new one."""
        try:
            # Query for existing page using the correct API
            response = self.client.request(
                "POST",
                f"/databases/{self.database_id}/query",
                body={"filter": {"property": "Symbol", "title": {"equals": symbol}}},
            )

            if response.get("results"):
                return response["results"][0]["id"]
        except Exception:
            pass

        # Create new page
        page = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties={
                "Symbol": {"title": [{"text": {"content": symbol}}]},
                "Exchange": {"rich_text": [{"text": {"content": exchange}}]},
            },
        )
        return page["id"]

    def calculate_entry_exit(
        self,
        close: float,
        rsi: float,
        bb_upper: float,
        bb_lower: float,
        atr: Optional[float] = None,
    ) -> dict[str, float]:
        """Calculate entry, exit (take profit), and stop loss levels based on technical indicators."""
        atr = atr or (close * 0.02)  # Default to 2% if ATR not provided

        # Entry point: near lower Bollinger Band for potential reversal
        entry = bb_lower if bb_lower < close else close * 0.98

        # Take profit: near upper Bollinger Band
        exit_tp = bb_upper if bb_upper > close else close * 1.05

        # Stop loss: below entry by ATR
        stop_loss = entry - atr

        # Risk/Reward ratio
        risk = entry - stop_loss
        reward = exit_tp - entry
        risk_reward = reward / risk if risk > 0 else 0

        return {
            "entry": round(entry, 2),
            "exit_tp": round(exit_tp, 2),
            "stop_loss": round(stop_loss, 2),
            "risk_reward": round(risk_reward, 2),
        }

    def update_page(self, page_id: str, analysis_data: dict) -> None:
        """Update a Notion page with technical analysis data."""
        levels = self.calculate_entry_exit(
            close=analysis_data.get("close", 0),
            rsi=analysis_data.get("rsi", 50),
            bb_upper=analysis_data.get("bb_upper", 0),
            bb_lower=analysis_data.get("bb_lower", 0),
            atr=analysis_data.get("atr"),
        )

        recommendation = analysis_data.get("recommendation", "NEUTRAL")
        # Ensure recommendation is valid
        if recommendation not in ["BUY", "SELL", "NEUTRAL"]:
            recommendation = "NEUTRAL"

        properties = {
            "Price": {"number": analysis_data.get("close")},
            "Change %": {"number": analysis_data.get("change_pct", 0) / 100},
            "Recommendation": {"select": {"name": recommendation}},
            "RSI": {"number": analysis_data.get("rsi")},
            "MACD": {"number": analysis_data.get("macd")},
            "BB Upper": {"number": analysis_data.get("bb_upper")},
            "BB Lower": {"number": analysis_data.get("bb_lower")},
            "Entry Point": {"number": levels["entry"]},
            "Exit Point (TP)": {"number": levels["exit_tp"]},
            "Stop Loss": {"number": levels["stop_loss"]},
            "Risk/Reward": {"number": levels["risk_reward"]},
            "Last Updated": {"date": {"start": datetime.now().isoformat()}},
            "Timeframe": {"select": {"name": analysis_data.get("timeframe", "1d")}},
        }

        self.client.pages.update(page_id=page_id, properties=properties)
        logger.info(f"Updated page {page_id}")

    def sync_symbol(
        self,
        symbol: str,
        exchange: str,
        screener: str = "america",
        timeframe: str = "1d",
    ) -> None:
        """Fetch TradingView analysis and sync to Notion."""
        try:
            handler = TA_Handler(
                symbol=symbol.upper(),
                exchange=exchange.upper(),
                screener=screener.lower(),
                interval=self._resolve_interval(timeframe),
                timeout=15,
            )
            analysis = handler.get_analysis()

            # Extract data
            analysis_data = {
                "close": analysis.indicators.get("close"),
                "change_pct": analysis.indicators.get("change", 0),
                "rsi": analysis.indicators.get("RSI"),
                "macd": analysis.indicators.get("MACD.macd"),
                "bb_upper": analysis.indicators.get("BB.upper"),
                "bb_lower": analysis.indicators.get("BB.lower"),
                "atr": analysis.indicators.get("ATR"),
                "recommendation": analysis.summary.get("RECOMMENDATION", "NEUTRAL"),
                "timeframe": timeframe,
            }

            # Get or create page
            page_id = self.get_or_create_page(symbol, exchange)

            # Update page
            self.update_page(page_id, analysis_data)
            logger.info(f"Synced {symbol} to Notion")

        except Exception as e:
            logger.error(f"Error syncing {symbol}: {e}")

    @staticmethod
    def _resolve_interval(timeframe: str) -> str:
        """Map timeframe string to Interval constant."""
        interval_map = {
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
        return interval_map.get(timeframe.lower(), Interval.INTERVAL_1_DAY)
