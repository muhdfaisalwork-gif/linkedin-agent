"""
GitHub SEO Agent — MCP Server (Model Context Protocol 2024-11-05)
Exposes audit, launch pack, and community file generation as JSON-RPC 2.0 tools
for Claude Desktop, Cursor, and other MCP-compatible hosts.
"""
import sys
import json
import os
from typing import Dict, Any, Optional, List
from core.seo_engine import GitHubSEOAgent


class GitHubSEOMCPServer:
    """Lightweight MCP (Model Context Protocol) stdio server for GitHub SEO Agent."""

    def __init__(self, repo_dir: Optional[str] = None):
        self.protocol_version = "2024-11-05"
        self.repo_dir = repo_dir or os.getcwd()
        owner = os.getenv("REPO_OWNER", "owner")
        name = os.getenv("REPO_NAME", "repo")
        self.agent = GitHubSEOAgent(owner, name, repo_dir=self.repo_dir)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns JSON-Schema tool definitions for MCP tools/list."""
        return [
            {
                "name": "audit_repo_seo",
                "description": "Audits a GitHub repository directory for SEO health, keyword density, badges, CI, and community standards. Returns a 0-100 score.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repo_dir": {
                            "type": "string",
                            "description": "Path to repository root directory to audit."
                        }
                    }
                }
            },
            {
                "name": "generate_launch_pack",
                "description": "Generates multi-channel launch copy for Hacker News, Reddit, Twitter/X, Product Hunt, and GitHub Releases.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "enum": ["all", "hacker_news", "reddit", "twitter_thread", "product_hunt", "release_notes"],
                            "description": "Target channel for launch copy.",
                            "default": "all"
                        }
                    }
                }
            },
            {
                "name": "generate_community_files",
                "description": "Generates GitHub Community Standards file contents (CI workflow, issue templates, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT).",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Dispatches tool execution and returns result as text."""
        if name == "audit_repo_seo":
            repo_dir = arguments.get("repo_dir", self.repo_dir)
            agent = GitHubSEOAgent(self.agent.repo_owner, self.agent.repo_name, repo_dir=repo_dir)
            audit = agent.audit_repository()
            lines = [
                f"### GitHub SEO Audit Score: {audit['score']}/100 (Grade: {audit['grade']})\n",
                "**Checklist**:"
            ]
            for item in audit["checklist"]:
                lines.append(f"- ✓ {item}")
            lines.append(f"\n**Recommended Topics**: {', '.join(audit['recommended_topics'])}")
            lines.append(f"\n**CLI Command**: `{agent.get_gh_cli_topics_command()}`")
            return "\n".join(lines)

        elif name == "generate_launch_pack":
            channel = arguments.get("channel", "all")
            packs = self.agent.generate_launch_pack(channel=channel)
            lines = [f"### Launch Pack ({channel}):\n"]
            for ch, text in packs.items():
                lines.append(f"#### {ch.upper()}\n{text}\n---\n")
            return "\n".join(lines)

        elif name == "generate_community_files":
            files = self.agent.generate_community_health_files()
            lines = ["### Community Health Files:\n"]
            for path in files:
                lines.append(f"- {path}")
            return "\n".join(lines)

        raise ValueError(f"Unknown tool: {name}")

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handles a single JSON-RPC 2.0 request."""
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "github-seo-agent", "version": "1.0.0"}
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": self.get_tool_definitions()}
            }

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments") or {}
            try:
                result_text = self.execute_tool(name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": result_text}]}
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Error: {str(e)}"}]
                    }
                }

        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            }
        return None

    def run_stdio(self):
        """Runs the MCP server over stdin/stdout line-by-line."""
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

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                continue


if __name__ == "__main__":
    server = GitHubSEOMCPServer()
    server.run_stdio()
