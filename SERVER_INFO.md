# Graph-Code MCP Server Information

This document contains the configuration and commands needed to start the Graph-Code MCP environment.

## Ports Configuration
This instance is configured to avoid conflicts with other running Memgraph instances.
- **Bolt Port (Database):** `7688`
- **HTTP Port:** `7444`
- **Memgraph Lab:** `http://localhost:3000`

## How to Start

### 1. Start the Database (Docker)
Run this command from the project root (`/home/mouedarbi/dev/code-graph-rag/`):
```bash
docker-compose up -d
```

### 2. Start the MCP Server
The MCP server is typically managed by your IDE (Claude/Gemini). If you need to verify it manually or if the IDE doesn't start it, use:
```bash
./start_mcp_server.sh
```

## Troubleshooting
If you see port conflicts (e.g., "port is already allocated"), ensure the environment variables are correctly loaded from the `.env` file. You can force them with:
```bash
MEMGRAPH_PORT=7688 MEMGRAPH_HTTP_PORT=7444 LAB_PORT=3000 docker-compose up -d
```

## Project Paths
- **Project Root:** `/home/mouedarbi/dev/code-graph-rag/`
- **Target Repo (for indexing):** `/home/mouedarbi/dev/platform`
- **Configuration File:** `/home/mouedarbi/dev/code-graph-rag/.env`
