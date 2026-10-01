#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated MCP Installer for LinkedIn Nexus Agent.
Detects Claude Desktop configuration, backs it up, and adds 'linkedin-nexus' to mcpServers.
Also outputs ready-to-paste configurations for Cursor, Windsurf, and Claude Code.
"""

import os
import sys
import json
import shutil
from typing import Optional
from pathlib import Path

# Ensure UTF-8 on Windows stdout/stderr
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def get_claude_desktop_config_path() -> Optional[Path]:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    return None

def install_for_claude_desktop():
    config_path = get_claude_desktop_config_path()
    project_root = Path(__file__).resolve().parent.parent
    run_mcp_path = project_root / "run_mcp.py"
    python_exe = sys.executable

    print("=" * 65)
    print("  LinkedIn Nexus Agent -- Model Context Protocol (MCP) Installer")
    print("=" * 65)

    nexus_server_config = {
        "command": str(python_exe),
        "args": [str(run_mcp_path)],
        "env": {
            "PYTHONIOENCODING": "utf-8"
        }
    }

    if config_path:
        print(f"\n[1] Checking Claude Desktop config path:\n    {config_path}")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {}
        if config_path.exists():
            try:
                # Backup
                backup_path = config_path.with_suffix(".json.bak")
                shutil.copy2(config_path, backup_path)
                print(f"    [Backup] Saved existing config to {backup_path.name}")
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception as e:
                print(f"    [Warning] Could not parse existing config: {e}. Creating fresh.")

        if "mcpServers" not in config_data:
            config_data["mcpServers"] = {}

        config_data["mcpServers"]["linkedin-nexus"] = nexus_server_config

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        print("    [OK SUCCESS] 'linkedin-nexus' server installed in Claude Desktop!")
        print("    Restart Claude Desktop to use LinkedIn Nexus tools directly inside Claude.")
    else:
        print("    [!] Could not automatically determine Claude Desktop config location.")

    print("\n" + "=" * 65)
    print("  Cursor IDE & Windsurf Configuration:")
    print("=" * 65)
    cursor_config = {
        "mcpServers": {
            "linkedin-nexus": nexus_server_config
        }
    }
    print("In Cursor -> Settings -> MCP -> Add new MCP server (or paste in .cursor/mcp.json):")
    print(json.dumps(cursor_config, indent=2))
    print("=" * 65)

if __name__ == "__main__":
    install_for_claude_desktop()
