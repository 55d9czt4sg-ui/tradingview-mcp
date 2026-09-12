# TradingView MCP Server — Test Suite

This directory contains automated tests for the TradingView MCP Server.

## Running Tests

### Prerequisites

Install test dependencies:

```bash
uv pip install -e ".[test]"
```

Or with pip:

```bash
pip install -e ".[test]"
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov
```

This generates:
- Terminal summary with coverage %
- HTML report in `htmlcov/index.html`
- XML report in `.coverage.xml` (for CI/CD integration)

### Run Specific Test File

```bash
pytest tests/test_helpers.py -v
```

### Run Specific Test

```bash
pytest tests/test_helpers.py::TestResolveInterval::test_valid_intervals -v
```

### Run Only Async Tests

```bash
pytest -m asyncio
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Detailed Output on Failure

```bash
pytest -vv --tb=long
```

---

## Test Structure

### `conftest.py`
Shared pytest fixtures:
- `mock_analysis` — Mock Analysis object for testing
- `mock_handler_class` — Mocked TA_Handler class
- `search_response` — Mock symbol search API response

### `test_helpers.py`
Unit tests for pure functions:
- `TestResolveInterval` — Interval string resolution
- `TestResolveScreener` — Screener name mapping
- `TestFormatSummary` — Technical analysis summary formatting
- `TestFormatIndicators` — Indicator value extraction and filtering

**Coverage target:** 95%+

### `test_tools.py`
Integration tests for MCP tools (with mocked external APIs):
- `TestGetTechnicalAnalysis` — Single-timeframe analysis
- `TestGetMultiTimeframe` — Multi-timeframe analysis
- `TestGetIndicatorValues` — Raw indicator values
- `TestSearchSymbol` — Symbol search API
- `TestScreenMarket` — Market screening
- `TestGetPriceData` — Current price data

**Coverage target:** 70%+

---

## Coverage Goals

| Module | Current | Target | Status |
|--------|---------|--------|--------|
| `server.py` helpers | 0% | 95% | 📝 In progress |
| `server.py` tools | 0% | 70% | 📝 In progress |
| Overall | 0% | 75% | ✅ Tests exist |

### View Coverage Report

```bash
pytest --cov
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Common Test Patterns

### Testing Async Functions

Use `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_something():
    result = await get_technical_analysis("AAPL", "NASDAQ")
    assert result is not None
```

### Mocking External API Calls

Use `unittest.mock.patch`:

```python
@pytest.mark.asyncio
async def test_with_mocked_api():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json.return_value = {"data": "mocked"}
        result = await search_symbol("AAPL")
        assert "data" in result
```

### Testing Exceptions

Use `pytest.raises`:

```python
def test_invalid_interval():
    with pytest.raises(ValueError, match="Unknown interval"):
        _resolve_interval("99m")
```

---

## CI/CD Integration

For GitHub Actions, add to `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - run: pip install -e ".[test]"
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## Writing New Tests

1. **Create test file** in `tests/test_*.py`
2. **Import modules** under test and pytest
3. **Use fixtures** from `conftest.py` for common test objects
4. **Use @pytest.mark.asyncio** for async tests
5. **Use descriptive test names**: `test_<function>_<scenario>`
6. **Add docstrings** explaining what's being tested

Example:

```python
import pytest
from tradingview_mcp.server import _resolve_interval

def test_resolve_interval_valid():
    """Test valid interval strings are resolved correctly."""
    assert _resolve_interval("1d") == "1d"

@pytest.mark.asyncio
async def test_tool_success(mock_handler_class):
    """Test tool returns valid JSON on success."""
    handler_class, mock_handler = mock_handler_class
    # ... setup mocks ...
    result = await some_tool("AAPL", "NASDAQ")
    data = json.loads(result)
    assert data["symbol"] == "AAPL"
```

---

## Troubleshooting

### Tests timeout

Increase timeout in `pytest.ini` or per test:

```python
@pytest.mark.asyncio
async def test_slow_operation():
    pytest.timeout = 30
    # ... test code ...
```

### Mock not working

Ensure you're patching the right import path:

```python
# Correct: patch where it's used, not where it's defined
with patch("tradingview_mcp.server.TA_Handler") as mock:
    # ...
```

### Async test not running

Add `asyncio_mode = auto` to `pytest.ini` (already configured).

### Coverage report missing

Ensure `pytest-cov` is installed and run:

```bash
pip install pytest-cov
pytest --cov
```

---

## Next Steps

- Add integration tests with real TradingView API calls (mark as `@pytest.mark.slow`)
- Add error scenario tests (network timeouts, malformed responses)
- Add property-based tests using `hypothesis`
- Integrate coverage checks into CI/CD pipeline
- Set minimum coverage threshold (target: 75%)
