"""Unit tests for helper functions."""

import pytest
from tradingview_ta import Interval
from tradingview_mcp.server import (
    _resolve_interval,
    _resolve_screener,
    _format_summary,
    _format_indicators,
)


class TestResolveInterval:
    """Tests for _resolve_interval()."""

    def test_valid_intervals(self):
        """Test all valid interval strings."""
        cases = [
            ("1m", Interval.INTERVAL_1_MINUTE),
            ("5m", Interval.INTERVAL_5_MINUTES),
            ("15m", Interval.INTERVAL_15_MINUTES),
            ("30m", Interval.INTERVAL_30_MINUTES),
            ("1h", Interval.INTERVAL_1_HOUR),
            ("2h", Interval.INTERVAL_2_HOURS),
            ("4h", Interval.INTERVAL_4_HOURS),
            ("1d", Interval.INTERVAL_1_DAY),
            ("1w", Interval.INTERVAL_1_WEEK),
            ("1M", Interval.INTERVAL_1_MONTH),
        ]
        for input_val, expected in cases:
            assert _resolve_interval(input_val) == expected

    def test_case_insensitive(self):
        """Test that interval resolution is case-insensitive."""
        assert _resolve_interval("1D") == Interval.INTERVAL_1_DAY
        assert _resolve_interval("5M") == Interval.INTERVAL_5_MINUTES
        assert _resolve_interval("1H") == Interval.INTERVAL_1_HOUR

    def test_whitespace_handling(self):
        """Test that intervals with surrounding whitespace are handled."""
        assert _resolve_interval("  1d  ") == Interval.INTERVAL_1_DAY
        assert _resolve_interval("\t5m\n") == Interval.INTERVAL_5_MINUTES

    def test_invalid_interval_raises_valueerror(self):
        """Test that invalid interval raises ValueError."""
        with pytest.raises(ValueError, match="Unknown interval"):
            _resolve_interval("99m")

    def test_invalid_interval_error_message(self):
        """Test that error message includes valid values."""
        with pytest.raises(ValueError) as exc_info:
            _resolve_interval("invalid")
        error = str(exc_info.value)
        assert "1m" in error
        assert "5m" in error
        assert "1d" in error

    def test_empty_string_raises_valueerror(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            _resolve_interval("")


class TestResolveScreener:
    """Tests for _resolve_screener()."""

    def test_all_aliases(self):
        """Test all screener aliases map correctly."""
        cases = [
            ("america", "america"),
            ("usa", "america"),
            ("us", "america"),
            ("crypto", "crypto"),
            ("forex", "forex"),
            ("cfd", "cfd"),
            ("india", "india"),
            ("uk", "uk"),
            ("japan", "japan"),
            ("germany", "germany"),
        ]
        for input_val, expected in cases:
            assert _resolve_screener(input_val) == expected

    def test_case_insensitive(self):
        """Test that screener resolution is case-insensitive."""
        assert _resolve_screener("AMERICA") == "america"
        assert _resolve_screener("CRYPTO") == "crypto"
        assert _resolve_screener("FOREX") == "forex"

    def test_whitespace_handling(self):
        """Test that screeners with whitespace are handled."""
        assert _resolve_screener("  america  ") == "america"
        assert _resolve_screener("\tcrypto\n") == "crypto"

    def test_unknown_screener_passthrough(self):
        """Test that unknown screener is returned as-is (fallback)."""
        # Unknown screeners are silently passed through
        result = _resolve_screener("custom_screener")
        assert result == "custom_screener"

    def test_empty_string_passthrough(self):
        """Test that empty string is returned as-is."""
        assert _resolve_screener("") == ""


class TestFormatSummary:
    """Tests for _format_summary()."""

    def test_format_summary_valid(self, mock_analysis):
        """Test formatting a valid Analysis object."""
        result = _format_summary(mock_analysis)

        assert result["symbol"] == "AAPL"
        assert result["exchange"] == "NASDAQ"
        assert result["interval"] == Interval.INTERVAL_1_DAY
        assert result["summary"] == "BUY"
        assert result["oscillators"]["RSI"] == 65.5
        assert result["moving_averages"]["EMA20"] == 185.50

    def test_format_summary_missing_oscillators(self, mock_analysis):
        """Test that missing oscillators are handled gracefully."""
        mock_analysis.oscillators = None
        result = _format_summary(mock_analysis)
        assert result["oscillators"] is None

    def test_format_summary_empty_moving_averages(self, mock_analysis):
        """Test that empty moving_averages dict is handled."""
        mock_analysis.moving_averages = {}
        result = _format_summary(mock_analysis)
        assert result["moving_averages"] == {}

    def test_format_summary_time_string_conversion(self, mock_analysis):
        """Test that time is converted to string."""
        mock_analysis.time = "2026-06-25 16:00"
        result = _format_summary(mock_analysis)
        assert isinstance(result["time"], str)

    def test_format_summary_keys(self, mock_analysis):
        """Test that result contains expected keys."""
        result = _format_summary(mock_analysis)
        expected_keys = {"symbol", "exchange", "interval", "time", "summary", "oscillators", "moving_averages"}
        assert set(result.keys()) == expected_keys


class TestFormatIndicators:
    """Tests for _format_indicators()."""

    def test_format_indicators_all(self, mock_analysis):
        """Test formatting all indicators."""
        result = _format_indicators(mock_analysis)

        assert result["symbol"] == "AAPL"
        assert result["indicators"]["RSI"] == 65.5
        assert result["indicators"]["close"] == 186.95
        assert "EMA20" in result["indicators"]

    def test_format_indicators_filtered(self, mock_analysis):
        """Test formatting with filtered indicators."""
        keys = ["RSI", "MACD.macd", "close"]
        result = _format_indicators(mock_analysis, keys=keys)

        # Should have exactly the requested keys
        assert set(result["indicators"].keys()) == set(keys)
        assert result["indicators"]["RSI"] == 65.5
        assert result["indicators"]["MACD.macd"] == 0.32

    def test_format_indicators_missing_key(self, mock_analysis):
        """Test that missing indicator keys return None."""
        keys = ["RSI", "NONEXISTENT_INDICATOR", "close"]
        result = _format_indicators(mock_analysis, keys=keys)

        assert result["indicators"]["RSI"] == 65.5
        assert result["indicators"]["NONEXISTENT_INDICATOR"] is None
        assert result["indicators"]["close"] == 186.95

    def test_format_indicators_empty_list(self, mock_analysis):
        """Test formatting with empty indicator list."""
        result = _format_indicators(mock_analysis, keys=[])
        assert result["indicators"] == {}

    def test_format_indicators_no_keys(self, mock_analysis):
        """Test formatting all indicators when keys is None."""
        result = _format_indicators(mock_analysis, keys=None)
        assert len(result["indicators"]) > 0
        assert result["indicators"]["RSI"] == 65.5

    def test_format_indicators_structure(self, mock_analysis):
        """Test that result has expected structure."""
        result = _format_indicators(mock_analysis, keys=["RSI"])
        expected_keys = {"symbol", "exchange", "interval", "time", "indicators"}
        assert set(result.keys()) == expected_keys
