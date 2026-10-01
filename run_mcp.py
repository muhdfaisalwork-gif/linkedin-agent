#!/usr/bin/env python3
"""
MCP stdio launcher for GitHub SEO Agent.
Connects standard I/O to GitHubSEOMCPServer for Claude Desktop, Cursor, and IDEs.
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows UTF-8 stdout/stdin
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stdin, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from core.mcp_server import GitHubSEOMCPServer

def main():
    try:
        server = GitHubSEOMCPServer()
        server.run_stdio()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error in MCP server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
