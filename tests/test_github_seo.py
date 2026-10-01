import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.seo.github_seo import LinkedInNexusGitHubSEO, TARGET_KEYWORDS, RECOMMENDED_GITHUB_TOPICS
from core.mcp.server import LinkedInNexusMCPServer
from api.app import app

client = TestClient(app)

def test_github_seo_keywords_and_topics():
    engine = LinkedInNexusGitHubSEO()
    assert len(TARGET_KEYWORDS) >= 8
    assert len(RECOMMENDED_GITHUB_TOPICS) >= 10
    assert "linkedin-agent" in RECOMMENDED_GITHUB_TOPICS
    assert "ollama" in RECOMMENDED_GITHUB_TOPICS
    assert "mcp-server" in RECOMMENDED_GITHUB_TOPICS

def test_github_seo_audit_full():
    engine = LinkedInNexusGitHubSEO()
    audit = engine.audit_repository()
    assert "score" in audit
    assert "grade" in audit
    assert "checklist" in audit
    assert audit["score"] >= 80, f"Expected high SEO score after optimizations, got {audit['score']}"
    assert audit["grade"] in ("A+", "A")
    assert "gh_cli_command" in audit

def test_github_seo_readme_generation():
    engine = LinkedInNexusGitHubSEO()
    readme = engine.generate_optimized_readme()
    assert "# 🚀 LinkedIn Nexus Agent" in readme
    assert "Taplio" in readme
    assert "Ollama" in readme
    assert "Model Context Protocol" in readme or "MCP" in readme
    assert "mermaid" in readme
    assert "quick start" in readme.lower()

def test_github_seo_launch_packs():
    engine = LinkedInNexusGitHubSEO()
    # Test all packs
    packs = engine.generate_launch_pack(channel="all")
    assert "hacker_news" in packs
    assert "reddit_localllama" in packs
    assert "reddit_selfhosted" in packs
    assert "twitter_thread" in packs
    assert "release_notes" in packs

    # Verify content quality
    assert "Show HN" in packs["hacker_news"]
    assert "Ollama" in packs["reddit_localllama"]
    assert "Taplio" in packs["twitter_thread"]

    # Test single channel retrieval
    hn_pack = engine.generate_launch_pack(channel="hacker_news")
    assert len(hn_pack) == 1
    assert "hacker_news" in hn_pack

def test_github_seo_community_health_files():
    engine = LinkedInNexusGitHubSEO()
    res = engine.generate_community_health_files()
    assert res["status"] == "success"
    assert len(res["files_written"]) >= 6

    # Verify files exist on disk
    for rel_path in res["files_written"]:
        full_path = os.path.join(engine.repo_dir, rel_path)
        assert os.path.exists(full_path), f"File {rel_path} was not created"

def test_api_seo_endpoints():
    # 1. GET /api/seo/audit
    res_audit = client.get("/api/seo/audit")
    assert res_audit.status_code == 200
    data_audit = res_audit.json()
    assert data_audit["score"] >= 80

    # 2. POST /api/seo/optimize-readme
    res_readme = client.post("/api/seo/optimize-readme", json={"apply": False})
    assert res_readme.status_code == 200
    assert "readme_content" in res_readme.json()

    # 3. POST /api/seo/launch-pack
    res_pack = client.post("/api/seo/launch-pack", json={"channel": "twitter_thread"})
    assert res_pack.status_code == 200
    assert "packs" in res_pack.json()
    assert "twitter_thread" in res_pack.json()["packs"]

    # 4. POST /api/seo/install-community-files
    res_comm = client.post("/api/seo/install-community-files")
    assert res_comm.status_code == 200
    assert res_comm.json()["status"] == "success"

def test_mcp_seo_tools():
    server = LinkedInNexusMCPServer()
    tools = [t["name"] for t in server.get_tool_definitions()]
    assert "audit_github_seo" in tools
    assert "generate_github_launch_pack" in tools

    # Test calling audit_github_seo
    req_audit = {
        "jsonrpc": "2.0",
        "id": 991,
        "method": "tools/call",
        "params": {
            "name": "audit_github_seo",
            "arguments": {}
        }
    }
    resp_audit = server.handle_request(req_audit)
    assert resp_audit["result"]["content"][0]["text"].startswith("### LinkedIn Nexus Agent — GitHub SEO Audit Score")

    # Test calling generate_github_launch_pack
    req_launch = {
        "jsonrpc": "2.0",
        "id": 992,
        "method": "tools/call",
        "params": {
            "name": "generate_github_launch_pack",
            "arguments": {"channel": "hacker_news"}
        }
    }
    resp_launch = server.handle_request(req_launch)
    assert "Show HN" in resp_launch["result"]["content"][0]["text"]
