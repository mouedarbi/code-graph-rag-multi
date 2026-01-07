#!/bin/bash
set -e

# Get the directory where this script is actually located, even if symlinked
SCRIPT_PATH=$(realpath "${BASH_SOURCE[0]}")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
PROJECT_ROOT="$SCRIPT_DIR"

# Navigate to project root
cd "$PROJECT_ROOT"

# Check for virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found in .venv or venv" >&2
    exit 1
fi

# Set PYTHONPATH to include the current directory to ensure imports work
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Unset conflicting environment variables to ensure .env is respected
# This prevents interference from other running instances (e.g., on ports 7688/7444)
unset MEMGRAPH_HOST
unset MEMGRAPH_PORT
unset MEMGRAPH_HTTP_PORT
unset LAB_PORT

# Run the MCP server directly to avoid CLI/Typer stdout pollution and module warnings
# The CLI wrapper uses rich/typer which might print to stdout on errors, breaking JSON-RPC
exec python codebase_rag/mcp/server.py "$@"
