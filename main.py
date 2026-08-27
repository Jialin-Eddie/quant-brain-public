"""Quant-Brain MCP Server — Entry Point.

Usage:
    python main.py

This starts the FastMCP server via stdio transport,
making all tools available to Claude Code.
"""

import sys
from pathlib import Path

# Add mcp-server/ to Python path so its modules can import each other
sys.path.insert(0, str(Path(__file__).parent / "mcp-server"))

from server import main

main()
