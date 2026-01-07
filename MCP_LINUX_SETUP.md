# MCP Server Setup on Linux

A script `start_mcp_server.sh` has been created to reliably start the MCP server.

## Usage

You can run the server manually:

```bash
./start_mcp_server.sh
```

## Integration with Claude Desktop

To use this with Claude Desktop on Linux, add the following to your configuration file (usually `~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "graph-code": {
      "command": "/home/mouedarbi/dev/code-graph-rag/start_mcp_server.sh",
      "args": [],
      "env": {
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Notes

- The script automatically handles the Python virtual environment activation.
- The server uses `stdio` (standard input/output) for communication, so it must be started by a client (like Claude) or piped to another tool. It is not designed to run as a standalone background service (daemon) without a client attached.
