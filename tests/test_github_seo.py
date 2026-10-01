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

    # Test calling generate_github_launch_pack with use_ai=True
    from unittest.mock import patch
    with patch("core.llm.client.OpenRouterProvider.chat_completion") as mock_chat:
        mock_chat.return_value = {
            "content": "AI generated launch post for Reddit r/LocalLLaMA",
            "model_used": "google/gemma-4-31b-it:free",
            "provider": "openrouter"
        }
        req_launch_ai = {
            "jsonrpc": "2.0",
            "id": 993,
            "method": "tools/call",
            "params": {
                "name": "generate_github_launch_pack",
                "arguments": {"channel": "reddit_localllama", "use_ai": True, "angle": "Privacy & Ollama"}
            }
        }
        resp_launch_ai = server.handle_request(req_launch_ai)
        assert "AI generated launch post" in resp_launch_ai["result"]["content"][0]["text"]
        assert "gemma-4-31b-it" in resp_launch_ai["result"]["content"][0]["text"]

def test_github_seo_ai_launch_and_pitch():
    from unittest.mock import patch
    engine = LinkedInNexusGitHubSEO()

    # 1. Test AI Launch Generation (live AI success path with Gemma 4)
    with patch("core.llm.client.OpenRouterProvider.chat_completion") as mock_chat:
        mock_chat.return_value = {
            "content": "Title: Show HN: LinkedIn Nexus Agent v1.0\n\nAI synthesised launch content with Gemma-4.",
            "model_used": "google/gemma-4-31b-it:free",
            "provider": "openrouter"
        }
        res = engine.generate_ai_launch_content(
            channel="hacker_news",
            angle="Focus on 100% offline Ollama and 82 humanizer rules",
            model="google/gemma-4-31b-it:free"
        )
        assert res["status"] == "success"
        assert res["source"] == "openrouter_ai"
        assert res["model_used"] == "google/gemma-4-31b-it:free"
        assert "AI synthesised launch content" in res["content"]

    # 2. Test AI Pitch Generation (with Nemotron)
    with patch("core.llm.client.OpenRouterProvider.chat_completion") as mock_chat:
        mock_chat.return_value = {
            "content": "### The #1 Open-Source LinkedIn AI Studio\n- Privacy-first\n- 82 Humanizer rules",
            "model_used": "nvidia/nemotron-3.5-lightning:free",
            "provider": "openrouter"
        }
        pitch_res = engine.ai_pitch_readme(focus_area="developer_growth", model="nvidia/nemotron-3.5-lightning:free")
        assert pitch_res["status"] == "success"
        assert pitch_res["source"] == "openrouter_ai"
        assert "Privacy-first" in pitch_res["pitch"]

    # 3. Test Graceful Fallback when OpenRouter hits 429 or quota limit
    with patch("core.llm.client.OpenRouterProvider.chat_completion", side_effect=Exception("Rate limit 429")):
        fallback_res = engine.generate_ai_launch_content(
            channel="hacker_news",
            angle="Test fallback",
            model="google/gemma-4-31b-it:free"
        )
        assert fallback_res["status"] == "success"
        assert fallback_res["source"] == "template_fallback"
        assert "Show HN" in fallback_res["content"]
        assert "LLM fallback active" in fallback_res["note"]

    # 4. Test API POST /api/seo/ai-launch
    with patch("core.llm.client.OpenRouterProvider.chat_completion") as mock_chat:
        mock_chat.return_value = {
            "content": "Reddit self-hosted copy generated by Gemma 4",
            "model_used": "google/gemma-4-31b-it:free",
            "provider": "openrouter"
        }
        api_res = client.post("/api/seo/ai-launch", json={
            "channel": "reddit_selfhosted",
            "angle": "Self-hosted alternative to Taplio with SQLite",
            "model": "google/gemma-4-31b-it:free"
        })
        assert api_res.status_code == 200
        data = api_res.json()
        assert data["status"] == "success"
        assert data["content"] == "Reddit self-hosted copy generated by Gemma 4"

    # 5. Test API POST /api/seo/ai-pitch
    with patch("core.llm.client.OpenRouterProvider.chat_completion") as mock_chat:
        mock_chat.return_value = {
            "content": "Hero pitch generated by Nemotron",
            "model_used": "nvidia/nemotron-3.5-lightning:free",
            "provider": "openrouter"
        }
        pitch_api = client.post("/api/seo/ai-pitch", json={
            "focus_area": "privacy",
            "model": "nvidia/nemotron-3.5-lightning:free"
        })
        assert pitch_api.status_code == 200
        assert pitch_api.json()["pitch"] == "Hero pitch generated by Nemotron"

