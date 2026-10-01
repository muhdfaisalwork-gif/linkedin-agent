#!/usr/bin/env python3
"""
LinkedIn Nexus Agent - GitHub SEO CLI
Usage:
  python scripts/github_seo.py audit
  python scripts/github_seo.py readme [--apply]
  python scripts/github_seo.py launch [--channel hacker_news|reddit_localllama|reddit_selfhosted|twitter_thread|release_notes]
  python scripts/github_seo.py community [--apply]
"""

import sys
import os
import argparse

# Ensure utf-8 stdout on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.seo.github_seo import LinkedInNexusGitHubSEO

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Nexus Agent - GitHub SEO & Virality Engine")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Audit command
    subparsers.add_parser("audit", help="Run GitHub SEO audit on repository")

    # Readme command
    readme_parser = subparsers.add_parser("readme", help="Generate or apply optimized README.md")
    readme_parser.add_argument("--apply", action="store_true", help="Overwrite README.md with optimized version (creates .backup first)")

    # Launch pack command
    launch_parser = subparsers.add_parser("launch", help="Generate multi-channel launch copy")
    launch_parser.add_argument("--channel", default="all", choices=["all", "hacker_news", "reddit_localllama", "reddit_selfhosted", "twitter_thread", "release_notes"], help="Specific channel")
    launch_parser.add_argument("--ai", action="store_true", help="Use OpenRouter free models (Gemma 4 / Nemotron) to synthesize custom copy")
    launch_parser.add_argument("--angle", type=str, default="", help="Custom strategic angle or hook to emphasize")
    launch_parser.add_argument("--model", type=str, default=None, help="OpenRouter model ID (defaults to google/gemma-4-31b-it:free)")

    # Community command
    comm_parser = subparsers.add_parser("community", help="Generate GitHub Community Standards files")
    comm_parser.add_argument("--apply", action="store_true", help="Write .github workflows, issue templates, and policies")

    args = parser.parse_args()

    engine = LinkedInNexusGitHubSEO()

    if args.command == "audit" or not args.command:
        res = engine.audit_repository()
        print("\n=======================================================")
        print(f"  LINKEDIN NEXUS AGENT — GITHUB SEO AUDIT: {res['score']}/100 (Grade: {res['grade']})")
        print("=======================================================\n")
        print("Checklist:")
        for item in res["checklist"]:
            icon = "✓" if item["status"] == "pass" else ("⚠️" if item["status"] == "warning" else "✗")
            print(f"  {icon} [{item['impact'].upper()}] {item['item']}: {item['note']}")

        print("\nRecommended GitHub Topics:")
        print("  " + ", ".join(res["recommended_topics"]))
        print("\nGitHub CLI Command:")
        print("  " + res["gh_cli_command"])
        print("")

    elif args.command == "readme":
        optimized = engine.generate_optimized_readme()
        if args.apply:
            readme_path = os.path.join(engine.repo_dir, "README.md")
            backup_path = os.path.join(engine.repo_dir, "README.md.backup")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    with open(backup_path, "w", encoding="utf-8") as b:
                        b.write(f.read())
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(optimized)
            print("✓ README.md updated with SEO-optimized version (original backed up to README.md.backup).")
        else:
            print(optimized)

    elif args.command == "launch":
        if getattr(args, "ai", False):
            channels = [args.channel] if args.channel != "all" else ["hacker_news", "reddit_localllama", "reddit_selfhosted", "twitter_thread", "release_notes"]
            for ch in channels:
                res = engine.generate_ai_launch_content(channel=ch, angle=args.angle, model=args.model)
                print(f"\n--- [CHANNEL: {ch.upper()}] (Model: {res.get('model_used')} | Source: {res.get('source')}) ---")
                if "note" in res:
                    print(f"Note: {res['note']}\n")
                print(res["content"])
                print("-" * 50)
        else:
            packs = engine.generate_launch_pack(channel=args.channel)
            for ch, text in packs.items():
                print(f"\n--- [CHANNEL: {ch.upper()}] ---")
                print(text)
                print("-" * 50)

    elif args.command == "community":
        if args.apply:
            res = engine.generate_community_health_files()
            print("✓ " + res["message"])
            for f in res["files_written"]:
                print(f"  + {f}")
        else:
            print("Run with --apply to write .github workflows, issue templates, CONTRIBUTING.md, and SECURITY.md.")

if __name__ == "__main__":
    main()
