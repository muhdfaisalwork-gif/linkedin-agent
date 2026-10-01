import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.database import init_db, get_connection
from core.linkedin.browser_agent import LinkedInBrowserAgent
from core.reach.reader import ReachReader
from core.reach.feed_engine import ReachFeedEngine
from api.app import app

client = TestClient(app)

def test_database_scanned_feed_posts_schema():
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanned_feed_posts'")
    table = c.fetchone()
    assert table is not None, "scanned_feed_posts table should exist in database"

    # Insert a mock post
    c.execute("""
        INSERT INTO scanned_feed_posts (
            author_name, author_headline, post_text, post_url, reaction_count, comment_count
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ("Test Creator", "Founder @ Stealth", "Testing Agent Reach visual feed inspection", "urn:li:activity:12345", 42, 7))
    conn.commit()

    c.execute("SELECT author_name, reaction_count FROM scanned_feed_posts WHERE post_url='urn:li:activity:12345'")
    row = c.fetchone()
    assert row["author_name"] == "Test Creator"
    assert row["reaction_count"] == 42
    conn.close()

def test_browser_agent_cookie_token_sanitization():
    agent = LinkedInBrowserAgent()
    # Invalid token length should fail fast without launching browser
    res_short = agent.save_cookie("abc")
    assert res_short["status"] == "error"

    # Disconnect should clear session
    res_disc = agent.disconnect()
    assert res_disc["status"] == "success"
    assert not agent.is_authenticated()

def test_reach_reader_url_handling():
    reader = ReachReader()
    # Test reading with mock or real public page
    res = reader.read_url("https://example.com")
    assert "status" in res
    assert "backend" in res

def test_reach_feed_engine_retrieval():
    engine = ReachFeedEngine()
    posts = engine.get_recent_scanned_posts(limit=5)
    assert isinstance(posts, list)

def test_api_settings_cookie_and_disconnect():
    # Disconnect endpoint
    res = client.post("/api/settings/disconnect")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # Save cookie validation endpoint
    res_invalid = client.post("/api/settings/save-cookie", json={"cookie": "short"})
    assert res_invalid.status_code == 200
    assert res_invalid.json()["status"] == "error"

def test_api_reach_feed_endpoint():
    res = client.get("/api/reach/feed")
    assert res.status_code == 200
    data = res.json()
    assert "posts" in data
    assert "count" in data

def test_reach_vision_analyzer():
    from core.reach.vision_analyzer import ReachVisionAnalyzer
    from core.llm.client import UniversalLLMClient
    from unittest.mock import patch, MagicMock

    analyzer = ReachVisionAnalyzer(UniversalLLMClient(provider="openrouter", api_key=""))
    # Non-existent image returns error
    res_err = analyzer.analyze_screenshot("non_existent_file_path_12345.png")
    assert res_err["status"] == "error"

    # Create temporary 1x1 test image
    import tempfile
    from PIL import Image
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        img = Image.new("RGB", (10, 10), color="blue")
        img.save(tmp_path)

    try:
        # Heuristic / mock when no API key is provided
        res_mock = analyzer.analyze_screenshot(tmp_path)
        assert res_mock["status"] in ("mock", "fallback", "success")
        assert "Visual Hierarchy" in res_mock["analysis"]

        # Ollama routing test
        ollama_client = UniversalLLMClient(provider="ollama")
        ollama_analyzer = ReachVisionAnalyzer(ollama_client)
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"message": {"content": "Ollama visual layout critique"}}
            mock_post.return_value = mock_resp

            res_ollama = ollama_analyzer.analyze_screenshot(tmp_path)
            assert res_ollama["status"] == "success"
            assert res_ollama["provider"] == "ollama"
            assert "Ollama visual" in res_ollama["analysis"]

        # Gemini routing test
        gemini_client = UniversalLLMClient(provider="gemini", api_key="fake-gemini-key")
        gemini_analyzer = ReachVisionAnalyzer(gemini_client)
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"choices": [{"message": {"content": "Gemini visual critique"}}]}
            mock_post.return_value = mock_resp

            res_gemini = gemini_analyzer.analyze_screenshot(tmp_path)
            assert res_gemini["status"] == "success"
            assert res_gemini["provider"] == "gemini"
            assert "Gemini visual" in res_gemini["analysis"]

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_reach_reader_empty_url_validation():
    reader = ReachReader()
    res1 = reader.read_url("")
    assert res1["status"] == "error"
    assert "valid URL" in res1["message"]

    res2 = reader.read_url("   ")
    assert res2["status"] == "error"

    res3 = reader.read_url("https://")
    assert res3["status"] == "error"

def test_reach_inspect_empty_url_endpoint():
    res = client.post("/api/reach/inspect", json={"url": ""})
    assert res.status_code == 200
    assert res.json()["status"] == "error"
    assert "valid URL" in res.json()["message"]

def test_settings_vision_model_persistence():
    # Save vision model
    res_save = client.post("/api/settings", json={"vision_model": "llama3.2-vision:latest"})
    assert res_save.status_code == 200
    assert res_save.json()["status"] == "saved"

    # Get settings
    res_get = client.get("/api/settings")
    assert res_get.status_code == 200
    assert res_get.json()["vision_model"] == "llama3.2-vision:latest"

def test_feed_engine_safe_metric_parsing():
    from core.reach.feed_engine import _parse_metric_count
    assert _parse_metric_count(None) == 0
    assert _parse_metric_count("") == 0
    assert _parse_metric_count("   ") == 0
    assert _parse_metric_count("42") == 42
    assert _parse_metric_count("1,250 reactions") == 1250
    assert _parse_metric_count("invalid string") == 0

