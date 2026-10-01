"""
GitHub SEO Agent — Automated Test Suite
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.seo_engine import GitHubSEOAgent
from core.ai_synthesizer import AISynthesizer
from core.mcp_server import GitHubSEOMCPServer


# ─── SEO Engine Tests ───────────────────────────────────────────────

def test_engine_init():
    engine = GitHubSEOAgent("owner", "repo")
    assert engine.repo_owner == "owner"
    assert engine.repo_name == "repo"
    assert len(engine.get_top_keywords()) >= 4

def test_engine_set_keywords():
    engine = GitHubSEOAgent("owner", "repo")
    custom = [{"keyword": "ai-agent", "volume": "high", "difficulty": "low"}]
    engine.set_keywords(custom)
    assert engine.get_top_keywords() == custom

def test_engine_audit_on_self():
    """Audit the github-seo-agent project directory itself."""
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    engine = GitHubSEOAgent("test", "github-seo-agent", repo_dir=project_dir)
    audit = engine.audit_repository()
    assert "score" in audit
    assert "grade" in audit
    assert "checklist" in audit
    assert audit["score"] >= 50, f"Expected decent score for own project, got {audit['score']}"

def test_engine_audit_no_dir():
    engine = GitHubSEOAgent("owner", "repo", repo_dir="/nonexistent/path")
    audit = engine.audit_repository()
    assert audit["score"] == 0
    assert audit["grade"] == "F"

def test_engine_generate_readme():
    engine = GitHubSEOAgent("testowner", "testrepo")
    readme = engine.generate_optimized_readme(
        "Test Project", "A test tagline",
        ["Feature A", "Feature B"], ["Python", "FastAPI"]
    )
    assert "# Test Project" in readme
    assert "Feature A" in readme
    assert "Python" in readme
    assert "shields.io" in readme
    assert "testowner/testrepo" in readme

def test_engine_launch_packs_all():
    engine = GitHubSEOAgent("owner", "myrepo")
    packs = engine.generate_launch_pack("all")
    assert "hacker_news" in packs
    assert "reddit" in packs
    assert "twitter_thread" in packs
    assert "product_hunt" in packs
    assert "release_notes" in packs
    for key, text in packs.items():
        assert len(text) > 10

def test_engine_launch_pack_single():
    engine = GitHubSEOAgent("owner", "myrepo")
    packs = engine.generate_launch_pack("hacker_news")
    assert len(packs) == 1
    assert "hacker_news" in packs

def test_engine_community_health():
    engine = GitHubSEOAgent("owner", "myrepo")
    files = engine.generate_community_health_files()
    assert "CONTRIBUTING.md" in files
    assert "SECURITY.md" in files
    assert ".github/workflows/ci.yml" in files

def test_engine_gh_cli_command():
    engine = GitHubSEOAgent("muhdfaisalwork-gif", "linkedin-agent")
    cmd = engine.get_gh_cli_topics_command()
    assert "gh repo edit muhdfaisalwork-gif/linkedin-agent" in cmd
    assert "--add-topic" in cmd


# ─── AI Synthesizer Tests ───────────────────────────────────────────

def test_ai_synthesizer_no_key():
    synth = AISynthesizer(api_key=None)
    synth.api_key = None  # force no key
    res = synth.synthesize_launch_copy("https://github.com/a/b", "Test", ["f1"], "reddit")
    assert "error" in res

def test_ai_synthesizer_success_mock():
    with patch("core.ai_synthesizer.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "AI-generated HN launch copy"}}]
        }
        mock_post.return_value = mock_resp

        synth = AISynthesizer(api_key="sk-test-fake")
        res = synth.synthesize_launch_copy("https://github.com/a/b", "MyProject", ["open-source"], "hacker_news", "privacy first")
        assert "result" in res
        assert "AI-generated HN launch copy" in res["result"]

def test_ai_synthesizer_pitch_mock():
    with patch("core.ai_synthesizer.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Hero pitch for README"}}]
        }
        mock_post.return_value = mock_resp

        synth = AISynthesizer(api_key="sk-test-fake")
        res = synth.synthesize_readme_pitch("TestProject", "Fast and free", "developer_growth")
        assert "result" in res
        assert "Hero pitch" in res["result"]

def test_ai_synthesizer_fallback_chain():
    """Verify fallback chain contains correct model IDs."""
    synth = AISynthesizer()
    assert "google/gemma-4-31b-it:free" in synth.DEFAULT_FALLBACKS
    assert "nvidia/nemotron-3.5-lightning:free" in synth.DEFAULT_FALLBACKS
    assert "qwen/qwen3.8-27b:free" in synth.DEFAULT_FALLBACKS


# ─── MCP Server Tests ──────────────────────────────────────────────

def test_mcp_tool_definitions():
    server = GitHubSEOMCPServer()
    tools = server.get_tool_definitions()
    names = [t["name"] for t in tools]
    assert "audit_repo_seo" in names
    assert "generate_launch_pack" in names
    assert "generate_community_files" in names

def test_mcp_initialize():
    server = GitHubSEOMCPServer()
    resp = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert "tools" in resp["result"]["capabilities"]

def test_mcp_tools_list():
    server = GitHubSEOMCPServer()
    resp = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert len(resp["result"]["tools"]) >= 3

def test_mcp_ping():
    server = GitHubSEOMCPServer()
    resp = server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "ping"})
    assert resp["result"] == {}

def test_mcp_audit_tool():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server = GitHubSEOMCPServer(repo_dir=project_dir)
    resp = server.handle_request({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "audit_repo_seo", "arguments": {}}
    })
    text = resp["result"]["content"][0]["text"]
    assert "Score" in text or "score" in text.lower()


# ─── API Server Tests ──────────────────────────────────────────────

def test_api_health():
    from api.server import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_api_audit():
    from api.server import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/api/audit")
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "grade" in data

def test_engine_empty_keywords_edge_case():
    engine = GitHubSEOAgent("owner", "repo")
    engine.set_keywords([])
    packs = engine.generate_launch_pack("all")
    assert "hacker_news" in packs
    cmd = engine.get_gh_cli_topics_command()
    assert "gh repo edit" in cmd

def test_api_root_serves_html():
    from api.server import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert "GitHub SEO Agent" in res.text
