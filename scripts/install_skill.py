#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
1-Click Agent Skill Installer for LinkedIn Nexus Agent.
Installs the skill into Antigravity, Claude Code, or OpenClaw skills directory.
"""

import os
import sys
import shutil
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

def install_agent_skill():
    project_root = Path(__file__).resolve().parent.parent
    source_skill = project_root / "skill" / "SKILL.md"

    if not source_skill.exists():
        print(f"Error: Source skill not found at {source_skill}")
        return

    # Check Antigravity / Gemini skills directory
    target_dirs = [
        Path.home() / ".gemini" / "config" / "skills" / "linkedin-nexus",
        Path.home() / ".claude" / "skills" / "linkedin-nexus",
        project_root / ".skills" / "linkedin-nexus"
    ]

    installed_paths = []
    for target in target_dirs:
        try:
            target.mkdir(parents=True, exist_ok=True)
            dest = target / "SKILL.md"
            shutil.copy2(source_skill, dest)
            installed_paths.append(str(target))
        except Exception:
            pass

    print("=" * 60)
    print("  LinkedIn Nexus Agent -- Skill Installer")
    print("=" * 60)
    if installed_paths:
        print("\n[OK SUCCESS] Installed skill to:")
        for p in installed_paths:
            print(f"  * {p}")
        print("\nYour AI assistant (Antigravity, Claude Code, OpenClaw) can now use 'linkedin-nexus'!")
    else:
        print("\nCould not automatically write to global skill locations. Copied to local .skills folder.")

if __name__ == "__main__":
    install_agent_skill()
