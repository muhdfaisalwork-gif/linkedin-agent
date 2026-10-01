"""
Model Context Protocol (MCP) Server for LinkedIn Nexus Agent.
Enables Claude Desktop, Cursor, Windsurf, Claude Code, and Antigravity
to invoke LinkedIn Nexus tools natively over stdio JSON-RPC.
"""

from .server import run_stdio_server

__all__ = ["run_stdio_server"]
