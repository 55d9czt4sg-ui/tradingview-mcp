"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock
from tradingview_ta import Interval


@pytest.fixture
def mock_analysis():
    """Mock Analysis object for testing."""
    analysis = Mock()
    analysis.symbol = "AAPL"
    analysis.exchange = "NASDAQ"
    analysis.interval = Interval.INTERVAL_1_DAY
    analysis.time = "2026-06-25 16:00"
    analysis.summary = "BUY"
    analysis.oscillators = {
        "RSI": 65.5,
        "MACD.macd": 0.32,
        "MACD.signal": 0.28,
        "Stoch.K": 72.4,
        "Stoch.D": 68.9,
    }
    analysis.moving_averages = {
        "EMA20": 185.50,
        "EMA50": 180.20,
        "EMA200": 175.80,
    }
    analysis.indicators = {
        "open": 184.50,
        "high": 187.30,
        "low": 184.10,
        "close": 186.95,
        "volume": 52_300_000,
        "RSI": 65.5,
        "MACD.macd": 0.32,
        "BB.upper": 190.20,
        "BB.lower": 180.40,
        "EMA20": 185.50,
        "EMA50": 180.20,
        "EMA200": 175.80,
    }
    return analysis


@pytest.fixture
def mock_handler_class(monkeypatch):
    """Mock TA_Handler class for testing."""
    mock_handler = Mock()
    mock_handler_class = Mock(return_value=mock_handler)

    # Import here to avoid circular imports
    import tradingview_mcp.server as server
    monkeypatch.setattr(server, "TA_Handler", mock_handler_class)

    return mock_handler_class, mock_handler


@pytest.fixture
def search_response():
    """Mock symbol search API response."""
    return {
        "symbols": [
            {
                "symbol": "AAPL",
                "exchange": "NASDAQ",
                "type": "stock",
                "description": "Apple Inc.",
            },
            {
                "symbol": "AAPL.D",
                "exchange": "CSE",
                "type": "stock",
                "description": "<b>Apple</b> Inc. (other exchange)",
            },
        ]
    }
