# Desktop Commander MCP Integration

## Overview

**Desktop Commander MCP** (v0.2.52+) extends Claude Desktop with direct access to your desktop environment, enabling:
- File system navigation and operations
- Process management
- System information retrieval
- Command execution

This integration allows Claude to assist with complex desktop workflows across your trading/analytics tools.

---

## Installation & Setup

### Prerequisites
- Node.js 18+ (for npx)
- Claude Desktop app (macOS/Windows)
- Git (for cloning/updating)

### Quick Start

Run the official installer:
```bash
curl -fsSL https://raw.githubusercontent.com/wonderwhy-er/DesktopCommanderMCP/refs/heads/main/install.sh | bash
```

This automatically:
1. Downloads the latest Desktop Commander MCP package
2. Adds the configuration to `~/.config/Claude/claude_desktop_config.json` (macOS/Linux)
3. Configures it under the `mcpServers` section as `"desktop-commander"`

### Manual Configuration

If you prefer manual setup, add this to your Claude Desktop config:

**macOS/Linux:** `~/.config/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": [
        "-y",
        "@wonderwhy-er/desktop-commander@latest"
      ]
    }
  }
}
```

### Verify Installation

1. **Restart Claude Desktop** (close and reopen)
2. **Check the Model Selector** → "Tools" tab
3. **Look for "desktop-commander"** in the connected MCP servers list

If not listed, restart Claude Desktop again.

---

## Integration with TradingView MCP

Desktop Commander pairs with TradingView MCP to create a powerful workflow:

- **TradingView MCP**: Fetch market data, technical analysis, screener results
- **Desktop Commander MCP**: Execute local system commands, manage files, interact with other desktop applications

### Example Combined Workflow

```
User: "Fetch AAPL analysis and save a report to my Desktop"

1. TradingView MCP fetches: Technical analysis, RSI, MACD for AAPL (1D)
2. Desktop Commander MCP writes the file to ~/Desktop/aapl_report.txt
3. Desktop Commander opens the file in your default text editor
```

---

## Available Tools

Desktop Commander exposes these tool categories:

| Category | Tools |
|----------|-------|
| **File System** | `read_file`, `write_file`, `list_directory`, `get_file_info`, `move_file`, `create_directory` |
| **Process** | `list_processes`, `start_process`, `interact_with_process`, `kill_process`, `stop_search` |
| **System** | `who_am_i`, `ping`, `shutdown`, `get_config`, `set_config_value` |
| **Search** | `start_search`, `get_more_search_results`, `list_searches` |
| **Misc** | `give_feedback_to_desktop_commander` |

Refer to Desktop Commander MCP's official docs for detailed parameters and usage.

---

## Troubleshooting

### "desktop-commander" not appearing in Claude Desktop

**Solutions:**
1. Ensure config file is valid JSON (use a JSON validator)
2. Restart Claude Desktop completely (not just the chat)
3. Check file permissions on the config file
4. Re-run the installer: `curl -fsSL https://raw.githubusercontent.com/wonderwhy-er/DesktopCommanderMCP/refs/heads/main/install.sh | bash`

### Command execution errors

- Check that the command syntax is correct
- Verify file paths are absolute (not relative)
- On Windows, use forward slashes `/` in paths or escape backslashes

### NPX timeout or connection issues

- Check your internet connection
- Ensure Node.js/npm is up to date: `node --version`, `npm --version`
- Try installing globally: `npm install -g @wonderwhy-er/desktop-commander`

---

## Security Considerations

**Desktop Commander MCP has full access to your local system.** Use it carefully:

- ✅ **Safe:** File operations within your home directory, reading system info, harmless commands
- ⚠️ **Risky:** Running arbitrary shell commands, modifying system files, executing untrusted code
- ❌ **Avoid:** Passing user input directly to shell commands (risk of injection)

**Best practices:**
1. Review command suggestions before approving
2. Don't enable Desktop Commander for untrusted AI contexts
3. Use restrictive file permissions when possible
4. Keep Claude Desktop updated

---

## Useful Shortcuts

### Common Tasks

**List all processes:**
```
"Use desktop-commander to list all running processes"
```

**Create a trading journal:**
```
"Write a CSV file to ~/Documents/trading_journal.csv with headers: Date, Symbol, Entry, Exit, PnL"
```

**Read a system file:**
```
"Read the file ~/.config/Claude/claude_desktop_config.json and show me the MCP servers"
```

---

## Resources

- **Desktop Commander MCP:** https://github.com/wonderwhy-er/DesktopCommanderMCP
- **Claude Desktop:** https://claude.ai/download
- **Model Context Protocol:** https://modelcontextprotocol.io/

---

## Support & Feedback

- **Issues:** Report bugs on the [GitHub repo](https://github.com/wonderwhy-er/DesktopCommanderMCP/issues)
- **Feedback:** Use the `give_feedback_to_desktop_commander` tool in Claude
- **Discord/Community:** Check the official MCP channels for announcements

---

**Last updated:** 2026-10-01  
**Version:** 0.2.52  
**Status:** Active
