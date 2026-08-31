"""Tests for Python module entrypoints."""

import runpy


def test_python_m_tradingview_mcp_calls_server_main(mocker):
    """`python -m tradingview_mcp` should delegate to server.main()."""
    server_main = mocker.patch("tradingview_mcp.server.main")

    runpy.run_module("tradingview_mcp", run_name="__main__")

    server_main.assert_called_once_with()
