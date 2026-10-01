#!/usr/bin/env python3
"""
GitHub SEO Agent — CLI Entry Point
Usage:
  python github_seo_agent.py audit [--repo-dir .]
  python github_seo_agent.py readme --project-name "My Project" --tagline "..." --features "a,b,c" --tech-stack "x,y" [--apply]
  python github_seo_agent.py launch [--channel hacker_news] [--ai] [--angle "..."] [--model "..."]
  python github_seo_agent.py community [--apply]
  python github_seo_agent.py mcp
"""
import argparse
import os
import sys

# Windows UTF-8 console support
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from core.seo_engine import GitHubSEOAgent


def main():
    parser = argparse.ArgumentParser(
        description="🔍 GitHub SEO Agent — Open-Source Repository Discoverability Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # audit
    audit_p = subparsers.add_parser("audit", help="Run SEO audit on a repository")
    audit_p.add_argument("--repo-dir", default=".", help="Path to repository root (default: current directory)")
    audit_p.add_argument("--owner", default="owner", help="GitHub repo owner")
    audit_p.add_argument("--name", default="repo", help="GitHub repo name")

    # readme
    readme_p = subparsers.add_parser("readme", help="Generate optimized README template")
    readme_p.add_argument("--project-name", required=True)
    readme_p.add_argument("--tagline", default="An awesome open-source project")
    readme_p.add_argument("--features", default="", help="Comma-separated features")
    readme_p.add_argument("--tech-stack", default="", help="Comma-separated technologies")
    readme_p.add_argument("--apply", action="store_true", help="Write README.md to disk")
    readme_p.add_argument("--repo-dir", default=".")
    readme_p.add_argument("--owner", default="owner")
    readme_p.add_argument("--name", default="repo")

    # launch
    launch_p = subparsers.add_parser("launch", help="Generate multi-channel launch copy")
    launch_p.add_argument("--channel", default="all",
                          choices=["all", "hacker_news", "reddit", "twitter_thread", "product_hunt", "release_notes"])
    launch_p.add_argument("--ai", action="store_true", help="Use OpenRouter free models (Gemma 4 / Nemotron)")
    launch_p.add_argument("--angle", default="", help="Custom strategic angle")
    launch_p.add_argument("--model", default=None, help="OpenRouter model ID")
    launch_p.add_argument("--owner", default="owner")
    launch_p.add_argument("--name", default="repo")

    # community
    comm_p = subparsers.add_parser("community", help="Generate GitHub Community Standards files")
    comm_p.add_argument("--apply", action="store_true", help="Write files to disk")
    comm_p.add_argument("--repo-dir", default=".")
    comm_p.add_argument("--owner", default="owner")
    comm_p.add_argument("--name", default="repo")

    # mcp
    subparsers.add_parser("mcp", help="Start MCP stdio server")

    args = parser.parse_args()

    if args.command == "audit":
        engine = GitHubSEOAgent(args.owner, args.name, repo_dir=os.path.abspath(args.repo_dir))
        audit = engine.audit_repository()
        print(f"\n{'='*55}")
        print(f"  GITHUB SEO AUDIT: {audit['score']}/100 (Grade: {audit['grade']})")
        print(f"{'='*55}\n")
        print("Checklist:")
        for item in audit["checklist"]:
            print(f"  ✓ {item}")
        print(f"\nRecommended Topics: {', '.join(audit['recommended_topics'])}")
        print(f"\nGitHub CLI Command:\n  {engine.get_gh_cli_topics_command()}\n")

    elif args.command == "readme":
        engine = GitHubSEOAgent(args.owner, args.name, repo_dir=os.path.abspath(args.repo_dir))
        features = [f.strip() for f in args.features.split(",") if f.strip()] or ["Feature 1"]
        tech = [t.strip() for t in args.tech_stack.split(",") if t.strip()] or ["Python"]
        content = engine.generate_optimized_readme(args.project_name, args.tagline, features, tech)
        if args.apply:
            path = os.path.join(os.path.abspath(args.repo_dir), "README.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ README.md written to {path}")
        else:
            print(content)

    elif args.command == "launch":
        engine = GitHubSEOAgent(args.owner, args.name)
        if args.ai:
            from core.ai_synthesizer import AISynthesizer
            synth = AISynthesizer(model=args.model or "google/gemma-4-31b-it:free")
            repo_url = f"https://github.com/{args.owner}/{args.name}"
            channels = [args.channel] if args.channel != "all" else ["hacker_news", "reddit", "twitter_thread", "product_hunt", "release_notes"]
            for ch in channels:
                res = synth.synthesize_launch_copy(repo_url, args.name, ["open-source"], ch, args.angle)
                source = "AI" if "result" in res else "Error"
                print(f"\n--- [{ch.upper()}] (Source: {source}) ---")
                print(res.get("result", res.get("error", "Unknown error")))
                print("-" * 50)
        else:
            packs = engine.generate_launch_pack(channel=args.channel)
            for ch, text in packs.items():
                print(f"\n--- [{ch.upper()}] ---")
                print(text)
                print("-" * 50)

    elif args.command == "community":
        engine = GitHubSEOAgent(args.owner, args.name, repo_dir=os.path.abspath(args.repo_dir))
        files = engine.generate_community_health_files()
        if args.apply:
            for rel_path, content in files.items():
                full_path = os.path.join(os.path.abspath(args.repo_dir), rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  + {rel_path}")
            print("✓ Community health files installed.")
        else:
            print("Run with --apply to write files. Generated file list:")
            for rel_path in files:
                print(f"  {rel_path}")

    elif args.command == "mcp":
        from core.mcp_server import GitHubSEOMCPServer
        server = GitHubSEOMCPServer()
        server.run_stdio()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
